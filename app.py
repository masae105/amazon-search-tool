from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Amazon商品検索ツール"


if __name__ == "__main__":
    app.run(debug=True)