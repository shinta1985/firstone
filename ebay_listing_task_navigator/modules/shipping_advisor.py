from __future__ import annotations

from typing import Any


def recommend_shipping(dimensions_cm: dict[str, float], weight_g: float, parsed: dict[str, Any], sale_price_jpy: float = 0) -> list[dict[str, Any]]:
    volume = dimensions_cm["length"] * dimensions_cm["width"] * dimensions_cm["height"]
    fragile = parsed.get("fragility") == "High"
    category = parsed.get("category", "")
    recommendations: list[dict[str, Any]] = []

    if weight_g <= 2000 and volume <= 60000 and sale_price_jpy < 30000:
        recommendations.append({
            "carrier": "Japan Post",
            "reason": "推定: 小型軽量・標準価格帯のため候補。要確認: 引受停止、国別条件、料金。",
            "source_keys": ["japan_post_international", "japan_post_rates"],
        })
    if sale_price_jpy >= 30000 or fragile:
        recommendations.extend([
            {"carrier": "FedEx", "reason": "推定: 高額/壊れ物は追跡・補償重視。要確認: 料金とサーチャージ。", "source_keys": ["fedex_japan", "fedex_rates"]},
            {"carrier": "DHL Express", "reason": "推定: 速達・追跡重視の候補。要確認: 通関・見積。", "source_keys": ["dhl_japan", "dhl_rates"]},
            {"carrier": "UPS", "reason": "推定: 高額・追跡重視の候補。要確認: 料金ガイド。", "source_keys": ["ups_japan"]},
        ])
    if "Cameras" in category:
        recommendations.append({
            "carrier": "Battery restriction check",
            "reason": "要確認: カメラは電池同梱の有無で発送条件が変わる可能性があります。",
            "source_keys": ["japan_post_international", "ebay_prohibited_items"],
        })
    if not recommendations:
        recommendations.append({
            "carrier": "Compare all carriers",
            "reason": "推定: サイズ・重量が標準外の可能性があります。要確認: 公式料金ページで比較。",
            "source_keys": ["japan_post_rates", "fedex_rates", "dhl_rates", "ups_japan"],
        })
    return recommendations
