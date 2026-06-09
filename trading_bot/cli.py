#!/usr/bin/env python3
import os
import sys

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bot import orders
from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.validators import validate_price, validate_quantity, validate_side, validate_symbol, validate_stop_limit_prices

load_dotenv()

console = Console()
err_console = Console(stderr=True)


def _side_color(side: str) -> str:
    return "green" if side.upper() == "BUY" else "red"


def _status_color(status: str) -> str:
    return {"FILLED": "green", "NEW": "yellow", "PARTIALLY_FILLED": "yellow"}.get(
        status.upper(), "white"
    )


def _get_client() -> BinanceFuturesClient:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        _print_error(
            "Missing Credentials",
            "BINANCE_API_KEY and BINANCE_API_SECRET must be set in your .env file.",
        )
        sys.exit(1)
    return BinanceFuturesClient(api_key, api_secret)


def _print_error(label: str, message: str) -> None:
    error_text = Text()
    error_text.append(f"{label}\n", style="bold red")
    error_text.append(str(message), style="white")
    err_console.print(
        Panel(
            error_text,
            title="[bold red]error[/bold red]",
            title_align="left",
            border_style="red",
            padding=(0, 1),
        )
    )


def _print_order_request(
    order_type: str,
    symbol: str,
    side: str,
    quantity: float,
    price: float | None = None,
    stop_price: float | None = None,
) -> None:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="dim", justify="right")
    table.add_column(style="bold white")

    table.add_row("type", order_type)
    table.add_row("symbol", symbol)
    table.add_row("side", Text(side, style=f"bold {_side_color(side)}"))
    table.add_row("quantity", str(quantity))
    if price is not None:
        table.add_row("price", f"{price:,.4f}")
    if stop_price is not None:
        table.add_row("stop price", f"{stop_price:,.4f}")

    console.print(
        Panel(
            table,
            title="[dim]order request[/dim]",
            title_align="left",
            border_style="bright_black",
            padding=(0, 1),
        )
    )


def _print_order_result(result: dict) -> None:
    side = result.get("side", "")
    status = result.get("status", "")

    table = Table.grid(padding=(0, 2))
    table.add_column(style="dim", justify="right")
    table.add_column(style="bold white")

    table.add_row("order id", str(result.get("orderId", "N/A")))
    table.add_row("symbol", result.get("symbol", "N/A"))
    table.add_row("side", Text(side, style=f"bold {_side_color(side)}"))
    table.add_row("type", result.get("type", "N/A"))
    table.add_row("status", Text(status, style=f"bold {_status_color(status)}"))
    table.add_row("quantity", str(result.get("origQty", "N/A")))
    table.add_row("executed", str(result.get("executedQty", "N/A")))

    try:
        avg = result.get("avgPrice")
        if avg and float(avg) > 0:
            table.add_row("avg price", f"{float(avg):,.4f}")
    except (TypeError, ValueError):
        pass

    try:
        price = result.get("price")
        if price and float(price) > 0:
            table.add_row("limit price", f"{float(price):,.4f}")
    except (TypeError, ValueError):
        pass

    try:
        stop = result.get("stopPrice")
        if stop and float(stop) > 0:
            table.add_row("stop price", f"{float(stop):,.4f}")
    except (TypeError, ValueError):
        pass

    console.print(
        Panel(
            table,
            title="[bold green]order placed[/bold green]",
            title_align="left",
            border_style="green",
            padding=(0, 1),
        )
    )


@click.group()
@click.option("--log-dir", default="logs", show_default=True, help="Log output directory.")
@click.pass_context
def cli(ctx: click.Context, log_dir: str) -> None:
    """Binance Futures Testnet — market  limit  stop-limit  account"""
    ctx.ensure_object(dict)
    log_file = setup_logging(log_dir)
    ctx.obj["log_file"] = log_file

    header = Text()
    header.append("Binance Futures", style="bold white")
    header.append("  /  Testnet", style="dim white")
    header.append("\nLogging to: ", style="dim")
    header.append(log_file, style="dim cyan")

    console.print(
        Panel(
            header,
            title="[bold]primetrade[/bold]",
            title_align="left",
            subtitle="[dim]market  limit  stop-limit  account[/dim]",
            subtitle_align="right",
            border_style="bright_black",
            padding=(0, 1),
        )
    )


