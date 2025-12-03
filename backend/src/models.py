"""データベースモデル定義

各テーブルのSQLAlchemyモデルを定義します。
"""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from src.database import db


class NovelStatus(str, Enum):
    """小説およびチャプター生成処理の状態 Enum

    PENDING: 生成待ち
    GENERATING: 生成中
    COMPLETED: 完了
    FAILED: 失敗
    """

    PENDING = "PENDING"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class User(db.Model):
    """
    ユーザーテーブル

    アプリケーションのユーザー情報を管理します。
    """

    __tablename__ = "users"

    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid4().hex)
    user_name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # リレーション: ユーザーは複数の小説を持つ
    novels = db.relationship("Novel", backref="author", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.user_name}>"


class Novel(db.Model):
    """
    小説テーブル

    生成された小説の情報を管理します。
    """

    __tablename__ = "novels"

    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid4().hex)
    title = db.Column(db.String(200), nullable=False)  # AIが生成した小説のタイトル
    overall_plot = db.Column(db.Text, nullable=False)  # AIが生成した小説の全体プロット
    # status = db.Column(db.String(20), default="PENDING")  # PENDING, GENERATING, COMPLETED, FAILED
    # ジャンルコード
    genre_code = db.Column(db.String(32), db.ForeignKey("genres.code"), nullable=False)
    style = db.Column(db.String(50), nullable=True)
    text_length = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.String(32), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    # addition 11/22
    short_summary = db.Column(db.Text, nullable=False)
    true_text_length = db.Column(db.Integer, nullable=True)
    # ステータス (Enum)
    status = db.Column(db.Enum(NovelStatus), nullable=False, default=NovelStatus.PENDING)
    # init_data: Novelistのprepare_novel()で生成されたJSON
    init_data = db.Column(db.Text, nullable=True)

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
    # addition 11/22
    # ステータス (Enum)
    status = db.Column(db.Enum(NovelStatus), nullable=False, default=NovelStatus.PENDING)
    plot = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Chapter {self.chapter_number} of Novel {self.novel_id}>"


class Genre(db.Model):
    """ジャンルテーブル

    ジャンルの情報を管理.
    """

    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 英語スラッグ等の一意の内部コード
    code = db.Column(db.String(32), unique=True, nullable=False)
    # 表示名 (日本語ラベル)
    genre = db.Column(db.String(32), nullable=False)

    # リレーション: ジャンルは複数の小説を持つ
    novels = db.relationship("Novel", backref="genre", lazy=True)

    def __repr__(self):
        return f"<Genre id : {self.id} , genre : {self.genre}>"


class Test(db.Model):
    """
    テストテーブル

    テスト用のデータを管理します。
    """

    __tablename__ = "tests"

    # テスト項目を一意に識別するID。UUID形式の文字列。
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid4().hex)
    # テスト用データの内容。最大100文字までの文字列。
    content = db.Column(db.String(100), nullable=False)
    # レコードの作成日時。デフォルトで現在日時が設定される。
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # レコードの最終更新日時。デフォルトで現在日時が設定され、更新時に自動的に更新される。
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Test Content: {self.content}>"
