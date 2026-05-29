# -*- coding: utf-8 -*-
# AI-SUMMARY: 基金持仓更新 - 指数型跳过, 主动型先API再PDF(report_id缓存避免重复下载)
"""基金持仓更新流程。

分类只分两种: 指数型 / 主动型

指数型: 跳过 (ETF映射在 fund_classifier.py 硬编码)

主动型更新逻辑:
  1. 先调 akshare API 获取持仓
  2. 若 API 有数据且合计占比 >= 25% -> 直接用 API 数据，结束
  3. 若 API 无数据或合计 < 25% -> 获取最新季报 report_id
  4. 对比前一天缓存的 report_id:
     - 相同 -> 无新季报，跳过 PDF 下载/解析，沿用 DB 现有数据
     - 不同 -> 下载 PDF -> LLM 解析 -> 写入 DB -> 更新缓存
"""
import json
import os
import datetime
import time
from typing import Optional, Tuple

from data_fetch.lof_db.schema import get_db, init_db


# API覆盖率阈值: 低于此值触发PDF解析
_API_COVERAGE_THRESHOLD = 25.0

# PDF存储目录
_PDF_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'qreport')


def _load_funds():
    """从config加载所有基金列表"""
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get('data_fetch', {}).get('plugins', {})
        lof_cfg = plugins.get('lof_arbitrage', plugins.get('lof_iopv', {}))
        funds = lof_cfg.get('funds', [])
        return [f for f in funds if f.get('code')]
    except Exception:
        return []


def _is_index_fund(code: str) -> bool:
    from data_fetch.lof_iopv.fund_classifier import is_index_fund
    return is_index_fund(code)


# ============================================================
# report_id 缓存: 避免重复下载/解析同一只基金的同一篇季报
# 缓存文件: runtime_data/report_id_cache.json
# 格式: {code: {report_id, updated}}
# ============================================================
_CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'report_id_cache.json')


