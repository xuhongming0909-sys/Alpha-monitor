# Yahoo Finance API 代理方案

## 背景

服务器 IP (43.139.35.190) 被 Yahoo Finance 封禁（429），所有 query1.finance.yahoo.com 请求均返回 429。本地（Windows）未被封禁。

## 解决方案

通过 Deno Deploy 免费代理中转：服务器 -> Deno Deploy -> Yahoo Finance

代理地址：https://careful-mallard-62.xuhongming0909-sys.deno.net

## 使用方式

路径和参数与 Yahoo 完全一致，只换域名：

原来（服务器429）：https://query1.finance.yahoo.com/v8/finance/chart/{代码}?range={范围}&interval={周期}
改成（服务器200）：https://careful-mallard-62.xuhongming0909-sys.deno.net/v8/finance/chart/{代码}?range={范围}&interval={周期}

## 代理代码（已部署在 Deno Deploy）

```typescript
Deno.serve(async (req) => {
  const url = new URL(req.url);
  const target = "https://query1.finance.yahoo.com" + url.pathname + url.search;
  const resp = await fetch(target, {
    headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" },
  });
  return new Response(resp.body, {
    status: resp.status,
    headers: { "Access-Control-Allow-Origin": "*", "Content-Type": "application/json" },
  });
});
```

## 服务器实测（全部HTTP 200）

原油ETF：CRUD.L, BRNT.L, USO, BNO, OILK, XLE
全球股票：AAPL, MSFT, 0700.HK, 7203.T, SAP.DE, AIR.PA, HSBA.L

## 服务器上其他可用API

| API | 覆盖 | 状态 |
|-----|------|------|
| Deno代理->Yahoo | 全球所有市场 | OK |
| qt.gtimg (us/hk前缀) | 美股/港股即时 | OK |
| eastmoney push2 | 美股/港股即时 | OK |
| stooq (.us/.de后缀) | 美股/德国CSV | OK |
| Yahoo直连 | 全部 | 429封禁 |
| Cloudflare Workers | - | workers.dev被墙 |
| Vercel | - | vercel.app 443超时 |

## Deno Deploy 免费额度

100,000次请求/天，100GiB带宽/月，无需绑卡

## 注意事项

- 服务器上所有Yahoo请求必须走Deno代理，不要直连
- 代理无额外延迟（Deno边缘节点）
- yahoo-finance-api.md 中的API文档仍然有效，只需替换域名
