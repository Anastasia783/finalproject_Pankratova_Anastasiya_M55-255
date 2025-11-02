import hashlib
from datetime import datetime
from typing import Optional, Tuple
from .models import User, Portfolio, Wallet
from .utils import (
    read_json, write_json, generate_salt,
    USERS_FILE, PORTFOLIOS_FILE, RATES_FILE,
    validate_currency_code, validate_amount
)


class UserManager:
    @staticmethod
    def register_user(username: str, password: str) -> User:
        """Регистрация нового пользователя"""
        users_data = read_json(USERS_FILE)
        
        # Проверяем, существует ли username
        if any(user["username"] == username for user in users_data):
            raise ValueError(f"Имя пользователя '{username}' уже занято")
        
        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        
        # Генерируем user_id
        user_id = max([user["user_id"] for user in users_data], default=0) + 1
        
        # Создаем пользователя
        salt = generate_salt()
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        registration_date = datetime.now()
        
        user = User(user_id, username, hashed_password, salt, registration_date)
        
        # Сохраняем пользователя
        users_data.append(user.to_dict())
        write_json(users_data, USERS_FILE)
        
        # Создаем пустой портфель
        portfolio_manager = PortfolioManager()
        portfolio_manager.create_portfolio(user_id)
        
        return user

    @staticmethod
    def login_user(username: str, password: str) -> User:
        """Вход пользователя в систему"""
        users_data = read_json(USERS_FILE)
        
        # Ищем пользователя
        user_data = next((user for user in users_data if user["username"] == username), None)
        if not user_data:
            raise ValueError(f"Пользователь '{username}' не найден")
        
        user = User.from_dict(user_data)
        
        # Проверяем пароль
        if not user.verify_password(password):
            raise ValueError("Неверный пароль")
        
        return user

    @staticmethod
    def find_user_by_id(user_id: int) -> Optional[User]:
        """Найти пользователя по ID"""
        users_data = read_json(USERS_FILE)
        user_data = next((user for user in users_data if user["user_id"] == user_id), None)
        return User.from_dict(user_data) if user_data else None


class PortfolioManager:
    @staticmethod
    def create_portfolio(user_id: int) -> Portfolio:
        """Создать пустой портфель для пользователя"""
        portfolios_data = read_json(PORTFOLIOS_FILE)
        
        # Проверяем, существует ли портфель
        if any(portfolio["user_id"] == user_id for portfolio in portfolios_data):
            raise ValueError(f"Портфель для пользователя {user_id} уже существует")
        
        portfolio = Portfolio(user_id)
        
        # Сохраняем портфель
        portfolios_data.append(portfolio.to_dict())
        write_json(portfolios_data, PORTFOLIOS_FILE)
        
        return portfolio

    @staticmethod
    def get_portfolio(user_id: int) -> Portfolio:
        """Получить портфель пользователя"""
        portfolios_data = read_json(PORTFOLIOS_FILE)
        
        portfolio_data = next(
            (portfolio for portfolio in portfolios_data if portfolio["user_id"] == user_id), 
            None
        )
        
        if not portfolio_data:
            # Создаем портфель, если его нет
            return PortfolioManager.create_portfolio(user_id)
        
        return Portfolio.from_dict(portfolio_data)

    @staticmethod
    def save_portfolio(portfolio: Portfolio) -> None:
        """Сохранить портфель"""
        portfolios_data = read_json(PORTFOLIOS_FILE)
        
        # Ищем существующий портфель
        for i, portfolio_data in enumerate(portfolios_data):
            if portfolio_data["user_id"] == portfolio.user_id:
                portfolios_data[i] = portfolio.to_dict()
                break
        else:
            # Если не нашли, добавляем новый
            portfolios_data.append(portfolio.to_dict())
        
        write_json(portfolios_data, PORTFOLIOS_FILE)

    @staticmethod
    def buy_currency(user_id: int, currency: str, amount: float) -> Tuple[float, float]:
        """Покупка валюты"""
        if not validate_amount(amount):
            raise ValueError("'amount' должен быть положительным числом")
        
        currency = currency.upper()
        
        # Получаем портфель
        portfolio = PortfolioManager.get_portfolio(user_id)
        
        # Добавляем валюту, если ее нет
        if currency not in portfolio.wallets:
            portfolio.add_currency(currency)
        
        # Получаем кошелек
        wallet = portfolio.get_wallet(currency)
        if not wallet:
            raise ValueError(f"Не удалось создать кошелек для {currency}")
        
        # Получаем курс для расчета стоимости
        from .utils import get_exchange_rate
        rate = get_exchange_rate(currency, "USD")
        if not rate:
            raise ValueError(f"Не удалось получить курс для {currency}→USD")
        
        # Запоминаем старый баланс
        old_balance = wallet.balance
        
        # Пополняем кошелек
        wallet.deposit(amount)
        
        # Сохраняем изменения
        PortfolioManager.save_portfolio(portfolio)
        
        estimated_cost = amount * rate
        return old_balance, estimated_cost

    @staticmethod
    def sell_currency(user_id: int, currency: str, amount: float) -> Tuple[float, float]:
        """Продажа валюты"""
        if not validate_amount(amount):
            raise ValueError("'amount' должен быть положительным числом")
        
        currency = currency.upper()
        
        # Получаем портфель
        portfolio = PortfolioManager.get_portfolio(user_id)
        
        # Проверяем существование кошелька
        wallet = portfolio.get_wallet(currency)
        if not wallet:
            raise ValueError(f"У вас нет кошелька '{currency}'. Добавьте валюту: она создаётся автоматически при первой покупке.")
        
        # Проверяем достаточно ли средств
        if amount > wallet.balance:
            raise ValueError(f"Недостаточно средств: доступно {wallet.balance:.4f} {currency}, требуется {amount:.4f} {currency}")
        
        # Получаем курс для расчета выручки
        from .utils import get_exchange_rate
        rate = get_exchange_rate(currency, "USD")
        if not rate:
            raise ValueError(f"Не удалось получить курс для {currency}→USD")
        
        # Запоминаем старый баланс
        old_balance = wallet.balance
        
        # Снимаем средства
        wallet.withdraw(amount)
        
        # Сохраняем изменения
        PortfolioManager.save_portfolio(portfolio)
        
        estimated_revenue = amount * rate
        return old_balance, estimated_revenue


class RateManager:
    @staticmethod
    def get_rate(from_currency: str, to_currency: str) -> Tuple[float, str]:
        """Получить курс валюты"""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if not from_currency or not to_currency:
            raise ValueError("Коды валют не могут быть пустыми")
        
        if from_currency == to_currency:
            raise ValueError("Исходная и целевая валюта не могут быть одинаковыми")
        
        from .utils import get_exchange_rate
        rate = get_exchange_rate(from_currency, to_currency)
        
        if not rate:
            raise ValueError(f"Курс {from_currency}→{to_currency} недоступен. Повторите попытку позже.")
        
        # Получаем время обновления
        rates_data = read_json(RATES_FILE)
        rate_key = f"{from_currency}_{to_currency}"
        updated_at = rates_data.get(rate_key, {}).get("updated_at", "неизвестно")
        
        return rate, updated_at

