# -*- coding: utf-8 -*-
"""デザイン: kiban … プリント基板（PCB）風のTier表。

「AI時代に強い学部Tier表」用に書き下ろし。深緑のレジストにクリームの
シルク印刷、金メッキのパッドとスルーホール、という基板そのものの見た目。
Tierのランクは基板に載る IC チップ（金のピンが左右に出た黒い角チップ）、
学部はチップに貼られたクリームの部品ラベルとして並べている。
AIの話なので「機械の中身」をそのままモチーフにした。

既存デザインとの描き分け（→ CLAUDE.md「デザインは毎回作り直す」）:
    seizu   … 青焼き（濃青地＋白い方眼＋アンバー）。同じ「濃地＋細線＋暖色」だが、
              こちらは方眼を敷かず、太いトレース（配線）が曲がって走る／地は緑
    saiten  … 炭色の「発光する画面」。こちらは発光しないマットな印刷物（レジスト）
    kurai/fes … 藍地＋金／墨紫＋ネオン。こちらは深緑＋クリーム＋金という別系統
    tokushu/sanmyaku … 先行のTier表2つはどちらも明るい紙もの。こちらは暗い基板
Tier色は基板に載る部品の色（金→銅→水色のコンデンサ→鉛グレー→赤いジャンパ）。
赤橙黄緑青のゲーム的Tier色にも、sanmyaku の標高ランプにも寄せていない。

行の見せ方も先行Tier表と変える:
    tokushu  … 校名を活字のまま余白で流す（雑誌のインデックス）
    kiban    … 1学部＝1枚の部品ラベル。左に品名（枠付き）、右に説明を刷る。
               1行1項目なので、学部名と「なぜそのTierか」の一言が必ず対になる。

品名の枠だけ固定幅（240px）で、説明は残り幅に流れるだけなので、`.paper` の
幅が ±5.5% 揺らいでも壊れない（→ CLAUDE.md「量産に見せない」）。説明は
JSON側で19文字前後に収めてあり、自動折り返しに頼らない（→「2行以上は手で改行」）。

eyebrow・hook・凡例・注釈・サブタイトル・締めの一言は載せない
（→ CLAUDE.md「★載せるのは4つだけ」）。空いた縦幅は大題と学部名に回した。

任意キー（このデザインだけが読む）:
    "tiers"  … [{"rank","cap","schools":[{"n":学部名,"h":一言}]}]
    "handle" … ヘッダー右上のアカウント名
"""
from .common import inline, esc

LABEL = "プリント基板（PCB）風（深緑のレジスト＋クリームのシルク印刷＋金のパッド＋ICチップのランク）"

# 基板に載る部品の色。上位＝金メッキ、下るほど銅・水色・鉛グレー・赤いジャンパ線へ。
TIER_INK = ["#f2b93c", "#e2703a", "#42b7c4", "#8fa3ae", "#e0554e"]

