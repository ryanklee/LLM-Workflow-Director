class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded."""
    pass

class CustomRateLimitError(Exception):
    """Exception raised for custom rate limit scenarios."""
    pass
