"""
データベースモデル定義

各テーブルのSQLAlchemyモデルを定義します。
"""

from datetime import datetime
from uuid import uuid4

from src.database import db


class User(db.Model):
    """
    ユーザーテーブル

    アプリケーションのユーザー情報を管理します。
    """

    __tablename__ = "users"

    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid4().hex)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # リレーション: ユーザーは複数の小説を持つ
    novels = db.relationship("Novel", backref="author", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class Novel(db.Model):
    """
    小説テーブル

    生成された小説の情報を管理します。
    """

    __tablename__ = "novels"

    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid4().hex)
    title = db.Column(db.String(200), nullable=False)  # AIが生成した小説のタイトル
    overall_plot = db.Column(db.Text, nullable=False)  # AIが生成した小説の全体プロット
    # status = db.Column(db.String(20), default="PENDING")  # PENDING, GENERATING, COMPLETED
    genre = db.Column(db.String(50), nullable=True)
    style = db.Column(db.String(50), nullable=True)
    text_length = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.String(32), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # リレーション: 小説は複数のチャプターを持つ
    chapters = db.relationship("Chapter", backref="novel", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Novel {self.title}>"


class Chapter(db.Model):
    """
    チャプターテーブル

    小説の各チャプター（章）の情報を管理します。
    """

    __tablename__ = "chapters"

    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid4().hex)
    chapter_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    novel_id = db.Column(db.String(32), db.ForeignKey("novels.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Chapter {self.chapter_number} of Novel {self.novel_id}>"
