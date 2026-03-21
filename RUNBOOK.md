# Alpha Monitor Runbook

## 1. Local development

- Start: `npm run dev`
- Health check: `npm run check:health`
- Smoke check: `npm run check`
- Boundary check: `npm run check:boundaries`
- Access info: `npm run show:access`

Windows local helper entrypoints remain:

- Start: double-click `start_dashboard.bat`
- Stop: double-click `stop_dashboard.bat`

## 2. Health check meaning

`/api/health` returns layered status:

- `web`: web service and dashboard entry availability
- `data_jobs`: background data sync state
- `push_scheduler`: push scheduling state

Rule:

- If `web = ok`, the site should still be considered reachable.
- `data_jobs = warn` or `push_scheduler = warn` means background work degraded, not that the homepage is down.

## 3. Official cloud-server target

Formal public deployment target:

1. Ubuntu server
2. Node app running from this project root
3. `systemd` keeps the service alive
4. `Nginx` or `Caddy` exposes `80/443`
5. Public users open the homepage through the public URL, not `:5000`

Recommended public entry:

- Preferred: `https://your-domain/`
- Transitional: `http://your-server-ip/`

App internal port:

- Node app still listens on the configured app port, default `5000`
- Reverse proxy forwards public traffic to that internal port

## 4. Required config before public deployment

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
sudo cp tools/deploy/nginx-alpha-monitor.conf /etc/nginx/sites-available/alpha-monitor
sudo ln -sf /etc/nginx/sites-available/alpha-monitor /etc/nginx/sites-enabled/alpha-monitor
sudo nginx -t
sudo systemctl reload nginx
```

For Caddy:

```bash
sudo cp tools/deploy/Caddyfile /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
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
3. The workflow connects to the server through SSH
4. The server runs `tools/deploy/update_from_github.sh`
5. The script updates code, installs dependencies, restarts the service, and checks health

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

## 11. Server-side manual dry run

Before trusting GitHub auto deploy, run this once on the server:

```bash
cd "/home/ubuntu/Alpha monitor"
bash tools/deploy/update_from_github.sh
```

Expected behavior:

1. Reset to `origin/main`
2. Install Node dependencies
3. Restart `alpha-monitor` if it exists
4. Print local health-check result

## 12. If auto deploy fails

Check in this order:

1. GitHub Actions job log
2. SSH connectivity and key validity
3. Server directory path
4. `git status` and repo permissions on the server
5. `sudo systemctl status alpha-monitor`
6. `curl http://127.0.0.1:5000/api/health`
7. `sudo journalctl -u alpha-monitor -n 100 --no-pager`
