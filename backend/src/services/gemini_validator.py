"""Gemini APIレスポンスの検証ユーティリティ

Gemini APIから返されるレスポンスを検証し、エラーを適切に処理するための
ヘルパー関数を提供します。
"""

import json
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
    InvalidJSONError,
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


# ==============================================================================
# JSON検証機能
# ==============================================================================

# JSONスキーマ定義: 期待されるJSON構造を定義
# プロンプト変更時はここを編集するだけでバリデーションを更新可能
NOVEL_INIT_SCHEMA = {
    "title": {"type": "str", "required": True, "description": "小説のタイトル"},
    "summary": {"type": "str", "required": True, "description": "小説の要約"},
    "plot": {"type": "str", "required": True, "description": "小説の全体プロット"},
    "characters": {
        "type": "list",
        "required": True,
        "description": "登場人物のリスト",
        "item_schema": {
            "name": {"type": "str", "required": True, "description": "キャラクター名"},
            "role": {"type": "str", "required": True, "description": "役割"},
        },
    },
    "chapter_plots": {
        "type": "list",
        "required": True,
        "description": "各章のプロットリスト",
        "item_schema": {"plot": {"type": "str", "required": True, "description": "章のプロット"}},
    },
}


def validate_json_response(json_text: str, schema: dict = None, context: str = "validate_json") -> dict:
    """Gemini APIから返されたJSON文字列を検証してパースする

    JSON形式の検証と、期待されるスキーマに基づく構造チェックを行います。

    Args:
        json_text: JSON形式の文字列
        schema: 検証に使用するスキーマ定義（デフォルトはNOVEL_INIT_SCHEMA）
        context: エラーメッセージに含めるコンテキスト情報

    Returns:
        dict: パース済みのJSON辞書

    Raises:
        InvalidJSONError: JSON解析失敗または構造が不正な場合

    Example:
        >>> json_text = '{"title": "My Novel", "summary": "...", ...}'
        >>> data = validate_json_response(json_text)
        >>> print(data["title"])
    """
    if schema is None:
        schema = NOVEL_INIT_SCHEMA

    context_msg = f" [{context}]" if context else ""

    # 1. JSON文字列の解析
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error{context_msg}: {e}")
        raise InvalidJSONError(
            message=f"Failed to parse JSON{context_msg}",
            raw_text=json_text,
            parse_error=str(e),
        )

    # 2. 型チェック（辞書であることを確認）
    if not isinstance(data, dict):
        logger.error(f"JSON is not a dictionary{context_msg}")
        raise InvalidJSONError(
            message=f"Expected JSON object (dict), got {type(data).__name__}{context_msg}",
            raw_text=json_text,
        )

    # 3. スキーマに基づく検証
    try:
        _validate_schema(data, schema, context_msg)
    except InvalidJSONError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during schema validation{context_msg}: {e}")
        raise InvalidJSONError(
            message=f"Schema validation failed{context_msg}: {str(e)}",
            raw_text=json_text,
        )

    logger.debug(f"JSON validation passed{context_msg}")
    return data


def _validate_schema(data: dict, schema: dict, context_msg: str) -> None:
    """スキーマに基づいてデータ構造を検証する

    Args:
        data: 検証対象のデータ
        schema: スキーマ定義
        context_msg: コンテキストメッセージ

    Raises:
        InvalidJSONError: スキーマに適合しない場合
    """
    missing_keys = []

    for key, rules in schema.items():
        # 必須キーの存在確認
        if rules.get("required", False) and key not in data:
            missing_keys.append(key)
            continue

        # キーが存在しない場合はスキップ（オプショナル）
        if key not in data:
            continue

        value = data[key]
        expected_type = rules.get("type")

        # 型チェック
        if expected_type == "str" and not isinstance(value, str):
            raise InvalidJSONError(
                message=f"Key '{key}' should be string, got {type(value).__name__}{context_msg}",
                missing_keys=[key],
            )

        elif expected_type == "list" and not isinstance(value, list):
            raise InvalidJSONError(
                message=f"Key '{key}' should be list, got {type(value).__name__}{context_msg}",
                missing_keys=[key],
            )

        elif expected_type == "dict" and not isinstance(value, dict):
            raise InvalidJSONError(
                message=f"Key '{key}' should be dict, got {type(value).__name__}{context_msg}",
                missing_keys=[key],
            )

        # リスト内の要素の検証
        if expected_type == "list" and "item_schema" in rules:
            item_schema = rules["item_schema"]
            for i, item in enumerate(value):
                if not isinstance(item, dict):
                    raise InvalidJSONError(
                        message=f"Key '{key}[{i}]' should be dict, got {type(item).__name__}{context_msg}",
                        missing_keys=[f"{key}[{i}]"],
                    )
                # 再帰的にアイテムスキーマを検証
                try:
                    _validate_schema(item, item_schema, f"{context_msg} in {key}[{i}]")
                except InvalidJSONError as e:
                    # リストアイテムのエラーに親キー情報を追加
                    raise InvalidJSONError(
                        message=e.message,
                        missing_keys=[f"{key}[{i}].{mk}" for mk in (e.missing_keys or [])],
                    )

    # 必須キーが欠けている場合
    if missing_keys:
        logger.error(f"Missing required keys{context_msg}: {missing_keys}")
        raise InvalidJSONError(
            message=f"Missing required keys{context_msg}: {', '.join(missing_keys)}",
            missing_keys=missing_keys,
        )


