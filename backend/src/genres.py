"""ジャンル関連エンドポイント

ジャンル参照テーブルの取得APIを提供します。
"""

from flask import Blueprint
from flask_restx import Namespace, Resource, fields

from src.database import db
from src.models import Genre

# URIが"/genres"以下のエンドポイントを定義
genres_module = Blueprint("genres_module", __name__)
api = Namespace("genres", description="ジャンル参照API")

# ジャンルデータのレスポンススキーマ
genre_model = api.model(
    "Genre",
    {
        "id": fields.Integer(description="ジャンルID"),
        "code": fields.String(description="ジャンル内部コード (例: scifi, fantasy)"),
        "genre": fields.String(description="ジャンル表示名 (日本語)"),
    },
)


@api.route("/")
class GenreList(Resource):
    """ジャンル一覧取得エンドポイント

    /genres/ へのリクエストを処理し、全ジャンルを返却します。
    """

    @api.doc("get_genres")
    @api.marshal_list_with(genre_model)
    def get(self):
        """登録されているすべてのジャンルを取得する

        Returns:
            list[dict]: ジャンル一覧 (id, code, genre)
        """
        try:
            genres = db.session.query(Genre).all()
            return genres
        except Exception as e:
            api.abort(500, f"ジャンル取得に失敗しました: {str(e)}")
