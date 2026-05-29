import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import _extract_holdings_sections
import pdfplumber

pdf = pdfplumber.open('runtime_data/qreport/501018_2026Q1.pdf')
full = chr(10).join([p.extract_text() or '' for p in pdf.pages])
print(f'Full text length: {len(full)}')

sections = _extract_holdings_sections(full)
print(f'Sections length: {len(sections)}')
print(f'Sections preview: {repr(sections[:500])}')

# Also check what keywords match
for kw in ['前十名股票', '前十名基金投资', '前十名债券', '前十名资产支持证券',
           '前十名证券', '期末基金投资明细', '前十名衍生', '投资组合', '期末权益',
           '基金投资明细', '期末按行业']:
    idx = full.find(kw)
    if idx >= 0:
        print(f'  "{kw}" found at {idx}')