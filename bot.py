import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from rakuten import search_rakuten
from excel import save_excel
from filter import filter_products
from product_history import (
    get_db_connection,
    get_latest_price,
    save_product_history,
)
from slack import (send_slack, create_notification_message)


def _search_and_prepare(keyword, include_keyword=False):
    df = search_rakuten(keyword)

    if df.empty:
        return df, len(df)

    df = filter_products(df, keyword)

    print(f"フィルター後件数：{len(df)}件", flush=True)

    df["価格"] = (
        df["価格"].astype(str)
        .str.replace(",", "", regex=False)
    )

    df["価格"] = pd.to_numeric(df["価格"], errors="coerce")
    df = df.sort_values("価格").reset_index(drop=True)
    df = df.dropna(subset=["価格"])
    df["価格"] = df["価格"].astype(int)

    if include_keyword:
        df["検索キーワード"] = keyword

    return df, len(df)


def _check_price_history(df, keyword):
    new_items = []
    price_down_items = []

    with get_db_connection() as conn:
        for _, row in df.iterrows():
            item_code = row["ASIN"]
            current_price = row["価格"]
            previous_price = get_latest_price(conn, item_code)

            if previous_price is None:
                new_items.append(row)
            elif current_price < previous_price:
                price_down_items.append({
                    "商品名": row["商品名"],
                    "商品URL": row["商品URL"],
                    "前回価格": previous_price,
                    "今回価格": current_price,
                    "値下げ額": previous_price - current_price,
                })

            history_keyword = row.get("検索キーワード", keyword)
            save_product_history(
                conn,
                history_keyword,
                item_code,
                row["商品名"],
                current_price,
                row["商品URL"],
            )

        conn.commit()

    new_df = pd.DataFrame(new_items, columns=df.columns)
    return new_df, price_down_items


def run_search(keyword):
    start_time = datetime.now(ZoneInfo("Asia/Tokyo"))

    df, total_count = _search_and_prepare(keyword)

    if df.empty:
        return df

    new_df, price_down_items = _check_price_history(df, keyword)

    save_excel(df)

    if not new_df.empty or price_down_items:
        message = create_notification_message(
            new_df,
            price_down_items
        )
        slack_success = send_slack(message)

    end_time = datetime.now(ZoneInfo("Asia/Tokyo"))

    return df


def run_search_keywords(keywords, notification_settings=None):
    start_time = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")

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
        if notification_settings is not None:
            print("取得件数: 0", flush=True)
            print("新商品: 0", flush=True)
            print("値下げ: 0", flush=True)
            print("Slack通知: なし", flush=True)
        return pd.DataFrame()

    df = pd.concat(results, ignore_index=True)

    new_df, price_down_items = _check_price_history(df, "、".join(keywords))

    save_excel(df)

    if notification_settings is not None:
        if notification_settings.get("notify_new_items") is False:
            new_df = new_df.iloc[0:0]

        if notification_settings.get("notify_price_drops") is False:
            price_down_items = []
        else:
            min_amount = notification_settings.get("min_price_drop_amount") or 0
            min_percent = notification_settings.get("min_price_drop_percent") or 0
            price_down_items = [
                item for item in price_down_items
                if (
                    min_amount <= 0
                    or item["値下げ額"] >= min_amount
                )
                and (
                    min_percent <= 0
                    or item["値下げ額"] / item["前回価格"] * 100 >= min_percent
                )
            ]

    if notification_settings is not None:
        print(f"取得件数: {total_count}", flush=True)
        print(f"新商品: {len(new_df)}", flush=True)
        print(f"値下げ: {len(price_down_items)}", flush=True)

    should_notify = bool(not new_df.empty or price_down_items)
    if notification_settings is not None:
        should_notify = should_notify or (
            notification_settings.get("notify_no_change") is True
        )

    slack_success = None
    if should_notify:
        message = create_notification_message(
            new_df,
            price_down_items
        )
        slack_success = send_slack(message)

    if notification_settings is not None:
        if slack_success is None:
            slack_status = "なし"
        elif slack_success:
            slack_status = "送信"
        else:
            slack_status = "失敗"
        print(
            f"Slack通知: {slack_status}",
            flush=True,
        )

    end_time = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")

    return df