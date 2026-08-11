# -*- coding: utf-8 -*-
"""デザイン: rosen … 路線図（駅の並び）風。1本の朱赤のラインに駅ナンバリングの丸を7個通す。

英文法ネタ「英文法は[[順番が9割]]」用に書き下ろし。中身が「やる順番を外すと崩れる」
話なので、モチーフを表・リストから離して**乗り換えのできない1本の路線**にした。
番号は駅ナンバリングの丸、項目名は駅名、上の黒帯は行先表示、という見立て。

過去デザインとの描き分け:
    行を「帯」で敷くもの（weekplan / saiten / batsu / redsheet）とは構造から別で、
    左に縦のライン＋丸が通るのはこのデザインだけ。地図ものは sanmyaku があるが、
    あちらは等高線とアイボリーの地形図、こちらは白地＋1色の交通図で、
    色数（朱赤ほぼ1色）も線の性格（等高線＝曲線／路線＝直線）も重ならない。

大題を一目で読ませるための約束（2026-08-02にユーザー指摘）:
    ・グロー・多重シャドウは一切敷かない（輪郭がぼけて読めなくなる）
    ・色の切り替えは行単位。1行の途中で色を変えない（JSON側で [[ ]] を行まるごとに掛ける）
    ・大題 138px に対して項目 56px（約2.5倍）。カード内で最も強い要素にする
    ・項目を10個から7個に絞ったぶん（2026-08-02にユーザー指摘）、
      空いた縦幅はカードを縮めずに大題と項目・駅の丸の拡大に回している

載せるのは「ラベル → 大題 → 項目 → CTA」の4つだけ
（→ ノート画像生成/CLAUDE.md「★載せるのは4つだけ」）。eyebrow / hook / 一言欄は持たない。

任意キー:
    "subject"   … 上の黒帯の左（省略時「英文法」）
    "subject_r" … 上の黒帯の右（省略時「やる順番」）
"""
from .common import inline, esc

LABEL = "路線図風（白地＋朱赤の1本ライン＋駅ナンバリングの丸。順番＝駅の並び）"

CSS = """
  :root{ --ink:#14202c; --route:#d8322a; --sub:#1462b5; --paper:#f7f5ef;
         --tint:#eeeae0; --rule:#d8d2c4; }
  *{ box-sizing:border-box; margin:0; padding:0; }
  html,body{ background:#0c141d; }
  /* 紙幅の揺らぎ（+5.5% で最大992px）でも縮まないよう外枠に余裕を取る */
  #stage{ width:1150px; padding:56px 60px; display:flex; justify-content:center;
    background:
      repeating-linear-gradient(90deg, rgba(255,255,255,.03) 0 1px, transparent 1px 58px),
      repeating-linear-gradient(0deg,  rgba(255,255,255,.03) 0 1px, transparent 1px 58px),
      linear-gradient(165deg,#1b2b3c,#080d13); }

  /* 交通図の掲示板。白に近い紙＋薄い方眼（駅の路線図パネルの地） */
  .paper{ width:940px; color:var(--ink); overflow:hidden;
    font-family:'Noto Sans CJK JP', sans-serif;
    background:
      repeating-linear-gradient(90deg, rgba(20,32,44,.045) 0 1px, transparent 1px 62px),
      repeating-linear-gradient(0deg,  rgba(20,32,44,.045) 0 1px, transparent 1px 62px),
      var(--paper);
    border:4px solid var(--ink); border-radius:10px;
    box-shadow:0 22px 52px rgba(0,0,0,.5); }

  /* ---- 上の行先表示（教科ラベル）---- */
  .topbar{ display:flex; justify-content:space-between; align-items:center;
    padding:15px 30px 14px; background:var(--ink); color:#fff;
    font-size:28px; font-weight:700; letter-spacing:9px; }
  .topbar .r{ color:#f0b9b3; letter-spacing:6px; }

  /* ---- 大題 ---- */
  .head{ padding:34px 26px 30px; text-align:center;
    border-bottom:5px solid var(--ink); background:#fffdf7; }
  .title{ font-family:'Dela',sans-serif; font-size:138px; line-height:1.06;
    letter-spacing:-2px; color:var(--ink); }
  .title .em{ color:var(--route); }

  /* ---- 路線（縦の1本ライン＋駅ナンバリングの丸）----
     ラインは各駅の .rail に描いた縦棒をつなげて1本に見せる。
     始発と終着だけ丸の中心で切って、線が飛び出さないようにする。 */
  .route{ padding:30px 26px 24px; }
  .stop{ display:flex; align-items:center; gap:20px; }
  .rail{ position:relative; flex:0 0 96px; align-self:stretch;
    display:flex; align-items:center; justify-content:center; }
  .rail::before{ content:""; position:absolute; left:50%; top:0; bottom:0;
    width:18px; margin-left:-9px; background:var(--route); }
  .stop:first-child .rail::before{ top:50%; }
  .stop:last-child .rail::before{ bottom:50%; }
  .dot{ position:relative; width:88px; height:88px; border-radius:50%;
    background:#fff; border:10px solid var(--route);
    display:flex; align-items:center; justify-content:center;
    font-family:'Dela',sans-serif; font-size:40px; color:var(--ink); }

  /* ---- 駅名＝項目 ---- */
  .txt{ flex:1; font-size:56px; font-weight:700; line-height:1.18;
    padding:20px 22px; border-radius:12px; }
  .stop:nth-child(even) .txt{ background:var(--tint); }
  .txt .em{ color:var(--route); }
  .txt .kw{ color:var(--sub); }
  .txt u{ text-decoration:none;
    background:linear-gradient(transparent 62%, #ffd84d 62%); }

  /* ---- CTA ---- */
  .cta{ background:var(--route); color:#fff; padding:22px 30px 26px;
    display:flex; align-items:center; justify-content:center; gap:22px; }
  .ctaText{ font-size:42px; font-weight:700; }
  .ctaText .em{ color:#ffe14d; }
  .follow{ font-family:'Dela',sans-serif; font-size:54px; color:var(--route);
    background:#fff; padding:6px 26px 10px; border-radius:8px; }
"""


def build_body(c: dict) -> str:
    stops = "\n      ".join(
        f'<div class="stop"><div class="rail"><div class="dot">{i}</div></div>'
        f'<div class="txt">{inline(it)}</div></div>'
        for i, it in enumerate(c["items"], 1)
    )
    return f"""  <div class="paper">
    <div class="topbar"><span>{esc(c.get("subject", "英文法"))}</span>
      <span class="r">{esc(c.get("subject_r", "やる順番"))}</span></div>
    <div class="head">
      <div class="title">{inline(c["title"])}</div>
    </div>
    <div class="route">
      {stops}
    </div>
    <div class="cta">
      <div class="ctaText">{inline(c["cta_line"])}</div>
      <span class="follow">{esc(c["cta_follow"])}</span>
    </div>
  </div>"""
