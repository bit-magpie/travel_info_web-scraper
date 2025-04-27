import os
import requests
from tqdm import tqdm
from ..utils import Logger

logger = Logger()


def download_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes (e.g., 404)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching the page: {e}"

# Example usage

save_dir = "raw_html"
os.makedirs(save_dir, exist_ok=True)

japan_prefectures = [
    "Hokkaido",
    "Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima",
    "Ibaraki", "Tochigi", "Gunma", "Saitama", "Chiba", "Tokyo", "Kanagawa",
    "Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano", "Gifu", "Shizuoka", "Aichi",
    "Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama",
    "Tottori", "Shimane", "Okayama", "Hiroshima", "Yamaguchi",
    "Tokushima", "Kagawa", "Ehime", "Kochi",
    "Fukuoka", "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima", "Okinawa"
]

base_url = "https://j100s.com/en/{pref}.html"


for pref in tqdm(japan_prefectures):
    url = base_url.replace("{pref}", pref)
    try:
        html_content = download_webpage(url)
    except Exception as e:
        logger.error(f"download failed: {url}")
        continue
    with open(f"{save_dir}/{pref}.html", "w", encoding='utf-8') as f:
        logger.info(f"writing {url} to {save_dir}/{pref}.html")
        f.write(html_content)
