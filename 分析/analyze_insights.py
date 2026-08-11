# Meta Business Suiteエクスポート（投稿インサイト）の傾向分析
# 使い方: cd 分析 && python3 analyze_insights.py
import pandas as pd
from pathlib import Path

# 分析/ にある insights_*.csv のうち最新のものを使う（再エクスポートしたら自動で切り替わる）
CSV = sorted((Path(__file__).parent).glob("insights_*.csv"))[-1]

df = pd.read_csv(CSV, encoding="utf-8-sig")
df = df.rename(columns={
    "説明": "caption", "時間(秒)": "duration_s", "公開時間": "published",
    "投稿タイプ": "type", "ビュー": "views", "リーチ": "reach",
    "ええやん！": "likes", "わけわけ数": "shares", "フォロー数": "follows",
    "つっこみ": "comments", "保存数": "saves",
})
df["published"] = pd.to_datetime(df["published"], format="%m/%d/%Y %H:%M")
for c in ["views", "reach", "likes", "shares", "follows", "comments", "saves", "duration_s"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.sort_values("published").reset_index(drop=True)
df["gap_days"] = df["published"].diff().dt.total_seconds() / 86400
df["save_rate"] = df["saves"] / df["views"] * 1000    # 保存/1000ビュー
df["share_rate"] = df["shares"] / df["views"] * 1000
df["follow_rate"] = df["follows"] / df["views"] * 1000
df["weekday"] = df["published"].dt.day_name()
df["hour"] = df["published"].dt.hour
df["title"] = df["caption"].fillna("(キャプションなし)").str.split("\n").str[0].str.slice(0, 38)

pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 100)

print("=" * 80)
print(f"投稿数: {len(df)}  期間: {df['published'].min():%Y/%m/%d} 〜 {df['published'].max():%Y/%m/%d}")
print(f"タイプ内訳:\n{df['type'].value_counts().to_string()}")
print()

print("=" * 80)
print("■ 全投稿（時系列・投稿間隔つき）")
cols = ["published", "gap_days", "views", "reach", "likes", "saves", "shares", "follows", "title"]
out = df[cols].copy()
out["published"] = out["published"].dt.strftime("%m/%d %H:%M")
out["gap_days"] = out["gap_days"].round(1)
print(out.to_string(index=False))
print()

print("=" * 80)
print("■ 仮説検証: 投稿間隔とビュー数の関係")
d = df.dropna(subset=["gap_days"])
bins = [0, 1.5, 3, 7, 1000]
labels = ["毎日ペース(〜1.5日)", "2〜3日空け", "3〜7日空け", "1週間以上空け"]
d = d.assign(gap_bucket=pd.cut(d["gap_days"], bins=bins, labels=labels))
g = d.groupby("gap_bucket", observed=True).agg(
    n=("views", "size"),
    ビュー中央値=("views", "median"),
    ビュー平均=("views", "mean"),
    ビュー最大=("views", "max"),
    保存率=("save_rate", "median"),
    フォロー率=("follow_rate", "median"),
)
print(g.round(1).to_string())
corr = d["gap_days"].corr(d["views"], method="spearman")
print(f"\n投稿間隔×ビューのSpearman相関: {corr:.3f}  (0=無関係, 1=間隔が長いほど伸びる)")
print()

print("=" * 80)
print("■ ビューTOP10 と ワースト5")
top = df.nlargest(10, "views")[["published", "gap_days", "views", "saves", "follows", "title"]]
top["published"] = top["published"].dt.strftime("%m/%d")
print(top.round(1).to_string(index=False))
print("--- ワースト5 ---")
worst = df.nsmallest(5, "views")[["published", "gap_days", "views", "saves", "follows", "title"]]
worst["published"] = worst["published"].dt.strftime("%m/%d")
print(worst.round(1).to_string(index=False))
print()

print("=" * 80)
print("■ 保存率TOP5（保存/1000ビュー: フォロワー増に効く指標）")
st = df.nlargest(5, "save_rate")[["published", "views", "saves", "save_rate", "title"]]
st["published"] = st["published"].dt.strftime("%m/%d")
print(st.round(2).to_string(index=False))
print()

print("=" * 80)
print("■ 曜日・時間帯別の中央値ビュー")
print(df.groupby("weekday")["views"].agg(["size", "median"]).reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]).dropna().to_string())
print()
print(df.assign(时=pd.cut(df["hour"], [0, 12, 17, 20, 24], labels=["午前", "昼〜夕方", "18-20時", "21時以降"]))
      .groupby("时", observed=True)["views"].agg(["size", "median"]).to_string())
print()

print("=" * 80)
print("■ 月別推移")
m = df.set_index("published").resample("ME").agg(
    投稿数=("views", "size"), ビュー中央値=("views", "median"), ビュー合計=("views", "sum"),
    フォロー合計=("follows", "sum"))
m.index = m.index.strftime("%Y-%m")
print(m.to_string())
