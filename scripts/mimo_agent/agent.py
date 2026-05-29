# -*- coding: utf-8 -*-
"""MiMo Agent: 调用小米MiMo API，支持本地工具调用（联网搜索 + ticker查询）。

用法:
    python scripts/mimo_agent/agent.py "帮我查一下原油LOF的代码"
    python scripts/mimo_agent/agent.py --search "标普500最新行情"
    python scripts/mimo_agent/agent.py --lookup "原油"
"""

import argparse
import json
import os
import sys

import requests

from scripts.mimo_agent.tools import TOOLS_DEFINITION, TOOL_HANDLERS

# ============================================================
# 配置（从 config/secrets.yaml 读取）
# ============================================================

def _load_config():
    """从 config/secrets.yaml 加载 MiMo API 配置。"""
    try:
        import yaml
        secrets_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'secrets.yaml')
        with open(secrets_path, 'r', encoding='utf-8') as f:
            secrets = yaml.safe_load(f) or {}
        mimo = secrets.get("mimo", {})
        return {
            "api_key": mimo.get("api_key", ""),
            "base_url": mimo.get("base_url", "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"),
            "model": mimo.get("model", "mimo-v2.5"),
        }
    except Exception:
        return {
            "api_key": os.environ.get("MIMO_API_KEY", ""),
            "base_url": os.environ.get("MIMO_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"),
            "model": os.environ.get("MIMO_MODEL", "mimo-v2.5"),
        }


# ============================================================
# MiMo Agent 核心
# ============================================================

SYSTEM_PROMPT = (
    "你是Alpha Monitor金融助手，专注于QDII LOF基金套利监控。"
    "你可以：1)查询基金/ETF代码 2)联网搜索最新市场数据。"
    "回答要简洁准确，数据优先。"
)


def chat(user_message: str, system_prompt: str = None, max_tool_rounds: int = 5, verbose: bool = False) -> str:
    """发送消息给 MiMo，自动处理工具调用循环，返回最终文本回复。"""
    cfg = _load_config()
    if not cfg["api_key"]:
        return "错误: 未配置 MiMo API Key，请在 config/secrets.yaml 中添加 mimo.api_key"

    messages = []
    messages.append({"role": "system", "content": system_prompt or SYSTEM_PROMPT})
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }

    for round_num in range(max_tool_rounds + 1):
        payload = {
            "model": cfg["model"],
            "messages": messages,
            "tools": TOOLS_DEFINITION,
            "tool_choice": "auto",
            "temperature": 0.3,
        }

        if verbose:
            print(f"\n--- Round {round_num + 1} ---")

        try:
            resp = requests.post(cfg["base_url"], headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as e:
            return f"API请求失败: {e}"
        except (KeyError, json.JSONDecodeError) as e:
            return f"API响应解析失败: {e}\n响应: {resp.text[:500]}"

        choice = data["choices"][0]
        message = choice["message"]
        finish_reason = choice.get("finish_reason", "")

        # 如果MiMo直接回复文本（没有工具调用），返回
        if finish_reason == "stop" or not message.get("tool_calls"):
            return message.get("content", "")

        # MiMo 决定调用工具
        messages.append(message)

        for tool_call in message["tool_calls"]:
            func_name = tool_call["function"]["name"]
            func_args = json.loads(tool_call["function"]["arguments"])

            if verbose:
                print(f"  工具调用: {func_name}({json.dumps(func_args, ensure_ascii=False)})")

            handler = TOOL_HANDLERS.get(func_name)
            if handler:
                result = handler(func_args)
            else:
                result = json.dumps({"status": "error", "message": f"未知工具: {func_name}"}, ensure_ascii=False)

            if verbose:
                print(f"  工具结果: {result[:300]}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result,
            })

    return "达到最大工具调用轮数，未能获得最终回复。"


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="MiMo Agent - 联网搜索 + 本地ticker查询")
    parser.add_argument("message", nargs="?", help="用户消息")
    parser.add_argument("--search", help="直接联网搜索（不经过MiMo）")
    parser.add_argument("--lookup", help="直接查询本地ticker（不经过MiMo）")
    parser.add_argument("--system", default=None, help="自定义系统提示词")
    parser.add_argument("--verbose", "-v", action="store_true", help="打印工具调用详情")
    args = parser.parse_args()

    # 快捷模式：直接搜索
    if args.search:
        from scripts.mimo_agent.tools import web_search
        print(web_search(args.search))
        return

    # 快捷模式：直接查询
    if args.lookup:
        from scripts.mimo_agent.tools import lookup_ticker_locally
        print(lookup_ticker_locally(args.lookup))
        return

    # 交互模式
    if args.message:
        reply = chat(args.message, system_prompt=args.system, verbose=args.verbose)
        print(reply)
    else:
        print("MiMo Agent 交互模式 (输入 quit 退出)")
        print("-" * 40)
        while True:
            try:
                user_input = input("\n你: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not user_input or user_input.lower() in ("quit", "exit", "q"):
                break
            reply = chat(user_input, system_prompt=args.system, verbose=args.verbose)
            print(f"\nMiMo: {reply}")


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    main()