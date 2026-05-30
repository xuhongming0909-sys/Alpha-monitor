# LOF 基金全流程分析 Skill

**触发词**: lof分析, LOF fund analysis, 基金代码分析, lof pipeline

## 用途

输入一个 LOF 基金代码（如 161125），自动完成：基金分类 → 数据抓取 → 数据库搭建 → IOPV 计算 → 溢价率 → 结果呈现。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fund_code | string | 是 | 6位基金代码，如 `161125` |

## 输出

完整分析报告：基金信息、分类结果、持仓明细、实时行情、IOPV 估值、溢价率、数据库状态。

## 执行步骤

### Step 1: 基金分类

判断基金类型（指数型/主动型）和 ETF 映射关系。

```bash
cd "C:\Users\93724\Desktop\Alpha monitor"
python -c "
import sys; sys.path.insert(0,'.')
from data_fetch.lof_iopv.fund_classifier import is_index_fund, get_fund_class, INDEX_ETF
code = '{fund_code}'
print(f'指数型: {is_index_fund(code)}')
print(f'分类: {get_fund_class(code)}')
if code in INDEX_ETF:
    print(f'ETF映射: {INDEX_ETF[code]}')
"
```

### Step 2: 数据库初始化 + 状态检查

确保 5 张核心表存在，报告当前数据量。

```bash
python -c "
import sys; sys.path.insert(0,'.')
from data_fetch.lof_db.schema import init_db, get_db
init_db()
conn = get_db()
for t in ['fund_nav','etf_prices','stock_prices','fx_rates','holdings']:
    n = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
    print(f'{t}: {n} rows')
conn.close()
"
```

### Step 3: 抓取实时快照

调用数据源层获取最新 NAV、行情、持仓。

```bash
python -c "
import sys, json; sys.path.insert(0,'.')
from data_fetch.lof_iopv.source import build_lof_snapshot
result = build_lof_snapshot()
rows = result.get('data', [])
target = [r for r in rows if r.get('code') == '{fund_code}']
if target:
    r = target[0]
    print(json.dumps({
        'name': r.get('name'),
        'nav': r.get('nav'),
        'navDate': r.get('navDate'),
        'price': r.get('price'),
        'currency': r.get('currency'),
        'stockPosition': r.get('stockPosition'),
        'holdings_count': len(r.get('holdings', [])),
        'dailyLimit': r.get('dailyLimit'),
    }, ensure_ascii=False, indent=2))
else:
    print('基金未在监控池中，需要先加入 config.yaml')
"
```

### Step 4: 计算 IOPV + 溢价率

调用业务计算层获取完整的 IOPV 估算和溢价率。

```bash
python -c "
import sys, json; sys.path.insert(0,'.')
from strategy.lof_iopv.service import build_lof_response
from data_fetch.lof_iopv.source import build_lof_snapshot
snap = build_lof_snapshot()
resp = build_lof_response(snap)
rows = resp.get('data', {}).get('rows', [])
target = [r for r in rows if r.get('code') == '{fund_code}']
if target:
    r = target[0]
    print(json.dumps({
        'code': r.get('code'), 'name': r.get('name'),
        'iopv': r.get('iopv'), 'price': r.get('price'),
        'premiumRate': r.get('premiumRate'), 'premiumAbs': r.get('premiumAbs'),
        'iopvNote': r.get('iopvNote'),
        'nav': r.get('nav'), 'navDate': r.get('navDate'),
        'fxRatio': r.get('fxRatio'), 'stockRatio': r.get('stockRatio'),
        'dailyLimit': r.get('dailyLimit'),
    }, ensure_ascii=False, indent=2))
"
```

### Step 5: 查询历史数据

查看数据库中的净值和持仓记录。

```bash
python -c "
import sys; sys.path.insert(0,'.')
from data_fetch.lof_db.schema import get_db
conn = get_db()
code = '{fund_code}'
print('=== 最近5条净值 ===')
for r in conn.execute('SELECT * FROM fund_nav WHERE code=? ORDER BY date DESC LIMIT 5', (code,)):
    print(r)
print('=== 持仓 ===')
for r in conn.execute('SELECT * FROM holdings WHERE code=? ORDER BY weight DESC', (code,)):
    print(r)
conn.close()
"
```

### Step 6: 汇总报告

将以上结果整合为结构化报告。报告格式：

```
## {fund_code} 基金分析报告

### 基本信息
- 名称: xxx
- 类型: 指数型/主动型
- 币种: USD/HKD

### 行情
- 场内价: xxx
- 净值: xxx (日期)
- IOPV 估算: xxx (note)
- 溢价率: xxx%

### 持仓
| 序号 | 标的 | 权重 | 市场 |
|------|------|------|------|

### 数据库状态
- fund_nav: N 条
- 持仓: N 条
```

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| 基金未在监控池 | config.yaml 未配置 | 提示用户添加到 lof_arbitrage.funds |
| 无净值数据 | DB 无记录 | 执行 nav_updater 补数据 |
| 无持仓 | 主动型无 DB/hardcoded | 用 PDF 解析 Skill 补充 |
| ETF 价格缺失 | akshare 源问题 | 尝试 yahoo_finance.py 备用源 |

## 新增基金流程

若基金不在配置中：

1. `config/config.yaml` → `lof_arbitrage.funds` 添加条目
2. `fund_classifier.py` → 确认分类映射
3. 指数型 → `INDEX_ETF` 添加 ETF 映射
4. 主动型 → `holdings_hardcoded.py` 添加兜底持仓
5. 重跑 Step 2-5

## 关键文件

| 文件 | 职责 |
|------|------|
| `data_fetch/lof_iopv/fund_classifier.py` | 分类 + 持仓获取 |
| `data_fetch/lof_iopv/source.py` | 数据源（NAV+行情+持仓） |
| `data_fetch/lof_db/schema.py` | DB Schema |
| `strategy/lof_iopv/calc.py` | IOPV 计算公式 |
| `strategy/lof_iopv/service.py` | 业务层 |
| `config/config.yaml` | 基金列表 |

## IOPV 公式

```
IOPV = NAV_T-2 * (1 + stock_ratio/100 * weighted_ret) * fx_ratio
```
- 指数型：ETF/指数映射法
- 主动型：前10持仓加权法