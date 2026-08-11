# -*- coding: utf-8 -*-
"""デザインの置き場。

ノート画像生成（パターン3）と違い、こちらは「投稿ごとに毎回作り直す」対象ではない。
パターン1は元々1つのCanvaテンプレの使い回しだったので、ここでも**基本は plain 1本**で運用する
（→ ../CLAUDE.md）。それでも複数デザインを置けるようにしてあるのは、飽きが来たときや
ジャンル違いのアカウントに流用するときに増やせるようにするため。

ファイルを置けば自動で認識される（登録作業は不要）。各デザインは以下を持つこと:
    LABEL       … 一行の説明
    CSS         … そのデザインのCSS（文字列）
    build_body  … 中身dict → #stage の中に入るHTML を返す関数
"""
import importlib
import pkgutil

_HIDDEN = {"common"}


def available() -> list:
    """designs/ にある使用可能なデザイン名の一覧。"""
    return sorted(m.name for m in pkgutil.iter_modules(__path__)
                  if not m.name.startswith("_") and m.name not in _HIDDEN)


def load(name: str):
    """名前でデザインモジュールを読み込む。"""
    if name not in available():
        raise SystemExit(
            f"デザイン '{name}' が designs/ にありません。\n"
            f"  使えるデザイン: {', '.join(available())}\n"
            f"  新しく作る場合は designs/{name}.py を追加してください（LABEL / CSS / build_body）。")
    return importlib.import_module(f".{name}", __package__)
