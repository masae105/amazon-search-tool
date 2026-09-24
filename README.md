# 商品検索・価格監視ツール

## 概要

FlaskとPostgreSQLを使用した商品検索・価格監視Webアプリです。
楽天市場APIで商品を検索し、検索履歴と商品価格履歴を保存します。
監視キーワードを登録し、新商品や値下げ商品を通知条件に応じてSlackへ通知します。
Cloud Run、Cloud SQL、Cloud Schedulerを利用して定期監視できます。

## 主な機能

- 商品キーワード検索
- 複数キーワード検索
- 検索履歴の保存・表示
- 検索履歴からの再検索
- 検索履歴の削除
- 監視キーワードの登録
- 監視キーワードの有効/無効切替
- 監視処理の手動実行
- 新商品の検出
- 値下げ商品の検出
- 最低値下げ額の設定
- 最低値下げ率の設定
- 変化なし通知の設定
- Slack通知
- 商品価格履歴の保存
- Cloud Runでの運用
- Cloud SQL(PostgreSQL)との接続
- Cloud Schedulerによる定期監視
- Cloud Loggingによる監視ログ・エラーログ確認

## 通知設定

監視画面では以下の設定を変更できます。

- `notify_new_items`: 新商品をSlack通知するかどうか
- `notify_price_drops`: 値下げ商品をSlack通知するかどうか
- `notify_no_change`: 新商品・値下げ商品の通知対象がなくてもSlack通知するかどうか
- `min_price_drop_amount`: 通知対象とする最低値下げ額
- `min_price_drop_percent`: 通知対象とする最低値下げ率

`notify_new_items` が `false` の場合、新商品はSlack通知の対象から除外されます。
`notify_price_drops` が `false` の場合、値下げ商品はSlack通知の対象から除外されます。

最低値下げ額と最低値下げ率がどちらも0より大きい場合は、値下げ額と値下げ率の両方の条件を満たした商品だけが通知対象になります。どちらか一方の閾値が0以下の場合、その閾値の条件は無効です。

値下げ率は次の式で計算します。

```text
(前回価格 - 現在価格) / 前回価格 * 100
```

`notify_no_change` が `true` の場合、新商品・値下げ商品の通知対象がなくてもSlack通知を送信します。

通常検索と検索履歴からの再検索では、`notification_settings` を指定せず、従来の通知動作を使用します。

## 技術構成

- Python 3.13
- Flask
- Gunicorn
- PostgreSQL
- psycopg (`psycopg[binary]`)
- pandas
- openpyxl
- requests
- python-dotenv
- Selenium / Chromium
- Slack Webhook
- 楽天市場API
- Google Cloud Run
- Cloud SQL for PostgreSQL
- Cloud Scheduler
- Cloud Logging

依存パッケージは [requirements.txt](requirements.txt) で管理しています。

## データベース

初期化用SQLは [schema.sql](schema.sql) にあります。

### search_history

検索履歴を保存するテーブルです。

- `id`: 自動採番される検索履歴ID
- `keyword`: 検索キーワード
- `result_count`: 検索結果件数
- `searched_at`: 検索日時

### monitor_keywords

監視対象のキーワードを保存するテーブルです。

- `id`: 自動採番される監視キーワードID
- `keyword`: 監視キーワード
- `is_active`: 監視対象として有効かどうか
- `created_at`: 登録日時

### notification_settings

監視通知設定を保存するテーブルです。`id = 1` の行を使用します。

- `id`: 設定ID
- `notify_new_items`: 新商品通知の有効・無効
- `notify_price_drops`: 値下げ通知の有効・無効
- `notify_no_change`: 変化なし通知の有効・無効
- `min_price_drop_amount`: 最低値下げ額
- `min_price_drop_percent`: 最低値下げ率

### product_history

商品の価格履歴を保存するテーブルです。

- `id`: 自動採番される履歴ID
- `keyword`: 検索キーワード
- `item_code`: 楽天商品識別子。コード上では `ASIN` 列の値を使用
- `product_name`: 商品名
- `price`: 価格
- `product_url`: 商品URL
- `checked_at`: 確認日時

## プロジェクト構成

```text
app.py
bot.py
rakuten.py
product_history.py
slack.py
schema.sql
config.py
filter.py
excel.py
Dockerfile
requirements.txt
auto_run.py
run_amazon_search.bat
test_price_down.py
test_notification_settings.py
templates/
```

主要ファイル:

