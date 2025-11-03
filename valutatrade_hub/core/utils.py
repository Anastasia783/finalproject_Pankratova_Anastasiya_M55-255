import json
import os
from typing import Any, List, Dict, Optional


# Правильные пути для Windows
DATA_DIR = "data"


def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def get_data_path(filename: str) -> str:
    """Get full path to data file (Windows compatible)"""
    return os.path.join(DATA_DIR, filename)


def load_session() -> Optional[int]:
    """Load current user ID from session"""
    ensure_data_dir()
    try:
        with open(get_data_path("session.json"), "r", encoding="utf-8") as f:
            session_data = json.load(f)
            return session_data.get("user_id")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_session(user_id: int):
    """Save user session"""
    ensure_data_dir()
    with open(get_data_path("session.json"), "w", encoding="utf-8") as f:
        json.dump({"user_id": user_id}, f, indent=2, ensure_ascii=False)


def clear_session():
    """Clear user session"""
    ensure_data_dir()
    try:
        os.remove(get_data_path("session.json"))
    except FileNotFoundError:
        pass


def load_users() -> List[Dict[str, Any]]:
    """Load users from JSON file"""
    ensure_data_dir()
    try:
        with open(get_data_path("users.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_users(users: List[Dict[str, Any]]):
    """Save users to JSON file"""
    ensure_data_dir()
    with open(get_data_path("users.json"), "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def load_portfolios() -> List[Dict[str, Any]]:
    """Load portfolios from JSON file"""
    ensure_data_dir()
    try:
        with open(get_data_path("portfolios.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_portfolios(portfolios: List[Dict[str, Any]]):
    """Save portfolios to JSON file"""
    ensure_data_dir()
    with open(get_data_path("portfolios.json"), "w", encoding="utf-8") as f:
        json.dump(portfolios, f, indent=2, ensure_ascii=False)


def load_rates() -> Dict[str, Any]:
    """Load exchange rates from JSON file"""
    ensure_data_dir()
    try:
        with open(get_data_path("rates.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_rates(rates: Dict[str, Any]):
    """Save exchange rates to JSON file"""
    ensure_data_dir()
    with open(get_data_path("rates.json"), "w", encoding="utf-8") as f:
        json.dump(rates, f, indent=2, ensure_ascii=False)


def validate_currency_code(currency_code: str) -> bool:
    """Validate currency code format"""
    return (isinstance(currency_code, str) and 
            len(currency_code) == 3 and 
            currency_code.isalpha() and 
            currency_code.isupper())


def get_next_user_id() -> int:
    """Get next available user ID"""
    users = load_users()
    if not users:
        return 1
    return max(user["user_id"] for user in users) + 1