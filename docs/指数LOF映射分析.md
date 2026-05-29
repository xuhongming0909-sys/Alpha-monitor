# 指数LOF映射分析

生成时间: 2026-05-29

说明: 16只指数型LOF基金的业绩基准拆解、对应ETF标的、数据获取能力、匹配度分析。

## 汇总表

| 代码 | 名称 | 业绩基准(原文) | 基准构成 | 指数仓位 | 映射标的 | 标的比例 | 历史数据 | 实时数据 | 匹配度 |
|------|------|---------------|----------|----------|----------|----------|----------|----------|--------|
| 161128 | 标普信息科技LOF | 标普500信息科技指数×95%+活期×5% | S&P 500 Information Technology ×95% | 95% | XLK | 100% | ✅ (5383天) | ✅ | 完全匹配 |
| 161130 | 纳指LOF | 纳斯达克100指数×95%+活期×5% | Nasdaq 100 ×95% | 95% | QQQ | 100% | ✅ (4795天) | ✅ | 完全匹配 |
| 161125 | 标普500LOF | 标普500指数×95%+活期×5% | S&P 500 ×95% | 95% | SPY | 100% | ✅ (6387天) | ✅ | 完全匹配 |
| 161126 | 标普医疗保健LOF | 标普500医疗保健等权重指数×95%+活期×5% | S&P 500 Equal Weight Health Care ×95% | 95% | XLV | 100% | ✅ (5383天) | ✅ | 近似(权重方式不同) |
| 161127 | 标普生物科技LOF | 标普生物科技精选行业指数×95%+活期×5% | S&P Biotechnology Select Industry ×95% | 95% | XBI | 100% | ✅ (5108天) | ✅ | 完全匹配 |
| 162415 | 美国消费LOF | 标普美国品质消费股票指数×95%+活期×5% | S&P Consumer Discretionary ×95% | 95% | XLY | 100% | ✅ (5383天) | ✅ | 完全匹配 |
| 164906 | 中概互联网LOF | 中证海外中国互联网指数×95%+活期×5% | 中证海外中国互联网指数 ×95% | 95% | KWEB | 100% | ✅ (2147天) | ✅ | 完全匹配 |
| 160416 | 石油基金LOF | 标普全球石油净总收益指数 | S&P Global Oil Net Total Return ×100% | 100% | IXC | 100% | ✅ (5383天) | ✅ | 近似(IXC为S&P Global Energy) |
| 162719 | 石油LOF | 道琼斯美国石油开发与生产指数×95%+活期×5% | Dow Jones US Oil & Gas E&P ×95% | 95% | IEO | 100% | ✅ (5045天) | ✅ | 完全匹配(IEO追踪道琼斯版) |
| 162411 | 华宝油气LOF | 标普石油天然气上游股票指数(全收益) | S&P Oil & Gas E&P Select Industry ×100% | 100% | XOP | 100% | ✅ (5013天) | ✅ | 完全匹配 |
| 160719 | 嘉实黄金LOF | 伦敦金价格(经汇率调整) | 伦敦金PM Fix ×100% | 100% | GLD | 100% | ✅ (5413天) | ✅ | 完全匹配 |
| 164824 | 印度基金LOF | 中信证券印度ETP指数×90%+活期×10% | 中信证券印度ETP(底层MSCI India) ×90% | 90% | INDA | 100% | ✅ (3597天) | ✅ | 近似(INDA追踪MSCI India) |
| 160723 | 嘉实原油LOF | 100% WTI原油价格收益率 | WTI Crude Oil ×100% | 100% | USO | 100% | ✅ (5064天) | ✅ | 完全匹配 |
| 161129 | 原油LOF | S&P GSCI Crude Oil Index ER收益率 | S&P GSCI Crude Oil ER ×100% | 100% | USO | 100% | ✅ (5064天) | ✅ | 近似(USO追踪WTI，GSCI底层也是WTI) |
| 501018 | 南方原油LOF | 60%WTI+40%BRENT | WTI×60% + Brent×40% | 100% | USO+BNO | 60%+40% | ✅ 均有 | ✅ | 完全匹配 |
| 160140 | 美国REIT精选LOF | 道琼斯美国精选REIT指数×95%+活期×5% | Dow Jones US Select REIT ×95% | 95% | IYR | 100% | ✅ (5383天) | ✅ | 近似(IYR追踪道琼斯美国房地产，非精选版) |

