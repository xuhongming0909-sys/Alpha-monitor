# Alpha Monitor 规格说明

## 1. 文档规则
- `REQUIREMENTS.md` 是 PM 视角的需求合同。
- 本文件是页面结构、接口绑定、表格交互和业务逻辑字典的实现合同。
- 本轮固定遵守：先改文档，再改代码，最后做一致性核对。

## 2. 页面与接口合同

### 2.1 固定接口
页面层继续只消费现有接口：
- `汇率`：`/api/market/exchange-rate`
- `十年期国债收益率`：`/api/market/convertible-bond-arbitrage`
- `新股打新`：`/api/market/ipo`
- `可转债打新`：`/api/market/convertible-bonds`
- `转债套利`：`/api/market/convertible-bond-arbitrage`
- `AH溢价`：`/api/market/ah`
- `AB溢价`：`/api/market/ab`
- `监控套利`：`/api/monitors`
- `分红提醒`：`/api/dividend?action=refresh`
- `收购私有`：`/api/market/merger`
- `展示配置`：`GET /api/dashboard/ui-config`
- `推送设置`：`GET /api/push/config`、`POST /api/push/config`

### 2.2 首页结构合同
首页严格采用以下顺序：
1. 标题区：只保留 `Alpha Monitor` 标题。
2. 顶部状态行：一行显示 `HKD/CNY`、`USD/CNY`、十年期国债收益率、更新时间。
3. 顶部功能区：
   - 仅保留 `股债打新` 今日事项长表。
4. 主导航 tab：
   - `转债套利`
   - `AH溢价`
   - `AB溢价`
   - `LOF套利`
   - `监控套利`
   - `分红提醒`
   - `事件套利`
5. 主功能面板：根据当前 tab 展示对应真实数据。
6. 页面末尾：渲染简洁版 `推送设置` 编辑区。

首页不允许再出现：
- `市场动态`
- `今日概况`
- `重点机会摘要`
- 标题下方长说明
- 按资产类型拆开的双列打新卡片
- 推送设置中的长段解释文案

### 2.3 顶部状态行合同
状态行必须展示：
- `HKD/CNY`
- `USD/CNY`
- `十年期国债收益率`
- 最新更新时间

规则：
- 不显示十年期国债日期。
- `treasuryYield10y` 缺失时，文案必须显示 `十年期国债收益率 暂未返回`。
- 状态行是单行文本信息带，不再渲染为独立大面板。

### 2.4 股债打新长表合同
顶部打新区必须改成“仅今日事项”的横向长表。

固定规则：
- 只收敛今天相关的条目：
  - `subscribeDate = today`
  - `paymentDate = today`
  - `listingDate = today`
- 表头至少展示：
  - `当前阶段`
  - `类型`
  - `名称/代码`
  - `申购日`
  - `中签缴款日`
  - `上市日`
  - `申购上限`
  - `发行价/转股价`
- 页面不再单独展示 `抽签日` 列。
- 页面展示的 `中签缴款日` 列本轮固定读取 `lotteryDate`。
- `今日中签缴款` 阶段判断也固定读取 `lotteryDate`，与展示口径保持一致。
- 同一张表内混排新股和转债。
- `当前阶段` 使用分色标签区分：
  - `今日申购`
  - `今日中签缴款`
  - `今日上市`
- 无数据时，表内明确显示 `今日无数据`。

### 2.5 推送设置合同
- 面板标题固定为 `推送设置`。
- 只保留 3 个时间框：
  - 时间框 1：常规模块主推送
  - 时间框 2：常规模块主推送
  - 时间框 3：收购私有专报推送
- 页面必须支持读取当前配置并保存修改结果。
- 推送设置固定放在整页 tab 面板之后的页面末尾，不再占用顶部右侧区域。
- 布局为无大边框的简洁条带，只保留状态文字、时间框、保存按钮和刷新按钮。
- 每次读取成功后，3 个时间框都必须以最新接口返回值刷新，不能仅在输入框为空时填充。
- 保存成功后，页面必须直接使用 `POST /api/push/config` 返回结果回写状态文案和 3 个时间框。

## 3. 通用表格系统合同

### 3.1 生效范围
本轮统一升级以下 3 张主表：
- `转债套利`
- `AH溢价`
- `AB溢价`

### 3.2 状态模型
每张表至少维护以下前端状态：
- 当前排序字段
- 当前排序方向
- 当前页码
- 每页条数

默认值：
- 每页条数固定为 `50`
- `转债套利` 初始保持接口原始顺序
- `AH溢价 / AB溢价` 初始按 `溢价率` 降序
- `监控套利` 初始按“最优收益率”降序
- `分红提醒` 初始按“股息率”降序
- `收购私有` 初始按“公告时间”倒序

### 3.3 表头排序规则
- 只有声明为可排序的表头才响应点击。
- 首次点击某字段时，使用该字段默认排序方向。
- 再次点击同一字段时，在升序 / 降序之间切换。
- 切换到其他字段时，重置为该字段默认方向。
- 当前排序字段必须有明确激活态和方向提示。

### 3.4 分页规则
- 每页固定 `50` 条。
- 分页控件至少包含：
  - 首页
  - 上一页
  - 当前页 / 总页数
  - 下一页
  - 末页
  - 总条数
- 序号列必须按“当前排序结果 + 当前分页位置”连续计算，不允许直接使用原始数组下标。

### 3.5 响应式规则
- 电脑端：页面主体使用接近满屏布局，长表允许自由横向和纵向滚动。
- 手机端：不拆第二套页面，保留同一套表格语义，通过单列堆叠和横向滚动保证可用。
- 长表区域必须保留清晰的表头、滚动边界和分页控件。
- 全局基础字号、tab、按钮、输入框、表头和表格正文必须统一上调，保证桌面端长时间阅读不吃力。

## 4. 功能页合同

### 4.1 转债套利
转债套利页面结构固定为：
1. 标题与更新时间
2. 紧凑摘要区
3. 主表
4. 分页区

不再保留旧版大指标条带，也不允许三张高占用摘要卡把首屏大量挤掉。

摘要区合同：
- 保留 3 组摘要：
  - `双低靠前`
  - `理论溢价率靠前`
  - `转股套利候选`
- 摘要布局参考 `AH / AB` 的分栏秩序，但密度更高，条目数更少。
- 桌面端优先使用紧凑多栏布局，移动端回落为单列堆叠。
- 每组摘要默认最多显示 `3` 条，避免纵向空间失控。

主表固定字段顺序为：
- `序号`
- `转债代码`
- `转债名称`
- `正股代码`
- `正股名称`
- `转债现价`
- `转债涨跌幅`
- `正股现价`
- `正股涨跌幅`
- `转股价`
- `转股价值`
- `转股溢价率`
- `双低`
- `理论溢价率`
- `评级`
- `剩余年限`
- `剩余规模(亿)`
- `成交额(亿)`
- `到期税前收益率`
- `上市日`
- `转股起始日`

可排序字段至少包括：
- `转债现价`
- `转股价值`
- `转股溢价率`
- `双低`
- `理论溢价率`
- `剩余年限`
- `剩余规模(亿)`
- `成交额(亿)`
- `到期税前收益率`
- `上市日`
- `转股起始日`

### 4.2 AH / AB 共用骨架
AH 和 AB 页面必须使用完全相同的布局和样式，只允许通过字段映射区分：
- AH：
  - `对手代码 = hCode`
  - `对手名称 = hName`
  - `对手市场价 = hPrice`
  - `对手人民币价 = hPriceCny`
- AB：
  - `对手代码 = bCode`
  - `对手名称 = bName`
  - `对手市场价 = bPrice`
  - `对手人民币价 = bPriceCny`

页面结构固定为：
1. 标题与更新时间
2. 双摘要区
3. 主表
4. 样本说明区
5. 分页区

### 4.3 AH / AB 摘要合同
- 顶部必须保留两块摘要：
  - 左侧：前三
  - 右侧：倒数前三
- 当主排序字段为 `premium` 时：
  - 摘要标题显示 `溢价率前三` / `溢价率倒数前三`
- 当主排序字段为 `percentile` 时：
  - 摘要标题显示 `近三年百分位前三` / `近三年百分位倒数前三`
