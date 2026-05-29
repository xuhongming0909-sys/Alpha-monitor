import sys, traceback; sys.path.insert(0, '.')
import pdfplumber, httpx, json, re

# Manual debug of the parsing
pdf_path = 'runtime_data/qreport/501018_2026Q1.pdf'
code = '501018'

with pdfplumber.open(pdf_path) as pdf:
    full_text = chr(10).join([p.extract_text() or '' for p in pdf.pages])

from data_fetch.lof_iopv.report_holdings import _extract_holdings_sections
sections = _extract_holdings_sections(full_text)
print(f'Sections: {len(sections)} chars')

text_for_llm = sections if sections else full_text[:10000]
print(f'Text for LLM: {len(text_for_llm)} chars')

prompt = f'基金代码: {code}\n提取持仓JSON数组。\n\nPDF:\n{text_for_llm}'
print(f'Prompt length: {len(prompt)}')

try:
    r = httpx.post('https://api.deepseek.com/chat/completions',
        headers={'Authorization': 'Bearer sk-209491d68a0e4a18b24b1d32be416120'},
        json={'model':'deepseek-v4-flash','messages':[{'role':'user','content':prompt}],'max_tokens':3000,'temperature':0.0},
        timeout=90)
    r.raise_for_status()
    content = r.json()['choices'][0]['message']['content']
    print(f'Response length: {len(content)}')
    print(f'Response: {content[:500]}')
    
    # Try to parse
    json_match = re.search(r'\[.*\]', content, re.DOTALL)
    if json_match:
        items = json.loads(json_match.group())
        print(f'\nParsed {len(items)} items')
        for item in items[:3]:
            normalized = {str(k).strip().lower(): v for k, v in item.items()}
            print(f'  Keys: {list(normalized.keys())}')
            print(f'  Values: {list(normalized.values())}')
    else:
        print('No JSON array found in response')
except Exception as e:
    traceback.print_exc()