## 逐基金详细分析

---

### 161128 标普信息科技LOF

- **基金类型**: QDII-股票，指数型
- **业绩基准原文**: 标普500信息科技指数收益率（使用估值汇率折算）×95%+活期存款利率（税后）×5%
- **基准指数**: S&P 500 Information Technology Index
- **基准仓位**: 指数95% + 现金5%
- **映射标的**: XLK (Technology Select Sector SPDR Fund)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ akshare stock_us_daily，5383天
- **实时数据**: ✅ 腾讯qt.gtimg.cn
- **匹配度分析**:
  - XLK追踪的是S&P 500中的科技板块(Technology Select Sector)，成分股与S&P 500 Information Technology Index高度重合
  - 两者都是市值加权，权重分配方式一致
  - 差异: XLV包含少量可选消费中的科技股(如特斯拉被归入可选消费而非科技)
  - **结论: 匹配度极高，回测误差可控**

---

### 161130 纳指LOF

- **基金类型**: QDII-股票，指数型
- **业绩基准原文**: 纳斯达克100指数收益率（使用估值汇率折算）×95%+活期存款利率（税后）×5%
- **基准指数**: Nasdaq 100 Index
- **基准仓位**: 指数95% + 现金5%
- **映射标的**: QQQ (Invesco QQQ Trust)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 4795天
- **实时数据**: ✅
- **匹配度分析**:
  - QQQ就是直接追踪Nasdaq 100的ETF，一一对应
  - 该基金本身也是QQQ的联接基金(LOF)
  - **结论: 完全匹配**

---

### 161125 标普500LOF

- **基金类型**: QDII-股票，指数型
- **业绩基准原文**: 标普500指数收益率（使用估值汇率折算）×95%+活期存款利率（税后）×5%
- **基准指数**: S&P 500 Index
- **基准仓位**: 指数95% + 现金5%
- **映射标的**: SPY (SPDR S&P 500 ETF Trust)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 6387天
- **实时数据**: ✅
- **匹配度分析**:
  - SPY就是追踪S&P 500的ETF，一一对应
  - 全球最大的ETF，流动性极好
  - **结论: 完全匹配**

---

### 161126 标普医疗保健LOF

- **基金类型**: QDII-股票，指数型
- **业绩基准原文**: 标普500医疗保健等权重指数收益率（使用估值汇率折算）×95%+活期存款利率（税后）×5%
- **基准指数**: S&P 500 Equal Weight Health Care Index
- **基准仓位**: 指数95% + 现金5%
- **映射标的**: XLV (Health Care Select Sector SPDR)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 5383天
- **实时数据**: ✅
- **匹配度分析**:
  - **核心差异**: 基准是"等权重"(Equal Weight)，XLV是"市值加权"(Market Cap Weighted)
  - 成分股一致，但权重分配不同: XLV中强生(JNJ)、联合健康(UNH)等大公司占比高，等权重版则每只股票权重相同
  - 实际影响: 等权重版中小型医疗股波动更大，XLV相对更稳
  - 没有追踪S&P 500 Equal Weight Health Care的ETF在国内数据源中可用
  - **结论: 近似匹配，存在系统性偏差——XLV的波动会比基准小**

---

### 161127 标普生物科技LOF

