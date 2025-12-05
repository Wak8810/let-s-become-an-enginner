import logging

from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource

from src.database import init_db
from src.genres import api as genres_api
from src.genres import genres_module
from src.moods import api as moods_api
from src.moods import moods_module
from src.novels import api as novels_api
from src.novels import novels_module
from src.seeds.genres import seed_genres
from src.seeds.moods import seed_moods
from src.tests import api as test_api
from src.tests import test_module
from src.users import api as user_api
from src.users import users_module

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = Flask(__name__)

# データベースの初期化
init_db(app)
seed_genres(app)
seed_moods(app)


# flask-restxの設定
api = Api(app, version="1.0", title="ReadFit API", description="時間ぴったり読書アプリAPI")

# /tests以下のエンドポイントを登録
app.register_blueprint(test_module)
api.add_namespace(test_api, path="/tests")

# /genres以下の登録
app.register_blueprint(genres_module)
api.add_namespace(genres_api, path="/genres")

# /moods以下の登録
app.register_blueprint(moods_module)
api.add_namespace(moods_api, path="/moods")

# /novels以下の登録.
app.register_blueprint(novels_module)
api.add_namespace(novels_api, path="/novels")

# /users以下.
app.register_blueprint(users_module)
api.add_namespace(user_api, path="/users")

# CORSの設定
CORS(app)

CORS(
    app,
    origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


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