@cli.command()
@click.option("--symbol", "-s", required=True, help="Trading pair, e.g. BTCUSDT")
@click.option("--side", required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order side")
@click.option("--quantity", "-q", required=True, help="Order quantity")
def market(symbol: str, side: str, quantity: str) -> None:
    """Place a MARKET order."""
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        qty = validate_quantity(quantity)
    except ValueError as exc:
        _print_error("Validation Error", str(exc))
        sys.exit(1)

    _print_order_request("MARKET", symbol, side, qty)
    client = _get_client()
    try:
        result = orders.place_market_order(client, symbol, side, qty)
        _print_order_result(result)
    except Exception as exc:
        _print_error("Order Failed", str(exc))
        sys.exit(1)


@cli.command()
@click.option("--symbol", "-s", required=True, help="Trading pair, e.g. BTCUSDT")
@click.option("--side", required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order side")
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
        _print_error("Validation Error", str(exc))
        sys.exit(1)

    _print_order_request("LIMIT", symbol, side, qty, price=px)
    client = _get_client()
    try:
        result = orders.place_limit_order(client, symbol, side, qty, px)
        _print_order_result(result)
    except Exception as exc:
        _print_error("Order Failed", str(exc))
        sys.exit(1)


@cli.command("stop-limit")
@click.option("--symbol", "-s", required=True, help="Trading pair, e.g. BTCUSDT")
@click.option("--side", required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order side")
@click.option("--quantity", "-q", required=True, help="Order quantity")
@click.option("--price", "-p", required=True, help="Limit price")
@click.option("--stop-price", required=True, help="Stop trigger price")
def stop_limit(symbol: str, side: str, quantity: str, price: str, stop_price: str) -> None:
    """Place a STOP-LIMIT order."""
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        qty = validate_quantity(quantity)
        px = validate_price(price, required=True)
        sp = validate_price(stop_price, required=True)
        validate_stop_limit_prices(side, px, sp)
    except ValueError as exc:
        _print_error("Validation Error", str(exc))
        sys.exit(1)

    _print_order_request("STOP LIMIT", symbol, side, qty, price=px, stop_price=sp)
    client = _get_client()
    try:
        result = orders.place_stop_limit_order(client, symbol, side, qty, px, sp)
        _print_order_result(result)
    except Exception as exc:
        _print_error("Order Failed", str(exc))
        sys.exit(1)


@cli.command()
def account() -> None:
    """Show account balance from Binance Futures Testnet."""
    client = _get_client()
    try:
        data = client.get_account()
        total = data.get("totalWalletBalance", "N/A")
        available = data.get("availableBalance", "N/A")
        upnl = data.get("totalUnrealizedProfit", "N/A")

        try:
            upnl_val = float(upnl)
            if upnl_val > 0:
                upnl_display = Text(f"{upnl_val:+.4f} USDT", style="bold green")
            elif upnl_val < 0:
                upnl_display = Text(f"{upnl_val:+.4f} USDT", style="bold red")
            else:
                upnl_display = Text(f"{upnl_val:.4f} USDT", style="dim white")
        except (TypeError, ValueError):
            upnl_display = Text(str(upnl), style="white")

        table = Table.grid(padding=(0, 2))
        table.add_column(style="dim", justify="right")
        table.add_column(style="bold white")

        table.add_row("total balance", f"{total} USDT")
        table.add_row("available", f"{available} USDT")
        table.add_row("unrealized pnl", upnl_display)

        console.print(
            Panel(
                table,
                title="[dim]account / testnet[/dim]",
                title_align="left",
                border_style="bright_black",
                padding=(0, 1),
            )
        )
    except Exception as exc:
        _print_error("API Error", str(exc))
        sys.exit(1)


if __name__ == "__main__":
    cli()
