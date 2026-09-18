from flask import Flask, render_template, request
from bot import run_search

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    keyword = request.form.get("keyword", "")
    results = []
    searched = False
    error = None

    if request.method == "POST":
        searched = True
        try:
            search_results = run_search(keyword)
            results = search_results.to_dict(orient="records")
        except Exception:
            error = "検索中にエラーが発生しました"

    return render_template(
        "index.html",
        keyword=keyword,
        results=results,
        searched=searched,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)