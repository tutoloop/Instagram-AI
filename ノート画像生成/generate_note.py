#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手書きノート系画像（投稿パターン3）の生成ドライバ。

使い方:
    python3 generate_note.py samples/xxx.json               # JSONの design でノートを出力
    python3 generate_note.py samples/xxx.json --design abc   # デザインだけ差し替えて試す（比較用）
    python3 generate_note.py --list                          # designs/ にあるデザイン一覧

やること:
    1. 中身JSONを読む（"design" キーで designs/<名前>.py を選ぶ。既定は "note"）
    2. デザインの CSS + build_body でHTMLを組む          ( draft/<slug>.html )
    3. node render.js を呼んでPNG化                      ( output/<slug>_preview.png / _paper.png )

**デザインは毎回新しく起こすもので、使い回すものではない**（→ CLAUDE.md「デザインは毎回作り直す」）。
このドライバと render.js、中身JSONの記法だけが共通インフラ。

インライン装飾記法（items / hook / title / cta_line で使える）:
    [[ここ]]  → 強調1（色はデザインごと。ノート=赤 / 黒板=黄チョーク …）
    {{ここ}}  → 強調2（ノート=青 …）
    __ここ__  → アンダーライン / マーカー
"""
import sys
import json
import random
import re
import subprocess
from pathlib import Path

import designs
from designs.common import font_face, BASE_CSS

HERE = Path(__file__).resolve().parent
DRAFT_DIR = HERE / "draft"
OUTPUT_DIR = HERE / "output"

DEFAULT_DESIGN = "note"


JITTER_RANGE = 0.055  # 紙の幅を ±5.5% の範囲で揺らす


def jitter_css(design, slug: str, seed: str | None) -> tuple:
    """紙の幅を投稿ごとに少しずらす上書きCSSを作る。

    毎回まったく同じ寸法・同じ位置で書き出すと、投稿が機械的な量産に見える
    （＝Instagram側にそう扱われうる、というユーザーの懸念）。幅が変わると
    行の折り返しや余白の詰まり方も変わるので、縦横比も自然に少しズレる。

    乱数の種は既定でslug（投稿ごとに固定）。**同じ投稿を撮り直しても結果は変わらず、
    投稿どうしでは必ず違う**ようにするため。振り直したいときだけ --seed を渡す。
    """
    m = re.search(r"\.paper\s*\{[^}]*?width:\s*(\d+)px", design.CSS, re.S)
    if not m:
        return "", None
    base = int(m.group(1))
    rng = random.Random(seed if seed is not None else f"paper-width:{slug}")
    width = round(base * (1 + rng.uniform(-JITTER_RANGE, JITTER_RANGE)))
    return f"\n  .paper{{ width:{width}px; }}\n", (base, width)


def build_html(content: dict, design, extra_css: str = "") -> str:
    # BASE_CSS はデザインCSSより前（＝デザイン側で上書きできる位置）に置く
    return f"""<meta charset="utf-8">
<style>{font_face()}
{BASE_CSS}
{design.CSS}{extra_css}
</style>
<div id="stage">
{design.build_body(content)}
</div>
"""


def main():
    args = [a for a in sys.argv[1:]]

    if "--list" in args:
        print("designs/ にあるデザイン:")
        for name in designs.available():
            label = getattr(designs.load(name), "LABEL", "")
            print(f"  {name:14s} {label}")
        return

    json_args = [a for a in args if not a.startswith("--")]
    if not json_args:
        raise SystemExit("中身JSONを指定してください。例: python3 generate_note.py samples/aho_benkyou.json")
    content = json.loads(Path(json_args[0]).read_text(encoding="utf-8"))

    # --design で上書きしたときは、元の出力を潰さないよう出力名に付ける（デザイン比較用）
    override = None
    if "--design" in args:
        override = args[args.index("--design") + 1]
    design_name = override or content.get("design", DEFAULT_DESIGN)
    design = designs.load(design_name)

    slug = content.get("slug", "note")
    base = f"{slug}_{design_name}" if override else slug
    preview = "--preview" in args

    # 紙の幅を投稿ごとに少しずらす（--no-jitter で無効、--seed <文字列> で振り直し）
    extra_css, jit = "", None
    if "--no-jitter" not in args:
        seed = args[args.index("--seed") + 1] if "--seed" in args else None
        extra_css, jit = jitter_css(design, slug, seed)

    DRAFT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    html_path = DRAFT_DIR / f"{base}.html"
    html_path.write_text(build_html(content, design, extra_css), encoding="utf-8")
    print(f"design: {design_name}")
    if jit:
        print(f"紙の幅: {jit[0]}px → {jit[1]}px（投稿ごとの揺らぎ。slugで固定なので撮り直しても同じ）")
    print(f"HTML  -> {html_path}")

    # PNG化（render.js が output/<base>_paper.png を出す。確認用の _preview.png は
    # --preview を付けたときだけ。output/ に2枚並ぶと見分けがつかないため）
    cmd = ["node", "render.js", str(html_path), base]
    if preview:
        cmd.append("--preview")
    subprocess.run(cmd, cwd=str(HERE), check=True)


if __name__ == "__main__":
    main()
