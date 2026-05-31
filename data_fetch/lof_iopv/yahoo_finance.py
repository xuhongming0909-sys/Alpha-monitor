# -*- coding: utf-8 -*-
# AI-SUMMARY: Yahoo Finance ticker搜索 + 海外资产历史价格获取（走Deno代理）
"""Yahoo Finance模块（服务器安全版）。

所有请求走 Deno Deploy 代理，绕过服务器IP封禁。

功能:
1. search_ticker: 按资产名搜Yahoo ticker + 市场
2. fetch_history: 拉取单只标的收盘价历史
3. resolve_holdings_tickers: 批量为持仓name补全ticker+market
"""
import json
import logging
import os
import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

# ============================================================
# 配置
# ============================================================

def _get_proxy_base() -> str:
    """从secrets.yaml读取Yahoo代理地址。"""
    try:
        import yaml
        p = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'secrets.yaml')
        with open(p, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f) or {}
        return cfg.get('yahoo', {}).get('proxy_base', '')
    except Exception:
        return ''

_PROXY_BASE = ''

def _proxy_url() -> str:
    global _PROXY_BASE
    if not _PROXY_BASE:
        _PROXY_BASE = _get_proxy_base()
    return _PROXY_BASE

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

# Yahoo交易所 -> (市场, 后缀)
_EXCHANGE_SUFFIX = {
    "NMS": ("US", ""), "NYQ": ("US", ""), "PCX": ("US", ""),
    "BTS": ("US", ""), "NGM": ("US", ""),
    "HKG": ("HK", ".HK"), "LSE": ("UK", ".L"),
    "MIL": ("IT", ".MI"), "JPX": ("JP", ".T"),
    "EBS": ("CH", ".SW"), "TOR": ("CA", ".TO"), "ASX": ("AU", ".AX"),
}


# ============================================================
# Ticker搜索（Yahoo auto-complete API）
# ============================================================

def search_ticker(name: str, max_results: int = 5) -> Optional[Dict]:
    """Yahoo搜索ticker。

    Returns:
        {"ticker": "OILK", "name": "...", "exchange": "BTS",
         "market": "US", "yahoo_symbol": "OILK"}
        or None
    """
    base = _proxy_url()
    if not base:
        logger.warning("Yahoo proxy_base 未配置")
        return None

    # Yahoo auto-complete / search API
    search_url = f"{base}/v1/finance/search"
    try:
        r = _SESSION.get(search_url, params={
            "q": name, "quotesCount": max_results,
            "newsCount": 0, "enableFuzzyQuery": False,
            "quoteType": "", "resultList": True,
        }, timeout=15)
        if r.status_code != 200:
            logger.warning(f"Yahoo search {r.status_code}: {name}")
            return None
        data = r.json()
        quotes = data.get("quotes", [])
        if not quotes:
            return None

        best = quotes[0]
        symbol = best.get("symbol", "")
        exchange = best.get("exchange", "")
        short_name = best.get("shortname", best.get("longname", ""))

        market = _infer_market(symbol, exchange)
        ticker = symbol.split(".")[0] if market == "US" else symbol

        return {
            "ticker": ticker,
            "name": short_name,
            "exchange": exchange,
            "market": market,
            "yahoo_symbol": symbol,
        }
    except Exception as e:
        logger.warning(f"Yahoo search failed for '{name}': {e}")
        return None


def batch_search_tickers(names: List[str], delay: float = 0.5) -> Dict[str, Optional[Dict]]:
    """批量搜索ticker。"""
    results = {}
    for name in names:
        results[name] = search_ticker(name)
        if delay > 0:
            time.sleep(delay)
    return results


# ============================================================
# 历史价格（Yahoo chart API via Deno proxy）
# ============================================================

