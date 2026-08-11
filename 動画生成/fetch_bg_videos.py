"""
フリー背景動画ダウンロードスクリプト
Pexels の動画検索APIから縦向きの背景動画を指定本数ダウンロードし、背景動画/ に保存する。
検索クエリとAPIキーは pexels_queries.py にまとまっている。

使い方:
  python3 fetch_bg_videos.py                              # 5本ダウンロード（全ジャンルからランダム）
  python3 fetch_bg_videos.py 15                           # 15本ダウンロード
  python3 fetch_bg_videos.py 12 --theme epic              # 「壮大な自然」のクエリだけで12本
  python3 fetch_bg_videos.py 12 --theme city --prefix city  # city_001.mp4 …として保存
"""

import os, sys, random, requests

import pexels_queries

# --theme で選べるクエリ集合（値は pexels_queries.py 側の定数名）
THEMES = {
    "all": "PEXELS_QUERIES",
    "epic": "PEXELS_QUERIES_EPIC",
    "city": "PEXELS_QUERIES_CITY",
    "wafu": "PEXELS_QUERIES_WAFU",
    # 自分のジャンル用テーマを足すときは、pexels_queries.py に
    # PEXELS_QUERIES_<名前> を定義し、ここに1行足す
}


def parse_args():
    """本数 / --theme / --prefix を取り出す。

    --prefix は保存名 `<prefix>_001.mp4` を変えるためのもの。テイスト別のセットを
    背景動画/ に共存させたいとき（既存の bg_*.mp4 を消さずに追加したいとき）に使う。
    """
    args = [a for a in sys.argv[1:]]

    def take(flag, default):
        if flag not in args:
            return default
        i = args.index(flag)
        val = args[i + 1] if i + 1 < len(args) else default
        del args[i:i + 2]
        return val

    theme = take("--theme", "all")
    prefix = take("--prefix", "bg")
    if theme not in THEMES:
        sys.exit(f"--theme は {'/'.join(THEMES)} のいずれかを指定してください（指定値: {theme}）")
    return (int(args[0]) if args else 5), theme, prefix


PEXELS_API_KEY = pexels_queries.PEXELS_API_KEY

VIDEO_DIR = "背景動画"
NUM_VIDEOS, THEME, PREFIX = parse_args()
PEXELS_QUERIES = getattr(pexels_queries, THEMES[THEME])
MIN_DURATION_SEC = 8
TARGET_WIDTH = 1080  # リール(1080x1920)の幅。これ以上の解像度のファイルを選ぶ


def pick_file(video_files):
    """リールの幅(1080px)を満たす中で一番小さいファイルを選ぶ。

    以前は quality が "hd"/"sd"/"uhd" のものだけを見ていたが、Pexels が quality に
    null を返すようになりフィルタが全滅 → APIの並び順の先頭（=最低解像度の360x640）を
    掴んでいた。quality には頼らず width だけで判断する。
    4Kを避けるのは、1080x1920に縮めるだけのために40MB超を落とす意味がないため。
    """
    files = sorted(
        (f for f in video_files if f.get("link") and f.get("width")),
        key=lambda x: x["width"],
    )
    if not files:
        return None
    for f in files:
        if f["width"] >= TARGET_WIDTH:
            return f
    return files[-1]  # 1080に届くものが無ければ一番大きいもの


def download_bg_video(query: str, save_path: str) -> bool:
    print(f"  背景動画を検索: '{query}'")
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
    except Exception as e:
        print(f"  通信エラー: {e}"); return False

    if resp.status_code == 401:
        print("  APIキーが無効です。"); return False
    if resp.status_code != 200:
        print(f"  APIエラー: {resp.status_code}"); return False

    videos = [v for v in resp.json().get("videos", []) if v.get("duration", 0) >= MIN_DURATION_SEC]
    if not videos:
        print(f"  {MIN_DURATION_SEC}秒以上の動画が見つかりませんでした"); return False

    video = random.choice(videos)
    picked = pick_file(video["video_files"])
    if picked is None:
        print("  ダウンロード可能なファイルがありませんでした"); return False

    print(f"  ダウンロード中... ({picked.get('width')}x{picked.get('height')})")
    r = requests.get(picked["link"], stream=True, timeout=60)
    with open(save_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    print(f"  保存: {save_path}")
    return True


def main():
    os.makedirs(VIDEO_DIR, exist_ok=True)
    print(f"テーマ: {THEME}（クエリ{len(PEXELS_QUERIES)}種）\n")
    if NUM_VIDEOS <= len(PEXELS_QUERIES):
        queries = random.sample(PEXELS_QUERIES, NUM_VIDEOS)
    else:  # 本数がクエリ数を超える場合は重複を許して埋める
        queries = random.choices(PEXELS_QUERIES, k=NUM_VIDEOS)

    saved = 0
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{NUM_VIDEOS}]")
        save_path = os.path.join(VIDEO_DIR, f"{PREFIX}_{i:03d}.mp4")
        if os.path.exists(save_path):
            print(f"  スキップ（既存）: {save_path}"); continue
        if download_bg_video(query, save_path):
            saved += 1
        print()

    print(f"完了！ {saved}本を '{VIDEO_DIR}/' に保存しました。")


if __name__ == "__main__":
    main()
