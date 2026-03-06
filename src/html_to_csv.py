import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict


# 設定
RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def extract_player_id(td):
	"""棋士情報のセルから棋士ID（pro/264 や lady/73 の形式）を抽出する"""
	link = td.find('a')
	if not link:
		return ""  # アマチュアなどリンクがない場合は空
	
	# /player/pro/264.html や /player/lady/73.html からIDを抽出
	match = re.search(r'/player/(pro|lady)/(\d+)\.html', link['href'])
	if match:
		return f"{match.group(1)}/{match.group(2)}"
	return ""


def parse_html_file(html_path):
	"""1つのHTMLファイルから対局結果を抽出してリストで返す"""
	# ファイル名から年月を取得（例: 202602.html → 202602）
	yyyymm = html_path.stem
	
	with open(html_path, 'r', encoding='utf-8') as f:
		soup = BeautifulSoup(f.read(), 'html.parser')
	
	# メインの対局結果テーブルを探す
	table = soup.find('table', class_='tableElements01')
	if not table:
		return []
	
	games = []
	current_date = None
	current_tournament = None
	current_tournament_url = None
	
	tbody = table.find('tbody')
	if not tbody:
		return []
	
	for row in tbody.find_all('tr'):
		cells = row.find_all('td')
		
		# 日付行の判定（colspan="6"の行）
		if len(cells) == 1 and cells[0].get('colspan') == '6':
			current_date = cells[0].text.strip()
			continue
		
		# 対局行の判定（6列 or 5列）
		# 6列: 棋戦列あり、5列: rowspanで棋戦列が省略されている
		if len(cells) == 6:
			# 棋戦情報（rowspanで複数行にまたがる場合は最初の行だけテキストがある）
			tournament_text = cells[0].get_text(strip=True)
			if tournament_text:
				current_tournament = tournament_text
				tournament_link = cells[0].find('a')
				current_tournament_url = tournament_link['href'] if tournament_link else ""
			
			# 各対局データを抽出
			game = {
				'年月': yyyymm,
				'日付': current_date,
				'棋戦': current_tournament,
				'棋戦URL': current_tournament_url,
				'先手名': cells[2].get_text(strip=True),
				'先手ID': extract_player_id(cells[2]),
				'先手結果': cells[1].text.strip(),
				'後手名': cells[3].get_text(strip=True),
				'後手ID': extract_player_id(cells[3]),
				'後手結果': cells[4].text.strip(),
			}
			games.append(game)
		elif len(cells) == 5:
			# rowspanで棋戦列が省略されている行（前の棋戦を継承）
			game = {
				'年月': yyyymm,
				'日付': current_date,
				'棋戦': current_tournament,
				'棋戦URL': current_tournament_url,
				'先手名': cells[1].get_text(strip=True),
				'先手ID': extract_player_id(cells[1]),
				'先手結果': cells[0].text.strip(),
				'後手名': cells[2].get_text(strip=True),
				'後手ID': extract_player_id(cells[2]),
				'後手結果': cells[3].text.strip(),
			}
			games.append(game)
	
	return games


def get_fiscal_year(yyyymm: str) -> int:
	"""YYYYMM形式から日本の会計年度を取得する
	
	例：
	- 200604 → 2006年度（2006年4月～2007年3月）
	- 200703 → 2006年度
	- 200704 → 2007年度
	"""
	year = int(yyyymm[:4])
	month = int(yyyymm[4:6])
	
	if month >= 4:  # 4月～12月は同じ年の会計年度
		return year
	else:  # 1月～3月は前年の会計年度
		return year - 1


def main():
	"""results/フォルダの全HTMLを処理して、年度ごとにCSVを出力する"""
	# 出力ディレクトリが存在しない場合は作成
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	
	# resultsフォルダ内の全HTMLファイルを取得（ソート順）
	html_files = sorted(RESULTS_DIR.glob('*.html'))
	
	if not html_files:
		print("HTMLファイルが見つかりませんでした")
		return
	
	# 年度ごとにゲームをグループ化
	games_by_fiscal_year = defaultdict(list)
	
	for html_file in html_files:
		print(f"処理中: {html_file.name}")
		games = parse_html_file(html_file)
		
		# 各ゲームを会計年度でグループ化
		yyyymm = html_file.stem
		fiscal_year = get_fiscal_year(yyyymm)
		games_by_fiscal_year[fiscal_year].extend(games)
	
	# 年度ごとにCSVを出力
	fieldnames = ['年月', '日付', '棋戦', '棋戦URL', '先手名', '先手ID', 
	              '先手結果', '後手名', '後手ID', '後手結果']
	
	for fiscal_year in sorted(games_by_fiscal_year.keys()):
		games = games_by_fiscal_year[fiscal_year]
		output_csv = OUTPUT_DIR / f"{fiscal_year}年度.csv"
		
		with open(output_csv, 'w', encoding='utf-8', newline='') as f:
			writer = csv.DictWriter(f, fieldnames=fieldnames)
			writer.writeheader()
			writer.writerows(games)
		
		print(f"完了: {fiscal_year}年度の {len(games)}件の対局を {output_csv.name} に出力しました")
	
	print(f"\n全処理完了: {len(games_by_fiscal_year)}年度のCSVを出力しました")


if __name__ == "__main__":
	main()
