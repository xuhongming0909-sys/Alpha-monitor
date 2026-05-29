#!/bin/bash
sleep 4
curl -s "http://localhost:8888/search?q=ProShares+oil+ETF+UCO+ticker&format=json" > /tmp/searx_r.json
python3 << 'PY'
import json
with open("/tmp/searx_r.json") as f:
    d = json.load(f)
r = d.get("results", [])
u = d.get("unresponsive_engines", [])
print(f"Results: {len(r)}")
print(f"Unresponsive: {[e[0] for e in u]}")
for x in r[:5]:
    print(f"  {x.get('title','')[:80]}")
    print(f"    {x.get('url','')[:80]}")
PY