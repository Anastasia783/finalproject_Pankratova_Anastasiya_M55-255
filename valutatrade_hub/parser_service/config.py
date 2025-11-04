import os


class ParserConfig:
    """Configuration for Parser Service"""
    
    def __init__(self):
        # API Keys (load from environment variables)
        self.EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY", "14f77a4a07872fd710f92e4b")
        
        # Endpoints
        self.COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
        self.EXCHANGERATE_API_URL = "https://v6.exchangerate-api.com/v6"
        
        # Currencies - используем валюты, которые точно есть в API
        self.BASE_CURRENCY = "USD"
        self.FIAT_CURRENCIES = ("EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "RUB")
        self.CRYPTO_CURRENCIES = ("BTC", "ETH", "LTC", "ADA")
        self.CRYPTO_ID_MAP = {
            "BTC": "bitcoin",
            "ETH": "ethereum", 
            "LTC": "litecoin",
            "ADA": "cardano"
        }
        
        # File paths
        self.RATES_FILE_PATH = "data/rates.json"
        self.HISTORY_FILE_PATH = "data/exchange_rates.json"
        
        # Network settings
        self.REQUEST_TIMEOUT = 10
        self.RATES_TTL_SECONDS = 300  # 5 minutes
        
        # Update settings
        self.UPDATE_INTERVAL_MINUTES = 5


# Global configuration instance
config = ParserConfig()