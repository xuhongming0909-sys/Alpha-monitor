# API 参考手册

**用途**：项目所有外部 API 和内部 API 的集中参考，供开发和维护时查阅。
**更新规则**：每次新增/变更 API 调用时，同步更新本文档。

---

## 1. 内部 API（项目服务暴露）

项目服务运行在 Node.js，默认端口 `5001`（本地）/ `43.139.35.190`（服务器）。

| 端点 | 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|------|
| `/api/health` | GET | - | `{status, uptime}` | 健康检查 |
| `/api/market/lof-arbitrage` | GET | `?force=1`（可选） | LOF套利数据 | 主数据接口，加force跳过缓存 |

---

## 2. 外部 API — 腾讯行情（qt.gtimg.cn）

**用途**：获取 A 股、港股、美股实时行情
**无需代理**：国内直连
**请求频率**：无严格限制，建议 < 10次/秒

### 2.1 股票实时行情

```
GET https://qt.gtimg.cn/q={code}
```

**code 格式**：
- A 股：`sh600000`（沪市）、`sz000001`（深市）
- 港股：`hk00700`
- 美股：`usAAPL`、`usGOOGL`（后缀 `.us`）

**返回**：`~` 分隔的字符串，字段顺序：

| 位置 | 字段 | 示例 |
|------|------|------|
| 1 | 名称 | 浦发银行 |
| 3 | 最新价 | 12.50 |
| 4 | 昨收 | 12.40 |
| 5 | 开盘 | 12.45 |
| 6 | 成交量 | 1234567 |
| 8 | 时间戳 | 20260527150000 |
| 9 | 涨跌额 | 0.10 |
| 10 | 涨跌幅 | 0.81 |

**调用示例**：
```python
import requests
text = requests.get("https://qt.gtimg.cn/q=sh600000").text
fields = text.split("~")
price = float(fields[3])
```

### 2.2 K 线数据

```
GET http://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={code},day,{count}
```

**参数**：
- `code`：同上
- `count`：K 线天数，如 `30` 表示最近 30 天

**返回**：JSON，`data.day` 数组包含 `[date, open, close, high, low, volume]`

---

## 3. 外部 API — 东方财富（eastmoney.com）

**用途**：基金净值、持仓、申购状态、历史K线
**无需代理**：国内直连
**请求频率**：建议 < 5次/秒

### 3.1 基金历史净值

```
GET http://api.fund.eastmoney.com/f10/lsjz
```

**参数**：
| 参数 | 说明 | 示例 |
|------|------|------|
| `fundCode` | 基金代码 | `501312` |
| `pageIndex` | 页码 | `1` |
| `pageSize` | 每页条数 | `3` |
| `callback` | JSONP回调（留空返回JSON） | |

**返回**：JSON，`Data.LSJZList` 数组包含：
- `FSRQ`：日期
- `DWJZ`：单位净值
- `LJJZ`：累计净值
- `JZZZL`：净值增长率

### 3.2 基金持仓数据

```
GET http://fundf10.eastmoney.com/FundArchivesDatas.aspx
```

**参数**：
| 参数 | 说明 | 示例 |
|------|------|------|
| `type` | 数据类型 | `jjcc`（基金持仓） |
| `code` | 基金代码 | `501312` |
| `topline` | 取前N大持仓 | `10` |
| `year` | 年份（可选） | `2026` |
| `month` | 月份（可选） | `3` |

**返回**：HTML 片段，需解析表格

### 3.3 基金基础信息

```
GET https://fund.eastmoney.com/pingzhongdata/{code}.js
```

**返回**：JavaScript 变量，包含：
- `fS_name`：基金名称
- `fS_code`：基金代码
- 资产规模、基金经理等信息

### 3.4 基金申购状态

```
GET https://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx
```

**参数**：`t=8`（全部基金申购状态列表）

**返回**：JSON 数组，包含：
- `code`：基金代码
- `name`：基金名称
- `applyStatus`：申购状态（1=开放申购, 2=暂停大额, 3=暂停申购, 4=限制大额）
- `applyMoney`：限额金额（万）

**解析示例**：
```python
import re, json
resp = requests.get("https://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=8").text
data = json.loads(re.search(r'\[.*\]', resp, re.DOTALL).group())
```

### 3.5 股票历史K线（含美股）

```
GET https://push2his.eastmoney.com/api/qt/stock/kline/get
```

