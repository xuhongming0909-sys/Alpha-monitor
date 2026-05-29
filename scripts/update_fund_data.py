# -*- coding: utf-8 -*-
# AI-SUMMARY: 每个基金独立文件夹管理持仓和K线数据，每天增量更新
# 对应 INDEX.md §9.x 数据管理

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data_fetch.lof_db.schema import get_db
from data_fetch.lof_iopv.fund_classifier import (
    INDEX_ETF, get_fund_class, get_holdings_for_service, is_index_fund
)
from shared.config.script_config import load_config

# 数据目录
FUND_DATA_DIR = ROOT / "runtime_data" / "fund_data"


def _load_fund_list():
    """从config加载基金列表"""
    cfg = load_config()
    plugins = cfg.get("data_fetch", {}).get("plugins", {})
    lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
    return lof_cfg.get("funds", [])


def _get_db_holdings(code):
    """从DB读取持仓数据"""
    conn = get_db()
    rows = conn.execute(
        "SELECT ticker, name, weight, market FROM holdings WHERE code=? ORDER BY weight DESC",
        (code,)
    ).fetchall()
    conn.close()
    return [{"ticker": r[0], "name": r[1], "weight": r[2], "market": r[3]} for r in rows]


def _get_stock_prices(ticker, start_date=None):
    """从DB读取股票K线数据"""
    conn = get_db()
    if start_date:
        rows = conn.execute(
            "SELECT date, close FROM stock_prices WHERE ticker=? AND date>? ORDER BY date",
            (ticker, start_date)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT date, close FROM stock_prices WHERE ticker=? ORDER BY date",
            (ticker,)
        ).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def _save_json(filepath, data):
    """保存JSON文件"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_json(filepath):
    """加载JSON文件"""
    if not filepath.exists():
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _update_holdings(fund_dir, code):
    """更新持仓文件，返回是否有变化"""
    holdings_path = fund_dir / "holdings.json"
    old_holdings = _load_json(holdings_path) or []
    old_tickers = set(h["ticker"] for h in old_holdings)
    
    # 从DB获取最新持仓
    new_holdings = _get_db_holdings(code)
    if not new_holdings:
        return False, []
    
    new_tickers = set(h["ticker"] for h in new_holdings)
    
    # 保存持仓
    _save_json(holdings_path, {
        "code": code,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "holdings": new_holdings
    })
    
    # 比对变化
    added = new_tickers - old_tickers
    removed = old_tickers - new_tickers
    
    if old_holdings and (added or removed):
        print(f"  持仓变化: +{added if added else ''} -{removed if removed else ''}")
        return True, list(removed)
    
    return False, []


def _update_stock_klines(fund_dir, tickers, force_full=False):
    """更新股票K线数据"""
    stocks_dir = fund_dir / "stocks"
    stocks_dir.mkdir(parents=True, exist_ok=True)
    
    for ticker in tickers:
        kline_path = stocks_dir / f"{ticker}.json"
        
        if force_full:
            # 强制全量更新
            existing = {}
        else:
            # 增量更新：读取现有数据
            existing = _load_json(kline_path) or {}
        
        # 从DB读取K线
        if existing:
            last_date = max(existing.keys()) if existing else None
            new_data = _get_stock_prices(ticker, last_date)
        else:
            new_data = _get_stock_prices(ticker)
        
        if new_data:
            # 合并数据
            existing.update(new_data)
            _save_json(kline_path, existing)
            print(f"  {ticker}: +{len(new_data)}条 (总计{len(existing)}条)")
        elif not existing:
            print(f"  {ticker}: 无数据")
        else:
            print(f"  {ticker}: 已最新")


def _delete_stock_klines(fund_dir, tickers):
    """删除股票K线文件"""
    stocks_dir = fund_dir / "stocks"
    for ticker in tickers:
        kline_path = stocks_dir / f"{ticker}.json"
        if kline_path.exists():
            kline_path.unlink()
            print(f"  删除 {ticker}")


def _update_nav(fund_dir, code):
    """更新基金净值数据"""
    conn = get_db()
    rows = conn.execute(
        "SELECT date, nav FROM fund_nav WHERE code=? ORDER BY date",
        (code,)
    ).fetchall()
    conn.close()
    
    if rows:
        nav_data = {r[0]: r[1] for r in rows}
        _save_json(fund_dir / "nav.json", nav_data)
        print(f"  NAV: {len(nav_data)}条")


def update_single_fund(code, name, force_full=False):
    """更新单个基金的数据"""
    print(f"\n=== {code} {name} ===")
    
    cls = get_fund_class(code)
    fund_dir = FUND_DATA_DIR / code
    
    # 指数型基金：只更新ETF的K线，不需要拉持仓
    if cls == "index":
        print(f"  指数型基金，跳过持仓更新")
        # 只更新NAV
        _update_nav(fund_dir, code)
        return
    
    # 主动型基金：更新持仓和K线
    print(f"  主动型基金，更新持仓...")
    
    # 1. 更新持仓
    changed, removed_tickers = _update_holdings(fund_dir, code)
    
    # 2. 处理持仓变化
    if changed:
        print(f"  持仓变化，删除旧K线...")
        _delete_stock_klines(fund_dir, removed_tickers)
    
    # 3. 更新K线数据
    holdings = _load_json(fund_dir / "holdings.json")
    if holdings:
        tickers = [h["ticker"] for h in holdings.get("holdings", [])]
        print(f"  更新K线 ({len(tickers)}只股票)...")
        _update_stock_klines(fund_dir, tickers, force_full=changed or force_full)
    
    # 4. 更新NAV
    _update_nav(fund_dir, code)


def run_all(force_full=False):
    """更新所有基金数据"""
    funds = _load_fund_list()
    if not funds:
        print("错误: 无法加载基金列表")
        return
    
    print(f"开始更新 {len(funds)} 只基金...")
    for fund in funds:
        code = fund.get("code", "")
        name = fund.get("name", "")
        update_single_fund(code, name, force_full=force_full)
    
    print(f"\n完成! 数据目录: {FUND_DATA_DIR}")


if __name__ == "__main__":
    force_full = "--full" in sys.argv
    run_all(force_full=force_full)