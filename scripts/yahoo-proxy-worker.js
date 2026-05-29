// Cloudflare Worker - Yahoo Finance Proxy
// 部署到 Cloudflare Workers（免费10万次/天）
// 然后服务器用 https://your-worker.workers.dev 替代 query1.finance.yahoo.com

export default {
  async fetch(request) {
    const url = new URL(request.url);
    
    // 路径映射: /v8/finance/chart/xxx -> Yahoo Finance
    const target = 'https://query1.finance.yahoo.com' + url.pathname + url.search;
    
    const resp = await fetch(target, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      },
    });
    
    // 复制响应，加 CORS 头
    const newResp = new Response(resp.body, resp);
    newResp.headers.set('Access-Control-Allow-Origin', '*');
    return newResp;
  },
};