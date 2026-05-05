#!/usr/bin/env python3
"""批量给文件添加 AI-SUMMARY 注释头。"""

from pathlib import Path

SUMMARIES = {
    "server_config_loader.js": "服务器配置加载：端口/路径/策略/超时等配置读取",
    "start_server.js": "Express 主入口：启动服务、挂载路由、注册调度器、管理运行时状态",
    "data_dispatch.py": "CLI 数据调度器：根据 action 调用对应 data_fetch 抓取和 strategy 计算",
    "config.yaml": "业务配置合同：所有参数、阈值、URL、开关的单一来源",
    "data_fetch/ah_premium/fetcher.py": "AH 溢价抓取调度：调用腾讯行情 API 并标准化为 Bus 记录",
    "data_fetch/ah_premium/normalizer.py": "AH 溢价数据标准化：原始行情转为 Bus 标准化记录",
    "data_fetch/ab_premium/fetcher.py": "AB 溢价抓取调度：调用腾讯行情 API 并标准化为 Bus 记录",
    "data_fetch/ab_premium/normalizer.py": "AB 溢价数据标准化：原始行情转为 Bus 标准化记录",
    "data_fetch/convertible_bond/fetcher.py": "可转债抓取调度：调用集思录/东方财富 API",
    "data_fetch/convertible_bond/cb_metrics.py": "可转债指标计算：波动率/ATR/理论定价/纯债价值/期权价值",
    "data_fetch/convertible_bond/source.py": "可转债上游 API：集思录实时行情 + 东方财富财务数据",
    "data_fetch/convertible_bond/normalizer.py": "可转债数据标准化：含理论定价的 Bus 记录生成",
    "data_fetch/lof_arbitrage/fetcher.py": "LOF 套利抓取调度：调用集思录 API",
    "data_fetch/lof_arbitrage/source.py": "LOF 套利上游 API：集思录 LOF/QDII 实时数据",
    "data_fetch/merger/fetcher.py": "并购数据抓取调度：调用巨潮公告 API",
    "data_fetch/merger/source.py": "并购公告 API：巨潮资讯公告搜索与解析",
    "data_fetch/dividend/fetcher.py": "股息抓取调度：调用 AkShare/巨潮 API",
    "data_fetch/dividend/source.py": "股息上游 API：AkShare CNINFO + 腾讯行情",
    "data_fetch/subscription/fetcher.py": "申购抓取调度：IPO + 转债申购日历",
    "data_fetch/exchange_rate/fetcher.py": "汇率抓取调度：调用腾讯汇率 API",
    "data_fetch/custom_monitor/input_reader.py": "自定义监控输入读取：从运行态 JSON 读取用户组合",
    "data_fetch/event_arbitrage/fetcher.py": "事件套利抓取调度：调用集思录事件 API",
    "data_fetch/cb_rights_issue/fetcher.py": "抢权配售抓取调度：调用集思录预案 API",
    "strategy/ah_premium/service.py": "AH 溢价业务计算：溢价率排名、历史百分位",
    "strategy/ah_premium/service.js": "AH 溢价 Node 适配器：Python 计算结果转为 API 响应",
    "strategy/ab_premium/service.py": "AB 溢价业务计算：AB 股溢价率排名",
    "strategy/ab_premium/service.js": "AB 溢价 Node 适配器：Python 计算结果转为 API 响应",
    "strategy/convertible_bond/service.py": "可转债业务计算：双低策略、理论收益率、回售套利",
    "strategy/convertible_bond/service.js": "可转债 Node 适配器：计算结果格式化、折价策略状态",
    "strategy/merger/service.py": "并购套利业务计算：Deal 分析、AI 报告生成",
    "strategy/merger/service.js": "并购套利 Node 适配器：报告生成调度",
    "strategy/lof_arbitrage/service.py": "LOF 套利业务计算：溢价率排名与过滤",
    "strategy/custom_monitor/service.py": "自定义监控业务计算：组合收益率、对价计算",
    "strategy/dividend/service.py": "股息业务计算：登记日跟踪、股息率计算",
    "strategy/subscription/service.py": "申购业务计算：申购事件跟踪与状态管理",
    "strategy/event_arbitrage/service.py": "事件套利业务计算：事件匹配与过滤规则",
    "strategy/cb_rights_issue/service.py": "抢权配售业务计算：预期收益、阶段判定、入池判断",
    "presentation/routes/market_routes.js": "市场行情 API 路由：/api/market/* 端点定义",
    "presentation/routes/dashboard_routes.js": "看板 API 路由：/api/dashboard/* 端点定义",
    "presentation/routes/push_routes.js": "推送配置 API 路由：/api/push/* 端点定义",
    "presentation/view_models/overview.js": "看板概览数据组装：聚合各模块数据为统一视图",
    "presentation/view_models/push_payload.js": "推送配置响应格式：推送配置数据结构整形",
    "presentation/dashboard/constants.js": "看板 UI 常量：端点、Tab 序列、表格配置、样式默认值",
    "presentation/dashboard/dashboard_page.js": "旧看板页面逻辑：HTML 看板渲染与交互",
    "presentation/templates/dashboard_template.html": "旧看板 HTML 模板：含内联 CSS/JS",
    "notification/wecom/client.js": "企业微信客户端：发送 Markdown 到 Webhook",
    "notification/scheduler/wecom_scheduler.js": "推送调度器：定时 tick 触发各模块推送",
    "notification/scheduler/push_config_store.js": "推送配置存储：主推送配置读写",
    "notification/scheduler/push_runtime_store.js": "推送运行时存储：推送状态与历史",
    "notification/summary/main_summary.js": "每日摘要组装：聚合所有模块生成推送 Markdown",
    "notification/alerts/event_alert_service.js": "事件告警服务：折价策略买入/卖出/监控实时推送",
    "notification/cb_arbitrage/service.js": "可转债套利推送：独立推送逻辑与格式化",
    "notification/cb_rights_issue/service.js": "抢权配售推送：独立推送逻辑与格式化",
    "notification/lof_arbitrage/service.js": "LOF 套利推送：独立推送逻辑与格式化",
    "notification/merger_report/service.js": "并购报告推送：DeepSeek AI 报告生成与推送",
    "notification/styles/markdown_style.js": "推送 Markdown 样式：通用格式化模板",
    "shared/config/node_config.js": "Node 配置读取器：YAML 解析 + 环境变量/Secrets 注入",
    "shared/config/script_config.py": "Python 配置读取器：YAML 解析 + 环境变量/Secrets 注入",
    "shared/bus/market_record.js": "Bus 标准化记录（JS）：跨层通信数据结构",
    "shared/bus/market_record.py": "Bus 标准化记录（Python）：跨层通信数据结构",
    "shared/runtime/json_store.js": "JSON 持久化（JS）：运行时状态读写",
    "shared/runtime/json_store.py": "JSON 持久化（Python）：运行时状态读写",
    "shared/runtime/state_registry.js": "状态注册表（JS）：运行时文件统一管理",
    "shared/runtime/state_registry.py": "状态注册表（Python）：运行时文件统一管理",
    "shared/time/shanghai_time.js": "上海时区（JS）：交易时段检测、市场时间",
    "shared/time/shanghai_time.py": "上海时区（Python）：交易时段检测、市场时间",
    "shared/paths/node_paths.js": "路径解析（JS）：运行时目录、数据库路径",
    "shared/paths/script_paths.py": "路径解析（Python）：运行时目录、数据库路径",
    "shared/models/service_result.js": "标准响应包装（JS）：成功/错误响应格式",
    "shared/models/service_result.py": "标准响应包装（Python）：成功/错误响应格式",
    "shared/market_service.py": "跨市场工具：价格查询、配对匹配、股票搜索",
    "shared/utils/ranking.js": "通用排序工具：按字段升降序取 Top N",
    "tools/check_plugin_boundaries.py": "架构边界检查：验证插件间无非法依赖",
    "tools/rebuild_premium_db.py": "溢价历史数据库重建：AH/AB 溢价历史维护",
    "tools/stock_price_history_db.py": "股价历史数据库：正股 K 线数据管理",
    "tools/premium_history_db.py": "溢价历史数据库：溢价率历史数据管理",
    "tools/export_pair_pool.py": "配对池导出：AH/AB 配对表生成",
    "tests/smoke_check.js": "冒烟测试：验证服务首页和 health 端点可达",
}