- 摘要排序跟随当前主排序字段，不再额外维护第二套摘要排序状态。

### 4.4 AH / AB 主表合同
主表固定字段顺序为：
- `序号`
- `A股代码`
- `A股名称`
- `H股代码 / B股代码`
- `H股名称 / B股名称`
- `A股价`
- `H股价 / B股价`
- `对手人民币价`
- `价差`
- `溢价率`
- `近三年百分位`
- `样本区间`

规则：
- `价差 = 对手人民币价 - A股价`
- `近三年百分位` 是对 `percentile` 的简化显示名称
- 主表不单独显示 `historyCount`
- `样本区间` 必须压缩为 `YYMMDD-YYMMDD`

可排序字段至少包括：
- `A股价`
- `对手人民币价`
- `价差`
- `溢价率`
- `近三年百分位`

### 4.5 监控套利
监控套利页面结构固定为：
1. 标题与更新时间
2. 新增 / 编辑表单区
3. 实时监控主表
4. 分页区

主表必须展示：
- 监控名称
- 收购方名称与股价
- 目标方名称与股价
- 换股比例
- 安全系数
- 理论对价计算说明
- 股票腿理论对价
- 股票腿价差
- 股票腿收益率
- 现金腿对价
- 现金腿价差
- 现金腿收益率

规则：
- 顶部表单使用同一个保存入口同时支持新增与编辑。
- 编辑已有项目时，`POST /api/monitors` 必须携带现有 `id` 并覆盖该条监控参数。
- 主表使用共享分页表格渲染路径，不允许继续使用不可分页的单独简表实现。
- 补充参数区固定直接显示在每个主行下方，不再保留单独的 `详情` 控制列。
- 补充文案必须使用真实业务名词，例如 `理论对价计算说明`，不得使用不准确的自造标签。
- 默认按“最优收益率”降序。
- 每页固定 `50` 条。

### 4.6 分红提醒
分红提醒页面结构固定为：
1. 今日登记日提醒
2. 完整观察表
3. 分页区

不再保留顶部统计卡。

规则：
- 完整观察表默认按 `股息率` 降序。
- 每页固定 `50` 条。

### 4.7 收购私有
收购私有页面结构固定为：
1. 标题与更新时间
2. 主表
3. 分页区

规则：
- 页面显示全量公告，不再只取当天。
- 主表默认按公告时间倒序。
- 当 `announcementDate` 或 `announcementTime` 属于当天时，该行必须高亮。
- 高亮行必须带 `今日公告` 角标或标签。
- 每页固定 `50` 条。

主表优先展示以下字段中的可用项：
- `announcementTime`
- `secCode`
- `secName`
- `dealType`
- `searchKeyword`
- `title`
- `latestPrice`
- `offerPrice`
- `premiumRate`
- `announcementUrl`
- `pdfUrl`

## 5. 视觉与交互合同

### 5.1 视觉方向
- 主色：黑、深红、金属灰
- 气质：科技感 + 艺术感
- 重点：规整、层次清楚、长表易读、桌面端利用率高

### 5.2 交互规则
所有模块必须保留：
- 加载中
- 暂无数据
- 加载失败

所有 tab、可排序表头、分页按钮、保存按钮必须提供：
- hover 态
- active 态
- disabled 态

## 6. 业务逻辑与计算字典
本章是页面展示逻辑的唯一计算口径来源。代码逻辑如需修改，必须先改本章。

### 6.1 AH溢价
- 公式：`AH 溢价 = (H 股人民币价 / A 股价 - 1) * 100`
- 其中：`H 股人民币价 = H 股价格 * 港币兑人民币汇率`

### 6.2 AB溢价
- 公式：`AB 溢价 = (B 股人民币价 / A 股价 - 1) * 100`
- 其中：`B 股人民币价 = B 股价格 * 对应汇率`

### 6.3 价差
- AH / AB 页面中的 `价差 = 对手人民币价 - A股价`

### 6.4 转股价值
- 公式：`转股价值 = 正股价格 * 100 / 转股价`

### 6.5 转债溢价率
- 公式：`转债溢价率 = (转债现价 / 转股价值 - 1) * 100`
- 若上游已返回 `premiumRate`，页面优先展示上游值。

### 6.6 双低值
- 公式：`双低值 = 转债现价 + 转债溢价率`

### 6.7 转股套利空间
- 公式：`转股套利空间 = (转股价值 - 转债现价) / 转债现价 * 100`
- 当前规则：只有 `转股套利空间 > 2%` 才进入候选机会集合。

### 6.8 监控套利股票腿理论对价
- 公式：`股票腿理论对价 = 收购方股价 * 换股比例 * 安全系数 + 现金分派`

### 6.9 监控套利股票腿收益率
- 公式：`股票腿收益率 = (股票腿理论对价 - 目标现价) / 目标现价 * 100`

### 6.10 监控套利现金腿收益率
- 公式：`现金腿收益率 = (现金对价 - 目标现价) / 目标现价 * 100`

### 6.11 股息率
- 公式：`股息率 = 每股分红 / 当前股价 * 100`

### 6.12 股债打新今日事件
- `申购日 = 今天` 归入 `今日申购`
- `lotteryDate = 今天` 归入 `今日中签缴款`
- `上市日 = 今天` 归入 `今日上市`

### 6.13 股债打新展示日期映射
- 顶部长表使用统一口径：
  - `中签缴款日` 列固定显示 `lotteryDate`
  - `今日中签缴款` 阶段也固定按 `lotteryDate`
  - `抽签日` 不再单独显示

## 7. 验收与一致性核对

### 7.1 页面验收
以下条件必须同时满足：
1. 打开 `http://127.0.0.1:5000/` 后能看到真实数据。
2. 顶部状态信息为一行文字，不再是大块状态盒。
3. `股债打新` 是“仅今日事项”的横向长表，并显示关键日期与申购上限等字段。
4. `推送设置` 位于页面末尾，只有 3 个时间框，且能保存并立即回显。
5. 7 个主 tab 可以切换。
6. `转债套利 / AH / AB` 主表均新增序号列。
7. `转债套利 / AH / AB` 主表均支持点击表头排序。
8. `转债套利 / AH / AB` 主表均支持分页，每页 50 条。
9. `监控套利 / 分红提醒 / 收购私有` 主表均支持分页，每页 50 条。
10. `监控套利` 支持新增和编辑已有监控，且补充参数固定显示在每个项目下方。
11. AH / AB 同时显示前三和倒数前三。
12. `收购私有` 显示全量公告，今日公告高亮明显。
13. `转债套利` 摘要区明显更紧凑，主表更早进入视野。
14. 电脑端接近满屏显示，整体字号明显提升，手机端布局不压坏。
15. 首页保持 7 个根 tab，且包含 `LOF套利`。
16. `LOF套利` 作为首页根模块可直接打开并渲染真实 QDII 数据。
17. `GET /api/market/lof-arbitrage` 可返回可解析的 LOF 数据。
18. `GET /api/market/historical-premium` 仅接受 `type=AH|AB`。

### 7.2 一致性核对
每次修改后都要做一次 `/speckit.analyze` 等价核对，至少报告：
- `AH` 代码中的计算逻辑是否与本文件第 `6.1` 条一致
- `AB` 代码中的计算逻辑是否与本文件第 `6.2` 条一致

本轮默认结论应为：
- AH：一致
- AB：一致

原因：
- 本轮不修改公式，只修改页面展示、排序、分页、字段组织和响应式布局。

## 8. 云服务器公网访问合同

### 8.1 部署目标
- 当前项目除了本地调试外，必须支持部署到云服务器并长期对外提供访问。
- 正式访问目标从“本机或局域网可打开”升级为“任意公网用户拿到网址即可访问”。
- 本轮起，云服务器部署视为正式运行环境，不再把“Windows 本机稳定启动”视为最终交付形态。

### 8.2 对外访问入口
- 正式对外入口优先采用：
  - `HTTPS + 域名 + 443`
  - 次选为 `HTTP + 80`
- `http://公网IP:5000/` 只允许作为临时调试或证书未完成前的过渡入口。
- 页面正式对外地址与 `/api/health` 必须经过同一套反向代理入口暴露，不允许首页走域名而健康检查只能本机访问。

