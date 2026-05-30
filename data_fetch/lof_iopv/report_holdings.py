# -*- coding: utf-8 -*-
# AI-SUMMARY: 持仓提取 - PDF渲染→Vision LLM提取→文本LLM兜底→直接覆盖DB
# 对应 INDEX.md §9.3 文件摘要索引
"""持仓提取器：PDF渲染→Vision LLM→文本LLM兜底→直接覆盖DB。"""
from __future__ import annotations

import base64
import io
import json
import os
import re
import sqlite3
import sys
from datetime import datetime
import time
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import httpx
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0"})

_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'lof_db', 'lof.db')
_PDF_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'qreport')
_CONCURRENCY = 5

_SECTION_KW = [
    "前十名股票", "前十名基金投资", "前十名权益投资",
    "前十名资产支持证券", "基金投资明细", "权益投资明细",
    "股票及存托凭证投资明细", "债券投资明细", "占基金资产净值比例",
]

_LLM_PROMPT = """你是基金持仓数据提取专家。从基金季报PDF中提取所有持仓的名称和净值占比。

你的唯一任务：从PDF中抄写持仓名称和对应比例。不要猜测任何代码。

输出格式（纯JSON数组，不要任何其他文字）：
[{"name":"PDF原文中的完整名称","weight":数字}]

规则：
1. name必须是PDF中显示的原始名称（合并跨行），一字不改
2. weight是占基金资产净值比例%，纯数字
3. 必须提取每一条持仓，不能遗漏
4. 股票、ETF、ETC、基金、债券都算持仓
5. 排除：银行存款、结算备付金、货币基金、应收类、其他资产
6. 不要输出任何代码字段，代码会在后续步骤中查找
"""


# ============================================================
# 配置加载
# ============================================================

def _load_secrets() -> dict:
    import yaml
    p = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'secrets.yaml')
    if not os.path.exists(p):
        return {}
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _vision_config() -> dict:
    return _load_secrets().get('vision', {})



# ============================================================
# PDF处理
# ============================================================

def _find_holdings_pages(pdf_path: str) -> List[int]:
    """找到包含持仓关键词的页码（含下一页）。"""
    doc = fitz.open(pdf_path)
    pages = set()
    for i, page in enumerate(doc):
        if any(kw in page.get_text() for kw in _SECTION_KW):
            pages.add(i)
            if i + 1 < len(doc):
                pages.add(i + 1)
    doc.close()
    return sorted(pages)[:6]


def _render_pages(pdf_path: str) -> Optional[str]:
    """渲染持仓页为base64 JPEG。"""
    try:
        from PIL import Image as PILImage
    except ImportError:
        return None
    doc = fitz.open(pdf_path)
    pages = _find_holdings_pages(pdf_path)
    if not pages:
        doc.close()
        return None
    imgs = []
    for pi in pages:
        if pi < len(doc):
            pix = doc[pi].get_pixmap(dpi=200)
            imgs.append(PILImage.frombytes('RGB', [pix.width, pix.height], pix.samples))
    doc.close()
    if not imgs:
        return None
    gap = 10
    total_h = sum(im.height for im in imgs) + gap * (len(imgs) - 1)
    max_w = max(im.width for im in imgs)
    combined = PILImage.new('RGB', (max_w, total_h), 'white')
    y = 0
    for im in imgs:
        combined.paste(im, (0, y))
        y += im.height + gap
    buf = io.BytesIO()
    combined.save(buf, format='JPEG', quality=75)
    return base64.b64encode(buf.getvalue()).decode()


# ============================================================
# LLM调用
# ============================================================

def _parse_json(content: str) -> List[Dict]:
    """从LLM返回中解析JSON数组。LLM只输出name+weight，ticker由后续步骤补全。"""
    content = content.strip()
    content = re.sub(r'^```json\s*', '', content)
    content = re.sub(r'\s*```$', '', content)
    jm = re.search(r'\[.*\]', content, re.DOTALL)
    if not jm:
        print(f"  [debug] LLM返回无JSON数组: {content[:200]}")
        return []
    try:
        items = json.loads(jm.group())
    except json.JSONDecodeError:
        print(f"  [debug] JSON解析失败: {jm.group()[:200]}")
        return []
    valid = []
    for item in items:
        name = str(item.get("name", "")).strip()
        try:
            weight = float(item.get("weight", 0))
        except (ValueError, TypeError):
            continue
        if not name or weight <= 0:
            continue
        # ticker/market 由 _guess_ticker 兜底（返回 "TICKER|MARKET" 或空）
        guessed = _guess_ticker(name)
        if "|" in guessed:
            ticker, market = guessed.split("|", 1)
        else:
            ticker, market = guessed, ""
        valid.append({"ticker": ticker, "name": name, "weight": weight, "market": market})
    return valid


