import urllib.request, json

proxy = urllib.request.ProxyHandler({"https":"http://127.0.0.1:7890","http":"http://127.0.0.1:7890"})
opener = urllib.request.build_opener(proxy)

queries = [
    "akshare",
    "yfinance",
    "stock sina api python",
    "eastmoney python stock",
    "US ETF historical data",
]

for q in queries:
    url = "https://api.github.com/search/repositories?q=" + q + "&sort=stars&per_page=5"
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    resp = opener.open(req, timeout=15)
    data = json.loads(resp.read())
    total = data.get("total_count", 0)
    print("=== " + q + " (total:" + str(total) + ") ===")
    for x in data.get("items", []):
        name = x["full_name"]
        stars = x["stargazers_count"]
        desc = (x.get("description") or "")[:100]
        topics = ", ".join((x.get("topics") or [])[:5])
        print("  " + name + " stars=" + str(stars))
        print("    " + desc)
        if topics:
            print("    topics: " + topics)
