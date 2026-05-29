export default async function handler(req, res) {
  const { path } = req.query;
  const subpath = Array.isArray(path) ? path.join("/") : path || "";
  const qs = req.url.includes("?") ? req.url.split("?")[1] : "";
  const target = "https://query1.finance.yahoo.com/" + subpath + (qs ? "?" + qs : "");
  try {
    const resp = await fetch(target, {
      headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" },
    });
    const data = await resp.text();
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Content-Type", "application/json");
    res.status(resp.status).send(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}