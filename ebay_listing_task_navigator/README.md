# eBay Listing Task Navigator

`eBay Listing Task Navigator` は、eBay APIを使わずに、eBayの手作業出品を支援するローカルGUIアプリです。

ユーザーは基本的に次の4つだけを入力します。

1. 商品画像
2. 商品説明
3. サイズ（縦・横・高さ）
4. 重量

アプリは説明文とサイズ・重量からルールベースで以下を推定し、出品前から発送完了までの行動チェックリストを公式リンク付きで表示します。

- 商品カテゴリ
- 商品状態
- 壊れやすさ
- 規制リスク
- 返品リスク
- 追加撮影すべき箇所
- eBay説明文の注意点
- 推奨配送方法
- 推奨梱包
- 英語タイトル案
- 英語説明文案
- Condition description
- バイヤー注意文

> 注意: 推定結果は必ず「推定」「要確認」として扱ってください。送料・規制・禁止商品・手数料は変更される可能性があります。

## 重要な制約

このアプリは、以下を行いません。

- eBay API操作
- eBayへの自動出品
- 自動ログイン
- ログイン代行
- スクレイピング依存の情報取得
- 有料APIの利用

最終確認は必ずeBay、日本郵便、FedEx、DHL、UPSなどの公式ページで行ってください。

## 動作環境

- macOS Ventura 13.4 以降を想定
- Windows 10 / 11 のローカル実行にも対応
- Python 3.13 対応
- Streamlit
- ローカル実行
- JSON保存

## 作成済みファイルをまとめてローカルへダウンロードする方法

このアプリは `ebay_listing_task_navigator/` フォルダ一式を自分のPCに置いて使います。必要なのは、`app.py` だけではなく、`modules/`、`knowledge/`、`data/`、`requirements.txt`、`run_windows.bat` を含むフォルダ全体です。

### GitHub画面からZIPでダウンロードする場合

1. GitHubでこのリポジトリまたはプルリクエストのブランチを開きます。
2. 緑色の **Code** ボタンを押します。
3. **Download ZIP** を押します。
4. ダウンロードしたZIPを展開します。
5. 展開したフォルダの中にある `ebay_listing_task_navigator/` を、デスクトップやドキュメントなど好きな場所へ移動します。
6. Windowsなら `ebay_listing_task_navigator\run_windows.bat` をダブルクリック、macOSならターミナルで `streamlit run app.py` を実行します。

### Gitを使ってダウンロードする場合

Gitが使える場合は、ターミナル / PowerShellでリポジトリをクローンしてからアプリフォルダへ移動します。

```bash
git clone <このリポジトリのURL>
cd <リポジトリ名>/ebay_listing_task_navigator
```

その後、Windowsなら `run_windows.bat`、macOS / Linuxなら下のセットアップ手順で起動してください。

### すでにリポジトリを持っていてZIPを作りたい場合

開発環境上でフォルダをZIP化したい場合は、リポジトリのルートで次を実行します。

macOS / Linux:

```bash
zip -r ebay_listing_task_navigator.zip ebay_listing_task_navigator -x "*/.venv/*" "*/__pycache__/*"
```

Windows PowerShell:

```powershell
Compress-Archive -Path ebay_listing_task_navigator -DestinationPath ebay_listing_task_navigator.zip -Force
```

作成された `ebay_listing_task_navigator.zip` を自分のPCで展開すれば、アプリ一式をまとめて配置できます。

## セットアップ方法

### macOS / Linux / VSCode Terminal

ターミナルまたはVSCodeのターミナルで、以下をコピペしてください。

```bash
cd ebay_listing_task_navigator
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Python 3.13 のコマンド名が `python3` の場合は、次のようにしてください。

```bash
cd ebay_listing_task_navigator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### Windows 10 / 11: ダブルクリックで起動する方法

