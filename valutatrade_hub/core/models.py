import hashlib
import json
from datetime import datetime
from typing import Dict, Optional


class User:
    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str,
        salt: str,
        registration_date: datetime,
    ):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Username cannot be empty")
        self._username = value

    @property
    def hashed_password(self) -> str:
        return self._hashed_password

    def get_user_info(self) -> str:
        return (
            f"User ID: {self._user_id}, "
            f"Username: {self._username}, "
            f"Registered: {self._registration_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def change_password(self, new_password: str) -> None:
        if len(new_password) < 4:
            raise ValueError("Password must be at least 4 characters long")
        self._hashed_password = self._hash_password(new_password)

    def verify_password(self, password: str) -> bool:
        return self._hashed_password == self._hash_password(password)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256((password + self._salt).encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            salt=data["salt"],
            registration_date=datetime.fromisoformat(data["registration_date"]),
        )


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code.upper()
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            raise ValueError("Balance cannot be negative")
        if not isinstance(value, (int, float)):
            raise TypeError("Balance must be a number")
        self._balance = float(value)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError(f"Insufficient funds. Available: {self.balance}, required: {amount}")
        self.balance -= amount

    def get_balance_info(self) -> str:
        return f"{self.currency_code}: {self.balance:.4f}"

    def to_dict(self) -> dict:
        return {
            "currency_code": self.currency_code,
            "balance": self._balance,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Wallet":
        return cls(
            currency_code=data["currency_code"],
            balance=data["balance"],
        )


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

    def add_currency(self, currency_code: str) -> None:
        currency_code = currency_code.upper()
        if currency_code in self._wallets:
            raise ValueError(f"Wallet for {currency_code} already exists")
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Optional[Wallet]:
        return self._wallets.get(currency_code.upper())

    def get_total_value(self, base_currency: str = "USD") -> float:
        # Импортируем здесь, чтобы избежать циклических импортов
        from .utils import get_exchange_rate
        
        total = 0.0
        base_currency = base_currency.upper()
        
        for currency, wallet in self._wallets.items():
            if currency == base_currency:
                total += wallet.balance
            else:
                rate = get_exchange_rate(currency, base_currency)
                if rate is not None:
                    total += wallet.balance * rate
                else:
                    print(f"Warning: Could not get exchange rate for {currency} -> {base_currency}")
        
        return total

    def to_dict(self) -> dict:
        return {
            "user_id": self._user_id,
            "wallets": {
                currency: wallet.to_dict()
                for currency, wallet in self._wallets.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Portfolio":
        wallets = {
            currency: Wallet.from_dict(wallet_data)
            for currency, wallet_data in data["wallets"].items()
        }
        return cls(user_id=data["user_id"], wallets=wallets)