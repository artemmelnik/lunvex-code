# LLM Response Caching System

## Overview

The LLM Response Caching System is a new feature in LunVex Code that caches LLM responses to reduce API costs and improve performance. When the same query is made multiple times, the cached response is returned instead of making a new API call.

## Key Features

- **Automatic caching** of LLM responses
- **Configurable TTL** (Time-To-Live) for cache entries
- **LRU eviction** when cache is full
- **Persistent storage** across sessions
- **Statistics tracking** (hit rate, tokens saved, etc.)
- **CLI commands** for cache management
- **AI tools** for cache operations

## How It Works

### Cache Key Generation
Each LLM request generates a unique cache key based on:
- Model name
- Messages (conversation history)
- Tools (if any)
- Temperature
- Max tokens
- Other parameters

Identical requests generate identical cache keys, ensuring consistent caching.

### Cache Flow
1. When an LLM request is made, the system checks the cache first
2. If a valid cached response exists, it's returned immediately
3. If not, the API call is made and the response is cached
4. Cache entries expire based on TTL configuration
5. When cache is full, least recently used entries are evicted

## Configuration

### Environment Variables

```bash
# Maximum number of responses to cache (default: 100)
export LUNVEX_LLM_CACHE_MAX_SIZE=200

# Time-to-live for cache entries in seconds (default: 3600 = 1 hour)
export LUNVEX_LLM_CACHE_TTL_SECONDS=7200
```

### CLI Commands

```bash
# Show LLM cache statistics
lunvex-code llm-cache-stats

# Clear all LLM cache entries
lunvex-code clear-llm-cache

# Configure LLM cache settings
lunvex-code configure-llm-cache --max-size 200 --ttl-seconds 7200
```

### AI Tools

The AI assistant can manage the cache using these tools:

```bash
# Show cache statistics
lunvex-code run "show llm cache statistics"

# Clear the cache
lunvex-code run "clear the llm cache"

# Configure cache
lunvex-code run "configure llm cache with max size 500 and ttl 2 hours"
```

Available tools:
- `llm_cache_stats` - Get cache statistics
- `clear_llm_cache` - Clear all cache entries
- `configure_llm_cache` - Configure cache settings
- `invalidate_llm_cache` - Invalidate specific entries

## Integration with LLM Client

The cache is automatically integrated with `LunVexClient`:

```python
from lunvex_code.llm import LunVexClient

client = LunVexClient()
messages = [{'role': 'user', 'content': 'Hello'}]

# First call - cache miss, makes API request
response1 = client.chat(messages)

# Second call - cache hit, returns cached response
response2 = client.chat(messages)  # Same parameters

# Disable cache for a specific call
response3 = client.chat(messages, use_cache=False)
```

## Cache Statistics

The system tracks comprehensive statistics:

- **Hits/Misses**: Number of cache hits and misses
- **Hit Rate**: Percentage of requests served from cache
- **Tokens Saved**: Total tokens saved by cache hits
- **Current Size**: Number of entries in cache
- **TTL**: Current time-to-live setting
- **Most Accessed**: Most frequently accessed entry

## Cost Savings Example

Assuming DeepSeek pricing ($0.14 per 1M tokens):

- Each cache hit saves the tokens used in that response
- With 1000 cache hits averaging 100 tokens each:
  - Tokens saved: 100,000
  - Cost saved: ~$0.014
- With higher usage, savings can be significant

## Best Practices

### When to Use Cache
- **Development queries**: Repeated testing of the same prompts
- **Documentation generation**: Consistent responses for documentation
- **Code analysis**: Same code analyzed multiple times
- **Learning/tutorial sessions**: Repeated educational queries

### When to Disable Cache
- **Real-time data**: Queries requiring current information
- **Creative tasks**: Where varied responses are desired
- **Debugging**: When you need fresh responses each time
- **Temperature > 0**: Non-deterministic responses shouldn't be cached

### Configuration Recommendations
- **Development**: Smaller cache (50-100 entries), shorter TTL (1-2 hours)
- **Production**: Larger cache (200-500 entries), longer TTL (6-24 hours)
- **Testing**: Very small cache (10-20 entries), very short TTL (5-10 minutes)

## Technical Details

### Cache Storage
- Cache is stored in `~/.lunvex-code/llm_cache.pkl`
- Uses Python's `pickle` for serialization
- Automatically loads on startup
- Automatically saves on configuration changes

### Cache Invalidation
- **Automatic**: Based on TTL expiration
- **Manual**: Via CLI commands or AI tools
- **Pattern-based**: Invalidate entries matching specific patterns
- **Complete**: Clear all entries

### Memory Management
- Uses LRU (Least Recently Used) eviction
- Configurable maximum size
- Each entry includes response data and metadata
- Memory usage scales with cache size and response sizes

## Troubleshooting

### Cache Not Working
1. Check if cache is enabled: `lunvex-code llm-cache-stats`
2. Verify environment variables are set correctly
3. Check file permissions for cache storage directory
4. Ensure you're using the same parameters for identical queries

### High Memory Usage
1. Reduce cache size: `configure-llm-cache --max-size 50`
2. Clear cache: `clear-llm-cache`
3. Reduce TTL to expire entries faster

### Stale Responses
1. Reduce TTL: `configure-llm-cache --ttl-seconds 300`
2. Manually invalidate cache when needed
3. Use `use_cache=False` for time-sensitive queries

## Performance Impact

### Benefits
- **Reduced latency**: Cached responses are instant
- **Lower costs**: Fewer API calls means lower bills
- **Rate limit protection**: Cache hits don't count against rate limits
- **Offline capability**: Cached responses available without network

### Overhead
- **Memory usage**: Cache stores responses in memory
- **Disk I/O**: Persistent storage requires file operations
- **Key generation**: Hashing requests adds minimal CPU overhead

## Future Enhancements

Planned improvements:
- **Multi-level caching**: Memory + disk cache hierarchy
- **Selective caching**: Cache only specific types of responses
- **Cost tracking**: Real-time cost savings display
- **Cache analytics**: Detailed usage patterns and insights
- **Distributed caching**: Share cache across team members

## See Also

- [File Cache System](CACHE_SYSTEM.md) - For file content caching
- [CLI Reference](../README.md#common-commands) - For all CLI commands
- [API Documentation](API.md) - For developer API details
- [Performance Benchmarks](BENCHMARKS.md) - For performance metrics