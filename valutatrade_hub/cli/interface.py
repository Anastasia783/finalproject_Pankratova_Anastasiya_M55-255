import argparse
import sys
from valutatrade_hub.core.usecases import user_manager, trading_service, portfolio_manager
from valutatrade_hub.core.currencies import get_currency, get_all_currencies, CurrencyNotFoundError
from valutatrade_hub.core.exceptions import InsufficientFundsError, ApiRequestError, ValutaTradeError
from valutatrade_hub.logging_config import get_logger


logger = get_logger(__name__)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="ValutaTrade Hub - Currency Trading Platform")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register new user")
    register_parser.add_argument("--username", required=True, help="Username")
    register_parser.add_argument("--password", required=True, help="Password")
    
    # Login command
    login_parser = subparsers.add_parser("login", help="Login to system")
    login_parser.add_argument("--username", required=True, help="Username")
    login_parser.add_argument("--password", required=True, help="Password")
    
    # Logout command
    subparsers.add_parser("logout", help="Logout from system")
    
    # Show portfolio command
    portfolio_parser = subparsers.add_parser("show-portfolio", help="Show user portfolio")
    portfolio_parser.add_argument("--base", default="USD", help="Base currency for valuation")
    
    # Buy command
    buy_parser = subparsers.add_parser("buy", help="Buy currency")
    buy_parser.add_argument("--currency", required=True, help="Currency to buy")
    buy_parser.add_argument("--amount", type=float, required=True, help="Amount to buy")
    
    # Sell command
    sell_parser = subparsers.add_parser("sell", help="Sell currency")
    sell_parser.add_argument("--currency", required=True, help="Currency to sell")
    sell_parser.add_argument("--amount", type=float, required=True, help="Amount to sell")
    
    # Get rate command
    rate_parser = subparsers.add_parser("get-rate", help="Get exchange rate")
    rate_parser.add_argument("--from", required=True, dest="from_currency", help="Source currency")
    rate_parser.add_argument("--to", required=True, dest="to_currency", help="Target currency")
    
    # List currencies command
    subparsers.add_parser("list-currencies", help="List all supported currencies")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "register":
            success, message = user_manager.register_user(args.username, args.password)
            print(message)
        
        elif args.command == "login":
            success, message = user_manager.login_user(args.username, args.password)
            print(message)
        
        elif args.command == "logout":
            user_manager.logout()
            print("Logged out successfully")
        
        elif args.command == "show-portfolio":
            if not user_manager.is_logged_in():
                print("Please login first")
                return
            
            portfolio = portfolio_manager.get_user_portfolio()
            if portfolio and portfolio.wallets:
                print(f"Portfolio for user '{user_manager.current_user.username}':")
                for currency, wallet in portfolio.wallets.items():
                    try:
                        currency_info = get_currency(currency)
                        print(f"- {currency_info.get_display_info()}: {wallet.balance:.4f}")
                    except CurrencyNotFoundError:
                        print(f"- {currency}: {wallet.balance:.4f} (unknown currency)")
                
                total_value = portfolio.get_total_value(args.base)
                print(f"Total value: {total_value:.2f} {args.base}")
            else:
                print("Portfolio is empty")
        
        elif args.command == "buy":
            success, message = trading_service.buy_currency(args.currency.upper(), args.amount)
            print(message)
        
        elif args.command == "sell":
            success, message = trading_service.sell_currency(args.currency.upper(), args.amount)
            print(message)
        
        elif args.command == "get-rate":
            try:
                rate, updated_at = trading_service.get_exchange_rate(
                    args.from_currency.upper(), 
                    args.to_currency.upper()
                )
                if rate:
                    print(f"Exchange rate {args.from_currency}→{args.to_currency}: {rate:.6f}")
                    if updated_at:
                        print(f"Last updated: {updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"Rate not available for {args.from_currency}→{args.to_currency}")
            
            except CurrencyNotFoundError as e:
                print(str(e))
                print("Use 'list-currencies' command to see available currencies.")
            
            except ApiRequestError as e:
                print(str(e))
                print("Please try again later or check your network connection.")
        
        elif args.command == "list-currencies":
            currencies = get_all_currencies()
            if currencies:
                print("Supported currencies:")
                for code, currency in currencies.items():
                    print(f"  {currency.get_display_info()}")
            else:
                print("No currencies registered")
    
    except ValutaTradeError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in CLI: {str(e)}")
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()