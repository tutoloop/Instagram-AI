# -*- coding: utf-8 -*-
"""デザイン: karte … 診断結果票風（白い書類＋ティールの罫＋赤い判定スタンプ）。

「長文が読めない子の特徴」用に書き下ろし。中身が「当てはまる数を数える診断」なので、
モチーフも健康診断の結果票・検査シートに寄せて、内容と見た目が同じことを言う状態にした。
項目に 01〜07 の検査番号を振り、下に「所見」欄と「要改善」の判定スタンプを置いている。

既存4種との違い:
    note      … クリーム紙＋手書き（やわらかい）→ こちらは事務書類の硬さ
    makimono  … 和紙＋墨
    weekplan  … ネイビー＋蛍光イエローの計画表
    redsheet  … 白＋赤ベタのヘッダー＋緑マーカー → こちらは赤ベタを使わず、ティール＋細罫が主役

任意キー:
    "note" … 「所見」欄に入る一言（無ければ所見欄ごと出ない＝スタンプも消える）
"""
from .common import inline, esc

LABEL = "診断結果票風（白い書類＋ティールの細罫＋所見欄＋赤い判定スタンプ。検査シートの硬さ）"

CSS = """
  :root{ --teal:#0d8577; --teal-d:#0a5f55; --ink:#19222c; --sub:#6d7783;
         --line:#dde4e8; --red:#d5342b; --amber:#ffd84a; --paper:#fdfdfb; }
  *{ box-sizing:border-box; margin:0; padding:0; }
  html,body{ background:#e9edf0; }
  #stage{ width:960px; padding:48px 44px; display:flex; justify-content:center;
    background:linear-gradient(160deg,#f3f6f8,#d6dee4); }

  .paper{ width:830px; background:var(--paper); color:var(--ink);
    font-family:'Noto Sans CJK JP', sans-serif;
    border:3px solid var(--ink); border-radius:6px; overflow:hidden;
    box-shadow:0 18px 40px rgba(20,30,40,.3); }

  /* ---- 書類ヘッダ（検査票の上端）---- */
  .docbar{ display:flex; justify-content:space-between; align-items:baseline;
    padding:15px 26px 13px; border-bottom:2px solid var(--ink);
    font-size:24px; letter-spacing:2px; color:var(--sub); }
  .docbar b{ color:var(--teal-d); }

  /* ---- 見出し ---- */
  .head{ padding:28px 30px 26px; text-align:center; border-bottom:2px solid var(--line); }
  .eyebrow{ font-size:27px; font-weight:700; color:var(--teal-d); letter-spacing:1px; }
  /* 13文字の長い大題なので、はみ出す前提の74pxではなく最初から詰めた寸法にしている */
  .title{ font-family:'Dela',sans-serif; font-size:57px; line-height:1.12;
    white-space:nowrap; margin:14px 0 4px; }
  /* 下線だと大題から離れて棒が浮くので、字にかかる蛍光マーカーにしている */
  .title .em{ color:var(--teal);
    background:linear-gradient(transparent 74%, var(--amber) 74%, var(--amber) 94%, transparent 94%); }
  .hook{ display:inline-block; margin-top:16px; padding:9px 28px; border-radius:999px;
    background:var(--ink); color:#fff; font-size:32px; font-weight:700; }
  .hook .em{ color:var(--amber); }

  /* ---- 検査項目 ---- */
  .list{ padding:12px 28px 4px; }
  .row{ display:flex; align-items:center; gap:20px; padding:19px 2px;
    border-bottom:1px solid var(--line); }
  .row:last-child{ border-bottom:none; }
  .no{ flex:0 0 56px; height:56px; border-radius:8px; background:var(--teal); color:#fff;
    font-family:'Dela',sans-serif; font-size:26px;
    display:flex; align-items:center; justify-content:center; }
  .txt{ flex:1; font-size:40px; font-weight:700; line-height:1.15; }
  .txt .em{ color:var(--red); }
  .txt .kw{ color:var(--teal-d); }
  .txt u{ text-decoration:none; background:linear-gradient(transparent 60%, var(--amber) 60%); }

  /* ---- 所見欄＋判定スタンプ ---- */
  .memoRow{ display:flex; align-items:stretch; gap:18px; margin:20px 28px 26px; }
  .memo{ position:relative; flex:1; border:2px solid var(--ink); border-radius:8px;
    padding:24px 22px 20px; background:#fff;
    font-size:31px; font-weight:700; line-height:1.4; }
  .memo::before{ content:'所見'; position:absolute; top:-15px; left:18px;
    background:var(--paper); padding:0 12px;
    font-size:23px; letter-spacing:3px; color:var(--teal-d); }
  .memo u{ text-decoration:none; color:var(--red); border-bottom:4px solid var(--red); }
  .stamp{ flex:0 0 146px; align-self:center; height:146px; border:6px double var(--red);
    border-radius:50%; color:var(--red); font-family:'Dela',sans-serif; font-size:36px;
    display:flex; align-items:center; justify-content:center;
    transform:rotate(-11deg); opacity:.88; }

  /* ---- CTA ---- */
  .cta{ background:var(--teal); color:#fff; padding:20px 28px 24px;
    display:flex; align-items:center; justify-content:center; gap:18px; }
  .ctaText{ font-size:35px; font-weight:700; }
  .ctaText .em{ color:var(--amber); }
  .follow{ font-family:'Dela',sans-serif; font-size:46px; color:var(--teal-d); background:#fff;
    padding:5px 24px 7px; border-radius:999px; }
"""


def build_body(c: dict) -> str:
    rows = "\n      ".join(
        f'<div class="row"><div class="no">{i:02d}</div>'
        f'<div class="txt">{inline(it)}</div></div>'
        for i, it in enumerate(c["items"], 1)
    )
    memo = ""
    if c.get("note"):
        memo = (f'<div class="memoRow"><div class="memo">{inline(c["note"])}</div>'
                f'<div class="stamp">要改善</div></div>')
    return f"""  <div class="paper">
    <div class="docbar"><span><b>ENGLISH</b> / 長文読解</span><span>診断結果</span></div>
    <div class="head">
      <div class="eyebrow">{esc(c["eyebrow"])}</div>
      <div class="title">{inline(c["title"])}</div>
      <div class="hook">{inline(c["hook"])}</div>
    </div>
    <div class="list">
      {rows}
    </div>
    {memo}
    <div class="cta">
      <div class="ctaText">{inline(c["cta_line"])}</div>
      <span class="follow">{esc(c["cta_follow"])}</span>
    </div>
  </div>"""