def fetch_history(yahoo_symbol: str, period: str = "3mo", interval: str = "1d", include_pre_post: bool = False) -> Dict[str, float]:
    """拉取Yahoo历史收盘价。

    Returns:
        {"2026-03-03": 45.12, "2026-03-04": 45.30, ...}
    """
    base = _proxy_url()
    if not base:
        return {}

    url = f"{base}/v8/finance/chart/{yahoo_symbol}"
    try:
        params = {"range": period, "interval": interval}
        # 期货(=F)不支持includePrePost，会返回空数据
        if include_pre_post and interval != "1d" and "=F" not in yahoo_symbol:
            params["includePrePost"] = "true"
        r = _SESSION.get(url, params=params, timeout=20)
        if r.status_code != 200:
            logger.warning(f"Yahoo chart {r.status_code} for {yahoo_symbol}")
            return {}

        result = r.json().get("chart", {}).get("result", [])
        if not result:
            return {}
        r0 = result[0]
        ts = r0.get("timestamp", [])
        quotes = r0.get("indicators", {}).get("quote", [{}])[0]
        closes = quotes.get("close", [])
        prices = {}
        for i, t in enumerate(ts):
            if i < len(closes) and closes[i] is not None:
                from datetime import datetime
                date_str = datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")
                c = float(closes[i])
                if c > 0:
                    prices[date_str] = c
        return prices
    except Exception as e:
        logger.warning(f"Yahoo download failed for '{yahoo_symbol}': {e}")
        return {}


def fetch_latest_price(yahoo_symbol: str) -> Optional[float]:
    """获取最新收盘价。"""
    prices = fetch_history(yahoo_symbol, "5d", "1d")
    if not prices:
        return None
    return list(prices.values())[-1]


def fetch_latest_realtime_price(yahoo_symbol: str) -> Optional[float]:
    """获取最新实时价（含盘前盘后），用于IOPV实时计算。

    美股ETF/个股：5m + includePrePost，覆盖~16h
    期货：5m，天然覆盖~23h（不加includePrePost）
    港股/伦敦/日股：5m，覆盖各市场交易时段
    """
    prices = fetch_history(yahoo_symbol, "5d", "5m", include_pre_post=True)
    if not prices:
        return None
    return list(prices.values())[-1]



def batch_fetch_prices(yahoo_symbols: List[str], period: str = "3mo",
                       delay: float = 0.3) -> Dict[str, Dict[str, float]]:
    """批量拉取历史价格。"""
    results = {}
    for symbol in yahoo_symbols:
        results[symbol] = fetch_history(symbol, period)
        if delay > 0:
            time.sleep(delay)
    return results


# ============================================================
# 持仓ticker解析
# ============================================================

def resolve_holdings_tickers(holdings: List[Dict], delay: float = 0.5) -> List[Dict]:
    """为持仓列表补全ticker和market。

    已有ticker的跳过，没有的用Yahoo搜索。
    """
    for h in holdings:
        ticker = h.get("ticker", "")
        market = h.get("market", "")
        name = h.get("name", "")

        # 已有有效ticker，跳过
        if ticker and market:
            continue

        # 用Yahoo搜索
        if name:
            result = search_ticker(name)
            if result:
                if not ticker:
                    h["ticker"] = result["ticker"]
                if not market:
                    h["market"] = result["market"]
                h["yahoo_symbol"] = result["yahoo_symbol"]
            time.sleep(delay)

    return holdings


# ============================================================
# 辅助函数
# ============================================================

def _infer_market(symbol: str, exchange: str) -> str:
    """从symbol后缀或exchange代码推断市场。"""
    for exch_code, (mkt, suffix) in _EXCHANGE_SUFFIX.items():
        if exchange == exch_code:
            return mkt
    # 后缀兜底
    if ".HK" in symbol: return "HK"
    if ".L" in symbol: return "UK"
    if ".T" in symbol: return "JP"
    if ".SW" in symbol: return "CH"
    if ".MI" in symbol: return "IT"
    if ".TO" in symbol: return "CA"
    if ".AX" in symbol: return "AU"
    if ".DE" in symbol: return "DE"


def determine_market_from_ticker(ticker: str) -> str:
    """从ticker推断市场。"""
    return _infer_market(ticker, "")


def normalize_ticker_for_yahoo(ticker: str, market: str) -> str:
    """将ticker转换为Yahoo格式。"""
    suffix_map = {
        "HK": ".HK", "UK": ".L", "JP": ".T",
        "CH": ".SW", "IT": ".MI", "CA": ".TO", "AU": ".AX",
        "DE": ".DE",
    }
    suffix = suffix_map.get(market, "")
    if suffix and not ticker.endswith(suffix):
        # HK: 补前导零到4位 (883 -> 0883)
        if market == "HK" and ticker.isdigit() and len(ticker) < 4:
            ticker = ticker.zfill(4)
        return ticker + suffix
    return ticker


