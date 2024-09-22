from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
import time
from collections import OrderedDict
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class AdvancedCache:
    def __init__(self, default_expiration: int = 3600, max_size: Optional[int] = None, similarity_threshold: float = 0.8):
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.default_expiration = default_expiration
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        logger.info(f"AdvancedCache initialized with default_expiration={default_expiration}, max_size={max_size}, similarity_threshold={similarity_threshold}")

    def set(self, key: str, value: Any, expiration: Optional[int] = None) -> None:
        if self.max_size and len(self.cache) >= self.max_size:
            removed_key, _ = self.cache.popitem(last=False)
            logger.debug(f"Cache full, removed oldest item with key: {removed_key}")
        
        expiration_time = time.time() + (expiration or self.default_expiration)
        self.cache[key] = {
            'value': value,
            'expiration': expiration_time
        }
        self.cache.move_to_end(key)
        logger.debug(f"Set key '{key}' with expiration {expiration_time}")

    def get(self, key: str, partial_match: bool = False) -> Optional[Tuple[Any, float]]:
        logger.debug(f"Attempting to get key '{key}' with partial_match={partial_match}")
        logger.debug(f"Current cache state: {self.cache}")
        
        if key in self.cache:
            item = self.cache[key]
            if time.time() < item['expiration']:
                self.cache.move_to_end(key)
                logger.debug(f"Exact match found for key '{key}'")
                return item['value'], 1.0
            else:
                del self.cache[key]
                logger.debug(f"Key '{key}' found but expired, removed from cache")
        
        if partial_match:
            best_match = None
            best_ratio = 0
            for cache_key in self.cache:
                ratio = SequenceMatcher(None, key, cache_key).ratio()
                logger.debug(f"Partial match check: key='{key}', cache_key='{cache_key}', ratio={ratio}, threshold={self.similarity_threshold}")
                if ratio > best_ratio and ratio >= self.similarity_threshold:
                    best_match = cache_key
                    best_ratio = ratio
            
            if best_match:
                item = self.cache[best_match]
                if time.time() < item['expiration']:
                    self.cache.move_to_end(best_match)
                    logger.debug(f"Partial match found: requested key='{key}', matched key='{best_match}', ratio={best_ratio}")
                    return item['value'], best_ratio
                else:
                    del self.cache[best_match]
                    logger.debug(f"Partial match found for key '{key}', but matched key '{best_match}' was expired")
            else:
                logger.debug(f"No partial match found above threshold {self.similarity_threshold}")
        
        logger.debug(f"No match found for key '{key}'")
        return None

    def remove_expired(self) -> None:
        current_time = time.time()
        expired_keys = [key for key, item in self.cache.items() if current_time >= item['expiration']]
        for key in expired_keys:
            del self.cache[key]
        logger.debug(f"Removed {len(expired_keys)} expired keys")

    def clear(self) -> None:
        self.cache.clear()
        logger.debug("Cache cleared")

    def size(self) -> int:
        return len(self.cache)

    def dump_state(self) -> Dict[str, Any]:
        return {
            'cache_contents': {k: v for k, v in self.cache.items()},
            'size': self.size(),
            'max_size': self.max_size,
            'default_expiration': self.default_expiration,
            'similarity_threshold': self.similarity_threshold
        }
