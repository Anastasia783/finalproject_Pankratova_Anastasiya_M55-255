
from typing import Optional, Tuple
from datetime import datetime, timedelta
from valutatrade_hub.core.models import User, Portfolio, Wallet
from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.exceptions import CurrencyNotFoundError, InsufficientFundsError, ApiRequestError
from valutatrade_hub.infra.database import db
from valutatrade_hub.infra.settings import settings
from valutatrade_hub.decorators import log_action
from valutatrade_hub.logging_config import get_logger


logger = get_logger(__name__)


class UserManager:
    """Manages user registration and authentication"""
    
    def __init__(self):
        self.current_user: Optional[User] = None
        self._load_session()
    
    def _load_session(self):
        """Load user session if exists"""
        session_data = db.load_session()
        user_id = session_data.get("user_id")
        if user_id:
            users = db.load_users()
            for user_data in users:
                if user_data["user_id"] == user_id:
                    self.current_user = self._create_user_from_data(user_data)
                    break
    
    def _create_user_from_data(self, user_data: dict) -> User:
        """Create User object from stored data without password validation"""
        user = User.__new__(User)
        user._user_id = user_data["user_id"]
        user._username = user_data["username"]
        user._salt = user_data["salt"]
        user._hashed_password = user_data["hashed_password"]
        user._registration_date = datetime.fromisoformat(user_data["registration_date"])
        return user
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Register a new user"""
        try:
            # Check if username already exists
            users = db.load_users()
            if any(user["username"] == username for user in users):
                return False, f"Username '{username}' is already taken"
            
            # Create new user
            user_id = self._get_next_user_id()
            user = User(user_id, username, password)
            
            # Save user
            users.append(user.to_dict())
            db.save_users(users)
            
            # Create empty portfolio for user
            portfolios = db.load_portfolios()
            portfolios.append({
                "user_id": user_id,
                "wallets": {}
            })
            db.save_portfolios(portfolios)
            
            logger.info(f"User registered: {username} (id={user_id})")
            return True, f"User '{username}' registered successfully (id={user_id})"
            
        except Exception as e:
            logger.error(f"Registration failed for {username}: {str(e)}")
            return False, f"Registration failed: {str(e)}"
    
    def _get_next_user_id(self) -> int:
        """Get next available user ID"""
        users = db.load_users()
        if not users:
            return 1
        return max(user["user_id"] for user in users) + 1
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Authenticate user"""
        try:
            users = db.load_users()
            for user_data in users:
                if user_data["username"] == username:
                    # Create user from stored data with password verification
                    user = User(
                        user_data["user_id"],
                        user_data["username"],
                        password,
                        user_data["salt"],
                        user_data["registration_date"]
                    )
                    # Set the stored hash for verification
                    user._hashed_password = user_data["hashed_password"]
                    
                    if user.verify_password(password):
                        self.current_user = user
                        db.save_session({"user_id": user.user_id})
                        logger.info(f"User logged in: {username}")
                        return True, f"Logged in as '{username}'"
                    else:
                        logger.warning(f"Failed login attempt for {username}: invalid password")
                        return False, "Invalid password"
            
            logger.warning(f"Failed login attempt: user {username} not found")
            return False, f"User '{username}' not found"
            
        except Exception as e:
            logger.error(f"Login failed for {username}: {str(e)}")
            return False, f"Login failed: {str(e)}"
    
    def logout(self) -> None:
        """Logout current user"""
        if self.current_user:
            logger.info(f"User logged out: {self.current_user.username}")
        db.clear_session()
        self.current_user = None
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.current_user is not None


class PortfolioManager:
    """Manages portfolio operations"""
    
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
    
    def get_user_portfolio(self) -> Optional[Portfolio]:
        """Get portfolio for current user"""
        if not self.user_manager.is_logged_in():
            return None
        
        portfolios = db.load_portfolios()
        user_id = self.user_manager.current_user.user_id
        
        for portfolio_data in portfolios:
            if portfolio_data["user_id"] == user_id:
                wallets = {}
                for currency, wallet_data in portfolio_data["wallets"].items():
                    wallets[currency] = Wallet(
                        wallet_data["currency_code"],
                        wallet_data["balance"]
                    )
                return Portfolio(user_id, wallets)
        
        # Create empty portfolio if not found
        return Portfolio(user_id)
    
    def save_portfolio(self, portfolio: Portfolio) -> bool:
        """Save portfolio to storage"""
        try:
            portfolios = db.load_portfolios()
            user_id = portfolio.user_id
            
            # Remove existing portfolio for user
            portfolios = [p for p in portfolios if p["user_id"] != user_id]
            
            # Add updated portfolio
            portfolios.append(portfolio.to_dict())
            db.save_portfolios(portfolios)
            return True
            
        except Exception as e:
            logger.error(f"Failed to save portfolio for user {user_id}: {str(e)}")
            return False


