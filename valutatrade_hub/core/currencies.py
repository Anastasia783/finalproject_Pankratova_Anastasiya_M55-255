from abc import ABC, abstractmethod
from typing import Dict
from valutatrade_hub.core.exceptions import CurrencyNotFoundError


class Currency(ABC):
    """Abstract base class for all currencies"""
    
    def __init__(self, name: str, code: str):
        self._validate_code(code)
        self._validate_name(name)
        
        self._name = name
        self._code = code.upper()
    
    def _validate_code(self, code: str):
        """Validate currency code"""
        if not isinstance(code, str) or not 2 <= len(code) <= 5:
            raise ValueError("Currency code must be 2-5 characters long")
        if not code.isalpha() or " " in code:
            raise ValueError("Currency code must contain only letters without spaces")
    
    def _validate_name(self, name: str):
        """Validate currency name"""
        if not name or not name.strip():
            raise ValueError("Currency name cannot be empty")
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def code(self) -> str:
        return self._code
    
    @abstractmethod
    def get_display_info(self) -> str:
        """Get string representation for UI/logs"""
        pass
    
    def __str__(self) -> str:
        return self.get_display_info()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', code='{self.code}')"


class FiatCurrency(Currency):
    """Fiat currency representation"""
    
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self._issuing_country = issuing_country
    
    @property
    def issuing_country(self) -> str:
        return self._issuing_country
    
    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    """Cryptocurrency representation"""
    
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float = 0.0):
        super().__init__(name, code)
        self._algorithm = algorithm
        self._market_cap = market_cap
    
    @property
    def algorithm(self) -> str:
        return self._algorithm
    
    @property
    def market_cap(self) -> float:
        return self._market_cap
    
    def get_display_info(self) -> str:
        mcap_str = f"{self.market_cap:.2e}" if self.market_cap > 1e9 else f"{self.market_cap:,.2f}"
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {mcap_str})"


# Currency registry
_currency_registry: Dict[str, Currency] = {}


def register_currency(currency: Currency):
    """Register a currency in the global registry"""
    _currency_registry[currency.code] = currency


def get_currency(code: str) -> Currency:
    """Get currency by code"""
    code = code.upper()
    if code not in _currency_registry:
        raise CurrencyNotFoundError(code)
    return _currency_registry[code]


def get_all_currencies() -> Dict[str, Currency]:
    """Get all registered currencies"""
    return _currency_registry.copy()


# Initialize with common currencies
register_currency(FiatCurrency("US Dollar", "USD", "United States"))
register_currency(FiatCurrency("Euro", "EUR", "Eurozone"))
register_currency(FiatCurrency("British Pound", "GBP", "United Kingdom"))
register_currency(FiatCurrency("Japanese Yen", "JPY", "Japan"))
register_currency(FiatCurrency("Swiss Franc", "CHF", "Switzerland"))
register_currency(FiatCurrency("Russian Ruble", "RUB", "Russia"))

register_currency(CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12))
register_currency(CryptoCurrency("Ethereum", "ETH", "Ethash", 372e9))
register_currency(CryptoCurrency("Litecoin", "LTC", "Scrypt", 4.5e9))
register_currency(CryptoCurrency("Cardano", "ADA", "Ouroboros", 12e9))