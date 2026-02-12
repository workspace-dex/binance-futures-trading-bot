"""
Binance Futures Testnet Client
A clean wrapper for Binance Futures Testnet API
"""

import hmac
import hashlib
import time
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class BinanceFuturesClient:
    """
    Binance Futures Testnet API Client
    
    Handles authentication, request signing, and API communication
    """
    
    TESTNET_BASE_URL = "https://testnet.binancefuture.com"
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize the client with API credentials
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': api_key
        })
        
    def _generate_signature(self, query_string: str) -> str:
        """
        Generate HMAC SHA256 signature for API requests
        
        Args:
            query_string: Query string to sign
            
        Returns:
            Hex-encoded signature
        """
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds"""
        return int(time.time() * 1000)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to Binance API
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            params: Request parameters
            signed: Whether to sign the request
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.RequestException: On network/API errors
        """
        url = f"{self.TESTNET_BASE_URL}{endpoint}"
        params = params or {}
        
        if signed:
            params['timestamp'] = self._get_timestamp()
            params['recvWindow'] = 5000
            
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            params['signature'] = self._generate_signature(query_string)
        
        try:
            logger.info(f"API Request: {method} {endpoint} - Params: {params}")
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"API Response: {response.status_code} - {result}")
            
            # Check for API errors
            if 'code' in result and result['code'] != 0:
                error_msg = result.get('msg', 'Unknown error')
                logger.error(f"API Error: Code {result['code']} - {error_msg}")
                raise BinanceAPIError(result['code'], error_msg)
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {method} {endpoint}")
            raise BinanceNetworkError("Request timed out")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {method} {endpoint} - {str(e)}")
            raise BinanceNetworkError(f"Connection failed: {str(e)}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {method} {endpoint} - {e.response.status_code} - {e.response.text}")
            raise BinanceAPIError(e.response.status_code, e.response.text)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {endpoint} - {str(e)}")
            raise BinanceNetworkError(f"Request failed: {str(e)}")
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return self._make_request('GET', '/fapi/v2/account', signed=True)
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange information (trading rules, symbols)"""
        return self._make_request('GET', '/fapi/v1/exchangeInfo')
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: Optional[str] = None,
        stop_price: Optional[float] = None,
        close_position: bool = False
    ) -> Dict[str, Any]:
        """
        Place a new order on Binance Futures
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            order_type: MARKET, LIMIT, STOP_MARKET, STOP_LOSS_LIMIT, etc.
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            time_in_force: GTC, IOC, FOK (required for LIMIT orders)
            stop_price: Stop price for stop orders
            close_position: Close position flag
            
        Returns:
            Order response from API
        """
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': quantity
        }
        
        if order_type.upper() == 'LIMIT':
            if price is None:
                raise ValueError("Price is required for LIMIT orders")
            params['price'] = price
            params['timeInForce'] = time_in_force or 'GTC'
        
        if stop_price is not None:
            params['stopPrice'] = stop_price
            
        if close_position:
            params['closePosition'] = 'true'
        
        return self._make_request('POST', '/fapi/v1/order', params=params, signed=True)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Get status of a specific order"""
        params = {
            'symbol': symbol.upper(),
            'orderId': order_id
        }
        return self._make_request('GET', '/fapi/v1/order', params=params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel a specific order"""
        params = {
            'symbol': symbol.upper(),
            'orderId': order_id
        }
        return self._make_request('DELETE', '/fapi/v1/order', params=params, signed=True)
    
    # Market Data Methods
    def get_ticker_price(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get latest price for a symbol or all symbols
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT). If None, returns all symbols.
            
        Returns:
            Price data for symbol(s)
        """
        params = {}
        if symbol:
            params['symbol'] = symbol.upper()
        return self._make_request('GET', '/fapi/v1/ticker/price', params=params)
    
    def get_ticker_24hr(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get 24hr ticker price change statistics
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT). If None, returns all symbols.
            
        Returns:
            24hr statistics for symbol(s)
        """
        params = {}
        if symbol:
            params['symbol'] = symbol.upper()
        return self._make_request('GET', '/fapi/v1/ticker/24hr', params=params)
    
    def get_klines(self, symbol: str, interval: str, limit: int = 500, 
                   start_time: Optional[int] = None, end_time: Optional[int] = None) -> list:
        """
        Get kline/candlestick data
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            limit: Number of candles to retrieve (default 500, max 1500)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            List of kline data
        """
        params = {
            'symbol': symbol.upper(),
            'interval': interval,
            'limit': limit
        }
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        return self._make_request('GET', '/fapi/v1/klines', params=params)
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get order book for a symbol
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            limit: Number of bids/asks (5, 10, 20, 50, 100, 500, 1000)
            
        Returns:
            Order book data with bids and asks
        """
        params = {
            'symbol': symbol.upper(),
            'limit': limit
        }
        return self._make_request('GET', '/fapi/v1/depth', params=params)
    
    def get_recent_trades(self, symbol: str, limit: int = 500) -> list:
        """
        Get recent trades for a symbol
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            limit: Number of trades to retrieve (default 500, max 1000)
            
        Returns:
            List of recent trades
        """
        params = {
            'symbol': symbol.upper(),
            'limit': limit
        }
        return self._make_request('GET', '/fapi/v1/trades', params=params)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """
        Get all open orders for a symbol or all symbols
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT). If None, returns all open orders.
            
        Returns:
            List of open orders
        """
        params = {}
        if symbol:
            params['symbol'] = symbol.upper()
        return self._make_request('GET', '/fapi/v1/openOrders', params=params, signed=True)
    
    def get_all_orders(self, symbol: str, limit: int = 500) -> list:
        """
        Get all orders for a symbol
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            limit: Number of orders to retrieve (default 500, max 1000)
            
        Returns:
            List of orders
        """
        params = {
            'symbol': symbol.upper(),
            'limit': limit
        }
        return self._make_request('GET', '/fapi/v1/allOrders', params=params, signed=True)


class BinanceAPIError(Exception):
    """Exception for Binance API errors"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API Error {code}: {message}")


class BinanceNetworkError(Exception):
    """Exception for network-related errors"""
    pass
