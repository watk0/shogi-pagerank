import csv
import networkx as nx
from pathlib import Path


# 設定
RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "outputs"


def build_graph_from_csv(csv_path):
	"""CSVから対局結果を読み込み、敗者→勝者の有向グラフを作る（pro棋士のみ）"""
	G = nx.DiGraph()
	id_to_name = {}  # ID/名前 → 表示用名前のマッピング
	
	with open(csv_path, 'r', encoding='utf-8') as f:
		reader = csv.DictReader(f)
		
		for row in reader:
			# 先手と後手の情報を取得
			player1_name = row['先手名']
			player1_id = row['先手ID']
			player1_result = row['先手結果']
			
			player2_name = row['後手名']
			player2_id = row['後手ID']
			player2_result = row['後手結果']
			
			# 結果が空の場合（未対局）はスキップ
			if not player1_result or not player2_result:
				continue
			
			# 棋士の識別子（IDがあればID、なければ名前）
			player1 = player1_id if player1_id else player1_name
			player2 = player2_id if player2_id else player2_name
			
			# "pro"を含まない棋士はスキップ（女流棋士などを除外）
			if 'pro' not in player1 or 'pro' not in player2:
				continue
			
			# 名前マッピングに登録
			id_to_name[player1] = player1_name
			id_to_name[player2] = player2_name
			
			# 勝敗判定：○□が勝ち、●■が負け
			if player1_result in ('○', '□') and player2_result in ('●', '■'):
				# 先手勝ち → 後手（敗者）から先手（勝者）へリンク
				if G.has_edge(player2, player1):
					G[player2][player1]['weight'] += 1
				else:
					G.add_edge(player2, player1, weight=1)
			elif player1_result in ('●', '■') and player2_result in ('○', '□'):
				# 後手勝ち → 先手（敗者）から後手（勝者）へリンク
				if G.has_edge(player1, player2):
					G[player1][player2]['weight'] += 1
				else:
					G.add_edge(player1, player2, weight=1)
	
	return G, id_to_name


def main():
	# 出力ディレクトリが存在しない場合は作成
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	
	# results/フォルダの全CSV（年度ごと）を取得
	csv_files = sorted(RESULTS_DIR.glob('*年度.csv'))
	
	if not csv_files:
		print("年度別のCSVファイルが見つかりませんでした")
		return
	
	print(f"合計 {len(csv_files)} 年度のCSVを処理します\n")
	
	for csv_path in csv_files:
		fiscal_year = csv_path.stem  # ファイル名から年度を取得（例：2006年度）
		print(f"=== {fiscal_year} の処理を開始 ===")
		
		# グラフを構築
		G, id_to_name = build_graph_from_csv(csv_path)
		
		if G.number_of_nodes() == 0:
			print(f"{fiscal_year}: データが見つかりませんでした\n")
			continue
		
		print(f"ノード数（棋士数）: {G.number_of_nodes()}")
		print(f"エッジ数（勝利リンク数）: {G.number_of_edges()}")
		
		# PageRankを計算（エッジの重みを考慮）
		print("PageRankを計算中...")
		pagerank = nx.pagerank(G, weight='weight')
		
		# スコアでソートして上位を表示
		sorted_players = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
		
		print(f"\n=== {fiscal_year} PageRankトップ10 ===")
		for i, (player, score) in enumerate(sorted_players[:10], 1):
			name = id_to_name.get(player, player)
			print(f"{i:2d}. {name:20s} ({player:15s}) {score:.6f}")
		
		# CSVに出力
		output_path = OUTPUT_DIR / f"pagerank_results_{fiscal_year}.csv"
		with open(output_path, 'w', encoding='utf-8', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(['順位', '棋士名', '棋士ID', 'PageRankスコア'])
			for i, (player, score) in enumerate(sorted_players, 1):
				name = id_to_name.get(player, player)
				writer.writerow([i, name, player, score])
		
		print(f"結果を {output_path.name} に出力しました\n")


if __name__ == "__main__":
	main()
