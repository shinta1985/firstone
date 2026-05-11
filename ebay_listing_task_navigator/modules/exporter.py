from __future__ import annotations

import html
import json
from typing import Any


def to_markdown(listing: dict[str, Any]) -> str:
    product = listing.get("product", {})
    parsed = listing.get("parsed", {})
    lines = [
        f"# {listing.get('name', 'eBay Listing Task Navigator')}",
        "",
        "## 商品情報",
        f"- 説明: {product.get('description', '')}",
        f"- 発送先国: {product.get('destination_country', 'USA')}",
        f"- サイズ: {product.get('dimensions_cm', {})}",
        f"- 重量: {product.get('weight_g', 0)} g",
        "",
        "## 推定結果（推定・要確認）",
        f"- カテゴリ: {parsed.get('category', '')}",
        f"- 状態: {parsed.get('condition', '')}",
        f"- 壊れやすさ: {parsed.get('fragility', '')}",
        f"- 規制リスク: {parsed.get('regulatory_risk', '')}",
        f"- 返品リスク: {parsed.get('return_risk', '')}",
        "",
        "## 英文案",
        f"- Title: {parsed.get('english_title', '')}",
        f"- Description: {parsed.get('english_description', '')}",
        f"- Condition: {parsed.get('condition_description', '')}",
        f"- Buyer notice: {parsed.get('buyer_notice', '')}",
        "",
        "## タスクリスト",
    ]
    for section in listing.get("tasks", []):
        lines.append(f"### {section.get('name')}")
        for task in section.get("tasks", []):
            checked = "x" if task.get("status") else " "
            lines.append(f"- [{checked}] {task.get('label')} ([{task.get('source_name')}]({task.get('official_link')}))")
        lines.append("")
    return "\n".join(lines)


def to_json(listing: dict[str, Any]) -> str:
    return json.dumps(listing, ensure_ascii=False, indent=2)


def to_print_html(listing: dict[str, Any]) -> str:
    markdown = html.escape(to_markdown(listing))
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>{html.escape(listing.get('name', 'Listing'))}</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,'Hiragino Sans',sans-serif;line-height:1.6;margin:32px}} pre{{white-space:pre-wrap}}</style>
</head><body><pre>{markdown}</pre></body></html>"""
