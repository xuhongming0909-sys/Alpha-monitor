import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import _extract_holdings_sections
import pdfplumber

pdf = pdfplumber.open('runtime_data/qreport/501018_2026Q1.pdf')
full = chr(10).join([p.extract_text() or '' for p in pdf.pages])
sections = _extract_holdings_sections(full)

# Check if key data is in sections
for kw in ['WisdomTree', 'United States Oil', 'Brent', 'USO', 'BNO', '19.80', '19.20', '19.06']:
    if kw in sections:
        print(f'  FOUND: {kw}')
    else:
        print(f'  MISSING: {kw}')

print(f'\nSection length: {len(sections)}')
print(f'Last 500 chars:')
print(sections[-500:])