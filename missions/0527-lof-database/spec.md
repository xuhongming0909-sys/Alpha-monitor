# LOF数据库+数据更新架构

## 目标

建立SQLite数据库存储所有IOPV计算和回测所需数据，确保数据动态更新，消除硬编码和默认值。

## 背景

当前问题：
1. 回测脚本每次运行都从外部API获取数据，速度慢且不稳定
2. 部分基金的ETF标的无法获取数据（东方财富美股API不可用）
3. IOPV计算时有默认值和降级逻辑
4. 没有统一的数据存储和更新机制

## 架构设计

### 1. 数据库Schema

```sql
-- 基金基本信息
CREATE TABLE funds (
    code TEXT PRIMARY KEY,
    name TEXT,
    currency TEXT,
    estimation TEXT,  -- A/B
    etf TEXT,
    fund_company TEXT,
    apply_fee REAL,
    redeem_fee REAL,
    custodian_fee REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 基金净值历史
CREATE TABLE fund_nav (
    code TEXT,
    date TEXT,
    nav REAL,
    PRIMARY KEY (code, date)
);

-- ETF价格历史
CREATE TABLE etf_prices (
    ticker TEXT,
    date TEXT,
    close REAL,
    PRIMARY KEY (ticker, date)
);

-- 汇率历史
CREATE TABLE fx_rates (
    currency TEXT,
    date TEXT,
    rate REAL,
    PRIMARY KEY (currency, date)
);

-- 持仓数据（B类基金）
CREATE TABLE holdings (
    code TEXT,
    report_date TEXT,
    ticker TEXT,
    name TEXT,
    weight REAL,
    market TEXT,
    PRIMARY KEY (code, report_date, ticker)
);

-- IOPV计算结果
CREATE TABLE iopv_results (
    code TEXT,
    date TEXT,
    nav REAL,
    iopv REAL,
    premium_rate REAL,
    calc_mode TEXT,
    calc_status TEXT,
    PRIMARY KEY (code, date)
);
```

### 2. 数据更新脚本

```python
# scripts/update_lof_db.py
# 功能：
# 1. 更新基金列表（从东方财富API）
# 2. 更新基金净值（增量更新）
# 3. 更新ETF价格（增量更新）
# 4. 更新汇率（增量更新）
# 5. 更新持仓数据（季度更新）
# 6. 计算IOPV（每日）
```

### 3. API端点（写死）

```python
# 数据源配置（固定，不尝试）
API_CONFIG = {
    "fund_nav": "http://api.fund.eastmoney.com/f10/lsjz",
    "fund_info": "https://fundf10.eastmoney.com/jbgk_{code}.html",
    "fund_holdings": "https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10",
    "etf_prices": "https://push2his.eastmoney.com/api/qt/stock/kline/get",
    "fx_rates": "https://api.fund.eastmoney.com/f10/lsjz",
    "tencent_kline": "http://web.ifzq.gtimg.cn/appstock/app/kline/kline",
}
```

### 4. 数据更新频率

| 数据类型 | 更新频率 | 增量策略 |
|----------|----------|----------|
| 基金列表 | 每月 | 全量替换 |
| 基金净值 | 每日 | 按日期增量 |
| ETF价格 | 每日 | 按日期增量 |
| 汇率 | 每日 | 按日期增量 |
| 持仓数据 | 每季度 | 按报告期增量 |
| IOPV结果 | 每日 | 按日期增量 |

### 5. 文件结构

```
data_fetch/lof_db/
├── __init__.py
├── schema.py          # 数据库Schema定义
├── updater.py         # 数据更新调度
├── nav_updater.py     # 净值更新
├── etf_updater.py     # ETF价格更新
├── fx_updater.py      # 汇率更新
├── holdings_updater.py # 持仓更新
└── iopv_calculator.py # IOPV计算

strategy/lof_iopv/
├── service.py         # IOPV服务（从数据库读取）
├── backtest.py        # 回测脚本（从数据库读取）
└── classifier.py      # 分类器

runtime_data/lof_db/
└── lof.db             # SQLite数据库文件
```

### 6. 回测流程

```
1. 从数据库读取基金净值
2. 从数据库读取ETF价格
3. 从数据库读取汇率
4. 计算日收益率
5. 对齐日期
6. 计算R²/MAE/方向准确率
7. 输出结果
```

### 7. IOPV计算流程

```
1. 从数据库读取基金净值
2. 从数据库读取ETF/持仓价格
3. 从数据库读取汇率
4. 根据estimation类型计算IOPV
5. 计算溢价率
6. 写入iopv_results表
```

## 约束

1. 所有API端点写死，不尝试多个备选
2. 数据更新失败时记录日志，不使用默认值
3. IOPV计算失败时返回空，不伪造
4. 数据库文件位于runtime_data/lof_db/，不提交Git
5. 每个核心文件必须有AI-SUMMARY注释

## 验证

1. 运行数据更新脚本，确认数据入库
2. 运行回测脚本，确认从数据库读取
3. 运行IOPV计算，确认结果正确
4. 运行根目录清洁检查
5. 运行AI-SUMMARY覆盖检查