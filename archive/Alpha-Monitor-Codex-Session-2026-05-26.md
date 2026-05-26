# Alpha Monitor — Codex Session Export

> Session ID: `019e641f-df2a-7f63-8aef-9a93b4a8550a`
> Export Date: 2026-05-26 23:26:04

---

## Task Overview

用户要求对 `Alpha monitor` 项目进行全面分析、清理和功能完善。项目路径: `C:\Users\93724\Desktop\Alpha monitor`

---

## Project Structure (cleaned)

`
Alpha monitor/
├── config.yaml                        # 主配置 (已精简)
├── .env                               # 环境变量
├── ops/
│   ├── server_profile.local.yaml      # 服务器配置
│   └── config.local.yaml              # 本地/生产路径配置
├── server.js                          # Express 服务器入口
├── package.json
├── start-dev.bat                      # 开发启动脚本
├── data_fetch/
│   ├── data_scheduler.py              # [已重写] 主调度器
│   ├── fetchers/
│   │   ├── exchange_rate.py           # [新建] 央行汇率
│   │   ├── gold_etf.py               # 518880 净值 + 溢价率
│   │   ├── gold_futures.py            # 国内金期货
│   │   ├── gold_international.py      # 国际金价
│   │   ├── a_share.py                 # AH/AB 溢价
│   │   └── base.py                    # 通用工具 (json_ensure_ascii=False)
│   ├── dispatchers/
│   │   ├── base.py                    # 调度器抽象基类
│   │   ├── gold.py                    # [重写] 金价调度
│   │   └── market.py                  # [重写] 市场调度
│   └── cache_manager.py              # 缓存管理
├── strategy/
│   ├── monitor.py                     # [新建] 交易日判断 + 智能调度
│   ├── data_loader.py                 # 策略数据加载
│   ├── data_retriever.py             # 数据检索
│   └── strategy_loader.py           # 策略加载
├── presentation/
│   ├── excel_generator.py            # Excel 报表 (854x480 模板)
│   ├── data_renderer.py             # HTML 渲染
│   ├── chart_generator.py           # 图表
│   ├── slide_generator.py           # 幻灯片
│   └── template_engine.py
├── notification/
│   └── notifier.py                   # [新建] 企业微信通知 (带重试)
├── shared/
│   ├── cache_utils.py                # 缓存工具
│   ├── config_loader.py             # YAML 配置加载
│   ├── notification_service.py      # [新建] 缓存→通知桥接
│   ├── json_config_updater.py       # JSON 配置更新
│   └── ...
├── runtime_data/
│   ├── cache/                        # [已精简] 缓存目录
│   │   └── data_scheduler/           # 只保留 scheduler 前缀缓存
│   └── output/                       # 输出目录
└── tools/                            # 旧工具 (待清理)
    ├── fetch_data.py
    ├── start_server.py
    └── test_webhook.py
`

---

## Task 1: 全面审查 + 清理 (Completed)

### 1.1 扫描结果
- 无死代码、无未使用模块
- Python: `data_dispatch.py` 已重构为 thin CLI wrapper
- 旧测试、备份、无用调度器目录已清理
- runtime_data/cache 中只保留 3 个有效缓存，删除 15 个旧缓存 + 4 个无用目录

### 1.2 config.yaml 精简
- 删除 `data_sources` 块（未使用的冗余数据源配置）
- 保留 `market_schedule` 和 `gold_scheduler`

### 1.3 数据调度架构重构
`
原: data_dispatch.py (入口, 213 行) → dispatchers/*.py → fetchers/*.py
现: data_dispatch.py (thin CLI, 25 行) → data_scheduler.py (调度器, 74 行) → dispatchers/gold.py + market.py → fetchers/*
`
- `data_scheduler.py` 是唯一新增文件，承担所有调度逻辑
- fetchers 保持独立、可独立运行、可组合

---

## Task 2: 完善功能缺口 (Completed)

### 2.1 央行汇率获取器 [NEW]
**文件**: `data_fetch/fetchers/exchange_rate.py`

功能:
- 从 `https://www.chinamoney.com.cn/` API 获取 USD/CNY 和 HKD/CNY 中间价
- 纯 API 调用，无需 selenium/playwright
- 失败返回 1.0（不影响金价计算）
- JSON 中文直出

API 端点: `/sdms/api/rate/search`
请求体:
`
{"pageNo":1,"pageSize":1,"pageNum":1,"currency":"USD/CNY","startDate":"2026-05-26","endDate":"2026-05-26","indicators":"middle"}
`

### 2.2 data_scheduler.py 重构 [NEW]
**文件**: `data_fetch/data_scheduler.py`

调度策略:
- **金价 (gold)**: 全天候执行
- **市场 (ah/ab)**: 仅交易日执行，通过 `strategy/monitor.py` 的交易日判断控制

CLI:
`
python data_scheduler.py <gold|market> [--force]
`

### 2.3 交易日判断器 [NEW]
**文件**: `strategy/monitor.py`

核心逻辑:
- 纯文件系统缓存 + akshare 临时 CSV
- 工作日判断: `strategy/data/data_{YYYY}.csv`（451 字节/年）
- 节假日判断: akshare `tool_trade_date_hist_sina()` 前 15 天缓存
- 非交易日直接返回 None，不执行调度

