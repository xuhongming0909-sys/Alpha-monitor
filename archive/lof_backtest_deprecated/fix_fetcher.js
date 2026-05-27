const fs = require('fs');
const path = 'C:\\Users\\93724\\Desktop\\Alpha monitor\\data_fetch\\lof_iopv\\fetcher.py';
let content = fs.readFileSync(path, 'utf-8');

if (!content.includes('_fetch_etf_changes')) {
    const insertAfter = '    "Referer": "https://fundf10.eastmoney.com/",\n})';
    const etfCode = '\n\n# ETF\u5b9e\u65f6\u6da8\u8dcc\u5e45\u83b7\u53d6\uff08\u4e1c\u8d22\u7f8e\u80a1K\u7ebf \u2192 \u817e\u8baf\u884c\u60c5 fallback\uff09\n_ETF_SESSION = requests.Session()\n_ETF_SESSION.trust_env = False\n_ETF_SESSION.proxies = {\'http\': None, \'https\': None}\n\n\ndef _fetch_etf_changes(etf_codes: list) -> dict:\n    """\u83b7\u53d6ETF\u5b9e\u65f6\u6da8\u8dcc\u5e45\uff08\u767e\u5206\u6bd4\uff09\u3002\u4e1c\u8d22K\u7ebf\u4f18\u5148\uff0c\u817e\u8baffallback\u3002"""\n    if not etf_codes:\n        return {}\n    changes = {}\n    for ticker in etf_codes:\n        try:\n            url = (f\'https://push2his.eastmoney.com/api/qt/stock/kline/get\'\n                   f\'?secid=107.{ticker}&fields1=f1,f2,f3&fields2=f51,f52,f53,f54\'\n                   f\'&klt=101&fqt=1&beg=0&end=20500101&lmt=2\')\n            r = _ETF_SESSION.get(url, timeout=10)\n            data = r.json().get(\'data\', {})\n            klines = data.get(\'klines\', [])\n            if len(klines) >= 2:\n                prev = float(klines[-2].split(\',\')[2])\n                cur = float(klines[-1].split(\',\')[2])\n                if prev > 0:\n                    changes[ticker] = (cur / prev - 1) * 100\n        except Exception:\n            pass\n    missing = [t for t in etf_codes if t not in changes]\n    if missing:\n        try:\n            qt_codes = [f"us{t}.us" for t in missing]\n            text = _ETF_SESSION.get(f"https://qt.gtimg.cn/q={\','.join(qt_codes)}", timeout=10).content.decode("gbk", errors="ignore")\n            for i, line in enumerate(text.splitlines()):\n                if i >= len(missing):\n                    break\n                parts = line.split("~")\n                if len(parts) > 4:\n                    prev = _to_float(parts[4])\n                    cur = _to_float(parts[3])\n                    if prev and prev > 0 and cur:\n                        changes[missing[i]] = (cur / prev - 1) * 100\n        except Exception:\n            pass\n    return changes\n\n';
    content = content.replace(insertAfter, insertAfter + etfCode);
    console.log('Step 1: ETF fetcher added');
} else { console.log('Step 1: skip'); }

if (!content.includes('etf_changes = _fetch_etf_changes')) {
    const old = '    # \u4ece\u96c6\u601d\u5f55\u83b7\u53d6\u9650\u989d\u6570\u636e\n    jisilu_data = _fetch_jisilu_qdii()\n\n    all_rows = []';
    const rep = '    # \u4ece\u96c6\u601d\u5f55\u83b7\u53d6\u9650\u989d\u6570\u636e\n    jisilu_data = _fetch_jisilu_qdii()\n\n    # A\u7c7bETF\u5b9e\u65f6\u6da8\u8dcc\u5e45\n    etf_codes = list({f.get("etf") for f in QDII_FUNDS if f.get("etf") and f.get("estimation") == "A"})\n    etf_changes = _fetch_etf_changes(etf_codes)\n\n    all_rows = []';
    content = content.replace(old, rep);
    console.log('Step 2: ETF call added');
} else { console.log('Step 2: skip'); }

if (!content.includes('"etfChange"')) {
    const old = '            "fundCompany": fund_info.get("fundCompany"),\n        })';
    const rep = '            "fundCompany": fund_info.get("fundCompany"),\n            "etfChange": etf_changes.get(fund.get("etf")),\n        })';
    content = content.replace(old, rep);
    console.log('Step 3: etfChange field added');
} else { console.log('Step 3: skip'); }

if (!content.includes('holdingsPrevClose')) {
    const old = '                    if tc in quotes:\n                        current_prices[h["ticker"]] = quotes[tc].get("price")';
    const rep = '                    if tc in quotes:\n                        current_prices[h["ticker"]] = quotes[tc].get("price")\n                        if quotes[tc].get("prev_close"):\n                            current_prices.setdefault("_prev_close", {})[h["ticker"]] = quotes[tc]["prev_close"]';
    content = content.replace(old, rep);
    const old2 = '            "stockPosition": stock_position,';
    const rep2 = '            "stockPosition": stock_position,\n            "holdingsPrevClose": current_prices.pop("_prev_close", None),';
    content = content.replace(old2, rep2);
    console.log('Step 4: holdingsPrevClose added');
} else { console.log('Step 4: skip'); }

fs.writeFileSync(path, content, 'utf-8');
console.log('fetcher.py saved');
