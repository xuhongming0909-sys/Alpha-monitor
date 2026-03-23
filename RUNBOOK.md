# Alpha Monitor Runbook

## 1. Runtime model

- Official runtime mode: cloud only
- Official user access: configured public URL
- Official process hosting: cloud `systemd` + reverse proxy
- Local `npm run dev` is development validation only and is not an operator-facing access path

## 2. Development-only local checks

- Start: `npm run dev`
- Health check: `npm run check:health`
- Smoke check: `npm run check`
- Boundary check: `npm run check:boundaries`

## 3. Health check meaning

`/api/health` returns layered status:

- `web`: web service and dashboard entry availability
- `data_jobs`: background data sync state
- `push_scheduler`: push scheduling state

Rule:

- If `web = ok`, the site should still be considered reachable.
- `data_jobs = warn` or `push_scheduler = warn` means background work degraded, not that the homepage is down.

## 4. Official cloud-server target

Formal public deployment target:

1. Ubuntu server
2. Node app running from this project root
3. `systemd` keeps the service alive
4. `Nginx` or `Caddy` exposes `80/443`
5. Public users open the homepage through the public URL, not `:5000`
6. Runtime JSON state stays on the server and is not treated as source code

Recommended public entry:

- Preferred: `https://your-domain/`
- Transitional: `http://your-server-ip/`

App internal port:

- Node app still listens on the configured app port, default `5000`
- Reverse proxy forwards public traffic to that internal port

## 4A. Required config before public deployment

Update `config.yaml` before server rollout:

- `app.environment`
- `app.host`
- `app.port`
- `app.server_base_url`
- `app.healthcheck_path`
- `app.trust_proxy`
- `deployment.public_base_url`
- `deployment.reverse_proxy.enabled`
- `deployment.reverse_proxy.type`
- `deployment.systemd.service_name`

If you use a domain and HTTPS:

- Set `deployment.public_base_url` to the final HTTPS URL
- Keep `app.server_base_url` aligned with the formal external base URL

## 5. Ubuntu deployment steps

From the project root on the server:

1. Install Node.js 18+ and Python 3
2. Install dependencies with `npm install`
3. Fill `.env` if secrets are required
4. Update `config.yaml` to production values
5. Install the `systemd` service:

```bash
sudo bash tools/deploy/install_systemd.sh
```

6. Pick one reverse proxy:

For Nginx:

```bash
sudo bash tools/deploy/install_nginx_site.sh alpha-monitor YOUR_DOMAIN_OR_IP 5000
```

For Caddy:

```bash
sudo bash tools/deploy/install_caddy_site.sh YOUR_DOMAIN_OR_IP 5000
```

7. Verify:

```bash
curl http://127.0.0.1:5000/api/health
curl http://YOUR_PUBLIC_HOST/api/health
```

## 5.1 Fastest rollout path

If your server is already prepared with Node.js, Python, and nginx, the shortest path is:

```bash
cd /path/to/Alpha-monitor
npm install
sudo bash tools/deploy/install_systemd.sh
sudo bash tools/deploy/install_nginx_site.sh alpha-monitor YOUR_DOMAIN_OR_IP 5000
bash tools/deploy/server_doctor.sh
```

Meaning:

1. Install project dependencies
2. Register the app as a `systemd` service
3. Expose public port `80` through nginx
4. Run the doctor script to check local health, public health, service state, and listening ports

If you already use a domain and HTTPS, you can keep nginx for HTTP forwarding first, then add certificate management after the app is confirmed reachable.

## 5.2 Runtime state rule

The following files are runtime state, not source-of-truth code artifacts:

- `runtime_data/shared/*.json`

Deployment must preserve these files on the server. They should stay local to the runtime environment and must not be relied on as Git-tracked release content.

## 5.3 Core env sync

Official core cloud-env sync entry:

```powershell
npm run sync:server:env
```

What it does:

1. Reads `ops/server_profile.local.yaml`
2. Syncs core remote `.env` keys such as `WECOM_WEBHOOK_URL`, `PUBLIC_BASE_URL`, `PUSH_HTML_URL`
3. Restarts the managed service only when values changed
4. Checks the configured health endpoint

Safe inspection mode:

```powershell
python tools/deploy/sync_remote_env_from_profile.py --dry-run
```

## 6. systemd operations

Service name default: `alpha-monitor`

Common commands:

