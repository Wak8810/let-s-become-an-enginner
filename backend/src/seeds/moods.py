"""ムード初期化シード挿入モジュール

固定ムード(英語スラッグ + 日本語表示名)を初回起動時に不足分のみ挿入します。
"""

from typing import Dict, List

from flask import Flask

from src.database import db
from src.models import Mood

# 固定ムード一覧: code = 内部スラッグ, mood = 日本語表示名
MOODS: List[Dict[str, str]] = [
    {"code": "serious", "mood": "シリアス"},
    {"code": "comedy", "mood": "コメディ"},
    {"code": "dark", "mood": "ダーク"},
    {"code": "dramatic", "mood": "ドラマチック"},
    {"code": "heartwarming", "mood": "ほのぼの"},
    {"code":"none","mood":"指定なし"}
]


def seed_moods(app: Flask) -> None:
    """未登録の固定ムードを参照テーブルへ挿入する。

    Args:
        app (Flask): Flask アプリケーションインスタンス (アプリコンテキスト取得用)
    """
    with app.app_context():
        # 既存ジャンルコード集合を取得
        existing_codes = {g.code for g in db.session.query(Mood.code).all()}
        created = 0  # 今回追加した件数
        for g in MOODS:
            if g["code"] not in existing_codes:
                db.session.add(Mood(code=g["code"], mood=g["mood"]))
                created += 1
        if created:
            db.session.commit()