**参数**：
| 参数 | 说明 | 示例 |
|------|------|------|
| `secid` | 股票ID | `107.XOP`（美股格式：`市场.代码`） |
| `fields1` | 基础字段 | `f1,f2,f3` |
| `fields2` | K线字段 | `f51,f52,f53`（日期,开盘,收盘） |
| `klt` | K线类型 | `101`（日K） |
| `fqt` | 复权类型 | `1`（前复权） |
| `beg` | 开始日期 | `20260520` |
| `end` | 结束日期 | `20260527` |

**市场代码**：
- `1`：沪市
- `0`：深市
- `105`：纳斯达克
- `106`：纽交所
- `107`：美交所
- `116`：港股

---

## 4. 外部 API — 集思录（jisilu.cn）

**用途**：可转债数据、QDII溢折价、套利机会
**需要代理**：部分接口需登录Cookie
**请求频率**：反爬严格，建议 < 2次/秒

### 4.1 可转债预发行数据

```
GET https://www.jisilu.cn/webapi/cb/pre/
```

**返回**：JSON，可转债预发行列表

### 4.2 QDII溢价数据

```
GET https://www.jisilu.cn/data/qdii/?code={code}
```

**参数**：`code` 基金代码
**返回**：JSON，包含溢折价率

### 4.3 A股套利机会

```
GET https://www.jisilu.cn/data/taoligu/astock_arbitrage_list/
```

**返回**：JSON 数组，A 股相关套利机会

### 4.4 港股套利机会

```
GET https://www.jisilu.cn/data/taoligu/hk_arbitrage_list/
```

### 4.5 深市套利机会

```
GET https://www.jisilu.cn/data/taoligu/cn_arbitrage_list/
```

---

## 5. 外部 API — 雪球（xueqiu.com）

**用途**：基金持仓、股票行情
**需要代理**：部分接口需Cookie
**请求频率**：中等，建议 < 3次/秒

### 5.1 基金持仓数据

```
GET https://stock.xueqiu.com/v5/fund/portfolio/stock.json
```

**参数**：
| 参数 | 说明 | 示例 |
|------|------|------|
| `symbol` | 基金代码 | `501225` |
| `size` | 返回持仓数 | `10` |

**返回**：JSON，`data.list` 数组包含：
- `stock_name`：股票名称
- `stock_code`：股票代码
- `percent`：持仓占比

---

## 6. 外部 API — 新浪基金（fund.sina.com.cn）

**用途**：基金基础信息
+**无需代理**

### 6.1 基金信息查询

```
GET http://fund.sina.com.cn/fundInfo/api/getFundInfo.php
```

**参数**：`fundcode={code}`

**返回**：JSON，基金基础信息和近期净值

---

## 7. 外部 API — 好买基金（howbuy.com）

**用途**：基金持仓（可转债持仓）
**无需代理**

### 7.1 基金持仓查询

```
GET https://www.howbuy.com/fund/FundDetailNewAPI/FundPortfolioNew
```

**返回**：JSON，包含可转债持仓明细

---

## 8. 外部 API — 雅虎财经（Yahoo Finance）

**用途**：美股行情
**需要代理**

### 8.1 股票行情

```
GET https://query1.finance.yahoo.com/v8/finance/chart/{symbol}
```

**参数**：
| 参数 | 说明 | 示例 |
|------|------|------|
| `symbol` | 股票代码 | `QQQ` |
| `interval` | K线间隔 | `1d` |
| `range` | 时间范围 | `1mo` |

**返回**：JSON，包含价格、成交量等

---

## 9. 外部 API — 汇率

### 9.1 中国银行汇率（备用）

```
GET https://www.boc.cn/sourcedb/whjsen/
```

**返回**：HTML 页面，需解析

---

## 10. API 使用注意事项

### 代理配置

部分国外 API 需要代理，项目使用：
```
http://127.0.0.1:7890
```

### 请求头

建议添加标准请求头：
```python
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://fundf10.eastmoney.com/",
}
```

### 错误处理

- 所有 API 调用需设置超时（建议 20-30 秒）
- 网络错误应重试 2-3 次
- 部分 API 有访问频率限制，被封后需等待

### 数据校验

- API 返回的数值需校验是否为有效数字
- 汇率、价格等需检查合理范围

---

## 11. 更新日志

| 日期 | 变更内容 |
|------|----------|
| 2026-05-27 | 初始版本，整理主要API |