```bash
sudo systemctl status alpha-monitor
sudo systemctl restart alpha-monitor
sudo systemctl stop alpha-monitor
sudo systemctl enable alpha-monitor
sudo journalctl -u alpha-monitor -n 100 --no-pager
```

Uninstall service:

```bash
sudo bash tools/deploy/uninstall_systemd.sh
```

## 7. Reverse proxy rules

Requirements:

1. Public `80/443` must reach the reverse proxy
2. Reverse proxy must forward to `127.0.0.1:5000`
3. Homepage and `/api/health` must use the same public entry
4. Cloud security group and OS firewall must both allow the required ports

Useful commands:

```bash
sudo bash tools/deploy/install_nginx_site.sh alpha-monitor YOUR_DOMAIN_OR_IP 5000
sudo nginx -t
sudo systemctl reload nginx
```

## 8. Public smoke checklist

After deployment, all of the following must pass:

1. `npm run check`
2. `npm run check:boundaries`
3. `python data_dispatch.py exchange-rate`
4. `python data_dispatch.py ah`
5. `python data_dispatch.py ab`
6. Open the public homepage in a browser
7. Open the public `/api/health`
8. Reboot the server and verify auto-recovery

## 9. Failure diagnosis

If the site is not reachable:

1. Check `systemd` status first
2. Check local `http://127.0.0.1:5000/api/health`
3. Check reverse proxy status
4. Check cloud security group and server firewall
5. Check runtime logs in `runtime_logs/`

Recommended one-shot diagnosis:

```bash
bash tools/deploy/server_doctor.sh
```

What it checks:

1. `node / npm / python` presence
2. `systemd` service state
3. `nginx` or `caddy` state
4. Local `/api/health`
5. Public `/api/health` if `deployment.public_base_url` is already configured
6. Whether `80 / 443 / app.port` are actually listening

If `/api/health` is reachable but `web != ok`:

- Focus on `start_server.js`, entry file path, or port binding

If `web = ok` but `data_jobs = warn`:

- The homepage is up; investigate Python data jobs separately

## 10. GitHub auto deploy

Official repo-side auto deploy chain:

1. Push code to `main`
2. GitHub Actions runs `.github/workflows/deploy.yml`
3. Runner connects to the server through SSH
4. Runner triggers `tools/deploy/update_from_github.sh` inside `SERVER_APP_DIR`
5. The server-side script performs code sync, dependency install, service refresh/restart, and health checks

Required GitHub Secrets:

- `SERVER_HOST`
- `SERVER_USER`
- `SERVER_PORT`
- `SERVER_SSH_KEY`

Optional GitHub Secrets:

- `SERVER_APP_DIR`
- `SERVER_SERVICE_NAME`

Default values used by the workflow if optional secrets are not set:

- `SERVER_APP_DIR=/home/ubuntu/Alpha monitor`
- `SERVER_SERVICE_NAME=alpha-monitor`

Important notes:

- GitHub Actions only validates secrets, prepares SSH, and triggers the remote script.
- All server-side business steps stay inside `tools/deploy/update_from_github.sh`.
- The remote directory must already contain the repository and the deploy script.

## 11. Server-side manual dry run

Before trusting GitHub auto deploy, run this once on the server:

```bash
cd "/home/ubuntu/Alpha monitor"
bash tools/deploy/update_from_github.sh
```

Expected behavior:

1. Fetch and reset to the configured target branch
2. Install Node and Python dependencies
3. Refresh and restart `alpha-monitor` if it exists
4. Print health-check and homepage marker verification results

## 12. If auto deploy fails

Check in this order:

1. GitHub Actions job log
2. SSH connectivity and key validity
3. Server directory path
4. Whether `tools/deploy/update_from_github.sh` exists under `SERVER_APP_DIR`
5. `sudo systemctl status alpha-monitor`
6. `curl http://127.0.0.1:5000/api/health`
7. `sudo journalctl -u alpha-monitor -n 100 --no-pager`

## 13. Local agent-assist workflow

This repository now includes a local `mini-SWE-agent` task generator:

```powershell
npm run agent:mini:task -- --help
```

Recommended use:

1. Let Codex confirm whether docs/contracts must be updated first.
2. Generate a repository-safe task prompt with `npm run agent:mini:task -- ...`.
3. Run `mini-SWE-agent` with the generated task text.
4. Review the resulting diff before merge.

Project-specific guide:

- [docs/mini-swe-agent-guide.md](docs/mini-swe-agent-guide.md)
