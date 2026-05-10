from decimal import Decimal

import asyncio

from app.config import Settings
from app.ebay.client import run_listing_workflow
from app.models import ListingForm


def sample_form() -> ListingForm:
    return ListingForm(
        sku="JP SAMPLE 001",
        title="Vintage Japanese Ceramic Cup",
        description="Carefully stored in Japan and ready to ship internationally.",
        category_id="870",
        price_usd=Decimal("29.99"),
        quantity=1,
        condition="USED_GOOD",
        image_url="https://example.com/photo.jpg",
        weight_kg=Decimal("0.5"),
        length_cm=Decimal("20"),
        width_cm=Decimal("15"),
        height_cm=Decimal("10"),
        shipping_cost_usd=Decimal("18.00"),
    )


def test_dry_run_builds_inventory_offer_and_publish_steps() -> None:
    settings = Settings(
        ebay_payment_policy_id="pay-1",
        ebay_fulfillment_policy_id="ship-1",
        ebay_return_policy_id="return-1",
    )
    result = asyncio.run(run_listing_workflow(sample_form(), settings, access_token=None, dry_run=True))

    assert result.dry_run is True
    assert result.offer_id == "DRY-RUN-OFFER"
    assert result.listing_id == "DRY-RUN-LISTING"
    assert [step["name"] for step in result.steps] == ["在庫データ作成", "出品オファー作成", "出品公開"]
    assert result.steps[0]["payload"]["product"]["title"] == "Vintage Japanese Ceramic Cup"
    assert result.steps[1]["payload"]["listingPolicies"]["paymentPolicyId"] == "pay-1"


def test_sku_is_normalized_for_ebay_inventory_key() -> None:
    assert sample_form().sku == "JP-SAMPLE-001"
