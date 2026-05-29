import os
path = os.path.join(r'C:\Users\93724\Desktop\Alpha monitor', 'data_fetch', 'lof_iopv', 'fetcher.py')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: ETF fetcher function
if '_fetch_etf_changes' not in content:
    marker = '    "Referer": "https://fundf10.eastmoney.com/",\n})'
    etf_func = '''

# ETF实时涨跌幅获取（东财美股K线 → 腾讯行情 fallback）
_ETF_SESSION = requests.Session()
_ETF_SESSION.trust_env = False
_ETF_SESSION.proxies = {'http': None, 'https': None}


def _fetch_etf_changes(etf_codes: list) -> dict:
    """获取ETF实时涨跌幅（百分比）。东财K线优先，腾讯fallback。"""
    if not etf_codes:
        return {}
    changes = {}
    for ticker in etf_codes:
        try:
            url = (f'https://push2his.eastmoney.com/api/qt/stock/kline/get'
                   f'?secid=107.{ticker}&fields1=f1,f2,f3&fields2=f51,f52,f53,f54'
                   f'&klt=101&fqt=1&beg=0&end=20500101&lmt=2')
            r = _ETF_SESSION.get(url, timeout=10)
            data = r.json().get('data', {})
            klines = data.get('klines', [])
            if len(klines) >= 2:
                prev = float(klines[-2].split(',')[2])
                cur = float(klines[-1].split(',')[2])
                if prev > 0:
                    changes[ticker] = (cur / prev - 1) * 100
        except Exception:
            pass
    # 腾讯 fallback
    missing = [t for t in etf_codes if t not in changes]
    if missing:
        try:
            qt_codes = [f"us{t}.us" for t in missing]
            resp = _ETF_SESSION.get(f"https://qt.gtimg.cn/q={','.join(qt_codes)}", timeout=10)
            text = resp.content.decode("gbk", errors="ignore")
            for i, line in enumerate(text.splitlines()):
                if i >= len(missing):
                    break
                parts = line.split("~")
                if len(parts) > 4:
                    prev = _to_float(parts[4])
                    cur = _to_float(parts[3])
                    if prev and prev > 0 and cur:
                        changes[missing[i]] = (cur / prev - 1) * 100
        except Exception:
            pass
    return changes

'''
    content = content.replace(marker, marker + etf_func)
    print('Step 1: ETF fetcher function added')
else:
    print('Step 1: skip')

# Step 2: ETF call in snapshot
if 'etf_changes = _fetch_etf_changes' not in content:
    old = '    # 从集思录获取限额数据\n    jisilu_data = _fetch_jisilu_qdii()\n\n    all_rows = []'
    new = ('    # 从集思录获取限额数据\n    jisilu_data = _fetch_jisilu_qdii()\n\n'
           '    # A类ETF实时涨跌幅\n'
           '    etf_codes = list({f.get("etf") for f in QDII_FUNDS if f.get("etf") and f.get("estimation") == "A"})\n'
           '    etf_changes = _fetch_etf_changes(etf_codes)\n\n'
           '    all_rows = []')
    content = content.replace(old, new)
    print('Step 2: ETF call added')
else:
    print('Step 2: skip')

# Step 3: etfChange in output
if '"etfChange"' not in content:
    old = '            "fundCompany": fund_info.get("fundCompany"),\n        })'
    new = '            "fundCompany": fund_info.get("fundCompany"),\n            "etfChange": etf_changes.get(fund.get("etf")),\n        })'
    content = content.replace(old, new)
    print('Step 3: etfChange field added')
else:
    print('Step 3: skip')

# Step 4: holdingsPrevClose for B类
if 'holdingsPrevClose' not in content:
    old = '                    if tc in quotes:\n                        current_prices[h["ticker"]] = quotes[tc].get("price")'
    new = ('                    if tc in quotes:\n'
           '                        current_prices[h["ticker"]] = quotes[tc].get("price")\n'
           '                        if quotes[tc].get("prev_close"):\n'
           '                            current_prices.setdefault("_prev_close", {})[h["ticker"]] = quotes[tc]["prev_close"]')
    content = content.replace(old, new)
    
    old2 = '            "stockPosition": stock_position,'
    new2 = '            "stockPosition": stock_position,\n            "holdingsPrevClose": current_prices.pop("_prev_close", None),'
    content = content.replace(old2, new2)
    print('Step 4: holdingsPrevClose added')
else:
    print('Step 4: skip')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('fetcher.py saved')