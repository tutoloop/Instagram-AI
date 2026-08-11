---
name: setup
description: このリポジトリを初めて使う人向けの導入セットアップ。ランタイム（Node.js/Python/Chromium）のインストールから、アカウント・ジャンルの初期設定まで対話形式で一気に進める。「セットアップして」「導入して」「/setup」で使う。非技術者が自分のPCで、Claude Codeとの対話だけで完了させる想定。
---

# 導入セットアップ

**このスキルを実行しているのはClaude Codeを使い始めたばかりの非技術者**という前提で進める。コマンドの意味を聞かれたら都度かみ砕いて説明し、失敗したらエラーメッセージをそのまま見せず「〇〇が原因っぽいので次はこうします」と要約して次の一手を示す。一度に大量のコマンドを流さず、**1ステップごとに結果を確認してから次に進む**。

Claude Code自体が使える時点でこのスキルは呼び出せている＝一番の関門は超えているので、ここから先は基本的にClaudeがコマンドを実行して進める。ユーザーに手打ちさせるのは「はい/いいえ」の返事や、APIキーのような**Claudeが代わりに取得できない値の入力**だけでよい。

## 0. ランタイム環境の構築（Node.js / Python / Chromium）

買い手のPCには何も入っていない前提で始める。**Claudeが自分でコマンドを実行して確認・インストールする**（ユーザーに手順書を渡して終わりにしない）。

### 0-1. OSを判定する

```bash
uname -s 2>/dev/null || echo "uname-not-found"
```

- `Linux` → WSL上のLinuxとして扱う（`apt`が使えることが多い）
- `Darwin` → macOS
- `MINGW*` / `MSYS*` / `uname-not-found` → Windows（Git Bash等の可能性）。この場合はコマンドプロンプト/PowerShellから`winget`で入れる案内に切り替える

### 0-2. Node.jsの確認・インストール

```bash
node --version
```

コマンドが見つからない、またはメジャーバージョンが18未満なら入れる。

| OS | インストールコマンド |
|---|---|
| Windows | `winget install -e --id OpenJS.NodeJS.LTS`（Windows 10 2004以降/11に標準搭載。無ければ https://nodejs.org/ja/ からインストーラーを落として案内する） |
| macOS | `brew install node`（Homebrewが無ければ先に `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` で入れる） |
| Linux (WSL/Ubuntu系) | `sudo apt-get update && sudo apt-get install -y nodejs npm`。バージョンが古い場合は https://github.com/nodesource/distributions の手順でLTSを入れ直す |

インストール後、必ず`node --version`で入ったことを確認してから次へ進む（シェルの再起動が必要な場合はその旨を伝える）。

### 0-3. Python 3の確認・インストール

```bash
python3 --version
```

無ければ入れる。

| OS | インストールコマンド |
|---|---|
| Windows | `winget install -e --id Python.Python.3.12` |
| macOS | `brew install python3` |
| Linux (WSL/Ubuntu系) | `sudo apt-get install -y python3 python3-pip` |

### 0-4. Pythonライブラリの導入

```bash
pip install pillow requests imageio-ffmpeg pandas
```

**Ubuntu/WSLでは`error: externally-managed-environment`で失敗することがある**（PEP 668。システム側のPythonを保護する仕様で、Ubuntu 23.04以降・最近のWSL Ubuntuイメージで標準）。このエラーが出たら黙って次を試す（ユーザーに原因を説明する必要はなく、そのまま進めてよい）:

```bash
pip install --break-system-packages pillow requests imageio-ffmpeg pandas
```

`pip`コマンドが見つからなければ`pip3`で試す。

### 0-5. Node側の依存導入とChromiumの取得

このリポジトリの2つの生成フォルダそれぞれで実行する（HTML→PNG変換に使う）。

```bash
cd テキスト画像生成 && npm install && npx playwright-core install chromium && cd ..
cd ノート画像生成 && npm install && npx playwright-core install chromium && cd ..
```

`npx playwright-core install chromium`はブラウザ本体（数十〜100MB程度）をダウンロードするので、回線が遅いと数分かかる。時間がかかっていても失敗ではないことを伝える。

