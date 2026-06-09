import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}


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


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be positive, got {qty}.")
    return qty


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
