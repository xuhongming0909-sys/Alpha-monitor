import akshare as ak
from datetime import datetime

FUNDS = [
    ("161128","鏍囨櫘淇℃伅绉戞妧LOF","USD"),("501225","鍏ㄧ悆鑺墖LOF","USD"),
    ("161130","绾虫寚LOF","USD"),("161125","鏍囨櫘500LOF","USD"),
    ("161126","鏍囨櫘鍖荤枟淇濆仴LOF","USD"),("161127","鏍囨櫘鐢熺墿绉戞妧LOF","USD"),
    ("162415","缇庡浗娑堣垂LOF","USD"),("160140","缇庡浗REIT绮鹃€塋OF","USD"),
    ("501300","缇庡厓鍊篖OF","USD"),("164824","鍗板害鍩洪噾LOF","USD"),
    ("160416","鐭虫补鍩洪噾LOF","USD"),("162719","鐭虫补LOF","USD"),
    ("162411","鍗庡疂娌规皵LOF","USD"),("160723","鍢夊疄鍘熸补LOF","USD"),
    ("161129","鍘熸补LOF","USD"),("501018","鍗楁柟鍘熸补LOF","USD"),
    ("163208","鍏ㄧ悆娌规皵鑳芥簮LOF","USD"),("160719","鍢夊疄榛勯噾LOF","USD"),
    ("164701","榛勯噾LOF","USD"),("161116","榛勯噾涓婚LOF","USD"),
    ("160644","娓編浜掕仈缃慙OF","HKD"),
    ("164906","涓浜掕仈缃慙OF","USD"),("501312","娴峰绉戞妧LOF","USD"),
]

report = []
ok_count = 0

for code, name, cur in FUNDS:
    print(f">>> {code} {name}")
    try:
        df = ak.fund_portfolio_hold_em(symbol=code, date="2026")
        if df is None or df.empty:
            report.append(f"## {code} {name} ({cur})\n\n**鏃犳暟鎹?*\n")
            print(f"  empty")
            continue
        quarters = df["瀛ｅ害"].unique().tolist()
        # 鍙1瀛ｅ害
        target = None
        for q in quarters:
            if "1瀛ｅ害" in q:
                target = q
                break
        if not target:
            report.append(f"## {code} {name} ({cur})\n\n鏃?瀛ｅ害鏁版嵁锛屼粎鏈? {', '.join(quarters)}\n")
            print(f"  no Q1, has: {quarters}")
            continue
        qdf = df[df["瀛ｅ害"] == target].copy()
        qdf = qdf.sort_values("鍗犲噣鍊兼瘮渚?, ascending=False)
        ok_count += 1
        report.append(f"## {code} {name} ({cur})\n")
        report.append(f"**{target}** ({len(qdf)}鍙?\n")
        report.append("| 搴忓彿 | 鑲＄エ浠ｇ爜 | 鑲＄エ鍚嶇О | 鍗犲噣鍊兼瘮渚?%) | 鎸佽偂鏁?涓囪偂) | 鎸佷粨甯傚€?涓囧厓) |")
        report.append("|---:|:---|:---|---:|---:|---:|")
        for _, row in qdf.iterrows():
            report.append(f"| {int(row['搴忓彿'])} | {row['鑲＄エ浠ｇ爜']} | {row['鑲＄エ鍚嶇О']} | {row['鍗犲噣鍊兼瘮渚?]} | {row['鎸佽偂鏁?]} | {row['鎸佷粨甯傚€?]} |")
        report.append("")
        print(f"  OK: {target} {len(qdf)} rows")
    except Exception as e:
        report.append(f"## {code} {name} ({cur})\n\n**鎶ラ敊**: {str(e)[:150]}\n")
        print(f"  ERROR: {e}")

header = f"# LOF鍩洪噾2026骞?瀛ｅ害鎸佷粨鏄庣粏\n\n鐢熸垚鏃堕棿: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## 姹囨€籠n\n- 鎬诲熀閲戞暟: {len(FUNDS)}\n- 鏈夋暟鎹? {ok_count}\n- 鏃犳暟鎹? {len(FUNDS)-ok_count}\n"
with open("lof_holdings_report.md", "w", encoding="utf-8") as f:
    f.write(header + "\n## 閫愬熀閲戞槑缁哱n\n" + "\n".join(report))
print(f"\n=== done: {ok_count}/{len(FUNDS)} ===")