### 0-6. 動作確認

```bash
cd ノート画像生成
python3 generate_note.py samples/ai_gakubu_tier.json --seed test
```

`output/ai_gakubu_tier_paper.png`ができれば成功。**この画像をユーザーに見せて「ここまでで環境構築は完了」と明確に伝える**（非技術者は動いたかどうかの判断がつかないので、ここで区切りをはっきり示すことが重要）。

うまくいかない場合によくある原因:
- `npx playwright-core install chromium`が権限エラー → 管理者権限で実行し直すか、ユーザーディレクトリ配下に入るはずなので原因を切り分ける
- `node`コマンドが見つからない → 0-2のインストール後にターミナル（Claude Codeのセッション）を再起動していない可能性が高い

---

## 1. ヒアリング

環境構築が終わったら、以下を対話で聞く。1つずつ、決め打ちで進めず必ず確認する。

- **アカウント名・ハンドル**（例: ＠〇〇。画像内のCTAに使う）
- **ジャンル**（例: 就活／筋トレ／節約／語学…）
- **投稿の構造がリスト・ランキング・チェックリストに分解できるか**（→ルートCLAUDE.md「導入時にまず決めること」の判定基準を一緒に確認する。分解できないなら、この仕組みが合わないことを正直に伝える）
- **Pexels APIキー**を持っているか（無ければ https://www.pexels.com/api/ でアカウント作成→取得してもらう。この値だけはClaudeが代わりに取得できないので、ユーザーにコピペしてもらう）
- **（任意・スキップ可）分析機能用のFacebook/Instagramログイン情報**（メールアドレス・パスワード）。`分析/`でインサイトを自動取得したい場合だけ聞く。**必ず「いま設定しますか？後回しでも大丈夫です」と選べる形で聞き、スキップされたら深追いしない**。理由を尋ねる必要もない
  - 提供された場合 → `分析/.env`に`FB_EMAIL=` `FB_PASSWORD=`として保存する（`.gitignore`で除外済みなので、コミットにもGitHubにも一切乗らない。保存したらその場で「このファイルはあなたのPCの中だけに残り、外には送信されません」と伝える）
  - スキップされた場合 → `分析/.env`は作らず、`分析/README.md`にある「後で使いたくなったら`.env.example`をコピーして書く」手順を一言案内するだけで次に進む

## 2. プレースホルダーの書き換え

聞き取った内容で、以下を書き換える。

- `テキスト画像生成/samples/*.json` / `ノート画像生成/samples/*.json` の `handle` フィールド（`＠アカウント名` → 実際のハンドル）
- `Tier表/draft/*/*.html` 内の `＠アカウント名`
- `動画生成/pexels_queries.py.example` を `pexels_queries.py` にコピーし、`PEXELS_API_KEY` を実際のキーに差し替える（`.gitignore`済みなのでコミットされない）
- 必要なら `動画生成/pexels_queries.py` にジャンル用の `PEXELS_QUERIES_<名前>` を追記し、`fetch_bg_videos.py` の `THEMES` に1行足す
- FB/IGログイン情報を受け取った場合のみ `分析/.env` を作成（上記の通り）

## 3. 最初の1本を一緒に作る

聞き取ったジャンルで実際にネタを1つ選び、以下を一緒に実行する。

1. 中身JSON（`samples/`）をそのジャンルの内容で新規作成
2. `ノート画像生成/`なら新しいデザインを1つ書き下ろす（ルートCLAUDE.md「デザインは毎回作り直す」の水準を満たすか、既存3サンプル(`kiban`/`rosen`/`karte`)と並べて確認する）
3. 背景動画を`動画生成/fetch_bg_videos.py`で1〜2本取得（内容に合うテーマで。テーマが無ければ`all`でよい）
4. `動画生成/make_note_video.py`で合成し、`完成品/`に書き出す

## 4. 引き継ぎ

- `CLAUDE.md`・各モジュールの`CLAUDE.md`を一通り読んでもらう（特に「全パターン共通のルール」）
- 以降は`分析/`でインサイトを見ながら、自分のジャンルでの伸びる型を記録・更新していく運用になることを伝える
