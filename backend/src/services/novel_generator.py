import os
import json
from google import generativeai as genai

# 小説生成系を担当するクラス.
# ai側でのエラーを処理しないので注意.
class NovelGenerator:
    def __init__(self):
        self.model = None
        self.is_generating = False

    def setup_ai(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model_version = os.getenv("GEMINI_MODEL", "2.0-flash")
        if model_version not in ["2.0-flash", "2.5-flash"]:
            raise ValueError(f"Invalid GEMINI_MODEL: {model_version}. Must be '2.0-flash' or '2.5-flash'.")
        self.model = genai.GenerativeModel(f"gemini-{model_version}")

    # プロット生成.
    def generate_plot(self, genre, text_length):
        return self.model.generate_content(
            f"{genre}の小説のプロットを具体的に作成してください。小説は{text_length}文字程度になります。",
            request_options={"timeout": 600},
        ).text

    # 小説の初期データを生成して返す jsonテキストを返す努力をする.
    def generate_init(self, text_length, chapter_count, other):
        ret_text = self.model.generate_content(
            f"""下記の内容の小説を作成するのに、設定やプロット、登場人物等を具体的に作成してください。小説は全体で{text_length}文字程度、章は{chapter_count}です。
            {json.dumps(other)}
            出力は以下のjson形式で行ってください、その他は一切出力してはいけません。:
            {{
                "title":(novel's title),
                "summary":(summary),
                "plot":(plot),
                "characters":[
                    {{
                        "name":(name),
                        "role":(role)
                    }},
                    (generate characters you needed)
                ],
                "chapter_plots":[
                    {{
                        "plot":(plot)
                    }},
                    (generate same number of items as chapters)
                ]
            }}
            """,
            request_options={"timeout": 600},
        ).text.replace("\n", "")
        json_start = ret_text.find("{")
        ret_text = ret_text[json_start:]
        json_end = ret_text.rfind("}")
        ret_text = ret_text[: json_end + 1]
        return ret_text

    # チャプター生成.
    def generate_chapter(self, plot, style, previous_chapter=None, chapter_num=0):
        return self.model.generate_content(
            f"""{plot}の小説の第{chapter_num}章を、以下の情報を参考に生成してください。
            {f"- 文体:{style}" if isinstance(style, str) else ""}
            {f"下記は前の章です:\n{previous_chapter}" if previous_chapter else ""}
            """,
            request_options={"timeout": 600},
        ).text

    # 小説生成のジェネレーター.
    def generate_novel(self, genre, text_length, style):
        self.is_generating = True
        plot = self.generate_plot(genre, text_length)
        yield 0, plot
        total_text_len = 0
        previous_chapter = None
        count = 1
        while True:
            chapter = self.generate_chapter(
                plot=plot, style=style, previous_chapter=previous_chapter, chapter_num=count
            )
            total_text_len += len(chapter)
            previous_chapter = chapter
            yield count, chapter
            if total_text_len > text_length:
                self.is_generating = False
                return
            previous_chapter = chapter
            count += 1