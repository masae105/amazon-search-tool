import os

import requests

import psycopg

from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from flask import Flask, jsonify, redirect, render_template, request, url_for

from bot import run_search_keywords

load_dotenv(dotenv_path=".env")

app = Flask(__name__)


def get_db_connection():
    db_host = os.getenv("DB_HOST")

    if os.getenv("K_SERVICE"):
        db_host = "/cloudsql/project-3df45723-f4b0-4dfb-9ca:asia-northeast1:amazon-search-db"

    return psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=db_host,
        port=os.getenv("DB_PORT")
    )

def save_search_history(keyword, result_count):
    conn = get_db_connection()
    cur = conn.cursor()

    searched_at = datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None)
    cur.execute(
        """
        INSERT INTO search_history (keyword, result_count, searched_at)
        VALUES (%s, %s, %s)
        """,
        (keyword, result_count, searched_at)
    )

    conn.commit()
    cur.close()
    conn.close()


def add_monitor_keyword(keyword):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO monitor_keywords (keyword) VALUES (%s)",
        (keyword,)
    )

    conn.commit()
    cur.close()
    conn.close()


def get_monitor_keywords():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, keyword, is_active, created_at "
        "FROM monitor_keywords ORDER BY id ASC"
    )

    keywords = cur.fetchall()
    cur.close()
    conn.close()
    return keywords


def get_active_monitor_keywords():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT keyword FROM monitor_keywords "
        "WHERE is_active = TRUE ORDER BY id ASC"
    )

    rows = cur.fetchall()
    keywords = [row[0] for row in rows]
    cur.close()
    conn.close()
    return keywords


def run_monitored_search():
    keywords = get_active_monitor_keywords()
    if not keywords:
        return None

    result = run_search_keywords(keywords)
    return result


def toggle_monitor_keyword(keyword_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE monitor_keywords SET is_active = NOT is_active WHERE id = %s",
        (keyword_id,)
    )

    conn.commit()
    cur.close()
    conn.close()


def delete_monitor_keyword(keyword_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM monitor_keywords WHERE id = %s",
        (keyword_id,)
    )

    conn.commit()
    cur.close()
    conn.close()


def get_search_history():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, keyword, result_count, searched_at "
        "FROM search_history ORDER BY id DESC"
    )

    history = cur.fetchall()
    cur.close()
    conn.close()
    return history


def get_product_history():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT product_name, keyword, price, product_url, checked_at, item_code "
        "FROM product_history ORDER BY checked_at DESC"
    )

    history = cur.fetchall()
    cur.close()
    conn.close()
    return history


def get_product_history_by_item_code(item_code):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT product_name, keyword, price, product_url, checked_at, item_code "
        "FROM product_history "
        "WHERE item_code = %s ORDER BY checked_at ASC",
        (item_code,)
    )

    history = cur.fetchall()
    cur.close()
    conn.close()
    return history


def convert_product_history_to_jst(history):
    jst = ZoneInfo("Asia/Tokyo")
    utc = ZoneInfo("UTC")
    converted_history = []

    for record in history:
        checked_at = record[4]
        if checked_at.tzinfo is None:
            checked_at = checked_at.replace(tzinfo=utc)
        checked_at = checked_at.astimezone(jst)
        converted_history.append(record[:4] + (checked_at,) + record[5:])

    return converted_history


def get_search_history_keyword(history_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT keyword FROM search_history WHERE id = %s",
        (history_id,)
    )

    record = cur.fetchone()
    keyword = record[0] if record else None
    cur.close()
    conn.close()
    return keyword


def delete_search_history(history_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM search_history WHERE id = %s",
        (history_id,)
    )

    conn.commit()
    cur.close()
    conn.close()


def clear_search_history():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM search_history")

    conn.commit()
    cur.close()
    conn.close()


@app.route("/monitor/toggle/<int:keyword_id>", methods=["POST"])
def toggle_monitor(keyword_id):
    toggle_monitor_keyword(keyword_id)
    return redirect(url_for("monitor"))


@app.route("/monitor/delete/<int:keyword_id>", methods=["POST"])
def delete_monitor(keyword_id):
    delete_monitor_keyword(keyword_id)
    return redirect(url_for("monitor"))


@app.route("/monitor/run", methods=["POST"])
def run_monitor_now():
    run_monitored_search()
    return redirect(url_for("monitor"))


@app.route("/api/monitor/run", methods=["POST"])
def run_monitor_api():
    result = run_monitored_search()
    if result is None:
        return jsonify(status="no_active_keywords")
    return jsonify(status="success")


@app.route("/api/check-ip")
def check_ip():
    response = requests.get("https://api.ipify.org", timeout=10)
    return jsonify(ip=response.text)


