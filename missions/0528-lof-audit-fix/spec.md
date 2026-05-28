# LOF全链路审查修复

## 目标
修复LOF模块4个HIGH bug、7个MEDIUM问题、6个LOW文档不对齐

## 范围
- data_fetch/lof_db/ (schema, updater, nav, etf, fx, holdings)
- data_fetch/lof_iopv/ (source, fetcher, normalizer)
- strategy/lof_iopv/ (calc, service, classifier)
- notification/lof_iopv/ (service.js)
- specs/ (lof-arbitrage.md, lof-db-maintenance.md, lof-holdings.md)

## 约束
- 文档修改以实际代码为准
- 不改变业务逻辑，只修bug和对齐
