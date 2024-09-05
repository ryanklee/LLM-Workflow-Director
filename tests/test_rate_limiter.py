import pytest
from src.rate_limiter import RateLimiter
import time

def test_rate_limiter_initialization():
    rate_limiter = RateLimiter.from_limits(requests_per_minute=60, requests_per_hour=1000)
    assert rate_limiter.requests_per_minute == 60
    assert rate_limiter.requests_per_hour == 1000

def test_rate_limiter_allows_requests_within_limit():
    rate_limiter = RateLimiter(requests_per_minute=2, requests_per_hour=5)
    assert rate_limiter.is_allowed()
    assert rate_limiter.is_allowed()
    assert not rate_limiter.is_allowed()  # Third request should be denied

def test_rate_limiter_resets_after_minute():
    rate_limiter = RateLimiter(requests_per_minute=1, requests_per_hour=5)
    assert rate_limiter.is_allowed()
    assert not rate_limiter.is_allowed()
    time.sleep(60)  # Wait for a minute
    assert rate_limiter.is_allowed()

def test_rate_limiter_hour_limit():
    rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=2)
    assert rate_limiter.is_allowed()
    assert rate_limiter.is_allowed()
    assert not rate_limiter.is_allowed()  # Third request should be denied

def test_wait_for_next_slot():
    rate_limiter = RateLimiter(requests_per_minute=1, requests_per_hour=5)
    assert rate_limiter.is_allowed()
    start_time = time.time()
    rate_limiter.wait_for_next_slot()
    end_time = time.time()
    assert end_time - start_time >= 60  # Should wait at least 60 seconds
