from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any
from urllib.parse import urlparse


class ListingCondition(str, Enum):
    NEW = "NEW"
    LIKE_NEW = "LIKE_NEW"
    USED_EXCELLENT = "USED_EXCELLENT"
    USED_GOOD = "USED_GOOD"
    USED_ACCEPTABLE = "USED_ACCEPTABLE"


@dataclass
class ListingForm:
    sku: str
    title: str
    description: str
    category_id: str
    price_usd: Decimal | str
    quantity: int
    condition: ListingCondition | str
    image_url: str
    weight_kg: Decimal | str
    length_cm: Decimal | str
    width_cm: Decimal | str
    height_cm: Decimal | str
    shipping_cost_usd: Decimal | str

    def __post_init__(self) -> None:
        self.sku = self.sku.strip().replace(" ", "-")
        self.price_usd = Decimal(str(self.price_usd))
        self.weight_kg = Decimal(str(self.weight_kg))
        self.length_cm = Decimal(str(self.length_cm))
        self.width_cm = Decimal(str(self.width_cm))
        self.height_cm = Decimal(str(self.height_cm))
        self.shipping_cost_usd = Decimal(str(self.shipping_cost_usd))
        self.condition = ListingCondition(str(self.condition))
        self._validate()

    def _validate(self) -> None:
        if len(self.sku) < 3 or len(self.sku) > 50:
            raise ValueError("SKU は3〜50文字で入力してください。")
        if len(self.title) < 5 or len(self.title) > 80:
            raise ValueError("タイトルは5〜80文字で入力してください。")
        if len(self.description) < 10:
            raise ValueError("説明は10文字以上で入力してください。")
        if not self.category_id:
            raise ValueError("カテゴリIDを入力してください。")
        for name in ["price_usd", "weight_kg", "length_cm", "width_cm", "height_cm"]:
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} は0より大きい値にしてください。")
        if self.shipping_cost_usd < 0:
            raise ValueError("送料は0以上にしてください。")
        if self.quantity < 1 or self.quantity > 99:
            raise ValueError("数量は1〜99で入力してください。")
        parsed = urlparse(self.image_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("画像URLは http:// または https:// で入力してください。")

    def inventory_payload(self) -> dict[str, Any]:
        return {
            "availability": {"shipToLocationAvailability": {"quantity": self.quantity}},
            "condition": self.condition.value,
            "product": {
                "title": self.title,
                "description": self.description,
                "imageUrls": [self.image_url],
                "aspects": {"Country/Region of Manufacture": ["Japan"]},
            },
            "packageWeightAndSize": {
                "dimensions": {
                    "height": float(self.height_cm),
                    "length": float(self.length_cm),
                    "width": float(self.width_cm),
                    "unit": "CENTIMETER",
                },
                "weight": {"value": float(self.weight_kg), "unit": "KILOGRAM"},
            },
        }

    def offer_payload(self, settings: Any) -> dict[str, Any]:
        return {
            "sku": self.sku,
            "marketplaceId": settings.ebay_marketplace_id,
            "format": "FIXED_PRICE",
            "availableQuantity": self.quantity,
            "categoryId": self.category_id,
            "merchantLocationKey": settings.ebay_merchant_location_key,
            "pricingSummary": {"price": {"value": str(self.price_usd), "currency": "USD"}},
            "listingPolicies": {
                "paymentPolicyId": settings.ebay_payment_policy_id,
                "fulfillmentPolicyId": settings.ebay_fulfillment_policy_id,
                "returnPolicyId": settings.ebay_return_policy_id,
            },
            "shippingCostOverrides": [
                {
                    "shippingServiceType": "DOMESTIC",
                    "priority": 1,
                    "shippingCost": {"value": str(self.shipping_cost_usd), "currency": "USD"},
                }
            ],
        }


@dataclass
class WorkflowResult:
    dry_run: bool
    steps: list[dict[str, Any]]
    listing_id: str | None = None
    offer_id: str | None = None

    def model_dump(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "steps": self.steps,
            "listing_id": self.listing_id,
            "offer_id": self.offer_id,
        }
