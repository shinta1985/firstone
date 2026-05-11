from __future__ import annotations

from typing import Any

from modules.knowledge_manager import source_map


def generate_tasks(parsed: dict[str, Any], risks: list[dict[str, str]], knowledge: dict[str, Any]) -> list[dict[str, Any]]:
    sources = source_map(knowledge)
    sections: list[dict[str, Any]] = []
    for section in knowledge.get("task_templates", {}).get("sections", []):
        tasks = []
        for index, item in enumerate(section.get("items", []), start=1):
            source = sources.get(item.get("source_key"), {})
            tasks.append({
                "id": f"{section['name']}-{index}",
                "label": item.get("label"),
                "status": False,
                "official_link": source.get("source_url", ""),
                "source_name": source.get("source_name", "公式確認リンク"),
                "warning": source.get("warning", "必ず公式ページを確認してください。"),
            })
        if section.get("name") == "写真撮影":
            for point in parsed.get("photo_points", []):
                tasks.append({
                    "id": f"写真撮影-extra-{point}",
                    "label": f"追加撮影: {point}",
                    "status": False,
                    "official_link": sources.get("ebay_seller_hub_help", {}).get("source_url", ""),
                    "source_name": "eBay Seller Hub Help",
                    "warning": "推定された追加撮影ポイントです。要確認。",
                })
        sections.append({"name": section.get("name"), "tasks": tasks})
    if risks:
        risk_tasks = []
        for index, risk in enumerate(risks, start=1):
            source = sources.get(risk.get("source_key"), {})
            risk_tasks.append({
                "id": f"risk-{index}",
                "label": risk.get("message"),
                "status": False,
                "official_link": source.get("source_url", ""),
                "source_name": source.get("source_name", "公式確認リンク"),
                "warning": risk.get("title", "要確認"),
            })
        sections.insert(0, {"name": "リスク確認", "tasks": risk_tasks})
    return sections
