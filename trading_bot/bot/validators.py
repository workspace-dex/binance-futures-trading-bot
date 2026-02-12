"""
Input Validation
Validates user input for trading operations
"""

import re
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    errors: List[str]
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
    
    def add_error(self, message: str):
        """Add an error message"""
        self.is_valid = False
        self.errors.append(message)
    
    def format_errors(self) -> str:
        """Format errors as a readable string"""
        if self.is_valid:
            return "Validation passed"
        return "\n".join([f"  - {error}" for error in self.errors])


class OrderValidator:
    """Validator for order inputs"""
    
    # Valid sides
    VALID_SIDES = ['BUY', 'SELL']
    
    # Valid order types
    VALID_ORDER_TYPES = ['MARKET', 'LIMIT', 'STOP_LIMIT']
    
    # Valid time in force values
    VALID_TIME_IN_FORCE = ['GTC', 'IOC', 'FOK']
    
    # Symbol pattern (e.g., BTCUSDT, ETHUSDT)
    SYMBOL_PATTERN = re.compile(r'^[A-Z0-9]{2,10}USDT$', re.IGNORECASE)
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> ValidationResult:
        """
        Validate trading symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()
        
        if not symbol:
            result.add_error("Symbol is required")
            return result
        
        symbol = symbol.strip().upper()
        
        if not cls.SYMBOL_PATTERN.match(symbol):
            result.add_error(f"Invalid symbol format: '{symbol}'. Expected format like 'BTCUSDT'")
        
        return result
    
    @classmethod
    def validate_side(cls, side: str) -> ValidationResult:
        """
        Validate order side
        
        Args:
            side: Order side (BUY or SELL)
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()
        
        if not side:
            result.add_error("Side is required")
            return result
        
        side = side.strip().upper()
        
        if side not in cls.VALID_SIDES:
            result.add_error(f"Invalid side: '{side}'. Must be one of: {', '.join(cls.VALID_SIDES)}")
        
        return result
    
    @classmethod
    def validate_order_type(cls, order_type: str) -> ValidationResult:
        """
        Validate order type
        
        Args:
            order_type: Type of order
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()
        
        if not order_type:
            result.add_error("Order type is required")
            return result
        
        order_type = order_type.strip().upper()
        
        if order_type not in cls.VALID_ORDER_TYPES:
            result.add_error(f"Invalid order type: '{order_type}'. "
                           f"Must be one of: {', '.join(cls.VALID_ORDER_TYPES)}")
        
        return result
    
    @classmethod
    def validate_quantity(cls, quantity: str) -> ValidationResult:
        """
        Validate order quantity
        
        Args:
            quantity: Order quantity as string
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()
        
        if not quantity:
            result.add_error("Quantity is required")
            return result
        
        try:
            qty = float(quantity)
            if qty <= 0:
                result.add_error(f"Quantity must be positive, got: {qty}")
        except ValueError:
            result.add_error(f"Invalid quantity format: '{quantity}'. Must be a number")
        
        return result
    
    @classmethod
    def validate_price(cls, price: str, order_type: str) -> ValidationResult:
        """
        Validate order price
        
        Args:
            price: Order price as string
            order_type: Type of order
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()
        
        # Price is required for LIMIT and STOP_LIMIT orders
        if order_type.upper() in ['LIMIT', 'STOP_LIMIT']:
            if not price:
                result.add_error(f"Price is required for {order_type} orders")
                return result
            
            try:
                price_val = float(price)
                if price_val <= 0:
                    result.add_error(f"Price must be positive, got: {price_val}")
            except ValueError:
                result.add_error(f"Invalid price format: '{price}'. Must be a number")
        
        return result
    
    @classmethod
    def validate_stop_price(cls, stop_price: str, order_type: str) -> ValidationResult:
        """
        Validate stop price
        
        Args:
            stop_price: Stop price as string
            order_type: Type of order
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()
        
        # Stop price is required for STOP_LIMIT orders
        if order_type.upper() == 'STOP_LIMIT':
            if not stop_price:
                result.add_error("Stop price is required for STOP_LIMIT orders")
                return result
            
            try:
                stop_val = float(stop_price)
                if stop_val <= 0:
                    result.add_error(f"Stop price must be positive, got: {stop_val}")
            except ValueError:
                result.add_error(f"Invalid stop price format: '{stop_price}'. Must be a number")
        
        return result
    
    @classmethod
    def validate_time_in_force(cls, time_in_force: str) -> ValidationResult:
        """
        Validate time in force
        
        Args:
            time_in_force: Time in force value
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()
        
        if not time_in_force:
            return result  # Optional, defaults to GTC
        
        time_in_force = time_in_force.strip().upper()
        
        if time_in_force not in cls.VALID_TIME_IN_FORCE:
            result.add_error(f"Invalid time in force: '{time_in_force}'. "
                           f"Must be one of: {', '.join(cls.VALID_TIME_IN_FORCE)}")
        
        return result
    
    @classmethod
    def validate_order_request(
        cls,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str = None,
        stop_price: str = None,
        time_in_force: str = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate a complete order request
        
        Args:
            symbol: Trading symbol
            side: Order side
            order_type: Order type
            quantity: Order quantity
            price: Order price
            stop_price: Stop price
            time_in_force: Time in force
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        all_errors = []
        
        validations = [
            cls.validate_symbol(symbol),
            cls.validate_side(side),
            cls.validate_order_type(order_type),
            cls.validate_quantity(quantity),
            cls.validate_price(price, order_type),
            cls.validate_stop_price(stop_price, order_type),
        ]
        
        if time_in_force:
            validations.append(cls.validate_time_in_force(time_in_force))
        
        for validation in validations:
            if not validation.is_valid:
                all_errors.extend(validation.errors)
        
        return len(all_errors) == 0, all_errors
