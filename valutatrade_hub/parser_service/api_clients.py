import requests
from typing import Dict
from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import config
from valutatrade_hub.logging_config import get_logger


logger = get_logger(__name__)


class BaseApiClient:
    """Base class for API clients"""
    
    def fetch_rates(self) -> Dict[str, float]:
        """Fetch exchange rates from API"""
        raise NotImplementedError("Subclasses must implement fetch_rates method")


class CoinGeckoClient(BaseApiClient):
    """Client for CoinGecko API"""
    
    def fetch_rates(self) -> Dict[str, float]:
        """Fetch cryptocurrency rates from CoinGecko"""
        try:
            # Prepare crypto IDs for request
            crypto_ids = []
            for code in config.CRYPTO_CURRENCIES:
                if code in config.CRYPTO_ID_MAP:
                    crypto_ids.append(config.CRYPTO_ID_MAP[code])
            
            if not crypto_ids:
                logger.warning("No crypto currencies configured")
                return {}
            
            ids_param = ",".join(crypto_ids)
            
            url = f"{config.COINGECKO_URL}?ids={ids_param}&vs_currencies={config.BASE_CURRENCY.lower()}"
            
            logger.info(f"Fetching rates from CoinGecko: {url}")
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            rates = {}
            
            for crypto_code in config.CRYPTO_CURRENCIES:
                if crypto_code in config.CRYPTO_ID_MAP:
                    crypto_id = config.CRYPTO_ID_MAP[crypto_code]
                    if crypto_id in data and config.BASE_CURRENCY.lower() in data[crypto_id]:
                        rate = data[crypto_id][config.BASE_CURRENCY.lower()]
                        pair = f"{crypto_code}_{config.BASE_CURRENCY}"
                        rates[pair] = float(rate)
                        logger.debug(f"Fetched rate for {pair}: {rate}")
            
            logger.info(f"Successfully fetched {len(rates)} rates from CoinGecko")
            return rates
            
        except requests.exceptions.RequestException as e:
            error_msg = f"CoinGecko API request failed: {str(e)}"
            logger.error(error_msg)
            raise ApiRequestError(error_msg)
        except (KeyError, ValueError, TypeError) as e:
            error_msg = f"CoinGecko API response parsing failed: {str(e)}"
            logger.error(error_msg)
            raise ApiRequestError(error_msg)


class ExchangeRateApiClient(BaseApiClient):
    """Client for ExchangeRate-API"""
    
    def fetch_rates(self) -> Dict[str, float]:
        """Fetch fiat currency rates from ExchangeRate-API"""
        try:
            url = f"{config.EXCHANGERATE_API_URL}/{config.EXCHANGERATE_API_KEY}/latest/{config.BASE_CURRENCY}"
            
            logger.info(f"Fetching rates from ExchangeRate-API: {url}")
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            
            if response.status_code != 200:
                logger.warning(f"ExchangeRate-API returned status code: {response.status_code}, using demo rates")
                return self._get_demo_rates()
                
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("result") != "success":
                logger.warning(f"ExchangeRate-API error: {data.get('error-type', 'Unknown error')}, using demo rates")
                return self._get_demo_rates()
            
            rates = {}
            conversion_rates = data.get("conversion_rates", {})
            logger.info(f"Available currencies from ExchangeRate-API: {len(conversion_rates)} currencies")
            
            for currency in config.FIAT_CURRENCIES:
                if currency in conversion_rates:
                    rate = conversion_rates[currency]
                    # ExchangeRate-API returns rates for USD->target, so we store as target_USD
                    pair = f"{currency}_{config.BASE_CURRENCY}"
                    rates[pair] = float(rate)
                    logger.debug(f"Fetched rate for {pair}: {rate}")
                else:
                    logger.warning(f"Currency {currency} not found in ExchangeRate-API response")
            
            logger.info(f"Successfully fetched {len(rates)} rates from ExchangeRate-API")
            return rates
            
        except requests.exceptions.RequestException as e:
            error_msg = f"ExchangeRate-API request failed: {str(e)}"
            logger.warning(f"{error_msg}, using demo rates")
            return self._get_demo_rates()
        except (KeyError, ValueError, TypeError) as e:
            error_msg = f"ExchangeRate-API response parsing failed: {str(e)}"
            logger.warning(f"{error_msg}, using demo rates")
            return self._get_demo_rates()
        
    def _get_demo_rates(self) -> Dict[str, float]:
        """Return demo rates for testing when no API key is available"""
        demo_rates = {
            "EUR_USD": 1.0786,
            "GBP_USD": 1.2593,
            "JPY_USD": 0.0067,
            "CHF_USD": 1.1150,
            "RUB_USD": 0.01016
        }
        logger.info("Using demo rates for fiat currencies")
        return demo_rates