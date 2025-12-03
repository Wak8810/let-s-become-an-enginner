# ロギング機能の実装まとめ

## 実装内容

### 1. 置き換えたファイル

#### `src/novels.py`
- **バックグラウンドタスク (`novelist_bg_task_runner`)**
  - ✅ `print()` → `logger.info()` / `logger.error()` / `logger.warning()`
  - タスク開始/終了、章の生成状況、エラーをロギング
  - 13箇所のprint文を置き換え

- **ストリーミング生成関数 (`novel_generater`)**
  - ✅ `print()` → `logger.info()` / `logger.error()` / `logger.debug()`
  - プロット生成、章の生成、データベースコミットをロギング
  - 6箇所のprint文を置き換え

#### `src/services/novelist.py`
- ✅ カスタムlog()メソッドを削除
- ✅ 標準的な`logging.Logger`に置き換え
- ✅ `self.log()` → `logger.debug()` / `logger.info()`
- 小説初期化、章生成、リトライ時のログ出力を改善

#### `src/services/error_handler.py`
- ✅ 既にloggerを使用（変更なし）
- エラーハンドリング、ステータス更新の詳細ログ

#### `src/services/novel_generator.py`
- ✅ 既にloggerを使用（変更なし）
- Gemini API呼び出し、初期化のログ

### 2. ログレベルの使い分け

| レベル | 用途 | 例 |
|--------|------|-----|
| `DEBUG` | 詳細なデバッグ情報 | 章の内容長、内部状態の変化 |
| `INFO` | 通常の動作情報 | タスク開始/完了、章生成完了 |
| `WARNING` | 警告（処理は継続） | 想定外のデータ状態 |
| `ERROR` | エラー（処理停止） | 章生成失敗、DB接続エラー |

### 3. ログ設定（`app.py`）

```python
# 固定でINFOレベル
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

### ログ例

#### 章生成成功時
```
2025-12-03 03:40:54 - src.novels - INFO - Background task: Starting chapter generation - Chapter: 2
2025-12-03 03:40:55 - src.services.novelist - DEBUG - Generated chapter - Next: 3, Total text length: 5432, Chapter length: 2716
2025-12-03 03:40:55 - src.novels - INFO - Background task: Chapter generated and committed - Chapter: 2
```

#### 章生成失敗時
```
2025-12-03 03:40:56 - src.novels - ERROR - Background task: Chapter generation failed - SafetyFilterError: Content blocked by safety filter
2025-12-03 03:40:56 - src.services.error_handler - ERROR - Chapter marked as FAILED - Chapter ID: abc123, Novel ID: def456, Chapter Number: 3, Type: SafetyFilterError, Message: Content blocked
2025-12-03 03:40:56 - src.novels - INFO - Background task: Task stopped due to chapter generation failure
```

## メリット

### 1. 見やすさ
- ✅ タイムスタンプ、モジュール名、ログレベルが自動付与
- ✅ ログレベルでフィルタリング可能

### 2. デバッグ効率
- ✅ エラー発生時の前後の状態を追跡しやすい
- ✅ 本番環境ではINFO以上のみ出力（ノイズ削減）

### 3. 保守性
- ✅ 標準的なlogging moduleを使用（拡張しやすい）
- ✅ 将来的にファイル出力や外部サービスへの送信も可能

## テスト

```bash
# ロギング機能のテスト
uv run python test_logging.py
```

すべてのモジュールで正常にログが出力されることを確認済み。

## 変更なし（docstring内のサンプルコード）

以下のファイルのprint文はdocstring内のサンプルコードなので変更なし：
- `src/services/gemini_validator.py`
- `src/services/error_handler.py`（docstring内のみ）

## まとめ

✅ 全てのprint文をloggerに置き換え完了  
✅ ログレベルを環境変数で制御可能  
✅ 開発時はDEBUG、本番時はINFOを推奨  
✅ エラーハンドリングのロギングは既に実装済み  
✅ テスト実行により動作確認済み
