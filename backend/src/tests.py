from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields

# URIが"/tests"以下のエンドポイントを定義
test_module = Blueprint("test_module", __name__)
api = Namespace("tests", description="API接続テスト用エンドポイント群")

# /tests/<test_id> にアクセスしたときのリクエストボディ
test_id_model = api.model(
    """test用のエンドポイントのリクエストボディ
    """
    "TestId",
    {
        "id": fields.String(readonly=True, description="The content unique identifier"),
        "content": fields.String(required=True, description="The content body"),
        "created_at": fields.DateTime(readonly=True, description="The content creation timestamp"),
    },
)


# localhost:5000/tests/ エンドポイント
@api.route("/")
class Test(Resource):
    """テスト用indexクラス

    /tests/ エンドポイントへのリクエストを処理するリソースクラス。
    テスト用の基本的なメッセージを返します。
    """

    @api.doc("get_test")
    def get(self):
        """動作確認用のメッセージを取得

        Returns:
            string: 固定メッセージ
        """
        return {
            "message": "tests route works!",
        }


# localhost:5000/tests/<test_id> エンドポイント
@api.route("/<test_id>")
class TestId(Resource):
    """テスト用IDクラス

    /tests/<test_id> エンドポイントへのリクエストを処理するリソースクラス。
    URIパラメータとして渡されたtest_idを利用します。
    """

    @api.doc("get_test_id")
    def get(self, test_id):
        """指定されたtest_idに対応する情報を取得

        Args:
            test_id (str): 取得対象のtest_id

        Returns:
            dict: test_idを含むメッセージ
        """
        # URIパラメータを取得してレスポンスに含める
        return {
            "message": "tests route works!",
            "test_id": test_id,
        }

    @api.doc("post_test_id")
    @api.expect(test_id_model)
    def post(self, test_id):
        """指定されたtest_idに対応する情報を作成

        Args:
            test_id (str): 新しいtest_id

        Returns:
            dict: test_idとリクエストボディを含むメッセージ
        """
        body = request.json
        return {
            "test_id": test_id,
            "body": body,
        }
