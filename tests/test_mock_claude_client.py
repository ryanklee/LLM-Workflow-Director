import pytest
import asyncio
from src.mock_claude_client import MockClaudeClient

@pytest.mark.asyncio
async def test_cache_hit():
    client = MockClaudeClient(cache_ttl=60)
    messages = [{"role": "user", "content": "Hello, Claude!"}]
    
    response1 = await client.messages.create("claude-3-opus-20240229", 100, messages)
    response2 = await client.messages.create("claude-3-opus-20240229", 100, messages)
    
    assert response1 == response2
    assert client.call_count == 1  # Only one actual API call should be made

@pytest.mark.asyncio
async def test_cache_expiration():
    client = MockClaudeClient(cache_ttl=1)  # Set cache TTL to 1 second for testing
    messages = [{"role": "user", "content": "Hello, Claude!"}]
    
    response1 = await client.messages.create("claude-3-opus-20240229", 100, messages)
    await asyncio.sleep(1.1)  # Wait for cache to expire
    response2 = await client.messages.create("claude-3-opus-20240229", 100, messages)
    
    assert response1 != response2
    assert client.call_count == 2  # Two API calls should be made

@pytest.mark.asyncio
async def test_token_count_caching():
    client = MockClaudeClient(cache_ttl=60)
    text = "This is a test message."
    
    count1 = await client.count_tokens(text)
    count2 = await client.count_tokens(text)
    
    assert count1 == count2
    assert client.call_count == 0  # Token counting doesn't increase call count

@pytest.mark.asyncio
async def test_cache_invalidation():
    client = MockClaudeClient(cache_ttl=60)
    messages = [{"role": "user", "content": "Hello, Claude!"}]
    
    response1 = await client.messages.create("claude-3-opus-20240229", 100, messages)
    client._cached_create_message.cache_clear()  # Manually clear the cache
    response2 = await client.messages.create("claude-3-opus-20240229", 100, messages)
    
    assert response1 != response2
    assert client.call_count == 2  # Two API calls should be made

@pytest.mark.asyncio
async def test_cache_with_different_parameters():
    client = MockClaudeClient(cache_ttl=60)
    messages1 = [{"role": "user", "content": "Hello, Claude!"}]
    messages2 = [{"role": "user", "content": "Hi, Claude!"}]
    
    response1 = await client.messages.create("claude-3-opus-20240229", 100, messages1)
    response2 = await client.messages.create("claude-3-opus-20240229", 100, messages2)
    
    assert response1 != response2
    assert client.call_count == 2  # Two API calls should be made for different messages
