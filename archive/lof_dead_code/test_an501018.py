import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import fetch_latest_report_id, download_report_pdf, deepseek_parse_holdings, _deepseek_parse_full_text
rid = fetch_latest_report_id('501018')
print(f'Report ID: {rid}')
pdf = download_report_pdf(rid)
print(f'PDF: {pdf}')
if pdf:
    h1 = deepseek_parse_holdings(pdf, '501018')
    print(f'section: {len(h1) if h1 else "None"}')
    h2 = _deepseek_parse_full_text(pdf, '501018')
    print(f'fulltext: {len(h2) if h2 else "None"}')
    if h2:
        for x in h2: print(f'  {x}')