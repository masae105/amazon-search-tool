import os

import psycopg
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for

from bot import run_search_keywords

load_dotenv(dotenv_path=".env")

app = Flask(__name__)


def get_db_connection():
    return psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


def save_search_history(keyword, result_count):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO search_history (keyword, result_count) VALUES (%s, %s)",
        (keyword, result_count)
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
    except Exception:
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
        except Exception:
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