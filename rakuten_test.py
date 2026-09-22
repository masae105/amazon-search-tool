import os

import requests
from dotenv import load_dotenv

load_dotenv()

application_id = os.getenv("RAKUTEN_APPLICATION_ID")
access_key = os.getenv("RAKUTEN_ACCESS_KEY")
endpoint = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"

if not application_id or not access_key:
	raise RuntimeError(
		"RAKUTEN_APPLICATION_ID and RAKUTEN_ACCESS_KEY must be set in .env"
	)

params = {
	"applicationId": application_id,
	"keyword": "USBハブ",
	"format": "json",
	"formatVersion": 2,
	"hits": 3,
}
headers = {"accessKey": access_key}

response = requests.get(endpoint, params=params, headers=headers, timeout=10)
response.raise_for_status()

print("HTTP status code:", response.status_code)

items = response.json().get("Items", [])
for item in items[:3]:
	print("商品名:", item.get("itemName"))
	print("価格:", item.get("itemPrice"))
	print("商品URL:", item.get("itemUrl"))