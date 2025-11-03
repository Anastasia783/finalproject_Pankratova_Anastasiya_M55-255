"""
Custom exceptions for ValutaTrade Hub
"""

class ValutaTradeError(Exception):
    """Base exception for ValutaTrade Hub"""
    pass


class InsufficientFundsError(ValutaTradeError):
    """Insufficient funds for operation"""
    
    def __init__(self, currency_code: str, available: float, required: float):
        self.currency_code = currency_code
        self.available = available
        self.required = required
        super().__init__(f"Недостаточно средств: доступно {available} {currency_code}, требуется {required} {currency_code}")


class CurrencyNotFoundError(ValutaTradeError):
    """Currency not found in registry"""
    
    def __init__(self, currency_code: str):
        self.currency_code = currency_code
        super().__init__(f"Неизвестная валюта '{currency_code}'")


class ApiRequestError(ValutaTradeError):
    """External API request failed"""
    
    def __init__(self, reason: str = "Unknown error"):
        self.reason = reason
        super().__init__(f"Ошибка при обращении к внешнему API: {reason}")


class UserNotFoundError(ValutaTradeError):
    """User not found"""
    
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Пользователь '{username}' не найден")


class AuthenticationError(ValutaTradeError):
    """Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)