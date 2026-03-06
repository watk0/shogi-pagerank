# 使い方

## 必要なライブラリのインストール

```bash
pip install -r requirements.txt
```

## 実行手順

以下の3ステップでPageRankを計算する。

### ステップ1: 対局結果HTMLのダウンロード

```bash
python src/get_result_from_webpage.py
```

日本将棋連盟の対局結果ページから、2006年4月〜2026年3月分のHTMLを取得し `data/raw/` に保存する。

### ステップ2: HTMLからCSVへの変換

```bash
python src/html_to_csv.py
```

`data/raw/` 内のHTMLを解析し、年度ごとの対局結果CSVを `data/processed/` に出力する。

### ステップ3: PageRankの計算

```bash
python src/calc_pagerank.py
```

`data/processed/` 内のCSVを読み込み、年度ごとのPageRankを計算して `data/outputs/` にCSVで出力する。

## ディレクトリ構成

```
shogi-pagerank/
├── data/
│   ├── raw/          # ダウンロードした対局結果HTML
│   ├── processed/    # 年度別対局結果CSV
│   └── outputs/      # PageRank計算結果CSV
├── src/
│   ├── get_result_from_webpage.py  # ステップ1
│   ├── html_to_csv.py              # ステップ2
│   └── calc_pagerank.py            # ステップ3
├── requirements.txt
├── README.md
└── USAGE.md
```
