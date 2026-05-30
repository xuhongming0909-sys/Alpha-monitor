# -*- coding: utf-8 -*-
# AI-SUMMARY: 持仓名称→ticker解析器：映射表查找→Yahoo搜索→mimo验证→回写映射表
"""持仓名称→ticker解析器。

流程:
1. PDF提取持仓名称
2. 查 holdings_name_map.json 映射表
3. 未命中 → Yahoo Finance search获取候选ticker
4. 候选ticker + 证券全名 → mimo验证有效性
5. mimo判定有效 → 记录映射；无效 → mimo提供正确ticker
6. 回写映射表，保证1:1一致性
"""
from __future__ import annotations

import json
import logging
import os
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_MAP_PATH = os.path.join(os.path.dirname(__file__), 'holdings_name_map.json')


# ============================================================
# 映射表读写
# ============================================================

def _load_map() -> Dict[str, Dict]:
    """加载映射表 {name: {ticker, market, source}}。"""
    if not os.path.exists(_MAP_PATH):
        return {}
    with open(_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f) or {}


def _save_map(mapping: Dict[str, Dict]) -> None:
    """保存映射表，保证1:1一致性。"""
    # 检查1:1: 同一ticker不应对应不同name(允许)，但同一name不能对应不同ticker(已由dict保证)
    with open(_MAP_PATH, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def add_mapping(name: str, ticker: str, market: str, source: str = "verified") -> bool:
    """添加映射。返回True表示新增，False表示已存在且一致。"""
    mapping = _load_map()
    key = name.strip()
    if key in mapping:
        existing = mapping[key]
        if existing['ticker'] == ticker:
            return False  # 已存在且一致
        # 冲突: 同名不同ticker → 覆盖为新值
        logger.warning(f"映射冲突: '{key}' {existing['ticker']} -> {ticker}")
    mapping[key] = {"ticker": ticker, "market": market, "source": source}
    _save_map(mapping)
    return True


# ============================================================
# 解析流程
# ============================================================

def resolve_from_map(name: str) -> Optional[Tuple[str, str]]:
    """从映射表查找。返回 (ticker, market) 或 None。"""
    mapping = _load_map()
    key = name.strip()
    if key in mapping:
        entry = mapping[key]
        return entry['ticker'], entry['market']
    # 模糊匹配: 大写比较
    nu = key.upper()
    for k, v in mapping.items():
        if k.upper() == nu:
            return v['ticker'], v['market']
    return None


def search_yahoo(name: str) -> Optional[Dict]:
    """Yahoo Finance搜索候选ticker。"""
    try:
        from data_fetch.lof_iopv.yahoo_finance import search_ticker
        return search_ticker(name)
    except Exception as e:
        logger.warning(f"Yahoo search failed: {e}")
        return None


def validate_with_mimo(holding_name: str, candidate_ticker: str, candidate_name: str) -> Dict:
    """发送候选ticker给mimo验证。

    Returns:
        {"valid": bool, "ticker": str, "market": str, "reason": str}
    """
    try:
        import httpx
        import yaml

        secrets_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'secrets.yaml')
        with open(secrets_path, 'r', encoding='utf-8') as f:
            cfg = (yaml.safe_load(f) or {}).get('vision', {})

        if not cfg.get('api_key'):
            return {"valid": False, "ticker": "", "market": "", "reason": "no_api_key"}

        prompt = f"""判断以下证券代码是否正确匹配持仓名称。

持仓名称: {holding_name}
候选代码: {candidate_ticker}
候选全名: {candidate_name}

请回复JSON格式:
{{"valid": true/false, "ticker": "正确代码", "market": "US/HK/UK/JP/A/DE/CH/EU", "reason": "简短说明"}}

如果候选代码正确，ticker保持不变。如果不正确，请提供正确的代码。
只输出JSON，不要其他文字。"""

        r = httpx.post(
            cfg.get('base_url', ''),
            headers={"Authorization": f"Bearer {cfg['api_key']}"},
            json={
                "model": cfg.get('model', 'mimo-v2.5'),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 200,
            },
            timeout=30,
        )
        content = r.json()["choices"][0]["message"]["content"].strip()
        # 提取JSON
        import re
        m = re.search(r'\{[^}]+\}', content)
        if m:
            return json.loads(m.group())
        return {"valid": False, "ticker": "", "market": "", "reason": "parse_error"}

    except Exception as e:
        logger.warning(f"mimo validation failed: {e}")
        return {"valid": False, "ticker": "", "market": "", "reason": str(e)}


def resolve_ticker(name: str, skip_validation: bool = False) -> Optional[Dict]:
    """完整解析流程: 映射表 → Yahoo搜索 → mimo验证 → 回写。

    Returns:
        {"ticker": str, "market": str, "source": "map|yahoo|mimo"}
        or None
    """
    # Step 1: 映射表查找
    result = resolve_from_map(name)
    if result:
        ticker, market = result
        return {"ticker": ticker, "market": market, "source": "map"}

    # Step 2: Yahoo搜索
    yahoo_result = search_yahoo(name)
    if not yahoo_result:
        return None

    candidate_ticker = yahoo_result.get("ticker", "")
    candidate_name = yahoo_result.get("name", "")
    candidate_market = yahoo_result.get("market", "US")

    if not candidate_ticker:
        return None

    # Step 3: mimo验证
    if skip_validation:
        # 直接信任Yahoo结果
        add_mapping(name, candidate_ticker, candidate_market, source="yahoo")
        return {"ticker": candidate_ticker, "market": candidate_market, "source": "yahoo"}

    validation = validate_with_mimo(name, candidate_ticker, candidate_name)

    if validation.get("valid"):
        final_ticker = validation.get("ticker", candidate_ticker)
        final_market = validation.get("market", candidate_market)
        add_mapping(name, final_ticker, final_market, source="verified")
        return {"ticker": final_ticker, "market": final_market, "source": "mimo_verified"}
    else:
        # mimo提供了正确代码
        correct_ticker = validation.get("ticker", "")
        correct_market = validation.get("market", "")
        if correct_ticker:
            add_mapping(name, correct_ticker, correct_market, source="mimo_corrected")
            return {"ticker": correct_ticker, "market": correct_market, "source": "mimo_corrected"}
        return None


def resolve_batch(holdings: List[Dict], skip_validation: bool = False) -> List[Dict]:
    """批量解析持仓。对每条持仓补充ticker和market。

    Args:
        holdings: [{"name": "xxx", "weight": 10.0}, ...]
        skip_validation: True则跳过mimo验证(直接信任Yahoo)

    Returns:
        [{"name": "xxx", "ticker": "YYY", "market": "US", "weight": 10.0}, ...]
    """
    import time
    results = []
    for h in holdings:
        name = h.get("name", "")
        if not name:
            results.append(h)
            continue

        # 已有ticker则跳过
        if h.get("ticker"):
            results.append(h)
            continue

        resolved = resolve_ticker(name, skip_validation=skip_validation)
        if resolved:
            h["ticker"] = resolved["ticker"]
            h["market"] = resolved["market"]
            logger.info(f"  resolved: {name} -> {resolved['ticker']} ({resolved['source']})")
        else:
            logger.warning(f"  unresolved: {name}")

        results.append(h)
        time.sleep(0.5)  # rate limit

    return results


def get_map_stats() -> Dict:
    """返回映射表统计。"""
    mapping = _load_map()
    sources = {}
    for v in mapping.values():
        s = v.get('source', 'unknown')
        sources[s] = sources.get(s, 0) + 1
    return {"total": len(mapping), "by_source": sources}