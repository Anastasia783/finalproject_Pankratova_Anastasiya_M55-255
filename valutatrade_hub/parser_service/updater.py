"""
Rates updater for Parser Service
"""

from typing import Dict
from valutatrade_hub.parser_service.api_clients import CoinGeckoClient, ExchangeRateApiClient
from valutatrade_hub.parser_service.storage import RatesStorage
from valutatrade_hub.parser_service.config import config
from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.logging_config import get_logger


logger = get_logger(__name__)


class RatesUpdater:
    """Orchestrates rates update from all sources"""
    
    def __init__(self):
        self.coingecko_client = CoinGeckoClient()
        self.exchangerate_client = ExchangeRateApiClient()
        self.storage = RatesStorage()
    
    def run_update(self, source: str = None) -> Dict[str, float]:
        """Run rates update from specified sources"""
        all_rates = {}
        
        logger.info("Starting rates update...")
        
        # Update from CoinGecko (crypto)
        if source is None or source == "coingecko":
            try:
                crypto_rates = self.coingecko_client.fetch_rates()
                all_rates.update(crypto_rates)
                
                # Save historical records for crypto
                for pair, rate in crypto_rates.items():
                    self.storage.save_historical_rate(
                        pair, rate, "CoinGecko", 
                        {"raw_id": config.CRYPTO_ID_MAP.get(pair.split("_")[0])}
                    )
                    
            except ApiRequestError as e:
                logger.error(f"Failed to update from CoinGecko: {str(e)}")
        
        # Update from ExchangeRate-API (fiat)
        if source is None or source == "exchangerate":
            try:
                fiat_rates = self.exchangerate_client.fetch_rates()
                all_rates.update(fiat_rates)
                
                # Save historical records for fiat
                for pair, rate in fiat_rates.items():
                    self.storage.save_historical_rate(pair, rate, "ExchangeRate-API")
                    
            except ApiRequestError as e:
                logger.error(f"Failed to update from ExchangeRate-API: {str(e)}")
        
        # Save current rates to cache
        if all_rates:
            source_str = source if source else "all"
            self.storage.save_rates(all_rates, source_str)
            logger.info(f"Rates update completed. Total rates: {len(all_rates)}")
        else:
            logger.warning("No rates were updated")
        
        return all_rates