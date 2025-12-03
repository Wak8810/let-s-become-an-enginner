"""Gemini API関連のカスタム例外クラス

Gemini APIとの通信で発生する様々なエラーを表現するための例外クラス群を定義します。
これらの例外を使用することで、エラーの種類に応じた適切な処理を実装できます。
"""

from typing import Any, Optional


class GeminiAPIError(Exception):
    """Gemini API関連エラーの基底クラス

    すべてのGemini API関連のカスタム例外はこのクラスを継承します。

    Attributes:
        message (str): エラーメッセージ
        response (Any): Gemini APIからのレスポンスオブジェクト（利用可能な場合）
        finish_reason (Optional[str]): Gemini APIのfinish_reason（利用可能な場合）
        details (Optional[dict]): 追加のエラー詳細情報
    """

    def __init__(
        self,
        message: str,
        response: Optional[Any] = None,
        finish_reason: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.response = response
        self.finish_reason = finish_reason
        self.details = details or {}

    def __str__(self):
        base_msg = self.message
        if self.finish_reason:
            base_msg += f" (finish_reason: {self.finish_reason})"
        if self.details:
            base_msg += f" | Details: {self.details}"
        return base_msg


class SafetyFilterError(GeminiAPIError):
    """安全性フィルターによってコンテンツがブロックされた場合のエラー

    Gemini APIの安全性フィルター（safety_ratings）によって、
    プロンプトまたは生成されたコンテンツがブロックされた場合に発生します。

    対処方法:
        - プロンプトの内容を見直す
        - より安全な表現に変更する
        - 必要に応じてsafetySettingsを調整する（非推奨）

    Attributes:
        safety_ratings (list): APIから返された安全性評価の詳細
        blocked_category (str): ブロックされたカテゴリ（例: HARM_CATEGORY_SEXUALLY_EXPLICIT）
    """

    def __init__(
        self,
        message: str = "Content was blocked by safety filter",
        response: Optional[Any] = None,
        safety_ratings: Optional[list] = None,
        blocked_category: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, response, **kwargs)
        self.safety_ratings = safety_ratings or []
        self.blocked_category = blocked_category
        self.details.update({"safety_ratings": self.safety_ratings, "blocked_category": self.blocked_category})


class EmptyResponseError(GeminiAPIError):
    """APIからの応答が空、またはcandidatesが含まれていない場合のエラー

    Gemini APIから有効なcandidatesが返されない場合に発生します。
    これは通常、以下の理由で発生します:
        - プロンプトが不適切または曖昧すぎる
        - モデルが生成できる内容がない
        - API側の一時的な問題

    対処方法:
        - プロンプトをより具体的に改善する
        - リトライを試みる
        - コンテキストウィンドウのサイズを確認する
    """

    def __init__(
        self,
        message: str = "API response contains no valid candidates or parts",
        response: Optional[Any] = None,
        **kwargs,
    ):
        super().__init__(message, response, **kwargs)


class InvalidJSONError(GeminiAPIError):
    """APIからの応答がJSON形式として無効、または期待する構造でない場合のエラー

    generate_initなどでJSON形式のレスポンスを期待している場合に、
    パースに失敗したり、必須キーが欠けていたりする場合に発生します。

    対処方法:
        - プロンプトでJSON形式の要求をより明確にする
        - レスポンスからJSONを抽出するロジックを改善する
        - リトライを試みる

    Attributes:
        raw_text (str): パースに失敗した元のテキスト
        missing_keys (list): 欠けている必須キーのリスト
        parse_error (str): JSON解析エラーの詳細
    """

    def __init__(
        self,
        message: str = "Failed to parse JSON from API response",
        raw_text: Optional[str] = None,
        missing_keys: Optional[list] = None,
        parse_error: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.raw_text = raw_text
        self.missing_keys = missing_keys or []
        self.parse_error = parse_error
        self.details.update(
            {
                "raw_text": raw_text[:200] if raw_text else None,  # 最初の200文字のみ
                "missing_keys": self.missing_keys,
                "parse_error": self.parse_error,
            }
        )


class MaxTokensError(GeminiAPIError):
    """最大トークン数に達したことによるエラー

    生成中に最大トークン数制限に達した場合に発生します。
    finish_reasonがMAX_TOKENSの場合に該当します。

    対処方法:
        - maxOutputTokensを増やす（モデルの制限内で）
        - 生成する内容を分割する
        - より短いコンテキストを使用する

    Attributes:
        tokens_used (int): 使用されたトークン数（利用可能な場合）
    """

    def __init__(self, message: str = "Maximum token limit reached", tokens_used: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.tokens_used = tokens_used
        if tokens_used:
            self.details["tokens_used"] = tokens_used


class RecitationError(GeminiAPIError):
    """著作権のある内容の再現が検出された場合のエラー

    生成されたコンテンツが既存の著作物の再現と判定された場合に発生します。
    finish_reasonがRECITATIONの場合に該当します。

    対処方法:
        - プロンプトをより独創的な内容に変更する
        - 特定の作品名や固有名詞を避ける
        - 生成のバリエーションを増やす
    """

    def __init__(self, message: str = "Content was flagged for recitation of copyrighted material", **kwargs):
        super().__init__(message, **kwargs)


class NetworkError(GeminiAPIError):
    """ネットワーク関連のエラー

    APIへの接続に失敗した場合や、ネットワーク通信中に問題が発生した場合のエラーです。

    対処方法:
        - ネットワーク接続を確認する
        - リトライを試みる（指数バックオフを使用）
        - プロキシ設定を確認する

    Attributes:
        original_error (Exception): 元のネットワークエラー
    """

    def __init__(
        self,
        message: str = "Network error occurred while communicating with Gemini API",
        original_error: Optional[Exception] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.original_error = original_error
        if original_error:
            self.details["original_error"] = str(original_error)


class TimeoutError(GeminiAPIError):
    """APIリクエストのタイムアウトエラー

    指定されたタイムアウト時間内にAPIからの応答が得られなかった場合に発生します。

    対処方法:
        - タイムアウト時間を延長する
        - リトライを試みる
        - プロンプトやコンテキストのサイズを削減する

    Attributes:
        timeout_seconds (int): タイムアウト設定（秒）
    """

    def __init__(self, message: str = "API request timed out", timeout_seconds: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        if timeout_seconds:
            self.details["timeout_seconds"] = timeout_seconds


class RateLimitError(GeminiAPIError):
    """APIレート制限エラー

    APIのレート制限に達した場合に発生します。
    短時間に多くのリクエストを送信した場合に起こります。

    対処方法:
        - 待機してからリトライする
        - リクエストの頻度を下げる
        - 必要に応じてAPIのクォータ上限を確認する

    Attributes:
        retry_after (int): 再試行までの待機時間（秒）
    """

    def __init__(self, message: str = "API rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        if retry_after:
            self.details["retry_after"] = retry_after


class UnexpectedFinishReasonError(GeminiAPIError):
    """予期しないfinish_reasonが返された場合のエラー

    finish_reasonが既知のカテゴリに該当しない場合に発生します。

    対処方法:
        - エラーログを確認する
        - Gemini APIのドキュメントで新しいfinish_reasonを確認する
        - 必要に応じてエラーハンドリングを更新する
    """

    def __init__(self, message: str = "Unexpected finish_reason received from API", **kwargs):
        super().__init__(message, **kwargs)


class APIAuthenticationError(GeminiAPIError):
    """API認証エラー

    APIキーが無効、期限切れ、または権限が不足している場合に発生します。

    対処方法:
        - APIキーを確認する
        - APIキーの権限を確認する
        - 必要に応じて新しいAPIキーを取得する
    """

    def __init__(self, message: str = "API authentication failed", **kwargs):
        super().__init__(message, **kwargs)


# エラー種別の判定に使用する定数
FINISH_REASON_STOP = "STOP"
FINISH_REASON_MAX_TOKENS = "MAX_TOKENS"
FINISH_REASON_SAFETY = "SAFETY"
FINISH_REASON_RECITATION = "RECITATION"
FINISH_REASON_OTHER = "OTHER"
FINISH_REASON_BLOCKLIST = "BLOCKLIST"
FINISH_REASON_PROHIBITED_CONTENT = "PROHIBITED_CONTENT"