def _load_report_id_cache() -> dict:
    """加载缓存"""
    try:
        with open(_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_report_id_cache(cache: dict):
    """保存缓存到文件"""
    os.makedirs(os.path.dirname(_CACHE_FILE), exist_ok=True)
    with open(_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _get_cached_report_id(code: str) -> Optional[str]:
    """读取单只基金缓存的 report_id，无缓存返回 None"""
    cache = _load_report_id_cache()
    entry = cache.get(code)
    if entry:
        return entry.get('report_id')
    return None


def get_holdings_source(code: str) -> str:
    """获取持仓数据来源: 'api' 或 'pdf'。无缓存返回 'unknown'。"""
    cache = _load_report_id_cache()
    entry = cache.get(code)
    if entry:
        return entry.get('source', 'unknown')
    return 'unknown'


def _set_cached_report_id(code: str, report_id: str, source: str = 'pdf'):
    """更新单只基金的 report_id 缓存。source: 'api' 或 'pdf'"""
    cache = _load_report_id_cache()
    cache[code] = {
        'report_id': report_id,
        'source': source,
        'updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    _save_report_id_cache(cache)


# ============================================================
# akshare API 获取最新季报 report_id (不下载PDF)
# ============================================================
def _fetch_latest_report_id(code: str) -> Optional[Tuple[str, str, str]]:
    """获取最新季度报告的 (report_id, title, date)。仅查ID不下载PDF。"""
    import akshare as ak
    try:
        df = ak.fund_announcement_report_em(symbol=code)
        if df is None or df.empty:
            return None
        quarterly = df[df['公告标题'].str.contains('季度报告', na=False)]
        if quarterly.empty:
            return None
        latest = quarterly.iloc[-1]
        return (
            str(latest['报告ID']),
            str(latest['公告标题']),
            str(latest['公告日期']),
        )
    except Exception as e:
        print(f'  {code}: 获取report_id异常 - {e}')
        return None


def _fetch_holdings_api(code: str, year: str = None) -> list:
    """akshare API获取持仓"""
    import akshare as ak
    try:
        df = ak.fund_portfolio_hold_em(symbol=code, date=year or '')
        if df is None or df.empty:
            return []
        holdings = []
        for _, row in df.iterrows():
            ticker = str(row.get('股票代码', ''))
            name = str(row.get('股票名称', ''))
            weight = float(row.get('占净值比例', 0) or 0)
            quarter = str(row.get('季度', ''))
            if ticker and weight > 0:
                holdings.append({'ticker': ticker, 'name': name, 'weight': weight, 'quarter': quarter})
        return holdings
    except Exception as e:
        print(f'  {code}: API失败 - {e}')
        return []


def _fetch_holdings_html(code: str) -> list:
    """东方财富HTML抓取持仓"""
    import re, requests
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fundf10.eastmoney.com/'})
    url = f'http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10'
    try:
        r = s.get(url, timeout=15)
        m = re.search(r'content:"(.*?)",arryear', r.text, re.DOTALL)
        if not m:
            return []
        rows = re.findall(
            r'<tr><td>(\d+)</td>.*?<a href=[^>]+>([A-Z0-9]+)</a>.*?<a href=[^>]+>([^<]+)</a>.*?<td[^>]*>([\d.]+)%</td>',
            m.group(1), re.DOTALL
        )
        return [{'ticker': c, 'name': n.strip(), 'weight': float(w), 'quarter': ''} for _, c, n, w in rows]
    except Exception:
        return []


def _download_latest_pdf(code: str, report_info: tuple = None) -> str | None:
    """下载最新季度报告PDF -> 返回本地路径。report_info可复用避免重复API调用。"""
    import requests as req
    os.makedirs(_PDF_DIR, exist_ok=True)
    try:
        if report_info is None:
            report_info = _fetch_latest_report_id(code)
        if not report_info:
            print(f'  {code}: 无季度报告')
            return None
        report_id, title, date = report_info
        pdf_path = os.path.join(_PDF_DIR, f'{code}_{report_id}.pdf')
        if os.path.exists(pdf_path):
            print(f'  {code}: PDF已存在 {report_id}')
            return pdf_path
        pdf_url = f'https://pdf.dfcfw.com/pdf/H2_{report_id}_1.pdf'
        print(f'  {code}: 下载 {title} ({date})')
        r = req.get(pdf_url, timeout=60, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            with open(pdf_path, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f'  {code}: PDF下载完成 {os.path.getsize(pdf_path)} bytes')
            return pdf_path
        else:
            print(f'  {code}: PDF下载失败 HTTP {r.status_code}')
            return None
    except Exception as e:
        print(f'  {code}: PDF获取异常 - {e}')
        return None


def _parse_pdf_holdings(code: str, pdf_path: str) -> list:
    """调LLM解析PDF持仓"""
    from data_fetch.lof_iopv.report_holdings import _render_pages, _call_vision_llm, _extract_text, _call_text_llm, _dedup
    b64 = _render_pages(pdf_path)
    if b64:
        try:
            items = _call_vision_llm(b64, code)
            if items:
                items = _dedup(items)
                total = sum(h['weight'] for h in items)
                print(f'  {code}: vision解析 {len(items)}条 覆盖率{total:.1f}%')
                return items
        except Exception as e:
            print(f'  {code}: vision失败 - {e}')
    text = _extract_text(pdf_path)
    if text and len(text) > 100:
        try:
            items = _call_text_llm(text, code)
            if items:
                items = _dedup(items)
                total = sum(h['weight'] for h in items)
                print(f'  {code}: text解析 {len(items)}条 覆盖率{total:.1f}%')
                return items
        except Exception as e:
            print(f'  {code}: text失败 - {e}')
    return []


def _fetch_holdings_pdf(code: str, report_info: tuple = None) -> list:
    """完整PDF流程: 下载最新季报 -> LLM解析 -> 返回持仓"""
    pdf_path = _download_latest_pdf(code, report_info)
    if not pdf_path:
        return []
    return _parse_pdf_holdings(code, pdf_path)


def _normalize_ticker(ticker: str, market: str) -> str:
    """规范化ticker: HK补前导零到5位, A股补到6位"""
    if market == 'HK' and ticker.isdigit() and len(ticker) < 5:
        return ticker.zfill(5)
    if market == 'A' and ticker.isdigit() and len(ticker) < 6:
        return ticker.zfill(6)
    return ticker


def _determine_market(ticker: str) -> str:
    """根据ticker判断市场"""
    if ticker.isdigit() and len(ticker) == 5:
        return 'HK'
    if ticker.isdigit() and len(ticker) == 6:
        return 'A'
    return 'US'


def _store_holdings(conn, code: str, holdings: list, quarter: str):
    """写入持仓到DB"""
    conn.execute('DELETE FROM holdings WHERE code = ?', (code,))
    for h in holdings:
        t = h['ticker']
        market = _determine_market(t)
        t = _normalize_ticker(t, market)
        conn.execute(
            'INSERT OR REPLACE INTO holdings (code, report_date, ticker, name, weight, market) VALUES (?,?,?,?,?,?)',
            (code, quarter, t, h.get('name', ''), h['weight'], market)
        )
    conn.commit()


def update_holdings():
    """主入口: 更新所有基金持仓。

    流程 (每只主动型基金):
      1. akshare API -> 有数据且占比>=25% -> 写入DB -> 结束
      2. 获取最新 report_id -> 对比缓存:
         - 相同 -> 无新季报，跳过，沿用DB现有数据
         - 不同 -> 下载PDF -> LLM解析 -> 写入DB -> 更新缓存
    """
    init_db()
    conn = get_db()
    funds = _load_funds()
    stats = {
        'index': 0,       # 指数型跳过
        'api_ok': 0,      # API 数据足够
        'api_low': 0,     # API 数据不足，需 PDF
        'cached_skip': 0, # report_id 未变，跳过 PDF
        'pdf_ok': 0,      # PDF 解析成功
        'fail': 0,        # 无数据
    }

    print(f'持仓更新: {len(funds)} 只基金')

    for fund in funds:
        code = fund['code']
        name = fund.get('name', '')

        # 指数型: 跳过
        if _is_index_fund(code):
            stats['index'] += 1
            continue

        print(f'\n--- {code} {name} ---')

        # ---- 步骤1: akshare API 获取持仓 ----
        holdings = _fetch_holdings_api(code)
        if not holdings:
            print('  API无数据, 尝试HTML...')
            holdings = _fetch_holdings_html(code)

        if holdings:
            total_weight = sum(h['weight'] for h in holdings)
            quarter = holdings[0].get('quarter', 'latest')
            print(f'  API: {len(holdings)}条, 覆盖率{total_weight:.1f}%')

            if total_weight >= _API_COVERAGE_THRESHOLD:
                _store_holdings(conn, code, holdings, quarter)
                # API数据足够，标记来源为api(无需查report_id)
                _set_cached_report_id(code, '__api__', source='api')
                print(f'  -> API数据OK, 已写入DB')
                stats['api_ok'] += 1
                time.sleep(0.5)
                continue
            else:
                print(f'  -> API覆盖率{total_weight:.1f}% < {_API_COVERAGE_THRESHOLD}%, 需PDF补充')
                stats['api_low'] += 1
        else:
            stats['api_low'] += 1

        # ---- 步骤2: API不足，获取最新 report_id 对比缓存 ----
        report_info = _fetch_latest_report_id(code)
        if not report_info:
            print(f'  -> 无季度报告数据，跳过')
            stats['fail'] += 1
            continue

        latest_id, title, date = report_info
        cached_id = _get_cached_report_id(code)
        print(f'  最新report_id={latest_id} 缓存={cached_id or "(无)"}')

        if cached_id and cached_id == latest_id:
            # report_id 没变 -> 没发新季报 -> 沿用DB现有数据
            print(f'  -> report_id未变，跳过PDF下载/解析，沿用DB现有持仓')
            stats['cached_skip'] += 1
            time.sleep(0.5)
            continue

        # ---- 步骤3: report_id 变了(或无缓存) -> 下载PDF -> LLM解析 ----
        print(f'  -> 新季报: {title} ({date}), 开始下载PDF...')
        pdf_holdings = _fetch_holdings_pdf(code, report_info)
        if pdf_holdings:
            total_weight = sum(h['weight'] for h in pdf_holdings)
            quarter = pdf_holdings[0].get('quarter', 'latest')
            _store_holdings(conn, code, pdf_holdings, quarter)
            print(f'  -> PDF解析OK: {len(pdf_holdings)}条, 覆盖率{total_weight:.1f}%')
            stats['pdf_ok'] += 1
            _set_cached_report_id(code, latest_id)
        else:
            print(f'  -> PDF解析失败(使用hardcoded兜底)')
            stats['fail'] += 1
            _set_cached_report_id(code, latest_id)

        time.sleep(0.5)

    conn.close()
    print(f"\n完成: 指数型{stats['index']}只跳过, API成功{stats['api_ok']}只, "
          f"API低覆盖{stats['api_low']}只, 缓存跳过{stats['cached_skip']}只, "
          f"PDF成功{stats['pdf_ok']}只, 失败{stats['fail']}只")
    return stats


if __name__ == '__main__':
    update_holdings()