### 8.3 服务器运行链路
- 正式链路固定为：
  - `Node 应用服务`
  - `服务守护层（systemd 或等价机制）`
  - `Nginx / Caddy 等反向代理`
  - `公网访问入口`
- 服务守护层必须满足：
  - 开机自动启动
  - 异常退出自动拉起
  - 日志可追踪
- 反向代理必须负责：
  - 将公网 `80/443` 请求转发到应用实际监听端口
  - 保留首页和 `/api/*` 路由可用
  - 在启用 HTTPS 时管理证书绑定

### 8.4 云网络与安全规则
- 必须同时检查并打通以下层级：
  - 云厂商安全组
  - 系统防火墙
  - 反向代理监听端口
  - 应用实际监听地址与端口
- 任何一层未放通，都视为“公网访问合同未完成”。
- 应用监听地址继续以 `config.yaml > app.host` 和 `config.yaml > app.port` 为唯一配置来源。

### 8.5 健康检查合同
- `/api/health` 继续作为唯一正式健康检查入口。
- 对外健康检查结果必须至少包含：
  - `web`
  - `data_jobs`
  - `push_scheduler`
- 公网验收时，首页是否可访问以 `web = ok` 为第一判断标准。
- `data_jobs` 或 `push_scheduler` 出现 `warn` 时，不应直接导致首页不可访问。

### 8.6 运维操作合同
- 正式运行环境必须有固定启动、停止、检查方式。
- 本地/Windows 辅助脚本可以保留，但云服务器正式环境必须补齐 Linux 侧正式运行方案。
- 后续计划文件和任务文件必须覆盖至少以下事项：
  - Ubuntu 服务器部署步骤
  - 反向代理配置
  - 服务守护配置
  - 公网端口与安全组核对
  - HTTPS 或过渡公网访问说明

### 8.7 公网部署验收
以下条件必须同时满足，才算完成“公网长期可访问”：
1. 在外部网络环境下，通过正式网址能打开首页。
2. 服务器重启后，无需手工进入终端执行命令，网页可自动恢复。
3. 手动杀掉网页主进程后，守护机制能自动拉起服务。
4. 正式网址下的 `/api/health` 可访问，且 `web` 状态为 `ok`。
5. 若已配置域名，则浏览器访问优先使用 HTTPS；若暂未配置域名，必须在文档中明确公网 IP 访问只是临时过渡方案。

### 8.8 GitHub 自动部署合同

#### 8.8.1 固定链路
GitHub 自动部署正式链路固定为：

1. GitHub `main` 分支收到 push
2. GitHub Actions 工作流触发
3. Runner 通过 SSH 登录服务器
4. 服务器执行统一更新脚本
5. 更新脚本完成代码同步、依赖同步、服务重启、健康检查

#### 8.8.2 仓库文件合同
仓库必须提供以下正式文件：

- `.github/workflows/deploy.yml`
- `tools/deploy/update_from_github.sh`

职责约束：

- `deploy.yml` 只负责触发远程部署，不内嵌大量服务器业务逻辑
- `deploy.yml` 仅允许执行以下职责：校验 Secrets、准备 SSH、触发远程脚本、输出阶段日志
- `deploy.yml` 禁止直接执行 `git fetch/reset`、`npm ci/install`、`systemctl restart` 等服务器业务步骤
- `update_from_github.sh` 作为服务器统一更新入口，供 GitHub Actions 和人工排障共用
- 工作流中的服务器业务输出应由该脚本统一产生，便于定位“脚本外失败”与“脚本内失败”

#### 8.8.3 服务器更新脚本合同
`tools/deploy/update_from_github.sh` 至少必须执行以下步骤：

1. 定位项目根目录
2. 执行 `git fetch --all`
3. 执行 `git reset --hard origin/main`
4. 若存在 `package-lock.json`，执行 `npm ci`；否则执行 `npm install`
5. 检查 `alpha-monitor` 或配置指定服务名是否存在
6. 若服务存在，则执行重启并输出状态
7. 对本地 `http://127.0.0.1:app.port/api/health` 做健康检查

约束：

- 服务未安装时，脚本必须给出明确警告
- 健康检查失败时，脚本必须返回非零退出码
- 脚本不得修改业务公式、页面合同和数据库口径

#### 8.8.4 GitHub Secrets 合同
工作流默认使用以下 Secrets：

- `SERVER_HOST`
- `SERVER_USER`
- `SERVER_PORT`
- `SERVER_SSH_KEY`

可选覆盖项：

- `SERVER_APP_DIR`
- `SERVER_SERVICE_NAME`

默认值：

- `SERVER_APP_DIR = /home/ubuntu/Alpha monitor`
- `SERVER_SERVICE_NAME = alpha-monitor`

#### 8.8.5 行为边界
- 自动部署只收口“代码更新与服务重启”，不替代首次服务器初始化
- 首次初始化仍由现有 Linux 部署脚本负责，例如：
  - `tools/deploy/install_systemd.sh`
  - `tools/deploy/install_nginx_site.sh`
- 自动部署不新增新的对外 API
- 自动部署不更改业务计算逻辑

#### 8.8.6 自动部署验收
以下条件必须同时满足：

1. 向 `main` 推送提交后，GitHub Actions 自动触发
2. 工作流能通过 SSH 进入目标服务器并执行更新脚本
3. 工作流 YAML 不重复实现服务器业务逻辑（如 git 同步、依赖安装、服务重启）
4. 更新脚本完成代码同步与依赖同步
5. 若服务已安装，则服务自动重启
6. `/api/health` 在部署后返回可用结果，且 `web = ok`


#### 8.8.7 Deploy Drift Guardrails (2026-03-22)

`tools/deploy/update_from_github.sh` must enforce:
1. `config.yaml` syntax validation before dependency install and service restart.
2. Resolve runtime app port from config, then release stale process owners on that port before restart.
3. Keep systemd unit refresh as the canonical service startup path.
4. After `/api/health` passes, run homepage marker verification on `http://127.0.0.1:${app.port}/`:
   - required marker: `dashboard_page.js`
   - forbidden legacy markers: `app.js|message-form`
5. Marker check failure must terminate deploy with non-zero exit code.
6. Health check must run with retry attempts and delay window to tolerate post-restart warm-up.

## 9. Compact List Rendering Spec (2026-03-22)

### 9.1 Rendering mode
- Desktop-first list rendering mode is fixed to:
  - key columns only in the default row
  - inline detail row expansion for non-key fields
  - strong pagination with default `pageSize = 50`
- Module-internal max-height scroll containers must be removed from primary list rendering.

### 9.2 Expansion interaction
- Each row provides a deterministic expand/collapse action.
- Expanded details render in-place directly below the row and must not navigate away.
- Expansion state is table-scoped and does not alter sorting or pagination behavior.

### 9.3 Error presentation
- Long backend traceback text must not be rendered directly in list panels.
- UI displays a concise error summary with actionable hint text.

## 10. Push API and Scheduler Spec (2026-03-22)

### 10.1 API parsing behavior
- Frontend API client must parse response from raw text and then JSON decode.
- On decode failure, client error message must include endpoint + HTTP status + short body preview.

### 10.2 Route fallback behavior
- Server must return JSON 404 for unmatched `/api/*` routes.
- Non-API paths continue to use dashboard HTML fallback.

### 10.3 Save consistency behavior
- Push save flow is:
  1. POST config
  2. apply POST response in-memory
  3. immediately GET config for calibration
  4. re-render inputs and state text from latest GET payload

### 10.4 Scheduler calendar behavior
- `notification.scheduler.calendar_mode` is introduced.
- Supported values:
  - `daily`
  - `workdays`
  - `trading_days`
- This round default is `daily`.

## 11. Deploy Python Readiness Spec (2026-03-22)
- Deploy script must resolve an available Python executable with fallback candidates.
- Deploy script must install `requirements.txt` dependencies before service restart.
- Deploy script must verify import readiness for `akshare`, `pandas`, `requests`.
- Import verification failure is fatal and must terminate deploy with non-zero exit code.

