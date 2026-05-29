import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import _extract_holdings_sections
import pdfplumber, httpx, json, re

pdf_path = 'runtime_data/qreport/501018_2026Q1.pdf'
code = '501018'

with pdfplumber.open(pdf_path) as pdf:
    full_text = chr(10).join([p.extract_text() or '' for p in pdf.pages])

sections = _extract_holdings_sections(full_text)
print(f'Sections length: {len(sections)}')
print(f'Has WisdomTree: {"WisdomTree" in sections or "Wisdom" in sections}')
print(f'Has 19.80: {"19.80" in sections}')

# Show sections around the data
for kw in ['19.80', 'Wisdom', 'Brent', 'United']:
    idx = sections.find(kw)
    if idx >= 0:
        print(f'\n=== {kw} at {idx} ===')
        print(sections[max(0,idx-100):idx+300])
        break

# Now actually call DeepSeek with debug
prompt = f'基金代码: {code}\n\n提取持仓JSON数组。\n\nPDF:\n{sections}'
print(f'\nPrompt length: {len(prompt)}')

r = httpx.post('https://api.deepseek.com/chat/completions',
    headers={'Authorization': 'Bearer sk-209491d68a0e4a18b24b1d32be416120'},
    json={'model':'deepseek-v4-flash','messages':[{'role':'user','content':prompt}],'max_tokens':3000,'temperature':0.0},
    timeout=90)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    content = r.json()['choices'][0]['message']['content']
    print(f'Response: {content[:1000]}')
else:
    print(f'Error: {r.text[:500]}')