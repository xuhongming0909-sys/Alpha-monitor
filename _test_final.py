import sys
sys.stdout.reconfigure(encoding='utf-8')
from data_fetch.lof_iopv.fetcher import fetch_lof_iopv_snapshot
from data_fetch.lof_iopv.normalizer import normalize_lof_iopv_snapshot
from strategy.lof_iopv.service import build_lof_iopv_response

payload = fetch_lof_iopv_snapshot()
records = normalize_lof_iopv_snapshot(payload)
result = build_lof_iopv_response(payload, records)
rows = result.get("data", {}).get("rows", [])

required = ["code","name","currency","nav","navDate","price","iopv","premiumRate",
            "applyFee","applyStatus","redeemFee","redeemStatus","custodianFee",
            "fundCompany","calcMode","calcStatus","stockPosition","holdings"]
print(f"Total: {len(rows)}")
for k in required:
    count = sum(1 for row in rows if row.get(k) is not None)
    print(f"  {k}: {count}/{len(rows)}")

# Show first row
if rows:
    r = rows[0]
    print(f"\nSample: {r.get('code')} {r.get('name')}")
    for k in required:
        v = r.get(k)
        if k == "holdings":
            print(f"  {k}: {len(v) if v else 0} items")
        else:
            print(f"  {k}: {v}")