- **基金类型**: QDII-股票，指数型
- **业绩基准原文**: 标普生物科技精选行业指数收益率（使用估值汇率折算）×95%+活期存款利率（税后）×5%
- **基准指数**: S&P Biotechnology Select Industry Index
- **基准仓位**: 指数95% + 现金5%
- **映射标的**: XBI (SPDR S&P Biotech ETF)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 5108天
- **实时数据**: ✅
- **匹配度分析**:
  - XBI直接追踪S&P Biotechnology Select Industry Index
  - 注意: XBI本身是等权重ETF，与基准的等权重方式一致
  - **结论: 完全匹配**

---

### 162415 美国消费LOF

- **基金类型**: QDII-股票，指数型
- **业绩基准原文**: 经人民币汇率调整的标普美国品质消费股票指数收益率×95%+人民币活期存款利率（税后）×5%
- **基准指数**: S&P Consumer Discretionary Select Sector Index
- **基准仓位**: 指数95% + 现金5%
- **映射标的**: XLY (Consumer Discretionary Select Sector SPDR)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 5383天
- **实时数据**: ✅
- **匹配度分析**:
  - XLY追踪的就是S&P 500可选消费板块，与基准一致
  - **结论: 完全匹配**

---

### 164906 中概互联网LOF

- **基金类型**: QDII-股票，指数型
- **业绩基准原文**: 中证海外中国互联网指数收益率×95%＋银行活期存款利率（税后）×5%
- **基准指数**: 中证海外中国互联网指数
- **基准仓位**: 指数95% + 现金5%
- **映射标的**: KWEB (KraneShares CSI China Internet ETF)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 2147天(约8年)
- **实时数据**: ✅
- **匹配度分析**:
  - KWEB追踪的就是CSI China Internet Index，即中证海外中国互联网指数
  - 该指数覆盖美股和港股上市的中国互联网公司
  - **结论: 完全匹配**
- **重要说明**: 之前我们用B类(港股持仓)来回测，但该基金投资目标是"紧密跟踪标的指数"，应改用A类方式(KWEB)

---

### 160416 石油基金LOF

- **基金类型**: QDII-股票，指数型
- **业绩基准原文**: 标普全球石油净总收益指数收益率(S&P Global Oil Index Net Total Return)
- **基准指数**: S&P Global Oil Index (Net Total Return)
- **基准仓位**: 100%
- **映射标的**: IXC (iShares Global Energy ETF)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 5383天
- **实时数据**: ✅
- **匹配度分析**:
  - IXC追踪的是S&P Global Energy Index，与S&P Global Oil Index不是同一指数
  - Global Energy覆盖更广(包含天然气、煤炭等)，Global Oil仅限石油
  - 更好的选择: 目前没有直接追踪S&P Global Oil的ETF在国内可用
  - 该基金之前的hardcoded持仓为空，无法回测
  - **结论: 近似匹配，IXC会多出天然气等非石油成分**

---

### 162719 石油LOF

- **基金类型**: QDII-股票，指数型
- **业绩基准原文**: 95%×人民币计价的道琼斯美国石油开发与生产指数收益率+5%×人民币活期存款收益率（税后）
- **基准指数**: Dow Jones U.S. Oil & Gas Exploration & Production Index
- **基准仓位**: 指数95% + 现金5%
- **映射标的**: IEO (iShares U.S. Oil & Gas Exploration & Production ETF)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 5045天
- **实时数据**: ✅
- **匹配度分析**:
  - IEO追踪的是Dow Jones U.S. Select Oil Exploration & Production Index
  - 这正是道琼斯版的石油天然气上游指数，与基准中的道琼斯美国石油开发与生产指数同源
  - 之前我们用XOP(S&P版)来映射，IEO(道琼斯版)更精确
  - **结论: 完全匹配(优于XOP)**

---

### 162411 华宝油气LOF

