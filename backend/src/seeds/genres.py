"""ジャンル初期化シード挿入モジュール

固定ジャンル(英語スラッグ + 日本語表示名)を初回起動時に不足分のみ挿入します。
"""

from typing import Dict, List

from flask import Flask

from src.database import db
from src.models import Genre

# 固定ジャンル一覧: code = 内部スラッグ, genre = 日本語表示名
GENRES: List[Dict[str, str]] = [
    {"code": "sf", "genre": "SF"},
    {"code": "fantasy", "genre": "ファンタジー"},
    {"code": "mystery", "genre": "ミステリー"},
    {"code": "horror", "genre": "ホラー"},
    {"code": "romance", "genre": "恋愛"},
    {"code": "history", "genre": "歴史"},
    {"code": "light_novel", "genre": "ライトノベル"},
    {"code": "youth", "genre": "青春"},
]


def seed_genres(app: Flask) -> None:
    """未登録の固定ジャンルを参照テーブルへ挿入する。

    Args:
        app (Flask): Flask アプリケーションインスタンス (アプリコンテキスト取得用)
    """
    with app.app_context():
        # 既存ジャンルコード集合を取得
        existing_codes = {g.code for g in db.session.query(Genre.code).all()}
        created = 0  # 今回追加した件数
        for g in GENRES:
            if g["code"] not in existing_codes:
                db.session.add(Genre(code=g["code"], genre=g["genre"]))
                created += 1
        if created:
            db.session.commit()
