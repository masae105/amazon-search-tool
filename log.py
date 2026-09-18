from slack import send_slack


def send_log(
    keyword,
    total_count,
    filter_count,
    new_count,
    price_down_count,
    start_time,
    end_time,
    slack_success
):
    message = f"""

=============================
Amazon検索Bot 実行ログ
=============================
開始時刻    :{start_time}

検索ワード  :{keyword}

取得件数    :{total_count}
フィルター後 : {filter_count}件

新商品 : {new_count}件
値下げ商品 : {price_down_count}件

Excel保存 : OK
Slack通知 : {"OK" if slack_success else "NG"}

終了時刻 : {end_time}
==============================
"""

    print(message)

    send_slack(message)
