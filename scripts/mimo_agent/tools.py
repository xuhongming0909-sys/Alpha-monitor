# -*- coding: utf-8 -*-
"""MiMo Agent 工具集：本地ticker查询 + 百度联网搜索"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

import json
import os
import re
import sqlite3
from typing import Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'lof_db', 'lof.db')

# ============================================================
# Tool 1: lookup_ticker_locally
# ============================================================

def lookup_ticker_locally(asset_name: str) -> str:
    """在本地LOF数据库+基金列表中模糊查询ticker。

    返回 JSON 字符串: {"status":"success","ticker":"SPY","name":"...","source":"..."}
    或 {"status":"not_found","query":"..."}
    """
    asset = asset_name.strip()
    if not asset:
        return json.dumps({"status": "error", "message": "asset_name 不能为空"}, ensure_ascii=False)

    results = []

    # 1. 查 config.yaml 基金列表（代码/名称模糊匹配）
    results += _search_fund_list(asset)

    # 2. 查 SQLite holdings 表（ticker/name模糊匹配）
    results += _search_holdings_db(asset)

    # 3. 查 INDEX_ETF 硬编码映射
    results += _search_index_etf(asset)

    # 去重
    seen = set()
    deduped = []
    for r in results:
        key = r.get("ticker", "")
        if key and key not in seen:
            seen.add(key)
            deduped.append(r)

    if deduped:
        return json.dumps({
            "status": "success",
            "query": asset,
            "matches": deduped[:10],
            "ticker": deduped[0]["ticker"],
        }, ensure_ascii=False)

    return json.dumps({"status": "not_found", "query": asset}, ensure_ascii=False)


def _search_fund_list(keyword: str) -> list:
    """从 config.yaml 基金列表搜索"""
    try:
        import yaml
        cfg_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        funds = cfg.get("data_fetch", {}).get("plugins", {}).get("lof_arbitrage", {}).get("funds", [])
        results = []
        kw = keyword.lower()
        for fund in funds:
            code = str(fund.get("code", ""))
            name = str(fund.get("name", ""))
            etf = str(fund.get("etf_ticker", ""))
            if kw in code or kw in name.lower() or kw in etf.lower():
                results.append({
                    "ticker": etf or code,
                    "name": name,
                    "fund_code": code,
                    "source": "fund_list",
                })
        return results
    except Exception:
        return []


def _search_holdings_db(keyword: str) -> list:
    """从 SQLite holdings 表搜索"""
    try:
        if not os.path.exists(_DB_PATH):
            return []
        conn = sqlite3.connect(_DB_PATH)
        rows = conn.execute(
            "SELECT DISTINCT ticker, name FROM holdings WHERE ticker LIKE ? OR name LIKE ? LIMIT 10",
            (f"%{keyword}%", f"%{keyword}%")
        ).fetchall()
        conn.close()
        return [{"ticker": r[0], "name": r[1], "source": "holdings_db"} for r in rows]
    except Exception:
        return []


def _search_index_etf(keyword: str) -> list:
    """从 INDEX_ETF 硬编码映射搜索"""
    try:
        from data_fetch.lof_iopv.fund_classifier import INDEX_ETF
        results = []
        kw = keyword.upper()
        for code, etfs in INDEX_ETF.items():
            for ticker, weight in etfs:
                if kw in ticker or kw in code:
                    results.append({
                        "ticker": ticker,
                        "fund_code": code,
                        "weight": weight,
                        "source": "index_etf",
                    })
        return results
    except Exception:
        return []


# ============================================================
# Tool 2: web_search（百度搜索）
# ============================================================

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def web_search(query: str, max_results: int = 5) -> str:
    """百度搜索，返回摘要结果列表。

    返回 JSON 字符串: {"status":"success","results":[{"title":"...","url":"...","snippet":"..."},...]}
    """
    query = query.strip()
    if not query:
        return json.dumps({"status": "error", "message": "query 不能为空"}, ensure_ascii=False)

    try:
        url = f"https://www.baidu.com/s?wd={quote_plus(query)}&rn={max_results}"
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        results = []
        for item in soup.select("div.result, div.c-container"):
            title_tag = item.select_one("h3 a, .c-title a, .t a")
            snippet_tag = item.select_one(".c-abstract, .c-span-last, .content-right_8Zs40")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            if title:
                results.append({
                    "title": title[:200],
                    "url": href,
                    "snippet": snippet[:500],
                })
            if len(results) >= max_results:
                break

        return json.dumps({
            "status": "success",
            "query": query,
            "results": results,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "query": query,
            "message": str(e),
        }, ensure_ascii=False)


# ============================================================
# Tool Definitions (JSON Schema for MiMo)
# ============================================================

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "lookup_ticker_locally",
            "description": "当用户输入基金、ETF、股票的名称、代码或简称，需要查找对应的Ticker代码时，调用此函数在本地数据库进行模糊查询。支持中文名、英文简称、基金代码。",
            "parameters": {
                "type": "object",
                "properties": {
                    "asset_name": {
                        "type": "string",
                        "description": "用户输入的资产名称、代码或简称，如 '标普500'、'SPY'、'161125'、'原油LOF'"
                    }
                },
                "required": ["asset_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "当你需要查找实时新闻、市场数据、最新公告、或任何你不确定的信息时，调用此函数进行联网搜索。适用于：查询最新行情、搜索基金公告、查找财经新闻、验证数据准确性。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，如 '标普500最新净值'、'南方原油160723持仓'、'QDII基金限购政策'"
                    }
                },
                "required": ["query"]
            }
        }
    },
]

# 工具名 -> 函数映射
TOOL_HANDLERS = {
    "lookup_ticker_locally": lambda args: lookup_ticker_locally(args["asset_name"]),
    "web_search": lambda args: web_search(args["query"]),
}