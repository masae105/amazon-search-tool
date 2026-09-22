from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


def search_amazon(keyword):
    # Chrome起動
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)

    data = []

    for page in range(1, 4):
        print(f"{page}ページ目取得開始", flush=True)

        # Amazon検索URL
        url = f"https://www.amazon.co.jp/s?k={keyword}&page={page}"
        print(f"取得URL：{url}", flush=True)

        # Amazonを開く
        driver.get(url)

        # 読み込み待機
        time.sleep(5)

        print(f"ページタイトル：{driver.title}", flush=True)

        # 商品一覧取得
        items = driver.find_elements(
            By.CSS_SELECTOR,
            "div[data-component-type='s-search-result']"
        )

        for item in items:
            try:
                title = item.find_element(
                    By.CSS_SELECTOR,
                    "h2 span"
                ).text
            except:
                continue

            # ASIN取得
            asin = item.get_attribute("data-asin")

            if not asin:
                continue

            # 商品URL作成
            link = f"https://www.amazon.co.jp/dp/{asin}"

            try:
                price = item.find_element(By.CLASS_NAME, "a-price-whole").text
            except:
                price = ""

            data.append({
                "ページ": page,
                "商品名": title,
                "価格": price,
                "ASIN": asin,
                "商品URL": link
            })

        print(f"{page}ページ目 現在取得件数：{len(data)}件", flush=True)

    driver.quit()

    return data
