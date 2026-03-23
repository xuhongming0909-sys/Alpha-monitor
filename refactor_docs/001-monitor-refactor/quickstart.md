# Quickstart: Alpha Monitor Dashboard Refactor

## Environment

1. Install Node.js 18+ and Python 3.
2. Install Node dependencies:

```powershell
npm install
```

3. Copy `.env.example` to `.env` when local secrets are required.

## Start the dashboard

```powershell
npm run dev
```

Open `http://127.0.0.1:5000`.

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

1. Update `config.yaml` for the real server URL and reverse proxy mode.
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
