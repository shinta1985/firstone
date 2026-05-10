# ユーザー側でやる作業・そろえる情報チェックリスト

このページは、eBay出品アシスタントを「迷わず最後まで進める」ための準備リストです。上から順番に埋めれば、Sandbox dry run → Sandbox実出品 → 本番出品へ進めます。

## 0. 先に決めること

| 決めること | おすすめ | メモ |
|---|---|---|
| 最初に使う環境 | `Sandbox` | 本番出品前に必ずテストします |
| 出品先マーケット | `EBAY_US` | 日本から海外向けに売る初期設定として扱います |
| 価格通貨 | `USD` | 画面とAPI payloadはUSD前提です |
| 送料 | まず手入力 | 後で配送会社APIやeBay Logisticsへ拡張します |

## 1. アカウント準備

- [ ] eBay販売用アカウントにログインできる。
- [ ] eBay Developer Programアカウントにログインできる。
- [ ] eBay Seller Hubで販売者情報、支払い受取、本人確認など販売に必要な基本設定が完了している。
- [ ] 2段階認証を自分で操作できる端末を手元に置いている。

> パスワード、2段階認証コード、Client Secret、refresh tokenはチャットやGitに貼らないでください。

## 2. eBay Developer Portalでそろえる情報

`.env` に入れるため、以下をメモします。

| 必要情報 | `.env` の項目 | どこで取るか | 必須 |
|---|---|---|---|
| Client ID / App ID | `EBAY_CLIENT_ID` | Developer PortalのApplication Keys | 必須 |
| Client Secret / Cert ID | `EBAY_CLIENT_SECRET` | Developer PortalのApplication Keys | 必須 |
| Redirect URI / RuName | `EBAY_REDIRECT_URI` | OAuth設定 | 必須 |
| Sandboxか本番か | `EBAY_SANDBOX` | 自分で決める | 必須 |
| Marketplace ID | `EBAY_MARKETPLACE_ID` | 初期は `EBAY_US` | 必須 |

## 3. eBay Seller Hub / Account APIでそろえるBusiness Policy ID

Inventory APIでOfferを作るには、出品に使うbusiness policy IDが必要です。最低限、以下3つを用意します。

| Policy | `.env` の項目 | 例 |
|---|---|---|
| Payment policy ID | `EBAY_PAYMENT_POLICY_ID` | 支払い条件 |
| Fulfillment policy ID | `EBAY_FULFILLMENT_POLICY_ID` | 発送方法・発送除外国・ハンドリング日数 |
| Return policy ID | `EBAY_RETURN_POLICY_ID` | 返品可否・返品期間 |

チェック:

- [ ] Payment policyを1つ作った。
- [ ] Fulfillment policyを1つ作った。
- [ ] Return policyを1つ作った。
- [ ] 3つのpolicy IDを控えた。
- [ ] Sandbox用と本番用を混ぜていない。

## 4. 商品ごとにそろえる情報

画像リサーチで一部を補助できますが、最終確認はユーザーが行います。

| 情報 | 必須 | 例 |
|---|---|---|
| 商品写真 | 必須 | 正面、裏面、キズ、付属品 |
| SKU | 必須 | `JP-CUP-001` |
| 商品名候補 | 必須 | `Vintage Japanese Ceramic Cup` |
| カテゴリID | 必須 | 陶器なら候補 `870` など |
| 状態 | 必須 | 新品 / 未使用に近い / 中古・非常に良い / 中古・良い / 中古・可 |
| 価格 | 必須 | 参考価格を見て最終決定 |
| 梱包後の重さ | 必須 | `0.5 kg` |
| 梱包サイズ | 必須 | 縦・横・高さ cm |
| 送料 | 必須 | `18.00 USD` |
| 付属品 | 推奨 | 箱、説明書、ケーブルなど |
| 傷・汚れ | 推奨 | 写真と説明文に書く |

## 5. ローカルアプリの設定手順

```bash
cp .env.example .env
```

`.env` を編集します。

```dotenv
EBAY_SANDBOX=true
EBAY_CLIENT_ID=your-client-id
EBAY_CLIENT_SECRET=your-client-secret
EBAY_REDIRECT_URI=http://localhost:8000/auth/callback
EBAY_MARKETPLACE_ID=EBAY_US
EBAY_PAYMENT_POLICY_ID=your-payment-policy-id
EBAY_FULFILLMENT_POLICY_ID=your-fulfillment-policy-id
EBAY_RETURN_POLICY_ID=your-return-policy-id
```

起動します。

```bash
uvicorn app.main:app --reload
```

ブラウザで開きます。

```text
http://localhost:8000
```

## 6. 画面での一番簡単な進め方

1. まず `EBAY_SANDBOX=true` にします。
2. 画面右上の **eBayログイン** を押します。
3. 自分のeBay画面で同意します。
4. **画像から商品リサーチ** に商品画像をアップロードします。
5. 必要なら補足キーワードを入れます。例: `ceramic cup`, `Nintendo`, `camera lens`
6. 状態プルダウンを選びます。
7. 表示された相場レンジと参考価格を確認します。
8. 自動生成された日本語概要を手で直します。
9. **英語に翻訳してプレビュー** を押します。
10. 英語説明を出品フォームへ貼ります。
11. 価格、カテゴリID、重さ、サイズ、送料を入力します。
12. **dry run** にチェックを入れたまま「出品内容を確認」を押します。
13. JSONに問題がなければ、Sandboxでdry runを外して出品します。
14. Sandboxで購入テストできたら `/orders` で注文を確認します。
15. 追跡番号をdry runで確認してから発送登録します。
16. 最後に `EBAY_SANDBOX=false` と本番policy IDへ切り替え、本番でも同じ手順を行います。

## 7. 完了条件

- [ ] SandboxのOAuthログインが成功した。
- [ ] 画像リサーチで商品概要と参考価格を確認できた。
- [ ] 日本語概要を修正し、英語プレビューを確認できた。
- [ ] dry runでInventory / Offer / PublishのJSONを確認できた。
- [ ] Sandboxへ実際に出品できた。
- [ ] Sandbox注文を取得できた。
- [ ] 発送追跡登録のdry runを確認できた。
- [ ] 現物で本番出品前の最終確認ができた。

## 8. 困った時に確認する場所

- APIキーがない: Developer PortalのApplication Keysを確認。
- OAuthで戻れない: Redirect URI / RuNameが `.env` とDeveloper Portalで一致しているか確認。
- Offer作成で失敗: Payment / Fulfillment / Return policy IDを確認。
- 送料が不安: まず手入力で高めに見積もり、後で配送会社API連携を追加。
- カテゴリが不安: eBay画面で類似商品のカテゴリを確認してから入力。
