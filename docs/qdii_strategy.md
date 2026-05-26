# QDII LOF 估值策略分类与方案

## 一、基金分类

### A类：指数型LOF（跟踪明确指数）
| 代码 | 名称 | 跟踪指数 | 指数代码 | 数据源 |
|------|------|---------|---------|--------|
| 161130 | 纳指100LOF | 纳斯达克100指数 | ^NDX | yfinance |
| 161125 | 标普500LOF | 标普500指数 | ^GSPC | yfinance |
| 161128 | 标普信息科技LOF | 标普500信息科技指数 | ^SP500-45 | yfinance |
| 161126 | 标普医疗保健LOF | 标普500医疗保健等权重指数 | RSPH(ETF替代) | yfinance |
| 164906 | 中概互联网LOF | 中证海外中国互联网指数 | H11136 | AKShare |
| 501225 | 全球芯片LOF | 费城半导体指数 | ^SOX | yfinance |
| 160140 | 美国REIT精选LOF | 道琼斯美国精选REIT | VNQ(ETF替代) | yfinance |
| 164824 | 印度基金LOF | MSCI India | INDA(ETF替代) | yfinance |
| 501300 | 美元债LOF | 彭博巴克莱美国综合债 | AGG(ETF替代) | yfinance |

估值公式：NAV_est = NAV_t2 × (1 + index_change × pos_ratio + fx_change)
pos_ratio从20日回归动态计算

### B类：主动管理型LOF（前十大持仓加权）
| 代码 | 名称 | 业绩基准 | 投资范围 |
|------|------|---------|---------|
| 160125 | 南方香港LOF | 恒指×95% | 仅港股 |
| 160644 | 港美互联网LOF | 中概互联网×95% | 港股+美股 |

估值公式：NAV_est = NAV_t2 × (1 + Σ(top10_weight_i × stock_return_i) / total_top10_weight × pos_ratio)

### C类：FOF型LOF（持仓ETF/指数加权）
| 代码 | 名称 | 业绩基准 | 持仓结构 |
|------|------|---------|---------|
| 501312 | 海外科技LOF | 纳指100×80%+恒生科技×10%+债×10% | ARK系列45.68%+其他ETF |

估值公式：NAV_est = NAV_t2 × (1 + Σ(etf_weight_i × etf_return_i) / total_etf_weight × pos_ratio)

## 二、估值优先级

A类指数型：指数数据 > 对应ETF > 前十大持仓兜底
B类主动管理：前十大持仓 > 业绩基准指数 > 同类ETF兜底
C类FOF型：持仓ETF加权 > 业绩基准组合 > 单一指数兜底

## 三、待验证

回测近20日，验证每个基金的估值误差是否<0.5%
