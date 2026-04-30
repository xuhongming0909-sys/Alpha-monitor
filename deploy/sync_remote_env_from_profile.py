#!/usr/bin/env python3
"""Sync core remote .env values from the repository-local server profile."""

from __future__ import annotations

import argparse
import posixpath
import sys
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any

import paramiko
import yaml


ROOT_DIR = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT_DIR / "ops" / "server_profile.local.yaml"
DEFAULT_HEALTH_PATH = "/api/health"
HEALTH_RETRY_COUNT = 20
HEALTH_RETRY_DELAY_SECONDS = 2
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.config.script_config import get_config


@dataclass(frozen=True)
class SyncValue:
    key: str
    value: str


def deep_get(target: Any, *path_parts: str, default: Any = "") -> Any:
    current = target
    for part in path_parts:
        if not isinstance(current, dict):
            return default
        current = current.get(part)
        if current is None:
            return default
    return current


def require_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"missing required field: {field_name}")
    return text


def normalize_public_base_url(value: Any) -> str:
    text = str(value or "").strip()
    return text.rstrip("/")


def normalize_html_url(value: Any) -> str:
    base_url = normalize_public_base_url(value)
    return f"{base_url}/" if base_url else ""


def load_profile() -> dict[str, Any]:
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(f"server profile not found: {PROFILE_PATH}")
    payload = yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("server profile root must be a mapping")
    return payload


def build_sync_values(profile: dict[str, Any], config: dict[str, Any]) -> list[SyncValue]:
    # 公网 URL 以 server_profile 为准，避免本地 .env 残留旧地址继续写回云端。
    public_url = normalize_public_base_url(
        deep_get(profile, "public_access", "public_url")
        or deep_get(config, "deployment", "public_base_url")
    )
    # webhook 同样优先取 server_profile 中已确认可用的值。
    webhook_url = str(
        deep_get(profile, "notifications", "wecom_webhook_url")
        or deep_get(config, "notification", "wecom", "webhook_url")
        or ""
    ).strip()
    push_html_url = normalize_html_url(
        deep_get(profile, "public_access", "public_url")
        or deep_get(config, "notification", "wecom", "push_html_url")
        or public_url
    )

    candidates: list[tuple[str, str]] = [
        ("WECOM_WEBHOOK_URL", webhook_url),
        ("PUBLIC_BASE_URL", public_url),
        ("PUSH_HTML_URL", push_html_url),
        ("ALPHA_MONITOR_HTML_URL", push_html_url),
        ("DEEPSEEK_API_KEY", str(deep_get(config, "strategy", "merger", "deepseek_api_key") or "").strip()),
        ("DEEPSEEK_BASE_URL", str(deep_get(config, "strategy", "merger", "deepseek_base_url") or "").strip()),
        ("JISILU_COOKIE", str(deep_get(config, "data_fetch", "plugins", "convertible_bond", "jisilu_cookie") or "").strip()),
    ]
    return [SyncValue(key, value) for key, value in candidates if value]


def create_ssh_client(profile: dict[str, Any]) -> paramiko.SSHClient:
    connection = deep_get(profile, "connection", default={})
    host = require_text(deep_get(connection, "host"), "connection.host")
    user = require_text(deep_get(connection, "user"), "connection.user")
    port = int(deep_get(connection, "port", default=22) or 22)
    auth_type = str(deep_get(connection, "auth_type") or "password").strip().lower()
    password = str(deep_get(connection, "password") or "")
    private_key = str(deep_get(connection, "private_key") or "").strip()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    connect_kwargs: dict[str, Any] = {
        "hostname": host,
        "port": port,
        "username": user,
        "timeout": 20,
        "banner_timeout": 20,
        "auth_timeout": 20,
        "look_for_keys": False,
        "allow_agent": False,
    }

    if auth_type == "private_key" and private_key:
        key_path = Path(private_key)
        if key_path.exists():
            connect_kwargs["key_filename"] = str(key_path)
        else:
            connect_kwargs["pkey"] = paramiko.RSAKey.from_private_key(StringIO(private_key))
        if password:
            connect_kwargs["passphrase"] = password
    else:
        connect_kwargs["password"] = require_text(password, "connection.password")

    client.connect(**connect_kwargs)
    return client


def read_remote_text(sftp: paramiko.SFTPClient, remote_path: str) -> str:
    try:
        with sftp.open(remote_path, "r") as file_obj:
            return file_obj.read().decode("utf-8")
    except FileNotFoundError:
        return ""


def ensure_remote_dir(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    current = ""
    for part in remote_dir.split("/"):
        if not part:
            continue
        current = f"{current}/{part}" if current else f"/{part}"
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)


def parse_env_lines(text: str) -> tuple[list[str], dict[str, int], dict[str, str]]:
    lines = text.splitlines()
    key_to_index: dict[str, int] = {}
    key_to_value: dict[str, str] = {}
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        env_key = key.strip()
        if not env_key:
            continue
        key_to_index[env_key] = index
        key_to_value[env_key] = raw_value.strip()
    return lines, key_to_index, key_to_value


