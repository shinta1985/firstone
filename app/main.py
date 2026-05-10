from __future__ import annotations

import json
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import Settings, get_settings
from app.ebay.client import EbayClient, run_listing_workflow
from app.models import ListingForm

app = FastAPI(title="らくらく eBay 出品アシスタント")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
SESSION: dict[str, str] = {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, settings: Annotated[Settings, Depends(get_settings)]) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "settings": settings,
            "has_token": bool(SESSION.get("access_token")),
            "result": None,
            "error": None,
        },
    )


@app.get("/auth/start")
async def auth_start(settings: Annotated[Settings, Depends(get_settings)]) -> RedirectResponse:
    if not settings.ebay_client_id:
        raise HTTPException(status_code=400, detail="EBAY_CLIENT_ID を .env に設定してください。")
    url, state = EbayClient(settings).authorization_url()
    SESSION["oauth_state"] = state
    return RedirectResponse(url)


@app.get("/auth/callback")
async def auth_callback(
    code: str,
    state: str,
    settings: Annotated[Settings, Depends(get_settings)],
) -> RedirectResponse:
    if state != SESSION.get("oauth_state"):
        raise HTTPException(status_code=400, detail="OAuth state が一致しません。")
    token = await EbayClient(settings).exchange_code(code)
    SESSION["access_token"] = token["access_token"]
    if refresh_token := token.get("refresh_token"):
        SESSION["refresh_token"] = refresh_token
    return RedirectResponse("/")


@app.post("/listings/preview", response_class=HTMLResponse)
async def preview_listing(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    sku: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    category_id: str = Form(...),
    price_usd: str = Form(...),
    quantity: int = Form(...),
    condition: str = Form(...),
    image_url: str = Form(...),
    weight_kg: str = Form(...),
    length_cm: str = Form(...),
    width_cm: str = Form(...),
    height_cm: str = Form(...),
    shipping_cost_usd: str = Form(...),
    dry_run: bool = Form(True),
) -> HTMLResponse:
    try:
        form = ListingForm(
            sku=sku,
            title=title,
            description=description,
            category_id=category_id,
            price_usd=price_usd,
            quantity=quantity,
            condition=condition,
            image_url=image_url,
            weight_kg=weight_kg,
            length_cm=length_cm,
            width_cm=width_cm,
            height_cm=height_cm,
            shipping_cost_usd=shipping_cost_usd,
        )
        if not dry_run and not SESSION.get("access_token"):
            raise ValueError("本番/Sandbox API実行には eBay ログインが必要です。")
        result = await run_listing_workflow(form, settings, SESSION.get("access_token"), dry_run=dry_run)
        pretty_result = json.dumps(result.model_dump(), ensure_ascii=False, indent=2, default=str)
        error = None
    except ValueError as exc:
        pretty_result = None
        error = str(exc)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "settings": settings,
            "has_token": bool(SESSION.get("access_token")),
            "result": pretty_result,
            "error": error,
        },
    )


@app.get("/orders", response_class=HTMLResponse)
async def orders(request: Request, settings: Annotated[Settings, Depends(get_settings)]) -> HTMLResponse:
    if not SESSION.get("access_token"):
        return templates.TemplateResponse(
            "orders.html",
            {"request": request, "orders": None, "error": "先に eBay ログインしてください。"},
        )
    try:
        orders_payload = await EbayClient(settings, SESSION["access_token"]).get_orders()
        error = None
    except Exception as exc:  # APIエラーを画面で確認できるようにする
        orders_payload = None
        error = str(exc)
    return templates.TemplateResponse(
        "orders.html",
        {"request": request, "orders": orders_payload, "error": error},
    )


@app.post("/shipments/create", response_class=HTMLResponse)
async def create_shipment_tracking(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    order_id: str = Form(...),
    line_item_id: str = Form(...),
    carrier_code: str = Form(...),
    tracking_number: str = Form(...),
    dry_run: bool = Form(True),
) -> HTMLResponse:
    payload = {
        "order_id": order_id,
        "line_item_id": line_item_id,
        "carrier_code": carrier_code,
        "tracking_number": tracking_number.replace(" ", ""),
    }
    if dry_run:
        result = {"dry_run": True, "endpoint": f"/sell/fulfillment/v1/order/{order_id}/shipping_fulfillment", "payload": payload}
        return templates.TemplateResponse("orders.html", {"request": request, "orders": result, "error": None})
    if not SESSION.get("access_token"):
        return templates.TemplateResponse("orders.html", {"request": request, "orders": None, "error": "先に eBay ログインしてください。"})
    try:
        result = await EbayClient(settings, SESSION["access_token"]).create_shipping_fulfillment(
            order_id=order_id,
            line_item_id=line_item_id,
            carrier_code=carrier_code,
            tracking_number=tracking_number,
        )
        error = None
    except Exception as exc:  # APIエラーを画面で確認できるようにする
        result = None
        error = str(exc)
    return templates.TemplateResponse("orders.html", {"request": request, "orders": result, "error": error})