## 12. Fresh Quote Revalidation Spec (2026-03-23)

### 12.1 Frontend request modes
- Dashboard API client must support two request modes for market datasets:
  - normal mode: existing endpoint path
  - force mode: same endpoint with `force=1`
- Manual `刷新` uses force mode for:
  - `/api/market/exchange-rate`
  - `/api/market/convertible-bond-arbitrage`
  - `/api/market/ah`
  - `/api/market/ab`
  - `/api/market/ipo`
  - `/api/market/convertible-bonds`
  - `/api/market/merger`

### 12.2 First-load cache revalidation
- If the initial dashboard response for `exchangeRate / cbArb / ah / ab` carries `servedFromCache = true`, frontend must trigger one background force revalidation for that dataset in the same session.
- Background revalidation must:
  - keep the current cached value visible until the fresh payload returns
  - replace the module state with the fresh payload after success
  - surface concise status text while revalidation is in progress

### 12.3 User-visible freshness text
- Push strip status is unrelated to market freshness.
- Market freshness copy must come from dataset response metadata:
  - `servedFromCache = true` => show cached/revalidating wording
  - no cache marker after force success => show real-time wording

## 13. Dense Core Table Rendering Spec (2026-03-23)

### 13.1 Convertible bond main table
- `转债套利` must render without a visible `详情` header column.
- Default-row columns are fixed to:
  - `序号`
  - `转债`
  - `正股`
  - `转债现价 / 转债涨跌幅`
  - `正股现价 / 正股涨跌幅`
  - `转股价 / 转股价值`
  - `转股溢价率`
  - `双低`
  - `60日波动率`
  - `纯债价值 / 理论价格`
  - `理论溢价率`
  - `到期税前收益率`
- Composite cells may use two-line rendering inside one column, but the values above must be visible without row expansion.
- Optional remaining low-priority fields may stay in inline detail rows only if they are no longer needed for the primary reading path.

### 13.2 AH / AB main tables
- `AH` and `AB` must share one rendering skeleton and differ only by field mapping.
- Default-row columns are fixed to:
  - `序号`
  - `A股`
  - `H股 / B股`
  - `A股价`
  - `对手市场价`
  - `对手人民币价`
  - `价差`
  - `溢价率`
  - `近三年分位`
  - `样本信息`
- `样本信息` uses a compact two-line cell:
  - line 1: `样本数`
  - line 2: compressed range `YYMMDD-YYMMDD`
- `AH / AB` default rendering must not require the old detail-label column.

### 13.3 Table renderer behavior
- Shared table renderer must support hiding the explicit detail header/button column when the module contract does not need it.
- If a module still uses inline details, the header cell for that control must be blank rather than showing `详情`.

## 14. Push Delivery Truthfulness Spec (2026-03-23)

### 14.1 Runtime state fields
- Push runtime state must separately retain:
  - `lastMainPushAttemptAt`
  - `lastMainPushSuccessAt`
  - `lastMainPushError`
  - `lastMergerPushAttemptAt`
  - `lastMergerPushSuccessAt`
  - `lastMergerPushError`

### 14.2 Scheduler success semantics
- Main push scheduler flow:
  1. record attempt time
  2. try downstream send
  3. on success:
     - clear latest error
     - set success time
     - record the schedule slot as sent
  4. on failure:
     - update latest error
     - do not record the slot as sent
- Merger report scheduler follows the same rule set.

### 14.3 Push config API payload
- `GET /api/push/config` response must include delivery-health metadata in addition to editable schedule fields:
  - `webhookConfigured`
  - `schedulerEnabled`
  - `calendarMode`
  - `selectedModules`
  - `lastMainPushAttemptAt`
  - `lastMainPushSuccessAt`
  - `lastMainPushError`
  - `lastMergerPushAttemptAt`
  - `lastMergerPushSuccessAt`
  - `lastMergerPushError`

### 14.4 Push strip rendering
- Dashboard push strip must render a concise status summary derived from the API payload.
- If `webhookConfigured = false`, UI must explicitly warn that push cannot be delivered.
- If latest runtime error exists, UI must surface the short reason instead of only showing historical dates.

## 15. Premium History Incremental Sync Tolerance Spec (2026-03-23)

### 15.1 Scope
- This rule applies only to `tools/rebuild_premium_db.py --mode update`.
- It does not relax failure behavior for `--mode rebuild`.

### 15.2 Update-mode tolerance
- During update mode, the script may downgrade a per-symbol upstream historical-price fetch failure from `failed` to `warning` when all of the following hold:
  - the failure is limited to a single symbol
  - the error originates from the upstream provider fetch step
  - the script can continue processing the rest of the batch
- Warning entries must still include:
  - `type`
  - `code`
  - `error`

### 15.3 Success semantics
- Update mode final payload may still return `success = true` when warning-only entries exist.
- Final payload must distinguish:
  - `failedCount`
  - `warningCount`
  - `failed`
  - `warnings`
- `failedCount > 0` remains fatal.
- `warningCount > 0` is informational and must not by itself fail the batch.

### 15.4 Non-tolerated failures
- The following remain fatal even in update mode:
  - config / import / environment failures
  - SQLite write failures
  - FX history failures
  - batch-wide provider failures that prevent useful progress
  - any failure path outside the per-symbol upstream price-fetch anomaly classification
## 16. Cloud Runtime Preservation And Proxy Install Spec (2026-03-23)

### 16.1 Runtime-state boundary
- `runtime_data/shared/*.json` is runtime state, not release-source truth.
- Repository sync may update code and static assets, but must not replace the server's current runtime JSON content with repository copies.

### 16.2 Deploy-script preservation behavior
- `tools/deploy/update_from_github.sh` must preserve tracked runtime JSON files before `git reset --hard` and restore them immediately after code sync completes.
- Preservation scope must cover at least:
  - monitor list
  - dividend portfolio
  - push config
  - push runtime state
  - merger company reports
  - market cache snapshots
  - market refresh state

### 16.3 Managed service template
- `tools/deploy/alpha-monitor.service` must declare:
  - project-root working directory
  - optional `.env` loading through `EnvironmentFile`
  - pre-start runtime directory creation
  - automatic restart on failure

### 16.4 Reverse-proxy install scripts
- Repo must provide one-command installer scripts for both bundled proxy options:
  - `tools/deploy/install_nginx_site.sh`
  - `tools/deploy/install_caddy_site.sh`
- Both scripts must template the public host and upstream app port, validate config, and reload the managed proxy service.

## 17. Convertible Bond Daily Delist Filter Spec (2026-03-23)

### 17.1 Scope
- This rule applies to the outward-facing row list used by:
  - `/api/market/convertible-bond-arbitrage`
  - dashboard `转债套利` panel
- The existing Python fetch layer may continue computing `isDelistedOrExpired`, but the final visible list must be re-checked again in Node strategy/service shaping.

### 17.2 Daily date source
- “Today” is fixed to the Shanghai calendar date.
- Node-side date comparison must use `shared/time/shanghai_time.js` so cloud/runtime timezone drift does not change the business result.

### 17.3 Exclusion decision
- Each row must be excluded from the final list when any of the following hold after date normalization:
  - `delistDate <= today`
  - `ceaseDate <= today`
  - `maturityDate < today`
- `delistDate` / `ceaseDate` are inclusive same-day cutoffs.
- `maturityDate` remains exclusive for same-day removal, matching the existing fetch-layer rule.

### 17.4 Cache tolerance behavior
- The Node-side sanitizer must recompute the rule on every response instead of trusting a stale cached `isDelistedOrExpired = false`.
- If a row already carries `isDelistedOrExpired = true`, it may be excluded immediately without further contradiction handling.

### 17.5 Output behavior
- Excluded rows must be removed before duplicate-row resolution and before any opportunity-set summary calculation.
- No new API field or route is required for this round; the correction is purely on visible row inclusion.
## 18. Event Arbitrage Unified Spec (2026-03-23)

### 18.1 Top-level dashboard contract
- The old dashboard tab label `鏀惰喘绉佹湁` is replaced by `浜嬩欢濂楀埄`.
- The root dashboard tab key count remains 6.
- The existing merger-related backend routes remain valid and unchanged for backward compatibility, but the main dashboard reading path switches to the new event-arbitrage aggregate payload.