def render_env_text(original_text: str, sync_values: list[SyncValue]) -> tuple[str, list[str]]:
    lines, key_to_index, key_to_value = parse_env_lines(original_text)
    changed_keys: list[str] = []

    for item in sync_values:
        rendered_line = f"{item.key}={item.value}"
        old_value = key_to_value.get(item.key)
        if old_value == item.value:
            continue
        changed_keys.append(item.key)
        if item.key in key_to_index:
            lines[key_to_index[item.key]] = rendered_line
        else:
            lines.append(rendered_line)

    new_text = "\n".join(lines).strip("\n")
    if new_text:
        new_text += "\n"
    return new_text, changed_keys


def write_remote_text(sftp: paramiko.SFTPClient, remote_path: str, text: str) -> None:
    remote_dir = posixpath.dirname(remote_path)
    ensure_remote_dir(sftp, remote_dir)
    with sftp.open(remote_path, "w") as file_obj:
        file_obj.write(text.encode("utf-8"))


def run_remote_command(client: paramiko.SSHClient, command: str) -> tuple[int, str, str]:
    stdin, stdout, stderr = client.exec_command(command)
    if stdin:
        stdin.close()
    exit_code = stdout.channel.recv_exit_status()
    out_text = stdout.read().decode("utf-8", errors="replace")
    err_text = stderr.read().decode("utf-8", errors="replace")
    return exit_code, out_text, err_text


def restart_and_check_health(client: paramiko.SSHClient, profile: dict[str, Any]) -> None:
    service_name = require_text(deep_get(profile, "app", "service_name"), "app.service_name")
    app_port = int(deep_get(profile, "app", "app_port", default=5000) or 5000)
    health_path = str(deep_get(profile, "app", "health_path") or DEFAULT_HEALTH_PATH).strip() or DEFAULT_HEALTH_PATH

    restart_command = (
        f"sudo -n systemctl restart {service_name} "
        f"|| systemctl restart {service_name}"
    )
    exit_code, _stdout, stderr = run_remote_command(client, restart_command)
    if exit_code != 0:
        raise RuntimeError(f"service restart failed: {stderr.strip() or service_name}")

    # 服务重启后给 Node 一点恢复窗口，避免刚起来的瞬间被误判为失败。
    for attempt in range(1, HEALTH_RETRY_COUNT + 1):
        health_command = (
            f"curl --fail --silent --show-error "
            f"http://127.0.0.1:{app_port}{health_path}"
        )
        exit_code, stdout, stderr = run_remote_command(client, health_command)
        if exit_code == 0:
            return
        if attempt == HEALTH_RETRY_COUNT:
            raise RuntimeError(f"health check failed: {stderr.strip() or stdout.strip()}")
        run_remote_command(client, f"sleep {HEALTH_RETRY_DELAY_SECONDS}")


def mask_value(key: str, value: str) -> str:
    if not value:
        return ""
    if key.endswith("_URL") and "://" in value:
        prefix, suffix = value.split("://", 1)
        if len(suffix) <= 12:
            return f"{prefix}://***"
        return f"{prefix}://{suffix[:6]}***{suffix[-4:]}"
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}***{value[-4:]}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync remote cloud .env from local server profile.")
    parser.add_argument("--dry-run", action="store_true", help="Only show the planned changes without writing remote .env.")
    parser.add_argument("--no-restart", action="store_true", help="Do not restart service after remote .env changes.")
    args = parser.parse_args()

    profile = load_profile()
    config = get_config()
    sync_values = build_sync_values(profile, config)
    if not sync_values:
        raise RuntimeError("no effective sync values resolved from server profile/config")

    host = require_text(deep_get(profile, "connection", "host"), "connection.host")
    remote_env_file = require_text(deep_get(profile, "app", "env_file"), "app.env_file")

    client = create_ssh_client(profile)
    try:
        sftp = client.open_sftp()
        try:
            original_text = read_remote_text(sftp, remote_env_file)
            new_text, changed_keys = render_env_text(original_text, sync_values)
            print(f"[sync] target host: {host}")
            print(f"[sync] remote env: {remote_env_file}")
            print(f"[sync] candidate keys: {', '.join(item.key for item in sync_values)}")

            if args.dry_run:
                if changed_keys:
                    print(f"[sync] dry-run changed keys: {', '.join(changed_keys)}")
                    for item in sync_values:
                        if item.key in changed_keys:
                            print(f"[sync] {item.key} -> {mask_value(item.key, item.value)}")
                else:
                    print("[sync] dry-run result: already in sync")
                return 0

            if changed_keys:
                # 只覆写需要同步的键，未触达的远端 env 保持原样。
                write_remote_text(sftp, remote_env_file, new_text)
                print(f"[sync] updated keys: {', '.join(changed_keys)}")
                for item in sync_values:
                    if item.key in changed_keys:
                        print(f"[sync] {item.key} -> {mask_value(item.key, item.value)}")
            else:
                print("[sync] remote env already aligned")

        finally:
            sftp.close()

        restarted = False
        if changed_keys and not args.no_restart:
            restart_and_check_health(client, profile)
            restarted = True
            print("[sync] service restarted and health check passed")
        elif changed_keys:
            print("[sync] restart skipped by --no-restart")
        else:
            print("[sync] restart skipped because no remote env change was needed")

        print(f"[sync] result: changed={len(changed_keys)} restarted={str(restarted).lower()}")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
