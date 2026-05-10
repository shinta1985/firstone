from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from app.models import ListingCondition

CONDITION_MULTIPLIERS: dict[ListingCondition, Decimal] = {
    ListingCondition.NEW: Decimal("1.18"),
    ListingCondition.LIKE_NEW: Decimal("1.08"),
    ListingCondition.USED_EXCELLENT: Decimal("1.00"),
    ListingCondition.USED_GOOD: Decimal("0.86"),
    ListingCondition.USED_ACCEPTABLE: Decimal("0.68"),
}

CONDITION_LABELS_JA: dict[ListingCondition, str] = {
    ListingCondition.NEW: "新品",
    ListingCondition.LIKE_NEW: "未使用に近い",
    ListingCondition.USED_EXCELLENT: "中古・非常に良い",
    ListingCondition.USED_GOOD: "中古・良い",
    ListingCondition.USED_ACCEPTABLE: "中古・可",
}

CATEGORY_PROFILES = [
    {
        "keywords": {"cup", "mug", "ceramic", "pottery", "tea", "vase", "bowl", "plate", "焼物", "陶器", "茶碗", "皿"},
        "product_name": "Japanese ceramic tableware",
        "category_id": "870",
        "low": Decimal("18"),
        "median": Decimal("34"),
        "high": Decimal("68"),
        "aspects": ["Japanese design", "carefully stored", "international shipping from Japan"],
    },
    {
        "keywords": {"camera", "lens", "film", "canon", "nikon", "pentax", "olympus", "カメラ", "レンズ"},
        "product_name": "Japanese vintage camera item",
        "category_id": "3326",
        "low": Decimal("55"),
        "median": Decimal("125"),
        "high": Decimal("260"),
        "aspects": ["popular Japanese camera gear", "collector demand", "tested condition should be stated"],
    },
    {
        "keywords": {"game", "nintendo", "sony", "sega", "switch", "famicom", "ゲーム", "任天堂"},
        "product_name": "Japanese video game collectible",
        "category_id": "139973",
        "low": Decimal("22"),
        "median": Decimal("58"),
        "high": Decimal("140"),
        "aspects": ["Japanese edition", "collector friendly", "region compatibility should be stated"],
    },
]

DEFAULT_PROFILE = {
    "product_name": "Japanese collectible item",
    "category_id": "1",
    "low": Decimal("20"),
    "median": Decimal("45"),
    "high": Decimal("95"),
    "aspects": ["sourced in Japan", "simple international listing", "condition should be checked from photos"],
}


@dataclass(frozen=True)
class MarketResearchResult:
    product_name: str
    keywords: list[str]
    category_id: str
    market_low_usd: Decimal
    market_median_usd: Decimal
    market_high_usd: Decimal
    suggested_price_usd: Decimal
    condition: ListingCondition
    confidence: str
    comparisons: list[dict[str, Any]]
    japanese_description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_name": self.product_name,
            "keywords": self.keywords,
            "category_id": self.category_id,
            "market_low_usd": str(self.market_low_usd),
            "market_median_usd": str(self.market_median_usd),
            "market_high_usd": str(self.market_high_usd),
            "suggested_price_usd": str(self.suggested_price_usd),
            "condition": self.condition.value,
            "confidence": self.confidence,
            "comparisons": self.comparisons,
            "japanese_description": self.japanese_description,
        }


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _tokens(text: str) -> set[str]:
    return {part.lower() for part in Path(text).stem.replace("_", "-").replace(" ", "-").split("-") if part}


def _select_profile(filename: str, user_hint: str) -> tuple[dict[str, Any], list[str]]:
    tokens = _tokens(filename) | _tokens(user_hint)
    for profile in CATEGORY_PROFILES:
        if tokens & profile["keywords"]:
            keywords = sorted(tokens | set(profile["keywords"]))[:8]
            return profile, keywords
    return DEFAULT_PROFILE, sorted(tokens or {"japan", "collectible"})[:8]


def _normalize_condition(condition: ListingCondition | str) -> ListingCondition:
    if isinstance(condition, ListingCondition):
        return condition
    return ListingCondition(str(condition))


def suggest_price(market_median_usd: Decimal | str, condition: ListingCondition | str) -> Decimal:
    normalized_condition = _normalize_condition(condition)
    median = Decimal(str(market_median_usd))
    return _money(median * CONDITION_MULTIPLIERS[normalized_condition])


def build_japanese_description(product_name: str, condition: ListingCondition | str, aspects: list[str]) -> str:
    normalized_condition = _normalize_condition(condition)
    condition_label = CONDITION_LABELS_JA[normalized_condition]
    aspect_text = "、".join(aspects[:3])
    return (
        f"日本で保管されていた {product_name} です。状態は「{condition_label}」として出品予定です。"
        f"特徴は {aspect_text} です。写真に写っているものがすべてです。"
        "海外のお客様にも分かりやすいよう、サイズ・重さ・キズや汚れの有無を確認してから購入してください。"
    )


def analyze_product_image(filename: str, user_hint: str = "", condition: ListingCondition | str = ListingCondition.USED_GOOD) -> MarketResearchResult:
    normalized_condition = _normalize_condition(condition)
    profile, keywords = _select_profile(filename, user_hint)
    low = _money(profile["low"])
    median = _money(profile["median"])
    high = _money(profile["high"])
    suggested = suggest_price(median, normalized_condition)
    comparisons = [
        {"title": f"Sold example - {profile['product_name']}", "price_usd": str(low), "source": "dry-run estimate"},
        {"title": f"Active listing - {profile['product_name']}", "price_usd": str(median), "source": "dry-run estimate"},
        {"title": f"Premium condition - {profile['product_name']}", "price_usd": str(high), "source": "dry-run estimate"},
    ]
    description = build_japanese_description(profile["product_name"], normalized_condition, profile["aspects"])
    return MarketResearchResult(
        product_name=profile["product_name"],
        keywords=keywords,
        category_id=profile["category_id"],
        market_low_usd=low,
        market_median_usd=median,
        market_high_usd=high,
        suggested_price_usd=suggested,
        condition=normalized_condition,
        confidence="medium" if profile is not DEFAULT_PROFILE else "low",
        comparisons=comparisons,
        japanese_description=description,
    )


TRANSLATION_REPLACEMENTS = {
    "日本で保管されていた": "This item was stored in Japan:",
    "状態は": "Condition:",
    "として出品予定です": "for this listing.",
    "特徴は": "Highlights:",
    "写真に写っているものがすべてです": "Only the items shown in the photos are included",
    "海外のお客様にも分かりやすいよう": "For international buyers",
    "サイズ・重さ・キズや汚れの有無を確認してから購入してください": "please review the size, weight, and any scratches or stains before purchase",
    "新品": "New",
    "未使用に近い": "Like new",
    "中古・非常に良い": "Used - excellent",
    "中古・良い": "Used - good",
    "中古・可": "Used - acceptable",
}


def translate_description_to_english(japanese_text: str) -> str:
    translated = japanese_text.strip()
    for japanese, english in TRANSLATION_REPLACEMENTS.items():
        translated = translated.replace(japanese, english)
    return translated