def process_file(rel_path, summary, root):
    path = root / rel_path
    if not path.exists():
        print(f"SKIP (not found): {rel_path}")
        return

    content = path.read_text(encoding="utf-8")
    prefix = "#" if path.suffix == ".py" else "//"
    if path.suffix == ".html":
        prefix, suffix = "<!--", " -->"
    else:
        suffix = ""

    summary_line = f"{prefix} AI-SUMMARY: {summary}{suffix}\n"
    idx_line = f"{prefix} 对应 INDEX.md §9 文件摘要索引{suffix}\n"

    if "AI-SUMMARY:" in content:
        lines = content.splitlines(keepends=True)
        new_lines = []
        updated_summary = False
        for line in lines:
            if "AI-SUMMARY:" in line and not updated_summary:
                new_lines.append(summary_line)
                updated_summary = True
            elif "对应 INDEX.md" in line and updated_summary:
                new_lines.append(idx_line)
            else:
                new_lines.append(line)
        path.write_text("".join(new_lines), encoding="utf-8")
        print(f"UPDATED: {rel_path}")
        return

    # Insert at top, after shebang if present
    if content.startswith("#!/") or content.startswith("# -*- coding"):
        lines = content.splitlines(keepends=True)
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("#!/") or line.startswith("# -*- coding"):
                insert_pos = i + 1
        new_lines = lines[:insert_pos] + ["\n", summary_line, idx_line, "\n"] + lines[insert_pos:]
        path.write_text("".join(new_lines), encoding="utf-8")
    else:
        path.write_text(summary_line + idx_line + "\n" + content, encoding="utf-8")
    print(f"ADDED: {rel_path}")


def main():
    root = Path("/Users/xuhongming/Desktop/Alpha monitor")
    for rel_path, summary in SUMMARIES.items():
        process_file(rel_path, summary, root)


if __name__ == "__main__":
    main()
