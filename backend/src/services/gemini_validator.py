"""Gemini APIレスポンスの検証ユーティリティ

Gemini APIから返されるレスポンスを検証し、エラーを適切に処理するための
ヘルパー関数を提供します。
"""

import logging
from typing import Any, Optional

from src.services.gemini_exceptions import (
    FINISH_REASON_BLOCKLIST,
    FINISH_REASON_MAX_TOKENS,
    FINISH_REASON_OTHER,
    FINISH_REASON_PROHIBITED_CONTENT,
    FINISH_REASON_RECITATION,
    FINISH_REASON_SAFETY,
    FINISH_REASON_STOP,
    EmptyResponseError,
    MaxTokensError,
    RecitationError,
    SafetyFilterError,
    UnexpectedFinishReasonError,
)

# ロガーの設定
logger = logging.getLogger(__name__)


def validate_response(response: Any, context: str = "") -> None:
    """Gemini APIレスポンスの包括的な検証を行う

    レスポンスが有効かどうかを確認し、問題があれば適切な例外を投げます。

    Args:
        response: Gemini APIから返されたレスポンスオブジェクト
        context: エラーメッセージに含めるコンテキスト情報（例: "generate_plot"）

    Raises:
        EmptyResponseError: candidatesが空またはpartsがない場合
        SafetyFilterError: 安全性フィルターでブロックされた場合
        MaxTokensError: トークン数制限に達した場合
        RecitationError: 著作権問題で停止した場合
        UnexpectedFinishReasonError: 予期しないfinish_reasonの場合

    Example:
        >>> response = model.generate_content("...")
        >>> validate_response(response, context="generate_plot")
    """
    context_msg = f" [{context}]" if context else ""

    # 1. candidatesの存在確認
    if not hasattr(response, "candidates") or not response.candidates:
        logger.error(f"Empty candidates in response{context_msg}")
        raise EmptyResponseError(message=f"API response contains no candidates{context_msg}", response=response)

    # 最初のcandidateを取得
    candidate = response.candidates[0]

    # 2. finish_reasonの確認
    finish_reason = None
    if hasattr(candidate, "finish_reason"):
        # finish_reasonはenumの可能性があるため、name属性または文字列変換を試みる
        finish_reason = getattr(candidate.finish_reason, "name", None) or str(candidate.finish_reason)
        logger.debug(f"Response finish_reason{context_msg}: {finish_reason}")

    # 3. content.partsの存在確認
    if not hasattr(candidate, "content") or not candidate.content:
        logger.error(f"No content in candidate{context_msg}")
        _handle_finish_reason_error(finish_reason, response, candidate, context_msg)

    if not hasattr(candidate.content, "parts") or not candidate.content.parts:
        logger.error(f"No parts in candidate content{context_msg}")
        _handle_finish_reason_error(finish_reason, response, candidate, context_msg)

    # 4. finish_reasonの詳細チェック（STOPまたはNone以外の場合）
    if finish_reason and finish_reason != FINISH_REASON_STOP:
        _handle_finish_reason_error(finish_reason, response, candidate, context_msg)

    logger.debug(f"Response validation passed{context_msg}")


def _handle_finish_reason_error(finish_reason: Optional[str], response: Any, candidate: Any, context_msg: str) -> None:
    """finish_reasonに基づいて適切なエラーを投げる

    Args:
        finish_reason: 終了理由
        response: レスポンスオブジェクト
        candidate: candidateオブジェクト
        context_msg: コンテキストメッセージ

    Raises:
        適切なカスタム例外
    """
    # safety_ratingsの取得
    safety_ratings = []
    blocked_category = None
    if hasattr(candidate, "safety_ratings") and candidate.safety_ratings:
        safety_ratings = [
            {
                "category": getattr(rating.category, "name", str(rating.category)),
                "probability": getattr(rating.probability, "name", str(rating.probability)),
                "blocked": getattr(rating, "blocked", False),
            }
            for rating in candidate.safety_ratings
        ]
        # ブロックされたカテゴリを特定
        for rating in candidate.safety_ratings:
            if getattr(rating, "blocked", False):
                blocked_category = getattr(rating.category, "name", str(rating.category))
                break

    # finish_reasonに応じた例外を投げる
    if finish_reason == FINISH_REASON_SAFETY:
        raise SafetyFilterError(
            message=f"Content blocked by safety filter{context_msg}",
            response=response,
            finish_reason=finish_reason,
            safety_ratings=safety_ratings,
            blocked_category=blocked_category,
        )

    elif finish_reason == FINISH_REASON_MAX_TOKENS:
        tokens_used = None
        if hasattr(response, "usage_metadata") and hasattr(response.usage_metadata, "total_token_count"):
            tokens_used = response.usage_metadata.total_token_count
        raise MaxTokensError(
            message=f"Maximum token limit reached{context_msg}",
            response=response,
            finish_reason=finish_reason,
            tokens_used=tokens_used,
        )

    elif finish_reason == FINISH_REASON_RECITATION:
        raise RecitationError(
            message=f"Content flagged for recitation{context_msg}", response=response, finish_reason=finish_reason
        )

    elif finish_reason in [FINISH_REASON_BLOCKLIST, FINISH_REASON_PROHIBITED_CONTENT]:
        raise SafetyFilterError(
            message=f"Content blocked due to prohibited content or blocklist{context_msg}",
            response=response,
            finish_reason=finish_reason,
            safety_ratings=safety_ratings,
        )

    elif finish_reason == FINISH_REASON_OTHER or finish_reason:
        # その他の予期しないfinish_reason
        raise UnexpectedFinishReasonError(
            message=f"Unexpected finish_reason: {finish_reason}{context_msg}",
            response=response,
            finish_reason=finish_reason,
        )

    # finish_reasonがないがエラーが発生している場合
    raise EmptyResponseError(message=f"API response contains no valid parts{context_msg}", response=response)


