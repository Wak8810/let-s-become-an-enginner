"""ムード関連エンドポイント

ムード参照テーブルの取得APIを提供します。
"""

from flask import Blueprint
from flask_restx import Namespace, Resource, fields

from src.database import db
from src.models import Mood

# URIが"/moods"以下のエンドポイントを定義
moods_module = Blueprint("moods_module", __name__)
api = Namespace("moods", description="ムード参照API")

# mu-doデータのレスポンススキーマ
mood_model = api.model(
    "Mood",
    {
        "id": fields.Integer(description="mood ID"),
        "code": fields.String(description="ムード内部コード (例: dark, none)"),
        "mood": fields.String(description="ムード表示名 (日本語)"),
    },
)


@api.route("/")
class MoodList(Resource):
    """ムード一覧取得エンドポイント"""

    @api.doc("get_moods")
    @api.marshal_list_with(mood_model)
    def get(self):
        """登録されているすべてのムードを取得する

        Returns:
            list[dict]: ムード一覧 (id, code, mood)
        """
        try:
            moods = db.session.query(Mood).all()
            return moods
        except Exception as e:
            api.abort(500, f"ムード取得に失敗しました: {str(e)}")
