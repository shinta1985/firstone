from __future__ import annotations

import base64
import secrets
from typing import Any
from urllib.parse import urlencode


from app.config import Settings
from app.models import ListingForm, WorkflowResult

SELL_SCOPES = [
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
    "https://api.ebay.com/oauth/api_scope/sell.account",
]


class EbayClient:
    """Small wrapper around eBay Sell APIs used by the guided workflow."""

    def __init__(self, settings: Settings, access_token: str | None = None) -> None:
        self.settings = settings
        self.access_token = access_token

    def authorization_url(self) -> tuple[str, str]:
        state = secrets.token_urlsafe(24)
        query = urlencode(
            {
                "client_id": self.settings.ebay_client_id,
                "redirect_uri": self.settings.ebay_redirect_uri,
                "response_type": "code",
                "scope": " ".join(SELL_SCOPES),
                "state": state,
            }
        )
        return f"{self.settings.auth_base_url}/oauth2/authorize?{query}", state

    async def exchange_code(self, code: str) -> dict[str, Any]:
        auth = base64.b64encode(
            f"{self.settings.ebay_client_id}:{self.settings.ebay_client_secret}".encode()
        ).decode()
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.settings.api_base_url}/identity/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.settings.ebay_redirect_uri,
                },
            )
        response.raise_for_status()
        return response.json()

    def _headers(self) -> dict[str, str]:
        if not self.access_token:
            raise ValueError("eBay access token is missing. Start OAuth first.")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Content-Language": self.settings.ebay_locale,
        }

    async def put_inventory_item(self, form: ListingForm) -> dict[str, Any]:
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.put(
                f"{self.settings.api_base_url}/sell/inventory/v1/inventory_item/{form.sku}",
                headers=self._headers(),
                json=form.inventory_payload(),
            )
        response.raise_for_status()
        return {"status_code": response.status_code, "body": response.json() if response.content else {}}

    async def create_offer(self, form: ListingForm) -> dict[str, Any]:
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.settings.api_base_url}/sell/inventory/v1/offer",
                headers=self._headers(),
                json=form.offer_payload(self.settings),
            )
        response.raise_for_status()
        return response.json()

    async def publish_offer(self, offer_id: str) -> dict[str, Any]:
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.settings.api_base_url}/sell/inventory/v1/offer/{offer_id}/publish",
                headers=self._headers(),
            )
        response.raise_for_status()
        return response.json()

    async def get_orders(self, limit: int = 10) -> dict[str, Any]:
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.settings.api_base_url}/sell/fulfillment/v1/order",
                headers=self._headers(),
                params={"limit": limit},
            )
        response.raise_for_status()
        return response.json()

    async def create_shipping_fulfillment(
        self,
        order_id: str,
        line_item_id: str,
        carrier_code: str,
        tracking_number: str,
    ) -> dict[str, Any]:
        payload = {
            "lineItems": [{"lineItemId": line_item_id}],
            "shippedDate": None,
            "shippingCarrierCode": carrier_code,
            "trackingNumber": tracking_number.replace(" ", ""),
        }
        payload.pop("shippedDate")
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.settings.api_base_url}/sell/fulfillment/v1/order/{order_id}/shipping_fulfillment",
                headers=self._headers(),
                json=payload,
            )
        response.raise_for_status()
        return response.json() if response.content else {"status_code": response.status_code}


async def run_listing_workflow(
    form: ListingForm,
    settings: Settings,
    access_token: str | None,
    dry_run: bool = True,
) -> WorkflowResult:
    inventory_payload = form.inventory_payload()
    offer_payload = form.offer_payload(settings)

    if dry_run:
        return WorkflowResult(
            dry_run=True,
            offer_id="DRY-RUN-OFFER",
            listing_id="DRY-RUN-LISTING",
            steps=[
                {"name": "在庫データ作成", "method": "PUT", "endpoint": f"/sell/inventory/v1/inventory_item/{form.sku}", "payload": inventory_payload},
                {"name": "出品オファー作成", "method": "POST", "endpoint": "/sell/inventory/v1/offer", "payload": offer_payload},
                {"name": "出品公開", "method": "POST", "endpoint": "/sell/inventory/v1/offer/DRY-RUN-OFFER/publish", "payload": {}},
            ],
        )

    client = EbayClient(settings, access_token)
    inventory = await client.put_inventory_item(form)
    offer = await client.create_offer(form)
    offer_id = offer["offerId"]
    publish = await client.publish_offer(offer_id)
    return WorkflowResult(
        dry_run=False,
        offer_id=offer_id,
        listing_id=publish.get("listingId"),
        steps=[
            {"name": "在庫データ作成", "response": inventory},
            {"name": "出品オファー作成", "response": offer},
            {"name": "出品公開", "response": publish},
        ],
    )
