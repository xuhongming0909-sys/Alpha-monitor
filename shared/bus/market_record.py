"""The Bus 标准记录模型。

本模块只定义抓取层与策略层之间共享的normalizer数据结构，
不承载任何具体业务插件的抓取逻辑或策略判断。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


REQUIRED_FIELDS = (
    "plugin",
    "market",
    "symbol",
    "name",
    "event_type",
    "quote_time",
    "metrics",
    "raw",
    "status",
)

ALLOWED_STATUS = {"ok", "empty", "error"}


@dataclass(slots=True)
class MarketRecord:
    """The Bus 单条标准记录。

    字段设计目标是让策略层只关心业务语义，不关心上游source长什么样。
    """

    plugin: str
    market: str
    symbol: str
    name: str
    event_type: str
    quote_time: str
    metrics: Dict[str, Any]
    raw: Dict[str, Any]
    status: str
    currency: Optional[str] = None
    source: Optional[str] = None
    date: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    message: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """将标准记录转换为可序列化字典。"""

        return {
            "plugin": self.plugin,
            "market": self.market,
            "symbol": self.symbol,
            "name": self.name,
            "event_type": self.event_type,
            "quote_time": self.quote_time,
            "metrics": dict(self.metrics),
            "raw": dict(self.raw),
            "status": self.status,
            "currency": self.currency,
            "source": self.source,
            "date": self.date,
            "tags": list(self.tags),
            "message": self.message,
            "extra": dict(self.extra),
        }


def validate_market_record(payload: Dict[str, Any]) -> None:
    """校验一条记录是否满足 The Bus v1 的最低契约。

    这里故意只校验结构，不做业务含义判断。
    业务阈值、排序规则等应由策略插件自己负责。
    """

    missing = [field_name for field_name in REQUIRED_FIELDS if field_name not in payload]
    if missing:
        raise ValueError(f"missing required bus fields: {', '.join(missing)}")

    status = str(payload.get("status") or "").strip()
    if status not in ALLOWED_STATUS:
        raise ValueError(f"invalid bus status: {status}")

    metrics = payload.get("metrics")
    raw = payload.get("raw")
    if not isinstance(metrics, dict):
        raise ValueError("metrics must be a dict")
    if not isinstance(raw, dict):
        raise ValueError("raw must be a dict")


def create_market_record(**kwargs: Any) -> Dict[str, Any]:
    """创建并校验标准记录字典。

    之所以返回字典而不是直接返回 dataclass，是为了让现有 Python 代码
    能更平滑地与 JSON、CLI 输出和旧逻辑兼容。
    """

    record = MarketRecord(**kwargs)
    payload = record.to_dict()
    validate_market_record(payload)
    return payload


# 保留英文别名，方便shared内部或后续脚本按稳定英文接口引用。
validate_market_record = validate_market_record
create_market_record = create_market_record


