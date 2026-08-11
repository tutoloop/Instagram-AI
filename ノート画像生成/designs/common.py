# -*- coding: utf-8 -*-
"""全デザイン共通のパーツ。

- インライン装飾記法の変換（[[ ]] {{ }} __ __）
- ローカルフォントの @font-face
- 手書きノート用のキャラSVG

装飾記法は「意味」だけを表すクラスに変換し、実際の色は各デザインのCSSが決める:
    [[ここ]] → <span class="em">   強調1（ノート=赤 / 黒板=黄チョーク / 雑誌=赤 …）
    {{ここ}} → <span class="kw">   強調2（補足キーワード。ノート=青 …）
    __ここ__ → <u>                 アンダーライン
    改行(\\n) → <br>               意味の切れ目で手で折る（→ BASE_CSS のコメント）
"""
import re
import html
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"

# 紙・板などの「本体」に付けるクラス名。render.js がこれを探して背景透過PNGを切り出すので、
# どのデザインでもカード本体には必ず .paper を付けること。
CARD_CLASS = "paper"

# ---- 全デザイン共通の下地CSS（generate_note.py が design.CSS より前に差し込む＝上書き可）----
#
# 日本語の行分割。ブラウザ既定の line-break:auto は「自分だけじ／ゃなく、」のように
# 小書き文字（ゃゅょっ）や長音符が行頭に来るのを許してしまう（2026-07-30、指定校の
# 注意書きで発生）。strict にするとこれらの行頭が禁止され、自動折り返しでも崩れにくい。
#
# ただしこれは**保険**。長い文は中身JSON側で改行（\n）を入れ、意味の切れ目（句点・読点・
# 文節の頭）で自分で折るのが基本。自動折り返しに任せた文は、幅の揺らぎ（±5.5%）で
# 折り位置が変わるので、投稿ごとに読みやすさがブレる。
BASE_CSS = """
  * { line-break: strict; word-break: normal; }"""


def esc(text) -> str:
    return html.escape(str(text), quote=False)


def inline(text) -> str:
    """装飾記法を span/u に変換。< > & は先にエスケープ（記法は [ ] { } _ のみ使用）。

    JSONの改行（\\n）は <br> になる。**2行以上になる長い文は必ずここで手で折る**
    （→ BASE_CSS のコメント）。自動折り返しは折り位置が幅の揺らぎで動くため、
    意味の切れ目で折れているとは限らない。
    """
    s = esc(text)
    s = re.sub(r"\[\[(.+?)\]\]", r'<span class="em">\1</span>', s)
    s = re.sub(r"\{\{(.+?)\}\}", r'<span class="kw">\1</span>', s)
    s = re.sub(r"__(.+?)__", r"<u>\1</u>", s)
    return s.replace("\n", "<br>")


def font_face() -> str:
    """fonts/ の手書き系フォントを全デザインで使えるように登録する。

    ゴシック体は環境の Noto Sans CJK JP をfamily名で直接参照する（fonts/ には無い）。
    """
    def u(name):
        return (FONT_DIR / name).as_uri()
    return f"""
  @font-face{{ font-family:'Yusei';     src:url('{u("YuseiMagic-Regular.ttf")}'); }}
  @font-face{{ font-family:'Kurenaido'; src:url('{u("ZenKurenaido-Regular.ttf")}'); }}
  @font-face{{ font-family:'Yomogi';    src:url('{u("Yomogi-Regular.ttf")}'); }}
  @font-face{{ font-family:'Dela';      src:url('{u("DelaGothicOne-Regular.ttf")}'); }}
  @font-face{{ font-family:'Reggae';    src:url('{u("ReggaeOne-Regular.ttf")}'); }}"""


# ---- 手書きノート用のキャラ（差し替え前提の簡易SVG。いらすとや化するならここを <img> に）----
DOODLE_SVG = """<svg class="doodle" viewBox="0 0 100 100">
        <circle cx="50" cy="52" r="34" fill="#fff" stroke="#2c2b29" stroke-width="4"/>
        <path d="M20 40 Q28 20 44 30" fill="none" stroke="#2c2b29" stroke-width="4"/>
        <path d="M80 40 Q72 20 56 30" fill="none" stroke="#2c2b29" stroke-width="4"/>
        <circle cx="40" cy="50" r="8" fill="#2c2b29"/><circle cx="62" cy="50" r="8" fill="#2c2b29"/>
        <circle cx="43" cy="48" r="2.5" fill="#fff"/><circle cx="65" cy="48" r="2.5" fill="#fff"/>
        <path d="M40 70 Q50 60 60 70" fill="none" stroke="#e0362a" stroke-width="4"/>
        <path d="M46 72 q4 10 8 0" fill="#e0362a"/>
      </svg>"""

NINJA_SVG = """<svg class="ninja" viewBox="0 0 100 100">
        <circle cx="50" cy="55" r="30" fill="#3a3a3a"/>
        <rect x="18" y="46" width="64" height="16" fill="#e7e2d2"/>
        <circle cx="40" cy="54" r="5" fill="#2c2b29"/><circle cx="60" cy="54" r="5" fill="#2c2b29"/>
        <circle cx="50" cy="20" r="16" fill="#e0362a"/>
        <text x="50" y="26" font-family="Yusei" font-size="15" fill="#fff" text-anchor="middle">合格</text>
      </svg>"""

CHECKBOX_SVG = ('<svg class="box" viewBox="0 0 40 40">'
                '<path d="M4 5 L36 3 L37 36 L3 37 Z" fill="none" stroke="#2c2b29" stroke-width="3"/></svg>')

CLOUD_SVG = ('<svg viewBox="0 0 560 150" preserveAspectRatio="none"><path d="M40 90 Q10 90 18 62 Q0 40 30 34 '
             'Q34 8 74 20 Q100 -2 140 16 Q200 -6 250 16 Q320 -8 380 16 Q450 -4 500 22 Q548 20 540 56 '
             'Q566 78 536 100 Q548 132 500 128 Q460 150 400 132 Q330 150 260 132 Q180 152 110 132 '
             'Q60 144 40 118 Q18 116 40 90 Z" fill="#fff" stroke="#2c2b29" stroke-width="3"/></svg>')

DIAG_SVG = ('<svg viewBox="0 0 720 80" preserveAspectRatio="none">'
            '<rect x="4" y="4" width="712" height="72" rx="36" fill="#fff7cf" stroke="#2c2b29" stroke-width="3"/></svg>')
