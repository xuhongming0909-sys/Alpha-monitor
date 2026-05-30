# PDF 基金季报持仓提取 Skill

**触发词**: PDF持仓提取, 季报解析, PDF holdings extraction, 报告解析

## 用途

从基金季报 PDF 中提取前10大持仓数据（股票代码、名称、权重、市场），写入 LOF 数据库。支持自动下载和 Vision LLM 解析。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fund_code | string | 否 | 6位基金代码（不指定则更新全部） |
| pdf_path | string | 否 | 本地 PDF 路径（不指定则自动下载） |

## 输出

- 持仓数据写入 `runtime_data/lof_db/lof.db` 的 `holdings` 表
- 输出提取结果摘要（持仓数、权重合计、覆盖基金数）

## 执行步骤

### Step 1: 自动更新全部基金持仓

最常用场景：一键更新所有配置基金的持仓。

```bash
cd "C:\Users\93724\Desktop\Alpha monitor"
python -c "
import sys; sys.path.insert(0,'.')
from data_fetch.lof_iopv.report_holdings import update_all_holdings
from shared.config.script_config import load_config
cfg = load_config()
plugins = cfg.get('data_fetch', {}).get('plugins', {})
lof_cfg = plugins.get('lof_arbitrage', plugins.get('lof_iopv', {}))
codes = [f['code'] for f in lof_cfg.get('funds', [])]
print(f'更新 {len(codes)} 只基金持仓...')
update_all_holdings(codes)
print('完成')
"
```

### Step 2: 查询提取结果

```bash
python -c "
import sys; sys.path.insert(0,'.')
from data_fetch.lof_db.schema import get_db
conn = get_db()
rows = conn.execute('SELECT code, report_date, COUNT(*) as cnt, SUM(weight) as total_weight FROM holdings GROUP BY code, report_date ORDER BY report_date DESC').fetchall()
for r in rows:
    print(f'{r[0]} | {r[1]} | {r[2]}只 | 权重合计{r[3]:.2f}%')
conn.close()
"
```

### Step 3: 单基金持仓更新

针对特定基金更新持仓（跳过已有最新数据的）。

```bash
python -c "
import sys; sys.path.insert(0,'.')
from data_fetch.lof_iopv.report_holdings import update_fund_holdings
update_fund_holdings('{fund_code}')
print('完成')
"
```

## 技术架构

```
季报 PDF
    ↓
下载（eastmoney docf10 API）
    ↓
PyMuPDF 渲染每页为图片
    ↓
截取「前十名股票投资」区域
    ↓
Vision LLM（DeepSeek/OpenAI）提取结构化数据
    ↓
ticker 解析（ticker_resolver.py）
    ↓
写入 holdings 表（直接覆盖）
```

## 核心代码

`data_fetch/lof_iopv/report_holdings.py`:

- `update_all_holdings(codes)`: 批量更新入口
- `update_fund_holdings(code)`: 单基金更新
- `_extract_from_pdf(pdf_path, code)`: PDF → 图片 → LLM 提取
- `_resolve_ticker(raw_name)`: 股票名称 → 交易代码
- `_save_to_db(code, holdings)`: 写入 DB

## LLM Prompt 模板

提取 Prompt 内嵌在 `report_holdings.py` 的 `_LLM_PROMPT` 常量中：
- 输入：PDF 渲染图片（base64）
- 输出：JSON 数组 `[{"name":"xxx","ticker":"xxx","weight":x.x,"market":"US/HK/CN"}]`
- 支持 DeepSeek Vision 和 OpenAI Vision 两种后端

## 数据库写入

持仓写入 `holdings` 表，schema：
```sql
CREATE TABLE holdings (
    code TEXT,           -- 基金代码
    report_date TEXT,    -- 报告日期
    ticker TEXT,         -- 交易代码（如 AAPL, 0700.HK）
    name TEXT,           -- 股票名称
    weight REAL,         -- 占基金净值比例(%)
    market TEXT,         -- US/HK/CN
    PRIMARY KEY (code, report_date, ticker)
);
```

更新策略：同一基金的同一报告期数据直接覆盖。

## 依赖

- `PyMuPDF` (fitz): PDF 渲染
- `httpx`/`requests`: HTTP 请求
- Vision LLM API: DeepSeek 或 OpenAI（通过 config 配置）
- `shared/config/script_config.py`: 读取配置

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| PDF 下载失败 | eastmoney 限流 | 重试 + 切换代理 |
| LLM 提取为空 | PDF 格式不标准 | 记录日志，跳过 |
| ticker 解析失败 | 股票名无法匹配 | 输出原始名，人工确认 |
| 持仓权重合计 < 50% | 提取不完整 | 标记 warning |

## 关键文件

| 文件 | 职责 |
|------|------|
| `data_fetch/lof_iopv/report_holdings.py` | PDF 下载 + 渲染 + LLM 提取 + DB 写入 |
| `data_fetch/lof_iopv/ticker_resolver.py` | 股票名 → 交易代码解析 |
| `data_fetch/lof_iopv/fund_classifier.py` | 基金分类（决定用 ETF 映射还是持仓加权） |
| `data_fetch/lof_db/schema.py` | 数据库 Schema |
| `runtime_data/qreport/` | PDF 缓存目录 |