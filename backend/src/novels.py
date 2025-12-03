import json
import logging
import threading

from dotenv import load_dotenv
from flask import Blueprint, Response, request, stream_with_context
from flask_restx import Namespace, Resource, fields, reqparse

from src.database import db
from src.models import Chapter, Genre, Novel, NovelStatus, User
from src.services.error_handler import handle_chapter_generation_failure, mark_novel_as_failed
from src.services.novel_generator import NovelGenerator  # ここでこれを使わないほうが綺麗だが必須ではない.
from src.services.novelist import Novelist

load_dotenv()

# Set up logger for this module
logger = logging.getLogger(__name__)

# URI "/novels/" 以下を定義.
novels_module = Blueprint("novel_module", __name__)
api = Namespace("novels", description="小説生成・管理用エンドポイント群")


# リストからcompare_funcがTrueを返す要素のインデックスを得る.
def list_finder(tar_list, compare_func):
    for i in range(len(tar_list)):
        if compare_func(tar_list[i]):
            return i
    return -1


# -- threading --
# バックエンドタスク.
def novelist_bg_task_runner(novelist, novel_id):
    """バックグラウンドで小説の章を順次生成するタスク

    第2章以降を順番に生成し、データベースに保存します。
    エラーが発生した場合は生成を停止し、適切にステータスを更新します。

    Args:
        novelist: Novelistインスタンス
        novel_id: 小説のID
    """
    print("bg task started")
    from app import app

    if not isinstance(novelist, Novelist):
        return

    with app.app_context():
        try:
            chapters_data = db.session.query(Chapter).filter_by(novel_id=novel_id).all()

            # 小説のステータスをGENERATINGに更新
            novel_data = db.session.get(Novel, novel_id)
            if not novel_data:
                print(f"bg:: error : novel not found -> task killed - id:{novel_id}")
                return

            novel_data.status = NovelStatus.GENERATING
            db.session.commit()

            # 章を順次生成
            while not novelist.is_completed():
                # 対象chapterの探索
                chpind = list_finder(chapters_data, lambda x: x.chapter_number == novelist.next_chapter_num)
                chapter = None

                if chpind == -1:
                    # チャプターがDBに存在しない場合は作成（通常は発生しないはず）
                    print(f"bg:: warning: generated chapter but data not found - number:{novelist.next_chapter_num}")
                    new_chapter = Chapter(
                        chapter_number=novelist.next_chapter_num,
                        content="NO CONTENT",
                        novel_id=novel_id,
                        status=NovelStatus.GENERATING,
                        plot=novelist.chapter_plots[novelist.next_chapter_num - 1],
                    )
                    db.session.add(new_chapter)
                    chapter = new_chapter
                else:
                    chapter = chapters_data[chpind]

                # チャプターのステータスをGENERATINGに更新
                chapter.status = NovelStatus.GENERATING
                db.session.commit()

                # 章を生成（エラーは上位でキャッチ）
                try:
                    print(f"bg:: start generating chapter: {novelist.next_chapter_num}")
                    chapter_content = novelist.write_next_chapter()
                    chapter.content = chapter_content
                    chapter.status = NovelStatus.COMPLETED
                    db.session.commit()
                    print("bg:: chapter generated and commited")

                except Exception as e:
                    # 章の生成が完全に失敗した場合
                    print(f"bg:: error: chapter generation failed - {type(e).__name__}: {e}")
                    handle_chapter_generation_failure(
                        novel_id=novel_id, chapter_id=chapter.id, error=e, db_session=db.session
                    )
                    print("bg:: task stopped due to chapter generation failure")
                    return  # 生成を停止

            # 全章完了
            novel_data.status = NovelStatus.COMPLETED
            db.session.commit()
            print("bg:: novel commited, task done")

        except Exception as e:
            # タスク全体のエラー（DB接続エラーなど）
            print(f"bg:: critical error: background task failed - {type(e).__name__}: {e}")
            try:
                # 小説をFAILEDにマーク
                mark_novel_as_failed(
                    novel_id=novel_id,
                    error_message=f"Background task failed: {str(e)}",
                    error_type=type(e).__name__,
                    db_session=db.session,
                )
            except Exception as mark_error:
                # エラー処理自体が失敗しても無視
                print(f"bg:: error: failed to mark novel as failed - {mark_error}")
            print("bg:: task terminated due to critical error")


