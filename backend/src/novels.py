import json
import os

from dotenv import load_dotenv
from flask import Blueprint, Response, request
from flask_restx import Namespace, Resource, fields
from google import generativeai as genai

from src.database import db
from src.models import Chapter, Novel

load_dotenv()

# URI "/novels/" 以下を定義.
novels_module = Blueprint("novel_module", __name__)
api = Namespace("novels", description="役割はタスク分解ドキュメントを参照してください…")


# 小説生成系を担当するクラス.
# ai側でのエラーを処理しないので注意.
class NovelGenerater:
    def __init__(self):
        self.model = None
        self.is_generating = False
        self.novel_db = None
        self.chapter_db = None

    def setup_ai(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    # プロット生成.
    def generate_plot(self, genre, text_length):
        return self.model.generate_content(
            f"{genre}の小説のプロットを具体的に作成してください。小説は{text_length}程度になります。"
        ).text

    # チャプター生成.
    def generate_chapter(self, plot, style, previous_chapter=None, chapter_num=0):
        return self.model.generate_content(
            f"""{plot}の小説の第{chapter_num}章を、以下の情報を参考に生成してください。
            {f"- 文体:{style}" if type(style) == type("") else ""}
            {f"下記は前の章です:\n{previous_chapter}" if previous_chapter else ""}
            """
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
            if total_text_len > text_length:
                self.is_generating = False
                yield count, chapter  # ここにreturnを使ってはいけないbyAI(未検証).
                return
            else:
                yield count, chapter
            count += 1


# --- model ---
novel_start_model = api.model(
    "novelStart",
    {
        "genre": fields.String(description="novel's genre // now, only this is sent to ai -2025/11/14 3:00"),
        "textLen": fields.Integer(required=True, description="required novel's length"),
        "style": fields.String(description="novel's style"),
    },
)
novel_item_model = api.model(
    "NovelListItem",
    {
        "novel_id": fields.String(attribute="id"),
        "title": fields.String(),
        "overall_plot": fields.String(),
        "created_at": fields.DateTime(),
        "updated_at": fields.DateTime(),
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


# "/novels/" : 小説生成の開始時のエンドポイント.
@api.route("/")
class NovelStart(Resource):
    @api.doc("post_novels")
    @api.expect(novel_start_model)
    def post(self):
        """最初に送る小説の設定的なの

        Returns:

        """
        try:
            # リクエストボディの解凍.
            requested_param = request.get_json()
            genre = requested_param.get("genre")
            text_length = requested_param.get("textLen")
            style = requested_param.get("style")
            # db
            novel_data = Novel(
                style=style,
                genre=genre,
                text_length=text_length,
                title="test",  # debug
                overall_plot="",  # debug
                user_id="",  # debug
            )
            db.session.add(novel_data)
            db.session.commit()
            # ai-apiとのやり取り
            novelist = NovelGenerater()
            novelist.setup_ai()

            # NovelGeneraterのgenerate_novelメソッドの出力に以下の処理をする.
            # - DB登録
            # - レスポンスのjsonボディに変形
            def novel_generater():
                try:
                    gen = novelist.generate_novel(genre, text_length, style)
                    count, plot = next(gen)
                    novel_data.overall_plot = plot
                    db.session.commit()
                    yield json.dumps({"response_count": count, "plot": plot})
                    while novelist.is_generating:
                        count, chapter = next(gen)
                        chapter_data = Chapter(chapter_number=count, content=chapter, novel_id=novel_data.id)
                        db.session.add(chapter_data)
                        yield json.dumps({"response_count": count, "chapter": chapter})
                    db.session.commit()
                    return json.dumps({"response_count": count + 1, "fin": True})
                except Exception as e:
                    return json.dumps({"error": str(e)})

            return Response(novel_generater(), mimetype="text/plain")
        except Exception as e:
            return {"status": False, "error": str(e)}

    @api.doc("get_novels")
    def get(self):
        """novelsとchaptersのデータベースの数を返す

        Returns:
            n:count of novels
            c:count of chapters
        """
        try:
            n = 0
            c = 0
            novels = db.session.query(Novel).all()
            chapters = db.session.query(Chapter).all()
            n = len(novels)
            c = len(chapters)
            return {"n": n, "c": c}
        except Exception as e:
            return {"error": str(e), "n": n, "c": c}
