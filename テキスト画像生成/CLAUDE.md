# CLAUDE.md — テキスト画像生成（投稿パターン1）

## これは何

白背景に極太ゴシックで「タイトル→箇条書き→CTA」だけを積んだシンプルなカードを、HTML/CSS→PNGで直接生成する。装飾を削ぎ、情報量そのもので見せるのがこのパターンの持ち味。

## ノート画像生成（パターン3）との違い

同じ「HTML/CSS→PNG→`動画生成/make_note_video.py`で背景動画に合成」という土台を使うが、デザイン運用の方針が逆になる。

| | ノート画像生成（パターン3） | テキスト画像生成（パターン1） |
|---|---|---|
| 見た目 | モチーフごとに投稿ごとに別デザイン | 白いカード＋太いゴシック、飾りなしの定番1本 |
| デザイン方針 | **毎回新しく作り直す**（`designs/`は記録） | **基本 `plain` を使い回す** |
| 情報量 | タイトル・項目・CTAをモチーフで飾る | 装飾を削ぎ、情報量そのもので見せる |

`designs/`に複数デザインを置ける構造にはしてあるが、これは「飽きが来たら足す」ための余地であって、パターン3のように投稿ごとに増やす前提ではない。

## 「画像作って」と言われたらやること

1. **このCLAUDE.mdを読む**
2. **ネタを考える**（指定があればそれを使う）
3. **ルートの`分析/`とパフォーマンス分析の記録を見る**（あれば）
4. **中身JSONを書く**（`samples/<slug>.json`）
5. `python3 generate_text_image.py samples/<slug>.json` で生成 → PNGを目視確認
6. 背景動画があれば`動画生成/make_note_video.py`でそのまま合成して`完成品/`に書き出す

## 使い方

```bash
python3 generate_text_image.py samples/kansuu_technique.json           # JSONの design で生成（既定 plain）
python3 generate_text_image.py samples/kansuu_technique.json --preview # 確認用 _preview.png も出す
python3 generate_text_image.py samples/kansuu_technique.json --no-jitter   # カード幅の揺らぎを止める
python3 generate_text_image.py samples/kansuu_technique.json --seed abc    # カード幅を振り直す
python3 generate_text_image.py --list                                  # designs/ の一覧
```

出力（`output/`）:
- `<slug>_paper.png` … **カードだけ・背景透過**。これを`動画生成/make_note_video.py`に渡す
- `<slug>_preview.png` … `--preview`を付けたときだけ（背景つきの確認用）

## 中身JSONの書き方

```json
{
  "slug": "英数字の出力ファイル名",
  "design": "使うデザイン名（省略時は plain）",
  "title": "大タイトル（例: 関数のグラフ\n裏ワザ知らないのは損😭）",
  "items": ["①〜の項目を配列で。数はいくつでもOK"],
  "cta_line": "締めのCTA（例: 後悔しないように保存‼️）"
}
```

`eyebrow` / `hook` / 締めの一言（`note`）は持たない。ルートCLAUDE.md「小さい文字の補足を置かない」のとおり、このパターンはもともとタイトル・項目・CTAの3要素しかない。

**インライン装飾記法**（`title` / `items` / `cta_line`で使える）:

| 書き方 | 変換先 | 見え方（`plain`） |
|---|---|---|
| `[[ここ]]` | `<span class="em">` | 赤 |
| `{{ここ}}` | `<span class="kw">` | 青 |
| `__ここ__` | `<u>` | 黄マーカー |
| 改行（`\n`） | `<br>` | 意味の切れ目で手で折る |

装飾記法は**使いたいときだけ**使う（毎回使う必要はない。使いすぎると"飾らない"という持ち味が消える）。

## ★2行以上になる文は、自分で改行を入れる

ルートCLAUDE.mdの共通ルール。`title`を2行に割るときは`\n`で意味の切れ目（句点・読点・文節の頭）を自分で指定する。自動折り返しに任せない。

```json
"title": "関数のグラフ\n裏ワザ知らないのは損😭"
```

保険として`designs/common.py`の`BASE_CSS`が`line-break: strict`を効かせている（`ゃゅょっー`の行頭を禁止するだけで、意味の切れ目までは面倒を見ない）。

## 文字数の目安（`plain`での実測値の一例。ジャンル・フォントで変わるので実際に出力して確認する）

| 項目 | 目安 | 超えるとどうなる |
|---|---|---|
| `title`（1行あたり） | 12文字以内 | render.js が自動でフォントサイズを縮める（ログに出る） |
| `items`（1項目） | 20文字以内 | 折り返して2行になる（崩れはしないが行間が詰まって見える） |
| `cta_line` | 14文字以内 | 折り返して2行になる |

`items`は5〜7個が収まりの良い目安（8個を超えると縦に伸びてカードが縦長になりすぎる。そのときはカード幅ではなく項目数を見直す）。

出力したPNGは必ず目視確認すること（崩れは実行時にエラーにならない）。

## ★量産に見せない: カード幅は毎回わずかに変わる

`generate_text_image.py`は生成のたびに`.paper`の幅を±5.5%ランダムにずらす（ルートCLAUDE.md「量産に見せない」参照）。乱数の種は既定でslug（投稿ごとに固定）。`--no-jitter`で無効化、`--seed <文字列>`で振り直し。

## フォルダ / ファイルの役割

- `generate_text_image.py` … ドライバ（JSON読み → デザイン選択 → 幅の揺らぎ → HTML組み立て → render.js 呼び出し）
- `designs/` … デザイン置き場。`plain`（白カード＋極太ゴシック）が既定かつ基本これだけでよい
  - `designs/common.py` … 全デザイン共通の部品（装飾記法の変換・丸数字・改行ルール）
  - `designs/<名前>.py` … `LABEL` / `CSS` / `build_body(c)` の3つを持つ
- `render.js` … HTML→PNGレンダラ（`ノート画像生成/render.js`と同じ実装。playwright-core＋キャッシュ済chromium）
- `samples/` … 中身JSONの置き場
- `draft/` … 生成された作業用HTML
- `output/` … PNG出力

フォントは`fonts/`を持たない。太いゴシックが必要なだけなので、環境の**Noto Sans CJK JP**（Black〜Boldの太さ）をfamily名で直接指定している。

## 依存

`ノート画像生成/`と同じ。初回に各フォルダで`npm install`が必要（`package.json`に`playwright-core`を記載）。