class TradingService:
    """Handles trading operations"""
    
    def __init__(self, user_manager: UserManager, portfolio_manager: PortfolioManager):
        self.user_manager = user_manager
        self.portfolio_manager = portfolio_manager
    
    def _get_cached_rate(self, from_currency: str, to_currency: str) -> Tuple[Optional[float], Optional[datetime]]:
        """Get cached exchange rate with timestamp"""
        rates = db.load_rates()
        pairs = rates.get("pairs", {})
        
        # Try direct pair
        pair = f"{from_currency}_{to_currency}"
        if pair in pairs:
            rate_data = pairs[pair]
            updated_at = datetime.fromisoformat(rate_data["updated_at"])
            return rate_data.get("rate"), updated_at
        
        # Try reverse pair
        reverse_pair = f"{to_currency}_{from_currency}"
        if reverse_pair in pairs:
            rate_data = pairs[reverse_pair]
            updated_at = datetime.fromisoformat(rate_data["updated_at"])
            return 1 / rate_data.get("rate"), updated_at
        
        # Try using USD as intermediate currency
        if from_currency != "USD" and to_currency != "USD":
            usd_to_from = None
            usd_to_to = None
            
            from_usd_pair = f"{from_currency}_USD"
            to_usd_pair = f"{to_currency}_USD"
            
            if from_usd_pair in pairs:
                usd_to_from = pairs[from_usd_pair].get("rate")
            if to_usd_pair in pairs:
                usd_to_to = pairs[to_usd_pair].get("rate")
            
            if usd_to_from and usd_to_to:
                # Calculate cross rate: (USD/TO) / (USD/FROM) = FROM/TO
                calculated_rate = usd_to_to / usd_to_from
                return calculated_rate, datetime.now()
        
        return None, None
    
    def _is_rate_fresh(self, updated_at: datetime) -> bool:
        """Check if rate is still fresh based on TTL"""
        ttl_seconds = settings.get("rates_ttl_seconds", 300)
        return datetime.now() - updated_at < timedelta(seconds=ttl_seconds)
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Tuple[Optional[float], Optional[datetime]]:
        """Get exchange rate between two currencies"""
        # Validate currencies
        try:
            get_currency(from_currency)
            get_currency(to_currency)
        except CurrencyNotFoundError as e:
            raise e
        
        # Try to get cached rate
        rate, updated_at = self._get_cached_rate(from_currency, to_currency)
        
        if rate and updated_at and self._is_rate_fresh(updated_at):
            return rate, updated_at
        
        # Rate is stale or not found - try to update from Parser Service
        try:
            from valutatrade_hub.parser_service.updater import RatesUpdater
            updater = RatesUpdater()
            logger.info("Rates not found in cache, updating from Parser Service...")
            updater.run_update()
            
            # Try again after update
            rate, updated_at = self._get_cached_rate(from_currency, to_currency)
            if rate and updated_at:
                logger.info(f"Successfully retrieved rate after update: {rate}")
                return rate, updated_at
            else:
                raise ApiRequestError(f"Rate for {from_currency}->{to_currency} not available after update")
                
        except ImportError:
            # Parser Service not available
            raise ApiRequestError("Parser Service not available")
        except Exception as e:
            raise ApiRequestError(f"Failed to update rates: {str(e)}")
    
    @log_action(verbose=True)
    def buy_currency(self, currency: str, amount: float) -> Tuple[bool, str]:
        """Buy currency operation"""
        if not self.user_manager.is_logged_in():
            return False, "Please login first"
        
        try:
            # Validate currency
            get_currency(currency)
            
            if amount <= 0:
                return False, "Amount must be positive"
            
            portfolio = self.portfolio_manager.get_user_portfolio()
            if portfolio is None:
                return False, "Portfolio not found"
            
            # Get or create wallet for target currency
            target_wallet = portfolio.get_wallet(currency)
            if target_wallet is None:
                portfolio.add_currency(currency)
                target_wallet = portfolio.get_wallet(currency)
            
            # Calculate estimated cost in base currency
            base_currency = settings.get("default_base_currency", "USD")
            try:
                rate, _ = self.get_exchange_rate(currency, base_currency)
                estimated_cost = amount * rate if rate else None
            except (ApiRequestError, CurrencyNotFoundError):
                estimated_cost = None
            
            # Execute buy operation
            target_wallet.deposit(amount)
            
            # Save changes
            self.portfolio_manager.save_portfolio(portfolio)
            
            message = f"Successfully bought {amount} {currency}"
            if estimated_cost:
                message += f" (estimated cost: {estimated_cost:.2f} {base_currency})"
            
            return True, message
            
        except CurrencyNotFoundError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Buy operation failed: {str(e)}"
    
    @log_action(verbose=True)
    def sell_currency(self, currency: str, amount: float) -> Tuple[bool, str]:
        """Sell currency operation"""
        if not self.user_manager.is_logged_in():
            return False, "Please login first"
        
        try:
            # Validate currency
            get_currency(currency)
            
            if amount <= 0:
                return False, "Amount must be positive"
            
            portfolio = self.portfolio_manager.get_user_portfolio()
            if portfolio is None:
                return False, "Portfolio not found"
            
            target_wallet = portfolio.get_wallet(currency)
            if target_wallet is None:
                return False, f"No wallet found for currency: {currency}"
            
            # Check sufficient funds
            if amount > target_wallet.balance:
                raise InsufficientFundsError(currency, target_wallet.balance, amount)
            
            # Calculate estimated revenue in base currency
            base_currency = settings.get("default_base_currency", "USD")
            try:
                rate, _ = self.get_exchange_rate(currency, base_currency)
                estimated_revenue = amount * rate if rate else None
            except (ApiRequestError, CurrencyNotFoundError):
                estimated_revenue = None
            
            # Execute sell operation
            target_wallet.withdraw(amount)
            
            # Save changes
            self.portfolio_manager.save_portfolio(portfolio)
            
            message = f"Successfully sold {amount} {currency}"
            if estimated_revenue:
                message += f" (estimated revenue: {estimated_revenue:.2f} {base_currency})"
            
            return True, message
            
        except (CurrencyNotFoundError, InsufficientFundsError) as e:
            return False, str(e)
        except Exception as e:
            return False, f"Sell operation failed: {str(e)}"


# Global instances
user_manager = UserManager()
portfolio_manager = PortfolioManager(user_manager)
trading_service = TradingService(user_manager, portfolio_manager)