"""
Singleton SettingsLoader for configuration management
"""

import os
import toml
from typing import Any, Dict


class SettingsLoader:
    """Singleton class for configuration management"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._config: Dict[str, Any] = {}
            self._load_config()
            self._initialized = True
    
    def _load_config(self):
        """Load configuration from pyproject.toml and environment"""
        # Default configuration
        self._config = {
            "data_dir": "data",
            "rates_ttl_seconds": 300,  # 5 minutes
            "default_base_currency": "USD",
            "log_dir": "logs",
            "log_format": "string",  # or "json"
            "log_level": "INFO",
            "api_timeout": 30,
            "supported_currencies": ["USD", "EUR", "GBP", "JPY", "CHF", "RUB", "BTC", "ETH", "LTC", "ADA"]
        }
        
        # Try to load from pyproject.toml
        try:
            with open("pyproject.toml", "r", encoding="utf-8") as f:
                pyproject_data = toml.load(f)
                
            tool_config = pyproject_data.get("tool", {}).get("valutatrade", {})
            if tool_config:
                self._config.update(tool_config)
        except (FileNotFoundError, toml.TomlDecodeError):
            pass  # Use defaults
        
        # Override with environment variables
        self._config["data_dir"] = os.getenv("VALUTATRADE_DATA_DIR", self._config["data_dir"])
        self._config["rates_ttl_seconds"] = int(os.getenv("VALUTATRADE_RATES_TTL", self._config["rates_ttl_seconds"]))
        self._config["log_level"] = os.getenv("VALUTATRADE_LOG_LEVEL", self._config["log_level"])
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self._config.get(key, default)
    
    def reload(self):
        """Reload configuration"""
        self._initialized = False
        self.__init__()
    
    def __getitem__(self, key: str) -> Any:
        return self._config[key]
    
    def __contains__(self, key: str) -> bool:
        return key in self._config


# Global instance
settings = SettingsLoader()