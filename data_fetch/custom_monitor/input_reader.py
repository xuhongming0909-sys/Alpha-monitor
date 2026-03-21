"""custom_monitorinput_reader器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.paths.script_paths import runtime_file_path
from shared.runtime.json_store import read_json
from shared.time.shanghai_time import now_iso


def read_custom_monitor_records() -> list[dict]:
    """从运行态 JSON 读取custom_monitor配置，并映射成总线记录。"""

    file_path = runtime_file_path("custom_monitors.json")
    payload = read_json(file_path, {"monitors": []})
    rows = payload.get("monitors") if isinstance(payload, dict) else []
    records = []
    for item in rows if isinstance(rows, list) else []:
        records.append(
            create_market_record(
                plugin="custom_monitor",
                market="CN",
                symbol=str(item.get("targetCode") or item.get("id") or ""),
                name=str(item.get("name") or ""),
                event_type="monitor_definition",
                quote_time=str(item.get("updateTime") or now_iso()),
                metrics={
                    "stock_ratio": item.get("stockRatio"),
                    "cash_distribution": item.get("cashDistribution"),
                    "cash_option_price": item.get("cashOptionPrice"),
                    "safety_factor": item.get("safetyFactor"),
                },
                raw=dict(item),
                status="ok",
                currency="CNY",
                source="runtime_state",
                date=str(item.get("updateTime") or now_iso())[:10],
                tags=["custom_monitor"],
            )
        )
    return records

