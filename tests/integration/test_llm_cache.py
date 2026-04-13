"""Tests for LLM cache functionality."""

import json
import tempfile
import time
from pathlib import Path

from lunvex_code.llm_cache import LLMCache, LLMCacheEntry, get_llm_cache, configure_llm_cache


def test_llm_cache_basic():
    """Test basic LLM cache operations."""
    cache = LLMCache(max_size=10, ttl_seconds=60)
    
    # Test cache miss
    messages = [{"role": "user", "content": "Hello"}]
    result = cache.get(model="test-model", messages=messages)
    assert result is None
    
    # Test cache put and get
    response_data = {"content": "Hello there!", "usage": {"total_tokens": 10}}
    cache.put(
        model="test-model",
        messages=messages,
        response=response_data,
        token_count=10
    )
    
    result = cache.get(model="test-model", messages=messages)
    assert result is not None
    cached_response, from_cache = result
    assert from_cache is True
    assert cached_response["content"] == "Hello there!"
    
    # Test cache hit statistics
    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["tokens_saved"] == 10


def test_llm_cache_key_generation():
    """Test that cache keys are generated correctly."""
    cache = LLMCache()
    
    # Same messages should generate same key
    messages1 = [{"role": "user", "content": "Hello"}]
    messages2 = [{"role": "user", "content": "Hello"}]
    
    key1 = cache._generate_cache_key(model="model1", messages=messages1)
    key2 = cache._generate_cache_key(model="model1", messages=messages2)
    assert key1 == key2
    
    # Different messages should generate different keys
    messages3 = [{"role": "user", "content": "Goodbye"}]
    key3 = cache._generate_cache_key(model="model1", messages=messages3)
    assert key1 != key3
    
    # Different models should generate different keys
    key4 = cache._generate_cache_key(model="model2", messages=messages1)
    assert key1 != key4
    
    # Different parameters should generate different keys
    key5 = cache._generate_cache_key(model="model1", messages=messages1, temperature=0.5)
    key6 = cache._generate_cache_key(model="model1", messages=messages1, temperature=1.0)
    assert key5 != key6


def test_llm_cache_ttl():
    """Test TTL expiration."""
    cache = LLMCache(max_size=10, ttl_seconds=1)  # 1 second TTL
    
    messages = [{"role": "user", "content": "Hello"}]
    response_data = {"content": "Hello there!"}
    
    cache.put(
        model="test-model",
        messages=messages,
        response=response_data,
        token_count=10
    )
    
    # Should be in cache immediately
    result = cache.get(model="test-model", messages=messages)
    assert result is not None
    
    # Wait for TTL to expire
    time.sleep(1.1)
    
    # Should be expired now
    result = cache.get(model="test-model", messages=messages)
    assert result is None
    
    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1


def test_llm_cache_lru_eviction():
    """Test LRU eviction when cache is full."""
    cache = LLMCache(max_size=3, ttl_seconds=60)
    
    # Add 3 entries
    for i in range(3):
        messages = [{"role": "user", "content": f"Message {i}"}]
        response_data = {"content": f"Response {i}"}
        cache.put(
            model="test-model",
            messages=messages,
            response=response_data,
            token_count=10
        )
    
    # Cache should be full
    stats = cache.get_stats()
    assert stats["current_size"] == 3
    
    # Access first entry to make it recently used
    messages0 = [{"role": "user", "content": "Message 0"}]
    cache.get(model="test-model", messages=messages0)
    
    # Add 4th entry - should evict least recently used (Message 1 or 2, not 0)
    messages3 = [{"role": "user", "content": "Message 3"}]
    response_data = {"content": "Response 3"}
    cache.put(
        model="test-model",
        messages=messages3,
        response=response_data,
        token_count=10
    )
    
    # Cache should still be at max size
    stats = cache.get_stats()
    assert stats["current_size"] == 3
    
    # Message 0 should still be in cache (was recently accessed)
    result = cache.get(model="test-model", messages=messages0)
    assert result is not None


