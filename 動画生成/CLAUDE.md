# CLAUDE.md — 動画生成

背景動画をPexelsから取ってくるのと、テキストカード（パターン1・3。透過PNGならどちらでも）を背景に乗せてリールに書き出すための一式。パターン1・3共通の合成口。

| ファイル | 役割 |
|---|---|
| `pexels_queries.py.example` | APIキーと検索クエリ集の雛形。**使う前に`pexels_queries.py`にコピーし、自分のAPIキーに差し替える**（`pexels_queries.py`自体は`.gitignore`済みでリポジトリには残らない） |
| `fetch_bg_videos.py` | 背景動画を取得 → `背景動画/`に保存 |
| `make_note_video.py` | 紙（透過PNG）＋背景動画 → `../完成品/<名前>.mp4` |
| `背景動画/` | 取得した背景動画の置き場 |

## 初回セットアップ

```bash
cp pexels_queries.py.example pexels_queries.py
# pexels_queries.py を開いて PEXELS_API_KEY を自分のキーに差し替える（https://www.pexels.com/api/ で無料取得）
pip install requests imageio-ffmpeg
```

## 使い方

```bash
python3 fetch_bg_videos.py 15                       # 15本ダウンロード（全テーマからランダム、8秒以上のみ）
python3 fetch_bg_videos.py 12 --theme epic          # 「壮大な自然」テーマだけで12本
python3 fetch_bg_videos.py 12 --theme city --prefix city  # city_001.mp4 …として追加保存（既存は消えない）

python3 make_note_video.py ../ノート画像生成/output/<slug>_paper.png 背景動画/<file>.mp4 --out ../完成品/<名前>.mp4
```

## 注意点

- **取得する動画は8秒以上のもの限定**（durationでフィルタ）
- **新しく取り直すときは、実行前に`背景動画/`の既存動画を削除するか別の場所へ移動させる**（同名ファイルはスキップされ、古い動画が残る）
- **★投稿1本を作るたびに、必ずAPIでその内容に合った新しい背景動画を取得すること。`背景動画/`に既にある動画を使い回さない**。過去に取得済みの動画を安易に再利用すると、投稿ごとの新鮮さが失われる（→ ルートCLAUDE.md「量産に見せない」とも矛盾する）。`make_note_video.py`に渡す前に、必ずその回のテーマで`fetch_bg_videos.py`を実行してから選ぶ
- 取得直後の動画は**必ず中身を目視確認する**（尺・解像度が条件を満たしていても、暗いテイストは真っ黒に近いコマばかりで使えないことがある）
- Pexels APIは`video_files[].quality`にnullを返すため、解像度は`width`だけで判断すること
- クエリは英語の一般名詞だけだと国籍が混ざる。特定の国・地域のテイストが欲しいときは国名・地名を必ず入れる

## 合成の設計方針（ルートCLAUDE.mdの「動画合成はフェードのみ・尺固定」参照）

- **紙は動かさない。その場でフェードインさせるだけ**
- **尺は固定**（アカウント共通ルール。最初に決めた秒数を投稿ごとに崩さない）
- **貼り付け位置・大きさは毎回わざとバラす**（→ ルートCLAUDE.md「量産に見せない」）。紙の幅・位置・フェードのタイミング・背景の暗さ・切り出し位置を`--width` `--shift` `--sec` `--fade` `--fade-at` `--dark`で明示指定すれば固定もできる
- 乱数の種は既定で「紙の名前＋背景の名前」。同じ組み合わせなら何度作り直しても同じ仕上がりになる。振り直したいときは`--seed <文字列>`
- 明るい背景に白い紙を乗せるときは`--dark`を上げる（既定の揺らぎは暗めの背景を想定した幅）
- 背景が尺より短くても`-stream_loop -1`で繰り返して埋める

## 依存

```bash
pip install requests imageio-ffmpeg   # moviepy不要。ffmpegはimageio-ffmpegのバイナリを使用
```
