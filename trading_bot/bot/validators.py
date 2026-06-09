import re

VALID_SIDES = {"BUY", "SELL"}


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not re.match(r"^[A-Z0-9]{4,20}$", symbol):
        raise ValueError(
            f"Invalid symbol '{symbol}'. Must be 4-20 alphanumeric characters (e.g. BTCUSDT)."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be BUY or SELL.")
    return side


def validate_quantity(quantity: str | float | int) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be positive, got {qty}.")
    return qty


def validate_stop_limit_prices(side: str, price: float, stop_price: float) -> None:
    if side == "SELL" and not stop_price > price:
        raise ValueError(
            f"For SELL stop-limit, stop price ({stop_price}) must be above limit price ({price})."
        )
    if side == "BUY" and not stop_price < price:
        raise ValueError(
            f"For BUY stop-limit, stop price ({stop_price}) must be below limit price ({price})."
        )


def validate_price(price, required: bool = True) -> float | None:
    if price is None:
        if required:
            raise ValueError("Price is required for LIMIT and STOP_LIMIT orders.")
        return None
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValueError(f"Price must be positive, got {p}.")
    return p
