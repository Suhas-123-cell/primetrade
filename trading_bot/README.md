# Binance Futures Testnet Trading Bot

A clean, reusable Python CLI for placing orders on Binance Futures Testnet (USDT-M).  
Supports **Market**, **Limit**, and **Stop-Limit** orders with structured logging and full error handling.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (HMAC signing, request/response logging)
│   ├── orders.py          # Order placement logic (market, limit, stop-limit)
│   ├── validators.py      # Input validation (symbol, side, quantity, price)
│   └── logging_config.py  # Structured logging to file + console
├── cli.py                 # Click CLI entry point
├── logs/                  # Auto-created; log files land here
├── .env.example           # Copy to .env and fill in your API keys
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet API credentials

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with a GitHub account
3. Go to **API Keys** → generate a key pair
4. Copy the API Key and Secret

### 2. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure credentials

```bash
cp .env.example .env
# Edit .env and fill in your BINANCE_API_KEY and BINANCE_API_SECRET
```

---

## Usage

All commands are run from inside the `trading_bot/` directory.

### Place a Market order

```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.001
python cli.py market -s ETHUSDT --side SELL -q 0.05
```

### Place a Limit order

```bash
python cli.py limit --symbol BTCUSDT --side BUY --quantity 0.001 --price 60000
python cli.py limit -s ETHUSDT --side SELL -q 0.1 -p 3500
```

### Place a Stop-Limit order (bonus)

```bash
python cli.py stop-limit --symbol BTCUSDT --side SELL \
    --quantity 0.001 --price 58000 --stop-price 58500
```

### Check account balance

```bash
python cli.py account
```

### Custom log directory

```bash
python cli.py --log-dir /tmp/my_logs market --symbol BTCUSDT --side BUY --quantity 0.001
```

---

## Example output

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

## Validation rules

| Field    | Rule                                      |
|----------|-------------------------------------------|
| symbol   | Uppercase letters only, 4–20 chars        |
| side     | `BUY` or `SELL` (case-insensitive)        |
| quantity | Positive number                           |
| price    | Positive number; required for LIMIT/STOP  |

---

## Assumptions

- All orders use the **USDT-M Futures Testnet** (`https://testnet.binancefuture.com`)
- Limit orders use `timeInForce=GTC` (Good-Till-Cancelled)
- Stop-Limit orders use Binance type `STOP` (limit + stop trigger)
- Credentials are loaded from `.env` file or environment variables
- Log files rotate daily by date suffix (`trading_bot_YYYYMMDD.log`)

---

## Log files

Sample logs from real testnet runs are included in `logs/`:

- `logs/market_order_sample.log` — BUY MARKET order on BTCUSDT, status FILLED
- `logs/limit_order_sample.log`  — SELL LIMIT order on ETHUSDT, status NEW (resting)
