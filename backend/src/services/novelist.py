import json
from pathlib import Path

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
        """plotと章の数を準備"""
        self.chapter_count = self.calc_chapter_count(self.target_text_length)
        raw = self.generator.generate_init(self.target_text_length, self.chapter_count, self.other_settings)
        self.init_data = raw
        self.log(["generated initial data :\n", raw, "\n"])
        generated = json.loads(raw)
        self.plot = generated.get("plot", "")
        self.chapter_plots = generated.get("chapter_plots", [])
        self.other_novel_data = {k: v for k, v in generated.items() if k not in ["plot", "chapter_plots"]}

        # チャプター数とプロット数の不整合チェック
        if len(self.chapter_plots) != self.chapter_count:
            raise ValueError(
                f"チャプター数とプロット数の不整合: 作成予定の章の数 {self.chapter_count}に対して、AIが生成した章の数 {len(self.chapter_plots)}"
            )

    def write_next_chapter(self):
        """チャプターを一つ生成

        Returns:
            string: chapter content
        """
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

    def chapter_generator(self):
        while self.next_chapter_num != self.chapter_count + 1:
            yield self.write_next_chapter()

    def is_completed(self):
        return self.next_chapter_num == self.chapter_count + 1