def extract_json_from_text(text: str) -> str:
    """テキストからJSON部分を抽出する

    Gemini APIのレスポンスにはJSONの前後に余分なテキストが含まれる場合があるため、
    JSON部分のみを抽出します。

    Args:
        text: JSON文字列を含むテキスト

    Returns:
        str: 抽出されたJSON文字列

    Raises:
        InvalidJSONError: JSONが見つからない場合

    Example:
        >>> text = "Here is the data: {\"key\": \"value\"} end"
        >>> json_str = extract_json_from_text(text)
        >>> print(json_str)  # '{"key": "value"}'
    """
    # 改行を除去
    text = text.replace("\n", "")

    # JSONの開始位置を探す
    json_start = text.find("{")
    if json_start == -1:
        logger.error("No opening brace found in text")
        raise InvalidJSONError(
            message="Could not find JSON opening brace '{' in response",
            raw_text=text,
        )

    # JSONの終了位置を探す（最後の}）
    json_end = text.rfind("}")
    if json_end == -1 or json_end < json_start:
        logger.error("No closing brace found in text")
        raise InvalidJSONError(
            message="Could not find JSON closing brace '}' in response",
            raw_text=text,
        )

    # JSON部分を抽出
    json_text = text[json_start : json_end + 1]
    logger.debug(f"Extracted JSON: {json_text[:100]}...")

    return json_text


def validate_novel_init_json(
    json_text: str, expected_chapter_count: Optional[int] = None, context: str = "generate_init"
) -> dict:
    """generate_init用のJSON検証（高レベル関数）

    extract_json_from_text、validate_json_response、および追加の
    ビジネスロジック検証を組み合わせた便利な関数です。

    Args:
        json_text: Gemini APIから返されたテキスト
        expected_chapter_count: 期待される章の数（検証に使用）
        context: コンテキスト情報

    Returns:
        dict: 検証済みのJSON辞書

    Raises:
        InvalidJSONError: 検証失敗時

    Example:
        >>> response_text = model.generate_content(...).text
        >>> data = validate_novel_init_json(response_text, expected_chapter_count=5)
        >>> print(data["title"])
    """
    # 1. JSONを抽出
    try:
        extracted_json = extract_json_from_text(json_text)
    except InvalidJSONError:
        raise

    # 2. JSONをバリデーション
    data = validate_json_response(extracted_json, schema=NOVEL_INIT_SCHEMA, context=context)

    # 3. ビジネスロジックの検証（章の数）
    if expected_chapter_count is not None:
        actual_count = len(data.get("chapter_plots", []))
        if actual_count != expected_chapter_count:
            logger.warning(f"Chapter count mismatch: expected {expected_chapter_count}, got {actual_count}")
            raise InvalidJSONError(
                message=f"Expected {expected_chapter_count} chapter_plots, but got {actual_count}",
                raw_text=json_text,
                missing_keys=["chapter_plots"],
            )

    # 4. charactersの最小数チェック（少なくとも1人は必要）
    if not data.get("characters") or len(data["characters"]) == 0:
        logger.warning("No characters defined in JSON")
        raise InvalidJSONError(
            message="At least one character must be defined",
            raw_text=json_text,
            missing_keys=["characters"],
        )

    logger.info(f"Successfully validated novel init JSON with {len(data['chapter_plots'])} chapters")
    return data


def create_custom_schema(schema_definition: dict) -> dict:
    """カスタムスキーマを作成するヘルパー関数

    プロンプトの改善時に新しいスキーマを簡単に定義できるようにします。

    Args:
        schema_definition: スキーマ定義辞書

    Returns:
        dict: バリデーション用のスキーマ

    Example:
        >>> custom_schema = create_custom_schema({
        ...     "field1": {"type": "str", "required": True},
        ...     "field2": {"type": "list", "required": False}
        ... })
        >>> data = validate_json_response(json_text, schema=custom_schema)
    """
    return schema_definition
