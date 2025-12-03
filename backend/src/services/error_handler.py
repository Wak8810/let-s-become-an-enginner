"""エラーハンドラモジュール

Gemini APIエラー発生時のデータベース状態管理を行います。
NovelとChapterのステータス更新、エラー情報の記録、復旧処理などを提供します。
"""

import logging
from datetime import datetime
from typing import List, Optional

from src.database import db
from src.models import Chapter, Novel, NovelStatus
from src.services.gemini_exceptions import GeminiAPIError

# ロガーの設定
logger = logging.getLogger(__name__)


def mark_novel_as_failed(
    novel_id: str,
    error_message: str,
    error_type: Optional[str] = None,
    failed_chapter_id: Optional[str] = None,
    db_session=None,
) -> bool:
    """小説のステータスをFAILEDに更新する

    小説全体をFAILEDにマークします。
    特定の章の失敗が原因の場合、その章だけをFAILEDにし、
    それ以降の章はPENDINGのままにします。

    Args:
        novel_id: 小説のID
        error_message: エラーメッセージ
        error_type: エラーの種類（例: "SafetyFilterError"）
        failed_chapter_id: 失敗した章のID（章の失敗が原因の場合）
        db_session: データベースセッション（Noneの場合はdb.sessionを使用）

    Returns:
        bool: 更新が成功した場合True、失敗した場合False

    Example:
        >>> mark_novel_as_failed(
        ...     novel_id="abc123",
        ...     error_message="Safety filter blocked content",
        ...     error_type="SafetyFilterError",
        ...     failed_chapter_id="def456"
        ... )
        True
    """
    session = db_session or db.session

    try:
        # 小説を取得
        novel = session.get(Novel, novel_id)
        if not novel:
            logger.error(f"Novel not found for marking as failed: {novel_id}")
            return False

        # 小説のステータスを更新
        novel.status = NovelStatus.FAILED
        novel.updated_at = datetime.now(timezone.utc)

        # 特定の章が失敗した場合、その章だけをFAILEDにする
        if failed_chapter_id:
            failed_chapter = session.get(Chapter, failed_chapter_id)
            if failed_chapter:
                failed_chapter.status = NovelStatus.FAILED
                failed_chapter.updated_at = datetime.now(timezone.utc)
                failed_chapter_number = failed_chapter.chapter_number
            else:
                logger.warning(f"Failed chapter not found: {failed_chapter_id}")
                failed_chapter_number = None
        else:
            failed_chapter_number = None

        session.commit()

        # ログに記録
        error_info = f"Type: {error_type}, " if error_type else ""
        chapter_info = f"Failed chapter: {failed_chapter_number}, " if failed_chapter_number else ""
        logger.error(
            f"Novel marked as FAILED - "
            f"ID: {novel_id}, "
            f"Title: '{novel.title}', "
            f"{chapter_info}"
            f"{error_info}"
            f"Message: {error_message}"
        )

        return True

    except Exception as e:
        logger.error(f"Failed to mark novel as failed (ID: {novel_id}): {e}")
        session.rollback()
        return False


def mark_chapter_as_failed(
    chapter_id: str, error_message: str, error_type: Optional[str] = None, db_session=None
) -> bool:
    """特定のチャプターのステータスをFAILEDに更新する

    単一のチャプターのステータスをFAILEDに変更します。
    エラー情報はログに記録されます。

    Args:
        chapter_id: チャプターのID
        error_message: エラーメッセージ
        error_type: エラーの種類
        db_session: データベースセッション

    Returns:
        bool: 更新が成功した場合True、失敗した場合False

    Example:
        >>> mark_chapter_as_failed(
        ...     chapter_id="def456",
        ...     error_message="Timeout during generation",
        ...     error_type="TimeoutError"
        ... )
        True
    """
    session = db_session or db.session

    try:
        # チャプターを取得
        chapter = session.get(Chapter, chapter_id)
        if not chapter:
            logger.error(f"Chapter not found for marking as failed: {chapter_id}")
            return False

        # チャプターのステータスを更新
        chapter.status = NovelStatus.FAILED
        chapter.updated_at = datetime.now(timezone.utc)

        session.commit()

        # ログに記録
        error_info = f"Type: {error_type}, " if error_type else ""
        logger.error(
            f"Chapter marked as FAILED - "
            f"Chapter ID: {chapter_id}, "
            f"Novel ID: {chapter.novel_id}, "
            f"Chapter Number: {chapter.chapter_number}, "
            f"{error_info}"
            f"Message: {error_message}"
        )

        return True

    except Exception as e:
        logger.error(f"Failed to mark chapter as failed (ID: {chapter_id}): {e}")
        session.rollback()
        return False


