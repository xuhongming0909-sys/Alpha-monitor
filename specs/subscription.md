---
name: subscription
description: 打新/申购模块规格：IPO 与可转债申购数据抓取、日程状态机、SQLite 历史持久化
type: spec
---

# Module Spec: 打新/申购

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. Scope

- 抓取 A 股新股 IPO 和可转债申购数据
- 管理申购日程状态（即将申购/申购中/待缴款/待上市/已上市）
- SQLite 本地历史库做持久化与状态管理
- 不覆盖：港股 IPO、基金申购

## 2. Requirements

- IPO 数据来自 AkShare，补充打新收益率数据
- 可转债数据来自 AkShare 转债发行列表
- 状态机基于日期自动判断，缺失日期按工作日推算
- 历史数据保留 1095 天（3 年，可配置）
- 必须有 code 和 subscribeDate 才入池

## 3. Interface / API

**数据抓取（Python）**
- `fetch_ipo_snapshot() -> dict` — A 股新股申购数据
- `fetch_bond_subscription_snapshot() -> dict` — 可转债申购数据

**策略层（Python）**
- `build_subscription_response(fetch_payload, bus_records) -> dict` — 按旧接口格式恢复 upcoming/data 结构

**策略层（JS）**
- `collectTodaySubscriptionEvents(ipo, bonds, todayText) -> Array<Event>` — 收集今日申购/缴款/上市事件
- `sanitizeSubscriptionResult(result, type) -> object` — 清洗并去重申购数据

**HTTP API**
- `GET /api/market/ipo?force=0|1` — IPO 数据
- `GET /api/market/convertible-bonds?force=0|1` — 可转债数据
- `GET /api/market/subscriptions?force=0|1` — 合并返回 IPO + 可转债

## 4. Rules

**数据来源**
- IPO：akshare `stock_new_ipo_cninfo`
- 打新收益率：akshare `stock_dxsyl_em`
- 可转债：akshare `bond_zh_cov`
- 持久化：SQLite `subscription_history_db`

**状态机**
| 条件 | 状态 |
|------|------|
| subscribe_date > today | upcoming（daysUntilSubscribe = 差值天数） |
| subscribe_date == today | subscribing |
| listing_date <= today | listed |
| payment_date >= today | waiting_payment |
| listing_date > today | waiting_listing |
| 其他 | subscribed |

**日期推算（工作日）**
- lotteryDate 缺失：subscribe_date + 1 个工作日
- paymentDate 缺失：max(subscribe_date + 2 个工作日, lottery_date + 1 个工作日)

**IPO 字段映射**
- 证券代码/证券代号/股票代码 → code
- 证券简称/名称 → name
- 申购日期/发行日期 → subscribeDate
- 上市日期 → listingDate
- 中签公告日/摇号结果公告日 → lotteryDate
- 中签缴款日/缴款日期 → paymentDate
- 发行价格/发行价 → issuePrice
- 发行市盈率 → peRatio
- 网上发行中签率 → lotteryRate
- 网上申购上限 → subscribeLimit

**可转债字段映射**
- 债券代码/代码 → code
- 债券简称/名称 → name
- 申购日期 → subscribeDate
- 中签号发布日 → lotteryDate
- 上市时间/上市日期 → listingDate
- 申购代码 → subscribeCode
- 申购上限 → subscribeLimit
- 正股代码 → stockCode
- 正股简称 → stockName
- 正股价/正股价格 → stockPrice
- 转股价 → convertPrice
- 转股价值 → convertValue
- 债现价/现价 → bondPrice
- 转股溢价率 → premiumRate
- 中签率 → lotteryRate
- 发行规模 → issueSizeYi
- 信用评级 → creditRating

**去重规则**
- 以 code + subscribeDate + paymentDate + listingDate 为联合键
- 同键多条记录，取字段完整度最高的一条
- upcoming 和 data 数组去重合并

## 5. Acceptance

- [ ] IPO 接口返回 upcoming（即将申购）和 data（历史）两个数组
- [ ] 状态为 upcoming 的条目按 daysUntilSubscribe 升序排列
- [ ] 缺失 lotteryDate/paymentDate 时，按工作日规则自动推算
- [ ] 历史数据超过 1095 天的自动清理
- [ ] 今日有申购/缴款/上市事件时，推送摘要正确展示
