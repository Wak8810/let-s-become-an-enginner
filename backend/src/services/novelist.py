import json
from pathlib import Path
from typing import Optional

from src.services.novel_generator import NovelGenerator


class Novelist:
    """NovelGeneratorを使いやすくするためのラッパ"""

    def __init__(self):
        # generator
        self.generator = NovelGenerator()
        self.generator.setup_ai()
        # plot
        self.plot = ""
        self.chapter_plots = []
        self.init_data = ""
        # chapter
        self.previous_chapter_content = ""
        self.next_chapter_num = 1
        self.chapter_count = 0
        # text length
        self.total_text_length = 0
        self.target_text_length = 0
        # other その他はディクショナリ.
        self.other_settings = {}
        self.other_novel_data = {}

    # debug
    def log(self, log):
        """logの記録 - debug

        Args:
            log (str or list(str)): log
        """
        # ログディレクトリとファイルを安全に解決
        log_dir = Path(__file__).resolve().parent.parent / "logs"
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        log_file = log_dir / "novelist.log"
        try:
            with log_file.open("a", encoding="utf-8") as f:
                if isinstance(log, str):
                    f.write(log)
                else:
                    for text in log:
                        f.write(text)
        except Exception:
            pass

    def calc_chapter_count(self, text_length):
        # 4000未満->1 , 4000以上->textLen/2000
        return 1 if text_length < 4000 else int(text_length / 2000)

    def set_first_params(self, text_length, others={}):
        """小説生成のためのパラメータを設定する

        Args:
            text_length (int): text_length
            others (dict): other settings
        """
        self.target_text_length = text_length
        if not isinstance(others, dict):
            return
        for key, value in others.items():
            self.other_settings[key] = value

    def prepare_novel(self):
        """plotと章の数を準備

        NovelGeneratorのgenerate_init()を呼び出し、小説の基本情報を取得します。
        エラーが発生した場合は上位に伝播させます。

        Raises:
            GeminiAPIError: API呼び出しまたはJSON検証でエラーが発生した場合
            ValueError: チャプター数とプロット数に不整合がある場合
        """
        self.chapter_count = self.calc_chapter_count(self.target_text_length)

        # generate_init()はdictを返す（エラーは上位に伝播）
        generated = self.generator.generate_init(self.target_text_length, self.chapter_count, self.other_settings)

        # ログ用にJSON文字列化
        self.init_data = json.dumps(generated, ensure_ascii=False, indent=2)
        self.log(["generated initial data :\n", self.init_data, "\n"])

        self.plot = generated.get("plot", "")
        self.chapter_plots = generated.get("chapter_plots", [])
        self.other_novel_data = {k: v for k, v in generated.items() if k not in ["plot", "chapter_plots"]}

        # チャプター数とプロット数の不整合チェック
        if len(self.chapter_plots) != self.chapter_count:
            raise ValueError(
                f"チャプター数とプロット数の不整合: "
                f"作成予定の章の数 {self.chapter_count}に対して、"
                f"AIが生成した章の数 {len(self.chapter_plots)}"
            )

    def load_from_init_data(self, init_data_json: str):
        """既存のinit_dataから小説の状態を復元する

        データベースに保存されているinit_data（JSON文字列）から
        小説の基本情報を読み込み、Novelistの内部状態を復元します。
        next_chapter_numとprevious_chapter_contentは呼び出し側で設定する必要があります。

        Args:
            init_data_json: JSON文字列形式のinit_data

        Raises:
            json.JSONDecodeError: JSONのパースに失敗した場合
            KeyError: 必須キーが存在しない場合
            ValueError: チャプター数とプロット数に不整合がある場合

        Example:
            >>> novelist = Novelist()
            >>> novelist.load_from_init_data(novel_data.init_data)
            >>> novelist.next_chapter_num = 3  # 第3章から再開する場合
            >>> novelist.previous_chapter_content = chapter2_content
        """
        # JSON文字列をパース
        generated = json.loads(init_data_json)

        # 必須キーの確認
        if "plot" not in generated:
            raise KeyError("Missing required key 'plot' in init_data")
        if "chapter_plots" not in generated:
            raise KeyError("Missing required key 'chapter_plots' in init_data")

        # init_dataを保存
        self.init_data = init_data_json

        # 各フィールドを復元
        self.plot = generated.get("plot", "")
        self.chapter_plots = generated.get("chapter_plots", [])
        self.other_novel_data = {k: v for k, v in generated.items() if k not in ["plot", "chapter_plots"]}
        self.chapter_count = len(self.chapter_plots)

        # チャプター数の検証
        if self.chapter_count <= 0:
            raise ValueError(f"Invalid chapter count: {self.chapter_count}")

        self.log(["Loaded from init_data: ", f"{self.chapter_count} chapters\n"])

    def write_next_chapter(self):
        """チャプターを一つ生成

        次の章を生成し、内部状態を更新します。
        エラーが発生した場合は上位に伝播させます。

        Returns:
            str: 生成された章の内容

        Raises:
            GeminiAPIError: 章の生成でエラーが発生した場合
        """
        # 章を生成（エラーは上位に伝播）
        self.previous_chapter_content = self.generator.generate_chapter(
            self.plot,
            self.other_settings.get("style", ""),
            previous_chapter=self.previous_chapter_content if self.next_chapter_num != 1 else None,
            chapter_num=self.next_chapter_num,
        )
        self.next_chapter_num += 1
        self.total_text_length += len(self.previous_chapter_content)
        self.log(
            [
                "generated chapter - next:",
                str(self.next_chapter_num),
                ", total text: ",
                str(self.total_text_length),
                ", chapter:\n",
                self.previous_chapter_content,
                "\n",
            ]
        )
        return self.previous_chapter_content

    def retry_failed_chapter(self, chapter_number: int, previous_content: Optional[str] = None) -> str:
        """失敗した章を再生成する

        指定された章番号の章を再生成します。
        内部状態（next_chapter_num、previous_chapter_content）は変更しません。
        リトライエンドポイントから呼び出されることを想定しています。

        Args:
            chapter_number: 再生成する章の番号（1から始まる）
            previous_content: 前の章の内容（Noneの場合は自動判定）

        Returns:
            str: 生成された章の内容

        Raises:
            ValueError: 章番号が不正な場合
            GeminiAPIError: 生成に失敗した場合

        Example:
            >>> # 第3章が失敗した場合の再生成
            >>> content = novelist.retry_failed_chapter(
            ...     chapter_number=3,
            ...     previous_content=chapter2_content
            ... )
        """
        if chapter_number < 1 or chapter_number > self.chapter_count:
            raise ValueError(f"Invalid chapter number: {chapter_number}. Must be between 1 and {self.chapter_count}")

        # 前の章の内容を決定
        if previous_content is not None:
            prev = previous_content
        elif chapter_number == 1:
            prev = None
        else:
            # 前の章の内容が提供されていない場合は内部状態を使用
            prev = self.previous_chapter_content if self.next_chapter_num > chapter_number else None

        # 章を生成（エラーは上位に伝播）
        content = self.generator.generate_chapter(
            self.plot,
            self.other_settings.get("style", ""),
            previous_chapter=prev,
            chapter_num=chapter_number,
        )

        self.log([f"Retried chapter {chapter_number} - ", f"length: {len(content)}\n", content, "\n"])

        return content

    def chapter_generator(self):
        while self.next_chapter_num != self.chapter_count + 1:
            yield self.write_next_chapter()

    def is_completed(self):
        return self.next_chapter_num == self.chapter_count + 1