### 18.2 Page structure
- `浜嬩欢濂楀埄` page structure is fixed to:
  1. module title and update time
  2. internal sub-tab strip
  3. sub-view content area
- Internal sub-tabs are fixed to:
  - `鎬昏`
  - `娓偂绉佹湁鍖?`
  - `涓鑲＄鏈夊寲`
  - `A鑲″鍒?`
  - `鍏憡姹?`
  - `娓偂渚涜偂鏉?寰呮帴鍏?`
- Default internal sub-tab is `鎬昏`.

### 18.3 API contract
- New route: `GET /api/market/event-arbitrage`
- Response shape is fixed to:
  - `success`
  - `data.overview`
  - `data.categories`
  - `data.sourceStatus`
  - `error`
  - `updateTime`
  - `cacheTime`
  - `servedFromCache`
- `data.categories` fixed keys:
  - `hk_private`
  - `cn_private`
  - `a_event`
  - `rights_issue`
  - `announcement_pool`
- `data.sourceStatus` fixed keys:
  - `hk_private`
  - `cn_private`
  - `a_event`
  - `rights_issue`
  - `announcement_pool`

### 18.4 Standardized row schema
- Every external event row must expose:
  - `id`
  - `source`
  - `category`
  - `market`
  - `symbol`
  - `name`
  - `currentPrice`
  - `changeRate`
  - `marketValue`
  - `offerPrice`
  - `spreadRate`
  - `eventType`
  - `eventStage`
  - `offeror`
  - `offerorHolding`
  - `registryPlace`
  - `dealMethod`
  - `canShort`
  - `canCounter`
  - `summary`
  - `detailUrl`
  - `officialMatch`
  - `raw`
- `officialMatch` is either `null` or:
  - `matched`
  - `announcementId`
  - `title`
  - `announcementDate`
  - `pdfUrl`
  - `reportAvailable`

### 18.5 Source and adapter rules
- Phase-1 primary source is direct public JSON fetching from Jisilu:
  - `/data/taoligu/hk_arbitrage_list/`
  - `/data/taoligu/cn_arbitrage_list/`
  - `/data/taoligu/astock_arbitrage_list/`
- `rights_issue` stays in the outward-facing model but is disabled in phase 1:
  - rows = `[]`
  - status = `disabled_no_public_source`
- Firecrawl is not part of the production hot path in this round.
- If one source fails, only that category status may degrade; the whole aggregate endpoint must still return the remaining healthy categories when possible.

### 18.6 Matching rules
- External rows may be enriched from the existing merger announcement pool.
- Phase-1 matching rule is fixed to exact code matching only:
  - Jisilu `symbol`
  - matches merger `secCode`
- No fuzzy company-name matching is allowed in this round.
- If multiple merger rows share the same code, the newest announcement row wins.

### 18.7 Sub-view rendering contract
- `鎬昏` shows:
  - per-category row counts
  - positive-spread row counts
  - latest update time
  - matched announcement count
- `娓偂绉佹湁鍖?` main table columns:
  - `浠ｇ爜`
  - `鍚嶇О`
  - `鐜颁环`
  - `娑ㄨ穼骞?`
  - `甯傚€?`
  - `绉佹湁鍖栦环鏍?`
  - `濂楀埄绌洪棿`
  - `绉佹湁鍖栬繘绋?`
  - `瑕佺害鏂?`
  - `瑕佺害鏂规寔鑲?`
  - `鍏徃娉ㄥ唽鍦?`
  - `鏀惰喘鏂瑰紡`
  - `鍙嶅`
  - `鍙崠绌?`
  - `澶囨敞`
  - `璇︽儏閾炬帴`
- `涓鑲＄鏈夊寲` main table columns:
  - `浠ｇ爜`
  - `鍚嶇О`
  - `鐜颁环`
  - `娑ㄨ穼骞?`
  - `甯傚€?`
  - `绉佹湁鍖栦环鏍?`
  - `濂楀埄绌洪棿`
  - `杩涚▼`
  - `瑕佺害鏂?`
  - `鏀惰喘鏂瑰紡`
  - `璐圭敤鎻愮ず`
  - `璇︽儏閾炬帴`
- `A鑲″鍒?` main table columns:
  - `浠ｇ爜`
  - `鍚嶇О`
  - `鐜颁环`
  - `娑ㄨ穼骞?`
  - `瀹夊叏杈归檯浠?`
  - `瀹夊叏杈归檯鎶樹环`
  - `鐜伴噾閫夋嫨鏉冧环鏍?`
  - `鐜伴噾閫夋嫨鏉冩姌浠?`
  - `甯佺`
  - `浜嬩欢绫诲瀷`
  - `鎽樿`
  - `鍏憡閾炬帴`
  - `璁哄潧閾炬帴`
- `鍏憡姹?` continues to show the existing merger-announcement table and AI-report affordances.
- `娓偂渚涜偂鏉?寰呮帴鍏?` must render a real disabled-state panel with a reason message, not an empty fake table.

### 18.8 Runtime/cache rules
- New runtime cache file may be used for normalized aggregate payload:
  - `runtime_data/shared/event_arbitrage_cache.json`
- Cache payload must not replace the existing merger cache or merger APIs.
- Cached aggregate payload may be served for fast first paint, but source-level failure text must stay visible in `sourceStatus`.

## 19. Minimal Monitor Popup Editor Spec (2026-03-23)

### 19.1 Interaction mode
- `监控套利` panel keeps the monitor list visible by default.
- The editor is closed by default and must open only when:
  - user clicks `新增监控`
  - user clicks row-level `编辑`
- Create and edit share one inline implementation rendered above the monitor list.

### 19.2 Visible form fields
- Visible fields are fixed to:
  - `收购方`
  - `目标方`
  - `换股比例`
  - `安全系数`
  - `现金对价`
  - `现金对价币种`
  - `现金选择权`
  - `现金选择权币种`
- The old direct-input fields for code / market / share-currency / note / generated name must not render as normal visible inputs in this round.

### 19.3 Search confirmation behavior
- `收购方` and `目标方` inputs must support lightweight live lookup using the existing stock-search API.
- The editor must render a visible resolved-security hint when hidden metadata is already known, including at least:
  - resolved name
  - code
  - market type
  - currency
- When the search API returns multiple candidates, the editor may render a compact candidate list for explicit user confirmation.
- Selecting a candidate updates the hidden fields immediately.

### 19.4 Hidden-field preservation
- When editing an existing monitor row, hidden fields from stored runtime data must be carried forward unless the corresponding visible entity input changes.
- At minimum, preserved hidden fields include:
  - `id`
  - `name`
  - `acquirerCode`
  - `acquirerMarket`
  - `acquirerCurrency`
  - `targetCode`
  - `targetMarket`
  - `targetCurrency`
  - `note`
- `stockRatio` is no longer hidden in this round; it must follow the visible form value.
## 20. Startup Responsiveness And Premium History Recovery Spec (2026-03-23)

### 20.1 Dashboard latency model
- Cached dataset responses remain the default first-paint path.
- Force-refresh requests are still allowed to be slower than cached reads and must not redefine the normal latency baseline.
- Diagnosis for this round treats the following separately:
  - cached endpoint latency
  - force-refresh latency
  - broken-source fallback behavior

### 20.2 Degraded premium-summary detection
- A premium-history summary must be treated as degraded when any of the following hold:
  - `sampleCount <= 1`
  - `sampleCount3Y <= 1`
  - positive sample count exists but required date boundaries are missing
  - a very small 3Y sample count is paired with a same-day or near-same-day sample range, indicating the DB only kept a recent fragment
- Degraded summary means "not safe to skip sync", even if `endDate` already matches the latest market date.

### 20.3 Full-backfill escalation rule
- `tools/rebuild_premium_db.py --mode update` must escalate degraded symbols to a full backfill path instead of the normal short incremental fetch window.
- The same escalation rule must be available to the on-demand premium-history ensure path used by APIs/tools.
- Non-degraded symbols may continue using the existing incremental logic.

