# 插件边界规则

本文件定义插件化架构的强制边界规则。

## 总原则

- 每个业务插件必须拥有自己的目录。
- 插件目录之间严禁互相直接引用代码。
- 抓取插件与策略插件之间只允许通过 `The Bus` 交互。
- `notification/` 改动推送样式时，不应要求联动修改其他职责目录。

## 允许的依赖方向

- `data_fetch/<plugin>` 可以依赖：
  - `shared/*`
  - `shared/bus/*`
  - 自己插件目录内的文件
- `strategy/<plugin>` 可以依赖：
  - `shared/*`
  - `shared/bus/*`
  - 自己插件目录内的文件
- `ui/*` 可以依赖：
  - `strategy/*`
  - `shared/*`
  - `notification/*` 的稳定接口结果，但不能反向驱动推送样式实现
- `notification/*` 可以依赖：
  - `strategy/*` 产出的统一结果
  - `ui/view_models/*` 的稳定展示模型
  - `shared/*`

## 明确禁止

- `data_fetch/ah_premium` 直接引用 `data_fetch/merger`、`data_fetch/dividend` 等兄弟插件
- `strategy/convertible_bond` 直接引用 `strategy/ah_premium` 等兄弟插件
- `strategy/*` 直接解析网页、直接请求上游接口、直接读抓取原始响应文件
- `notification/*` 直接发起抓取、直接计算套利阈值、直接修改策略输出结构

## 当前执行要求

- 所有新改动都必须直接落在正式职责目录中，不允许回写历史壳层。
- 任一插件完成收口后，后续修改必须继续留在该插件目录内完成。

## 边界检查命令
- `python tools/check_plugin_boundaries.py`
- `npm run check:boundaries`


