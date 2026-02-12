"""
Order Placement Logic
Handles order execution and formatting
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .client import BinanceFuturesClient, BinanceAPIError, BinanceNetworkError

logger = logging.getLogger(__name__)


@dataclass
class OrderRequest:
    """Data class representing an order request"""
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    time_in_force: str = 'GTC'
    stop_price: Optional[float] = None


@dataclass
class OrderResult:
    """Data class representing an order result"""
    success: bool
    order_id: Optional[int] = None
    status: Optional[str] = None
    executed_qty: Optional[float] = None
    avg_price: Optional[float] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    order_type: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    
    def format_summary(self) -> str:
        """Format order result as a readable summary"""
        lines = []
        lines.append("=" * 50)
        lines.append("ORDER RESULT")
        lines.append("=" * 50)
        
        if self.success:
            lines.append(f"Status: SUCCESS")
            lines.append(f"Order ID: {self.order_id}")
            lines.append(f"Symbol: {self.symbol}")
            lines.append(f"Side: {self.side}")
            lines.append(f"Type: {self.order_type}")
            lines.append(f"Status: {self.status}")
            lines.append(f"Executed Qty: {self.executed_qty}")
            if self.avg_price:
                lines.append(f"Avg Price: {self.avg_price}")
        else:
            lines.append(f"Status: FAILED")
            lines.append(f"Error: {self.error_message}")
        
        lines.append("=" * 50)
        return "\n".join(lines)


class OrderManager:
    """
    Manages order placement operations
    Provides a high-level interface for placing orders
    """
    
    def __init__(self, client: BinanceFuturesClient):
        """
        Initialize OrderManager with a Binance client
        
        Args:
            client: Configured BinanceFuturesClient instance
        """
        self.client = client
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> OrderResult:
        """
        Place a market order
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            
        Returns:
            OrderResult with execution details
        """
        order_request = OrderRequest(
            symbol=symbol,
            side=side,
            order_type='MARKET',
            quantity=quantity
        )
        return self._execute_order(order_request)
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = 'GTC'
    ) -> OrderResult:
        """
        Place a limit order
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (GTC, IOC, FOK)
            
        Returns:
            OrderResult with execution details
        """
        order_request = OrderRequest(
            symbol=symbol,
            side=side,
            order_type='LIMIT',
            quantity=quantity,
            price=price,
            time_in_force=time_in_force
        )
        return self._execute_order(order_request)
    
    def place_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: str = 'GTC'
    ) -> OrderResult:
        """
        Place a stop-limit order (BONUS feature)
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price
            stop_price: Stop trigger price
            time_in_force: Time in force (GTC, IOC, FOK)
            
        Returns:
            OrderResult with execution details
        """
        order_request = OrderRequest(
            symbol=symbol,
            side=side,
            order_type='STOP_LOSS_LIMIT',
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
            stop_price=stop_price
        )
        return self._execute_order(order_request)
    
    def _execute_order(self, order_request: OrderRequest) -> OrderResult:
        """
        Execute an order request
        
        Args:
            order_request: OrderRequest object with order details
            
        Returns:
            OrderResult with execution result
        """
        logger.info(f"Placing {order_request.order_type} order: "
                   f"{order_request.side} {order_request.quantity} {order_request.symbol}")
        
        try:
            response = self.client.place_order(
                symbol=order_request.symbol,
                side=order_request.side,
                order_type=order_request.order_type,
                quantity=order_request.quantity,
                price=order_request.price,
                time_in_force=order_request.time_in_force,
                stop_price=order_request.stop_price
            )
            
            # Parse response
            result = OrderResult(
                success=True,
                order_id=response.get('orderId'),
                status=response.get('status'),
                executed_qty=float(response.get('executedQty', 0)),
                avg_price=float(response.get('avgPrice', 0)) if response.get('avgPrice') else None,
                symbol=response.get('symbol'),
                side=response.get('side'),
                order_type=response.get('type'),
                raw_response=response
            )
            
            logger.info(f"Order placed successfully: ID={result.order_id}, "
                       f"Status={result.status}, ExecutedQty={result.executed_qty}")
            
            return result
            
        except BinanceAPIError as e:
            logger.error(f"API error placing order: {e}")
            return OrderResult(
                success=False,
                error_message=f"API Error: {e.message}",
                symbol=order_request.symbol,
                side=order_request.side,
                order_type=order_request.order_type
            )
            
        except BinanceNetworkError as e:
            logger.error(f"Network error placing order: {e}")
            return OrderResult(
                success=False,
                error_message=f"Network Error: {str(e)}",
                symbol=order_request.symbol,
                side=order_request.side,
                order_type=order_request.order_type
            )
            
        except Exception as e:
            logger.error(f"Unexpected error placing order: {e}", exc_info=True)
            return OrderResult(
                success=False,
                error_message=f"Unexpected Error: {str(e)}",
                symbol=order_request.symbol,
                side=order_request.side,
                order_type=order_request.order_type
            )
