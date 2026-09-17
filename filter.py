from config import NG_WORDS


def filter_products(df, keyword):
    print(f"フィルター前：{len(df)}件")

    df = df[df["商品名"].str.contains(keyword, na=False)]

    for word in NG_WORDS:
        df = df[~df["商品名"].str.contains(word, na=False)]

    # ASIN重複削除
    df = df.drop_duplicates(subset="ASIN")

    print(f"filter後 :{len(df)}件")

    return df

        