CSS = """
  :root{
    --board:#0e3b32; --deep:#072721; --silk:#f1ece0;
    --gold:#f2b93c; --trace:rgba(241,236,224,.09); --sub:#46564f;
  }
  *{ margin:0; padding:0; box-sizing:border-box; }
  html,body{ background:#05100d; }

  /* 外側は作業台。基板が主役なので暗く落とす */
  #stage{ width:1100px; padding:42px 40px 46px; display:flex; justify-content:center;
    background:radial-gradient(120% 70% at 50% 0%, #1c2b26 0%, #0b1613 62%, #050b09 100%); }

  /* ---- 基板本体。レジストの深緑にトレース（配線）とスルーホールを刷る ---- */
  .paper{ position:relative; width:1000px; overflow:hidden; border-radius:14px;
    color:var(--silk); font-family:'Noto Sans CJK JP', sans-serif;
    background-color:var(--board);
    background-image:
      repeating-linear-gradient(90deg, var(--trace) 0 3px, transparent 3px 58px),
      repeating-linear-gradient(48deg, rgba(241,236,224,.055) 0 2px, transparent 2px 34px),
      radial-gradient(circle at 14px 14px, rgba(242,185,60,.16) 0 3px, transparent 3.5px);
    background-size:auto, auto, 58px 58px;
    box-shadow:0 24px 54px rgba(0,0,0,.6), inset 0 0 0 5px rgba(242,185,60,.28); }

  /* 強調（暗い地の上＝金／クリームのラベル上では使わない） */
  .em{ color:var(--gold); }
  .kw{ color:#42b7c4; }
  u{ text-decoration:none; box-shadow:inset 0 -12px 0 rgba(242,185,60,.32); }

  /* ---- ヘッダー（基板の端に刷られた品番エリア）----
     eyebrow / hook / サブタイトル / 凡例は載せない（→「★載せるのは4つだけ」）。
     空いた縦幅は大題サイズに回している。 */
  .head{ position:relative; background:var(--deep); padding:30px 36px 24px;
    border-bottom:5px solid var(--gold); }
  /* 端子（金のパッド）をヘッダー下端に並べる＝基板のエッジコネクタ */
  .head::after{ content:""; position:absolute; left:36px; right:36px; bottom:-5px; height:5px;
    background:repeating-linear-gradient(90deg, rgba(7,39,33,.85) 0 6px, transparent 6px 26px); }
  .handle{ position:absolute; top:26px; right:30px; font-size:21px; font-weight:700;
    color:var(--gold); border:2px solid rgba(242,185,60,.6); border-radius:999px; padding:4px 16px; }
  /* 大題は2行組み（中身JSONの \\n で折る）。nowrap のままなのは、文言を伸ばしたとき
     render.js が自動で縮めて右端の欠けを防いでくれるため。 */
  .title{ font-family:'Dela',sans-serif; font-size:100px; line-height:1.06;
    white-space:nowrap; letter-spacing:-3px; color:var(--silk); }

  /* ---- Tierの段 ---- */
  .rows{ padding:18px 30px 20px; }
  .tier{ display:flex; align-items:flex-start; gap:20px; padding:8px 0 10px; }
  .tier + .tier{ border-top:2px dashed rgba(241,236,224,.16); }

  /* ランク＝ICチップ。左右に金のピンが出た黒い角チップ */
  .chip{ position:relative; flex:0 0 126px; background:#12100e; border-radius:6px;
    border:2px solid rgba(241,236,224,.22); padding:12px 0 14px; text-align:center; }
  .chip::before,.chip::after{ content:""; position:absolute; top:14px; bottom:14px; width:9px;
    background:repeating-linear-gradient(180deg, var(--gold) 0 8px, transparent 8px 18px); }
  .chip::before{ left:-9px; }
  .chip::after{ right:-9px; }
  .chip .r{ font-family:'Dela',sans-serif; font-size:70px; line-height:.9; color:var(--c); }

  .body{ flex:1; min-width:0; }
  .cap{ font-size:30px; font-weight:700; color:var(--c); letter-spacing:.5px; margin:2px 0 8px; }
  .cap::before{ content:""; display:inline-block; width:14px; height:14px;
    background:var(--c); border-radius:3px; margin-right:12px; vertical-align:.05em; }

  /* 1学部＝1枚の部品ラベル（クリームのシルク面）。地と明暗を逆にして浮かせる */
  .list{ display:flex; flex-direction:column; gap:5px; }
  .it{ display:flex; align-items:stretch; background:var(--silk); border-radius:4px;
    border-left:9px solid var(--c); overflow:hidden; }
  .it b{ flex:0 0 236px; font-size:30px; font-weight:700; line-height:1.1; color:#11302a;
    letter-spacing:-1px; padding:4px 14px 5px 16px;
    border-right:2px dotted rgba(17,48,42,.3); display:flex; align-items:center; }
  .it span{ flex:1; min-width:0; font-size:23px; font-weight:500; line-height:1.25;
    color:var(--sub); padding:6px 16px 7px 15px; display:flex; align-items:center; }

  /* ---- CTA（基板の下端。ヘッダーと対の深緑帯）---- */
  .cta{ background:var(--deep); border-top:5px solid var(--gold);
    padding:22px 34px 24px; display:flex; align-items:center; justify-content:center; gap:24px; }
  .ctaText{ font-size:31px; font-weight:700; line-height:1.34; color:var(--silk); }
  .follow{ font-family:'Dela',sans-serif; font-size:45px; color:#0b2f28;
    background:var(--gold); border-radius:6px; padding:6px 24px 9px;
    transform:rotate(-1.5deg); box-shadow:5px 5px 0 rgba(241,236,224,.2); }
"""


def _items(schools) -> str:
    out = []
    for s in schools:
        note = f'<span>{inline(s["h"])}</span>' if s.get("h") else ""
        out.append(f'<div class="it"><b>{esc(s["n"])}</b>{note}</div>')
    return "".join(out)


def build_body(c: dict) -> str:
    rows = []
    for i, t in enumerate(c.get("tiers", [])):
        ink = TIER_INK[i % len(TIER_INK)]
        rows.append(
            f'<div class="tier" style="--c:{ink}">'
            f'<div class="chip"><div class="r">{esc(t["rank"])}</div></div>'
            f'<div class="body"><div class="cap">{inline(t["cap"])}</div>'
            f'<div class="list">{_items(t["schools"])}</div></div>'
            f'</div>'
        )

    handle = f'<div class="handle">{esc(c["handle"])}</div>' if c.get("handle") else ""

    return f"""  <div class="paper">
    <div class="head">
      {handle}
      <div class="title">{inline(c["title"])}</div>
    </div>
    <div class="rows">
      {"".join(rows)}
    </div>
    <div class="cta">
      <div class="ctaText">{inline(c["cta_line"])}</div>
      <span class="follow">{esc(c["cta_follow"])}</span>
    </div>
  </div>"""