def get_safe_text(response: Any, context: str = "") -> str:
    """レスポンスから安全にテキストを取得する

    レスポンスを検証してから.textプロパティにアクセスします。

    Args:
        response: Gemini APIから返されたレスポンスオブジェクト
        context: エラーメッセージに含めるコンテキスト情報

    Returns:
        str: 生成されたテキスト

    Raises:
        各種GeminiAPIError: レスポンスに問題がある場合

    Example:
        >>> response = model.generate_content("...")
        >>> text = get_safe_text(response, context="generate_chapter")
    """
    # レスポンスを検証
    validate_response(response, context)

    # 検証が通れば安全に.textにアクセス可能
    try:
        return response.text
    except Exception as e:
        # 万が一.textアクセスで失敗した場合
        logger.error(f"Failed to access response.text: {e}")
        context_msg = f" [{context}]" if context else ""
        raise EmptyResponseError(
            message=f"Failed to extract text from response{context_msg}: {str(e)}", response=response
        )


def check_safety_ratings(response: Any, context: str = "") -> list:
    """レスポンスのsafety_ratingsを取得して確認する

    デバッグやロギング目的でsafety_ratingsの詳細を取得します。

    Args:
        response: Gemini APIから返されたレスポンスオブジェクト
        context: コンテキスト情報

    Returns:
        list: safety_ratingsのリスト（辞書形式）

    Example:
        >>> response = model.generate_content("...")
        >>> ratings = check_safety_ratings(response)
        >>> for rating in ratings:
        ...     print(f"{rating['category']}: {rating['probability']}")
    """
    context_msg = f" [{context}]" if context else ""
    safety_ratings = []

    if hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, "safety_ratings") and candidate.safety_ratings:
            for rating in candidate.safety_ratings:
                rating_dict = {
                    "category": getattr(rating.category, "name", str(rating.category)),
                    "probability": getattr(rating.probability, "name", str(rating.probability)),
                    "blocked": getattr(rating, "blocked", False),
                }
                safety_ratings.append(rating_dict)

                # ログ出力
                logger.debug(
                    f"Safety rating{context_msg}: "
                    f"{rating_dict['category']} = {rating_dict['probability']} "
                    f"(blocked: {rating_dict['blocked']})"
                )

    return safety_ratings


def get_response_metadata(response: Any) -> dict:
    """レスポンスからメタデータを抽出する

    ロギングやデバッグ用にレスポンスの詳細情報を取得します。

    Args:
        response: Gemini APIから返されたレスポンスオブジェクト

    Returns:
        dict: メタデータの辞書

    Example:
        >>> response = model.generate_content("...")
        >>> metadata = get_response_metadata(response)
        >>> print(f"Tokens used: {metadata.get('total_tokens')}")
    """
    metadata = {}

    # finish_reasonの取得
    if hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, "finish_reason"):
            metadata["finish_reason"] = getattr(candidate.finish_reason, "name", str(candidate.finish_reason))

    # usage_metadataの取得
    if hasattr(response, "usage_metadata"):
        usage = response.usage_metadata
        metadata["prompt_token_count"] = getattr(usage, "prompt_token_count", None)
        metadata["candidates_token_count"] = getattr(usage, "candidates_token_count", None)
        metadata["total_token_count"] = getattr(usage, "total_token_count", None)

    # safety_ratingsの取得
    metadata["safety_ratings"] = check_safety_ratings(response)

    return metadata
