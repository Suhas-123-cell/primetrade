import logging

from bot.client import BinanceFuturesClient

logger = logging.getLogger(__name__)


def place_market_order(
    client: BinanceFuturesClient, symbol: str, side: str, quantity: float
) -> dict:
    logger.info(
        "Placing MARKET order | symbol=%s side=%s quantity=%s", symbol, side, quantity
    )
    result = client.place_order(
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=quantity,
    )
    logger.info(
        "MARKET order accepted | orderId=%s status=%s executedQty=%s avgPrice=%s",
        result.get("orderId"),
        result.get("status"),
        result.get("executedQty"),
        result.get("avgPrice"),
    )
    return result


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
) -> dict:
    logger.info(
        "Placing LIMIT order | symbol=%s side=%s quantity=%s price=%s",
        symbol,
        side,
        quantity,
        price,
    )
    result = client.place_order(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce="GTC",
    )
    logger.info(
        "LIMIT order accepted | orderId=%s status=%s",
        result.get("orderId"),
        result.get("status"),
    )
    return result


def place_stop_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
) -> dict:
    logger.info(
        "Placing STOP-LIMIT order | symbol=%s side=%s quantity=%s price=%s stopPrice=%s",
        symbol,
        side,
        quantity,
        price,
        stop_price,
    )
    result = client.place_order(
        symbol=symbol,
        side=side,
        type="STOP",
        quantity=quantity,
        price=price,
        stopPrice=stop_price,
        timeInForce="GTC",
    )
    logger.info(
        "STOP-LIMIT order accepted | orderId=%s status=%s",
        result.get("orderId"),
        result.get("status"),
    )
    return result