- **基金类型**: QDII-股票，指数型
- **业绩基准原文**: 标普石油天然气上游股票指数（全收益指数）
- **基准指数**: S&P Oil & Gas Exploration & Production Select Industry Index (Full Return)
- **基准仓位**: 100%
- **映射标的**: XOP (SPDR S&P Oil & Gas Exploration & Production ETF)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 5013天
- **实时数据**: ✅
- **匹配度分析**:
  - XOP就是追踪这个S&P Oil & Gas E&P指数的ETF
  - 完全对应
  - **结论: 完全匹配**

---

### 160719 嘉实黄金LOF

- **基金类型**: QDII-商品，指数型
- **业绩基准原文**: （经汇率调整后的）伦敦金价格（使用伦敦金每日下午收盘价 London Gold Price PM Fix）
- **基准指数**: 伦敦金PM Fix价格
- **基准仓位**: 100%
- **映射标的**: GLD (SPDR Gold Shares)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 5413天
- **实时数据**: ✅
- **匹配度分析**:
  - GLD追踪的就是伦敦金价格，持仓为实物黄金
  - GLD净值与伦敦金价格走势高度一致
  - **结论: 完全匹配**

---

### 164824 印度基金LOF

- **基金类型**: QDII-股票，FOF型
- **业绩基准原文**: 中信证券印度ETP指数收益率×90%+人民币活期存款收益率（税后）×10%
- **基准指数**: 中信证券印度ETP指数（底层实际为MSCI India相关标的）
- **基准仓位**: 指数90% + 现金10%
- **映射标的**: INDA (iShares MSCI India ETF)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 3597天(约14年)
- **实时数据**: ✅
- **匹配度分析**:
  - 中信证券印度ETP指数底层追踪的是MSCI India指数
  - INDA追踪的也是MSCI India指数
  - 该基金实际持仓就是INDA等印度ETF
  - 差异: 基准是中信证券编制的ETP指数，INDA是直接追踪MSCI India，中间可能有跟踪误差
  - **结论: 近似匹配，实际效果应该很好(因为该基金就持仓INDA)**

---

### 160723 嘉实原油LOF

- **基金类型**: QDII-商品，指数型
- **业绩基准原文**: 100%WTI原油价格收益率
- **基准指数**: WTI Crude Oil Price
- **基准仓位**: 100%
- **映射标的**: USO (United States Oil Fund)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 5064天
- **实时数据**: ✅
- **匹配度分析**:
  - USO追踪WTI原油期货价格，与基准WTI原油价格直接对应
  - 注意: USO持有期货合约而非现货，存在展期损耗(roll yield)，长期来看USO可能略跑输WTI现货
  - **结论: 完全匹配(注意期货展期损耗)**

---

### 161129 原油LOF

- **基金类型**: QDII-商品，指数型
- **业绩基准原文**: 标普高盛原油商品指数（S&P GSCI Crude Oil Index ER）收益率
- **基准指数**: S&P GSCI Crude Oil Index (Excess Return)
- **基准仓位**: 100%
- **映射标的**: USO (United States Oil Fund)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ 5064天
- **实时数据**: ✅
- **匹配度分析**:
  - S&P GSCI Crude Oil Index底层也是WTI原油期货，与USO的底层一致
  - 但GSCI指数的期货合约选择和展期策略与USO不完全相同
  - GSCI是更广泛的大宗商品指数中的原油部分
  - **结论: 近似匹配，底层都是WTI期货，策略细节有差异**

---

### 501018 南方原油LOF

- **基金类型**: QDII-商品，指数型
- **业绩基准原文**: 60%×WTI原油价格收益率+40%×BRENT原油价格收益率
- **基准指数**: 60% WTI + 40% Brent
- **基准仓位**: 100%
- **映射标的**: USO + BNO
- **标的比例**: USO 60% + BNO 40%
- **历史数据**: ✅ USO 5064天，BNO 4021天
- **实时数据**: ✅
- **匹配度分析**:
  - USO追踪WTI原油期货，BNO追踪Brent原油期货
  - 按基准的60:40比例配比，完全对应
  - 这也是我们hardcoded中的持仓数据
  - **结论: 完全匹配**

