# File Caching System

LunVex Code includes a sophisticated file caching system to improve performance when reading files repeatedly. This document describes how the caching system works and how to configure it.

## Overview

The file caching system provides:

1. **LRU (Least Recently Used) cache** for file contents
2. **TTL (Time-to-Live)** expiration for cache entries
3. **Automatic invalidation** when files are modified
4. **Metadata validation** to ensure cache consistency
5. **Configurable settings** via environment variables or CLI

## How It Works

### Cache Structure

The cache stores file contents along with metadata hashes:

```python
@dataclass
class CacheEntry:
    content: str           # File content
    metadata_hash: str     # Hash of file metadata (size, mtime)
    timestamp: float       # When the entry was cached
    access_count: int      # How many times it's been accessed
```

### Cache Validation

When retrieving a file from cache, the system checks:

1. **TTL expiration**: Has the cache entry expired?
2. **File existence**: Does the file still exist?
3. **Metadata match**: Has the file been modified since caching?

If any check fails, the cache entry is invalidated and the file is read from disk.

### Automatic Invalidation

The cache is automatically invalidated when:
- Files are modified via `write_file` tool
- Files are edited via `edit_file` tool
- Files are deleted or moved

## Configuration

### Environment Variables

You can configure the cache using environment variables:

```bash
# Set maximum number of files to cache (default: 100)
export LUNVEX_CACHE_MAX_SIZE=200

# Set cache TTL in seconds (default: 300 = 5 minutes)
export LUNVEX_CACHE_TTL_SECONDS=600
```

### CLI Commands

Manage the cache via CLI commands:

```bash
# Show cache statistics
lunvex-code cache-stats

# Clear all cache entries
lunvex-code clear-cache

# Configure cache settings
lunvex-code configure-cache --max-size 200 --ttl-seconds 600
```

### Tool Commands

The cache can also be managed via AI tools:

```bash
# Ask the AI to show cache stats
lunvex-code run "show cache statistics"

# Ask the AI to clear the cache
lunvex-code run "clear the file cache"

# Ask the AI to configure cache
lunvex-code run "configure cache with max size 200 and TTL 10 minutes"
```

Available cache tools:
- `cache_stats` - Get cache statistics
- `clear_cache` - Clear all cache entries
- `configure_cache` - Configure cache settings
- `invalidate_cache` - Invalidate cache for specific files

## Performance Benefits

### Typical Use Cases

1. **Reading configuration files** - `.env`, `pyproject.toml`, `package.json`
2. **Reading source files multiple times** - During refactoring or analysis
3. **Reading documentation files** - `README.md`, `docs/` files
4. **Reading test files** - When running tests multiple times

### Performance Metrics

With caching enabled:
- **First read**: Read from disk (cache miss)
- **Subsequent reads**: Read from cache (cache hit)
- **Cache hit rate**: Typically 60-80% for development workflows
- **Speed improvement**: 10-100x faster for cached reads

## Cache Indicators

When using the `read_file` tool, cached reads are indicated with `[cached]`:

```
Contents of README.md [cached]:
     1  # Project Name
     2  
     3  This is the project README file.
```

## Technical Details

### Cache Implementation

The cache is implemented as an LRU cache using `collections.OrderedDict`:

```python
class FileCache:
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
```

### Metadata Hashing

File metadata is hashed using MD5 of file size and modification time:

```python
def _get_file_metadata_hash(self, file_path: Path) -> str:
    stat = file_path.stat()
    metadata = f"{stat.st_size}:{stat.st_mtime_ns}"
    return hashlib.md5(metadata.encode()).hexdigest()
```

### Cache Statistics

The cache tracks:
- **Size**: Current number of cached files
- **Hits**: Number of successful cache retrievals
- **Misses**: Number of cache misses
- **Hit Rate**: Percentage of cache hits vs total requests

## Best Practices

### When to Use Cache

✅ **Good candidates for caching:**
- Configuration files
- Documentation files
- Source files being analyzed
- Test files
- Static assets

❌ **Poor candidates for caching:**
- Log files (constantly changing)
- Temporary files
- Very large files (>10MB)
- Files accessed only once

### Configuration Recommendations

**For small projects:**
```bash
export LUNVEX_CACHE_MAX_SIZE=50
export LUNVEX_CACHE_TTL_SECONDS=300  # 5 minutes
```

**For large projects:**
```bash
export LUNVEX_CACHE_MAX_SIZE=200
export LUNVEX_CACHE_TTL_SECONDS=600  # 10 minutes
```

**For development sessions:**
```bash
export LUNVEX_CACHE_MAX_SIZE=100
export LUNVEX_CACHE_TTL_SECONDS=1800  # 30 minutes
```

## Troubleshooting

### Cache Not Working

If caching doesn't seem to be working:

1. **Check cache statistics:**
   ```bash
   lunvex-code cache-stats
   ```

2. **Verify file modifications:**
   - Cache is invalidated when files are modified
   - Check if files are being written outside LunVex

3. **Check TTL settings:**
   - Very short TTL may cause frequent cache misses

### High Memory Usage

If cache is using too much memory:

1. **Reduce cache size:**
   ```bash
   export LUNVEX_CACHE_MAX_SIZE=50
   ```

2. **Clear cache periodically:**
   ```bash
   lunvex-code clear-cache
   ```

3. **Exclude large files:**
   - Consider not caching files > 1MB

### Cache Inconsistency

If cached content doesn't match disk:

1. **Clear cache:**
   ```bash
   lunvex-code clear-cache
   ```

2. **Check file permissions:**
   - Ensure LunVex can read file metadata

3. **Report bug:**
   - File an issue if problem persists

## Integration with Other Systems

### Git Integration

The cache works well with Git tools:
- Reading Git configuration files
- Analyzing commit history
- Reviewing changed files

### Dependency Management

Cache improves dependency analysis:
- Reading `pyproject.toml`, `package.json`
- Parsing dependency trees
- Scanning for vulnerabilities

## Future Enhancements

Planned improvements:

1. **Multi-level caching** - Memory + disk cache
2. **Compression** - Compress cached content
3. **Predictive caching** - Cache files likely to be read
4. **Distributed caching** - Share cache across sessions
5. **Cache profiles** - Different settings for different project types