def _guess_ticker(name: str) -> str:
    """从名称推断ticker+market。本地映射表覆盖已知ETF/ETC，其余返回空。"""
    nu = name.upper()
    # 精确+模糊映射: (关键词, ticker, market)
    _MAP = [
        # 原油ETC/ETF
        ("WISDOMTREE WTI CRUDE", "CRUD", "UK"),
        ("WISDOMTREE BRENT", "BRNT", "UK"),
        ("PROSHARES K-1 FREE CRUDE", "FREE", "US"),
        ("UNITED STATES OIL", "USO", "US"),
        ("UNITED STATES BRENT OIL", "BNO", "US"),
        ("SIMPLEX WTI", "SimpleXWTI", "UK"),
        ("OILK", "OILK", "US"),
        # 大宗商品
        ("SAMSUNG S&P GSCI", "GSCI", "UK"),
        ("COLLATERALIZED ETC", "BRNT", "UK"),
        ("COLLATERISED ETC", "BRNT", "UK"),
        # 板块ETF
        ("STATE STREET ENERGY", "XLE", "US"),
        ("SPDR S&P OIL", "XOP", "US"),
        ("VAN ECK OIL", "OIH", "US"),
        ("ISHARES GLOBAL ENERGY", "IXC", "US"),
        # 股票
        ("APPLE", "AAPL", "US"),
        ("MICROSOFT", "MSFT", "US"),
        ("NVIDIA", "NVDA", "US"),
        ("TSMC", "2330", "HK"),
        ("SAMSUNG ELECTRONICS", "005930", "HK"),
        ("SAP SE", "SAP", "US"),
        ("AIRBUS", "AIR", "US"),
        ("HSBC", "HSBA", "UK"),
        ("TOYOTA", "7203", "HK"),
        ("TENCENT", "0700", "HK"),
        ("中国海洋石油", "0883", "HK"),
        ("中海油", "0883", "HK"),
        ("中国石油天然气", "601857", "A"),
        ("中国石化", "600028", "A"),
        ("中国神华", "601088", "A"),
        ("ALIBABA", "BABA", "US"),
        ("SAMSUNG SDS", "018260", "HK"),
        ("SK HYNIX", "000660", "HK"),
        # 指数ETF
        ("SPDR S&P 500", "SPY", "US"),
        ("INVESCO QQQ", "QQQ", "US"),
        ("ISHARES RUSSELL", "IWM", "US"),
        # 宽基
        ("INDA", "INDA", "US"),
        ("ISHARES US REAL ESTATE", "IYR", "US"),
    ]
    for keyword, ticker, market in _MAP:
        if keyword in nu:
            return f"{ticker}|{market}"
    # 5位数字=港股代码
    import re
    m = re.search(r'\b(\d{5})\b', name)
    if m:
        return f"{m.group(1)}|HK"
    # 6位数字=A股代码
    m = re.search(r'\b(\d{6})\b', name)
    if m:
        return f"{m.group(1)}|A"
    return ""
def _call_vision_llm(b64_image: str, fund_code: str) -> List[Dict]:
    """Vision LLM（mimo-v2.5）提取持仓。"""
    cfg = _vision_config()
    if not cfg.get('api_key'):
        return []
    url = cfg.get('base_url', '')
    r = httpx.post(
        url,
        headers={"Authorization": f"Bearer {cfg['api_key']}"},
        json={
            "model": cfg.get('model', 'mimo-v2.5'),
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": _LLM_PROMPT + f"\n\n基金代码: {fund_code}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
            ]}],
            "max_tokens": 50000,
            "temperature": 0.0,
        },
        timeout=120,
    )
    r.raise_for_status()
    content = r.json()['choices'][0]['message']['content']
    return _parse_json(content)


# ============================================================
# 去重
# ============================================================

def _dedup(items: List[Dict]) -> List[Dict]:
    """同一ticker取最大weight。"""
    best = {}
    for item in items:
        t = item["ticker"]
        if t not in best or item["weight"] > best[t]["weight"]:
            best[t] = item
    return list(best.values())


# ============================================================
# DB覆盖写入
# ============================================================

def _report_date_from_path(pdf_path: str) -> str:
    """从PDF文件名推导报告期。如 160723_2026Q1.pdf → 2026-03-31"""
    basename = os.path.basename(pdf_path)
    m = re.search(r'(\d{4})Q(\d)', basename)
    if not m:
        return datetime.now().strftime('%Y-%m-%d')
    year, q = int(m.group(1)), int(m.group(2))
    q_end = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
    return f"{year}-{q_end.get(q, '03-31')}"


def save_to_db(code: str, holdings: List[Dict], pdf_path: str) -> int:
    """覆盖写入DB。DELETE旧数据+INSERT新数据。返回写入条数。"""
    if not holdings:
        return 0
    report_date = _report_date_from_path(pdf_path)
    db = sqlite3.connect(_DB_PATH)
    try:
        db.execute("DELETE FROM holdings WHERE code = ? AND report_date = ?", (code, report_date))
        for h in holdings:
            db.execute(
                "INSERT INTO holdings (code, report_date, ticker, name, weight, market) VALUES (?, ?, ?, ?, ?, ?)",
                (code, report_date, h["ticker"], h["name"], h["weight"], h["market"]),
            )
        db.commit()
        return len(holdings)
    finally:
        db.close()


