"""Gemini APIリトライ機構

指数バックオフを使用したリトライデコレータを提供します。
一時的なエラー（ネットワーク、タイムアウト、レート制限）に対して自動リトライを行います。
"""

import logging
import time
from functools import wraps
from typing import Callable, Tuple, Type

from src.services.gemini_exceptions import (
    APIAuthenticationError,
    EmptyResponseError,
    GeminiAPIError,
    InvalidJSONError,
    MaxTokensError,
    NetworkError,
    RateLimitError,
    RecitationError,
    SafetyFilterError,
    TimeoutError,
    UnexpectedFinishReasonError,
)

# ロガーの設定
logger = logging.getLogger(__name__)

# リトライ対象のエラー（一時的なエラー）
# これらのエラーは再試行で成功する可能性がある
RETRIABLE_ERRORS: Tuple[Type[Exception], ...] = (
    NetworkError,
    TimeoutError,
    RateLimitError,
    EmptyResponseError,  # API側の一時的な問題の可能性
    UnexpectedFinishReasonError,  # 予期しないfinish_reasonも一時的な可能性
)

# リトライ対象外のエラー（構造的な問題）
# これらのエラーは再試行しても成功しない
NON_RETRIABLE_ERRORS: Tuple[Type[Exception], ...] = (
    SafetyFilterError,  # プロンプトの内容に問題がある
    MaxTokensError,  # トークン制限の問題
    RecitationError,  # 著作権問題
    InvalidJSONError,  # JSON構造の問題（ただしGeminiの出力ミスの可能性もあるため要注意）
    APIAuthenticationError,  # 認証問題
)


