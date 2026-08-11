# -*- coding: utf-8 -*-
"""全デザイン共通のパーツ。

- インライン装飾記法の変換（[[ ]] {{ }} __ __）
- 丸数字（①②③…）の変換
- 下地CSS（改行ルール）

装飾記法は「意味」だけを表すクラスに変換し、実際の色は各デザインのCSSが決める:
    [[ここ]] → <span class="em">   強調1
    {{ここ}} → <span class="kw">   強調2
    __ここ__ → <u>                 アンダーライン
    改行(\\n) → <br>               意味の切れ目で手で折る（→ BASE_CSS のコメント）

ノート画像生成（パターン3）と違い、手書きフォントは使わない。**太いゴシック体一本**が
このパターンの見た目そのものなので、`fonts/` は持たず環境の Noto Sans CJK JP を使う。
"""
import re
import html

# 紙・板などの「本体」に付けるクラス名。render.js がこれを探して背景透過PNGを切り出すので、
# どのデザインでもカード本体には必ず .paper を付けること。
CARD_CLASS = "paper"

# 丸数字。項目が10個を超えたら普通の "11." にフォールバックする。
CIRCLED_NUMS = "①②③④⑤⑥⑦⑧⑨⑩"

# ---- 全デザイン共通の下地CSS（generate_text_image.py が design.CSS より前に差し込む＝上書き可）----
#
# 日本語の行分割。ブラウザ既定の line-break:auto は「自分だけじ／ゃなく、」のように
# 小書き文字（ゃゅょっ）や長音符が行頭に来るのを許してしまう。strict にするとこれらの
# 行頭が禁止され、自動折り返しでも崩れにくい。
#
# ただしこれは**保険**。長い文は中身JSON側で改行（\n）を入れ、意味の切れ目（句点・読点・
# 文節の頭）で自分で折るのが基本（→ ルート CLAUDE.md「2行以上になる文は自分で改行」）。
BASE_CSS = """
  * { line-break: strict; word-break: normal; }"""


def esc(text) -> str:
    return html.escape(str(text), quote=False)


def inline(text) -> str:
    """装飾記法を span/u に変換。< > & は先にエスケープ（記法は [ ] { } _ のみ使用）。"""
    s = esc(text)
    s = re.sub(r"\[\[(.+?)\]\]", r'<span class="em">\1</span>', s)
    s = re.sub(r"\{\{(.+?)\}\}", r'<span class="kw">\1</span>', s)
    s = re.sub(r"__(.+?)__", r"<u>\1</u>", s)
    return s.replace("\n", "<br>")


def circled(i: int) -> str:
    """0始まりindex → 丸数字。10個を超えたら "11." 形式にフォールバック。"""
    return CIRCLED_NUMS[i] if i < len(CIRCLED_NUMS) else f"{i + 1}."
