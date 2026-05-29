import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import (
    fetch_latest_report_id, download_report_pdf,
    deepseek_parse_holdings, fetch_top10_stocks
)

# Test with 161128 - has known stock holdings in PDF
code = '161128'
print(f'=== Testing {code} ===')
rid = fetch_latest_report_id(code)
print(f'Report ID: {rid}')

if rid:
    pdf = download_report_pdf(rid)
    print(f'PDF: {pdf}')
    if pdf:
        holdings = deepseek_parse_holdings(pdf, code)
        print(f'DeepSeek extracted {len(holdings)} holdings:')
        tw = sum(h['weight'] for h in holdings)
        print(f'Total weight: {tw:.1f}%')
        for h in holdings:
            print(f'  {h["ticker"]:10s} {h["name"]:30s} {h["weight"]:6.2f}% {h["market"]:3s} ({h["type"]})')