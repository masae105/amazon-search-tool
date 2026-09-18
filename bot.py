import pandas as pd
from datetime import datetime

from scraper import search_amazon
from excel import save_excel
from config import OUTPUT_FILE
from filter import filter_products
from compare import (
    load_old_data,
    get_old_asins,
    get_old_prices,
    get_new_items,
    get_price_down_items
)
from slack import (send_slack, create_notification_message)
from log import send_log


def _search_and_prepare(keyword, include_keyword=False):
    data = search_amazon(keyword)
    df = pd.DataFrame(data)

    if df.empty:
        return df, len(data)

    df = filter_products(df, keyword)

    df["価格"] = (
        df["価格"]
        .str.replace(",", "", regex=False)
    )

    df["価格"] = pd.to_numeric(df["価格"], errors="coerce")
    df = df.sort_values("価格").reset_index(drop=True)
    df = df.dropna(subset=["価格"])
    df["価格"] = df["価格"].astype(int)

    if include_keyword:
        df["検索キーワード"] = keyword

    return df, len(data)


def run_search(keyword):
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    old_df = load_old_data(OUTPUT_FILE)
    old_asins = get_old_asins(old_df)

    df, total_count = _search_and_prepare(keyword)

    if df.empty:
        return df

    new_df = get_new_items(df, old_asins)
    old_prices = get_old_prices(old_df)
    price_down_items = get_price_down_items(df, old_prices)

    save_excel(df)

    message = create_notification_message(
        new_df,
        price_down_items
    )
    slack_success = False
    if message:
        slack_success = send_slack(message)

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    send_log(
        keyword=keyword,
        total_count=total_count,
        filter_count=len(df),
        new_count=len(new_df),
        price_down_count=len(price_down_items),
        start_time=start_time,
        end_time=end_time,
        slack_success=slack_success
    )

    return df


def run_search_keywords(keywords):
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    old_df = load_old_data(OUTPUT_FILE)
    old_asins = get_old_asins(old_df)

    results = []
    total_count = 0

    for keyword in keywords:
        df, count = _search_and_prepare(
            keyword,
            include_keyword=True
        )
        total_count += count

        if not df.empty:
            results.append(df)

    if not results:
        return pd.DataFrame()

    df = pd.concat(results, ignore_index=True)

    new_df = get_new_items(df, old_asins)
    old_prices = get_old_prices(old_df)
    price_down_items = get_price_down_items(df, old_prices)

    save_excel(df)

    message = create_notification_message(
        new_df,
        price_down_items
    )
    slack_success = False
    if message:
        slack_success = send_slack(message)

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    send_log(
        keyword="、".join(keywords),
        total_count=total_count,
        filter_count=len(df),
        new_count=len(new_df),
        price_down_count=len(price_down_items),
        start_time=start_time,
        end_time=end_time,
        slack_success=slack_success
    )

    return df