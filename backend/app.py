from flask import Flask
from flask_restx import Api, Resource

from src.database import init_db
from src.novels import api as novels_api
from src.novels import novels_module
from src.tests import api as test_api
from src.tests import test_module

app = Flask(__name__)

# データベースの初期化
init_db(app)

# flask-restxの設定
api = Api(app, version="1.0", title="ReadFit API", description="時間ぴったり読書アプリAPI")

# /tests以下のエンドポイントを登録
app.register_blueprint(test_module)
api.add_namespace(test_api, path="/tests")

# /novels以下の登録.
app.register_blueprint(novels_module)
api.add_namespace(novels_api, path="/novels")


@api.route("/hello")
class hello(Resource):
    def get(self):
        """hello worldチェック

        Returns:
            string: 固定メッセージ
        """
        return "Hello World"


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
