# Binance Futures Testnet Trading Bot

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Binance](https://img.shields.io/badge/Binance-Testnet-F0B90B.svg)](https://testnet.binancefuture.com)

A clean, structured Python application for placing orders on the **Binance Futures Testnet** (USDT-M). Features an interactive menu mode, real-time market data, comprehensive validation, and detailed logging.

## ✨ Features

### Core Trading Features
- 🎯 **Order Types**: MARKET, LIMIT, and STOP-LIMIT orders
- 💰 **Order Sides**: BUY and SELL
- ✅ **Input Validation**: Comprehensive validation with clear error messages
- 📝 **Logging**: Detailed API request/response logging to files
- 🛡️ **Error Handling**: Graceful handling of API errors, network failures, and invalid inputs

### Bonus Features (Beyond Requirements)
- 🖥️ **Interactive Mode**: Beautiful menu-driven interface with colored output
- 📊 **Market Data**: Real-time prices, 24h statistics, order book depth
- 🏆 **Market Analysis**: Top gainers, top losers, high volume symbols
- 👤 **Account Management**: View balances, positions, and order history
- 🔄 **Order Management**: View and cancel open orders

## 📸 Screenshots

### Interactive Menu Mode
<img width="932" height="375" alt="screenshot-2026-02-12_21-58-26" src="https://github.com/user-attachments/assets/8ed64ee7-4bb2-4785-a621-cb957588d7fc" />

*Main menu with colorful, easy-to-navigate interface*

### Market Data Display
<img width="934" height="715" alt="screenshot-2026-02-12_21-59-48" src="https://github.com/user-attachments/assets/a6680e76-a8e6-4510-a51a-f91a265ab758" />


*24h statistics with price changes, volume, and trading activity*

### Order Book

<img width="932" height="656" alt="screenshot-2026-02-12_22-00-50" src="https://github.com/user-attachments/assets/3f29e3ec-9422-4116-ab0b-11ea1bbd41ce" />

*Real-time order book with bids and asks*


## 🏗️ Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance Futures API client wrapper
│   ├── orders.py          # Order placement logic
│   ├── market_data.py     # Market data fetching and formatting
│   ├── interactive.py     # Interactive menu system
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Logging configuration
├── cli.py                 # CLI entry point
├── requirements.txt       # Python dependencies
└── README.md              # Documentation
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd trading_bot
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Credentials

**Option A: Environment Variables (Recommended)**
```bash
export BINANCE_API_KEY="your_api_key_here"
export BINANCE_API_SECRET="your_api_secret_here"
```

**Option B: Command Line**
```bash
python cli.py --api-key "your_key" --api-secret "your_secret" ...
```

> 🔑 **Note**: Get your API credentials from [Binance Futures Testnet](https://testnet.binancefuture.com)

## 📖 Usage Guide

### 🎮 Interactive Mode (Recommended)

Launch the beautiful menu-driven interface:

```bash
python cli.py --interactive
# or
python cli.py -i
```

**Navigation:**
- Use number keys (1-5) to select menu options
- Press `0` to exit or go back
- Follow on-screen prompts for inputs
- All confirmations require explicit "y/yes" input

### 💻 Command Line Usage

#### Test Connection
```bash
python cli.py --test-connection
```

#### Place Orders
```bash
# Market Order (Immediate execution)
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

# Limit Order (Execute at specific price)
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000

# Stop-Limit Order (Trigger + Limit price)
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT \
  --quantity 0.01 --price 66000 --stop-price 65500
```

#### Market Data Commands
```bash
# Current prices
python cli.py --get-price --symbol BTCUSDT

# 24-hour statistics
python cli.py --ticker --symbol BTCUSDT

# Order book (depth: 5-100)
python cli.py --order-book --symbol BTCUSDT --depth 10

# Market leaders
python cli.py --top-gainers
python cli.py --top-losers
python cli.py --high-volume
```

#### Account & Order Management
```bash
# View account info
python cli.py --account

# List open orders
python cli.py --list-orders
python cli.py --list-orders --symbol BTCUSDT

# Cancel orders
python cli.py --cancel-order 123456 --symbol BTCUSDT
python cli.py --cancel-all --symbol BTCUSDT
```

## 🎯 Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `--interactive`, `-i` | Launch interactive menu | `python cli.py -i` |
| `--symbol`, `-s` | Trading pair | `--symbol BTCUSDT` |
| `--side` | BUY or SELL | `--side BUY` |
| `--type`, `-t` | Order type | `--type LIMIT` |
| `--quantity`, `-q` | Order size | `--quantity 0.01` |
| `--price`, `-p` | Limit price | `--price 65000` |
| `--stop-price` | Stop trigger | `--stop-price 64000` |
| `--get-price` | Current price | `--get-price --symbol BTCUSDT` |
| `--ticker` | 24h stats | `--ticker --symbol BTCUSDT` |
| `--order-book` | Order book | `--order-book --symbol BTCUSDT` |
| `--account` | Account info | `--account` |
| `--list-orders` | View orders | `--list-orders` |
| `--cancel-order` | Cancel by ID | `--cancel-order 123 --symbol BTCUSDT` |
| `--cancel-all` | Cancel all | `--cancel-all --symbol BTCUSDT` |
| `--dry-run` | Validate only | Add to any order command |

## ✅ Validation

The bot validates all inputs before API calls:

| Field | Validation Rules |
|-------|------------------|
| **Symbol** | Format: XXXUSDT (e.g., BTCUSDT) |
| **Side** | Must be BUY or SELL |
| **Order Type** | MARKET, LIMIT, or STOP_LIMIT |
| **Quantity** | Positive number (> 0) |
| **Price** | Required for LIMIT, positive number |
| **Stop Price** | Required for STOP_LIMIT, positive number |

Example validation error:
```
Validation Errors:
  ✗ Invalid symbol format: 'BTC'. Expected format like 'BTCUSDT'
  ✗ Quantity must be positive, got: -0.01
```

## 📝 Logging

All operations are logged to:
- **File**: `logs/trading_bot_YYYYMMDD_HHMMSS.log`
- **Console**: INFO level and above (non-interactive mode)

**Log Format:**
```
2024-02-12 19:53:07 - bot.client - INFO - API Request: POST /fapi/v1/order
2024-02-12 19:53:07 - bot.orders - INFO - Order placed successfully: ID=123456
```

**Log Contents:**
- ✅ API requests with parameters
- ✅ API responses
- ⚠️ Validation errors
- ❌ API errors with codes
- 🌐 Network errors
- 🔍 Debug information (DEBUG level)

## 🛡️ Error Handling

The bot gracefully handles:

| Error Type | Handling |
|------------|----------|
| **Validation Errors** | Clear error messages before API call |
| **API Errors** | Display Binance error code and message |
| **Network Errors** | Connection timeout, retry suggestions |
| **Auth Errors** | Invalid API key/secret detection |
| **Margin Errors** | Insufficient balance notifications |

## 📊 Example Output

### Successful Market Order
```
==================================================
ORDER REQUEST SUMMARY
==================================================
Symbol:        BTCUSDT
Side:          BUY
Order Type:    MARKET
Quantity:      0.01
==================================================

Place this MARKET order? (y/N): y

==================================================
ORDER RESULT
==================================================
Status: SUCCESS
Order ID: 123456789
Symbol: BTCUSDT
Side: BUY
Type: MARKET
Status: FILLED
Executed Qty: 0.01
Avg Price: 65234.50
==================================================

✓ Order placed successfully!
```

### Account Information
```
============================================================
ACCOUNT INFORMATION
============================================================
Can Trade: True
Can Withdraw: False
Can Deposit: True

Balances:
  Asset          Wallet Balance          Available
  --------------------------------------------------
  USDT           10000.00000000      8500.00000000
  BTC                0.05000000         0.00000000

Open Positions:
  Symbol       Side         Amount    Entry Price   P&L
  ------------------------------------------------------
  BTCUSDT      LONG         0.0100       64000.00  +123.45
  ETHUSDT      SHORT        0.0500        3500.00   -45.67
============================================================
```

## 🔧 Troubleshooting

### "Margin is insufficient"
- Add testnet USDT from [Binance Testnet](https://testnet.binancefuture.com)
- Check your available balance with `--account`

### "Invalid API key"
- Ensure you're using **testnet** credentials, not production
- Verify the API key is active
- Check environment variables are set correctly

### "Symbol not found"
- Verify symbol format (BTCUSDT, not BTC-USDT)
- Check the symbol is available on testnet
- Use `--get-price` without symbol to see all available pairs

### Connection Issues
```bash
# Test connectivity
python cli.py --test-connection

# Check network
ping testnet.binancefuture.com
```

## 🎓 Learning Resources

- [Binance Futures API Documentation](https://binance-docs.github.io/apidocs/futures/en/)
- [Binance Testnet](https://testnet.binancefuture.com)
- [Futures Trading Guide](https://www.binance.com/en/support/faq/leverage-and-margin-trading-360043074591)

## ⚠️ Important Notes

- 🧪 This bot is for **Binance Futures Testnet ONLY**
- 🔒 Never use production API keys
- 💸 Testnet has fake money - perfect for learning
- 📉 Testnet has different liquidity than mainnet
- 🕒 Orders may not fill immediately on testnet

## 📝 Deliverables

This submission includes:

- ✅ **Source Code**: Clean, modular Python structure
- ✅ **Interactive Mode**: Beautiful menu-driven interface
- ✅ **Market Data**: Prices, 24h stats, order book, top movers
- ✅ **Order Management**: Place, view, and cancel orders
- ✅ **Account Viewer**: Balances and positions
- ✅ **Documentation**: Comprehensive README with examples
- ✅ **Log Files**: Sample logs from MARKET and LIMIT orders
- ✅ **Bonus Features**: STOP-LIMIT orders, interactive UI, market analysis

## 📄 License

MIT License - Feel free to use, modify, and distribute.

## 👨‍💻 Author

Created by Shakib S.

---

**Ready to trade?** Run `python cli.py --interactive` and start exploring! 🚀
