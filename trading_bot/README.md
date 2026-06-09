# Trading Bot — Binance Futures Testnet

Python CLI for placing orders on Binance Futures Testnet (USDT-M). Supports Market, Limit, and Stop-Limit orders with request/response logging and input validation.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── client.py          # REST API wrapper — signs requests, handles HTTP errors
│   ├── orders.py          # order placement functions (market, limit, stop-limit)
│   ├── validators.py      # input validation for symbol, side, quantity, price
│   └── logging_config.py  # configures file + console logging
├── tests/
│   ├── test_validators.py  # 24 unit tests for all validators
│   └── test_orders.py      # 7 tests for order placement logic (mocked client)
├── cli.py                 # CLI entry point (Click)
├── logs/                  # log files written here
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup

**1. Get testnet API credentials**

Go to [testnet.binancefuture.com](https://testnet.binancefuture.com), log in with GitHub, and generate an API key pair.

**2. Install dependencies**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Add credentials**

```bash
cp .env.example .env
```

Edit `.env`:
```
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

---

## Usage

Run all commands from inside `trading_bot/`.

**Market order**
```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.001
python cli.py market -s ETHUSDT --side SELL -q 0.05
```

**Limit order**
```bash
python cli.py limit --symbol BTCUSDT --side BUY --quantity 0.001 --price 60000
python cli.py limit -s ETHUSDT --side SELL -q 0.1 -p 3500
```

**Stop-Limit order**
```bash
python cli.py stop-limit --symbol BTCUSDT --side SELL \
    --quantity 0.001 --price 58000 --stop-price 58500
```

**Account balance**
```bash
python cli.py account
```

**Custom log directory**
```bash
python cli.py --log-dir /tmp/logs market --symbol BTCUSDT --side BUY --quantity 0.001
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

All 31 tests should pass. Tests cover:
- Symbol, side, quantity, and price validation (including edge cases)
- Market, limit, and stop-limit order placement with a mocked client

---

## Output Example

```
Logging -> logs/trading_bot_20260609.log

Request -> symbol=BTCUSDT side=BUY type=MARKET quantity=0.001

======================================================
  ORDER PLACED SUCCESSFULLY
======================================================
  Order ID    : 3824917263
  Symbol      : BTCUSDT
  Side        : BUY
  Type        : MARKET
  Status      : FILLED
  Quantity    : 0.001
  Executed    : 0.001
  Avg Price   : 67432.10
======================================================
```

---

## Validation Rules

| Field      | Rule                                             |
|------------|--------------------------------------------------|
| symbol     | 4-20 alphanumeric characters, uppercase          |
| side       | BUY or SELL (case-insensitive)                   |
| quantity   | positive number                                  |
| price      | positive number; required for LIMIT / STOP-LIMIT |
| stop-price | positive number; required for STOP-LIMIT         |

---

## Logging

Logs go to `logs/trading_bot_YYYYMMDD.log`. Every API request, response, and error is logged. The console shows INFO and above; the file captures DEBUG as well (full request params and raw responses).

Sample logs from testnet runs are in `logs/market_order_sample.log` and `logs/limit_order_sample.log`.

---

## Assumptions

- All requests go to `https://testnet.binancefuture.com` (USDT-M futures testnet)
- Limit and Stop-Limit orders use `timeInForce=GTC`
- Stop-Limit maps to Binance order type `STOP` (limit price + stop trigger)
- Credentials are read from `.env` or environment variables
