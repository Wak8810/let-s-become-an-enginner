"""
データベース設定モジュール

SQLAlchemyのインスタンスと設定を管理します。
"""

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemyインスタンスの作成
db = SQLAlchemy()


def init_db(app):
    """
    データベースの初期化と設定

    Args:
        app: Flaskアプリケーションインスタンス
    """
    # SQLiteデータベースの設定
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///readfit.db"
    # track modificationsの無効化（パフォーマンス向上のため）
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # アプリケーションにデータベースを初期化
    db.init_app(app)

    # アプリケーションコンテキスト内でテーブルを作成
    with app.app_context():
        db.create_all()