### 20.4 IPO empty-history fallback
- `data_fetch/subscription/ipo_source.py` must return a successful empty payload when:
  - latest upstream fetch failed or returned nothing
  - and SQLite currently has no stored IPO rows
- Required payload shape:
  - `success: true`
  - `data: []`
  - `upcoming: []`
  - `historyCount: 0`
  - `updateTime`
- Optional fields:
  - `source`
  - `warning`
- This fallback must not throw an API-level error or produce an HTTP 500 by itself.

### 20.5 Convertible-bond outward payload shaping
- `normalizeDatasetPayload('cbArb', ...)` may apply a final outward-facing field whitelist after row sanitization succeeds.
- The whitelist must preserve the fields used by the dashboard rendering path, including at least:
  - bond identity
  - stock identity
  - bond / stock current price and change
  - convert-price metrics
  - premium / double-low / volatility / theoretical-price / yield metrics
  - any remaining date fields still needed by sanitization before shaping
- Unused per-row internal fields may be removed from the HTTP payload even if they remain present in the raw Python result.
- This shaping step must not change:
  - row count
  - row order after sanitization
  - visible dashboard calculations
- Public output keeps `data` as the only row-array contract for this round.
- The same sanitized row collection must not be emitted again as top-level `list` or `rows` aliases.

## 21. Event Arbitrage UI Simplification Spec (2026-03-23)

### 21.1 Visible navigation
- The frontend event-arbitrage sub-tab sequence is fixed to:
  - `a_event`
  - `hk_private`
  - `cn_private`
  - `rights_issue`
  - `announcement_pool`
- `overview` remains an API field only; it is not part of the visible sub-tab sequence.
- Frontend default event-arbitrage sub-tab becomes `a_event`.

### 21.2 A-share rendering rule
- `A股套利` uses the standardized `a_event` rows directly.
- Table-visible A-share fields remain limited to the scraped core fields, including:
  - code
  - name
  - current price
  - change rate
  - safety price
  - safety discount
  - choose price
  - choose discount
  - currency
  - event type
  - official announcement link
- `forumUrl` may stay in raw payload storage, but frontend must not render it in this round.

### 21.3 HK/CN rendering rule
- `港股套利` main table displays only fetched core fields and a direct raw-announcement link from the scraped source row.
- That announcement link must point to the source-side original/core announcement URL carried by the normalized row.
- `中概私有` keeps the same non-expand secondary-row presentation pattern for textual notes.

### 21.4 Summary placement
- A-share `summary` is removed from the main table columns.
- Instead, each A-share row renders a second always-visible detail row directly below the main row.
- That detail row must not depend on expand/collapse interaction.
- The rendered label is fixed to `摘要`.
- HK/CN text notes follow the same always-visible detail-row pattern, but the rendered label is fixed to `备注`.

### 21.5 Event-arbitrage detail interaction
- `事件套利` tables no longer use row-level expand buttons in this round.
- `announcement_pool` renders without detail toggles.
- `hk_private`, `cn_private`, and `a_event` keep the secondary detail-row visual style, but it is always visible and not interactive.

## 22. Same-day Subscription Truthfulness And Dense CB Core Fields Spec (2026-03-23)

### 22.1 IPO same-day retry rule
- `ipo` dataset cache may not be treated as healthy-first-choice when all of the following hold:
  - `historyCount <= 0`
  - `data = []`
  - `upcoming = []`
- In that state, later normal requests must retry the live fetch path instead of serving the cached empty payload forever.
- This rule is limited to the subscription datasets whose current-user contract is same-day event visibility.

### 22.2 Beijing IPO market recognition
- Subscription source market inference must recognize Beijing exchange IPO code prefixes:
  - `4*`
  - `8*`
  - `9*`
- This rule only fixes market classification; it must not change row identity, subscribe dates, or dedup keys.

### 22.3 Invalid convertible-bond visible-row rule
- Node-side `sanitizeCbArbRows()` must exclude a row before outward rendering when either of the following holds:
  - `price <= 0`
  - `turnoverAmountYi <= 0` and the row already has terminal delist-chain evidence such as `ceaseDate` / `delistDate` / `maturityDate` crossing an imminent end-state cutoff
- Existing `delistDate <= today`, `ceaseDate <= today`, and `maturityDate < today` rules remain in force.
- This rule is meant to remove obviously dead rows from the visible list; it is not a new opportunity-ranking formula.

### 22.4 CB outward payload whitelist expansion
- Public `cbArb` rows must preserve at least the following fields for the dense table:
  - `code`
  - `bondName`
  - `price`
  - `changePercent`
  - `stockCode`
  - `stockName`
  - `stockPrice`
  - `stockChangePercent`
  - `stockAvgRoe3Y`
  - `stockDebtRatio`
  - `convertPrice`
  - `convertValue`
  - `premiumRate`
  - `pureBondValue`
  - `bondValue`
  - `doubleLow`
  - `redeemTriggerPrice`
  - `putbackPrice`
  - `volatility60`
  - `callOptionValue`
  - `putOptionValue`
  - `theoreticalPrice`
  - `theoreticalPremiumRate`
  - `listingDate`
  - `convertStartDate`
  - `maturityDate`
  - `rating`
  - `yieldToMaturityPretax`

### 22.5 Dense CB table rendering contract
- `转债套利` default-row columns are fixed to:
  - `序号`
  - `转债`
  - `转债现价 / 涨跌`
  - `正股`
  - `正股现价 / 涨跌`
  - `3Y平均ROE`
  - `资产负债率`
  - `转股价 / 转股价值`
  - `转股溢价率`
  - `纯债价值`
  - `纯债溢价率`
  - `双低`
  - `强赎价`
  - `回售价`
  - `60日波动率`
  - `期权理论价值`
  - `理论价值`
  - `理论溢价率`
  - `上市日`
  - `转股起始日`
  - `到期日`
  - `评级`
- `纯债价值` is rendered from:
  - prefer `pureBondValue`
  - fallback to `bondValue`
- `纯债溢价率` is rendered as `(转债现价 / 纯债基准 - 1) * 100`:
  - prefer `pureBondValue`
  - fallback to `bondValue`
- `60日波动率` is currently rendered from the annualized standard deviation of recent stock close-to-close log returns:
  - source close series = cached adjusted stock closes
  - current display semantics = historical estimate / reference
- `期权理论价值` is rendered as:
  - prefer `callOptionValue - putOptionValue`
  - fallback to `theoreticalPrice - 纯债基准`
- `理论价值` is rendered from `theoreticalPrice`.
- `理论溢价率` is rendered from `theoreticalPremiumRate`.
- The page must include a visible formula hint near the `转债套利` main table, stating at least:
  - `理论价值 = 纯债价值 + 期权理论价值`
  - `期权理论价值 = 看涨期权价值 - 看跌期权价值`
- The page must also visibly mark the following fields as reference-only in this round:
  - `60日波动率`
  - `期权理论价值`
  - `理论价值`
  - `理论溢价率`
- `yieldToMaturityPretax` outward value must come from a real upstream field:
  - prefer Jisilu `bond_cb_jsl()` `到期税前收益`
  - if the source row has no real value, keep `yieldToMaturityPretax = null`
  - do not populate this field from a local approximation formula in this round
- `stockAvgRoe3Y` and `stockDebtRatio` remain real-source financial metrics:
  - the stable bulk path may use Eastmoney report-summary tables:
    - `stock_yjbb_em(date=YYYY1231)` for annual `净资产收益率`
    - `stock_zcfz_em(date=YYYYMMDD)` for latest available `资产负债率`
  - if the bulk path still misses a code, fallback fetchers may still try:
    - `ak.stock_financial_abstract_ths(symbol=code, indicator="按报告期")`
    - `ak.stock_financial_abstract(symbol=code)`

## 22. Constitution Sync Guardrail Spec (2026-03-23)

### 22.1 Scope
- This round adds only a governance guardrail and does not change business API behavior.
- Fixed files:
  - source: `CONSTITUTION.md`
  - mirror: `.specify/memory/constitution.md`
  - checker: `tools/check_constitution_sync.py`
  - command entry: `npm run check:constitution`

### 22.2 Comparison rule
- The checker reads both constitution files as UTF-8 text.
- To avoid false positives caused only by Windows/Linux line-ending differences, comparison normalizes:
  - `\r\n` -> `\n`
  - trailing final newline presence
