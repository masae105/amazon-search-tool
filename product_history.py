import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

CLOUD_SQL_SOCKET = (
    "/cloudsql/project-3df45723-f4b0-4dfb-9ca:"
    "asia-northeast1:amazon-search-db"
)


def get_db_connection():
    db_host = os.getenv("DB_HOST")

    if os.getenv("K_SERVICE"):
        db_host = CLOUD_SQL_SOCKET

    return psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=db_host,
        port=os.getenv("DB_PORT"),
    )


def get_latest_price(connection, item_code):
    query = """
        SELECT price
        FROM product_history
        WHERE item_code = %s
        ORDER BY checked_at DESC
        LIMIT 1
    """

    with connection.cursor() as cur:
        cur.execute(query, (item_code,))
        row = cur.fetchone()

    return row[0] if row else None


def save_product_history(
    connection,
    keyword,
    item_code,
    product_name,
    price,
    product_url,
):
    query = """
        INSERT INTO product_history
            (keyword, item_code, product_name, price, product_url)
        VALUES (%s, %s, %s, %s, %s)
    """

    with connection.cursor() as cur:
        cur.execute(
            query,
            (keyword, item_code, product_name, price, product_url),
        )
