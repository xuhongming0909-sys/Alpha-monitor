const fs = require('fs');
const base = 'C:\\Users\\93724\\Desktop\\Alpha monitor\\';
const aR = JSON.parse(fs.readFileSync(base + 'runtime_data\\backtest\\a_results.json', 'utf-8'));
const bR = JSON.parse(fs.readFileSync(base + 'runtime_data\\backtest\\b_results.json', 'utf-8'));

// Fund master list (from config.yaml, hardcoded here for report generation)
const FUNDS = [
  {code:"161128",name:"标普信息科技LOF",currency:"USD",estimation:"A",etf:"XLK"},
  {code:"501225",name:"全球芯片LOF",currency:"USD",estimation:"A",etf:"SMH"},
  {code:"161130",name:"纳指LOF",currency:"USD",estimation:"A",etf:"QQQ"},
  {code:"161125",name:"标普500LOF",currency:"USD",estimation:"A",etf:"SPY"},
  {code:"161126",name:"标普医疗保健LOF",currency:"USD",estimation:"A",etf:"XLV"},
  {code:"161127",name:"标普生物科技LOF",currency:"USD",estimation:"A",etf:"XBI"},
  {code:"162415",name:"美国消费LOF",currency:"USD",estimation:"A",etf:"XLY"},
  {code:"160140",name:"美国REIT精选LOF",currency:"USD",estimation:"A",etf:"VNQ"},
  {code:"501300",name:"美元债LOF",currency:"USD",estimation:"A",etf:"AGG"},
  {code:"164824",name:"印度基金LOF",currency:"USD",estimation:"A",etf:"INDA"},
  {code:"160416",name:"石油基金LOF",currency:"USD",estimation:"A",etf:"XLE"},
  {code:"162719",name:"石油LOF",currency:"USD",estimation:"A",etf:"XOP"},
  {code:"162411",name:"华宝油气LOF",currency:"USD",estimation:"A",etf:"XOP"},
  {code:"160723",name:"嘉实原油LOF",currency:"USD",estimation:"A",etf:"USO"},
  {code:"161129",name:"原油LOF",currency:"USD",estimation:"A",etf:"USO"},
  {code:"501018",name:"南方原油LOF",currency:"USD",estimation:"A",etf:"USO"},
  {code:"163208",name:"全球油气能源LOF",currency:"USD",estimation:"A",etf:"XLE"},
  {code:"160216",name:"国泰商品LOF",currency:"USD",estimation:"A",etf:"GSG"},
  {code:"161815",name:"抗通胀LOF",currency:"USD",estimation:"A",etf:"GLD"},
  {code:"165513",name:"中信保诚商品LOF",currency:"USD",estimation:"A",etf:"GSG"},
  {code:"160719",name:"嘉实黄金LOF",currency:"USD",estimation:"A",etf:"GLD"},
  {code:"164701",name:"黄金LOF",currency:"USD",estimation:"A",etf:"GLD"},
  {code:"161116",name:"黄金主题LOF",currency:"USD",estimation:"A",etf:"GLD"},
  {code:"160125",name:"南方香港LOF",currency:"HKD",estimation:"B"},
  {code:"160644",name:"港美互联网LOF",currency:"HKD",estimation:"B"},
  {code:"164906",name:"中概互联网LOF",currency:"USD",estimation:"B"},
  {code:"501312",name:"海外科技LOF",currency:"USD",estimation:"B"},
];

function grade(r2, mae) {
  if (r2 >= 0.95 && mae <= 0.3) return 'A';
  if (r2 >= 0.90) return 'B';
  if (r2 >= 0.80) return 'C';
  if (r2 >= 0.60) return 'D';
  return 'F';
}

function gradeLabel(g) {
  return {A:'✅ 可信',B:'⚠️ 可用',C:'⚠️ 偏差大',D:'❌ 不可信',F:'❌ 失效'}[g] || '—';
}

// A类报告
let aRows = [];
for (const f of FUNDS.filter(f=>f.estimation==='A')) {
  const r = aR[f.code] || null;
  const g = r ? grade(r.r2, r.mae) : '—';
  aRows.push({
    code: f.code, name: f.name, etf: f.etf,
    r2: r ? r.r2.toFixed(4) : '—',
    mae: r ? r.mae.toFixed(4) : '—',
    maxErr: r ? r.maxErr.toFixed(4) : '—',
    sample: r ? r.samplePeriod : '—',
    grade: g, label: gradeLabel(g),
  });
}

// B类报告
let bRows = [];
for (const f of FUNDS.filter(f=>f.estimation==='B')) {
  const r = bR[f.code] || null;
  const g = r ? grade(r.r2, r.mae) : '—';
  bRows.push({
    code: f.code, name: f.name,
    r2: r ? r.r2.toFixed(4) : '—',
    mae: r ? r.mae.toFixed(4) : '—',
    maxErr: r ? r.maxErr.toFixed(4) : '—',
    sample: r ? r.samplePeriod : '—',
    grade: g, label: gradeLabel(g),
  });
}

