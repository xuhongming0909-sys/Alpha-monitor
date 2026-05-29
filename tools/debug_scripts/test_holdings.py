import akshare as ak
from datetime import datetime

FUNDS = [
    ("161128","标普信息科技LOF","USD"),("501225","全球芯片LOF","USD"),
    ("161130","纳指LOF","USD"),("161125","标普500LOF","USD"),
    ("161126","标普医疗保健LOF","USD"),("161127","标普生物科技LOF","USD"),
    ("162415","美国消费LOF","USD"),("160140","美国REIT精选LOF","USD"),
    ("501300","美元债LOF","USD"),("164824","印度基金LOF","USD"),
    ("160416","石油基金LOF","USD"),("162719","石油LOF","USD"),
    ("162411","华宝油气LOF","USD"),("160723","嘉实原油LOF","USD"),
    ("161129","原油LOF","USD"),("501018","南方原油LOF","USD"),
    ("163208","全球油气能源LOF","USD"),("160719","嘉实黄金LOF","USD"),
    ("164701","黄金LOF","USD"),("161116","黄金主题LOF","USD"),
    ("160125","南方香港LOF","HKD"),("160644","港美互联网LOF","HKD"),
    ("164906","中概互联网LOF","USD"),("501312","海外科技LOF","USD"),
]

report = []
ok_count = 0

for code, name, cur in FUNDS:
    print(f">>> {code} {name}")
    try:
        df = ak.fund_portfolio_hold_em(symbol=code, date="2026")
        if df is None or df.empty:
            report.append(f"## {code} {name} ({cur})\n\n**无数据**\n")
            print(f"  empty")
            continue
        quarters = df["季度"].unique().tolist()
        # 只要1季度
        target = None
        for q in quarters:
            if "1季度" in q:
                target = q
                break
        if not target:
            report.append(f"## {code} {name} ({cur})\n\n无1季度数据，仅有: {', '.join(quarters)}\n")
            print(f"  no Q1, has: {quarters}")
            continue
        qdf = df[df["季度"] == target].copy()
        qdf = qdf.sort_values("占净值比例", ascending=False)
        ok_count += 1
        report.append(f"## {code} {name} ({cur})\n")
        report.append(f"**{target}** ({len(qdf)}只)\n")
        report.append("| 序号 | 股票代码 | 股票名称 | 占净值比例(%) | 持股数(万股) | 持仓市值(万元) |")
        report.append("|---:|:---|:---|---:|---:|---:|")
        for _, row in qdf.iterrows():
            report.append(f"| {int(row['序号'])} | {row['股票代码']} | {row['股票名称']} | {row['占净值比例']} | {row['持股数']} | {row['持仓市值']} |")
        report.append("")
        print(f"  OK: {target} {len(qdf)} rows")
    except Exception as e:
        report.append(f"## {code} {name} ({cur})\n\n**报错**: {str(e)[:150]}\n")
        print(f"  ERROR: {e}")

header = f"# LOF基金2026年1季度持仓明细\n\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## 汇总\n\n- 总基金数: {len(FUNDS)}\n- 有数据: {ok_count}\n- 无数据: {len(FUNDS)-ok_count}\n"
with open("lof_holdings_report.md", "w", encoding="utf-8") as f:
    f.write(header + "\n## 逐基金明细\n\n" + "\n".join(report))
print(f"\n=== done: {ok_count}/{len(FUNDS)} ===")