import json
import os
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PORTFOLIOS_FILE = os.path.join(DATA_DIR, "portfolios.json")
RATES_FILE = os.path.join(DATA_DIR, "rates.json")


def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    os.makedirs(DATA_DIR, exist_ok=True)


def read_json(file_path: str) -> Any:
    """Read JSON file, return empty list/dict if file doesn't exist"""
    ensure_data_dir()
    if not os.path.exists(file_path):
        # Возвращаем соответствующую структуру по умолчанию
        if "users" in file_path:
            return []
        elif "portfolios" in file_path:
            return []
        else:
            return {}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        # Если файл поврежден, возвращаем структуру по умолчанию
        if "users" in file_path:
            return []
        elif "portfolios" in file_path:
            return []
        else:
            return {}


def write_json(data: Any, file_path: str) -> None:
    """Write data to JSON file"""
    ensure_data_dir()
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")


def generate_salt(length: int = 8) -> str:
    """Generate random salt for password hashing"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choices(characters, k=length))


def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """Get exchange rate between two currencies"""
    rates_data = read_json(RATES_FILE)
    
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency == to_currency:
        return 1.0
    
    # Прямой курс
    rate_key = f"{from_currency}_{to_currency}"
    
    # Проверяем свежесть курса (менее 5 минут)
    if rate_key in rates_data:
        rate_info = rates_data[rate_key]
        if "updated_at" in rate_info:
            try:
                updated_at = datetime.fromisoformat(rate_info["updated_at"])
                if datetime.now() - updated_at < timedelta(minutes=5):
                    return rate_info["rate"]
            except (ValueError, KeyError):
                pass
    
    # Если курс устарел или отсутствует, используем mock данные
    mock_rates = {
        "EUR_USD": 1.0786,
        "BTC_USD": 59337.21,
        "RUB_USD": 0.01016,
        "ETH_USD": 3720.00,
        "USD_EUR": 0.927,
        "USD_BTC": 0.00001685,
        "USD_RUB": 98.42,
        "USD_ETH": 0.000268,
        "EUR_BTC": 0.000018,
        "BTC_EUR": 55555.55,
    }
    
    return mock_rates.get(rate_key)


def validate_currency_code(currency_code: str) -> bool:
    """Validate currency code format"""
    return (isinstance(currency_code, str) and 
            len(currency_code) == 3 and 
            currency_code.isalpha())


def validate_amount(amount: float) -> bool:
    """Validate amount is positive number"""
    try:
        return float(amount) > 0
    except (ValueError, TypeError):
        return False


def init_default_rates():
    """Initialize default exchange rates if rates file doesn't exist"""
    if not os.path.exists(RATES_FILE):
        default_rates = {
            "EUR_USD": {
                "rate": 1.0786,
                "updated_at": datetime.now().isoformat()
            },
            "BTC_USD": {
                "rate": 59337.21,
                "updated_at": datetime.now().isoformat()
            },
            "RUB_USD": {
                "rate": 0.01016,
                "updated_at": datetime.now().isoformat()
            },
            "ETH_USD": {
                "rate": 3720.00,
                "updated_at": datetime.now().isoformat()
            },
            "source": "MockData",
            "last_refresh": datetime.now().isoformat()
        }
        write_json(default_rates, RATES_FILE)


# Инициализируем курсы по умолчанию при импорте модуля
init_default_rates()