#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""透過PNG（ノート画像生成/output/*_paper.png）を背景動画に乗せてリール動画を作る。

「1枚の紙をまるごと背景の上に置く」だけなので ffmpeg 直叩きで完結する
（moviepy不要。ffmpeg は imageio-ffmpeg のバイナリを使う）。

使い方:
  python3 make_note_video.py ../ノート画像生成/output/koten_kouryaku_paper.png 背景動画/wafu_003.mp4
  python3 make_note_video.py <paper.png> <bg.mp4> --out ../完成品/古典勉強法2.mp4 --sec 8 --width 0.86

出力先は既定で ../完成品/<紙の名前>.mp4。**既にあるファイルは上書きしない**
（完成品/ にはユーザーが自分で編集した投稿が入っているため。上書きしたいときだけ --force）。
出力: 1080x1920 / 30fps / **8秒** / 音声なし（BGMを付ける回はCapCutで足す）
"""
import argparse
import random
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 30
DEFAULT_SEC = 8.0   # 尺は8秒で統一（アカウント共通ルール。2026-07-25）


def build_filter(paper_w: int, paper_h: int, sec: float, dark: float,
                 y_shift: int, x_shift: int, fade_at: float, fade_dur: float,
                 crop_fx: float, crop_fy: float) -> str:
    """背景を1080x1920でカバー→暗くする／紙は位置を動かさずフェードインだけで出す。

    紙をスライドさせたり浮き上がらせたりしない（完成品/ の投稿がすべてその場での
    フェードインのみで、動かすと別物の印象になるため。2026-07-25にユーザー指摘）。

    背景の切り出し位置（crop_fx/fy）も中央固定にしない。毎回まったく同じ構図で
    書き出さないための揺らぎ（→ jitter()）。
    """
    return (
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H}:'(in_w-out_w)*{crop_fx:.3f}':'(in_h-out_h)*{crop_fy:.3f}',"
        f"fps={FPS},trim=0:{sec},setpts=PTS-STARTPTS,"
        f"eq=brightness=-{dark:.3f}:saturation=0.92[bg];"
        f"[1:v]scale={paper_w}:{paper_h},format=rgba,"
        f"fade=in:st={fade_at:.2f}:d={fade_dur:.2f}:alpha=1[fg];"
        f"[bg][fg]overlay=(W-w)/2+{x_shift}:(H-h)/2-{y_shift}:shortest=1[v]"
    )


def jitter(seed: str, args) -> dict:
    """貼り付け位置・大きさ・尺・フェードを投稿ごとにばらつかせる。

    毎回1pxの狂いもなく同じ位置に貼ると、投稿が機械的な量産に見える
    （＝Instagram側にそう扱われうる、というユーザーの懸念。2026-07-25）。
    見た目が破綻しない範囲でだけ振る。

    種は既定で「紙の名前＋背景の名前」＝**同じ組み合わせなら何度作っても同じ結果**、
    投稿どうしでは必ず違う。振り直したいときだけ --seed を渡す。
    明示的に指定されたオプションは尊重し、揺らさない。
    """
    r = random.Random(seed)
    return {
        "width": args.width if args.width is not None else round(r.uniform(0.78, 0.88), 3),
        "shift": args.shift if args.shift is not None else r.randint(-90, 40),
        "x_shift": r.randint(-14, 14),
        # 尺だけは振らない。8秒がアカウント共通ルール（2026-07-25にユーザー指定）
        "sec": args.sec if args.sec is not None else DEFAULT_SEC,
        "dark": args.dark if args.dark is not None else round(r.uniform(0.07, 0.17), 3),
        "fade_at": args.fade_at if args.fade_at is not None else round(r.uniform(0.05, 0.30), 2),
        "fade": args.fade if args.fade is not None else round(r.uniform(0.6, 1.0), 2),
        "crop_fx": round(r.uniform(0.3, 0.7), 3),
        "crop_fy": round(r.uniform(0.3, 0.7), 3),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("paper", help="紙の透過PNG（*_paper.png）")
    p.add_argument("bg", help="背景動画（背景動画/*.mp4）")
    p.add_argument("--out", default=None, help="出力先（既定: ../完成品/<紙の名前>.mp4）")
    p.add_argument("--force", action="store_true", help="出力先に同名ファイルがあっても上書きする")
    # 以下は既定を持たせない。指定が無ければ jitter() が投稿ごとに値を決める
    p.add_argument("--sec", type=float, help="尺（秒）。既定は8.0（共通ルール。基本は変えない）")
    p.add_argument("--fade-at", type=float, help="フェード開始（秒）。既定は0.05〜0.30")
    p.add_argument("--fade", type=float, help="フェードにかける秒数。既定は0.6〜1.0")
    p.add_argument("--width", type=float, help="紙の横幅を画面幅の何割にするか。既定は0.78〜0.88")
    p.add_argument("--dark", type=float, help="背景を暗くする量。既定は0.07〜0.17")
    p.add_argument("--shift", type=int,
                   help="紙を中央より上にずらすpx（負なら下）。既定は-90〜+40")
    p.add_argument("--seed", default=None,
                   help="揺らぎの種。既定は<紙名>_<背景名>（同じ組み合わせなら毎回同じ仕上がり）")
    args = p.parse_args()

    paper, bg = Path(args.paper), Path(args.bg)
    for f in (paper, bg):
        if not f.exists():
            sys.exit(f"ファイルがありません: {f}")

    j = jitter(args.seed or f"{paper.stem}_{bg.stem}", args)

    # 紙は縦横比を保ったまま画面幅の width に合わせる。
    # ただし縦がはみ出す場合は高さ基準に切り替える（縦長すぎる紙への保険）。
    src_w, src_h = Image.open(paper).size
    paper_w = int(W * j["width"])
    paper_h = round(paper_w * src_h / src_w)
    max_h = int(H * 0.88)
    if paper_h > max_h:
        paper_h = max_h
        paper_w = round(paper_h * src_w / src_h)
    paper_w -= paper_w % 2
    paper_h -= paper_h % 2

    # 完成品/ はユーザーが自分で編集した投稿の置き場でもあるので、黙って上書きしない
    out = Path(args.out) if args.out else HERE.parent / "完成品" / f"{paper.stem.replace('_paper','')}.mp4"
    if out.exists() and not args.force:
        sys.exit(f"すでにあります: {out}\n  上書きするなら --force、別名にするなら --out <パス>")
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-stats",
        "-stream_loop", "-1", "-i", str(bg),   # 背景が尺より短くても繰り返して埋める
        "-loop", "1", "-i", str(paper),
        "-filter_complex", build_filter(paper_w, paper_h, j["sec"], j["dark"],
                                        j["shift"], j["x_shift"], j["fade_at"], j["fade"],
                                        j["crop_fx"], j["crop_fy"]),
        "-map", "[v]", "-t", str(j["sec"]), "-r", str(FPS),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
        "-y", str(out),
    ]
    print(f"紙 {src_w}x{src_h} → {paper_w}x{paper_h}（画面幅の{j['width']:.0%}） / 背景 {bg.name} / {j['sec']}秒")
    print(f"  位置: 中央から 横{j['x_shift']:+d}px 縦{-j['shift']:+d}px / "
          f"フェード {j['fade_at']}秒から{j['fade']}秒 / 背景の暗さ {j['dark']} / "
          f"背景の切り出し {j['crop_fx']:.2f},{j['crop_fy']:.2f}")
    subprocess.run(cmd, check=True)
    print(f"完成: {out}")


if __name__ == "__main__":
    main()
