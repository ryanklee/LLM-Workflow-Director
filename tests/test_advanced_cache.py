import pytest
import time
from src.advanced_cache import AdvancedCache
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def cache():
    return AdvancedCache(default_expiration=3600, max_size=None, similarity_threshold=0.8)

def test_set_and_get(cache):
    cache.set("key1", "value1")
    assert cache.get("key1") == ("value1", 1.0)

def test_expiration(cache):
    cache.set("key1", "value1", expiration=1)
    assert cache.get("key1") == ("value1", 1.0)
    time.sleep(1.1)
    assert cache.get("key1") is None

def test_custom_expiration(cache):
    cache.set("key1", "value1", expiration=1)
    cache.set("key2", "value2")
    time.sleep(1.1)
    assert cache.get("key1") is None
    assert cache.get("key2") == ("value2", 1.0)

def test_remove_expired(cache):
    cache.set("key1", "value1", expiration=1)
    cache.set("key2", "value2", expiration=2)
    time.sleep(1.1)
    cache.remove_expired()
    assert "key1" not in cache.cache
    assert "key2" in cache.cache

def test_clear(cache):
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

def test_partial_match(cache):
    cache.set("hello_world", "value1")
    cache.set("goodbye_world", "value2")
    result = cache.get("hello_earth", partial_match=True)
    logger.info(f"Partial match result: {result}")
    logger.info(f"Cache state: {cache.dump_state()}")
    assert result == ("value1", 0.8181818181818182)
    assert cache.get("hello_mars", partial_match=True) is None

def test_partial_match_threshold():
    cache_high_threshold = AdvancedCache(similarity_threshold=0.9)
    cache_high_threshold.set("hello_world", "value1")
    result_high = cache_high_threshold.get("hello_earth", partial_match=True)
    logger.info(f"High threshold result: {result_high}")
    logger.info(f"High threshold cache state: {cache_high_threshold.dump_state()}")
    assert result_high is None
    
    cache_low_threshold = AdvancedCache(similarity_threshold=0.7)
    cache_low_threshold.set("hello_world", "value1")
    result_low = cache_low_threshold.get("hello_earth", partial_match=True)
    logger.info(f"Low threshold result: {result_low}")
    logger.info(f"Low threshold cache state: {cache_low_threshold.dump_state()}")
    assert result_low == ("value1", 0.8181818181818182)

def test_partial_match_edge_cases(cache):
    cache.set("hello_world", "value1")
    logger.info(f"Cache state before edge cases: {cache.dump_state()}")
    assert cache.get("hello", partial_match=True) is None  # Too short
    assert cache.get("completely_different", partial_match=True) is None  # No similarity
    result = cache.get("hello_world_extra_long", partial_match=True)
    logger.info(f"Edge case result: {result}")
    assert result == ("value1", 0.8571428571428571)  # Longer but similar

def test_partial_match_multiple_similar_keys(cache):
    cache.set("hello_world", "value1")
    cache.set("hello_earth", "value2")
    cache.set("hello_mars", "value3")
    logger.info(f"Cache state with multiple keys: {cache.dump_state()}")
    result = cache.get("hello_planet", partial_match=True)
    logger.info(f"Partial match result with multiple similar keys: {result}")
    assert result[0] in ["value1", "value2", "value3"]  # Should match one of these
    assert result[1] >= 0.8  # Similarity should be at least 0.8

def test_cache_state_dump(cache):
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    state = cache.dump_state()
    logger.info(f"Cache state dump: {state}")
    assert "key1" in state['cache_contents']
    assert "key2" in state['cache_contents']
    assert state['size'] == 2
    assert state['similarity_threshold'] == 0.8
