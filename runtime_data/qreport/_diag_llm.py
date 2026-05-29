# -*- coding: utf-8 -*-
"""诊断纯文本LLM失败原因"""
import fitz, os, json, httpx, re, yaml, sys

PDF_DIR = "runtime_data/qreport"
KWS = ["前十名股票", "前十名基金投资", "前十名权益投资", "前十名资产支持证券",
       "基金投资明细", "权益投资明细", "股票及存托凭证投资明细", "债券投资明细", "占基金资产净值比例"]

LLM_PROMPT = """你是基金持仓数据提取专家。
从基金季报文本中提取所有持仓（股票、ETF、基金、债券）。
只返回JSON数组，不要markdown代码块、不要解释。

Schema: [{"t":"代码","n":"名称","w":数字,"m":"市场","tp":"类型"}]

t必须是短代码，不是名称：
- 美股ETF: ARKK,ARKG,ARKQ,ARKW,ARKF,QQQ,SOXX,SMH,BOTZ,AIQ,XLK,FINX,PSI,SOXQ,
  XOP,XLE,VDE,IYE,IXC,USO,BNO,GLD,IAU,CRUD,BRNT,OILK,DBO
- 美股: NVDA,MSFT,AAPL,AMZN,GOOGL,META,TSLA
- 港股: 5位数(00883,00857)
- A股ETF: 159995(景顺芯片),159881(华夏芯片),512760(国泰芯片),512480(半导体)
- 日本ETF: SimpleXWTI, NOMURA_CRUDE, UBS_CMCI
- 无法确定填""
- 例: "WisdomTree WTI Crude Oil"→CRUD, "United States Oil Fund"→USO,
  "CNOOC Ltd"代码883→00883, "Invesco DB Oil"→DBO

n: 原始完整名称
w: 占基金资产净值比例，纯数字不带%
m: US/HK/A
tp: stock/fund/bond

排除：银行存款、结算备付金、货币市场、应收类、待摊费用、其他资产、合计、买入返售。
注意：同一名称不同货币版本(如WisdomTree Brent USD/GBP)是不同持仓，都要提取。"""

with open("config/secrets.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
vcfg = cfg.get("vision", {})
api_key = vcfg.get("api_key", "")
base_url = vcfg.get("base_url", "https://token-plan-cn.xiaomimimo.com/v1/chat/completions")
model = vcfg.get("model", "mimo-v2.5")

url = base_url if "/chat/completions" in base_url else base_url.rstrip("/") + "/chat/completions"

results = {}
for fname in sorted(os.listdir(PDF_DIR)):
    if not fname.endswith(".pdf"):
        continue
    fund = fname.split("_")[0]
    path = os.path.join(PDF_DIR, fname)
    doc = fitz.open(path)
    pages = set()
    for i, page in enumerate(doc):
        txt = page.get_text()
        for kw in KWS:
            if kw in txt:
                pages.add(i)
                if i+1 < len(doc):
                    pages.add(i+1)
                break
    pages = sorted(pages)[:6]
    combined = ""
    for pi in pages:
        t = doc[pi].get_text().strip()
        if t:
            combined += t + "\n\n"
    doc.close()

    if len(combined) < 100:
        results[fund] = {"error": "text too short", "text_len": len(combined)}
        continue

    # call LLM
    try:
        r = httpx.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user",
                              "content": f"{LLM_PROMPT}\n\n基金代码: {fund}\n\n季报文本:\n{combined}"}],
                "max_tokens": 2000,
                "temperature": 0.0,
            },
            timeout=90,
        )
        resp = r.json()
        content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # parse
        jm = re.search(r'\[.*\]', content, re.DOTALL)
        parsed = []
        if jm:
            try:
                parsed = json.loads(jm.group())
            except:
                parsed = ["JSON_PARSE_ERROR"]

        results[fund] = {
            "status": r.status_code,
            "raw_content": content[:2000],
            "parsed_count": len(parsed) if isinstance(parsed, list) else -1,
            "parsed_preview": parsed[:5] if isinstance(parsed, list) else str(parsed),
        }
    except Exception as e:
        results[fund] = {"error": str(e)}

with open("runtime_data/qreport/_diag_llm.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("done - see _diag_llm.json")