import time
from typing import Dict
from src.domain_models import RateLimit, RateLimitPolicy

class RateLimiter(RateLimitPolicy):
    def __init__(self, rate_limit: RateLimit):
        self.rate_limit = rate_limit
        self.minute_bucket: Dict[int, int] = {}
        self.hour_bucket: Dict[int, int] = {}

    def is_allowed(self) -> bool:
        current_minute = int(time.time() / 60)
        current_hour = int(time.time() / 3600)

        # Clean up old entries
        self.minute_bucket = {k: v for k, v in self.minute_bucket.items() if k >= current_minute - 1}
        self.hour_bucket = {k: v for k, v in self.hour_bucket.items() if k >= current_hour - 1}

        # Check minute limit
        minute_requests = sum(self.minute_bucket.values())
        if minute_requests >= self.rate_limit.requests_per_minute:
            return False

        # Check hour limit
        hour_requests = sum(self.hour_bucket.values())
        if hour_requests >= self.rate_limit.requests_per_hour:
            return False

        # Increment counters
        self.minute_bucket[current_minute] = self.minute_bucket.get(current_minute, 0) + 1
        self.hour_bucket[current_hour] = self.hour_bucket.get(current_hour, 0) + 1

        return True

    def wait_for_next_slot(self) -> None:
        while not self.is_allowed():
            time.sleep(1)
