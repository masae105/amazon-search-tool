import requests

from datetime import datetime
from zoneinfo import ZoneInfo

from config import SLACK_WEBHOOK_URL


def send_slack(message):
    payload = {
        "text": message
    }

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json=payload
    )

    if response.status_code == 200:
        print("Slack通知成功")
        return True

    else:
        print("Slack通知失敗")
        print(f"Slack送信エラー: HTTP {response.status_code}")
        return False


def send_result_notification(df):
    lowest = df.iloc[0]

    message = f"""
🏆 最安値商品

1. {lowest['商品名']}
価格：{lowest['価格']}円
URL：
{lowest['商品URL']}
"""

    send_slack(message)


def create_notification_message(new_df, price_down_items):
    message = "🛒 楽天商品検索通知\n\n"

    if not new_df.empty:
        message += "🆕 新商品\n"
        message += "--------------------\n"

        for i, row in new_df.iterrows():
            message += f"""
{i+1}. {row['商品名']}

💰 {row['価格']:,}円

🔗 {row['商品URL']}
--------------------
"""

    if price_down_items:
        message += "\n📉 値下げ商品\n"
        message += "--------------------\n"

        for i, item in enumerate(price_down_items, start=1):
            message += f"""
{i}. {item['商品名']}

💰 {item['前回価格']:,}円
⬇️ {item['今回価格']:,}円

🔥 {item['値下げ額']:,}円値下げ

🔗 {item['商品URL']}

--------------------
"""

    finish_time = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")
    message += f"""
    ⏰ 完了時刻：{finish_time}
    """

    return message


if __name__ == "__main__":
    send_slack("楽天商品検索Bot テスト通知")
