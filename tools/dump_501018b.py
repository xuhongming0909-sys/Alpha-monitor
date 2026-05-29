import pdfplumber
# Check the other PDF file
pdf = pdfplumber.open('runtime_data/qreport/501018_2026Q1.pdf')
full = chr(10).join([p.extract_text() or '' for p in pdf.pages])
print(f'Pages: {len(pdf.pages)}, chars: {len(full)}')
# Search for fund/ETF keywords
for kw in ['前十名基金','基金投资明细','USO','BNO','United States Oil','Brent','ETF','WisdomTree','Samsung','Simplex','DB Oil']:
    idx = full.find(kw)
    if idx >= 0:
        print(f'\n=== {kw} at {idx} ===')
        print(full[max(0,idx-50):idx+300])