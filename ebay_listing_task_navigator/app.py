from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st

from modules.exporter import to_json, to_markdown, to_print_html
from modules.knowledge_manager import load_knowledge, load_listings, mark_sources_checked, save_listing, source_map, stale_sources
from modules.product_parser import parse_product
from modules.profit_calculator import calculate_profit
from modules.risk_checker import check_risks
from modules.shipping_advisor import recommend_shipping
from modules.task_generator import generate_tasks

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
EXPORT_DIR = BASE_DIR / "exports"
UPLOAD_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="eBay Listing Task Navigator", page_icon="🧭", layout="wide")

NOTICE = """
このアプリはeBay出品作業を支援するチェックリスト生成ツールです。

eBayへの自動出品、API操作、ログイン代行は行いません。

送料・規制・禁止商品・手数料は変更される可能性があるため、最終確認は必ず公式ページで行ってください。
"""


def render_sources(source_keys: list[str], sources: dict[str, dict]) -> None:
    for key in source_keys:
        source = sources.get(key, {})
        if source:
            st.markdown(f"- [{source.get('source_name')}]({source.get('source_url')}) — {source.get('summary')}")


def build_listing(form: dict, knowledge: dict) -> dict:
    parsed = parse_product(form["description"], knowledge)
    risks = check_risks(form["description"], parsed, knowledge)
    tasks = generate_tasks(parsed, risks, knowledge)
    shipping = recommend_shipping(form["dimensions_cm"], form["weight_g"], parsed, form.get("sale_price_jpy", 0))
    profit = calculate_profit(
        form.get("cost_jpy", 0),
        form.get("sale_price_jpy", 0),
        form.get("shipping_jpy", 0),
        form.get("materials_jpy", 0),
        form.get("fee_rate_percent", 13.25),
        form.get("fx_rate", 150),
        form.get("other_costs_jpy", 0),
    )
    return {
        "id": form.get("id") or str(uuid4()),
        "name": form.get("name") or f"Listing {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "product": form,
        "parsed": parsed,
        "risks": risks,
        "shipping_recommendations": shipping,
        "profit": profit,
        "tasks": tasks,
        "notes": form.get("notes", ""),
    }


def save_uploads(uploaded_files) -> list[str]:
    paths = []
    for uploaded_file in uploaded_files or []:
        safe_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
        path = UPLOAD_DIR / safe_name
        with path.open("wb") as file:
            shutil.copyfileobj(uploaded_file, file)
        paths.append(str(path.relative_to(BASE_DIR)))
    return paths


def render_listing(listing: dict, knowledge: dict) -> None:
    sources = source_map(knowledge)
    parsed = listing.get("parsed", {})
    st.subheader("推定結果（推定・要確認）")
    cols = st.columns(5)
    cols[0].metric("カテゴリ", parsed.get("category", ""))
    cols[1].metric("状態", parsed.get("condition", ""))
    cols[2].metric("壊れやすさ", parsed.get("fragility", ""))
    cols[3].metric("規制リスク", parsed.get("regulatory_risk", ""))
    cols[4].metric("返品リスク", parsed.get("return_risk", ""))

    if listing.get("risks"):
        st.subheader("リスク警告")
        for risk in listing["risks"]:
            st.warning(f"{risk['title']} — {risk['message']}")

    st.subheader("英文生成")
    st.text_input("English title", parsed.get("english_title", ""))
    st.text_area("English description", parsed.get("english_description", ""), height=120)
    st.text_area("Condition description", parsed.get("condition_description", ""), height=80)
    st.text_area("Buyer notice", parsed.get("buyer_notice", ""), height=80)

    st.subheader("配送候補")
    for rec in listing.get("shipping_recommendations", []):
        with st.expander(f"{rec['carrier']} — {rec['reason']}", expanded=True):
            render_sources(rec.get("source_keys", []), sources)

    st.subheader("価格計算")
    profit = listing.get("profit", {})
    pcols = st.columns(4)
    pcols[0].metric("eBay手数料 推定", f"¥{profit.get('fees_jpy', 0):,.0f}")
    pcols[1].metric("総費用", f"¥{profit.get('total_cost_jpy', 0):,.0f}")
    pcols[2].metric("利益", f"¥{profit.get('profit_jpy', 0):,.0f}")
    pcols[3].metric("利益率", f"{profit.get('profit_margin_percent', 0):.1f}%")

    st.subheader("タスクリスト")
    for section in listing.get("tasks", []):
        with st.expander(section.get("name", "Task"), expanded=True):
            for task in section.get("tasks", []):
                checked = st.checkbox(task.get("label"), value=task.get("status", False), key=f"task-{listing['id']}-{task['id']}")
                task["status"] = checked
                st.caption(f"公式確認リンク: [{task.get('source_name')}]({task.get('official_link')}) / {task.get('warning')}")

    st.subheader("出力")
    markdown = to_markdown(listing)
    json_text = to_json(listing)
    html_text = to_print_html(listing)
    tabs = st.tabs(["Markdown", "JSON", "印刷用HTML"])
    tabs[0].text_area("Markdown", markdown, height=260)
    tabs[1].text_area("JSON", json_text, height=260)
    tabs[2].text_area("HTML", html_text, height=260)
    st.download_button("Markdownをダウンロード", markdown, file_name="listing_tasks.md")
    st.download_button("JSONをダウンロード", json_text, file_name="listing_tasks.json")
    st.download_button("印刷用HTMLをダウンロード", html_text, file_name="listing_tasks.html", mime="text/html")


