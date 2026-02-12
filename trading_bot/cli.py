#!/usr/bin/env python3
"""
Binance Futures Trading Bot - CLI Entry Point

A command-line interface for placing orders on Binance Futures Testnet
"""

import argparse
import os
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.client import BinanceFuturesClient, BinanceAPIError, BinanceNetworkError
from bot.orders import OrderManager
from bot.validators import OrderValidator
from bot.logging_config import setup_logging
from bot.interactive import run_interactive_mode
from bot.market_data import MarketDataManager, format_price_table, format_24h_table


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description='Binance Futures Testnet Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run interactive mode
  python cli.py --interactive --api-key KEY --api-secret SECRET
  
  # Test API connection
  python cli.py --test-connection --api-key KEY --api-secret SECRET
  
  # Place orders
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
  python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 \
                --price 66000 --stop-price 65500
  
  # Market data
  python cli.py --symbol BTCUSDT --get-price
  python cli.py --symbol BTCUSDT --ticker
  python cli.py --symbol BTCUSDT --order-book
  python cli.py --top-gainers
  python cli.py --high-volume
  
  # Account & Orders
  python cli.py --account
  python cli.py --list-orders
  python cli.py --list-orders --symbol BTCUSDT
  python cli.py --cancel-order 123456 --symbol BTCUSDT
  python cli.py --cancel-all --symbol BTCUSDT
        """
    )
    
    # API credentials (can also use environment variables)
    parser.add_argument(
        '--api-key',
        type=str,
        default=os.getenv('BINANCE_API_KEY'),
        help='Binance API Key (or set BINANCE_API_KEY env var)'
    )
    parser.add_argument(
        '--api-secret',
        type=str,
        default=os.getenv('BINANCE_API_SECRET'),
        help='Binance API Secret (or set BINANCE_API_SECRET env var)'
    )
    
    # Order parameters
    parser.add_argument(
        '--symbol',
        '-s',
        type=str,
        help='Trading symbol (e.g., BTCUSDT, ETHUSDT)'
    )
    parser.add_argument(
        '--side',
        type=str,
        choices=['BUY', 'SELL', 'buy', 'sell'],
        help='Order side: BUY or SELL'
    )
    parser.add_argument(
        '--type',
        '-t',
        dest='order_type',
        type=str,
        choices=['MARKET', 'LIMIT', 'STOP_LIMIT', 'market', 'limit', 'stop_limit'],
        help='Order type: MARKET, LIMIT, or STOP_LIMIT'
    )
    parser.add_argument(
        '--quantity',
        '-q',
        type=str,
        help='Order quantity (e.g., 0.01)'
    )
    parser.add_argument(
        '--price',
        '-p',
        type=str,
        help='Limit price (required for LIMIT and STOP_LIMIT orders)'
    )
    parser.add_argument(
        '--stop-price',
        type=str,
        help='Stop trigger price (required for STOP_LIMIT orders)'
    )
    parser.add_argument(
        '--time-in-force',
        type=str,
        default='GTC',
        choices=['GTC', 'IOC', 'FOK'],
        help='Time in force (default: GTC). Only for LIMIT orders.'
    )
    
    # Market Data
    parser.add_argument(
        '--get-price',
        action='store_true',
        help='Get current price for symbol'
    )
    parser.add_argument(
        '--ticker',
        action='store_true',
        help='Get 24h ticker statistics for symbol'
    )
    parser.add_argument(
        '--order-book',
        action='store_true',
        help='Get order book for symbol'
    )
    parser.add_argument(
        '--depth',
        type=int,
        default=10,
        help='Order book depth (default: 10)'
    )
    parser.add_argument(
        '--top-gainers',
        action='store_true',
        help='Show top gaining symbols (24h)'
    )
    parser.add_argument(
        '--top-losers',
        action='store_true',
        help='Show top losing symbols (24h)'
    )
    parser.add_argument(
        '--high-volume',
        action='store_true',
        help='Show high volume symbols (24h)'
    )
    
    # Order Management
    parser.add_argument(
        '--list-orders',
        action='store_true',
        help='List open orders'
    )
    parser.add_argument(
        '--cancel-order',
        type=int,
        help='Cancel specific order by ID'
    )
    parser.add_argument(
        '--cancel-all',
        action='store_true',
        help='Cancel all orders for symbol'
    )
    parser.add_argument(
        '--account',
        action='store_true',
        help='Show account information'
    )
    
    # Mode options
    parser.add_argument(
        '--interactive',
        '-i',
        action='store_true',
        help='Run in interactive menu mode'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate inputs without placing order'
    )
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Test API connection and exit'
    )
    
    return parser


def print_order_summary(args) -> None:
    """Print a summary of the order request"""
    print("\n" + "=" * 50)
    print("ORDER REQUEST SUMMARY")
    print("=" * 50)
    print(f"Symbol:        {args.symbol.upper()}")
    print(f"Side:          {args.side.upper()}")
    print(f"Order Type:    {args.order_type.upper()}")
    print(f"Quantity:      {args.quantity}")
    if args.price:
        print(f"Price:         {args.price}")
    if args.stop_price:
        print(f"Stop Price:    {args.stop_price}")
    if args.order_type.upper() in ['LIMIT', 'STOP_LIMIT']:
        print(f"Time In Force: {args.time_in_force}")
    print("=" * 50 + "\n")


def handle_market_data(args, client):
    """Handle market data commands"""
    market_manager = MarketDataManager(client)
    
    if args.get_price:
        if args.symbol:
            price = market_manager.get_price(args.symbol)
            if price:
                print(f"\n{price.symbol}: {price.price:,.2f} USDT\n")
            else:
                print(f"Could not fetch price for {args.symbol}")
        else:
            prices = market_manager.get_all_prices()
            print(format_price_table(prices))
        return True
    
    if args.ticker:
        if args.symbol:
            stats = market_manager.get_24h_stats(args.symbol)
            if stats:
                print(stats.format_summary())
            else:
                print(f"Could not fetch stats for {args.symbol}")
        else:
            stats = market_manager.get_all_24h_stats()
            print(format_24h_table(stats))
        return True
    
    if args.order_book:
        if not args.symbol:
            print("Error: --symbol is required for order book")
            sys.exit(1)
        order_book = market_manager.get_order_book(args.symbol, limit=100)
        if order_book:
            print(order_book.format_summary(depth=args.depth))
        else:
            print(f"Could not fetch order book for {args.symbol}")
        return True
    
    if args.top_gainers:
        gainers = market_manager.get_top_gainers(limit=15)
        print(format_24h_table(gainers, "Top Gainers (24h)"))
        return True
    
    if args.top_losers:
        losers = market_manager.get_top_losers(limit=15)
        print(format_24h_table(losers, "Top Losers (24h)"))
        return True
    
    if args.high_volume:
        high_vol = market_manager.get_high_volume_symbols(limit=15)
        print(format_24h_table(high_vol, "High Volume Symbols (24h)"))
        return True
    
    return False


def handle_order_management(args, client):
    """Handle order management commands"""
    
    if args.account:
        account_info = client.get_account_info()
        print("\n" + "="*60)
        print("ACCOUNT INFORMATION")
        print("="*60)
        print(f"Can Trade: {account_info.get('canTrade', False)}")
        print(f"Can Withdraw: {account_info.get('canWithdraw', False)}")
        print(f"Can Deposit: {account_info.get('canDeposit', False)}")
        
        assets = account_info.get('assets', [])
        if assets:
            print("\nBalances:")
            for asset in assets:
                wallet = float(asset.get('walletBalance', 0))
                available = float(asset.get('availableBalance', 0))
                if wallet != 0 or available != 0:
                    print(f"  {asset.get('asset')}: {wallet:.8f} (Available: {available:.8f})")
        
        positions = [p for p in account_info.get('positions', []) if float(p.get('positionAmt', 0)) != 0]
        if positions:
            print("\nOpen Positions:")
            for pos in positions:
                amt = float(pos.get('positionAmt', 0))
                side = 'LONG' if amt > 0 else 'SHORT'
                print(f"  {pos.get('symbol')}: {side} {abs(amt):.4f} @ {float(pos.get('entryPrice', 0)):.2f}")
        print("="*60 + "\n")
        return True
    
    if args.list_orders:
        orders = client.get_open_orders(args.symbol if args.symbol else None)
        if orders:
            print(f"\n{'Order ID':<15} {'Symbol':<12} {'Side':<6} {'Type':<12} {'Price':>12} {'Qty':>10} {'Status':<10}")
            print("-" * 90)
            for order in orders:
                price = float(order.get('price', 0))
                price_str = f"{price:.2f}" if price > 0 else "MARKET"
                print(f"{order.get('orderId', 0):<15} {order.get('symbol', ''):<12} "
                      f"{order.get('side', ''):<6} {order.get('type', ''):<12} "
                      f"{price_str:>12} {float(order.get('origQty', 0)):>10.4f} "
                      f"{order.get('status', ''):<10}")
        else:
            print("No open orders found")
        return True
    
    if args.cancel_order:
        if not args.symbol:
            print("Error: --symbol is required when cancelling an order")
            sys.exit(1)
        result = client.cancel_order(args.symbol, args.cancel_order)
        print(f"\nOrder cancelled successfully!")
        print(f"  Order ID: {result.get('orderId')}")
        print(f"  Symbol: {result.get('symbol')}")
        print(f"  Status: {result.get('status')}")
        return True
    
    if args.cancel_all:
        if not args.symbol:
            print("Error: --symbol is required when cancelling all orders")
            sys.exit(1)
        orders = client.get_open_orders(args.symbol)
        if orders:
            for order in orders:
                client.cancel_order(args.symbol, order.get('orderId'))
            print(f"\nCancelled {len(orders)} order(s) for {args.symbol}")
        else:
            print(f"No open orders for {args.symbol}")
        return True
    
    return False


def handle_order_placement(args, client):
    """Handle order placement"""
    # Validate inputs
    is_valid, errors = OrderValidator.validate_order_request(
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
        stop_price=args.stop_price,
        time_in_force=args.time_in_force
    )
    
    if not is_valid:
        print("Validation Errors:")
        for error in errors:
            print(f"  ✗ {error}")
        sys.exit(1)
    
    # Print order summary
    print_order_summary(args)
    
    # Dry run - just validate and exit
    if args.dry_run:
        print("✓ Dry run mode - inputs validated successfully")
        print("  Order would be placed with the above parameters")
        sys.exit(0)
    
    # Confirm order placement
    if args.order_type.upper() == 'MARKET':
        confirm = input("Place this MARKET order? This will execute immediately at market price. (y/N): ")
    else:
        confirm = input("Place this order? (y/N): ")
    
    if confirm.lower() not in ['y', 'yes']:
        print("Order cancelled by user")
        sys.exit(0)
    
    # Place the order
    order_manager = OrderManager(client)
    
    if args.order_type.upper() == 'MARKET':
        result = order_manager.place_market_order(
            symbol=args.symbol,
            side=args.side,
            quantity=float(args.quantity)
        )
    elif args.order_type.upper() == 'LIMIT':
        result = order_manager.place_limit_order(
            symbol=args.symbol,
            side=args.side,
            quantity=float(args.quantity),
            price=float(args.price),
            time_in_force=args.time_in_force
        )
    elif args.order_type.upper() == 'STOP_LIMIT':
        result = order_manager.place_stop_limit_order(
            symbol=args.symbol,
            side=args.side,
            quantity=float(args.quantity),
            price=float(args.price),
            stop_price=float(args.stop_price),
            time_in_force=args.time_in_force
        )
    else:
        print(f"Error: Unsupported order type: {args.order_type}")
        sys.exit(1)
    
    # Print result
    print(result.format_summary())
    
    return result.success


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Check API credentials first
    if not args.api_key or not args.api_secret:
        print("Error: API credentials required.")
        print("Provide via --api-key and --api-secret arguments")
        print("Or set BINANCE_API_KEY and BINANCE_API_SECRET environment variables")
        sys.exit(1)
    
    # Initialize client
    try:
        client = BinanceFuturesClient(api_key=args.api_key, api_secret=args.api_secret)
    except Exception as e:
        print(f"Error initializing client: {e}")
        sys.exit(1)
    
    # Test connection if requested
    if args.test_connection:
        try:
            account_info = client.get_account_info()
            print("✓ API connection successful!")
            print(f"Account canTrade: {account_info.get('canTrade', False)}")
            sys.exit(0)
        except Exception as e:
            print(f"✗ API connection failed: {e}")
            sys.exit(1)
    
    # Run interactive mode (suppress console logging for cleaner UI)
    if args.interactive:
        setup_logging(log_level=args.log_level, log_to_console=False, log_to_file=True)
        run_interactive_mode(client)
        sys.exit(0)
    
    # Setup logging for non-interactive mode
    setup_logging(log_level=args.log_level, log_to_console=True, log_to_file=True)
    
    # Handle market data commands
    if handle_market_data(args, client):
        sys.exit(0)
    
    # Handle order management commands
    if handle_order_management(args, client):
        sys.exit(0)
    
    # Validate required arguments for order placement
    if not args.symbol:
        print("Error: --symbol is required (use --help for available commands)")
        sys.exit(1)
    if not args.side:
        print("Error: --side is required for placing orders")
        sys.exit(1)
    if not args.order_type:
        print("Error: --type is required for placing orders")
        sys.exit(1)
    if not args.quantity:
        print("Error: --quantity is required for placing orders")
        sys.exit(1)
    
    # Handle order placement
    try:
        success = handle_order_placement(args, client)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