Windowsでは、`ebay_listing_task_navigator` フォルダ内の `run_windows.bat` をダブルクリックすると、仮想環境作成、依存ライブラリインストール、Streamlit起動までを順番に実行できます。

初回起動時はインターネット接続が必要です。2回目以降は作成済みの `.venv` を再利用します。

```text
ebay_listing_task_navigator\run_windows.bat
```

起動後、ブラウザで `http://localhost:8501` が開きます。止めるときは、黒いコマンドプロンプト画面で `Ctrl + C` を押してください。

### Windows 10 / 11: PowerShellで手動起動する方法

PowerShellを開き、プロジェクトの場所に合わせて `cd` した後、以下を実行してください。

```powershell
cd ebay_listing_task_navigator
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

もしPowerShellでスクリプト実行が制限される場合は、次のどちらかで起動してください。

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

または、コマンドプロンプトで次を実行します。

```bat
cd ebay_listing_task_navigator
py -3.13 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## 使い方

1. ブラウザで `http://localhost:8501` を開きます。Windowsで自動的に開かない場合は、このURLをChrome / Edgeに貼り付けてください。
2. 左サイドバーで「新規案件」を開きます。
3. 商品画像、商品説明、サイズ、重量を入力します。
4. 必要に応じて発送先国、仕入れ価格、希望利益、想定販売価格などを入力します。
5. 「タスク生成」を押します。
6. 推定結果、リスク警告、配送候補、公式リンク付きタスクを確認します。
7. チェックボックスで進捗管理します。
8. Markdown、JSON、印刷用HTMLを必要に応じて保存します。

## ナレッジ更新方法

左サイドバーの「ナレッジ更新」を開き、「ナレッジ更新」ボタンを押してください。

このMVPではスクレイピングを行わず、登録済み公式URLの確認日 `last_checked` を更新し、以下の項目をJSONへ保存します。

- `source_name`
- `source_url`
- `summary`
- `check_points`
- `last_checked`
- `confidence`
- `warning`

30日以上更新確認していない情報がある場合、アプリ上に次の警告を表示します。

> この情報は30日以上更新確認されていません。必ず公式ページを確認してください

## JSON編集方法

ナレッジは `knowledge/` に保存されています。

```text
knowledge/
  ebay_policies.json
  shipping_carriers.json
  prohibited_items.json
  category_rules.json
  task_templates.json
  source_links.json
  update_log.json
```

編集例:

- 公式リンクを追加する: `knowledge/source_links.json`
- カテゴリ推定キーワードを追加する: `knowledge/category_rules.json`
- 禁制品・規制リスクキーワードを追加する: `knowledge/prohibited_items.json`
- タスク項目を追加する: `knowledge/task_templates.json`

JSONを編集した後は、Streamlit画面を再読み込みしてください。

## 保存データ

案件は `data/listings.json` に保存されます。

保存内容:

- 商品情報
- タスクリスト
- チェック状態
- メモ
- 作成日
- 更新日

初期状態で「中古フィギュアを米国向けに出品する」サンプル案件を同梱しています。

## 出力機能

生成結果はアプリ画面から以下の形式で出力できます。

- Markdown
- JSON
- 印刷用HTML

## ディレクトリ構成

```text
ebay_listing_task_navigator/
  app.py
  run_windows.bat
  requirements.txt
  README.md

  uploads/
  exports/

  data/
    listings.json

  knowledge/
    ebay_policies.json
    shipping_carriers.json
    prohibited_items.json
    category_rules.json
    task_templates.json
    source_links.json
    update_log.json

  modules/
    product_parser.py
    task_generator.py
    risk_checker.py
    shipping_advisor.py
    profit_calculator.py
    knowledge_manager.py
    exporter.py
```

## 注意事項

このアプリはeBay出品作業を支援するチェックリスト生成ツールです。

eBayへの自動出品、API操作、ログイン代行は行いません。

送料・規制・禁止商品・手数料は変更される可能性があるため、最終確認は必ず公式ページで行ってください。
