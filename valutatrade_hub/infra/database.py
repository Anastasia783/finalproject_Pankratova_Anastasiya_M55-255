import json
import os
import threading
from typing import Any, List, Dict
from valutatrade_hub.infra.settings import settings


class DatabaseManager:
    """Singleton class for database operations"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.data_dir = settings.get("data_dir", "data")
            self._ensure_data_dir()
            self._initialized = True
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_file_path(self, filename: str) -> str:
        """Get full path to data file"""
        return os.path.join(self.data_dir, filename)
    
    def load_users(self) -> List[Dict[str, Any]]:
        """Load users from JSON file"""
        try:
            with open(self._get_file_path("users.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_users(self, users: List[Dict[str, Any]]):
        """Save users to JSON file"""
        with open(self._get_file_path("users.json"), "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    def load_portfolios(self) -> List[Dict[str, Any]]:
        """Load portfolios from JSON file"""
        try:
            with open(self._get_file_path("portfolios.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_portfolios(self, portfolios: List[Dict[str, Any]]):
        """Save portfolios to JSON file"""
        with open(self._get_file_path("portfolios.json"), "w", encoding="utf-8") as f:
            json.dump(portfolios, f, indent=2, ensure_ascii=False)
    
    def load_rates(self) -> Dict[str, Any]:
        """Load exchange rates from JSON file"""
        try:
            with open(self._get_file_path("rates.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_rates(self, rates: Dict[str, Any]):
        """Save exchange rates to JSON file"""
        # Atomic write using temporary file
        temp_file = self._get_file_path("rates.json.tmp")
        final_file = self._get_file_path("rates.json")
        
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(rates, f, indent=2, ensure_ascii=False)
        
        os.replace(temp_file, final_file)
    
    def load_session(self) -> Dict[str, Any]:
        """Load session data"""
        try:
            with open(self._get_file_path("session.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_session(self, session_data: Dict[str, Any]):
        """Save session data"""
        with open(self._get_file_path("session.json"), "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def clear_session(self):
        """Clear session data"""
        try:
            os.remove(self._get_file_path("session.json"))
        except FileNotFoundError:
            pass


# Global instance
db = DatabaseManager()