from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
import time
from collections import OrderedDict
from difflib import SequenceMatcher

class AdvancedCache:
    def __init__(self, default_expiration: int = 3600, max_size: Optional[int] = None, similarity_threshold: float = 0.8):
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.default_expiration = default_expiration
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold

    def set(self, key: str, value: Any, expiration: Optional[int] = None) -> None:
        if self.max_size and len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        expiration_time = time.time() + (expiration or self.default_expiration)
        self.cache[key] = {
            'value': value,
            'expiration': expiration_time
        }
        self.cache.move_to_end(key)

    def get(self, key: str, partial_match: bool = False) -> Optional[Tuple[Any, float]]:
        if key in self.cache:
            item = self.cache[key]
            if time.time() < item['expiration']:
                self.cache.move_to_end(key)
                return item['value'], 1.0
            else:
                del self.cache[key]
        
        if partial_match:
            best_match = None
            best_ratio = 0
            for cache_key in self.cache:
                ratio = SequenceMatcher(None, key, cache_key).ratio()
                if ratio > best_ratio and ratio >= self.similarity_threshold:
                    best_match = cache_key
                    best_ratio = ratio
            
            if best_match:
                item = self.cache[best_match]
                if time.time() < item['expiration']:
                    self.cache.move_to_end(best_match)
                    return item['value'], best_ratio
                else:
                    del self.cache[best_match]
        
        return None

    def remove_expired(self) -> None:
        current_time = time.time()
        expired_keys = [key for key, item in self.cache.items() if current_time >= item['expiration']]
        for key in expired_keys:
            del self.cache[key]

    def clear(self) -> None:
        self.cache.clear()

    def size(self) -> int:
        return len(self.cache)
