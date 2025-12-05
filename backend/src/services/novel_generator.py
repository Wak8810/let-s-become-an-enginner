import logging
import os

from google import generativeai as genai

from src.services.gemini_exceptions import NetworkError
from src.services.gemini_exceptions import TimeoutError as GeminiTimeoutError
from src.services.gemini_retry import retry_for_json_generation, retry_for_novel_generation
from src.services.gemini_validator import (
    get_response_metadata,
    get_safe_text,
    validate_novel_init_json,
)

# ロガーの設定
logger = logging.getLogger(__name__)


# 小説生成系を担当するクラス
class NovelGenerator:
    def __init__(self):
        self.model = None
        self.is_generating = False

    def setup_ai(self):
        """Gemini APIの初期設定を行う

        環境変数からAPIキーとモデルバージョンを読み込み、GenerativeModelを初期化します。

        Raises:
            ValueError: モデルバージョンが不正な場合
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        model_version = os.getenv("GEMINI_MODEL", "2.0-flash")
        if model_version not in ["2.0-flash", "2.5-flash"]:
            raise ValueError(f"Invalid GEMINI_MODEL: {model_version}. Must be '2.0-flash' or '2.5-flash'.")

        self.model = genai.GenerativeModel(f"gemini-{model_version}")
        logger.info(f"Gemini API initialized with model: gemini-{model_version}")

    @retry_for_novel_generation
    def generate_plot(self, genre: str, text_length: int) -> str:
        """小説のプロットを生成する

        指定されたジャンルと文字数に基づいて、小説の全体プロットを生成します。
        自動リトライ機構により、一時的なエラーから復旧を試みます。

        Args:
            genre: 小説のジャンル
            text_length: 目標文字数

        Returns:
            str: 生成されたプロット

        Raises:
            GeminiAPIError: API呼び出しでエラーが発生した場合
        """
        logger.info(f"Generating plot for genre='{genre}', text_length={text_length}")

        try:
            response = self.model.generate_content(
                f"{genre}の小説のプロットを具体的に作成してください。小説は{text_length}文字程度になります。",
                request_options={"timeout": 600},
            )

            # レスポンスを検証して安全にテキストを取得
            text = get_safe_text(response, context="generate_plot")

            # メタデータをログに記録
            metadata = get_response_metadata(response)
            logger.info(f"Plot generated successfully. Tokens used: {metadata.get('total_token_count', 'N/A')}")

            return text

        except Exception as e:
            # 標準ライブラリのエラーをGemini例外にラップ
            if isinstance(e, ConnectionError):
                logger.error(f"Network error in generate_plot: {e}")
                raise NetworkError(message=f"Network error while generating plot: {str(e)}", original_error=e)
            elif isinstance(e, TimeoutError):
                logger.error(f"Timeout error in generate_plot: {e}")
                raise GeminiTimeoutError(message=f"Timeout while generating plot: {str(e)}", timeout_seconds=600)
            else:
                # その他のエラーはそのまま投げる（GeminiAPIErrorは既に処理済み）
                raise

    @retry_for_json_generation
    def generate_init(self, text_length: int, chapter_count: int, other: dict) -> dict:
        """小説の初期データ（設定、プロット、登場人物等）を生成する

        JSON形式で小説の基本情報を生成します。
        自動リトライ機構により、JSON解析エラーからの復旧も試みます。

        Args:
            text_length: 目標文字数
            chapter_count: 章の数
            other: その他の設定
                genre (str): ジャンル
                mood (str): 雰囲気
                style (str): 文体

        Returns:
            dict: 小説の初期データ（title, summary, plot, characters, chapter_plots）

        Raises:
            GeminiAPIError: API呼び出しまたはJSON検証でエラーが発生した場合
        """
        # パラメータの解凍
        genre = other.get("genre", "指定なし")
        mood = other.get("mood", "指定なし")
        style = other.get("style", "指定なし")

        logger.info(
            f"Generating initial data: text_length={text_length}, chapter_count={chapter_count}, genre='{genre}', mood='{mood}', style='{style}'"
        )

        try:
            response = self.model.generate_content(
                f"""下記の内容の小説を作成するのに、設定やプロット、登場人物等を具体的に作成してください。小説は全体で{text_length}文字程度、章は{chapter_count}です。
            - ジャンル: {genre}
            - 雰囲気: {mood}
            - 文章スタイル: {style}

            出力は以下のjson形式で行ってください、その他は一切出力してはいけません。:
            {{
                "title":(novel's title),
                "summary":(summary),
                "plot":(plot),
                "characters":[
                    {{
                        "name":(name),
                        "role":(role)
                    }},
                    (generate characters you needed)
                ],
                "chapter_plots":[
                    {{
                        "plot":(plot)
                    }},
                    (generate same number of items as chapters)
                ]
            }}
            """,
                request_options={"timeout": 600},
            )

            # レスポンスを検証して安全にテキストを取得
            text = get_safe_text(response, context="generate_init")

            # JSONを検証してパース（章の数もチェック）
            data = validate_novel_init_json(text, expected_chapter_count=chapter_count, context="generate_init")

            # メタデータをログに記録
            metadata = get_response_metadata(response)
            logger.info(
                f"Initial data generated successfully. "
                f"Title: '{data.get('title', 'N/A')}', "
                f"Chapters: {len(data.get('chapter_plots', []))}, "
                f"Characters: {len(data.get('characters', []))}, "
                f"Tokens used: {metadata.get('total_token_count', 'N/A')}"
            )

            return data

        except Exception as e:
            # 標準ライブラリのエラーをGemini例外にラップ
            if isinstance(e, ConnectionError):
                logger.error(f"Network error in generate_init: {e}")
                raise NetworkError(message=f"Network error while generating initial data: {str(e)}", original_error=e)
            elif isinstance(e, TimeoutError):
                logger.error(f"Timeout error in generate_init: {e}")
                raise GeminiTimeoutError(
                    message=f"Timeout while generating initial data: {str(e)}", timeout_seconds=600
                )
            else:
                # その他のエラーはそのまま投げる（GeminiAPIErrorは既に処理済み）
                raise

    @retry_for_novel_generation
    def generate_chapter(self, plot: str, style: str = "", previous_chapter: str = None, chapter_num: int = 0) -> str:
        """小説の章を生成する

        指定されたプロットと設定に基づいて、特定の章の内容を生成します。
        前章の内容を参照することで、ストーリーの連続性を保ちます。

        Args:
            plot: 小説の全体プロット
            style: 文体（オプション）
            previous_chapter: 前の章の内容（オプション）
            chapter_num: 章番号

        Returns:
            str: 生成された章の内容

        Raises:
            GeminiAPIError: API呼び出しでエラーが発生した場合
        """
        logger.info(f"Generating chapter {chapter_num}")

        try:
            # プロンプトを構築
            prompt = f"{plot}の小説の第{chapter_num}章を、以下の情報を参考に生成してください。"
            if style and isinstance(style, str):
                prompt += f"\n- 文体:{style}"
            if previous_chapter:
                # 前の章が長すぎる場合は末尾のみを使用（コンテキスト節約）
                prev_excerpt = previous_chapter[-2000:] if len(previous_chapter) > 2000 else previous_chapter
                prompt += f"\n下記は前の章です:\n{prev_excerpt}"

            response = self.model.generate_content(
                prompt,
                request_options={"timeout": 600},
            )

            # レスポンスを検証して安全にテキストを取得
            text = get_safe_text(response, context=f"generate_chapter_{chapter_num}")

            # メタデータをログに記録
            metadata = get_response_metadata(response)
            logger.info(
                f"Chapter {chapter_num} generated successfully. "
                f"Length: {len(text)} chars, "
                f"Tokens used: {metadata.get('total_token_count', 'N/A')}"
            )

            return text

        except Exception as e:
            # 標準ライブラリのエラーをGemini例外にラップ
            if isinstance(e, ConnectionError):
                logger.error(f"Network error in generate_chapter (chapter {chapter_num}): {e}")
                raise NetworkError(
                    message=f"Network error while generating chapter {chapter_num}: {str(e)}", original_error=e
                )
            elif isinstance(e, TimeoutError):
                logger.error(f"Timeout error in generate_chapter (chapter {chapter_num}): {e}")
                raise GeminiTimeoutError(
                    message=f"Timeout while generating chapter {chapter_num}: {str(e)}", timeout_seconds=600
                )
            else:
                # その他のエラーはそのまま投げる（GeminiAPIErrorは既に処理済み）
                raise

    # 小説生成のジェネレーター.
    def generate_novel(self, genre, text_length, style):
        self.is_generating = True
        plot = self.generate_plot(genre, text_length)
        yield 0, plot
        total_text_len = 0
        previous_chapter = None
        count = 1
        while True:
            chapter = self.generate_chapter(
                plot=plot, style=style, previous_chapter=previous_chapter, chapter_num=count
            )
            total_text_len += len(chapter)
            previous_chapter = chapter
            yield count, chapter
            if total_text_len > text_length:
                self.is_generating = False
                return
            previous_chapter = chapter
            count += 1
