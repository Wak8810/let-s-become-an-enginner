# バックエンド

## API開発の流れ

### 1. 開発用コンテナに入る

- Docker Desktopを起動
- VS Codeでコマンドパレットを開き`Dev Containers: Reopen in Container`を選択
  - コンテナ設定ファイルに変更があった際は`Dev Containers: Rebuild and Reopen in Container`を選択
- セットアップ完了を待つ

### 2. ブラウザで自動生成APIドキュメントを開く

- `http://localhost:5000`をブラウザで開く
- 作成されているAPI一覧(Swagger UI)を閲覧できることを確認
- 「tests」関連のAPI操作でエラーが起きないか確認
  - プルダウンを開いて「Try it out」->「Execute」で実際にAPIリクエストを投げられる

### 3. APIを作成する

- `src/`フォルダ下のPythonファイルにAPIを作成
  - リクエストボディを決める
  - レスポンスを決める
  - testsなどを参考にしてエンドポイント関数を作成
- 一連の処理が実装出来たらSwagger UIから動作確認
  - `curl`コマンドでも動作確認可能
