from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields

from src.database import db
from src.models import Novel, User

users_module = Blueprint("users_module", __name__)
api = Namespace("users", description="ユーザー関連の処理")


# -- models --
user_registration_model = api.model(
    """ユーザーの新規登録内容
	"""
    "user_registration_data",
    {
        "user_id": fields.String(attribute="id"),
        "created_at": fields.DateTime(description="作成日時"),
        "updated_at": fields.DateTime(description="更新日時"),
    },
)
user_setting_model = api.model(
    """ユーザー情報の変更に必要なデータ
	"""
    "user_setting_data",
    {"email": fields.String(description="email"), "user_name": fields.String(description="user's name")},
)
user_item_model = api.model(
    """ユーザーのデータベース要素
	"""
    "user_item_data",
    {
        "user_id": fields.String(attribute="id"),
        "user_name": fields.String(),
        "email": fields.String(),
        "created_at": fields.DateTime(description="作成日時"),
        "updated_at": fields.DateTime(description="更新日時"),
    },
)
novel_item_model = api.model(
    """ユーザー一覧用のnovelのモデル
	"""
    "Novel",
    {
        "id": fields.String(attributes="id"),
        "title": fields.String(),
        "genre": fields.String(),
        "style": fields.String(),
        "text_length": fields.Integer(),
        "created_at": fields.Date(),
        "updated_at": fields.Date(),
    },
)


@api.route("/")
class UserList(Resource):
    @api.doc("post_users")
    @api.marshal_with(user_registration_model)
    def post(self):
        """新規にユーザIDを発行してデータベースに登録する

        Returns:
            Dict: 登録したユーザID、作成日時、更新日時
        """
        try:
            new_user = User()
            db.session.add(new_user)
            db.session.commit()
            print("new user registered")
            return new_user
        except Exception as e:
            return {"error": str(e)}

    @api.doc("get_users")
    @api.marshal_list_with(user_item_model)
    def get(self):
        """全てのユーザー情報を取得する

        Returns:
            List[Dict]: ユーザ情報（ユーザID、ユーザ名、メールアドレス、作成日時、更新日時）の配列
        """
        try:
            users = db.session.query(User).all()
            return users
        except Exception as e:
            return {"error": str(e)}


@api.route("/<string:user_id>")
class UserItem(Resource):
    @api.doc("get_user_id", params={"user_id": "取得対象のuser_id"})
    @api.marshal_with(user_item_model)
    def get(self, user_id):
        """idからユーザー情報を返す

        Args:
            user_id (String): 取得対象のユーザーのid

        Returns:
            Dict: ユーザー情報
        """
        try:
            user = User.query.get(user_id)
            return user
        except Exception as e:
            return {"error": str(e)}

    @api.doc("post_user_id", params={"user_id": "対象のuser_id"})
    @api.expect(user_setting_model)
    @api.marshal_with(user_item_model)
    def put(self, user_id):
        """ユーザ情報の更新

        Args:
            user_id (str)
        Returns:
            dict: 更新後のユーザ情報（ユーザID、ユーザ名、メールアドレス、作成日時、更新日時）
        """
        request_body = request.get_json()
        try:
            print(f"try to change user data - id: {user_id}")

            # データベースからuser_idに対応するデータを取得
            user_data = db.session.query(User).filter_by(id=user_id).first()
            if not user_data:
                print("user not found")
                return {"error": f"user not found - searched id:{user_id}"}, 404

            # リクエストボディから値を取得
            user_name = request_body.get("user_name")
            email = request_body.get("email")

            # 少なくとも一つの値が空でないかチェック
            if not user_name and not email:
                return {"error": "user_name または email の少なくとも一つは空でない値を指定してください"}, 400

            # 空でない値でデータベースを更新
            if user_name:
                user_data.user_name = user_name
            if email:
                user_data.email = email

            db.session.commit()

            return user_data
        except Exception as e:
            return {"error": str(e)}

    @api.doc("delete_user_id", params={"user_id": "対象のuser_id"})
    def delete(self, user_id):
        """ユーザー情報の削除

        Args:
            user_id (str)
        """
        try:
            print(f"try to delete user data - id: {user_id}")
            tar_user = User.query.get(user_id)
            if tar_user is None:
                print("user not found")
                return {"error": f"user not found - searched id:{user_id}"}
            db.session.delete(tar_user)
            db.session.commit()
            print(f"deleted user - id:{user_id}")
            return {"deleted": True}
        except Exception as e:
            return {"error": str(e)}


@api.route("/<string:user_id>/novels")
class UserNovelList(Resource):
    @api.doc("get_user_id/novels", params={"user_id": "対象のuser_id"})
    @api.marshal_list_with(novel_item_model)
    def get(self, user_id):
        """ユーザーidからそのユーザーのすべてのnovelを返す

        Args:
            user_id (str)

        Returns:
            List: novelのリスト
        """
        try:
            novels = Novel.query.filter_by(user_id=user_id).all()
            return novels
        except Exception as e:
            print(f"Er - UserNovelList - {str(e)}")
            return {"error": str(e)}
