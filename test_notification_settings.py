import unittest
from unittest.mock import patch

import pandas as pd

from bot import run_search_keywords


class NotificationSettingsTest(unittest.TestCase):
    def test_price_drop_thresholds(self):
        products = pd.DataFrame([{
            "ASIN": "B000DROP001",
            "商品名": "値下げ商品",
            "価格": 4500,
            "商品URL": "https://example.com/product",
            "検索キーワード": "テスト検索",
        }])
        price_down_items = [{
            "商品名": "値下げ商品",
            "商品URL": "https://example.com/product",
            "前回価格": 5000,
            "今回価格": 4500,
            "値下げ額": 500,
        }]
        cases = [
            (300, 5, True),
            (1000, 5, False),
            (300, 20, False),
            (0, 0, True),
        ]

        with patch("bot._search_and_prepare", return_value=(products, 1)), \
                patch("bot._check_price_history", return_value=(
                    pd.DataFrame(columns=products.columns),
                    price_down_items,
                )), \
                patch("bot.save_excel"), \
                patch("bot.send_slack") as mock_send_slack:
            for min_amount, min_percent, should_notify in cases:
                with self.subTest(
                    min_amount=min_amount,
                    min_percent=min_percent,
                ):
                    mock_send_slack.reset_mock()

                    run_search_keywords([
                        "テスト検索"
                    ], {
                        "notify_new_items": True,
                        "notify_price_drops": True,
                        "notify_no_change": False,
                        "min_price_drop_amount": min_amount,
                        "min_price_drop_percent": min_percent,
                    })

                    self.assertEqual(
                        mock_send_slack.called,
                        should_notify,
                    )


if __name__ == "__main__":
    unittest.main()
