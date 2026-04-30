# AI-SUMMARY: 自定义监控业务计算：组合收益率、对价计算
# 对应 INDEX.md §9 文件摘要索引

"""custom_monitor策略服务。"""

from __future__ import annotations


def to_cny(amount: float | None, currency: str, rates: dict[str, float]) -> float | None:
    """把不同币种统一换算成人民币。"""

    if amount is None:
        return None
    currency_text = str(currency or "CNY").upper()
    if currency_text == "CNY":
        return amount
    if currency_text == "HKD":
        return amount * float(rates.get("hkToCny") or 0) if rates.get("hkToCny") else None
    if currency_text == "USD":
        return amount * float(rates.get("usdToCny") or 0) if rates.get("usdToCny") else None
    return None


def recalculate_monitor(monitor: dict, rates: dict[str, float]) -> dict:
    """按既有公式重算换股腿、现金腿和收益率。"""

    target_price_cny = to_cny(monitor.get("targetPriceOriginal") or monitor.get("targetPrice"), monitor.get("targetCurrency", "CNY"), rates)
    acquirer_price_cny = to_cny(monitor.get("acquirerPriceOriginal") or monitor.get("acquirerPrice"), monitor.get("acquirerCurrency", "CNY"), rates)
    stock_ratio = float(monitor.get("stockRatio") or 0)
    safety_factor = min(1.0, max(0.0, float(monitor.get("safetyFactor") or 1)))
    cash_distribution_cny = to_cny(float(monitor.get("cashDistribution") or 0), monitor.get("cashDistributionCurrency", "CNY"), rates)
    cash_option_price_cny = to_cny(float(monitor.get("cashOptionPrice") or 0), monitor.get("cashOptionCurrency", "CNY"), rates)

    stock_payout = None
    if acquirer_price_cny is not None and cash_distribution_cny is not None and (stock_ratio != 0 or float(monitor.get("cashDistribution") or 0) != 0):
        stock_payout = acquirer_price_cny * stock_ratio * safety_factor + cash_distribution_cny

    stock_spread = (stock_payout - target_price_cny) if stock_payout is not None and target_price_cny not in (None, 0) else None
    stock_yield_rate = ((stock_spread / target_price_cny) * 100) if stock_spread is not None and target_price_cny not in (None, 0) else None
    cash_spread = (cash_option_price_cny - target_price_cny) if cash_option_price_cny is not None and target_price_cny not in (None, 0) else None
    cash_yield_rate = ((cash_spread / target_price_cny) * 100) if cash_spread is not None and target_price_cny not in (None, 0) else None

    return {
        **monitor,
        "acquirerPrice": acquirer_price_cny,
        "targetPrice": target_price_cny,
        "stockSpread": stock_spread,
        "stockYieldRate": stock_yield_rate,
        "cashSpread": cash_spread,
        "cashYieldRate": cash_yield_rate,
    }

