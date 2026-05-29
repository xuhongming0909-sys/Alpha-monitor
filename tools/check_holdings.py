import json, urllib.request
# 不 force，看缓存是否已刷新
r = urllib.request.urlopen("http://43.139.35.190/api/market/lof-arbitrage", timeout=30)
d = json.loads(r.read())
print("success:", d.get("success"))
if d.get("success"):
    rows = d["data"]["rows"]
    print(f"rows={len(rows)}")
    for row in rows[:5]:
        hl = row.get("holdings") or []
        print(f"  {row['code']} {row.get('name','')} holdings={len(hl)}")
        if hl:
            print(f"    {hl[0]['name']} {hl[0]['weight']}%")