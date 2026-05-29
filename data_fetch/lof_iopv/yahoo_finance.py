# -*- coding: utf-8 -*-
# AI-SUMMARY: Yahoo Finance ticker搜索 + 海外资产历史价格获取
"""Yahoo Finance模块。

功能:
1. ticker_search: 按基金名搜Yahoo ticker + 交易所
2. fetch_prices: 批量拉取历史收盘价
3. resolve_holdings: 用Yahoo修正持仓ticker和market
"""
import time
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Yahoo交易所后缀映射
_EXCHANGE_SUFFIX = {
    "NMS": ("US", ""),    # NASDAQ
    "NYQ": ("US", ""),    # NYSE
    "PCX": ("US", ""),    # NYSE Arca
    "BTS": ("US", ""),    # BATS
    "NGM": ("US", ""),    # NASDAQ GM
    "HKG": ("HK", ".HK"),
    "LSE": ("UK", ".L"),
    "MIL": ("IT", ".MI"),
    "JPX": ("JP", ".T"),
    "EBS": ("CH", ".SW"),
    "TOR": ("CA", ".TO"),
    "ASX": ("AU", ".AX"),
}


def search_ticker(name: str, max_results: int = 3) -> Optional[Dict]:
    """Yahoo Finance搜索ticker。

    Args:
        name: 基金/股票全称
        max_results: 最大返回数

    Returns:
        {"ticker": "OILK", "name": "...", "exchange": "BTS", "market": "US", "yahoo_symbol": "OILK"}
        or None
    """
    try:
        import yfinance as yf
        results = yf.Search(name, max_results=max_results).quotes
        if not results:
            return None
        best = results[0]
        symbol = best.get("symbol", "")
        exchange = best.get("exchange", "")
        short_name = best.get("shortName", best.get("longName", ""))

        # 从Yahoo symbol推导market
        market = "US"
        for exch_code, (mkt, _) in _EXCHANGE_SUFFIX.items():
            if exchange == exch_code:
                market = mkt
                break
        # 从symbol后缀推导
        if ".HK" in symbol:
            market = "HK"
        elif ".L" in symbol:
            market = "UK"
        elif ".T" in symbol:
            market = "JP"
        elif ".SW" in symbol:
            market = "CH"
        elif ".MI" in symbol:
            market = "IT"

        return {
            "ticker": symbol.split(".")[0] if market == "US" else symbol,
            "name": short_name,
            "exchange": exchange,
            "market": market,
            "yahoo_symbol": symbol,
        }
    except Exception as e:
        logger.warning(f"Yahoo search failed for '{name}': {e}")
        return None


def batch_search_tickers(names: List[str], delay: float = 1.5) -> Dict[str, Optional[Dict]]:
    """批量搜索ticker。

    Args:
        names: 基金名称列表
        delay: 每次请求间隔(秒)

    Returns:
        {name: search_result or None}
    """
    results = {}
    for name in names:
        result = search_ticker(name)
        results[name] = result
        if delay > 0:
            time.sleep(delay)
    return results


def fetch_history(yahoo_symbol: str, period: str = "3mo") -> Dict[str, float]:
    """拉取Yahoo历史收盘价。

    Args:
        yahoo_symbol: Yahoo ticker (如 "USO", "0883.HK", "1671.T")
        period: 时间范围

    Returns:
        {"2026-03-03": 45.12, "2026-03-04": 45.30, ...}
    """
    try:
        import yfinance as yf
        data = yf.download(yahoo_symbol, period=period, progress=False)
        if data is None or data.empty:
            return {}
        prices = {}
        for date_idx, row in data.iterrows():
            date_str = date_idx.strftime("%Y-%m-%d")
            close = float(row.iloc[0]) if hasattr(row, 'iloc') else float(row["Close"])
            if close > 0:
                prices[date_str] = close
        return prices
    except Exception as e:
        logger.warning(f"Yahoo download failed for '{yahoo_symbol}': {e}")
        return {}


def batch_fetch_prices(yahoo_symbols: List[str], period: str = "3mo", delay: float = 1.0) -> Dict[str, Dict[str, float]]:
    """批量拉取历史价格。

    Returns:
        {yahoo_symbol: {date: price}}
    """
    results = {}
    for symbol in yahoo_symbols:
        prices = fetch_history(symbol, period)
        results[symbol] = prices
        if delay > 0:
            time.sleep(delay)
    return results


def determine_market_from_ticker(ticker: str) -> str:
    """从ticker推断市场。"""
    if ".HK" in ticker:
        return "HK"
    if ".L" in ticker:
        return "UK"
    if ".T" in ticker:
        return "JP"
    if ".SW" in ticker:
        return "CH"
    if ".MI" in ticker:
        return "IT"
    if ticker.isdigit() and len(ticker) == 5:
        return "HK"
    if ticker.isdigit() and len(ticker) == 6:
        return "A"
    return "US"


def normalize_ticker_for_yahoo(ticker: str, market: str) -> str:
    """将ticker转换为Yahoo格式。"""
    if market == "HK" and not ticker.endswith(".HK"):
        return ticker + ".HK"
    if market == "UK" and not ticker.endswith(".L"):
        return ticker + ".L"
    if market == "JP" and not ticker.endswith(".T"):
        return ticker + ".T"
    if market == "CH" and not ticker.endswith(".SW"):
        return ticker + ".SW"
    return ticker