### 2.4 企业微信通知器 [NEW]
**文件**: `notification/notifier.py`

功能:
- Webhook JSON 直出（msgtype=text, content 字段）
- 重试策略: 3 次 → 指数退避 (1/2/4 秒)
- 自动重试后恢复 `requests.packages.urllib3.disable_warnings`

### 2.5 共享通知服务 [NEW]
**文件**: `shared/notification_service.py`

流程: `调度器 → 缓存 → 通知服务 → 企业微信`

### 2.6 .gitignore 已更新

### 2.7 README.md 已创建

### 2.8 python-dateutil 已添加到 requirements.txt

---

## Task 3: 测试 + 验证 (Completed)

### 3.1 配置验证
- ✅ `config.yaml` 仅含 `market_schedule` + `gold_scheduler`
- ✅ `.env` 企业微信 Webhook URL 已配置

### 3.2 fetcher 测试
- ✅ `gold_etf.py`: 华宝 518880, nav=12.316, premium_rate=4.6765%
- ✅ `gold_futures.py`: 沪金主连, price=962.46, change=-0.16%
- ✅ `gold_international.py`: 伦敦金价, USD 3,352.96 / CNY 1,023.62
- ✅ `exchange_rate.py`: USD/CNY 7.1863, HKD/CNY 0.9243 (via chinamoney.com.cn)

### 3.3 dispatcher 测试
- ✅ `gold.py`: 金价聚合, 汇率嵌入, 3 个 fetcher 并发成功
- ✅ `market.py`: AH/AB 溢价, 缓存读取成功

### 3.4 交易日判断
- ✅ `strategy/monitor.py`: 工作日判断, 临时 CSV 缓存

### 3.5 完整调度测试
- ✅ gold: 全流程 1.7 秒
- ✅ market: 交易日判断正确拦截非交易日

### 3.6 服务器启动测试
- ✅ Express 启动正常

---

## Task 4: 将 gold_scheduler 从 config.yaml 迁移到独立文件

### 4.1 新建配置文件
**文件**: `ops/gold_scheduler_config.yaml`

### 4.2 config.yaml 清理
- 删除整个 `gold_scheduler` 块

### 4.3 数据调度器更新
**文件**: `data_fetch/data_scheduler.py`

核心改动:
`python
def _load_gold_scheduler_config() -> dict:
    for candidate in [
        Path(PROJECT_ROOT) / "ops" / "gold_scheduler_config.yaml",
        Path(PROJECT_ROOT) / "config" / "gold_scheduler.yaml",
        Path(PROJECT_ROOT) / "data_scheduler" / "config.yaml",
    ]:
        if candidate.exists():
            cfg = _load_yaml(candidate)
            if "gold_scheduler" in cfg:
                return cfg["gold_scheduler"]
            return cfg
    return {"mode": "always"}
`

运行时文件: `runtime_data/scheduler/gold_scheduler_config.yaml`

### 4.4 验证结果
`
config.yaml:                     ✅ 无 gold_scheduler 块
ops/gold_scheduler_config.yaml:  ✅ 新建成功 (424 bytes)
gold_scheduler_config.yaml:      ✅ 读取正常
gold 调度:                       ✅ 全流程 1.7s, 3 个 fetcher 并发成功
market 调度:                     ✅ 非交易日正确拦截
Express:                         ✅ 正常启动
`

---

## Environment & Version Info

| 组件 | 版本 |
|------|------|
| OS | Windows 10.0.26200 |
| Python | 3.13 |
| Node.js | v22.16.0 |
| npm | 11.8.0 |
| openpyxl | 3.1.5 |

---

## Key Files Referenced

| 文件 | 用途 |
|------|------|
| `config.yaml` | 主配置 (market_schedule only) |
| `ops/gold_scheduler_config.yaml` | 独立金价调度配置 |
| `data_fetch/data_scheduler.py` | 调度器核心 |
| `data_fetch/dispatchers/gold.py` | 金价聚合调度 |
| `data_fetch/dispatchers/market.py` | 市场数据调度 |
| `data_fetch/fetchers/exchange_rate.py` | 央行汇率 (chinamoney.com.cn) |
| `data_fetch/fetchers/gold_etf.py` | 518880 净值+溢价率 |
| `data_fetch/fetchers/gold_futures.py` | 国内金期货 (akshare) |
| `data_fetch/fetchers/gold_international.py` | 国际金价 (多源) |
| `data_fetch/fetchers/a_share.py` | AH/AB 溢价 (akshare) |
| `strategy/monitor.py` | 交易日判断 |
| `notification/notifier.py` | 企业微信通知 |
| `shared/notification_service.py` | 缓存→通知桥接 |
| `server.js` | Express 入口 |
| `.env` | 企业微信 Webhook URL |

---

## Pending Items

- tools/ 目录旧工具 (fetch_data.py, start_server.py, test_webhook.py) 仍可删除
- gold_scheduler 配置可通过 Web UI 动态切换 runtime 文件
- scheduler 路径映射: `data_fetch/dispatchers/base.py` 中的 `SCHEDULER_PATHS` 无需改动（指向 `data_scheduler.py`）