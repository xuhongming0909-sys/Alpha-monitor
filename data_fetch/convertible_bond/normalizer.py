# AI-SUMMARY: 可转债数据标准化：含理论定价和小额刚兑字段的 Bus 记录生成
# 对应 INDEX.md §9 文件摘要索引

"""convertible_bond 标准化器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def normalize_convertible_bond_snapshot(payload: dict) -> list[dict]:
    """把 convertible_bond 实时结果转换成总线记录。"""

    if not payload or payload.get("success") is False:
        return [
            create_market_record(
                plugin="convertible_bond",
                market="CN",
                symbol="*",
                name="convertible_bond快照",
                event_type="convertible_bond_snapshot",
                quote_time=now_iso(),
                metrics={},
                raw={"error": payload.get("error") if isinstance(payload, dict) else "unknown"},
                status="error",
                source=(payload or {}).get("source") if isinstance(payload, dict) else None,
                message=(payload or {}).get("error", "convertible_bond抓取失败") if isinstance(payload, dict) else "convertible_bond抓取失败",
            )
        ]

    rows = []
    for item in payload.get("data", []) or []:
        rows.append(
            create_market_record(
                plugin="convertible_bond",
                market="CN",
                symbol=str(item.get("code") or ""),
                name=str(item.get("bondName") or ""),
                event_type="convertible_bond_snapshot",
                quote_time=str(payload.get("updateTime") or now_iso()),
                metrics={
                    "price": item.get("price"),
                    "stock_price": item.get("stockPrice"),
                    "convert_price": item.get("convertPrice"),
                    "convert_value": item.get("convertValue"),
                    "premium_rate": item.get("premiumRate"),
                    "volatility250": item.get("volatility250"),
                    "theoretical_premium_rate": item.get("theoreticalPremiumRate"),
                    "double_low": item.get("doubleLow"),
                    "remaining_years": item.get("remainingYears"),
                    "remaining_size_yi": item.get("remainingSizeYi"),
                    "holder_count": item.get("holderCount"),
                    "holder_count_report_period": item.get("holderCountReportPeriod"),
                    "holder_count_report_source_url": item.get("holderCountReportSourceUrl"),
                    "holder_count_fallback_used": item.get("holderCountFallbackUsed"),
                    "stock_net_assets_yi": item.get("stockNetAssetsYi"),
                    "stock_interest_bearing_debt_yi": item.get("stockInterestBearingDebtYi"),
                    "stock_broad_cash_yi": item.get("stockBroadCashYi"),
                    "stock_net_debt_exposure_yi": item.get("stockNetDebtExposureYi"),
                    "small_redemption_yield": item.get("smallRedemptionYield"),
                    "small_redemption_expected_years": item.get("smallRedemptionExpectedYears"),
                    "small_redemption_annualized_yield": item.get("smallRedemptionAnnualizedYield"),
                    "small_redemption_amount": item.get("smallRedemptionAmount"),
                    "small_redemption_total_amount": item.get("smallRedemptionTotalAmount"),
                    "small_redemption_option_value": item.get("smallRedemptionOptionValue"),
                    "small_redemption_option_yield": item.get("smallRedemptionOptionYield"),
                    "small_redemption_option_annualized_yield": item.get("smallRedemptionOptionAnnualizedYield"),
                    "small_redemption_total_annualized_yield": item.get("smallRedemptionTotalAnnualizedYield"),
                    "stock_name": item.get("stockName"),
                    "stock_code": item.get("stockCode"),
                    "stock_change_percent": item.get("stockChangePercent"),
                    "bond_name": item.get("bondName"),
                    "change_percent": item.get("changePercent"),
                    "convert_start_date": item.get("convertStartDate"),
                    "maturity_date": item.get("maturityDate"),
                    "redeem_trigger_price": item.get("redeemTriggerPrice"),
                    "putback_price": item.get("putbackPrice"),
                    "putback_trigger_price": item.get("putbackTriggerPrice"),
                    "force_redeem_status": item.get("forceRedeemStatus"),
                    "listing_date": item.get("listingDate"),
                    "turnover_amount_yi": item.get("turnoverAmountYi"),
                    "stock_market_value_yi": item.get("stockMarketValueYi"),
                    "stock_atr20": item.get("stockAtr20"),
                    "is_delisted_or_expired": item.get("isDelistedOrExpired"),
                    "call_strike": item.get("callStrike"),
                    "redeem_call_strike": item.get("redeemCallStrike"),
                    "option_value": item.get("optionValue"),
                    "theoretical_price": item.get("theoreticalPrice"),
                    "putback_status": item.get("putbackStatus"),
                },
                raw=dict(item),
                status="ok",
                currency="CNY",
                source=str(payload.get("source") or ""),
                date=str(payload.get("tradeDate") or "") or str(payload.get("updateTime") or "")[:10],
                tags=["convertible_bond"],
            )
        )
    return rows