- Other content differences are treated as real drift and must fail the check.

### 22.3 Failure behavior
- The checker exits non-zero when:
  - either constitution file is missing
  - normalized text differs
- On failure, output must clearly identify:
  - which file is missing, or
  - a short unified diff preview for the first mismatching section

### 22.4 Success behavior
- On success, the checker prints a concise confirmation that the two constitution files are synchronized.
- The checker performs no file mutation, network access, or side effects beyond stdout/stderr output and exit code.

## 23. LOF Arbitrage Zero-login Spec (2026-03-23)

### 23.1 Scope
- This round adds a new top-level dashboard module `LOF套利`.
- Phase-1 source scope is fixed to direct public JSON requests against Jisilu QDII endpoints:
  - `/data/qdii/qdii_list/E`
  - `/data/qdii/qdii_list/A`
  - `/data/qdii/qdii_list/C`
- Firecrawl is not in the hot path for this round.

### 23.2 Layering
- `data_fetch/lof_arbitrage/fetcher.py` only handles:
  - source request
  - retry / timeout
  - per-category cache fallback
  - outward raw-category snapshot
- `data_fetch/lof_arbitrage/normalizer.py` only maps source fields into bus rows.
- `strategy/lof_arbitrage/service.py` only handles:
  - premium-basis selection
  - fee adjustment
  - action-status classification
  - overview aggregation
- `presentation` only handles:
  - route registration
  - dataset refresh
  - dashboard rendering

### 23.3 API contract
- New route: `GET /api/market/lof-arbitrage`
- Response shape is fixed to:
  - `success`
  - `data.overview`
  - `data.rows`
  - `data.groups`
  - `data.sourceStatus`
  - `data.iopvSearch`
  - `error`
  - `updateTime`
  - `cacheTime`
  - `servedFromCache`

### 23.4 Source groups
- `data.groups` fixed keys:
  - `europe_us`
  - `asia`
  - `commodity`
- `data.sourceStatus` fixed keys mirror the same 3 groups.
- Any single-group source failure must only degrade that group and may not blank the whole LOF page or homepage.

### 23.5 Standardized row schema
- Each outward LOF row must expose at least:
  - `id`
  - `source`
  - `category`
  - `market`
  - `symbol`
  - `name`
  - `issuer`
  - `currentPrice`
  - `changeRate`
  - `volumeWan`
  - `navValue`
  - `navDate`
  - `navPremiumRate`
  - `iopv`
  - `iopvTime`
  - `iopvPremiumRate`
  - `estimatedValue`
  - `estimatedTime`
  - `estimatedPremiumRate`
  - `premiumBasis`
  - `premiumRate`
  - `confidence`
  - `estimatedCostRate`
  - `netPremiumRate`
  - `applyStatus`
  - `applyOpen`
  - `applyFeeRate`
  - `redeemStatus`
  - `redeemFeeRate`
  - `managementFeeRate`
  - `currency`
  - `t0`
  - `actionStatus`
  - `actionRank`
  - `riskFlags`
  - `detailUrl`
  - `raw`

### 23.6 Premium-basis rule
- Phase-1 signal basis priority is fixed to:
  1. `iopvPremiumRate`
  2. `estimatedPremiumRate`
  3. `navPremiumRate`
- The outward row field `premiumBasis` must be one of:
  - `iopv`
  - `estimate`
  - `nav`
- The outward row field `confidence` must be one of:
  - `high`
  - `medium`
  - `low`

### 23.7 Action-status rule
- `actionStatus = 不可参与` when current apply status is paused/closed.
- `actionStatus = 无明显溢价` when outward signal premium is missing or non-positive.
- `actionStatus = 仅观察` when:
  - only NAV premium is available and phase-1 rule forbids treating NAV-only rows as execution-grade
  - or apply is limited and the current strategy config keeps limited-apply rows as watch-only
- `actionStatus = 套利候选` only when all of the following hold:
  - signal premium exists
  - signal premium >= `strategy.lof_arbitrage.premium_threshold_pct`
  - net premium >= `strategy.lof_arbitrage.min_net_premium_pct`
  - apply is open
  - row is not downgraded by the phase-1 NAV-only rule

### 23.8 Fee and risk rules
- `estimatedCostRate` in phase 1 is the conservative visible fee sum of:
  - `applyFeeRate`
  - `managementFeeRate`
- `netPremiumRate = premiumRate - estimatedCostRate` when both are available.
- `riskFlags` must append warnings for at least:
  - NAV-only signal
  - limited apply
  - paused apply
  - low liquidity under `strategy.lof_arbitrage.low_liquidity_volume_wan`

### 23.9 Dashboard rendering
- The dashboard adds a new root tab key `lof-arb`.
- The LOF page structure is fixed to:
  1. module title and status text
  2. market subtab strip
  3. one paginated main table
- Visible top summary cards are removed from the LOF page in this round:
  - `套利候选`
  - `仅观察`
  - `数据链路`
- Main table columns are fixed to:
  - `序号`
  - `代码`
  - `基金 / 分区`
  - `现价 / 涨幅`
  - `净值 / 溢价`
  - `IOPV / 溢价`
  - `估值 / 溢价`
  - `信号溢价`
  - `扣费后溢价`
  - `申购状态`
  - `成交额(万)`
  - `结论`
  - `详情`
- Each row must render an always-visible secondary detail block for:
  - dates
  - fees
  - currency / T+0
  - reference index
  - risk flags

### 23.10 Search-status exposure
- `data.iopvSearch` is phase-1 operational metadata for the continuing zero-login IOPV search.
- It must expose at least:
  - `publicSourceStatus`
  - `currentZeroLoginAvailability`
- This metadata is informational only and must not block the page render.

## 24. LOF Authenticated Enrichment Spec (2026-03-23)

### 24.1 Fetch-mode rule
- `data_fetch/lof_arbitrage/fetcher.py` keeps using:
  - `/data/qdii/qdii_list/E`
  - `/data/qdii/qdii_list/A`
  - `/data/qdii/qdii_list/C`
- New optional config:
  - `data_fetch.plugins.lof_arbitrage.jisilu_cookie`
- When this cookie is present, the fetch session must send it as a request header and mark the source status as authenticated-enhanced.
- When the authenticated request fails or yields no usable response, the fetch layer must retry or fall back to the public path without taking down the module.

### 24.2 Source-status additions
- `data.sourceStatus.{group}` must additionally allow:
  - `cookieConfigured`
  - `authMode`
  - `usedLoginEnhancedRows`
- `authMode` is fixed to one of:
  - `public`
  - `authenticated`
  - `authenticated_fallback_public`
- `usedLoginEnhancedRows = true` only when the returned row set came from the authenticated request path.

### 24.3 Standardized LOF row additions
- Each outward LOF row keeps the phase-1 schema and additionally exposes:
  - `amountWanShares`
  - `amountIncreaseWanShares`
  - `amountIncreaseRate`
  - `navValueText`
  - `navPremiumRateText`
  - `iopvText`
  - `iopvPremiumRateText`
  - `estimatedValueText`
  - `estimatedPremiumRateText`
  - `referenceIndex`
  - `referenceIndexChangeRate`
  - `applyFeeText`
  - `redeemFeeText`
  - `managementFeeText`
  - `officialUrl`
  - `sourceDetailUrl`
- `officialUrl` comes from the source row `urls` field when available.
- `sourceDetailUrl` is the Jisilu detail page for the row symbol.

### 24.4 LOF page navigation
- The LOF page adds visible internal subtabs:
  - `europe_us`
  - `asia`
  - `commodity`
- Visible labels are fixed to:
  - `欧美市场`
  - `亚洲市场`
  - `商品`
- Frontend default LOF subtab becomes `europe_us`.

### 24.5 LOF long-table rendering
- The LOF main view renders one long table for the active market subtab.
- Main table columns are fixed to:
  - `序号`
  - `代码`
  - `名称`
  - `现价`
  - `涨跌幅`
  - `成交额(万元)`
  - `场内份额(万份)`
  - `场内新增(万份)`
  - `IOPV`
  - `IOPV溢价率`
  - `T-2净值`
  - `净值日期`
  - `T-2净值溢价`
  - `T-1指数涨幅`
  - `相关指数`
  - `申购费`
  - `申购状态`
  - `赎回费`
  - `赎回状态`
  - `管托费`
  - `基金公司`
  - `官方链接`
  - `集思录详情`
