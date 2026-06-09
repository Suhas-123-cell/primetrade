from unittest.mock import MagicMock, patch
import pytest
from bot.orders import place_market_order, place_limit_order, place_stop_limit_order


def make_client(response: dict) -> MagicMock:
    client = MagicMock()
    client.place_order.return_value = response
    return client


class TestPlaceMarketOrder:
    def test_calls_correct_params(self):
        client = make_client({"orderId": 1, "status": "FILLED", "executedQty": "0.001", "avgPrice": "67000"})
        result = place_market_order(client, "BTCUSDT", "BUY", 0.001)
        client.place_order.assert_called_once_with(
            symbol="BTCUSDT", side="BUY", type="MARKET", quantity=0.001
        )
        assert result["orderId"] == 1

    def test_returns_response(self):
        resp = {"orderId": 99, "status": "FILLED", "executedQty": "1.0", "avgPrice": "3500"}
        client = make_client(resp)
        result = place_market_order(client, "ETHUSDT", "SELL", 1.0)
        assert result == resp

    def test_propagates_api_error(self):
        client = MagicMock()
        client.place_order.side_effect = Exception("API error")
        with pytest.raises(Exception, match="API error"):
            place_market_order(client, "BTCUSDT", "BUY", 0.001)


class TestPlaceLimitOrder:
    def test_calls_correct_params(self):
        client = make_client({"orderId": 2, "status": "NEW"})
        place_limit_order(client, "BTCUSDT", "BUY", 0.001, 60000.0)
        client.place_order.assert_called_once_with(
            symbol="BTCUSDT",
            side="BUY",
            type="LIMIT",
            quantity=0.001,
            price=60000.0,
            timeInForce="GTC",
        )

    def test_gtc_time_in_force(self):
        client = make_client({"orderId": 3, "status": "NEW"})
        place_limit_order(client, "ETHUSDT", "SELL", 0.1, 3500.0)
        call_kwargs = client.place_order.call_args.kwargs
        assert call_kwargs["timeInForce"] == "GTC"


class TestPlaceStopLimitOrder:
    def test_calls_correct_params(self):
        client = make_client({"orderId": 4, "status": "NEW"})
        place_stop_limit_order(client, "BTCUSDT", "SELL", 0.001, 58000.0, 58500.0)
        client.place_order.assert_called_once_with(
            symbol="BTCUSDT",
            side="SELL",
            type="STOP",
            quantity=0.001,
            price=58000.0,
            stopPrice=58500.0,
            timeInForce="GTC",
        )

    def test_returns_response(self):
        resp = {"orderId": 5, "status": "NEW"}
        client = make_client(resp)
        result = place_stop_limit_order(client, "BTCUSDT", "SELL", 0.001, 58000.0, 58500.0)
        assert result == resp
