from __future__ import annotations

from typing import Any


def check_risks(description: str, parsed: dict[str, Any], knowledge: dict[str, Any]) -> list[dict[str, str]]:
    risks: list[dict[str, str]] = []
    lower = description.lower()
    for item in knowledge.get("prohibited_items", {}).get("risk_keywords", []):
        if item.get("keyword", "").lower() in lower:
            risks.append({
                "severity": item.get("severity", "medium"),
                "title": f"要確認: {item.get('risk')}",
                "message": item.get("message", "公式ページで確認してください。"),
                "source_key": "ebay_prohibited_items",
            })
    if parsed.get("return_risk") == "High":
        risks.append({
            "severity": "medium",
            "title": "推定: 返品リスク高め",
            "message": "傷・欠品・動作状態を写真と説明文で明確にしてください。",
            "source_key": "ebay_shipping_policy",
        })
    if parsed.get("fragility") == "High":
        risks.append({
            "severity": "medium",
            "title": "推定: 壊れやすい商品",
            "message": "緩衝材、二重梱包、補償付き配送を検討してください。",
            "source_key": "ebay_shipping_policy",
        })
    return risks