def recover_novel_status(novel_id: str, new_status: NovelStatus = NovelStatus.GENERATING, db_session=None) -> bool:
    """小説のステータスをFAILEDから復旧する

    リトライが成功した場合などに、ステータスをGENERATINGまたはCOMPLETEDに戻します。

    Args:
        novel_id: 小説のID
        new_status: 新しいステータス（デフォルト: GENERATING）
        db_session: データベースセッション

    Returns:
        bool: 更新が成功した場合True、失敗した場合False

    Example:
        >>> recover_novel_status("abc123", NovelStatus.GENERATING)
        True
    """
    session = db_session or db.session

    try:
        # 小説を取得
        novel = session.get(Novel, novel_id)
        if not novel:
            logger.error(f"Novel not found for recovery: {novel_id}")
            return False

        old_status = novel.status
        novel.status = new_status
        novel.updated_at = datetime.now(timezone.utc)

        session.commit()

        logger.info(
            f"Novel status recovered - "
            f"ID: {novel_id}, "
            f"Title: '{novel.title}', "
            f"Status: {old_status.value} -> {new_status.value}"
        )

        return True

    except Exception as e:
        logger.error(f"Failed to recover novel status (ID: {novel_id}): {e}")
        session.rollback()
        return False


def recover_chapter_status(chapter_id: str, new_status: NovelStatus = NovelStatus.COMPLETED, db_session=None) -> bool:
    """チャプターのステータスをFAILEDから復旧する

    リトライが成功した場合に、ステータスをCOMPLETEDに戻します。

    Args:
        chapter_id: チャプターのID
        new_status: 新しいステータス（デフォルト: COMPLETED）
        db_session: データベースセッション

    Returns:
        bool: 更新が成功した場合True、失敗した場合False

    Example:
        >>> recover_chapter_status("def456", NovelStatus.COMPLETED)
        True
    """
    session = db_session or db.session

    try:
        # チャプターを取得
        chapter = session.get(Chapter, chapter_id)
        if not chapter:
            logger.error(f"Chapter not found for recovery: {chapter_id}")
            return False

        old_status = chapter.status
        chapter.status = new_status
        chapter.updated_at = datetime.now(timezone.utc)

        session.commit()

        logger.info(
            f"Chapter status recovered - "
            f"Chapter ID: {chapter_id}, "
            f"Novel ID: {chapter.novel_id}, "
            f"Chapter Number: {chapter.chapter_number}, "
            f"Status: {old_status.value} -> {new_status.value}"
        )

        return True

    except Exception as e:
        logger.error(f"Failed to recover chapter status (ID: {chapter_id}): {e}")
        session.rollback()
        return False


def get_failed_novels(db_session=None) -> List[Novel]:
    """FAILEDステータスの小説一覧を取得する

    エラーで失敗した小説のリストを取得します。
    手動復旧やデバッグに使用できます。

    Args:
        db_session: データベースセッション

    Returns:
        List[Novel]: FAILEDステータスの小説のリスト

    Example:
        >>> failed_novels = get_failed_novels()
        >>> for novel in failed_novels:
        ...     print(f"Failed: {novel.title}")
    """
    session = db_session or db.session

    try:
        failed_novels = session.query(Novel).filter_by(status=NovelStatus.FAILED).all()
        return failed_novels
    except Exception as e:
        logger.error(f"Failed to retrieve failed novels: {e}")
        return []


def get_failed_chapters(novel_id: str, db_session=None) -> List[Chapter]:
    """特定の小説のFAILEDチャプター一覧を取得する

    Args:
        novel_id: 小説のID
        db_session: データベースセッション

    Returns:
        List[Chapter]: FAILEDステータスのチャプターのリスト

    Example:
        >>> failed_chapters = get_failed_chapters("abc123")
        >>> for chapter in failed_chapters:
        ...     print(f"Failed chapter: {chapter.chapter_number}")
    """
    session = db_session or db.session

    try:
        failed_chapters = (
            session.query(Chapter)
            .filter_by(novel_id=novel_id, status=NovelStatus.FAILED)
            .order_by(Chapter.chapter_number)
            .all()
        )
        return failed_chapters
    except Exception as e:
        logger.error(f"Failed to retrieve failed chapters for novel {novel_id}: {e}")
        return []


