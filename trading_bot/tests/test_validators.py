import pytest
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_quantity,
    validate_price,
)


class TestValidateSymbol:
    def test_uppercase_passthrough(self):
        assert validate_symbol("BTCUSDT") == "BTCUSDT"

    def test_lowercase_converted(self):
        assert validate_symbol("btcusdt") == "BTCUSDT"

    def test_mixed_case_converted(self):
        assert validate_symbol("EthUsdt") == "ETHUSDT"

    def test_symbol_with_numbers(self):
        assert validate_symbol("1000PEPEUSDT") == "1000PEPEUSDT"

    def test_too_short(self):
        with pytest.raises(ValueError, match="Invalid symbol"):
            validate_symbol("BTC")

    def test_too_long(self):
        with pytest.raises(ValueError):
            validate_symbol("A" * 21)

    def test_spaces_rejected(self):
        with pytest.raises(ValueError):
            validate_symbol("BTC USDT")

    def test_special_chars_rejected(self):
        with pytest.raises(ValueError):
            validate_symbol("BTC-USDT")


class TestValidateSide:
    def test_buy_uppercase(self):
        assert validate_side("BUY") == "BUY"

    def test_sell_lowercase(self):
        assert validate_side("sell") == "SELL"

    def test_invalid(self):
        with pytest.raises(ValueError, match="Must be BUY or SELL"):
            validate_side("HOLD")

    def test_empty(self):
        with pytest.raises(ValueError):
            validate_side("")


class TestValidateQuantity:
    def test_string_float(self):
        assert validate_quantity("0.001") == 0.001

    def test_int(self):
        assert validate_quantity(1) == 1.0

    def test_zero_rejected(self):
        with pytest.raises(ValueError, match="positive"):
            validate_quantity("0")

    def test_negative_rejected(self):
        with pytest.raises(ValueError, match="positive"):
            validate_quantity("-5")

    def test_non_numeric_rejected(self):
        with pytest.raises(ValueError, match="positive number"):
            validate_quantity("abc")


class TestValidatePrice:
    def test_valid_price(self):
        assert validate_price("60000") == 60000.0

    def test_float_string(self):
        assert validate_price("3500.50") == 3500.50

    def test_none_optional(self):
        assert validate_price(None, required=False) is None

    def test_none_required_raises(self):
        with pytest.raises(ValueError, match="required"):
            validate_price(None, required=True)

    def test_zero_rejected(self):
        with pytest.raises(ValueError, match="positive"):
            validate_price("0")

    def test_negative_rejected(self):
        with pytest.raises(ValueError, match="positive"):
            validate_price("-100")

    def test_non_numeric_rejected(self):
        with pytest.raises(ValueError, match="positive number"):
            validate_price("free")
