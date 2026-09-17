
import os

from dotenv import load_dotenv


load_dotenv()

NG_WORDS = [
    "映画",
    "DVD",
    "Prime Video",
]

OUTPUT_FILE = "Amazon検索結果.xlsx"

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")