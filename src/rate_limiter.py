import asyncio
import time
import logging
from typing import Dict
from src.domain_models import RateLimit, RateLimitPolicy
from src.exceptions import CustomRateLimitError

class RateLimiter(RateLimitPolicy):
    def __init__(self, requests_per_minute: int, requests_per_hour: int):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_bucket: Dict[int, int] = {}
        self.hour_bucket: Dict[int, int] = {}
        self.last_reset_time = time.time()
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"RateLimiter initialized with {requests_per_minute} requests/minute and {requests_per_hour} requests/hour")

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
                raise CustomRateLimitError("Rate limit exceeded for requests per minute")
            if hour_requests >= self.requests_per_hour:
                self.logger.warning("Rate limit reached (per hour)")
                raise CustomRateLimitError("Rate limit exceeded for requests per hour")
        
            self.minute_bucket[current_minute] = minute_requests + 1
            self.hour_bucket[current_hour] = hour_requests + 1
            self.logger.debug(f"Request allowed. New counts: minute={self.minute_bucket[current_minute]}, hour={self.hour_bucket[current_hour]}")
            return True

    def _reset_if_needed(self, current_time):
        if current_time - self.last_reset_time >= 60:
            self.minute_bucket.clear()
            self.last_reset_time = current_time
            self.logger.debug("Minute bucket reset")

    @classmethod
    def from_limits(cls, requests_per_minute: int, requests_per_hour: int):
        return cls(requests_per_minute, requests_per_hour)

    async def wait_for_next_slot(self) -> None:
        start_time = time.time()
        while True:
            try:
                if await self.is_allowed():
                    return
            except CustomRateLimitError:
                if time.time() - start_time > 60:  # Timeout after 60 seconds
                    raise TimeoutError("Waited too long for the next available slot")
                self.logger.debug("Waiting for next available slot")
                await asyncio.sleep(0.1)  # Sleep for 0.1 second before checking again
