from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields

from src.database import db
from src.models import Test

# URIが"/tests"以下のエンドポイントを定義
test_module = Blueprint("test_module", __name__)
api = Namespace("tests", description="API接続テスト用エンドポイント群")

# テスト用データ登録用リクエストボディ
test_insert_and_update_model = api.model(
    """test用データ登録用リクエストボディ
    """
    "Test",
    {
        "content": fields.String(required=True, description="The content body"),
    },
)

# テスト用データスキーマ
test_item_model = api.model(
    "TestListItem",
    {
        "test_id": fields.String(attribute="id", description="テスト用データのID"),
        "content": fields.String(description="テスト用データの内容"),
        "created_at": fields.DateTime(description="作成日時"),
        "updated_at": fields.DateTime(description="更新日時"),
    },
)


# localhost:5000/tests/ エンドポイント
@api.route("/")
class TestAccess(Resource):
    """テスト用indexクラス

    /tests/ エンドポイントへのリクエストを処理するリソースクラス。
    テスト用のデータを扱います。
    """

    @api.doc("get_test")
    @api.marshal_list_with(test_item_model)
    def get(self):
        """testsテーブルのすべての行を取得する

        Returns:
            _type_: _description_
        """
        try:
            tests = db.session.query(Test).all()
            return tests
        except Exception as e:
            return {"error": str(e)}

    @api.doc("post_test")
    @api.expect(test_insert_and_update_model)
    @api.marshal_with(test_item_model)
    def post(self):
        """testsテーブルに新しい行を登録する

        Returns:
            dict: 登録したデータの情報
        """
        try:
            data = request.json

            new_test = Test(content=data["content"])
            # データベースに追加
            db.session.add(new_test)
            db.session.commit()

            return new_test
        except Exception as e:
            return {"error": str(e)}


# localhost:5000/tests/<test_id> エンドポイント
@api.route("/<string:test_id>")
class TestId(Resource):
    """テスト用IDクラス

    /tests/<test_id> エンドポイントへのリクエストを処理するリソースクラス。
    URIパラメータとして渡されたtest_idを取得・更新します。
    """

    @api.doc("get_test_id", params={"test_id": "取得対象のtest_id"})
    @api.marshal_with(test_item_model)
    def get(self, test_id):
        """指定されたtest_idに対応する情報をデータベースから取得

        Args:
            test_id (str): 取得対象のtest_id

        Returns:
            dict: test_idを含むメッセージ
        """
        try:
            # データベースからtest_idに対応するデータを取得
            test_data = db.session.query(Test).filter_by(id=test_id).first()
            if not test_data:
                return {"error": "Test data not found"}, 404

            return test_data
        except Exception as e:
            return {"error": str(e)}

    @api.doc("put_test_id")
    @api.expect(test_insert_and_update_model)
    @api.marshal_with(test_item_model)
    def put(self, test_id):
        """指定されたtest_idに対応する情報を更新

        Args:
            test_id (str): 新しいtest_id

        Returns:
            dict: test_idとリクエストボディを含むメッセージ
        """
        body = request.json
        try:
            # データベースからtest_idに対応するデータを取得
            test_data = db.session.query(Test).filter_by(id=test_id).first()
            if not test_data:
                return {"error": "Test data not found"}, 404

            # contentを更新
            test_data.content = body["content"]
            db.session.commit()

            return test_data
        except Exception as e:
            return {"error": str(e)}

    @api.doc("delete_test_id")
    def delete(self, test_id):
        """指定されたtest_idに対応する情報を削除

        Args:
            test_id (str): 削除対象のtest_id

        Returns:
            dict: 削除結果のメッセージ
        """
        try:
            # データベースからtest_idに対応するデータを取得
            test_data = db.session.query(Test).filter_by(id=test_id).first()
            if not test_data:
                return {"error": "Test data not found"}, 404

            # データを削除
            db.session.delete(test_data)
            db.session.commit()

            return {"message": f"Test data with id {test_id} has been deleted."}
        except Exception as e:
            return {"error": str(e)}