- `app.py`: Flaskアプリ、Web画面、検索履歴、監視キーワード、通知設定、監視API
- `bot.py`: 楽天検索結果の整形、価格履歴との比較、新商品・値下げ判定、通知処理
- `rakuten.py`: 楽天市場APIの呼び出しと商品データのDataFrame化
- `product_history.py`: PostgreSQL接続、最新価格取得、価格履歴保存
- `slack.py`: Slack Webhookによる通知送信と通知メッセージ作成
- `schema.sql`: PostgreSQLの4テーブルと通知設定初期データの作成
- `config.py`: 除外ワード、出力ファイル名、Slack Webhook URLの読み込み
- `filter.py`: 検索結果のフィルタリング
- `excel.py`: 検索結果のExcel保存
- `Dockerfile`: Cloud Run向けコンテナイメージの定義。Gunicornで `app:app` を起動
- `auto_run.py`: `run_search()` を使う単独検索用の補助スクリプト
- `run_amazon_search.bat`: Windows環境で `auto_run.py` を実行する補助スクリプト
- `templates/`: 検索画面、監視画面、検索履歴、商品価格履歴などのHTMLテンプレート
- `test_price_down.py`: 新商品と値下げ商品の価格履歴判定をテスト
- `test_notification_settings.py`: 最低値下げ額・最低値下げ率の通知対象判定をテスト

## テスト

標準ライブラリの `unittest` を使用します。

```bash
python -m unittest discover -v
```

現在のテスト内容:

- `test_price_down.py`
  - 前回価格より現在価格が安い商品の検出
  - 価格履歴がない新商品の検出
  - `get_latest_price()` と `save_product_history()` の呼び出し内容
- `test_notification_settings.py`
  - 最低値下げ額300円・最低値下げ率5%で通知対象になるケース
  - 最低値下げ額1000円・最低値下げ率5%で通知対象外になるケース
  - 最低値下げ額300円・最低値下げ率20%で通知対象外になるケース
  - 最低値下げ額0円・最低値下げ率0%で通知対象になるケース

## ローカル起動

### 依存パッケージのインストール

```bash
python -m pip install -r requirements.txt
```

### Flaskの開発サーバーで起動

```bash
python -m flask --app app run
```

### Gunicornで起動

```bash
gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 app:app
```

ローカル環境では、アプリが使用する以下の環境変数を設定してください。

- `DB_HOST`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_PORT`
- `RAKUTEN_APPLICATION_ID`
- `RAKUTEN_ACCESS_KEY`
- `SLACK_WEBHOOK_URL`

データベースを新規作成する場合は、対象のPostgreSQLデータベースに接続してから次のSQLを実行します。

```bash
psql -f schema.sql
```

## Cloud Run

デプロイには [Dockerfile](Dockerfile) を使用します。現在確認されているデプロイコマンドは次のとおりです。

```bash
gcloud run deploy rakuten-search-tool --source . --region asia-northeast1
```

コンテナは `PORT` 環境変数を使用し、指定がない場合は8080番ポートでGunicornを起動します。

Cloud Runで使用するDB接続情報、楽天API認証情報、Slack Webhook URLなどの秘密情報は、ソースコードやREADMEに直接記載せず、Secret Managerから環境変数としてCloud Runへ渡してください。ローカルでは `.env` を利用できますが、秘密情報をGitHubへコミットしないでください。

Cloud Run環境では `K_SERVICE` を判定してCloud SQL Unixソケットへ接続します。Cloud SQL接続に必要な設定は、Cloud RunとCloud SQLの環境に合わせて行ってください。

## Cloud Scheduler

現在確認されている定期監視の設定は次のとおりです。

- ジョブ名: `rakuten-search-daily`
- リージョン: `asia-northeast1`
- スケジュール: `0 6 * * *`
- タイムゾーン: `Asia/Tokyo`
- HTTPメソッド: `POST`
- パス: `/api/monitor/run`

`/api/monitor/run` は有効な監視キーワードを取得し、通知設定を適用した監視検索を実行します。

## ログ

監視検索の実行時はCloud Loggingで次のログを確認できます。

```text
監視開始
キーワード: USBハブ, HDMIケーブル
取得件数: 30
新商品: 0
値下げ: 0
Slack通知: 送信
監視完了
```

`新商品` と `値下げ` は、通知設定と最低値下げ額・最低値下げ率を適用した後の実際の通知対象件数です。

Slack通知の状態は次の3種類です。

- `Slack通知: なし`: 通知条件に該当せず、Slack送信を呼び出していない
- `Slack通知: 送信`: Slack送信に成功した
- `Slack通知: 失敗`: Slack送信を呼び出したが、成功しなかった

エラー時は次のようなログが出力されます。

```text
監視エラー: 403 Client Error: CLIENT_IP_NOT_ALLOWED
```

監視入口では、短いエラー概要と `app.logger.exception()` によるスタックトレースが記録されます。SlackのHTTPエラーでは、レスポンス本文ではなくHTTPステータスが記録されます。

## 注意事項

- APIキー、楽天Access Key、DBパスワード、Slack Webhook URLなどの秘密情報をREADMEやソースコードへ記載しないでください。
- ローカルの秘密情報には `.env` を使用し、GitHubへコミットしないでください。
- Cloud RunではSecret Managerを利用して秘密情報を環境変数へ渡してください。
- Cloud Schedulerの認証設定など、コードから確認できない設定は別途確認してください。
- `schema.sql` 実行時には、接続先データベースと実行権限を確認してください。
