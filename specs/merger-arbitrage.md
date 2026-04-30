---
name: merger-arbitrage
description: 并购重组公告监控与套利机会挖掘模块规格
type: spec
---

# 合并套利模块规格

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. 模块职责

- 从巨潮资讯抓取并购重组相关公告，筛选潜在套利机会
- 过滤子公司内部重组、非上市公司主体交易、已终止交易
- 提供 AI 生成的单家公司并购简报
- 支持按公司分组展示和逐家公司推送

## 2. 数据来源

| 层级 | 来源 | 说明 |
|------|------|------|
| 公告搜索 | 巨潮资讯 `cninfo.com.cn/new/hisAnnouncement/query` | POST 分页搜索 |
| 实时股价 | 腾讯行情 `web.sqt.gtimg.cn` | 用于计算套利空间 |
| AI 报告 | DeepSeek API | 单家公司并购简报生成 |

## 3. 关键文件

| 路径 | 职责 |
|------|------|
| `data_fetch/merger/fetcher.py` | 调用 `MergerArbitrageScraper().run()` |
| `data_fetch/merger/source.py` | 核心爬虫：搜索、过滤、解析、股价填充 |
| `data_fetch/merger/normalizer.py` | 转为 Bus 标准记录 |
| `strategy/merger/service.py` | 消费 Bus 记录，恢复旧 API 结构 |
| `notification/merger_report/service.js` | AI 报告生成与推送 |

## 4. 数据字段

### 4.1 原始公告字段（`raw`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `announcementId` | string | 公告 ID |
| `secCode` | string | 股票代码 |
| `secName` | string | 股票名称 |
| `title` | string | 公告标题（已清理高亮标签） |
| `announcementTime` | number | 公告时间戳（毫秒） |
| `announcementDate` | string | 公告日期（YYYY-MM-DD） |
| `pdfUrl` | string | PDF 链接 |
| `announcementUrl` | string | 公告页面链接 |
| `searchKeyword` | string | 匹配到的搜索关键词 |
| `isCore` | boolean | 是否核心公告 |
| `dealType` | string | 交易类型：要约收购/吸收合并/重组/协议收购/私有化/其他 |
| `offerPrice` | number | 解析出的交易价格（元/股） |
| `stockPrice` | number | 当前股价 |
| `stockName` | string | 当前股票名称 |

### 4.2 Bus Metrics

| 字段 | 来源 |
|------|------|
| `announcement_date` | `item.announcementDate` |
| `deal_type` | `item.dealType` 或 `item.type` |
| `offer_price` | `item.offerPrice` 或 `item.bidPrice` |
| `stock_price` | `item.stockPrice` 或 `item.price` |

## 5. 计算规则

### 5.1 搜索关键词

```
SEARCH_KEYWORDS = ['要约收购', '吸收合并', '协议收购', '重大资产重组', '私有化']
```

### 5.2 核心公告关键词

```
CORE_KEYWORDS = ['要约收购报告书', '要约收购提示性公告', '收购报告书', '吸收合并报告书', '重大资产重组报告书', '重组报告书', '合并报告书']
```

### 5.3 过滤规则

| 过滤类型 | 关键词示例 | 结果 |
|----------|-----------|------|
| 子公司重组 | `全资子公司`, `吸收合并全资子公司` | 排除 |
| 非上市公司主体 | `控股股东拟被吸收合并`, `间接股东权益变动` | 排除 |
| 已终止交易 | `终止公告`, `撤回申请`, `未获通过`, `过户完成` | 排除 |

### 5.4 交易价格解析

正则模式：
- `(\d+\.?\d*)\s*元/股`
- `(\d+\.?\d*)\s*元每股`
- `要约价[为是]?\s*(\d+\.?\d*)\s*元`
- `收购价[为是]?\s*(\d+\.?\d*)\s*元`
- `价格[为是]?\s*(\d+\.?\d*)\s*元`

### 5.5 去重规则

- 按 `announcementId` 去重
- 按股票代码二次去重：保留最新核心公告，核心公告优先于非核心

## 6. API 合同

### 6.1 对外端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/market/merger` | 完整 merger 公告列表 |
| GET | `/api/merger/reports/today` | 今日公司分组列表 |
| GET | `/api/merger/report?date=&code=&name=` | 单家公司报告查询 |
| POST | `/api/merger/report/generate` | 强制生成/刷新单家公司报告 |
| GET | `/api/market/overview` | 看板概览（含今日 merger TOP 5） |

### 6.2 响应结构

```json
{
  "success": true,
  "data": [...],
  "total": 15,
  "updateTime": "2026-04-30T00:00:00+08:00",
  "keywords": ["要约收购", "吸收合并", "协议收购", "重大资产重组", "私有化"]
}
```

### 6.3 AI 报告端点

**POST** `/api/merger/report/generate`

请求体：
```json
{
  "date": "2026-04-30",
  "code": "000001",
  "name": "平安银行",
  "force": false
}
```

## 7. 推送规则

### 7.1 主摘要推送

- Merger 数据纳入看板概览，但不纳入定时摘要 Markdown 推送
- 看板展示今日公告公司 TOP 5

### 7.2 AI 简报推送

- `notification/merger_report/service.js` 逐家公司生成 DeepSeek AI 简报
- 推送渠道：企业微信
- 报告长度限制：`report_max_chars: 500`
- 包含：交易介绍、交易对价、信息来源

## 8. 配置参数

```yaml
data_fetch.plugins.merger:
  intraday: false
  refresh_time: "00:00"
  daily_incremental_sync: false
  announcement_timeout_seconds: 5
  quote_timeout_seconds: 15
  announcement_lookback_days: 90

strategy.merger:
  same_day_only: true
  ai_provider: "deepseek"
  ai_model: "deepseek-chat"
  prompt_template_code: "MERGER_DEAL_OVERVIEW_V1"
  report_max_chars: 500
  deepseek_api_key: "${DEEPSEEK_API_KEY}"
  deepseek_base_url: "https://api.deepseek.com"
```

## 9. 验收标准

- **AC-001**: 每日 00:00 自动抓取 90 天内公告
- **AC-002**: 子公司重组、非上市公司主体、已终止交易准确过滤
- **AC-003**: 交易价格从标题正确解析
- **AC-004**: AI 报告基于真实公告数据，不臆测编造
- **AC-005**: 报告生成失败时有兜底推送机制
