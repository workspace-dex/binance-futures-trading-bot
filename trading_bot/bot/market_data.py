"""
Market Data Module
Provides high-level functions for fetching and formatting market data
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from .client import BinanceFuturesClient

logger = logging.getLogger(__name__)


@dataclass
class TickerData:
    """Represents ticker price data"""
    symbol: str
    price: float
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'TickerData':
        return cls(
            symbol=data.get('symbol', ''),
            price=float(data.get('price', 0))
        )


@dataclass
class Ticker24hData:
    """Represents 24hr ticker statistics"""
    symbol: str
    price_change: float
    price_change_percent: float
    weighted_avg_price: float
    last_price: float
    last_qty: float
    open_price: float
    high_price: float
    low_price: float
    volume: float
    quote_volume: float
    open_time: int
    close_time: int
    first_id: int
    last_id: int
    count: int
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Ticker24hData':
        return cls(
            symbol=data.get('symbol', ''),
            price_change=float(data.get('priceChange', 0)),
            price_change_percent=float(data.get('priceChangePercent', 0)),
            weighted_avg_price=float(data.get('weightedAvgPrice', 0)),
            last_price=float(data.get('lastPrice', 0)),
            last_qty=float(data.get('lastQty', 0)),
            open_price=float(data.get('openPrice', 0)),
            high_price=float(data.get('highPrice', 0)),
            low_price=float(data.get('lowPrice', 0)),
            volume=float(data.get('volume', 0)),
            quote_volume=float(data.get('quoteVolume', 0)),
            open_time=data.get('openTime', 0),
            close_time=data.get('closeTime', 0),
            first_id=data.get('firstId', 0),
            last_id=data.get('lastId', 0),
            count=data.get('count', 0)
        )
    
    def format_summary(self) -> str:
        """Format 24hr data as readable summary"""
        open_time_str = datetime.fromtimestamp(self.open_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
        close_time_str = datetime.fromtimestamp(self.close_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
        
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"24HR STATISTICS: {self.symbol}")
        lines.append(f"{'='*60}")
        lines.append(f"Last Price:        {self.last_price:,.2f}")
        lines.append(f"24h Change:        {self.price_change:+,.2f} ({self.price_change_percent:+.2f}%)")
        lines.append(f"Open Price:        {self.open_price:,.2f}")
        lines.append(f"High Price:        {self.high_price:,.2f}")
        lines.append(f"Low Price:         {self.low_price:,.2f}")
        lines.append(f"Weighted Avg:      {self.weighted_avg_price:,.2f}")
        lines.append(f"Volume:            {self.volume:,.4f}")
        lines.append(f"Quote Volume:      {self.quote_volume:,.2f} USDT")
        lines.append(f"Period:            {open_time_str} to {close_time_str}")
        lines.append(f"Trades:            {self.count:,}")
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)


@dataclass
class OrderBookLevel:
    """Represents a single level in order book"""
    price: float
    quantity: float


@dataclass
class OrderBook:
    """Represents order book data"""
    symbol: str
    last_update_id: int
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    
    @classmethod
    def from_api(cls, data: Dict[str, Any], symbol: str) -> 'OrderBook':
        bids = [OrderBookLevel(float(b[0]), float(b[1])) for b in data.get('bids', [])]
        asks = [OrderBookLevel(float(a[0]), float(a[1])) for a in data.get('asks', [])]
        
        return cls(
            symbol=symbol,
            last_update_id=data.get('lastUpdateId', 0),
            bids=bids,
            asks=asks
        )
    
    def format_summary(self, depth: int = 5) -> str:
        """Format order book as readable table"""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"ORDER BOOK: {self.symbol}")
        lines.append(f"{'='*60}")
        lines.append(f"Last Update ID: {self.last_update_id}")
        lines.append(f"\n{'BIDS (Buy)':<30} {'ASKS (Sell)':<30}")
        lines.append(f"{'-'*60}")
        lines.append(f"{'Price':>12} {'Qty':>12}  |  {'Price':>12} {'Qty':>12}")
        lines.append(f"{'-'*60}")
        
        for i in range(min(depth, max(len(self.bids), len(self.asks)))):
            bid_line = ""
            ask_line = ""
            
            if i < len(self.bids):
                bid = self.bids[i]
                bid_line = f"{bid.price:>12,.2f} {bid.quantity:>12,.4f}"
            else:
                bid_line = " " * 25
            
            if i < len(self.asks):
                ask = self.asks[i]
                ask_line = f"{ask.price:>12,.2f} {ask.quantity:>12,.4f}"
            
            lines.append(f"{bid_line}  |  {ask_line}")
        
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)


class MarketDataManager:
    """
    High-level manager for market data operations
    """
    
    def __init__(self, client: BinanceFuturesClient):
        """
        Initialize MarketDataManager with a Binance client
        
        Args:
            client: Configured BinanceFuturesClient instance
        """
        self.client = client
    
    def get_price(self, symbol: str) -> Optional[TickerData]:
        """
        Get current price for a symbol
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            
        Returns:
            TickerData or None if error
        """
        try:
            data = self.client.get_ticker_price(symbol)
            return TickerData.from_api(data)
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    def get_all_prices(self) -> List[TickerData]:
        """
        Get current prices for all symbols
        
        Returns:
            List of TickerData
        """
        try:
            data = self.client.get_ticker_price()
            if isinstance(data, list):
                return [TickerData.from_api(d) for d in data]
            return [TickerData.from_api(data)]
        except Exception as e:
            logger.error(f"Error fetching all prices: {e}")
            return []
    
    def get_24h_stats(self, symbol: str) -> Optional[Ticker24hData]:
        """
        Get 24hr statistics for a symbol
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            
        Returns:
            Ticker24hData or None if error
        """
        try:
            data = self.client.get_ticker_24hr(symbol)
            return Ticker24hData.from_api(data)
        except Exception as e:
            logger.error(f"Error fetching 24h stats for {symbol}: {e}")
            return None
    
    def get_all_24h_stats(self) -> List[Ticker24hData]:
        """
        Get 24hr statistics for all symbols
        
        Returns:
            List of Ticker24hData
        """
        try:
            data = self.client.get_ticker_24hr()
            if isinstance(data, list):
                return [Ticker24hData.from_api(d) for d in data]
            return [Ticker24hData.from_api(data)]
        except Exception as e:
            logger.error(f"Error fetching all 24h stats: {e}")
            return []
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Optional[OrderBook]:
        """
        Get order book for a symbol
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            limit: Number of levels to retrieve
            
        Returns:
            OrderBook or None if error
        """
        try:
            data = self.client.get_order_book(symbol, limit)
            return OrderBook.from_api(data, symbol)
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            return None
    
    def get_top_gainers(self, limit: int = 10) -> List[Ticker24hData]:
        """
        Get top gaining symbols by 24h change percent
        
        Args:
            limit: Number of top gainers to return
            
        Returns:
            List of top gaining Ticker24hData
        """
        stats = self.get_all_24h_stats()
        sorted_stats = sorted(stats, key=lambda x: x.price_change_percent, reverse=True)
        return sorted_stats[:limit]
    
    def get_top_losers(self, limit: int = 10) -> List[Ticker24hData]:
        """
        Get top losing symbols by 24h change percent
        
        Args:
            limit: Number of top losers to return
            
        Returns:
            List of top losing Ticker24hData
        """
        stats = self.get_all_24h_stats()
        sorted_stats = sorted(stats, key=lambda x: x.price_change_percent)
        return sorted_stats[:limit]
    
    def get_high_volume_symbols(self, limit: int = 10) -> List[Ticker24hData]:
        """
        Get symbols with highest trading volume
        
        Args:
            limit: Number of symbols to return
            
        Returns:
            List of high volume Ticker24hData
        """
        stats = self.get_all_24h_stats()
        sorted_stats = sorted(stats, key=lambda x: x.quote_volume, reverse=True)
        return sorted_stats[:limit]


def format_price_table(prices: List[TickerData], title: str = "Prices") -> str:
    """
    Format a list of prices as a table
    
    Args:
        prices: List of TickerData
        title: Table title
        
    Returns:
        Formatted table string
    """
    lines = []
    lines.append(f"\n{'='*40}")
    lines.append(f"{title}")
    lines.append(f"{'='*40}")
    lines.append(f"{'Symbol':<15} {'Price':>20}")
    lines.append(f"{'-'*40}")
    
    for price in prices[:20]:  # Show first 20
        lines.append(f"{price.symbol:<15} {price.price:>20,.2f}")
    
    if len(prices) > 20:
        lines.append(f"... and {len(prices) - 20} more")
    
    lines.append(f"{'='*40}\n")
    return "\n".join(lines)


def format_24h_table(stats: List[Ticker24hData], title: str = "24h Statistics") -> str:
    """
    Format a list of 24h stats as a table
    
    Args:
        stats: List of Ticker24hData
        title: Table title
        
    Returns:
        Formatted table string
    """
    lines = []
    lines.append(f"\n{'='*80}")
    lines.append(f"{title}")
    lines.append(f"{'='*80}")
    lines.append(f"{'Symbol':<12} {'Last Price':>14} {'24h Change %':>14} {'Volume':>16} {'Trades':>12}")
    lines.append(f"{'-'*80}")
    
    for stat in stats[:15]:  # Show first 15
        change_str = f"{stat.price_change_percent:+.2f}%"
        lines.append(f"{stat.symbol:<12} {stat.last_price:>14,.2f} {change_str:>14} {stat.quote_volume:>16,.0f} {stat.count:>12,}")
    
    lines.append(f"{'='*80}\n")
    return "\n".join(lines)
