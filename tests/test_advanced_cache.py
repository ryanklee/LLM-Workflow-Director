import pytest
import time
from src.advanced_cache import AdvancedCache

def test_set_and_get():
    cache = AdvancedCache()
    cache.set("key1", "value1")
    assert cache.get("key1") == ("value1", 1.0)

def test_expiration():
    cache = AdvancedCache(default_expiration=1)
    cache.set("key1", "value1")
    assert cache.get("key1") == ("value1", 1.0)
    time.sleep(1.1)
    assert cache.get("key1") is None

def test_custom_expiration():
    cache = AdvancedCache(default_expiration=10)
    cache.set("key1", "value1", expiration=1)
    cache.set("key2", "value2")
    time.sleep(1.1)
    assert cache.get("key1") is None
    assert cache.get("key2") == ("value2", 1.0)

def test_remove_expired():
    cache = AdvancedCache(default_expiration=1)
    cache.set("key1", "value1")
    cache.set("key2", "value2", expiration=2)
    time.sleep(1.1)
    cache.remove_expired()
    assert "key1" not in cache.cache
    assert "key2" in cache.cache

def test_clear():
    cache = AdvancedCache()
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()
    assert len(cache.cache) == 0

def test_max_size():
    cache = AdvancedCache(max_size=2)
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    assert cache.size() == 2
    assert cache.get("key1") is None
    assert cache.get("key2") == ("value2", 1.0)
    assert cache.get("key3") == ("value3", 1.0)

def test_lru_eviction():
    cache = AdvancedCache(max_size=2)
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.get("key1")  # Move key1 to the end (most recently used)
    cache.set("key3", "value3")
    assert cache.size() == 2
    assert cache.get("key1") == ("value1", 1.0)
    assert cache.get("key2") is None
    assert cache.get("key3") == ("value3", 1.0)

def test_partial_match():
    cache = AdvancedCache(similarity_threshold=0.8)
    cache.set("hello_world", "value1")
    cache.set("goodbye_world", "value2")
    assert cache.get("hello_earth", partial_match=True) == ("value1", 0.8181818181818182)
    assert cache.get("hello_mars", partial_match=True) is None

def test_partial_match_threshold():
    cache = AdvancedCache(similarity_threshold=0.9)
    cache.set("hello_world", "value1")
    assert cache.get("hello_earth", partial_match=True) is None
    
    cache = AdvancedCache(similarity_threshold=0.7)
    cache.set("hello_world", "value1")
    assert cache.get("hello_earth", partial_match=True) == ("value1", 0.8181818181818182)
