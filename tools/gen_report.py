import sys, sqlite3, os; sys.path.insert(0, '.')
from datetime import datetime

db_path = 'runtime_data/lof_db/lof.db'
FUND_NAMES = {
    '161128': '标普科技LOF', '501225': '全球芯片LOF', '161130': '纳斯达克LOF',
    '161125': '标普500LOF', '161126': '医药卫生LOF', '161127': '生物科技LOF',
    '162415': '可选消费LOF', '160140': '美国REIT LOF', '501300': '全球元债券',
    '164824': '工银印度LOF', '160416': '华宝标普油气LOF', '162719': '华宝标普油气C',
    '162411': '华宝标普油气LOF', '160723': '嘉实原油LOF', '161129': '原油LOF',
    '501018': '南方原油LOF', '163208': '全球油气LOF', '160719': '黄金LOF',
    '164701': '易方达黄金LOF', '161116': '黄金基金LOF', '160125': '中国互联LOF',
    '160644': '港美互联LOF', '164906': '中国互联LOF(新)', '501312': '海外科技LOF',
}

codes = list(FUND_NAMES.keys())
conn = sqlite3.connect(db_path)
lines = []
lines.append('=' * 70)
lines.append(f'LOF基金持仓报告 - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
lines.append('=' * 70)
lines.append('数据来源: DeepSeek AI解析季报PDF + 东方财富API')
lines.append('持仓日期: 2026Q1季报')
lines.append('')

total_funds = 0
total_holdings = 0

for code in codes:
    rows = conn.execute(
        'SELECT ticker, weight, market FROM holdings WHERE code = ? ORDER BY weight DESC',
        (code,)
    ).fetchall()
    if not rows:
        continue
    total_funds += 1
    total_holdings += len(rows)
    name = FUND_NAMES.get(code, code)
    total_w = sum(r[1] for r in rows)
    lines.append(f'{code} {name}')
    lines.append(f'  持仓数: {len(rows)} 条, 归一化总权重: {total_w:.1f}%')
    for t, w, m in rows:
        tag = {'US': '[US]', 'HK': '[HK]', 'A': '[CN]'}.get(m, '[?]')
        lines.append(f'    {tag} {t:10s} {w:6.2f}%')
    lines.append('')

lines.append('=' * 70)
lines.append(f'统计: {total_funds} 只基金, {total_holdings} 条持仓')
lines.append('=' * 70)

report = chr(10).join(lines)

out_path = os.path.join(os.path.dirname(__file__), '..', 'runtime_data', 'holdings_report.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(report)

conn.close()

# Print without emoji for gbk console
sys.stdout.buffer.write(report.encode('utf-8', errors='replace'))
sys.stdout.buffer.write(b'\n\n')
sys.stdout.buffer.write(f'报告已保存到 {out_path}\n'.encode('utf-8'))