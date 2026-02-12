"""
Interactive Menu System
Provides a menu-driven interface for the trading bot
"""

import os
import sys
from typing import Optional, List
from getpass import getpass

from .client import BinanceFuturesClient
from .orders import OrderManager, OrderResult
from .market_data import MarketDataManager, format_price_table, format_24h_table
from .validators import OrderValidator


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print application header"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}      BINANCE FUTURES TESTNET TRADING BOT{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}\n")


def print_menu(title: str, options: List[str]):
    """Print a menu with options"""
    print(f"\n{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.YELLOW}{'-' * len(title)}{Colors.ENDC}")
    for i, option in enumerate(options, 1):
        print(f"  {Colors.GREEN}[{i}]{Colors.ENDC} {option}")
    print(f"  {Colors.RED}[0]{Colors.ENDC} Exit/Back")
    print()


def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default value"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    value = input(prompt).strip()
    return value if value else (default or "")


def get_choice(prompt: str, valid_choices: List[str]) -> str:
    """Get a valid choice from user"""
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print(f"{Colors.RED}Invalid choice. Please enter one of: {', '.join(valid_choices)}{Colors.ENDC}")


def confirm(prompt: str) -> bool:
    """Ask user for confirmation"""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")


class InteractiveMenu:
    """
    Interactive menu system for the trading bot
    """
    
    def __init__(self, client: BinanceFuturesClient):
        """
        Initialize the interactive menu
        
        Args:
            client: Configured BinanceFuturesClient instance
        """
        self.client = client
        self.order_manager = OrderManager(client)
        self.market_manager = MarketDataManager(client)
        self.running = True
    
    def run(self):
        """Run the main menu loop"""
        while self.running:
            clear_screen()
            print_header()
            print_menu("MAIN MENU", [
                "Place Order",
                "View Market Data",
                "View Account Info",
                "View Open Orders",
                "Cancel Orders"
            ])
            
            choice = input("Enter choice: ").strip()
            
            if choice == '1':
                self.place_order_menu()
            elif choice == '2':
                self.market_data_menu()
            elif choice == '3':
                self.account_info_menu()
            elif choice == '4':
                self.view_open_orders_menu()
            elif choice == '5':
                self.cancel_orders_menu()
            elif choice == '0':
                self.running = False
                print(f"\n{Colors.GREEN}Thank you for using Binance Futures Trading Bot!{Colors.ENDC}\n")
            else:
                input(f"{Colors.RED}Invalid choice. Press Enter to continue...{Colors.ENDC}")
    
    def place_order_menu(self):
        """Menu for placing orders"""
        clear_screen()
        print_header()
        print_menu("PLACE ORDER", [
            "Market Order",
            "Limit Order",
            "Stop-Limit Order"
        ])
        
        choice = input("Enter choice: ").strip()
        
        if choice == '0':
            return
        elif choice not in ['1', '2', '3']:
            input(f"{Colors.RED}Invalid choice. Press Enter to continue...{Colors.ENDC}")
            return
        
        # Get common order parameters
        print(f"\n{Colors.BOLD}Order Parameters:{Colors.ENDC}\n")
        
        symbol = get_input("Symbol (e.g., BTCUSDT)")
        if not symbol:
            input("Symbol is required. Press Enter to continue...")
            return
        
        side = get_choice("Side (BUY/SELL): ", ['BUY', 'SELL', 'buy', 'sell']).upper()
        quantity = get_input("Quantity (e.g., 0.01)")
        
        # Validate basic inputs
        is_valid, errors = OrderValidator.validate_order_request(
            symbol=symbol, side=side, order_type='MARKET', quantity=quantity
        )
        
        if not is_valid:
            print(f"\n{Colors.RED}Validation Errors:{Colors.ENDC}")
            for error in errors:
                print(f"  - {error}")
            input("\nPress Enter to continue...")
            return
        
        # Place order based on type
        try:
            if choice == '1':
                # Market Order
                print(f"\n{Colors.YELLOW}Placing MARKET order...{Colors.ENDC}")
                if not confirm(f"Place {side} MARKET order for {quantity} {symbol}?"):
                    print("Order cancelled.")
                    input("Press Enter to continue...")
                    return
                
                result = self.order_manager.place_market_order(symbol, side, float(quantity))
                
            elif choice == '2':
                # Limit Order
                price = get_input("Limit Price")
                time_in_force = get_input("Time in Force (GTC/IOC/FOK)", "GTC")
                
                is_valid, errors = OrderValidator.validate_order_request(
                    symbol=symbol, side=side, order_type='LIMIT', 
                    quantity=quantity, price=price, time_in_force=time_in_force
                )
                
                if not is_valid:
                    print(f"\n{Colors.RED}Validation Errors:{Colors.ENDC}")
                    for error in errors:
                        print(f"  - {error}")
                    input("\nPress Enter to continue...")
                    return
                
                print(f"\n{Colors.YELLOW}Placing LIMIT order...{Colors.ENDC}")
                if not confirm(f"Place {side} LIMIT order for {quantity} {symbol} @ {price}?"):
                    print("Order cancelled.")
                    input("Press Enter to continue...")
                    return
                
                result = self.order_manager.place_limit_order(
                    symbol, side, float(quantity), float(price), time_in_force
                )
                
            elif choice == '3':
                # Stop-Limit Order
                price = get_input("Limit Price")
                stop_price = get_input("Stop Price")
                time_in_force = get_input("Time in Force (GTC/IOC/FOK)", "GTC")
                
                is_valid, errors = OrderValidator.validate_order_request(
                    symbol=symbol, side=side, order_type='STOP_LIMIT',
                    quantity=quantity, price=price, stop_price=stop_price,
                    time_in_force=time_in_force
                )
                
                if not is_valid:
                    print(f"\n{Colors.RED}Validation Errors:{Colors.ENDC}")
                    for error in errors:
                        print(f"  - {error}")
                    input("\nPress Enter to continue...")
                    return
                
                print(f"\n{Colors.YELLOW}Placing STOP-LIMIT order...{Colors.ENDC}")
                if not confirm(f"Place {side} STOP-LIMIT order for {quantity} {symbol} @ {price} (stop: {stop_price})?"):
                    print("Order cancelled.")
                    input("Press Enter to continue...")
                    return
                
                result = self.order_manager.place_stop_limit_order(
                    symbol, side, float(quantity), float(price), 
                    float(stop_price), time_in_force
                )
            
            # Display result
            print(f"\n{result.format_summary()}")
            
            if result.success:
                print(f"{Colors.GREEN}✓ Order placed successfully!{Colors.ENDC}")
            else:
                print(f"{Colors.RED}✗ Order failed: {result.error_message}{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        
        input("\nPress Enter to continue...")
    
    def market_data_menu(self):
        """Menu for viewing market data"""
        while True:
            clear_screen()
            print_header()
            print_menu("MARKET DATA", [
                "Current Prices",
                "24h Statistics",
                "Order Book",
                "Top Gainers",
                "Top Losers",
                "High Volume Symbols"
            ])
            
            choice = input("Enter choice: ").strip()
            
            if choice == '0':
                return
            elif choice == '1':
                self.show_current_prices()
            elif choice == '2':
                self.show_24h_stats()
            elif choice == '3':
                self.show_order_book()
            elif choice == '4':
                self.show_top_gainers()
            elif choice == '5':
                self.show_top_losers()
            elif choice == '6':
                self.show_high_volume()
            else:
                input(f"{Colors.RED}Invalid choice. Press Enter to continue...{Colors.ENDC}")
    
    def show_current_prices(self):
        """Show current prices"""
        clear_screen()
        print_header()
        print(f"{Colors.BOLD}CURRENT PRICES{Colors.ENDC}\n")
        
        symbol = get_input("Enter symbol (or press Enter for all)")
        
        try:
            if symbol:
                price = self.market_manager.get_price(symbol)
                if price:
                    print(f"\n{Colors.GREEN}{symbol.upper()}: {price.price:,.2f} USDT{Colors.ENDC}\n")
                else:
                    print(f"{Colors.RED}Could not fetch price for {symbol}{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}Fetching all prices...{Colors.ENDC}")
                prices = self.market_manager.get_all_prices()
                if prices:
                    print(format_price_table(prices))
                else:
                    print(f"{Colors.RED}Could not fetch prices{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        
        input("Press Enter to continue...")
    
    def show_24h_stats(self):
        """Show 24h statistics"""
        clear_screen()
        print_header()
        print(f"{Colors.BOLD}24H STATISTICS{Colors.ENDC}\n")
        
        symbol = get_input("Enter symbol (or press Enter for all)")
        
        try:
            if symbol:
                stats = self.market_manager.get_24h_stats(symbol)
                if stats:
                    print(stats.format_summary())
                else:
                    print(f"{Colors.RED}Could not fetch stats for {symbol}{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}Fetching all 24h stats...{Colors.ENDC}")
                stats = self.market_manager.get_all_24h_stats()
                if stats:
                    print(format_24h_table(stats))
                else:
                    print(f"{Colors.RED}Could not fetch stats{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        
        input("Press Enter to continue...")
    
    def show_order_book(self):
        """Show order book"""
        clear_screen()
        print_header()
        print(f"{Colors.BOLD}ORDER BOOK{Colors.ENDC}\n")
        
        symbol = get_input("Enter symbol (e.g., BTCUSDT)")
        if not symbol:
            input("Symbol is required. Press Enter to continue...")
            return
        
        depth_str = get_input("Depth (5-100)", "10")
        try:
            depth = int(depth_str)
            depth = max(5, min(100, depth))
        except:
            depth = 10
        
        try:
            print(f"{Colors.YELLOW}Fetching order book...{Colors.ENDC}")
            order_book = self.market_manager.get_order_book(symbol, limit=100)
            if order_book:
                print(order_book.format_summary(depth=depth))
            else:
                print(f"{Colors.RED}Could not fetch order book for {symbol}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        
        input("Press Enter to continue...")
    
    def show_top_gainers(self):
        """Show top gaining symbols"""
        clear_screen()
        print_header()
        print(f"{Colors.BOLD}TOP GAINERS (24H){Colors.ENDC}\n")
        
        try:
            print(f"{Colors.YELLOW}Fetching top gainers...{Colors.ENDC}")
            gainers = self.market_manager.get_top_gainers(limit=15)
            if gainers:
                print(format_24h_table(gainers, "Top Gainers (24h)"))
            else:
                print(f"{Colors.RED}Could not fetch data{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        
        input("Press Enter to continue...")
    
    def show_top_losers(self):
        """Show top losing symbols"""
        clear_screen()
        print_header()
        print(f"{Colors.BOLD}TOP LOSERS (24H){Colors.ENDC}\n")
        
        try:
            print(f"{Colors.YELLOW}Fetching top losers...{Colors.ENDC}")
            losers = self.market_manager.get_top_losers(limit=15)
            if losers:
                print(format_24h_table(losers, "Top Losers (24h)"))
            else:
                print(f"{Colors.RED}Could not fetch data{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        
        input("Press Enter to continue...")
    
    def show_high_volume(self):
        """Show high volume symbols"""
        clear_screen()
        print_header()
        print(f"{Colors.BOLD}HIGH VOLUME SYMBOLS (24H){Colors.ENDC}\n")
        
        try:
            print(f"{Colors.YELLOW}Fetching high volume symbols...{Colors.ENDC}")
            high_vol = self.market_manager.get_high_volume_symbols(limit=15)
            if high_vol:
                print(format_24h_table(high_vol, "High Volume Symbols (24h)"))
            else:
                print(f"{Colors.RED}Could not fetch data{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        
        input("Press Enter to continue...")
    
    def account_info_menu(self):
        """Show account information"""
        clear_screen()
        print_header()
        print(f"{Colors.BOLD}ACCOUNT INFORMATION{Colors.ENDC}\n")
        
        try:
            print(f"{Colors.YELLOW}Fetching account info...{Colors.ENDC}")
            account_info = self.client.get_account_info()
            
            print(f"\n{Colors.CYAN}Account Details:{Colors.ENDC}")
            print(f"  Can Trade: {account_info.get('canTrade', False)}")
            print(f"  Can Withdraw: {account_info.get('canWithdraw', False)}")
            print(f"  Can Deposit: {account_info.get('canDeposit', False)}")
            
            # Show balances
            assets = account_info.get('assets', [])
            if assets:
                print(f"\n{Colors.CYAN}Balances:{Colors.ENDC}")
                print(f"  {'Asset':<10} {'Wallet Balance':>18} {'Available':>18} {'Unrealized P&L':>18}")
                print(f"  {'-' * 70}")
                
                for asset in assets:
                    wallet_balance = float(asset.get('walletBalance', 0))
                    available = float(asset.get('availableBalance', 0))
                    unrealized = float(asset.get('unrealizedProfit', 0))
                    
                    if wallet_balance != 0 or available != 0 or unrealized != 0:
                        asset_name = asset.get('asset', 'UNKNOWN')
                        print(f"  {asset_name:<10} {wallet_balance:>18.8f} {available:>18.8f} {unrealized:>18.8f}")
            
            # Show positions
            positions = account_info.get('positions', [])
            active_positions = [p for p in positions if float(p.get('positionAmt', 0)) != 0]
            
            if active_positions:
                print(f"\n{Colors.CYAN}Open Positions:{Colors.ENDC}")
                print(f"  {'Symbol':<12} {'Side':<6} {'Amount':>12} {'Entry Price':>14} {'Unrealized P&L':>16}")
                print(f"  {'-' * 70}")
                
                for pos in active_positions:
                    symbol = pos.get('symbol', '')
                    amt = float(pos.get('positionAmt', 0))
                    side = 'LONG' if amt > 0 else 'SHORT'
                    entry = float(pos.get('entryPrice', 0))
                    pnl = float(pos.get('unrealizedProfit', 0))
                    
                    pnl_color = Colors.GREEN if pnl >= 0 else Colors.RED
                    print(f"  {symbol:<12} {side:<6} {abs(amt):>12.4f} {entry:>14.2f} {pnl_color}{pnl:>16.2f}{Colors.ENDC}")
            else:
                print(f"\n{Colors.YELLOW}No open positions{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        
        input("\nPress Enter to continue...")
    
    def view_open_orders_menu(self):
        """View open orders"""
        clear_screen()
        print_header()
        print(f"{Colors.BOLD}OPEN ORDERS{Colors.ENDC}\n")
        
        symbol = get_input("Enter symbol (or press Enter for all)")
        
        try:
            print(f"{Colors.YELLOW}Fetching open orders...{Colors.ENDC}")
            orders = self.client.get_open_orders(symbol if symbol else None)
            
            if orders:
                print(f"\n{Colors.CYAN}Found {len(orders)} open order(s):{Colors.ENDC}\n")
                print(f"{'Order ID':<15} {'Symbol':<12} {'Side':<6} {'Type':<12} {'Price':>12} {'Qty':>10} {'Status':<10}")
                print(f"{'-' * 90}")
                
                for order in orders:
                    order_id = order.get('orderId', 0)
                    sym = order.get('symbol', '')
                    side = order.get('side', '')
                    order_type = order.get('type', '')
                    price = float(order.get('price', 0))
                    qty = float(order.get('origQty', 0))
                    status = order.get('status', '')
                    
                    price_str = f"{price:.2f}" if price > 0 else "MARKET"
                    print(f"{order_id:<15} {sym:<12} {side:<6} {order_type:<12} {price_str:>12} {qty:>10.4f} {status:<10}")
            else:
                print(f"\n{Colors.YELLOW}No open orders found{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        
        input("\nPress Enter to continue...")
    
    def cancel_orders_menu(self):
        """Cancel orders menu"""
        clear_screen()
        print_header()
        print_menu("CANCEL ORDERS", [
            "Cancel Specific Order",
            "Cancel All Orders for Symbol"
        ])
        
        choice = input("Enter choice: ").strip()
        
        if choice == '0':
            return
        elif choice == '1':
            self.cancel_specific_order()
        elif choice == '2':
            self.cancel_all_orders()
        else:
            input(f"{Colors.RED}Invalid choice. Press Enter to continue...{Colors.ENDC}")
    
    def cancel_specific_order(self):
        """Cancel a specific order"""
        print(f"\n{Colors.BOLD}Cancel Specific Order{Colors.ENDC}\n")
        
        symbol = get_input("Symbol (e.g., BTCUSDT)")
        if not symbol:
            input("Symbol is required. Press Enter to continue...")
            return
        
        order_id = get_input("Order ID")
        if not order_id:
            input("Order ID is required. Press Enter to continue...")
            return
        
        try:
            if not confirm(f"Cancel order {order_id} for {symbol}?"):
                print("Cancellation aborted.")
                input("Press Enter to continue...")
                return
            
            result = self.client.cancel_order(symbol, int(order_id))
            print(f"\n{Colors.GREEN}✓ Order cancelled successfully!{Colors.ENDC}")
            print(f"  Order ID: {result.get('orderId')}")
            print(f"  Symbol: {result.get('symbol')}")
            print(f"  Status: {result.get('status')}")
            
        except Exception as e:
            print(f"{Colors.RED}Error cancelling order: {e}{Colors.ENDC}")
        
        input("\nPress Enter to continue...")
    
    def cancel_all_orders(self):
        """Cancel all orders for a symbol"""
        print(f"\n{Colors.BOLD}Cancel All Orders{Colors.ENDC}\n")
        
        symbol = get_input("Symbol (e.g., BTCUSDT)")
        if not symbol:
            input("Symbol is required. Press Enter to continue...")
            return
        
        try:
            # First get open orders to show what will be cancelled
            orders = self.client.get_open_orders(symbol)
            
            if not orders:
                print(f"\n{Colors.YELLOW}No open orders for {symbol}{Colors.ENDC}")
                input("Press Enter to continue...")
                return
            
            print(f"\n{Colors.CYAN}This will cancel {len(orders)} order(s):{Colors.ENDC}")
            for order in orders:
                order_id = order.get('orderId')
                order_type = order.get('type')
                side = order.get('side')
                print(f"  - Order {order_id}: {side} {order_type}")
            
            if not confirm(f"\nCancel all orders for {symbol}?"):
                print("Cancellation aborted.")
                input("Press Enter to continue...")
                return
            
            # Cancel all orders
            cancelled_count = 0
            for order in orders:
                try:
                    self.client.cancel_order(symbol, order.get('orderId'))
                    cancelled_count += 1
                except Exception as e:
                    print(f"{Colors.RED}Failed to cancel order {order.get('orderId')}: {e}{Colors.ENDC}")
            
            print(f"\n{Colors.GREEN}✓ Cancelled {cancelled_count} order(s){Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        
        input("\nPress Enter to continue...")


def run_interactive_mode(client: BinanceFuturesClient):
    """
    Entry point to run the interactive menu
    
    Args:
        client: Configured BinanceFuturesClient instance
    """
    menu = InteractiveMenu(client)
    menu.run()
