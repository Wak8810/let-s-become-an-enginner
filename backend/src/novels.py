import json
import os

from dotenv import load_dotenv
from flask import Blueprint, Response, request, stream_with_context
from flask_restx import Namespace, Resource, fields
from google import generativeai as genai

from src.database import db
from src.models import Chapter, Novel, User
from src.status import get_status_id

load_dotenv()

# URI "/novels/" 以下を定義.
novels_module = Blueprint("novel_module", __name__)
api = Namespace("novels", description="小説生成・管理用エンドポイント群")


# 小説生成系を担当するクラス.
# ai側でのエラーを処理しないので注意.
class NovelGenerator:
    def __init__(self):
        self.model = None
        self.is_generating = False

    def setup_ai(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model_version = os.getenv("GEMINI_MODEL", "2.0-flash")
        if model_version not in ["2.0-flash", "2.5-flash"]:
            raise ValueError(f"Invalid GEMINI_MODEL: {model_version}. Must be '2.0-flash' or '2.5-flash'.")
        self.model = genai.GenerativeModel(f"gemini-{model_version}")

    # プロット生成.
    def generate_plot(self, genre, text_length):
        return self.model.generate_content(
            f"{genre}の小説のプロットを具体的に作成してください。小説は{text_length}文字程度になります。",
            request_options={"timeout": 600},
        ).text

    # 小説の初期データを生成して返す jsonテキストを返す努力をする.
    def generate_init(self, text_length, chapter_count, other):
        ret_text = self.model.generate_content(
            f"""下記の内容の小説を作成するのに、設定やプロット、登場人物等を具体的に作成してください。小説は全体で{text_length}文字程度、章は{chapter_count}です。
            {json.dumps(other)}
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
        ).text.replace("\n", "")
        json_start = ret_text.find("{")
        ret_text = ret_text[json_start:]
        json_end = ret_text.rfind("}")
        ret_text = ret_text[: json_end + 1]
        return ret_text

    # チャプター生成.
    def generate_chapter(self, plot, style, previous_chapter=None, chapter_num=0):
        return self.model.generate_content(
            f"""{plot}の小説の第{chapter_num}章を、以下の情報を参考に生成してください。
            {f"- 文体:{style}" if isinstance(style, str) else ""}
            {f"下記は前の章です:\n{previous_chapter}" if previous_chapter else ""}
            """,
            request_options={"timeout": 600},
        ).text

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


class Novelist:
    """NovelGeneratorを使いやすくするためのラッパ"""

    def __init__(self):
        # generator
        self.generator = NovelGenerator()
        self.generator.setup_ai()
        # plot
        self.plot = ""
        self.chapter_plots = []
        self.init_data = ""
        # chapter
        self.previous_chapter_content = ""
        self.next_chapter_num = 1
        self.chapter_count = 0
        # text length
        self.total_text_length = 0
        self.target_text_length = 0
        # other その他はディクショナリ.
        self.other_settings = {}
        self.other_novel_data = {}

    def calc_chapter_count(self, text_length):
        # 4000未満->1 , 4000以上->textLen/2000
        return 1 if text_length < 4000 else int(text_length / 2000)

    def set_first_params(self, text_length, others={}):
        """小説生成のためのパラメータを設定する

        Args:
            text_length (int): text_length
            others (dict): other settings
        """
        self.target_text_length = text_length
        if not isinstance(others, dict):
            return
        for key, value in others.items():
            self.other_settings[key] = value

    def prepare_novel(self):
        """plotと章の数を準備"""
        self.chapter_count = self.calc_chapter_count(self.target_text_length)
        generated = self.generator.generate_init(self.target_text_length, self.chapter_count, self.other_settings)
        self.init_data = generated
        print(generated)
        generated = json.loads(generated)
        self.plot = generated.get("plot", "")
        self.chapter_plots = generated.get("chapter_plots", [])
        self.other_novel_data = {k: v for k, v in generated.items() if k not in ["plot", "chapter_plots"]}

    def write_next_chapter(self):
        """チャプターを一つ生成

        Returns:
            string: chapter content
        """
        self.previous_chapter_content = self.generator.generate_chapter(
            self.plot,
            self.other_settings.get("style", ""),
            previous_chapter=self.previous_chapter_content if self.next_chapter_num != 1 else None,
            chapter_num=self.next_chapter_num,
        )
        self.next_chapter_num += 1
        self.total_text_length += len(self.previous_chapter_content)
        return self.previous_chapter_content


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
        "genre": fields.String(),
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
        "novel_id": fields.String(attribute="id"),
        "title": fields.String(),
        "text": fields.String(),
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
                genre=genre,
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
    @api.marshal_with(novel_content_model)
    def get(self, novel_id):
        """指定された小説の全チャプターの内容を結合して返す

        Args:
            novel_id (str): 小説のID

        Returns:
            dict: 小説のID、タイトル、結合されたテキスト内容
        """
        novel = db.session.get(Novel, novel_id)
        if not novel:
            api.abort(404, f"Novel {novel_id} not found")

        chapters = db.session.query(Chapter).filter_by(novel_id=novel_id).order_by(Chapter.chapter_number).all()
        full_text = "\n\n".join([chapter.content for chapter in chapters])

        return {
            "id": novel.id,
            "title": novel.title,
            "text": full_text,
        }


@api.route("/init")
class NovelInit(Resource):
    @api.doc("post_init")
    @api.expect(novel_init_model)
    def post(self):
        try:
            # データ解凍.
            requested_param = request.get_json()
            user_id = requested_param.get("user_id")
            text_length = requested_param.get("novel_setting").get("ideal_text_length")
            novel_other_settings = requested_param.get("novel_setting").copy().pop("ideal_text_length")
            # ユーザーの確認.
            user_data = db.session.query(User).filter_by(id=user_id).first()
            if not user_data:
                return {"error": f"user not found - user_id: {user_id}"}, 404
            # Novelist準備.
            print("starting novelist setup")
            novelist = Novelist()
            novelist.set_first_params(text_length, novel_other_settings)
            novelist.prepare_novel()
            print("finished novelist setup")
            # Novelのデータベース登録.
            novel_data = Novel(
                style=novelist.other_settings.get("style"),
                genre=novelist.other_settings.get("genre"),  # TODO:ジャンルのデータベースとの関連付け.
                text_length=text_length,
                title=novelist.other_novel_data.get("title", "untitled"),
                overall_plot=novelist.plot,
                short_summary=novelist.other_novel_data.get("summary", ""),
                user_id=user_data.id,
                status_id=get_status_id("PENDING"),
                true_text_length=0,
            )
            db.session.add(novel_data)
            db.session.commit()
            # 章のデータベースを作成する.
            for i in range(novelist.chapter_count):
                chapter = Chapter(
                    chapter_number=i + 1,
                    content="NO CONTENT",
                    novel_id=novel_data.id,
                    status_id=get_status_id("PENDING"),
                    plot=novelist.chapter_plots[i].get("plot"),
                )
                db.session.add(chapter)
            db.session.commit()
            # とりあえず一章のみ生成して返す. -test
            first_chapter = db.session.query(Chapter).filter_by(novel_id=novel_data.id, chapter_number=1).first()
            chapter = novelist.write_next_chapter()
            first_chapter.content = chapter
            db.session.commit()

            return {
                "novel_id": str(novel_data.id),
                "title": novel_data.title,
                "total_chapter_number": novelist.chapter_count,
                "first_chapter_text": chapter,
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500
