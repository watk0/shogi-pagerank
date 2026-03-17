import os
from pathlib import Path
from urllib.request import urlopen
import time


BASE_URL = "https://www.shogi.or.jp/game/result/{yyyymm}.html"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def iter_months(start_yyyymm: int, end_yyyymm: int) -> list[str]:
	# Generate a list like ["202504", "202505", ..., "202602"]
	months: list[str] = []
	year = start_yyyymm // 100
	month = start_yyyymm % 100
	end_year = end_yyyymm // 100
	end_month = end_yyyymm % 100
	while (year, month) <= (end_year, end_month):
		months.append(f"{year:04d}{month:02d}")
		month += 1
		if month == 13:
			year += 1
			month = 1
	return months


def download_html(yyyymm: str) -> None:
	# Download the HTML and save it into results/ as {yyyymm}.html
	url = BASE_URL.format(yyyymm=yyyymm)
	output_path = RESULTS_DIR / f"{yyyymm}.html"
	with urlopen(url) as response:
		content = response.read()
	output_path.write_bytes(content)


def main() -> None:
	# Create results/ directory if it doesn't exist
	os.makedirs(RESULTS_DIR, exist_ok=True)

	for yyyymm in iter_months(200604, 202603):
		download_html(yyyymm)
		print(f"Downloaded {yyyymm}.html")
		time.sleep(1)


if __name__ == "__main__":
	main()
