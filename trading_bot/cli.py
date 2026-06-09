#!/usr/bin/env python3
import os
import sys

import click
from dotenv import load_dotenv

from bot import orders
from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.validators import validate_price, validate_quantity, validate_side, validate_symbol

load_dotenv()


def _get_client() -> BinanceFuturesClient:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        click.echo(
            "[ERROR] BINANCE_API_KEY and BINANCE_API_SECRET must be set in your .env file or environment.",
            err=True,
        )
        sys.exit(1)
    return BinanceFuturesClient(api_key, api_secret)


def _print_order_result(result: dict) -> None:
    click.echo("\n" + "=" * 54)
    click.echo("  ORDER PLACED SUCCESSFULLY")
    click.echo("=" * 54)
    click.echo(f"  Order ID    : {result.get('orderId', 'N/A')}")
    click.echo(f"  Symbol      : {result.get('symbol', 'N/A')}")
    click.echo(f"  Side        : {result.get('side', 'N/A')}")
    click.echo(f"  Type        : {result.get('type', 'N/A')}")
    click.echo(f"  Status      : {result.get('status', 'N/A')}")
    click.echo(f"  Quantity    : {result.get('origQty', 'N/A')}")
    click.echo(f"  Executed    : {result.get('executedQty', 'N/A')}")
    avg = result.get("avgPrice")
    if avg and float(avg) > 0:
        click.echo(f"  Avg Price   : {avg}")
    price = result.get("price")
    if price and float(price) > 0:
        click.echo(f"  Limit Price : {price}")
    stop = result.get("stopPrice")
    if stop and float(stop) > 0:
        click.echo(f"  Stop Price  : {stop}")
    click.echo("=" * 54 + "\n")


@click.group()
@click.option("--log-dir", default="logs", show_default=True, help="Log output directory.")
@click.pass_context
def cli(ctx: click.Context, log_dir: str) -> None:
    """Binance Futures Testnet Trading Bot — place orders from the command line."""
    ctx.ensure_object(dict)
    log_file = setup_logging(log_dir)
    ctx.obj["log_file"] = log_file
    click.echo(f"Logging -> {log_file}")


@cli.command()
@click.option("--symbol", "-s", required=True, help="Trading pair, e.g. BTCUSDT")
@click.option(
    "--side",
    required=True,
    type=click.Choice(["BUY", "SELL"], case_sensitive=False),
    help="Order side",
)
@click.option("--quantity", "-q", required=True, help="Order quantity")
def market(symbol: str, side: str, quantity: str) -> None:
    """Place a MARKET order."""
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        qty = validate_quantity(quantity)
    except ValueError as exc:
        click.echo(f"[VALIDATION ERROR] {exc}", err=True)
        sys.exit(1)

    click.echo(f"\nRequest -> symbol={symbol} side={side} type=MARKET quantity={qty}")
    client = _get_client()
    try:
        result = orders.place_market_order(client, symbol, side, qty)
        _print_order_result(result)
    except Exception as exc:
        click.echo(f"\n[ORDER FAILED] {exc}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--symbol", "-s", required=True, help="Trading pair, e.g. BTCUSDT")
@click.option(
    "--side",
    required=True,
    type=click.Choice(["BUY", "SELL"], case_sensitive=False),
    help="Order side",
)
@click.option("--quantity", "-q", required=True, help="Order quantity")
@click.option("--price", "-p", required=True, help="Limit price")
def limit(symbol: str, side: str, quantity: str, price: str) -> None:
    """Place a LIMIT order (GTC)."""
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        qty = validate_quantity(quantity)
        px = validate_price(price, required=True)
    except ValueError as exc:
        click.echo(f"[VALIDATION ERROR] {exc}", err=True)
        sys.exit(1)

    click.echo(
        f"\nRequest -> symbol={symbol} side={side} type=LIMIT quantity={qty} price={px}"
    )
    client = _get_client()
    try:
        result = orders.place_limit_order(client, symbol, side, qty, px)
        _print_order_result(result)
    except Exception as exc:
        click.echo(f"\n[ORDER FAILED] {exc}", err=True)
        sys.exit(1)


@cli.command("stop-limit")
@click.option("--symbol", "-s", required=True, help="Trading pair, e.g. BTCUSDT")
@click.option(
    "--side",
    required=True,
    type=click.Choice(["BUY", "SELL"], case_sensitive=False),
    help="Order side",
)
@click.option("--quantity", "-q", required=True, help="Order quantity")
@click.option("--price", "-p", required=True, help="Limit price")
@click.option("--stop-price", required=True, help="Stop trigger price")
def stop_limit(
    symbol: str, side: str, quantity: str, price: str, stop_price: str
) -> None:
    """Place a STOP-LIMIT order (bonus order type)."""
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        qty = validate_quantity(quantity)
        px = validate_price(price, required=True)
        sp = validate_price(stop_price, required=True)
    except ValueError as exc:
        click.echo(f"[VALIDATION ERROR] {exc}", err=True)
        sys.exit(1)

    click.echo(
        f"\nRequest -> symbol={symbol} side={side} type=STOP-LIMIT "
        f"quantity={qty} price={px} stopPrice={sp}"
    )
    client = _get_client()
    try:
        result = orders.place_stop_limit_order(client, symbol, side, qty, px, sp)
        _print_order_result(result)
    except Exception as exc:
        click.echo(f"\n[ORDER FAILED] {exc}", err=True)
        sys.exit(1)


@cli.command()
def account() -> None:
    """Show account balance from Binance Futures Testnet."""
    client = _get_client()
    try:
        data = client.get_account()
        click.echo("\nAccount Info (Testnet)")
        click.echo(f"  Total Balance  : {data.get('totalWalletBalance', 'N/A')} USDT")
        click.echo(f"  Available      : {data.get('availableBalance', 'N/A')} USDT")
        click.echo(f"  Unrealized PnL : {data.get('totalUnrealizedProfit', 'N/A')} USDT\n")
    except Exception as exc:
        click.echo(f"\n[ERROR] {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
