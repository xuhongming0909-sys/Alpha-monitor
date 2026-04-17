# Quickstart: Alpha Monitor Dashboard Refactor

## Environment

1. Install Node.js 18+ and Python 3.
2. Install Node dependencies:

```powershell
npm install
```

3. Copy `.env.example` to `.env` when local secrets are required.

## Official verification path

Official update/view path is cloud-first:

1. sync code to the cloud server
2. verify the public homepage
3. verify the public `/api/health`

## Development-only local start

```powershell
npm run dev
```

Open `http://127.0.0.1:5000` only for temporary debugging when needed.

Official runtime access must use the cloud public URL configured in `config.yaml > deployment.public_base_url`.

## Required verification commands

Run the minimum constitution gate checks after structural changes:

```powershell
npm run check
python data_dispatch.py exchange-rate
python data_dispatch.py ah
```

Recommended extra checks for this feature:

```powershell
python data_dispatch.py cb-arb
python data_dispatch.py merger
npm run check:boundaries
```

## Refresh model

- Server-side background refresh remains the source of truth.
- Dashboard auto refresh is fixed at `60s`, but it is status-first:
  - poll status metadata every minute
  - reload full table data only when the corresponding cache changed
- The dashboard must not turn `5 分钟 / 15 分钟` server data into fake `1 分钟`
  source truth.
- Ordinary page opening and minute polling must not trigger heavy maintenance
  such as convertible underlying history sync.

## Manual verification checklist

1. Homepage shows title, single-line status text, today subscription table, and
   compact push settings.
2. Six tabs exist in this order: CB arbitrage, AH premium, AB premium, monitor,
   dividend, merger.
3. CB arbitrage, AH, and AB tables support sorting, pagination, and continuous
   sequence numbering across pages.
4. Push settings can load existing config, save changes, and show success/error
   feedback.
5. Dividend page highlights today's record-date items and still shows the full
   watch list.
6. Merger page defaults to newest-first announcements and highlights same-day
   items.
7. Mobile viewport keeps one-page semantics and allows horizontal scrolling for
   long tables instead of rendering a second UI.

## Cloud rollout checklist

1. Update `config.yaml` / remote `.env` for the real server URL and reverse proxy mode.
2. Install the managed service:

```bash
sudo bash tools/deploy/install_systemd.sh
```

3. Expose the public entry with one reverse proxy:

```bash
sudo bash tools/deploy/install_nginx_site.sh alpha-monitor YOUR_DOMAIN_OR_IP 5000
```

or

```bash
sudo bash tools/deploy/install_caddy_site.sh YOUR_DOMAIN_OR_IP 5000
```

4. Run the server doctor:

```bash
bash tools/deploy/server_doctor.sh
```

5. Verify public homepage and public `/api/health`.
6. If webhook/public URL class parameters changed, sync the server `.env` directly:

```powershell
npm run sync:server:env
```
