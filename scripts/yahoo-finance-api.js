// Yahoo Finance v8 API - 实时行情 + 历史K线
// 无需API Key，国内直连，Node.js 原生（无第三方依赖）

const https = require('https');

/**
 * 获取单只股票数据
 * @param {string} symbol - Yahoo代码，如 7203.T, HSBA.L, AAPL, CRUD.L
 * @param {string} range  - 时间范围: 1d/5d/1mo/3mo/6mo/1y/2y/5y/max
 * @param {string} interval - K线周期: 1m/5m/15m/30m/1h/1d/1wk/1mo
 * @returns {Promise<object>} 包含 meta + timestamp + OHLCV
 */
function fetchStock(symbol, range = '5d', interval = '1d') {
  return new Promise((resolve, reject) => {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?range=${range}&interval=${interval}`;
    https.get(url, { timeout: 10000, headers: { 'User-Agent': 'Mozilla/5.0' } }, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          const result = json.chart.result[0];
          const meta = result.meta;
          const ts = result.timestamp;
          const q = result.indicators.quote[0];
          resolve({
            symbol: meta.symbol,
            name: meta.shortName || meta.symbol,
            currency: meta.currency,
            exchange: meta.exchangeName,
            price: meta.regularMarketPrice,
            bars: ts.map((t, i) => ({
              date: new Date(t * 1000).toISOString().slice(0, 10),
              open: q.open[i],
              high: q.high[i],
              low: q.low[i],
              close: q.close[i],
              volume: q.volume[i],
            })),
          });
        } catch (e) {
          reject(new Error(`Parse error for ${symbol}: ${data.substring(0, 200)}`));
        }
      });
    }).on('error', reject);
  });
}

/**
 * 获取前收盘价和涨跌幅
 * @param {string} symbol
 * @returns {Promise<{price, prevClose, changePct, currency, date}>}
 */
async function getLatestWithChange(symbol) {
  const data = await fetchStock(symbol, '5d', '1d');
  const bars = data.bars;
  const latest = bars[bars.length - 1];
  const prev = bars.length >= 2 ? bars[bars.length - 2] : null;
  const changePct = prev ? ((data.price - prev.close) / prev.close * 100).toFixed(2) : null;
  return {
    symbol: data.symbol,
    name: data.name,
    currency: data.currency,
    exchange: data.exchange,
    price: data.price,
    prevClose: prev ? prev.close : null,
    changePct: changePct ? Number(changePct) : null,
    date: latest.date,
    prevDate: prev ? prev.date : null,
  };
}

/**
 * 批量获取（并发）
 * @param {string[]} symbols
 * @param {string} range
 * @param {string} interval
 * @returns {Promise<object[]>}
 */
async function fetchBatch(symbols, range = '5d', interval = '1d') {
  return Promise.all(symbols.map(s => fetchStock(s, range, interval).catch(e => ({ symbol: s, error: e.message }))));
}


// ======== 使用示例 ========

async function main() {
  // 1. 单只股票 - 实时 + 前收盘
  const tsmc = await getLatestWithChange('2330.TW');
  console.log('台积电:', tsmc);

  // 2. 单只股票 - 2年周线
  const sap = await fetchStock('SAP.DE', '2y', '1wk');
  console.log('SAP 2y weekly bars:', sap.bars.length, 'first:', sap.bars[0].date, 'last:', sap.bars[sap.bars.length - 1].date);

  // 3. 批量查询
  const symbols = ['NVDA', 'AAPL', 'MSFT', 'CRUD.L', 'BRNT.L', '0700.HK', '7203.T', '2330.TW'];
  const results = await fetchBatch(symbols);
  results.forEach(r => {
    if (r.error) { console.log(r.symbol + ': ERROR -', r.error); return; }
    console.log(`${r.symbol} (${r.exchange}) = ${r.price} ${r.currency}`);
  });
}

main().catch(console.error);
