#!/bin/bash
sleep 2
curl -s "http://localhost:8888/search?q=ProShares+oil+ETF+UCO&format=json" > /tmp/r.json
python3 -c "
import json
d = json.load(open('/tmp/r.json'))
r = d.get('results', [])
u = d.get('unresponsive_engines', [])
print('Results:', len(r))
print('Unresponsive:', [e[0] for e in u])
for x in r[:5]:
    print(' ', x.get('title','')[:80])
    print('   ', x.get('url','')[:80])
"