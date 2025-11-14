import os

from dotenv import load_dotenv
from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from google import generativeai as genai

load_dotenv()

# URI "/novels/" 以下を定義.
novels_module = Blueprint("novel_module", __name__)
api = Namespace("novels", description="役割はタスク分解ドキュメントを参照してください…")

# --- /novels/ ---
novel_start_model = api.model(
    "novelStart",
    {
        "genre": fields.String(description="novel's genre // now, only this is sent to ai -2025/11/14 3:00"),
        "textLen": fields.Integer(required=True, description="required novel's length"),
        "style": fields.String(description="novel's style"),
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
            point = 0
            requested_param = request.get_json()
            genre = requested_param.get("genre")
            text_length = requested_param.get("textLen")
            style = requested_param.get("style")
            point += 1
            # ai-apiとのやり取り
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            point += 1
            model = genai.GenerativeModel("gemini-2.0-flash")
            point += 1
            response = model.generate_content(
                f"{genre}の小説を{style}スタイルで、長さは{text_length}文字程度で出力してください。"
            )
            point += 1

            return response.text
        except Exception as e:
            return {"error": str(e), "point": point}
