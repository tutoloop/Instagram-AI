# -*- coding: utf-8 -*-
"""デザイン: plain … 白い角丸カード＋極太ゴシック（旧パターン1のCanvaテンプレの再現）。

白背景に黒文字で「タイトル→箇条書き→CTA」だけを積む、いちばん飾らない見た目。
このパターンの主役はデザインではなく情報量なので、装飾は最小限に留める。

任意キー: なし（common の JSON スキーマ通り）
"""
from .common import inline, esc, circled

LABEL = "白い角丸カード＋極太ゴシック（無地・パターン1の定番。飾りなし）"

CSS = """
  *{ box-sizing:border-box; margin:0; padding:0; }
  html,body{ background:#111; }
  #stage{ width:1040px; padding:70px 60px; display:flex; justify-content:center;
          background:linear-gradient(160deg,#3a3a3a,#111); }

  .paper{ width:900px; background:#fff; border-radius:56px; padding:88px 72px 96px;
    color:#181818; font-family:'Noto Sans CJK JP', sans-serif;
    box-shadow:0 24px 60px rgba(0,0,0,.5); }

  .title{ font-weight:900; font-size:66px; line-height:1.38; text-align:center;
    letter-spacing:.5px; margin-bottom:76px; }
  .title .em{ color:#e0362a; }
  .title .kw{ color:#1a5fd0; }

  .items{ list-style:none; }
  .item{ display:flex; align-items:flex-start; gap:20px; font-size:42px; font-weight:700;
    line-height:1.5; margin-bottom:34px; }
  .item:last-child{ margin-bottom:0; }
  .item .no{ flex:0 0 auto; color:#e0362a; }
  .item .em{ color:#e0362a; }
  .item .kw{ color:#1a5fd0; }
  .item u{ text-decoration:none; background:linear-gradient(transparent 62%, #ffe14d 62%); }

  .cta{ margin-top:78px; text-align:center; font-size:44px; font-weight:900; line-height:1.4; }
  .cta .em{ color:#e0362a; }
"""


def build_body(c: dict) -> str:
    items = "\n      ".join(
        f'<li class="item"><span class="no">{circled(i)}</span><span>{inline(it)}</span></li>'
        for i, it in enumerate(c["items"])
    )
    return f"""  <div class="paper">
    <div class="title">{inline(c["title"])}</div>
    <ul class="items">
      {items}
    </ul>
    <div class="cta">{inline(c["cta_line"])}</div>
  </div>"""
