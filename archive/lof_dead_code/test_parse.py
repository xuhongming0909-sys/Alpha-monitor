import sys, traceback; sys.path.insert(0, '.')
import json, re

# Simulate the parsing logic
content = '''[
  {"序号": 1, "基金名称": "WisdomTree WTI ETF", "基金类型": "ETF", "运作方式": "开放式", "管理人": "WisdomTree ETF Management Jersey Ltd", "公允价值": 386932195.35, "占基金资产净值比例": 19.80},
  {"序号": 2, "基金名称": "WisdomTree Brent ETF", "基金类型": "ETF", "运作方式": "开放式", "管理人": "WisdomTree ETF Management Jersey Ltd", "公允价值": 375177030.96, "占基金资产净值比例": 19.20},
  {"序号": 3, "基金名称": "United States Oil Fund LP", "基金类型": "ETF", "运作方式": "开放式", "管理人": "Commodity Funds LLC", "公允价值": 372566800.10, "占基金资产净值比例": 19.06}
]'''

items = json.loads(content)
for item in items:
    normalized = {str(k).strip().lower(): v for k, v in item.items()}
    print(f'Keys: {list(normalized.keys())}')
    
    # Test ticker extraction
    ticker = ""
    for key in ["ticker", "代码", "证券代码", "code"]:
        if normalized.get(key):
            ticker = str(normalized[key]).strip()
            break
    print(f'  ticker: "{ticker}" (empty={not ticker})')
    
    # Test name extraction
    name = ""
    for key in ["name", "名称", "基金名称", "股票名称", "证券名称"]:
        if normalized.get(key):
            name = str(normalized[key]).strip()
            break
    print(f'  name: "{name}"')
    
    # Test weight extraction
    weight = 0
    for key in ["weight", "占比", "占净值比例", "比例", "占基金资产净值比例", "占净值"]:
        val = normalized.get(key)
        if val is not None:
            try:
                weight = float(str(val).replace("%","").strip())
                print(f'  weight: {weight} (from key "{key}")')
                break
            except:
                continue
    
    # Condition: if not ticker or weight <= 0: continue
    if not ticker or weight <= 0:
        print(f'  SKIP: ticker="{ticker}", weight={weight}')
    else:
        print(f'  KEEP')
    print()