import unittest
from unittest.mock import ANY, patch

import pandas as pd

from bot import _check_price_history


class CheckPriceHistoryTest(unittest.TestCase):
	@patch("bot.save_product_history")
	@patch("bot.get_latest_price", return_value=5980)
	def test_detects_price_drop(self, mock_get_latest_price, mock_save_product_history):
		products = pd.DataFrame([{
			"ASIN": "B000TEST01",
			"商品名": "テスト商品",
			"価格": 5000,
			"商品URL": "https://example.com/product",
		}])

		new_df, price_down_items = _check_price_history(products, "テスト検索")

		self.assertTrue(new_df.empty)
		self.assertEqual(price_down_items, [{
			"商品名": "テスト商品",
			"商品URL": "https://example.com/product",
			"前回価格": 5980,
			"今回価格": 5000,
			"値下げ額": 980,
		}])
		mock_get_latest_price.assert_called_once_with(
			ANY, "B000TEST01"
		)
		mock_save_product_history.assert_called_once_with(
			ANY,
			"テスト検索",
			"B000TEST01",
			"テスト商品",
			5000,
			"https://example.com/product",
		)

	@patch("bot.save_product_history")
	@patch("bot.get_latest_price", return_value=None)
	def test_detects_new_product(self, mock_get_latest_price, mock_save_product_history):
		products = pd.DataFrame([{
			"ASIN": "B000NEW001",
			"商品名": "新商品",
			"価格": 5000,
			"商品URL": "https://example.com/new-product",
		}])

		new_df, price_down_items = _check_price_history(products, "新商品検索")

		self.assertEqual(len(new_df), 1)
		self.assertEqual(new_df.iloc[0].to_dict(), products.iloc[0].to_dict())
		self.assertEqual(price_down_items, [])
		mock_get_latest_price.assert_called_once_with(
			ANY, "B000NEW001"
		)
		mock_save_product_history.assert_called_once_with(
			ANY,
			"新商品検索",
			"B000NEW001",
			"新商品",
			5000,
			"https://example.com/new-product",
		)


if __name__ == "__main__":
	unittest.main()
