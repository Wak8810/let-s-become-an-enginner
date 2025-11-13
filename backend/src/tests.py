from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields

# URIが"/tests"以下のエンドポイントを定義
test_module = Blueprint("test_module", __name__, url_prefix="/tests")
api = Namespace("tests", description="Test operations")

# /tests/<test_id> にアクセスしたときのリクエストボディ
test_id_model = api.model(
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
    @api.doc("get_test")
    def get(self):
        return {
            "message": "tests route works!",
        }


# localhost:5000/tests/<test_id> エンドポイント
@api.route("/<test_id>")
class TestId(Resource):
    @api.doc("get_test_id")
    def get(self, test_id):
        # URIパラメータを取得してレスポンスに含める
        return {
            "message": "tests route works!",
            "test_id": test_id,
        }

    @api.doc("post_test_id")
    @api.expect(test_id_model)
    def post(self, test_id):
        body = request.json
        return {
            "test_id": test_id,
            "body": body,
        }
