import os
import pandas as pd


def load_old_data(file_name):
    if not os.path.exists(file_name):
        return pd.DataFrame()

    sheets = pd.read_excel(
        file_name,
        sheet_name=None
    )

    df = pd.concat(
        sheets.values(),
        ignore_index=True
    )

    return df


def get_old_prices(df):
    if df.empty:
        return {}

    return dict(zip(
        df["ASIN"],
        df["価格"]
    ))


def get_price_down_items(df, old_prices):
    result = []

    for _, row in df.iterrows():

        asin = row["ASIN"]
        price = row["価格"]

        if asin in old_prices:

            old_price = old_prices[asin]
            if price < old_price:
                result.append({
                    "商品名": row["商品名"],
                    "ASIN": asin,
                    "前回価格": old_price,
                    "今回価格": price,
                    "値下げ額": old_price - price,
                    "商品URL": row["商品URL"]
                })

    return result


def get_old_asins(df):
    if df.empty:
        return set()

    return set(df["ASIN"])


def is_new_item(asin, old_asins):
    return asin not in old_asins


def get_new_items(df, old_asins):
    new_items = []
    for _, row in df.iterrows():
        if row["ASIN"] not in old_asins:
            new_items.append(row)

    return pd.DataFrame(new_items)