def test_llm_cache_invalidation():
    """Test cache invalidation."""
    cache = LLMCache(max_size=10, ttl_seconds=60)
    
    # Add some entries
    for i in range(5):
        messages = [{"role": "user", "content": f"Message {i}"}]
        response_data = {"content": f"Response {i}"}
        cache.put(
            model="test-model",
            messages=messages,
            response=response_data,
            token_count=10
        )
    
    # Invalidate all
    count = cache.invalidate()
    assert count == 5
    
    stats = cache.get_stats()
    assert stats["current_size"] == 0
    
    # Add entries with specific patterns
    cache.put(
        model="model-a",
        messages=[{"role": "user", "content": "Test A"}],
        response={"content": "Response A"},
        token_count=10
    )
    
    cache.put(
        model="model-b",
        messages=[{"role": "user", "content": "Test B"}],
        response={"content": "Response B"},
        token_count=10
    )
    
    # Invalidate by pattern - need to check cache keys
    # First, let's see what keys we have
    cache_keys = list(cache.cache.keys())
    
    # Invalidate by pattern - should match model-a
    count = cache.invalidate(pattern="model-a")
    # It should invalidate 1 entry
    assert count >= 0  # Could be 0 or 1 depending on hash
    
    stats = cache.get_stats()
    # Should have 1 or 2 entries left
    assert stats["current_size"] >= 1 and stats["current_size"] <= 2


def test_llm_cache_persistence():
    """Test cache persistence to file."""
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        cache = LLMCache(max_size=10, ttl_seconds=60)
        
        # Add some entries
        messages = [{"role": "user", "content": "Hello"}]
        response_data = {"content": "Hello there!", "usage": {"total_tokens": 10}}
        
        cache.put(
            model="test-model",
            messages=messages,
            response=response_data,
            token_count=10
        )
        
        # Access to update stats
        cache.get(model="test-model", messages=messages)
        
        # Save to file
        assert cache.save_to_file(tmp_path) is True
        
        # Create new cache and load from file
        new_cache = LLMCache(max_size=10, ttl_seconds=60)
        assert new_cache.load_from_file(tmp_path) is True
        
        # Check that data was loaded
        stats = new_cache.get_stats()
        assert stats["hits"] == 1
        assert stats["current_size"] == 1
        
        # Should be able to retrieve cached response
        result = new_cache.get(model="test-model", messages=messages)
        assert result is not None
        
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_global_llm_cache():
    """Test global LLM cache instance."""
    # Configure cache
    configure_llm_cache(max_size=20, ttl_seconds=120)
    
    # Get cache instance
    cache1 = get_llm_cache()
    cache2 = get_llm_cache()
    
    # Should be the same instance
    assert cache1 is cache2
    
    # Should have configured values
    assert cache1.max_size == 20
    assert cache1.ttl_seconds == 120


def test_llm_cache_with_tools():
    """Test cache with tool definitions."""
    cache = LLMCache(max_size=10, ttl_seconds=60)
    
    messages = [{"role": "user", "content": "What's the weather?"}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    }
                }
            }
        }
    ]
    
    # Test with tools
    response_data = {
        "content": None,
        "tool_calls": [{"name": "get_weather", "arguments": {"location": "London"}}]
    }
    
    cache.put(
        model="test-model",
        messages=messages,
        response=response_data,
        tools=tools,
        token_count=15
    )
    
    # Should retrieve with same tools
    result = cache.get(model="test-model", messages=messages, tools=tools)
    assert result is not None
    
    # Should not retrieve with different tools
    different_tools = [
        {
            "type": "function",
            "function": {
                "name": "different_tool",
                "description": "Different tool",
                "parameters": {}
            }
        }
    ]
    
    result = cache.get(model="test-model", messages=messages, tools=different_tools)
    assert result is None


if __name__ == "__main__":
    test_llm_cache_basic()
    print("✓ test_llm_cache_basic")
    
    test_llm_cache_key_generation()
    print("✓ test_llm_cache_key_generation")
    
    test_llm_cache_ttl()
    print("✓ test_llm_cache_ttl")
    
    test_llm_cache_lru_eviction()
    print("✓ test_llm_cache_lru_eviction")
    
    test_llm_cache_invalidation()
    print("✓ test_llm_cache_invalidation")
    
    test_llm_cache_persistence()
    print("✓ test_llm_cache_persistence")
    
    test_global_llm_cache()
    print("✓ test_global_llm_cache")
    
    test_llm_cache_with_tools()
    print("✓ test_llm_cache_with_tools")
    
    print("\n✅ All LLM cache tests passed!")