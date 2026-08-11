#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""テキストカード画像（投稿パターン1・新方式）の生成ドライバ。

旧パターン1（台本Excel生成→Canva Bulk Create手動配置）を置き換えるもの。
中身JSONを渡すと、白背景に極太ゴシックの「タイトル→箇条書き→CTA」カードを
HTML/CSS→PNGで直接書き出す。ノート画像生成（パターン3）と同じ仕組みの流用。

使い方:
    python3 generate_text_image.py samples/xxx.json                # JSONの design でカードを出力
    python3 generate_text_image.py samples/xxx.json --design abc    # デザインだけ差し替えて試す
    python3 generate_text_image.py samples/xxx.json --no-jitter     # 紙幅の揺らぎを止める
    python3 generate_text_image.py samples/xxx.json --seed abc      # 紙幅を振り直す
    python3 generate_text_image.py --list                           # designs/ の一覧

出力は output/<slug>_paper.png（カードだけ・背景透過）の1枚だけ。
これを 動画生成/make_note_video.py でそのまま背景動画に合成できる（紙のPNGを渡す口は共通）。

インライン装飾記法（title / items / cta_line で使える）:
    [[ここ]]  → 強調1（赤）
    {{ここ}}  → 強調2（青）
    __ここ__  → アンダーライン / マーカー
"""
import sys
import json
import random
import re
import subprocess
from pathlib import Path

import designs
from designs.common import BASE_CSS

HERE = Path(__file__).resolve().parent
DRAFT_DIR = HERE / "draft"
OUTPUT_DIR = HERE / "output"

DEFAULT_DESIGN = "plain"

JITTER_RANGE = 0.055  # カード幅を ±5.5% の範囲で揺らす（→ ルート CLAUDE.md「量産に見せない」）


def jitter_css(design, slug: str, seed: str | None) -> tuple:
    """カード幅を投稿ごとに少しずらす上書きCSSを作る。ノート画像生成と同じ考え方。

    乱数の種は既定でslug（投稿ごとに固定）。同じ投稿を撮り直しても結果は変わらず、
    投稿どうしでは必ず違う。振り直したいときだけ --seed を渡す。
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
<style>
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
        raise SystemExit("中身JSONを指定してください。例: python3 generate_text_image.py samples/example.json")
    content = json.loads(Path(json_args[0]).read_text(encoding="utf-8"))

    # --design で上書きしたときは、元の出力を潰さないよう出力名に付ける（デザイン比較用）
    override = None
    if "--design" in args:
        override = args[args.index("--design") + 1]
    design_name = override or content.get("design", DEFAULT_DESIGN)
    design = designs.load(design_name)

    slug = content.get("slug", "text")
    base = f"{slug}_{design_name}" if override else slug

    extra_css, jit = "", None
    if "--no-jitter" not in args:
        seed = args[args.index("--seed") + 1] if "--seed" in args else None
        extra_css, jit = jitter_css(design, slug, seed)

    preview = "--preview" in args

    DRAFT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    html_path = DRAFT_DIR / f"{base}.html"
    html_path.write_text(build_html(content, design, extra_css), encoding="utf-8")
    print(f"design: {design_name}")
    if jit:
        print(f"カード幅: {jit[0]}px → {jit[1]}px（投稿ごとの揺らぎ。slugで固定なので撮り直しても同じ）")
    print(f"HTML  -> {html_path}")

    cmd = ["node", "render.js", str(html_path), base]
    if preview:
        cmd.append("--preview")
    subprocess.run(cmd, cwd=str(HERE), check=True)


if __name__ == "__main__":
    main()
