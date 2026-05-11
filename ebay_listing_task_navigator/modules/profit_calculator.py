from __future__ import annotations


def calculate_profit(cost_jpy: float, sale_price_jpy: float, shipping_jpy: float, materials_jpy: float, fee_rate_percent: float, fx_rate: float, other_costs_jpy: float) -> dict[str, float]:
    fees = sale_price_jpy * fee_rate_percent / 100
    total_cost = cost_jpy + shipping_jpy + materials_jpy + fees + other_costs_jpy
    profit = sale_price_jpy - total_cost
    profit_margin = (profit / sale_price_jpy * 100) if sale_price_jpy else 0
    sale_price_usd = (sale_price_jpy / fx_rate) if fx_rate else 0
    return {
        "fees_jpy": round(fees, 2),
        "total_cost_jpy": round(total_cost, 2),
        "profit_jpy": round(profit, 2),
        "profit_margin_percent": round(profit_margin, 2),
        "sale_price_usd": round(sale_price_usd, 2),
    }
