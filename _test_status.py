import sys, re, requests
sys.stdout.reconfigure(encoding='utf-8')
SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fundf10.eastmoney.com/'})

code = "160644"
url = f"https://fundf10.eastmoney.com/jbgk_{code}.html"
text = SESSION.get(url, timeout=10).content.decode("utf-8", errors="ignore")

# Find apply/redeem status
for pattern in [
    r'申购状态.*?>(.*?)<',
    r'赎回状态.*?>(.*?)<',
    r'开放申购',
    r'暂停申购',
    r'开放赎回',
    r'暂停赎回',
]:
    m = re.search(pattern, text, re.DOTALL)
    if m:
        print(f"Pattern: {pattern[:30]} -> {m.group(1) if m.lastindex else 'found'}")

# Try broader search
idx = text.find("申购")
if idx > 0:
    print(f"\n申购 context: ...{text[idx-20:idx+80]}...")
idx2 = text.find("赎回")
if idx2 > 0:
    print(f"赎回 context: ...{text[idx2-20:idx2+80]}...")