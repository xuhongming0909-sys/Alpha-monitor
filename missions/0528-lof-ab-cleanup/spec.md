# Mission Spec
Type: refactor
Goal: 清除LOF A/B类分类残留，统一IOPV计算
Scope: strategy/lof_iopv/, data_fetch/lof_iopv/, data_fetch/lof_db/, config/
Constraints: 不改业务逻辑，只统一入口和清除死代码
Impact: 回测、实时IOPV、数据更新