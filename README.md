# Instagram AI 投稿生成エンジン

Instagramのリール投稿（リスト・ランキング・チェックリスト形式）を、Claude CodeでHTML/CSS→PNG生成し、背景動画に合成するところまで半自動化する一式です。

導入・運用の詳しい考え方は [`CLAUDE.md`](./CLAUDE.md) を参照してください。このREADMEはセットアップ手順だけを扱います。

## 導入前に用意するもの（セッション前にお願いしたいこと）

- **Claude Codeが使える状態**（Anthropicのサブスク or APIキー契約済み）
- **Node.js**（v18以上目安）
- **Python 3**
- **Pexels APIキー**（無料。 https://www.pexels.com/api/ でアカウント作成後すぐ取得できます）

上記が揃っていれば、セットアップ本番は一緒に進めます。

## セットアップ手順

```bash
# 1. リポジトリを取得
git clone https://github.com/tutoloop/Instagram-AI.git
cd Instagram-AI

# 2. Node側の依存を導入（HTML→PNGレンダリング用）
cd テキスト画像生成 && npm install && cd ..
cd ノート画像生成 && npm install && cd ..

# 3. Python側の依存を導入
pip install pillow requests imageio-ffmpeg pandas

# 4. Pexels APIキーを設定
cd 動画生成
cp pexels_queries.py.example pexels_queries.py
# pexels_queries.py を開いて PEXELS_API_KEY を自分のキーに差し替える
cd ..
```

## 動作確認（サンプルを1本生成してみる）

```bash
cd ノート画像生成
python3 generate_note.py samples/ai_gakubu_tier.json
# ノート画像生成/output/ai_gakubu_tier_paper.png ができれば成功
```

## 次にやること

Claude Codeでこのフォルダを開き、`/setup`（`setup/`の構築スキル）を実行してください。ジャンル・アカウント名を聞き取り、`CLAUDE.md`・サンプル・検索クエリを自分のアカウント用に書き換えます。

セットアップ後の運用の流れは`CLAUDE.md`の「投稿1本を作る標準フロー」を参照してください。

## ライセンス・利用範囲

このリポジトリは購入者向けに提供しているものです。自分のアカウント運用での利用は自由ですが、このリポジトリ自体（コード・ノウハウ）を第三者に再配布・転売することは禁止します。同梱フォントはOFL（`ノート画像生成/fonts/NOTICE.md`参照）。
