from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
DATA_DIR = BASE_DIR / "data"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def load_knowledge() -> dict[str, Any]:
    files = [
        "ebay_policies",
        "shipping_carriers",
        "prohibited_items",
        "category_rules",
        "task_templates",
        "source_links",
        "update_log",
    ]
    return {name: load_json(KNOWLEDGE_DIR / f"{name}.json", {}) for name in files}


def source_map(knowledge: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {source["key"]: source for source in knowledge.get("source_links", {}).get("sources", [])}


def stale_sources(knowledge: dict[str, Any], max_age_days: int = 30) -> list[dict[str, Any]]:
    stale: list[dict[str, Any]] = []
    today = date.today()
    for source in knowledge.get("source_links", {}).get("sources", []):
        checked = source.get("last_checked")
        try:
            checked_date = datetime.strptime(checked, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            stale.append(source)
            continue
        if (today - checked_date).days > max_age_days:
            stale.append(source)
    return stale


def mark_sources_checked(knowledge: dict[str, Any]) -> dict[str, Any]:
    today = date.today().isoformat()
    source_links = knowledge.get("source_links", {"sources": []})
    for source in source_links.get("sources", []):
        source["last_checked"] = today
        source["confidence"] = source.get("confidence") or "official-url"
        source["warning"] = source.get("warning") or "公式ページで最新情報を確認してください。"
    save_json(KNOWLEDGE_DIR / "source_links.json", source_links)
    update_log = knowledge.get("update_log", {"updates": []})
    update_log.setdefault("updates", []).append(
        {"date": today, "message": "ナレッジ更新ボタンで公式URLの確認日を更新。スクレイピングは未実施。"}
    )
    save_json(KNOWLEDGE_DIR / "update_log.json", update_log)
    knowledge["source_links"] = source_links
    knowledge["update_log"] = update_log
    return knowledge


def load_listings() -> list[dict[str, Any]]:
    data = load_json(DATA_DIR / "listings.json", {"listings": []})
    return data.get("listings", [])


def save_listing(listing: dict[str, Any]) -> None:
    listings = load_listings()
    now = datetime.now().isoformat(timespec="seconds")
    listing.setdefault("created_at", now)
    listing["updated_at"] = now
    listings = [item for item in listings if item.get("id") != listing.get("id")]
    listings.insert(0, listing)
    save_json(DATA_DIR / "listings.json", {"listings": listings})
