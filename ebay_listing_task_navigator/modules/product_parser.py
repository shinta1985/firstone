from __future__ import annotations

import re
from typing import Any


def _contains(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(keyword.lower() in lower for keyword in keywords)


def parse_product(description: str, knowledge: dict[str, Any]) -> dict[str, Any]:
    text = description.strip()
    rules = knowledge.get("category_rules", {}).get("rules", [])
    matched = next((rule for rule in rules if _contains(text, rule.get("keywords", []))), rules[-1])

    condition = "Used"
    if _contains(text, ["新品", "未使用", "new", "unused"]):
        condition = "New / unused"
    elif _contains(text, ["中古", "古い", "傷", "used", "vintage"]):
        condition = "Used"
    elif _contains(text, ["ジャンク", "故障", "動作未確認", "broken", "parts"]):
        condition = "For parts or not working"

    fragility = "High" if matched.get("fragile") or _contains(text, ["ガラス", "陶器", "精密", "壊れ", "レンズ"]) else "Normal"
    return_risk = "High" if _contains(text, ["動作未確認", "ジャンク", "傷", "欠品", "古い"]) else "Medium" if condition == "Used" else "Low"
    regulated = _contains(text, ["電池", "バッテリー", "香水", "食品", "医療", "ブランド"])

    title_hint = matched.get("title_hint", "Japanese Item")
    cleaned = re.sub(r"\s+", " ", text)[:80]
    title = f"{title_hint} from Japan - {condition} - Please Check Photos"
    english_description = (
        f"This listing is for a {title_hint.lower()} from Japan. "
        f"Condition is estimated as {condition}. Original note: {cleaned}. "
        "Please review all photos and ask questions before purchase."
    )

    photo_points = list(dict.fromkeys(matched.get("photo_points", []) + ["正面", "背面", "傷", "付属品", "梱包前状態"]))
    notes = ["状態、型番、付属品、欠品の有無を明記してください。"]
    if condition == "Used":
        notes.append("中古品であること、使用感や小傷がある可能性を明記してください。")
    if regulated:
        notes.append("規制・禁制品・航空危険物に該当しないか公式ページで確認してください。")

    return {
        "category": matched.get("category", "General Merchandise"),
        "condition": condition,
        "fragility": fragility,
        "regulatory_risk": "要確認: High" if regulated else "要確認: Normal",
        "return_risk": return_risk,
        "photo_points": photo_points,
        "description_notes": notes,
        "english_title": title,
        "english_description": english_description,
        "condition_description": f"推定: {condition}. 要確認: Please inspect photos for scratches, accessories, and exact condition.",
        "buyer_notice": "要確認: Import duties, taxes, and remote area fees are the buyer's responsibility when applicable.",
        "labels": ["推定", "要確認"],
    }
