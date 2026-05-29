# Yahoo Finance 代理 - Cloudflare Worker 部署指南

## 为什么需要

服务器 IP (43.139.35.190) 被 Yahoo 封禁（429），本地没被封。
通过 Cloudflare Worker 中转，免费 10万次/天，够用。

## 部署步骤（5分钟）

### 1. 注册 Cloudflare（如果没有）
https://dash.cloudflare.com/sign-up （免费）

### 2. 安装 Wrangler CLI
npm install -g wrangler

### 3. 登录
wrangler login

### 4. 创建项目
mkdir yahoo-proxy && cd yahoo-proxy
wrangler init yahoo-proxy-worker --type javascript

### 5. 替换 worker 代码
把 scripts/yahoo-proxy-worker.js 的内容复制到 src/index.js

### 6. 部署
wrangler deploy

### 7. 记下 Worker URL
部署后会显示类似：https://yahoo-proxy-worker.your-subdomain.workers.dev

## 服务器使用

把代码里的：
  https://query1.finance.yahoo.com/v8/finance/chart/...

改成：
  https://your-worker-url.workers.dev/v8/finance/chart/...

其他不变，路径和参数完全兼容。

## 验证

在服务器上运行：
curl -s 'https://your-worker-url.workers.dev/v8/finance/chart/NVDA?range=1d&interval=1d' | head -c 200

返回 JSON 就是成功了。

## 限制

- 免费额度：10万次/天，1000次/分钟
- 如果超了可以再注册一个 Cloudflare 账号
- Worker 代码只有 10 行，无依赖