- The long table becomes the immediate primary reading path, without a visible summary-card band above it.

### 24.6 Missing-value truthfulness
- `IOPV`-related fields must remain empty when the current source chain does not return them.
- Frontend display text for truly missing `IOPV` / estimate values must use an explicit unavailability label rather than a fabricated number.
- The page should continue exposing the operational search state for better `IOPV` coverage, but this status is informational only.

### 24.7 LOF derived-estimate completion
- `data_fetch/lof_arbitrage/normalizer.py` may derive estimate fields only from source-provided raw fields.
- Phase-1 allowed estimate derivation:
  - `estimatedValue = navValue * (1 + est_val_increase_rt / 100)`
  - only when direct `estimate_value` is empty
- Phase-1 allowed estimate-premium derivation:
  - `estimatedPremiumRate = ((currentPrice / estimatedValue) - 1) * 100`
  - only when direct `discount_rt` is empty and `estimatedValue` exists
- `estimatedSource` fixed values:
  - `direct_source`
  - `derived_from_est_val_increase_rt`
- `estimatedSourceLabel` fixed outward semantics:
  - `源直接返回`
  - `Jisilu估值涨幅推导`
- LOF outward row additions for this round include:
  - `estimatedSource`
  - `estimatedSourceLabel`
  - `estimatedIncreaseRate`
  - `estimatedIncreaseRateText`
  - `turnoverRate`
  - `priceDate`
  - `amountDate`
  - `calculationTips`
  - `fundType`
- `estimatedTime` fallback order is fixed to:
  1. `last_est_datetime`
  2. `last_est_dt + last_est_time`
  3. `est_val_dt`
  4. `last_time`
- The LOF main table additionally renders:
  - `结论`
  - `信号溢价`
- `信号溢价` sorts by `premiumRate` descending by default inside each LOF market subtab.
- LOF detail rows additionally render:
  - `估值来源`
  - `估值涨幅`
  - `参考价`
  - `估值说明`
  - `报价时间`
- LOF secondary detail rows remain always visible beneath each row and serve as the default supplementary reading path.
- `IOPV` remains independent from the derived estimate path:
  - derived estimate logic must not populate `IOPV`
  - derived estimate logic must not populate `IOPV溢价率`

## 25. Event-arbitrage Detail Text Responsive Spec (2026-03-24)

### 25.1 Scope
- This round changes only the event-arbitrage detail-text presentation.
- No event-arbitrage API field names or payload semantics change.

### 25.2 Rendering rule
- `A股套利` detail `摘要` uses a dedicated single-column detail-grid variant.
- `港股套利` and `中概私有` detail `备注` use the same dedicated single-column variant.
- The single-column variant must span the available detail-row width on desktop instead of inheriting the default 4-column detail-grid compression.
- On narrow screens the same block continues wrapping naturally without horizontal overflow.
## 25. LOF Homepage Cancellation Spec (2026-03-24)

### 25.1 Scope rule
- `LOF套利` is removed from the public homepage module set in this round.
- This round is a homepage/runtime disconnect, not a full backend deletion.

### 25.2 Homepage navigation rule
- Visible homepage root tabs are fixed to:
  - `cb-arb`
  - `ah`
  - `ab`
  - `monitor`
  - `dividend`
  - `merger`
- The homepage template must not render:
  - `data-tab="lof-arb"`
  - `panel-lof-arb`

### 25.3 Dashboard bootstrap rule
- Frontend bootstrap must not request the LOF dataset.
- Frontend force-refresh key list must not include `lofArb`.
- The active-panel router must not route homepage tabs to `renderLofArbitragePanel()`.

### 25.4 Runtime preload rule
- Server preload dataset keys must not include `lofArb`.
- Existing backend route `GET /api/market/lof-arbitrage` may remain implemented, but it is outside the active homepage contract.

## 26. Shared Dashboard Table Readability Spec (2026-03-24)

### 26.1 Config contract
- `config.yaml` adds `presentation.dashboard_table_ui`.
- Required config fields:
  - `desktop_font_px`
  - `desktop_header_font_px`
  - `desktop_line_height`
  - `desktop_cell_padding_y`
  - `desktop_cell_padding_x`
  - `tablet_font_px`
  - `min_width_by_kind`
- `min_width_by_kind` must expose at least:
  - `subscription`
  - `convertible`
  - `premium`
  - `monitor`
  - `dividend`
  - `merger`
  - `lof`

### 26.2 UI-config API contract
- New route: `GET /api/dashboard/ui-config`
- Response shape:
  - `success`
  - `data.tableUi.desktopFontPx`
  - `data.tableUi.desktopHeaderFontPx`
  - `data.tableUi.desktopLineHeight`
  - `data.tableUi.desktopCellPaddingY`
  - `data.tableUi.desktopCellPaddingX`
  - `data.tableUi.tabletFontPx`
  - `data.tableUi.minWidthByKind`
- The route is read-only and reflects active presentation config only.

### 26.3 Shared rendering rule
- `renderPaginatedTable()` and `renderSimpleTable()` remain the only shared table rendering entry points in this round.
- Table readability upgrades must be implemented through shared CSS variables and shared renderer output, not module-specific table rewrites.
- Shared output structure must keep:
  - sticky headers
  - sort buttons
  - existing pagination bar
  - existing detail-row rendering behavior

### 26.4 Table density and width rule
- Desktop table body font target is larger than the previous `12px` contract.
- Desktop header font target is not smaller than body font.
- Shared table cells use relaxed line-height and larger padding than the old dense baseline.
- Tables may continue using horizontal wrappers, but width control shifts to per-kind `min-width` rules instead of relying only on a fully compressed fixed layout.
- `table[data-table-kind="subscription" | "convertible" | "premium" | "monitor" | "dividend" | "merger"]` must each consume the corresponding min-width config.
- If LOF table rendering is active later, `table[data-table-kind="lof"]` follows the same contract.

### 26.5 Typography and scanability rule
- Table cells use tabular-number rendering to stabilize:
  - price fields
  - percentage fields
  - code-like fields
  - pagination counters
- Shared table rows add clearer visual separation through:
  - a slightly stronger divider
  - or a weak zebra pattern
- Existing semantic row highlighting must remain visually dominant for:
  - today-highlight rows
  - subscription stage rows
  - error / status colors

### 26.6 Breakpoint rule
- `>= 1380px`: full desktop readability settings apply.
- `861px - 1379px`: use intermediate density with reduced font size relative to large desktop.
- `<= 860px`: keep the current compact/mobile-safe reading path:
  - limited font growth only
  - existing horizontal scroll containers remain valid
  - no separate mobile-only table rendering mode

## 26. LOF Complete Removal Spec (2026-03-24)

### 26.1 Scope rule
- `LOF套利` is fully removed from the active repository/runtime surface in this round.
- This round supersedes the earlier LOF homepage-cancellation-only approach.

### 26.2 Required removals
- Remove the LOF public route registration:
  - `GET /api/market/lof-arbitrage`
- Remove the LOF data-core action exposure:
  - `lof-arbitrage` in `data_dispatch.py`
- Remove active LOF dataset registration from server runtime.
- Remove active LOF bootstrap/render logic from the dashboard bundle.
- Remove active LOF config sections from `config.yaml`, including:
  - runtime file key
  - data-fetch plugin registration
  - strategy registration
  - LOF plugin tuning section
  - LOF strategy section
  - LOF presentation section
- Remove retired implementation directories:
  - `data_fetch/lof_arbitrage`
  - `strategy/lof_arbitrage`

### 26.3 Post-removal contract
- Homepage visible root tabs remain:
  - `cb-arb`
  - `ah`
  - `ab`
  - `monitor`
  - `dividend`
  - `merger`
- Unknown former LOF route access must fall back to the project's normal API 404 behavior.
- No active code path may still request, preload, or dispatch LOF data.