# ============================================================
# 主流程
# ============================================================


def get_fund_holdings(code: str) -> Tuple[List[Dict], Optional[str]]:
    """
    提取单只基金持仓。
    返回: (holdings列表, 错误信息)
    """
    import glob
    pdf_path = None
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        matches = glob.glob(os.path.join(_PDF_DIR, f"{code}_*{q}*.pdf"))
        if matches:
            pdf_path = max(matches, key=os.path.getmtime)
            break

    if not pdf_path:
        return [], f"无PDF文件: {code}"

    items = None

    # 1. Vision LLM（优先）
    b64 = _render_pages(pdf_path)
    if b64:
        try:
            items = _call_vision_llm(b64, code)
            if items:
                items = _dedup(items)
        except Exception as e:
            print(f"  {code}: vision失败: {e}")

    if not items:
        return [], f"提取失败: {code}"

    # Yahoo resolve: 为无ticker的持仓补全ticker+market
    items = _resolve_tickers(items, code)

    total = sum(h["weight"] for h in items)
    print(f"  {code}: {len(items)}条 占比{total:.1f}%")
    return items, None


def _resolve_tickers(items: List[Dict], code: str) -> List[Dict]:
    """用Yahoo搜索为无ticker的持仓补全。已有ticker的保留。"""
    try:
        from data_fetch.lof_iopv.yahoo_finance import search_ticker, determine_market_from_ticker
    except ImportError:
        return items

    resolved = 0
    for h in items:
        if h.get("ticker"):
            continue
        name = h.get("name", "")
        if not name:
            continue
        result = search_ticker(name)
        if result:
            h["ticker"] = result["ticker"]
            h["market"] = result["market"]
            h["yahoo_symbol"] = result["yahoo_symbol"]
            resolved += 1
            print(f"    {code}: Yahoo resolve '{name}' -> {result['ticker']} ({result['market']})")
        time.sleep(0.5)

    if resolved:
        print(f"  {code}: Yahoo resolve 补全 {resolved}/{len(items)} 条")
    return items


def _process_one(code: str) -> Tuple[str, Dict]:
    """处理单只基金：提取+覆盖写入DB。"""
    try:
        holdings, error = get_fund_holdings(code)
        if error:
            return code, {"ok": False, "error": error}
        if not holdings:
            return code, {"ok": False, "error": f"{code}: 0条持仓"}
        import glob
        pdf_path = None
        for q in ["Q1", "Q2", "Q3", "Q4"]:
            matches = glob.glob(os.path.join(_PDF_DIR, f"{code}_*{q}*.pdf"))
            if matches:
                pdf_path = max(matches, key=os.path.getmtime)
                break
        if pdf_path:
            n = save_to_db(code, holdings, pdf_path)
            return code, {"ok": True, "holdings": n}
        return code, {"ok": False, "error": f"{code}: 无PDF路径"}
    except Exception as e:
        return code, {"ok": False, "error": str(e)}

def update_all_holdings(fund_codes: List[str], concurrency: int = _CONCURRENCY):
    """并发更新所有基金持仓。"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from data_fetch.lof_db.schema import init_db
    init_db()
    results = {}
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(_process_one, code): code for code in fund_codes}
        for future in as_completed(futures):
            code, result = future.result()
            results[code] = result
            if result["ok"]:
                print(f"  {code} OK: {result['holdings']}条持仓已写入DB")
            else:
                print(f"  {code} FAIL: {result.get('error', '')}")
    return results


# ============================================================
# PDF下载工具
# ============================================================

def fetch_latest_report_id(code: str) -> Optional[str]:
    try:
        r = SESSION.get("https://reportapi.eastmoney.com/report/list", params={
            "cb": "datatable", "industryCode": "*", "pageSize": 5,
            "industry": "*", "rating": "*", "ratingChange": "*",
            "beginTime": "", "endTime": "", "pageNo": 1, "fields": "",
            "qType": 0, "orgCode": "", "code": code,
            "rcode": "", "p": 1, "pageNum": 1, "pageNumber": 1,
        }, timeout=15)
        m = re.search(r'"attachPath":"([^"]+)"', r.text)
        if m:
            return os.path.splitext(os.path.basename(m.group(1)))[0]
    except Exception:
        pass
    return None


def download_report_pdf(report_id: str, save_dir: str = None) -> Optional[str]:
    if save_dir is None:
        save_dir = _PDF_DIR
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{report_id}.pdf")
    if os.path.exists(path):
        return path
    try:
        r = SESSION.get(f"https://docf10.eastmoney.com/report/{report_id}.pdf", timeout=30, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return path
    except Exception:
        pass
    return None


if __name__ == "__main__":
    from shared.config.script_config import load_config
    cfg = load_config()
    plugins = cfg.get("data_fetch", {}).get("plugins", {})
    lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
    codes = [f["code"] for f in lof_cfg.get("funds", [])]
    print(f"更新 {len(codes)} 只基金持仓...")
    update_all_holdings(codes)