def retry_on_error(
    max_retries: int = 3,
    initial_delay: float = 2.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    retriable_errors: Tuple[Type[Exception], ...] = RETRIABLE_ERRORS,
    jitter: bool = True,
):
    """指数バックオフを使用したリトライデコレータ

    一時的なエラーが発生した場合に、指数バックオフで自動的にリトライします。

    Args:
        max_retries: 最大リトライ回数（デフォルト: 3回）
        initial_delay: 最初のリトライまでの待機時間（秒）（デフォルト: 2秒）
        backoff_factor: 待機時間の増加率（デフォルト: 2.0倍）
        max_delay: 最大待機時間（秒）（デフォルト: 60秒）
        retriable_errors: リトライ対象のエラータプル
        jitter: ジッター（ランダムな遅延）を追加するか（デフォルト: True）

    小説生成用のデフォルト設定:
        - max_retries=3: 合計4回の試行（初回+3回のリトライ）
        - initial_delay=2.0: 最初は2秒待機（小説生成は時間がかかるため短め）
        - backoff_factor=2.0: 2秒 → 4秒 → 8秒と倍増
        - max_delay=60.0: 最大60秒待機（長時間の生成処理に対応）
        - jitter=True: 複数リクエストの衝突を避けるため

    Example:
        >>> @retry_on_error(max_retries=3, initial_delay=2.0)
        ... def generate_content():
        ...     return model.generate_content("...")
        ...
        >>> result = generate_content()  # エラー時に自動リトライ

        >>> # カスタム設定
        >>> @retry_on_error(max_retries=5, initial_delay=1.0, backoff_factor=1.5)
        ... def quick_request():
        ...     return api_call()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = initial_delay

            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    # 関数を実行
                    result = func(*args, **kwargs)

                    # 成功した場合
                    if attempt > 0:
                        logger.info(f"Function '{func.__name__}' succeeded on attempt {attempt + 1}/{max_retries + 1}")
                    return result

                except retriable_errors as e:
                    last_exception = e

                    # 最後の試行の場合はリトライしない
                    if attempt >= max_retries:
                        logger.error(f"Function '{func.__name__}' failed after {max_retries + 1} attempts: {e}")
                        raise

                    # RateLimitErrorの場合はretry_afterを使用
                    if isinstance(e, RateLimitError) and hasattr(e, "retry_after") and e.retry_after:
                        wait_time = min(e.retry_after, max_delay)
                        logger.warning(
                            f"Rate limit hit for '{func.__name__}'. Waiting {wait_time}s (from retry_after header)"
                        )
                    else:
                        # 指数バックオフの計算
                        wait_time = min(delay, max_delay)

                        # ジッターを追加（衝突回避）
                        if jitter:
                            import random

                            wait_time = wait_time * (0.5 + random.random())

                        logger.warning(
                            f"Retriable error in '{func.__name__}' (attempt {attempt + 1}/{max_retries + 1}): "
                            f"{type(e).__name__}: {e}. Retrying in {wait_time:.2f}s..."
                        )

                    # 待機
                    time.sleep(wait_time)

                    # 次回の待機時間を計算
                    delay *= backoff_factor

                except NON_RETRIABLE_ERRORS as e:
                    # リトライ対象外のエラーはそのまま投げる
                    logger.error(f"Non-retriable error in '{func.__name__}': {type(e).__name__}: {e}")
                    raise

                except GeminiAPIError as e:
                    # その他のGeminiAPIErrorも基本的にリトライしない
                    logger.error(f"GeminiAPIError in '{func.__name__}': {type(e).__name__}: {e}")
                    raise

                except Exception as e:
                    # 予期しない例外はログに記録して投げる
                    logger.error(f"Unexpected error in '{func.__name__}': {type(e).__name__}: {e}", exc_info=True)
                    raise

            # ここには到達しないはずだが、念のため
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


# 小説生成用のプリセットデコレータ
def retry_for_novel_generation(func: Callable) -> Callable:
    """小説生成用のリトライデコレータ（プリセット）

    小説生成に最適化されたリトライ設定を適用します。
    - 最大3回リトライ（合計4回の試行）
    - 初期待機時間: 2秒
    - バックオフ係数: 2.0倍
    - 最大待機時間: 60秒

    Example:
        >>> @retry_for_novel_generation
        ... def generate_chapter(plot, style):
        ...     return model.generate_content(...)
    """
    return retry_on_error(max_retries=3, initial_delay=2.0, backoff_factor=2.0, max_delay=60.0, jitter=True)(func)


# 短時間処理用のプリセットデコレータ
def retry_for_quick_request(func: Callable) -> Callable:
    """短時間処理用のリトライデコレータ（プリセット）

    短時間のリクエスト（メタデータ取得など）に最適化されたリトライ設定です。
    - 最大2回リトライ（合計3回の試行）
    - 初期待機時間: 1秒
    - バックオフ係数: 1.5倍
    - 最大待機時間: 10秒

    Example:
        >>> @retry_for_quick_request
        ... def get_metadata():
        ...     return api.get_metadata()
    """
    return retry_on_error(max_retries=2, initial_delay=1.0, backoff_factor=1.5, max_delay=10.0, jitter=True)(func)


# JSON生成用のプリセットデコレータ（InvalidJSONErrorもリトライ対象に含める）
def retry_for_json_generation(func: Callable) -> Callable:
    """JSON生成用のリトライデコレータ（プリセット）

    JSON形式の生成に最適化されたリトライ設定です。
    InvalidJSONErrorもリトライ対象に含めます（Geminiの出力ミスの可能性があるため）。
    - 最大4回リトライ（合計5回の試行）
    - 初期待機時間: 2秒
    - バックオフ係数: 1.8倍
    - 最大待機時間: 45秒

    Example:
        >>> @retry_for_json_generation
        ... def generate_init_json(text_length, chapter_count, other):
        ...     return model.generate_content(...)
    """
    # InvalidJSONErrorをリトライ対象に追加
    extended_retriable = RETRIABLE_ERRORS + (InvalidJSONError,)

    return retry_on_error(
        max_retries=4,
        initial_delay=2.0,
        backoff_factor=1.8,
        max_delay=45.0,
        retriable_errors=extended_retriable,
        jitter=True,
    )(func)


def calculate_retry_delay(attempt: int, initial_delay: float = 2.0, backoff_factor: float = 2.0) -> float:
    """リトライ待機時間を計算するユーティリティ関数

    Args:
        attempt: 試行回数（0始まり）
        initial_delay: 初期待機時間（秒）
        backoff_factor: バックオフ係数

    Returns:
        float: 待機時間（秒）

    Example:
        >>> calculate_retry_delay(0)  # 2.0
        >>> calculate_retry_delay(1)  # 4.0
        >>> calculate_retry_delay(2)  # 8.0
    """
    return initial_delay * (backoff_factor**attempt)