knowledge = load_knowledge()
st.title("🧭 eBay Listing Task Navigator")
st.info(NOTICE)

stale = stale_sources(knowledge)
if stale:
    st.warning("この情報は30日以上更新確認されていません。必ず公式ページを確認してください")

page = st.sidebar.radio("メニュー", ["新規案件", "保存済み案件", "ナレッジ更新", "リンク集", "設定"])
st.sidebar.caption("eBay API不使用・自動出品なし・ローカル保存")

if page == "新規案件":
    st.header("新規案件")
    with st.form("listing_form"):
        name = st.text_input("案件名", "")
        uploaded_files = st.file_uploader("商品画像（必須）", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
        description = st.text_area("商品説明（必須）", "中古の日本製フィギュア、箱あり、少し傷あり", height=100)
        c1, c2, c3, c4 = st.columns(4)
        length = c1.number_input("縦 cm", min_value=0.1, value=22.0)
        width = c2.number_input("横 cm", min_value=0.1, value=15.0)
        height = c3.number_input("高さ cm", min_value=0.1, value=30.0)
        weight_g = c4.number_input("重量 g", min_value=1.0, value=850.0)
        destination = st.text_input("発送先国（任意・未入力時USA）", "USA")
        with st.expander("任意: 利益計算"):
            pc1, pc2, pc3 = st.columns(3)
            cost_jpy = pc1.number_input("仕入れ価格 円", min_value=0.0, value=3000.0)
            desired_profit = pc2.number_input("希望利益 円", min_value=0.0, value=2000.0)
            sale_price_jpy = pc3.number_input("想定販売価格 円", min_value=0.0, value=9800.0)
            pc4, pc5, pc6 = st.columns(3)
            shipping_jpy = pc4.number_input("想定送料 円", min_value=0.0, value=2500.0)
            materials_jpy = pc5.number_input("梱包資材費 円", min_value=0.0, value=300.0)
            fee_rate = pc6.number_input("eBay手数料率 %", min_value=0.0, value=13.25)
            pc7, pc8 = st.columns(2)
            fx_rate = pc7.number_input("為替レート（円/USD）", min_value=1.0, value=150.0)
            other_costs = pc8.number_input("その他費用 円", min_value=0.0, value=0.0)
        notes = st.text_area("メモ", "")
        submitted = st.form_submit_button("タスク生成")
    if submitted:
        image_paths = save_uploads(uploaded_files)
        form = {
            "name": name,
            "description": description,
            "destination_country": destination or "USA",
            "dimensions_cm": {"length": length, "width": width, "height": height},
            "weight_g": weight_g,
            "image_paths": image_paths,
            "cost_jpy": cost_jpy,
            "desired_profit_jpy": desired_profit,
            "sale_price_jpy": sale_price_jpy,
            "shipping_jpy": shipping_jpy,
            "materials_jpy": materials_jpy,
            "fee_rate_percent": fee_rate,
            "fx_rate": fx_rate,
            "other_costs_jpy": other_costs,
            "notes": notes,
        }
        listing = build_listing(form, knowledge)
        st.session_state["current_listing"] = listing
        save_listing(listing)
        st.success("案件をJSON保存しました。")
    if "current_listing" in st.session_state:
        render_listing(st.session_state["current_listing"], knowledge)

elif page == "保存済み案件":
    st.header("保存済み案件")
    listings = load_listings()
    if not listings:
        st.info("保存済み案件はありません。")
    else:
        selected = st.selectbox("案件を選択", listings, format_func=lambda item: item.get("name", item.get("id")))
        render_listing(selected, knowledge)

elif page == "ナレッジ更新":
    st.header("ナレッジ更新")
    st.write("登録済み公式URLの確認日を更新し、URL・要約・確認項目をJSONへ保存します。スクレイピングには依存しません。")
    if st.button("ナレッジ更新"):
        knowledge = mark_sources_checked(knowledge)
        st.success("ナレッジのlast_checkedを更新しました。")
    for source in knowledge.get("source_links", {}).get("sources", []):
        st.markdown(f"### [{source['source_name']}]({source['source_url']})")
        st.write(source.get("summary"))
        st.caption(f"last_checked: {source.get('last_checked')} / confidence: {source.get('confidence')} / warning: {source.get('warning')}")
        st.write("確認項目:", ", ".join(source.get("check_points", [])))

elif page == "リンク集":
    st.header("公式リンク集")
    for source in knowledge.get("source_links", {}).get("sources", []):
        st.markdown(f"- [{source['source_name']}]({source['source_url']}) — {source.get('summary')}")

else:
    st.header("設定")
    st.write("JSONファイルは `knowledge/` と `data/listings.json` を直接編集できます。")
    st.code(str(BASE_DIR), language="text")