@app.route("/api/rakuten-test", methods=["GET"])
def rakuten_test():
    application_id = os.getenv("RAKUTEN_APPLICATION_ID")
    access_key = os.getenv("RAKUTEN_ACCESS_KEY")

    if not application_id or not access_key:
        return jsonify(error="楽天APIの認証情報が設定されていません"), 500

    endpoint = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
    params = {
        "applicationId": application_id,
        "keyword": "USBハブ",
        "format": "json",
        "formatVersion": 2,
        "hits": 3,
    }
    headers = {"accessKey": access_key}

    try:
        response = requests.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
    except requests.HTTPError as error:
        status_code = error.response.status_code if error.response else 502
        return jsonify(error="楽天APIエラー", status_code=status_code), status_code
    except requests.RequestException:
        return jsonify(error="楽天APIへの接続に失敗しました"), 502

    items = response.json().get("Items", [])[:3]
    return jsonify(
        status_code=response.status_code,
        items=[
            {
                "itemName": item.get("itemName"),
                "itemPrice": item.get("itemPrice"),
                "itemUrl": item.get("itemUrl"),
            }
            for item in items
        ],
    )


@app.route("/monitor", methods=["GET", "POST"])
def monitor():
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        if keyword:
            add_monitor_keyword(keyword)
        return redirect(url_for("monitor"))

    monitor_keywords = get_monitor_keywords()
    return render_template("monitor.html", monitor_keywords=monitor_keywords)


@app.route("/history/clear/confirm", methods=["GET"])
def clear_history_confirm():
    return render_template("clear_history_confirm.html")


@app.route("/product-history")
def product_history():
    history = convert_product_history_to_jst(get_product_history())
    return render_template("product_history.html", history=history)


@app.route("/product-history/<item_code>")
def product_history_detail(item_code):
    history = convert_product_history_to_jst(
        get_product_history_by_item_code(item_code)
    )
    graph_labels = [
        record[4].strftime("%Y-%m-%d %H:%M")
        for record in history
    ]
    graph_prices = [record[2] for record in history]

    return render_template(
        "product_history.html",
        history=history,
        detail=True,
        graph_labels=graph_labels,
        graph_prices=graph_prices,
    )


@app.route("/history/clear", methods=["POST"])
def clear_history():
    clear_search_history()
    return redirect(url_for("index"))


@app.route("/history/delete/<int:history_id>", methods=["POST"])
def delete_history(history_id):
    delete_search_history(history_id)
    return redirect(url_for("index"))


@app.route("/history/research/<int:history_id>", methods=["POST"])
def research_history(history_id):
    global stored_results, stored_keyword, stored_searched, stored_error

    history_keyword = get_search_history_keyword(history_id)
    if history_keyword is None:
        return redirect(url_for("index"))

    stored_keyword = history_keyword
    stored_results = []
    stored_searched = True
    stored_error = None

    try:
        keywords = [
            keyword.strip()
            for keyword in history_keyword.split(", ")
            if keyword.strip()
        ]
        search_results = run_search_keywords(keywords)
        stored_results = search_results.to_dict(orient="records")
        save_search_history(", ".join(keywords), len(stored_results))
    except Exception as e:
        print("検索エラー:", e)
        stored_error = "検索中にエラーが発生しました"

    return redirect(url_for("index"))


PAGE_SIZE = 10
stored_results = []
stored_keyword = ""
stored_searched = False
stored_error = None

@app.route("/", methods=["GET", "POST"])
def index():
    global stored_results, stored_keyword, stored_searched, stored_error

    page = request.args.get("page", 1, type=int) or 1

    if request.method == "POST":
        page = 1
        stored_keyword = request.form.get("keyword", "")
        stored_results = []
        stored_searched = True
        stored_error = None

        try:
            keywords = [
                line.strip()
                for line in stored_keyword.splitlines()
                if line.strip()
            ]
            search_results = run_search_keywords(keywords)
            stored_results = search_results.to_dict(orient="records")
            save_search_history(", ".join(keywords), len(stored_results))
        except Exception as e:
            print("検索エラー:", e)
            stored_error = "検索中にエラーが発生しました"

    total_pages = (len(stored_results) + PAGE_SIZE - 1) // PAGE_SIZE
    if total_pages:
        current_page = max(1, min(page, total_pages))
        start = (current_page - 1) * PAGE_SIZE
        results = stored_results[start:start + PAGE_SIZE]
    else:
        current_page = 1
        results = []

    history = get_search_history()

    return render_template(
        "index.html",
        keyword=stored_keyword,
        results=results,
        searched=stored_searched,
        error=stored_error,
        current_page=current_page,
        total_pages=total_pages,
        history=history
    )


if __name__ == "__main__":
    app.run(debug=True)