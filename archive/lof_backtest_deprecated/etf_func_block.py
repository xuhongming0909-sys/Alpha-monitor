
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
            klines = r.json().get('data', {}).get('klines', [])
            if len(klines) >= 2:
                prev = float(klines[-2].split(',')[2])
                cur = float(klines[-1].split(',')[2])
                if prev > 0:
                    changes[ticker] = (cur / prev - 1) * 100
        except Exception:
            pass
    missing = [t for t in etf_codes if t not in changes]
    if missing:
        try:
            qt_codes = [f"us{t}.us" for t in missing]
            resp = _ETF_SESSION.get(f"https://qt.gtimg.cn/q={','.join(qt_codes)}", timeout=10)
            for i, line in enumerate(resp.content.decode("gbk", errors="ignore").splitlines()):
                if i >= len(missing):
                    break
                parts = line.split("~")
                if len(parts) > 4:
                    p, c = _to_float(parts[4]), _to_float(parts[3])
                    if p and p > 0 and c:
                        changes[missing[i]] = (c / p - 1) * 100
        except Exception:
            pass
    return changes
