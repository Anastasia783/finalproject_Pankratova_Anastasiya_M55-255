import hashlib
import secrets
from datetime import datetime
from typing import Dict


class User:
    def __init__(self, user_id: int, username: str, password: str, salt: str = None, registration_date: str = None):
        self._user_id = user_id
        self._username = username
        self._salt = salt or secrets.token_hex(16)
        self._hashed_password = self._hash_password(password)
        
        if registration_date:
            self._registration_date = datetime.fromisoformat(registration_date)
        else:
            self._registration_date = datetime.now()
    
    @property
    def user_id(self) -> int:
        return self._user_id
    
    @property
    def username(self) -> str:
        return self._username
    
    @username.setter
    def username(self, value: str):
        if not value or not value.strip():
            raise ValueError("Username cannot be empty")
        self._username = value.strip()
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt using SHA-256"""
        if len(password) < 4:
            raise ValueError("Password must be at least 4 characters long")
        return hashlib.sha256((password + self._salt).encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify if password matches the stored hash"""
        return self._hashed_password == self._hash_password(password)
    
    def change_password(self, new_password: str):
        """Change user password"""
        self._hashed_password = self._hash_password(new_password)
    
    def get_user_info(self) -> dict:
        """Get user information without password"""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for JSON storage"""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat()
        }


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self._balance = balance
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)):
            raise ValueError("Balance must be a number")
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = float(value)
    
    def deposit(self, amount: float):
        """Deposit funds to wallet"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
    
    def withdraw(self, amount: float):
        """Withdraw funds from wallet"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError(f"Insufficient funds. Available: {self.balance}")
        self.balance -= amount
    
    def get_balance_info(self) -> dict:
        """Get wallet balance information"""
        return {
            "currency_code": self.currency_code,
            "balance": self._balance
        }


class Portfolio:
    def __init__(self, user_id: int, wallets: Dict[str, Wallet] = None):
        self._user_id = user_id
        self._wallets = wallets or {}
    
    @property
    def user_id(self) -> int:
        return self._user_id
    
    @property
    def wallets(self) -> Dict[str, Wallet]:
        return self._wallets.copy()
    
    def add_currency(self, currency_code: str):
        """Add new currency wallet to portfolio"""
        if currency_code in self._wallets:
            raise ValueError(f"Currency {currency_code} already exists in portfolio")
        self._wallets[currency_code] = Wallet(currency_code)
    
    def get_wallet(self, currency_code: str) -> Wallet:
        """Get wallet by currency code"""
        return self._wallets.get(currency_code)
    
    def get_total_value(self, base_currency: str = "USD") -> float:
        """Calculate total portfolio value in base currency"""
        total = 0.0
        for wallet in self._wallets.values():
            total += wallet.balance
        return total
    
    def to_dict(self) -> dict:
        """Convert portfolio to dictionary for JSON storage"""
        wallets_dict = {}
        for currency, wallet in self._wallets.items():
            wallets_dict[currency] = {
                "currency_code": wallet.currency_code,
                "balance": wallet.balance
            }
        return {
            "user_id": self._user_id,
            "wallets": wallets_dict
        }