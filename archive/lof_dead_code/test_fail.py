import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import (
    fetch_top10_stocks, fetch_latest_report_id, download_report_pdf,
    deepseek_parse_holdings, _extract_holdings_sections
)
import pdfplumber

fail_codes = ['501300', '164824', '160723', '501018', '160719']
for code in fail_codes:
    print(f'\n=== {code} ===')
    # Check if we have a cached PDF
    rid = fetch_latest_report_id(code)
    print(f'  Report ID: {rid}')
    if rid:
        pdf = download_report_pdf(rid)
        print(f'  PDF: {pdf}')
        if pdf:
            with pdfplumber.open(pdf) as p:
                full = chr(10).join([pg.extract_text() or '' for pg in p.pages])
                print(f'  Pages: {len(p.pages)}, chars: {len(full)}')
                sections = _extract_holdings_sections(full)
                print(f'  Holdings sections length: {len(sections)}')
                if sections:
                    print(f'  First 300 chars: {sections[:300]}')
                else:
                    # Search for any holdings keywords
                    for kw in ['前十名','持仓','股票','基金投资','ETF']:
                        idx = full.find(kw)
                        if idx >= 0:
                            print(f'  Found "{kw}" at {idx}')
                            print(f'  Context: {full[idx:idx+200]}')
                            break