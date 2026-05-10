# らくらく eBay 出品アシスタント

日本から eBay に出品する作業を、シンプルな日本語UIで「商品入力 → API送信内容の dry run → Sandbox/本番出品 → 注文確認・発送追跡登録」へつなげるための FastAPI アプリです。

## できること

- eBay OAuth でセラーアカウントにログイン
- eBay Inventory API 用の在庫データを生成
- eBay Inventory API の Offer 作成・Publish までを dry run で確認
- dry run を外すと Sandbox/Production API に送信
- Fulfillment API で注文一覧取得・発送追跡登録を拡張しやすいクライアントを同梱

## eBay API の前提

最新の eBay 公式ドキュメントでは、Inventory API は在庫レコードを作り、それをオファーへ変換して公開する API です。公開時には支払い・発送・返品の business policy が必要です。Fulfillment API は注文取得と発送追跡登録に使います。Logistics API は eBay negotiated rate やラベル作成に使えますが、利用前に eBay アカウント側の支払い方法設定が必要です。

この初期実装では、送料はまず手入力で確実に dry run できる形にしています。次の拡張で Japan Post / DHL / FedEx / eBay Logistics API などの料金APIを追加できます。


## ユーザー側の準備チェックリスト

APIキー、Business Policy ID、商品ごとの入力情報、画面での進め方は [docs/USER_CHECKLIST.md](docs/USER_CHECKLIST.md) にまとめています。まずこのチェックリストを上から埋めてください。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

`.env` に eBay Developer の Client ID / Client Secret / Redirect URI と、eBay Seller Hub で作成した business policy ID を入れます。

```dotenv
EBAY_SANDBOX=true
EBAY_CLIENT_ID=...
EBAY_CLIENT_SECRET=...
EBAY_REDIRECT_URI=http://localhost:8000/auth/callback
EBAY_PAYMENT_POLICY_ID=...
EBAY_FULFILLMENT_POLICY_ID=...
EBAY_RETURN_POLICY_ID=...
```

## 起動

```bash
uvicorn app.main:app --reload
```

ブラウザで <http://localhost:8000> を開きます。

## UIサンプル

画面イメージは [docs/UI_SAMPLE.md](docs/UI_SAMPLE.md) で確認できます。


## 画像リサーチ・説明生成

トップ画面の「画像から商品リサーチ」では、商品画像と任意の補足キーワードを入力すると、商品候補、推定カテゴリ、相場レンジ、状態別の参考価格、eBay向けの日本語概要を表示します。状態プルダウンを変えて参考価格を再計算でき、日本語概要はユーザーが手作業で修正してから「英語に翻訳してプレビュー」できます。

現時点の相場は安全に動作確認できる dry-run 推定値です。実売データの精度を上げる場合は、eBay Browse API / Marketplace Insights API、または外部AI画像認識APIを接続してください。

## 実際の確認手順

1. `EBAY_SANDBOX=true` のまま起動します。
2. eBayログインを押して OAuth を完了します。
3. 商品名、説明、画像URL、カテゴリID、価格、梱包サイズ、送料を入力します。
4. `dry run` にチェックを入れたまま「出品内容を確認」を押し、送信予定の JSON を確認します。
5. Sandbox seller の business policy ID が正しいことを確認します。
6. 問題なければ `dry run` を外して Sandbox に出品します。
7. Sandbox で購入テスト後、`/orders` で注文取得を確認します。
8. 配送会社・追跡番号が決まったら Fulfillment API の `create_shipping_fulfillment` を使って追跡登録します。
9. 現物出品時は `EBAY_SANDBOX=false` に変更し、本番用 business policy ID へ差し替えて同じ手順を実行します。

## 注意

- 本番出品前に必ず Sandbox で dry run と実API実行を確認してください。
- eBay のカテゴリID、出品必須項目、返品条件はカテゴリ・マーケットごとに変わります。
- APIキーや refresh token は `.env` に入れ、Git にコミットしないでください。

## 参考にした公式ドキュメント

- Inventory API overview: https://developer.ebay.com/api-docs/sell/inventory/overview.html
- Create offer: https://developer.ebay.com/api-docs/sell/inventory/resources/offer/methods/createOffer
- Publish offer: https://developer.ebay.com/api-docs/sell/inventory/resources/offer/methods/publishOffer
- Fulfillment API shipping fulfillment: https://developer.ebay.com/api-docs/sell/fulfillment/resources/order/shipping_fulfillment/methods/createShippingFulfillment
- Logistics API overview: https://developer.ebay.com/api-docs/sell/logistics/overview.html