---

### 160140 美国REIT精选LOF

- **基金类型**: QDII-房地产信托，指数型
- **业绩基准原文**: 道琼斯美国精选REIT指数收益率×95%+银行人民币活期存款利率（税后）×5%
- **基准指数**: Dow Jones U.S. Select REIT Index
- **基准仓位**: 指数95% + 现金5%
- **映射标的**: VNQ (Vanguard Real Estate ETF)
- **备选标的**: IYR (iShares U.S. Real Estate ETF)
- **标的比例**: 100%（单标的）
- **历史数据**: ✅ VNQ 5383天，IYR 5383天
- **实时数据**: ✅
- **匹配度分析**:
  - VNQ追踪MSCI US Investable Market Real Estate 25/50 Index
  - IYR追踪Dow Jones U.S. Real Estate Index（与基准同属道琼斯系列）
  - 基准是"Dow Jones Select REIT"(精选REIT)，IYR是"Dow Jones Real Estate"(广义房地产)
  - IYR比基准更广(包含房地产服务公司等)，VNQ也是
  - 更好的选择: 暂无直接追踪Dow Jones Select REIT的ETF在国内数据源中可用
  - **结论: 近似匹配，IYR与基准同属道琼斯系列，略优于VNQ**

---

## 标的数据获取能力汇总

### 历史日线数据 (akshare stock_us_daily)

所有19个标的均可通过akshare获取历史日线数据:

| 标的 | 可用天数 | 起始约 | 数据源 |
|------|---------|--------|--------|
| XLK | 5383天 | ~2005 | akshare stock_us_daily |
| QQQ | 4795天 | ~2007 | akshare stock_us_daily |
| SPY | 6387天 | ~2000 | akshare stock_us_daily |
| XLV | 5383天 | ~2005 | akshare stock_us_daily |
| XBI | 5108天 | ~2006 | akshare stock_us_daily |
| XLY | 5383天 | ~2005 | akshare stock_us_daily |
| KWEB | 2147天 | ~2018 | akshare stock_us_daily |
| IXC | 5383天 | ~2005 | akshare stock_us_daily |
| IEO | 5045天 | ~2006 | akshare stock_us_daily |
| XOP | 5013天 | ~2006 | akshare stock_us_daily |
| GLD | 5413天 | ~2005 | akshare stock_us_daily |
| INDA | 3597天 | ~2012 | akshare stock_us_daily |
| USO | 5064天 | ~2006 | akshare stock_us_daily |
| BNO | 4021天 | ~2010 | akshare stock_us_daily |
| VNQ | 5383天 | ~2005 | akshare stock_us_daily |
| IYR | 5383天 | ~2005 | akshare stock_us_daily |
| OILK | 2427天 | ~2017 | akshare stock_us_daily |
| DBO | 4878天 | ~2007 | akshare stock_us_daily |
| GSG | 4993天 | ~2007 | akshare stock_us_daily |

### 实时数据 (腾讯qt.gtimg.cn)

所有美股ETF均可通过腾讯qt.gtimg.cn获取实时行情，格式为 `us{ticker}` (如 usXLK, usQQQ)。

## 推荐映射优化建议

相比现有holdings_hardcoded.py，以下调整可提升回测精度:

| 代码 | 当前映射 | 优化建议 | 理由 |
|------|---------|---------|------|
| 162719 石油LOF | XOP | **IEO** | 基准是道琼斯版，IEO追踪道琼斯版，XOP追踪S&P版 |
| 160140 美国REIT | VNQ | **IYR** | 基准是道琼斯版，IYR追踪道琼斯版，VNQ追踪MSCI版 |
| 164906 中概互联网 | 港股持仓(B类) | **KWEB**(A类) | 投资目标是"紧密跟踪标的指数"，应归为A类 |