# --- model ---
novel_start_model = api.model(
    "NovelStreams",
    {
        "user_id": fields.String(description="user's id"),
        "genre": fields.String(description="novel's genre // now, only this is sent to ai -2025/11/14 3:00"),
        "textLen": fields.Integer(required=True, description="required novel's length"),
        "style": fields.String(description="novel's style"),
    },
)
novel_init_model = api.model(
    "NovelInit",
    {
        "user_id": fields.String(description="user's id"),
        "novel_setting": fields.Nested(
            api.model(
                "NovelSetting",
                {
                    "ideal_text_length": fields.Integer(description="request of novel's text length"),
                    "genre": fields.String(description="genre of novel"),
                    "style": fields.String(description="style"),
                },
            )
        ),
    },
)
novel_item_model = api.model(
    "NovelListItem",
    {
        "novel_id": fields.String(attribute="id"),
        "title": fields.String(),
        "overall_plot": fields.String(),
        "genre": fields.String(attribute="genre_code"),
        "style": fields.String(),
        "text_length": fields.Integer(),
        "user_id": fields.String(),
        "created_at": fields.DateTime(),
        "updated_at": fields.DateTime(),
    },
)
novel_content_model = api.model(
    "NovelContent",
    {
        "novel_status": fields.String(),
        "current_chapter": fields.Integer(description="現在生成中または失敗した章番号"),
        "total_chapter_number": fields.Integer(description="全章数"),
        "new_chapters": fields.List(
            fields.Nested(api.model("Chapter", {"index": fields.Integer(), "content": fields.String()}))
        ),
    },
)
chapter_item_model = api.model(
    "ChapterListItem",
    {
        "chapter_id": fields.String(attribute="id"),
        "content": fields.String(),
        "created_at": fields.DateTime(),
        "updated_at": fields.DateTime(),
    },
)
novel_text_model = api.model(
    "NovelText",
    {
        "text": fields.String(),
        "last_chapter": fields.Integer(),
        "total_chapter_number": fields.Integer(description="全章数"),
        "has_all_chapters": fields.Boolean(),
    },
)
# -- parser --
novels_text_parser = reqparse.RequestParser()
novels_text_parser.add_argument("X-User-ID", location="headers", type=str, required=True, help="User id")
novels_contents_parser = reqparse.RequestParser()
novels_contents_parser.add_argument("X-User-ID", location="headers", type=str, required=True, help="User id")
novels_contents_parser.add_argument(
    "X-Current-Index", location="headers", type=str, required=True, help="フロント側の持っている最後の章の番号"
)


# "/novels/" : 小説一覧取得のエンドポイント.
@api.route("/")
class NovelList(Resource):
    @api.doc("get_all_novels_for_test")
    @api.marshal_list_with(novel_item_model)
    def get(self):
        """登録されている小説一覧を返す

        Returns:
            list: 登録されている小説の一覧
        """
        novels = db.session.query(Novel).all()
        return novels


