import pytest
from unittest.mock import patch
from src.rate_limiter import RateLimiter
import time

def test_rate_limiter_initialization():
    rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)
    assert rate_limiter.requests_per_minute == 60
    assert rate_limiter.requests_per_hour == 1000

def test_rate_limiter_allows_requests_within_limit():
    rate_limiter = RateLimiter(requests_per_minute=2, requests_per_hour=5)
    assert rate_limiter.is_allowed()
    assert rate_limiter.is_allowed()
    assert not rate_limiter.is_allowed()  # Third request should be denied

@pytest.mark.parametrize("sleep_time", [61, 3601])
def test_rate_limiter_resets(sleep_time):
    rate_limiter = RateLimiter(requests_per_minute=1, requests_per_hour=5)
    assert rate_limiter.is_allowed()
    assert not rate_limiter.is_allowed()
    
    # Mock time.time() to avoid actual sleeping
    with patch('time.time', return_value=time.time() + sleep_time):
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
    with patch('time.time', side_effect=[start_time, start_time + 30, start_time + 60]):
        rate_limiter.wait_for_next_slot()
    
    assert rate_limiter.is_allowed()
