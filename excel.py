import pandas as pd
import openpyxl
from config import OUTPUT_FILE


def save_excel(df):
    file_name = OUTPUT_FILE

    with pd.ExcelWriter(file_name) as writer:
        for page in df["ページ"].unique():
            df_page = df[df["ページ"] == page]

            df_page = df_page.drop(columns=["ページ"])

            df_page.to_excel(
                writer,
                sheet_name=f"ページ{page}",
                index=False
            )

    # openpyxlでExcelを開く
    wb = openpyxl.load_workbook(file_name)

    for ws in wb.worksheets:
        # 列幅調整
        ws.column_dimensions["A"].width = 40  # 商品名
        ws.column_dimensions["B"].width = 10  # 価格
        ws.column_dimensions["C"].width = 15  # ASIN
        ws.column_dimensions["D"].width = 60  # 商品URL

    # 保存
    wb.save(file_name)