# "/novels/streams" : 小説生成の開始時のエンドポイント.
@api.route("/streams")
class NovelStream(Resource):
    @api.doc("post_novels")
    @api.expect(novel_start_model)
    def post(self):
        """最初に送る小説の設定的なの

        Returns:

        """
        try:
            # リクエストボディの解凍.
            requested_param = request.get_json()
            user_id = requested_param.get("user_id")
            genre = requested_param.get("genre")
            text_length = requested_param.get("textLen")
            style = requested_param.get("style")

            # データベースからuser_idに対応するデータを取得
            user_data = db.session.query(User).filter_by(id=user_id).first()
            if not user_data:
                return {"error": f"User {user_id} not found"}, 404

            # データベースに新たな小説データを登録
            novel_data = Novel(
                style=style,
                genre_code=genre,
                text_length=text_length,
                title="test",  # TODO: タイトル生成機能実装時に更新
                overall_plot="",  # TODO: プロット生成後に更新
                user_id=user_data.id,
            )
            db.session.add(novel_data)
            db.session.commit()

            # 小説IDを保存（ジェネレータ内でも安全に使用可能）
            novel_id = novel_data.id

            # ai-apiとのやり取り
            novelist = NovelGenerator()
            novelist.setup_ai()

            # NovelGeneratorのgenerate_novelメソッドの出力に以下の処理をする.
            # - DB登録
            # - レスポンスのjsonボディに変形
            def novel_generater():
                try:
                    gen = novelist.generate_novel(genre, text_length, style)
                    count, plot = next(gen)

                    # プロットの保存
                    novel = db.session.get(Novel, novel_id)
                    novel.overall_plot = plot
                    db.session.commit()
                    print(f"Plot generated: {count}")
                    yield json.dumps({"response_count": count, "plot": plot}, ensure_ascii=False) + "\n"

                    for count, chapter in gen:
                        print(f"Chapter {count} generated, length: {len(chapter)}")
                        chapter_data = Chapter(chapter_number=count, content=chapter, novel_id=novel_id)
                        db.session.add(chapter_data)
                        print(f"Chapter {count} added to session")
                        yield json.dumps({"response_count": count, "chapter": chapter}, ensure_ascii=False) + "\n"

                    db.session.commit()
                    print("All chapters committed to database")
                    yield json.dumps({"response_count": count + 1, "fin": True}, ensure_ascii=False) + "\n"
                except Exception as e:
                    print(f"Error in novel_generater: {str(e)}")
                    import traceback

                    traceback.print_exc()
                    yield json.dumps({"error": str(e)}, ensure_ascii=False) + "\n"

            return Response(
                stream_with_context(novel_generater()),
                mimetype="application/json",
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
        except Exception as e:
            return {"status": False, "error": str(e)}


@api.route("/<string:novel_id>")
class NovelDetail(Resource):
    @api.doc("get_novel_detail", params={"novel_id": "詳細情報を取得したい小説のID"})
    @api.marshal_with(novel_item_model)
    def get(self, novel_id):
        """指定された小説の詳細情報を返す

        Args:
            novel_id (str): 小説のID

        Returns:
            Dict: 指定された小説の詳細情報
        """
        novel = db.session.get(Novel, novel_id)
        if not novel:
            api.abort(404, f"Novel {novel_id} not found")
        return novel


@api.route("/<string:novel_id>/chapters")
class NovelChapters(Resource):
    @api.doc("get_novel_chapters", params={"novel_id": "小説のID"})
    @api.marshal_list_with(chapter_item_model)
    def get(self, novel_id):
        """指定された小説の全チャプター一覧を返す

        Args:
            novel_id (str): 小説のID

        Returns:
            list: 指定された小説の全チャプター一覧
        """
        # データベースからnovel_idに対応するデータを取得
        chapters = db.session.query(Chapter).filter_by(novel_id=novel_id).order_by(Chapter.chapter_number).all()
        return chapters


@api.route("/<string:novel_id>/contents")
class NovelContent(Resource):
    @api.doc("get_novel_text", params={"novel_id": "小説のID"})
    @api.expect(novels_contents_parser)
    @api.marshal_with(novel_content_model)
    def get(self, novel_id):
        """指定された章以降をリストにして返す

        Args:
            novel_id (str): 小説のID

        Returns:
            dict: 小説のID、タイトル、結合されたテキスト内容
        """
        novel = db.session.get(Novel, novel_id)
        user_id = request.headers.get("X-User-ID")
        current_index = request.headers.get("X-Current-Index")
        # 情報なしエラー.
        if not user_id:
            api.abort(401, "Authorization header 'X-User-ID' is required")
        if not current_index:
            api.abort(401, "Authorization header 'X-Current-Index' is required")
        current_index = int(current_index)
        # 小説なしエラー.
        if not novel:
            api.abort(404, f"Novel not found - id:{novel_id}")
        # ユーザーの権限なしエラー.
        if novel.user_id != user_id:
            api.abort(403, "You do not have permission to access this novel")

        chapters = db.session.query(Chapter).filter_by(novel_id=novel_id).order_by(Chapter.chapter_number).all()

        # 現在生成中または失敗した章番号を特定
        current_chapter = None
        for chapter in chapters:
            if chapter.status in [NovelStatus.GENERATING, NovelStatus.FAILED]:
                current_chapter = chapter.chapter_number
                break

        # 完成した章のみを順番に返す
        results = []
        for i in range(current_index, len(chapters)):
            if chapters[i].status == NovelStatus.COMPLETED:
                results.append({"index": i + 1, "content": chapters[i].content})
            else:
                break

        return {
            "novel_status": novel.status.name,
            "current_chapter": current_chapter or len(chapters),
            "total_chapter_number": len(chapters),
            "new_chapters": results,
        }


@api.route("/init")
class NovelInit(Resource):
    @api.doc("post_init")
    @api.expect(novel_init_model)
    def post(self):
        """小説生成ジョブを開始し、第1章の内容を返す

        Request Body:
            - user_id (string): ユーザーID
            - novel_setting (dict):
            - - ideal_text_length (int): 目標文字数
            - - genre (string): sf, fantasy, mystery, horror, romance, history, light_novel, youthのどれか
            - - style (string): 文体

        Returns:
            dict: novel_id(string), title(string), total_chapter_number(int), first_chapter_text(string)
        """
        try:
            # データ解凍.
            requested_param = request.get_json()
            user_id = requested_param.get("user_id")
            novel_setting = requested_param.get("novel_setting")
            if not isinstance(novel_setting, dict):
                return {"error": "Missing or invalid 'novel_setting' in request payload."}, 400
            text_length = novel_setting.get("ideal_text_length")
            if text_length is None:
                return {"error": "Missing 'ideal_text_length' in 'novel_setting'."}, 400
            novel_other_settings = novel_setting.copy()
            novel_other_settings.pop("ideal_text_length")
            # ユーザーの確認.
            user_data = db.session.query(User).filter_by(id=user_id).first()
            if not user_data:
                return {"error": f"user not found - user_id: {user_id}"}, 404
            # Novelist準備.
            logger.info("starting novelist setup")
            novelist = Novelist()
            novelist.set_first_params(text_length, novel_other_settings)
            novelist.prepare_novel()
            logger.info("finished novelist setup")
            # Validate genre code.
            genre_code = novelist.other_settings.get("genre")
            if genre_code:
                genre_exists = db.session.query(db.exists().where(Genre.code == genre_code)).scalar()
                if not genre_exists:
                    return {"error": f"Invalid genre code: {genre_code}"}, 400
            # Novelのデータベース登録.
            novel_data = Novel(
                style=novelist.other_settings.get("style"),
                genre_code=novelist.other_settings.get("genre"),
                text_length=text_length,
                title=novelist.other_novel_data.get("title", "untitled"),
                overall_plot=novelist.plot,
                short_summary=novelist.other_novel_data.get("summary", ""),
                user_id=user_data.id,
                status=NovelStatus.GENERATING,
                true_text_length=0,
            )
            db.session.add(novel_data)
            db.session.commit()
            logger.info("new novel was registered to db")
            # 章のデータベースを作成する.
            for i in range(novelist.chapter_count):
                chapter = Chapter(
                    chapter_number=i + 1,
                    content="NO CONTENT",
                    novel_id=novel_data.id,
                    status=NovelStatus.PENDING,
                    plot=novelist.chapter_plots[i].get("plot"),
                )
                db.session.add(chapter)
            db.session.commit()
            logger.info(f"{novelist.chapter_count} chapters was registered to db")
            # 1章の生成開始をデータベースに記録.
            first_chapter = db.session.query(Chapter).filter_by(novel_id=novel_data.id, chapter_number=1).first()
            first_chapter.status = NovelStatus.GENERATING
            db.session.commit()
            # 1章生成.
            logger.info("start to generate chapter")
            chapter = novelist.write_next_chapter()
            logger.info("finished generating chapter")
            # データベース記録.
            first_chapter.content = chapter
            first_chapter.status = NovelStatus.COMPLETED
            db.session.commit()
            trd = threading.Thread(target=novelist_bg_task_runner, args=(novelist, novel_data.id))
            trd.daemon = False
            trd.start()

            return {
                "novel_id": str(novel_data.id),
                "title": novel_data.title,
                "total_chapter_number": novelist.chapter_count,
                "first_chapter_text": chapter,
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/<string:novel_id>/text")
class NovelText(Resource):
    @api.doc("get_text", params={"novel_id": "小説のID"})
    @api.expect(novels_text_parser)
    @api.marshal_with(novel_text_model)
    def get(self, novel_id):
        """小説idから作成済みのチャプター本文を結合して返す

        Args:
            novel_id (string): 小説id
            X-User-ID (string): user id

        Returns:
            dict: {
                text(string):結合されたテキスト,
                last_chapter(int):結合された最後のチャプター番号,
                has_all_chapters(boolean):生成予定のチャプターがすべて結合され、全文が返ったか
                }
        """
        novel = db.session.get(Novel, novel_id)
        user_id = request.headers.get("X-User-ID")
        # 認証情報なしエラー.
        if not user_id:
            api.abort(401, "Authorization header 'X-User-ID' is required")
        # 小説なしエラー.
        if not novel:
            api.abort(404, f"Novel not found - id:{novel_id}")
        # ユーザーの権限なしエラー.
        if novel.user_id != user_id:
            api.abort(403, "You do not have permission to access this novel")
        chapters = db.session.query(Chapter).filter_by(novel_id=novel_id).order_by(Chapter.chapter_number).all()
        text = ""
        count = 0
        for i in range(len(chapters)):
            chapter = chapters[i]
            if chapter.status != NovelStatus.COMPLETED:
                break
            text += chapter.content + "\n"
            count += 1
        return {
            "text": text,
            "last_chapter": count,
            "total_chapter_number": len(chapters),
            "has_all_chapters": count == len(chapters),
        }