// Stats
const aGrades = aRows.map(r=>r.grade).filter(g=>g!=='—');
const stats = {
  a: { total: aRows.length, ok: aGrades.filter(g=>g==='A'||g==='B').length, warn: aGrades.filter(g=>g==='C').length, bad: aGrades.filter(g=>g==='D'||g==='F').length, noData: aRows.length - aGrades.length },
  b: { total: bRows.length, ok: bRows.map(r=>r.grade).filter(g=>g==='A'||g==='B').length, noData: bRows.filter(r=>r.grade==='—').length },
};

// Markdown
let md = `# LOF IOPV 回测报告

**生成时间**: 2026-05-27
**数据来源**: a_results.json + b_results.json（样本区间 2026-03-03~2026-05-22）
**回测方法**: 基金净值日收益率 vs 估值因子日收益率

---

## 回测策略说明

### A类：指数跟踪法

- **IOPV公式**: \`IOPV = NAV × (1 + etf_ret) × fx_ratio\`
- **回测验证**: 基金净值日收益率 vs ETF日收益率
- **含义**: R² 越高，ETF涨幅对该基金NAV变化的解释力越强，IOPV估值越可信

### B类：T10持仓加权法

- **IOPV公式**: \`IOPV = NAV × (1 + stock_ratio/100 × Σ(wᵢ × retᵢ)) × fx_ratio\`
- **回测验证**: 基金净值日收益率 vs 前十大持仓加权日收益率
- **含义**: R² 越高，持仓组合对该基金NAV变化的解释力越强

### 评级标准

| 等级 | R² | MAE | 含义 |
|------|-----|------|------|
| A | ≥ 0.95 | ≤ 0.3% | ✅ 可信，估值偏差极小 |
| B | ≥ 0.90 | — | ⚠️ 可用，估值偏差可接受 |
| C | ≥ 0.80 | — | ⚠️ 偏差大，需注意 |
| D | ≥ 0.60 | — | ❌ 不可信，映射关系弱 |
| F | < 0.60 | — | ❌ 失效，不应使用该映射 |

---

## 汇总

| | A类（指数跟踪） | B类（T10持仓） |
|---|---|---|
| 总数 | ${stats.a.total} | ${stats.b.total} |
| A/B级（可信/可用） | ${stats.a.ok} | ${stats.a.ok} |
| C级（偏差大） | ${stats.a.warn} | — |
| D/F级（不可信/失效） | ${stats.a.bad} | — |
| 无数据 | ${stats.a.noData} | ${stats.b.noData} |

---

## A类明细（23只，按R²降序）

| # | 代码 | 名称 | ETF | R² | MAE(%) | MAX误差(%) | 样本区间 | 等级 |
|---|---|---|---|---|---|---|---|---|
`;

aRows.sort((a,b) => (parseFloat(b.r2)||-999) - (parseFloat(a.r2)||-999));
aRows.forEach((r,i) => {
  md += `| ${i+1} | ${r.code} | ${r.name} | ${r.etf} | ${r.r2} | ${r.mae} | ${r.maxErr} | ${r.sample} | ${r.grade} ${r.label} |\n`;
});

md += `
### A类问题分析

**可信基金 (A/B级)**: ${aRows.filter(r=>r.grade==='A'||r.grade==='B').map(r=>r.code+'('+r.etf+')').join(', ')}

**商品/原油类 (D/F级)**: ${aRows.filter(r=>r.grade==='D'||r.grade==='F').map(r=>r.code+'('+r.name+'→'+r.etf+')').join(', ')}

> 商品/原油类基金跟踪商品期货而非股票ETF，单一ETF无法解释期货展期+管理费+跟踪误差的叠加效果。这些基金的IOPV估值不可信，建议：
> 1. 标记为"低置信度"
> 2. 寻找期货价格数据替代ETF
> 3. 或直接使用天天基金gsz估值（如果有）

`;

md += `---

## B类明细（4只）

| # | 代码 | 名称 | R² | MAE(%) | MAX误差(%) | 样本区间 | 等级 |
|---|---|---|---|---|---|---|---|
`;

bRows.forEach((r,i) => {
  md += `| ${i+1} | ${r.code} | ${r.name} | ${r.r2} | ${r.mae} | ${r.maxErr} | ${r.sample || '—'} | ${r.grade} ${r.label} |\n`;
});

md += `
---

## 建议操作

### 立即可用（高置信度）
R² ≥ 0.90 的基金，IOPV估值可作为交易参考。

### 需优化映射
- **161126 标普医疗保健 → XLV** (R²=0.72): XLV不能完全代表该基金持仓，需确认是否持有非XLV成分股
- **160416 石油基金 → XLE** (R²=0.86): XLE是能源股ETF，石油基金可能跟踪油价指数
- **501300 美元债 → AGG** (R²=0.46): 美元债与AGG(全美债)相关性弱，需找更匹配的债券指数

### 不应使用当前映射
- **160723/161129/501018 原油类 → USO** (R²<0.4): USO期货ETF有严重展期损耗
- **160216 国泰商品 → GSG** (R²=-0.67): GSG与该基金几乎无关
- **161815 抗通胀 → GLD** (R²=-1.15): 抗通胀基金跟踪TIPS而非黄金
- **165513 中信保诚商品 → GSG** (R²=-3.02): 完全失效

`;

fs.writeFileSync(base + '001回测.md', md, 'utf-8');
console.log('Report written, length=' + md.length);
