#!/usr/bin/env python3
"""LOF每日数据更新+回测 - 凌晨5点定时执行
执行顺序: NAV → 价格(ETF+港股+持仓股) → 汇率 → 回测 → 清缓存 → 重启服务
"""
import os, sys, json, time, subprocess

PROJECT_DIR = os.path.expanduser("~/Alpha monitor")
os.chdir(PROJECT_DIR)
sys.path.insert(0, PROJECT_DIR)

LOG_FILE = os.path.join(PROJECT_DIR, "runtime_data", "daily_update.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_step(name, func):
    log(f"=== {name} START ===")
    try:
        func()
        log(f"=== {name} OK ===")
    except Exception as e:
        log(f"=== {name} FAIL: {e} ===")


# 1. NAV (天天基金API)
def update_nav():
    from data_fetch.lof_db.holdings_updater import update_holdings
    update_holdings()


# 2. 价格 (一次性更新所有ticker)
def update_prices():
    from data_fetch.lof_db.etf_updater import update_etf, update_stocks
    
    # ETF价格 → etf_prices表
    update_etf()
    
    # 所有需要的ticker合并到一个列表，一次性拉取 → stock_prices表
    all_tickers = _collect_all_tickers()
    log(f"  拉取 {len(all_tickers)} 个ticker价格")
    update_stocks(all_tickers)


def _collect_all_tickers():
    """从fund_classifier收集所有需要价格的ticker（去重）"""
    tickers = set()
    
    # 1) 指数型ETF ticker
    try:
        from data_fetch.lof_iopv.fund_classifier import INDEX_ETF
        for etfs in INDEX_ETF.values():
            for t, _ in etfs:
                tickers.add(t)
    except Exception:
        # fallback: 基础ETF列表
        tickers.update(["SPY","QQQ","XLY","XOP","IEO","XBI","IYR","IXC","XLK","INDA",
                        "GLD","USO","BNO","RYH","GDX","AGG","KWEB","EWH"])
    
    # 2) B类/主动型hardcoded持仓ticker
    try:
        from data_fetch.lof_iopv.fund_classifier import _硬编码
    except ImportError:
        pass
    try:
        from data_fetch.lof_iopv.fund_classifier import get_holdings_for_backtest
        from data_fetch.lof_iopv.fund_classifier import INDEX_ETF as _idx
        # 从config读所有基金code
        from shared.config.script_config import load_config
        cfg = load_config()
        funds = cfg.get("data_fetch", {}).get("plugins", {}).get("lof_arbitrage", {}).get("funds", [])
        for f in funds:
            code = f.get("code", "")
            try:
                holdings = get_holdings_for_backtest(code)
                for h in holdings:
                    tickers.add(h["ticker"])
            except Exception:
                pass
    except Exception:
        pass
    
    # 3) DB holdings表里的ticker
    try:
        from data_fetch.lof_db.schema import get_db
        conn = get_db()
        rows = conn.execute("SELECT DISTINCT ticker FROM holdings").fetchall()
        conn.close()
        for r in rows:
            if r[0]:
                tickers.add(r[0])
    except Exception:
        pass
    
    return sorted(tickers)


# 3. 汇率
def update_fx():
    import akshare as ak
    from data_fetch.lof_db.schema import get_db
    from datetime import datetime, timedelta
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    
    conn = get_db()
    for sym in ["美元", "港币"]:
        try:
            df = ak.currency_boc_sina(symbol=sym, start_date=start, end_date=end)
            if df is not None and not df.empty:
                currency = "USD" if sym == "美元" else "HKD"
                for _, row in df.iterrows():
                    date_str = str(row.get("日期", ""))[:10]
                    rate = float(row.get("中行汇买价", 0)) / 100
                    if date_str and rate > 0:
                        conn.execute("INSERT OR REPLACE INTO fx_rates (currency, date, rate) VALUES (?, ?, ?)",
                            (currency, date_str, rate))
                conn.commit()
                log(f"  {currency}: {len(df)} rows")
        except Exception as e:
            log(f"  {sym} FAIL: {e}")
    conn.close()


# 4. 回测
def run_backtest():
    from strategy.lof_iopv.backtest_v2 import run_all
    results = run_all()
    log(f"  回测: {len(results)}/24 funds")


# 5. 数据新鲜度检查
def check_freshness():
    from data_fetch.lof_db.schema import get_db
    from datetime import datetime, timedelta
    
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # NAV: QDII T+2，允许3天延迟
    nav_max = conn.execute("SELECT MAX(date) FROM fund_nav").fetchone()[0]
    if nav_max:
        nav_age = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(nav_max, "%Y-%m-%d")).days
        if nav_age > 3:
            log(f"  WARNING: NAV数据过期 {nav_age}天 (最新={nav_max})")
    
    # 股票价格: 允许1天延迟(周末)
    stock_max = conn.execute("SELECT MAX(date) FROM stock_prices").fetchone()[0]
    if stock_max:
        stock_age = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(stock_max, "%Y-%m-%d")).days
        if stock_age > 3:
            log(f"  WARNING: 股票价格过期 {stock_age}天 (最新={stock_max})")
    
    # 汇率
    fx_max = conn.execute("SELECT MAX(date) FROM fx_rates WHERE currency='USD'").fetchone()[0]
    if fx_max:
        fx_age = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(fx_max, "%Y-%m-%d")).days
        if fx_age > 3:
            log(f"  WARNING: 汇率过期 {fx_age}天 (最新={fx_max})")
    
    # 回测结果
    bt_path = os.path.join(PROJECT_DIR, "runtime_data", "backtest", "results_v2.json")
    if os.path.exists(bt_path):
        bt = json.load(open(bt_path))
        log(f"  回测覆盖: {len(bt)}/24 funds")
    else:
        log(f"  WARNING: 回测结果文件不存在!")
    
    conn.close()


# 6. 清理Python缓存 + 重启
def restart_service():
    # 清pycache（防止旧代码残留）
    subprocess.run(["find", PROJECT_DIR, "-name", "*.pyc", "-delete"], 
                   capture_output=True, timeout=10)
    subprocess.run(["find", PROJECT_DIR, "-name", "__pycache__", "-type", "d", "-exec", "rm", "-rf", "{}", "+"],
                   capture_output=True, timeout=10)
    log("  pycache cleared")
    
    # 重启PM2
    subprocess.run(["pm2", "restart", "alpha-monitor"], capture_output=True, timeout=30)
    log("  PM2 restarted")


if __name__ == "__main__":
    log("=" * 50)
    log("Daily update started")
    run_step("NAV", update_nav)
    run_step("Prices", update_prices)
    run_step("FX", update_fx)
    run_step("Backtest", run_backtest)
    run_step("Freshness", check_freshness)
    run_step("Restart", restart_service)
    log("Daily update completed")