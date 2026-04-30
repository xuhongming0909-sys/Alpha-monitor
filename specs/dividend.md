---
name: dividend
description: 股息提醒模块规格：分红派息数据查询、股息率计算、近期股权登记日提醒
type: spec
---

# Module Spec: 股息提醒

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. Scope

- 查询单只股票分红派息数据，计算股息率
- 维护用户自选股息组合（手动 + 监控派生）
- 提供近期股权登记日提醒
- 不覆盖：全市场即将分红榜单（当前版本未启用）

## 2. Requirements

- 支持 A 股、B 股（USD/HKD）、港股通标的分红查询
- 股息率必须基于真实股价实时计算
- 组合数据持久化到运行态 JSON
- 股价抓不到时显示 `--`，不伪造

## 3. Interface / API

**数据抓取（Python）**
- `fetch_dividend_snapshot(code: str) -> dict` — 单只股票分红数据
- `fetch_upcoming_dividend_snapshot(days: int = 3) -> dict` — 近期提醒（当前返回空列表）

**策略层（Python）**
- `build_dividend_response(fetch_payload: dict) -> dict` — 透传抓取结果

**运行态服务（JS）**
- `loadPortfolio()` — 读取合并后的股息组合
- `refreshPortfolio()` — 刷新组合内所有股票的最新分红数据
- `addDividendStock({ code, name })` — 添加股票到手动组合
- `removeDividendStock(code)` — 从手动组合移除
- `upcomingDividends(days = 7)` — 按登记日筛选近期分红

**HTTP API**
- `GET /api/dividend?action=portfolio` — 获取组合
- `GET /api/dividend?action=upcoming&days=N` — 近期登记日提醒（1-365）
- `GET /api/dividend?action=refresh` — 刷新组合数据
- `GET /api/dividend?action=search&keyword=xxx&limit=N` — 股票搜索
- `POST /api/dividend` — 添加股票 `{ code, name }`
- `DELETE /api/dividend/:code` — 移除股票

## 4. Rules

**数据来源**
- 分红数据：akshare `stock_dividend_cninfo`（巨潮资讯）
- 股价：腾讯行情 `https://qt.gtimg.cn/q={query_code}`
- B 股汇率：USD/HKD 通过 `shared/market_service.py` 换算

**币种规则**
- 900 开头 → USD
- 200/201 开头 → HKD
- 其他 → CNY

**计算规则**
- `dividendPerShare = dividendPer10Shares / 10`
- `dividendYield = (dividendPerShare / currentPrice) * 100`（保留 2 位小数）
- 股价或分红缺失时，股息率为 null

**组合合并规则**
- 手动组合（`dividend_portfolio.json`）优先级高于监控派生
- 监控派生：从 custom_monitor 的 acquirerCode + targetCode 自动提取 A/B 股
- 按 code 去重合并

**字段映射（AkShare -> 输出）**
- 实施方案公告日期 / 公告日期 → announcementDate
- 报告时间 / 报告期 → reportPeriod
- dividend 类型 → dividendType
- 派息比例 / 现金 dividend 比例 → dividendPer10Shares
- 送股比例 → stockDividendPer10
- 转增比例 → capitalReservePer10
- 股权登记日 → recordDate
- 除权日 / 除权除息日 → exDividendDate
- 派息日 → payDate
- 实施方案 dividend 说明 / 方案说明 → description

## 5. Acceptance

- [ ] 输入有效 A 股代码，返回包含 dividendPerShare、dividendYield 的完整数据
- [ ] 输入 B 股代码（如 900xxx），currency 为 USD，股价使用上海 B 股行情
- [ ] 股价抓不到时，currentPrice 为 null，dividendYield 为 null
- [ ] 添加重复股票到组合，抛错"该股票已在 dividend 组合中"
- [ ] upcoming 接口 days 超限时返回 400 错误
