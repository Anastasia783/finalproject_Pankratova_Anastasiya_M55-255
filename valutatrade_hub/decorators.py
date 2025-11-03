import functools
import time
from typing import Any, Callable, Optional
from valutatrade_hub.logging_config import get_logger


logger = get_logger(__name__)


def log_action(verbose: bool = False):
    """
    Decorator for logging domain operations
    
    Args:
        verbose: If True, log additional context information
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Extract operation context
            action = func.__name__.upper()
            username = "unknown"
            currency_code = kwargs.get('currency') or kwargs.get('currency_code')
            amount = kwargs.get('amount')
            
            # Try to extract user info from args (usually self or first arg)
            if args and hasattr(args[0], 'user_manager'):
                user_manager = args[0].user_manager
                if user_manager.is_logged_in():
                    username = user_manager.current_user.username
            
            start_time = time.time()
            result_status = "OK"
            error_info = None
            extra_context = {}
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Log success with optional verbose context
                if verbose and hasattr(args[0], 'portfolio_manager'):
                    portfolio = args[0].portfolio_manager.get_user_portfolio()
                    if portfolio and currency_code:
                        wallet = portfolio.get_wallet(currency_code)
                        if wallet:
                            extra_context = {f"{currency_code}_balance": wallet.balance}
                
                return result
                
            except Exception as e:
                result_status = "ERROR"
                error_info = {
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                raise  # Re-raise the exception
            
            finally:
                # Log the action
                log_data = {
                    "action": action,
                    "username": username,
                    "currency_code": currency_code,
                    "amount": amount,
                    "result": result_status,
                    "duration_ms": round((time.time() - start_time) * 1000, 2)
                }
                
                if error_info:
                    log_data.update(error_info)
                
                if extra_context:
                    log_data.update(extra_context)
                
                if result_status == "OK":
                    logger.info("Operation completed", extra=log_data)
                else:
                    logger.error("Operation failed", extra=log_data)
        
        return wrapper
    return decorator