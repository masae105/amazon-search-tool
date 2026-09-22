import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
RESULT_COLUMNS = ["商品名", "価格", "商品URL", "ASIN", "ページ"]


def search_rakuten(keyword):
    application_id = os.getenv("RAKUTEN_APPLICATION_ID")
    access_key = os.getenv("RAKUTEN_ACCESS_KEY")

    if not application_id or not access_key:
        raise RuntimeError(
            "RAKUTEN_APPLICATION_ID and RAKUTEN_ACCESS_KEY must be set"
        )

    params = {
        "applicationId": application_id,
        "keyword": keyword,
        "format": "json",
        "formatVersion": 2,
    }
    headers = {"accessKey": access_key}

    response = requests.get(
        ENDPOINT,
        params=params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()

    products = []
    for item in response.json().get("Items", []):
        item_code = item.get("itemCode")
        if not item_code:
            continue

        products.append(
            {
                "商品名": item.get("itemName"),
                "価格": item.get("itemPrice"),
                "商品URL": item.get("itemUrl"),
                "ASIN": item_code,
                "ページ": 1,
            }
        )

    results = pd.DataFrame(products, columns=RESULT_COLUMNS)
    results["価格"] = pd.to_numeric(results["価格"], errors="coerce")
    return results
