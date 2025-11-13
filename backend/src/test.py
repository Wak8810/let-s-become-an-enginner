from flask import Blueprint

# URIが"/test"以下のエンドポイントを定義
test_bp = Blueprint("tests", __name__, url_prefix="/test")


# localhost:5000/test/ にアクセスしたときの挙動
@test_bp.route("/")
def test():
    return "test route works!"


# localhost:5000/test/<message> にアクセスしたときの挙動
@test_bp.route("/<message>")
def test_message(message):
    # URIパラメータを取得してレスポンスに含める
    return f"test route works! message: {message}"
