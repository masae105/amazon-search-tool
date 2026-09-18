from flask import Flask, render_template, request
from bot import run_search

app = Flask(__name__)

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
            search_results = run_search(stored_keyword)
            stored_results = search_results.to_dict(orient="records")
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

    return render_template(
        "index.html",
        keyword=stored_keyword,
        results=results,
        searched=stored_searched,
        error=stored_error,
        current_page=current_page,
        total_pages=total_pages
    )


if __name__ == "__main__":
    app.run(debug=True)