def handle_chapter_generation_failure(novel_id: str, chapter_id: str, error: Exception, db_session=None) -> None:
    """章の生成が完全に失敗した場合の処理

    リトライが全て失敗した章について、章と小説のステータスを更新します。
    章はFAILEDにマークされ、小説全体もFAILEDになります。
    これにより、それ以降の章の生成が停止されます。

    Args:
        novel_id: 小説のID
        chapter_id: 失敗した章のID
        error: 発生したエラー
        db_session: データベースセッション

    Example:
        >>> try:
        ...     content = novelist.write_next_chapter()
        ... except GeminiAPIError as e:
        ...     handle_chapter_generation_failure(novel_id, chapter_id, e)
        ...     return  # 生成を停止
    """
    error_message = str(error)
    error_type = type(error).__name__

    # Gemini API関連のエラーの場合、詳細情報を取得
    if isinstance(error, GeminiAPIError):
        if hasattr(error, "finish_reason") and error.finish_reason:
            error_message += f" (finish_reason: {error.finish_reason})"
        if hasattr(error, "details") and error.details:
            error_message += f" | Details: {error.details}"

    # 章をFAILEDにマーク
    mark_chapter_as_failed(
        chapter_id=chapter_id, error_message=error_message, error_type=error_type, db_session=db_session
    )

    # 小説全体もFAILEDにマーク（この章で生成停止）
    mark_novel_as_failed(
        novel_id=novel_id,
        error_message=f"Chapter generation failed: {error_message}",
        error_type=error_type,
        failed_chapter_id=chapter_id,
        db_session=db_session,
    )


def handle_generation_error(
    error: Exception, novel_id: Optional[str] = None, chapter_id: Optional[str] = None, db_session=None
) -> None:
    """生成エラーを統合的に処理する（汎用）

    Gemini APIエラーを検出し、適切なデータベース更新とログ記録を行います。
    章の生成失敗の場合は handle_chapter_generation_failure() の使用を推奨します。

    Args:
        error: 発生したエラー
        novel_id: 小説のID（小説レベルのエラーの場合）
        chapter_id: チャプターのID（チャプターレベルのエラーの場合）
        db_session: データベースセッション

    Example:
        >>> try:
        ...     plot = generator.generate_plot(...)
        ... except GeminiAPIError as e:
        ...     handle_generation_error(e, novel_id="abc123")
    """
    error_message = str(error)
    error_type = type(error).__name__

    # Gemini API関連のエラーの場合、詳細情報を取得
    if isinstance(error, GeminiAPIError):
        if hasattr(error, "finish_reason") and error.finish_reason:
            error_message += f" (finish_reason: {error.finish_reason})"
        if hasattr(error, "details") and error.details:
            error_message += f" | Details: {error.details}"

    # チャプターレベルのエラー
    if chapter_id:
        mark_chapter_as_failed(
            chapter_id=chapter_id, error_message=error_message, error_type=error_type, db_session=db_session
        )

    # 小説レベルのエラー
    elif novel_id:
        mark_novel_as_failed(
            novel_id=novel_id, error_message=error_message, error_type=error_type, db_session=db_session
        )

    else:
        logger.warning(
            f"Generation error occurred but no novel_id or chapter_id provided: {error_type}: {error_message}"
        )


def update_chapter_status(chapter_id: str, status: NovelStatus, db_session=None) -> bool:
    """チャプターのステータスを更新する

    汎用的なステータス更新関数です。

    Args:
        chapter_id: チャプターのID
        status: 新しいステータス
        db_session: データベースセッション

    Returns:
        bool: 更新が成功した場合True、失敗した場合False

    Example:
        >>> update_chapter_status("def456", NovelStatus.GENERATING)
        True
    """
    session = db_session or db.session

    try:
        chapter = session.get(Chapter, chapter_id)
        if not chapter:
            logger.error(f"Chapter not found for status update: {chapter_id}")
            return False

        old_status = chapter.status
        chapter.status = status
        chapter.updated_at = datetime.now(timezone.utc)

        session.commit()

        logger.debug(
            f"Chapter status updated - "
            f"ID: {chapter_id}, "
            f"Chapter Number: {chapter.chapter_number}, "
            f"Status: {old_status.value} -> {status.value}"
        )

        return True

    except Exception as e:
        logger.error(f"Failed to update chapter status (ID: {chapter_id}): {e}")
        session.rollback()
        return False


def update_novel_status(novel_id: str, status: NovelStatus, db_session=None) -> bool:
    """小説のステータスを更新する

    汎用的なステータス更新関数です。

    Args:
        novel_id: 小説のID
        status: 新しいステータス
        db_session: データベースセッション

    Returns:
        bool: 更新が成功した場合True、失敗した場合False

    Example:
        >>> update_novel_status("abc123", NovelStatus.COMPLETED)
        True
    """
    session = db_session or db.session

    try:
        novel = session.get(Novel, novel_id)
        if not novel:
            logger.error(f"Novel not found for status update: {novel_id}")
            return False

        old_status = novel.status
        novel.status = status
        novel.updated_at = datetime.now(timezone.utc)

        session.commit()

        logger.debug(
            f"Novel status updated - "
            f"ID: {novel_id}, "
            f"Title: '{novel.title}', "
            f"Status: {old_status.value} -> {status.value}"
        )

        return True

    except Exception as e:
        logger.error(f"Failed to update novel status (ID: {novel_id}): {e}")
        session.rollback()
        return False
