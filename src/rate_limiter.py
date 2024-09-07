import time
import logging
from typing import Dict
from src.domain_models import RateLimit, RateLimitPolicy

class RateLimitError(Exception):
    pass

import asyncio

class RateLimiter(RateLimitPolicy):
    def __init__(self, requests_per_minute: int, requests_per_hour: int):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_bucket: Dict[int, int] = {}
        self.hour_bucket: Dict[int, int] = {}
        self.last_reset_time = time.time()
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)

    async def is_allowed(self) -> bool:
        async with self.lock:
            current_time = time.time()
            self._reset_if_needed(current_time)
            current_minute = int(current_time / 60)
            current_hour = int(current_time / 3600)
        
            minute_requests = self.minute_bucket.get(current_minute, 0)
            hour_requests = self.hour_bucket.get(current_hour, 0)
        
            self.logger.debug(f"Current requests: minute={minute_requests}, hour={hour_requests}")
        
            if minute_requests >= self.requests_per_minute:
                self.logger.warning("Rate limit reached (per minute)")
                return False
            if hour_requests >= self.requests_per_hour:
                self.logger.warning("Rate limit reached (per hour)")
                return False
        
            self.minute_bucket[current_minute] = minute_requests + 1
            self.hour_bucket[current_hour] = hour_requests + 1
            self.logger.debug(f"Request allowed. New counts: minute={self.minute_bucket[current_minute]}, hour={self.hour_bucket[current_hour]}")
            return True

    def _reset_if_needed(self, current_time):
        if current_time - self.last_reset_time >= 60:
            self.minute_bucket.clear()
            self.last_reset_time = current_time
        self.last_reset_time = time.time()

    @classmethod
    def from_limits(cls, requests_per_minute: int, requests_per_hour: int):
        return cls(requests_per_minute, requests_per_hour)

    async def is_allowed(self) -> bool:
        async with self.lock:
            current_time = time.time()
            self._reset_if_needed(current_time)
            current_minute = int(current_time / 60)
            current_hour = int(current_time / 3600)
        
        if self.minute_bucket.get(current_minute, 0) >= self.requests_per_minute:
            return False
        if self.hour_bucket.get(current_hour, 0) >= self.requests_per_hour:
            return False
            self.last_reset_time = current_time

        # Clean up old entries
        self.minute_bucket = {k: v for k, v in self.minute_bucket.items() if k >= current_minute - 1}
        self.hour_bucket = {k: v for k, v in self.hour_bucket.items() if k >= current_hour - 1}

        # Check minute limit
        minute_requests = sum(self.minute_bucket.values())
        if minute_requests >= self.requests_per_minute:
            return False

        # Check hour limit
        hour_requests = sum(self.hour_bucket.values())
        if hour_requests >= self.requests_per_hour:
            return False

        # Increment counters
        self.minute_bucket[current_minute] = self.minute_bucket.get(current_minute, 0) + 1
        self.hour_bucket[current_hour] = self.hour_bucket.get(current_hour, 0) + 1

        return True

    def wait_for_next_slot(self) -> None:
        start_time = time.time()
        while not self.is_allowed():
            if time.time() - start_time > 60:  # Timeout after 60 seconds
                raise TimeoutError("Waited too long for the next available slot")
            time.sleep(0.1)  # Sleep for 0.1 second before checking again
        # Remove the call to _increment_counters as it's not defined and not necessary
