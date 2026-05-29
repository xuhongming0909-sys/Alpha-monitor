#!/bin/bash
curl -s "http://localhost:8888/search?q=QDII+LOF+fund&format=json&pageno=1" > /tmp/searx_result.json
python3 << 'PYEOF'
import json
with open("/tmp/searx_result.json") as f:
    d = json.load(f)
results = d.get("results", [])
print(f"Found {len(results)} results")
for r in results[:5]:
    print(f"  Title: {r.get('title','')[:80]}")
    print(f"  URL: {r.get('url','')[:80]}")
    print()
PYEOF