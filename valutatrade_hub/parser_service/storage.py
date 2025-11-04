"""
Storage operations for Parser Service
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
from valutatrade_hub.parser_service.config import config
from valutatrade_hub.logging_config import get_logger


logger = get_logger(__name__)


class RatesStorage:
    """Handles reading and writing rates data"""
    
    @staticmethod
    def save_rates(rates: Dict[str, float], source: str) -> bool:
        """Save current rates to rates.json (cache for Core Service)"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(config.RATES_FILE_PATH), exist_ok=True)
            
            # Prepare rates data
            rates_data = {
                "pairs": {},
                "last_refresh": datetime.now().isoformat()
            }
            
            for pair, rate in rates.items():
                rates_data["pairs"][pair] = {
                    "rate": rate,
                    "updated_at": datetime.now().isoformat(),
                    "source": source
                }
            
            # Atomic write using temporary file
            temp_file = config.RATES_FILE_PATH + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(rates_data, f, indent=2, ensure_ascii=False)
            
            os.replace(temp_file, config.RATES_FILE_PATH)
            
            logger.info(f"Saved {len(rates)} rates to {config.RATES_FILE_PATH}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save rates: {str(e)}")
            return False
    
    @staticmethod
    def save_historical_rate(pair: str, rate: float, source: str, meta: Dict[str, Any] = None):
        """Save historical rate to exchange_rates.json"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(config.HISTORY_FILE_PATH), exist_ok=True)
            
            # Load existing history
            history = RatesStorage.load_history()
            
            # Create new record
            record_id = f"{pair}_{datetime.now().isoformat()}"
            record = {
                "id": record_id,
                "from_currency": pair.split("_")[0],
                "to_currency": pair.split("_")[1],
                "rate": rate,
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "meta": meta or {}
            }
            
            history.append(record)
            
            # Save history
            with open(config.HISTORY_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved historical rate for {pair}")
            
        except Exception as e:
            logger.error(f"Failed to save historical rate: {str(e)}")
    
    @staticmethod
    def load_history() -> List[Dict[str, Any]]:
        """Load historical rates from exchange_rates.json"""
        try:
            with open(config.HISTORY_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    @staticmethod
    def load_rates() -> Dict[str, Any]:
        """Load current rates from rates.json"""
        try:
            with open(config.RATES_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"pairs": {}, "last_refresh": None}