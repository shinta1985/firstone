from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    ebay_sandbox: bool = True
    ebay_client_id: str = ""
    ebay_client_secret: str = ""
    ebay_redirect_uri: str = "http://localhost:8000/auth/callback"
    ebay_marketplace_id: str = "EBAY_US"
    ebay_locale: str = "en-US"
    ebay_merchant_location_key: str = "jp-home"
    ebay_payment_policy_id: str = ""
    ebay_fulfillment_policy_id: str = ""
    ebay_return_policy_id: str = ""

    @property
    def api_base_url(self) -> str:
        return "https://api.sandbox.ebay.com" if self.ebay_sandbox else "https://api.ebay.com"

    @property
    def auth_base_url(self) -> str:
        return "https://auth.sandbox.ebay.com" if self.ebay_sandbox else "https://auth.ebay.com"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        ebay_sandbox=_bool_env("EBAY_SANDBOX", True),
        ebay_client_id=os.getenv("EBAY_CLIENT_ID", ""),
        ebay_client_secret=os.getenv("EBAY_CLIENT_SECRET", ""),
        ebay_redirect_uri=os.getenv("EBAY_REDIRECT_URI", "http://localhost:8000/auth/callback"),
        ebay_marketplace_id=os.getenv("EBAY_MARKETPLACE_ID", "EBAY_US"),
        ebay_locale=os.getenv("EBAY_LOCALE", "en-US"),
        ebay_merchant_location_key=os.getenv("EBAY_MERCHANT_LOCATION_KEY", "jp-home"),
        ebay_payment_policy_id=os.getenv("EBAY_PAYMENT_POLICY_ID", ""),
        ebay_fulfillment_policy_id=os.getenv("EBAY_FULFILLMENT_POLICY_ID", ""),
        ebay_return_policy_id=os.getenv("EBAY_RETURN_POLICY_ID", ""),
    )
