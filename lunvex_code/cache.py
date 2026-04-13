"""File caching system for improved performance."""

import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class CacheEntry:
    """Entry in the file cache."""

    content: str
    metadata_hash: str  # Hash of file metadata (size, mtime)
    timestamp: float
    access_count: int = 0


class FileCache:
    """LRU cache for file contents with TTL and metadata validation."""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        Initialize the file cache.

        Args:
            max_size: Maximum number of files to cache
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _get_file_metadata_hash(self, file_path: Path) -> str:
        """Generate a hash based on file metadata (size and modification time)."""
        try:
            stat = file_path.stat()
            # Combine size and mtime for metadata hash
            metadata = f"{stat.st_size}:{stat.st_mtime_ns}"
            return hashlib.md5(metadata.encode()).hexdigest()
        except (OSError, IOError):
            return "missing"

    def _is_cache_valid(self, file_path: Path, entry: CacheEntry) -> bool:
        """Check if a cache entry is still valid."""
        # Check TTL
        if time.time() - entry.timestamp > self.ttl_seconds:
            return False

        # Check if file still exists
        if not file_path.exists():
            return False

        # Check if metadata matches
        current_metadata_hash = self._get_file_metadata_hash(file_path)
        return current_metadata_hash == entry.metadata_hash

    def get(self, file_path: Path) -> Optional[Tuple[str, bool]]:
        """
        Get file content from cache if available and valid.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (content, from_cache) or None if not in cache
        """
        cache_key = str(file_path.resolve())

        if cache_key in self.cache:
            entry = self.cache[cache_key]

            if self._is_cache_valid(file_path, entry):
                # Update access count and move to end (most recently used)
                entry.access_count += 1
                self.cache.move_to_end(cache_key)
                self.hits += 1
                return entry.content, True
            else:
                # Remove invalid entry
                del self.cache[cache_key]

        self.misses += 1
        return None

    def put(self, file_path: Path, content: str) -> None:
        """
        Add file content to cache.

        Args:
            file_path: Path to the file
            content: File content to cache
        """
        cache_key = str(file_path.resolve())
        metadata_hash = self._get_file_metadata_hash(file_path)

        entry = CacheEntry(
            content=content, metadata_hash=metadata_hash, timestamp=time.time(), access_count=1
        )

        # Add to cache
        self.cache[cache_key] = entry
        self.cache.move_to_end(cache_key)

        # Enforce max size
        if len(self.cache) > self.max_size:
            # Remove least recently used entry
            self.cache.popitem(last=False)

    def invalidate(self, file_path: Path) -> None:
        """
        Invalidate cache entry for a file.

        Args:
            file_path: Path to the file
        """
        cache_key = str(file_path.resolve())
        if cache_key in self.cache:
            del self.cache[cache_key]

    def invalidate_all(self) -> None:
        """Invalidate all cache entries."""
        self.cache.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "ttl_seconds": self.ttl_seconds,
        }

    def clear(self) -> None:
        """Clear all cache entries and reset statistics."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0


# Global cache instance
_file_cache = FileCache()


def get_file_cache() -> FileCache:
    """Get the global file cache instance."""
    return _file_cache


def configure_cache(max_size: int = 100, ttl_seconds: int = 300) -> None:
    """
    Configure the global file cache.

    Args:
        max_size: Maximum number of files to cache
        ttl_seconds: Time-to-live for cache entries in seconds
    """
    global _file_cache
    _file_cache = FileCache(max_size=max_size, ttl_seconds=ttl_seconds)


def read_file_with_cache(
    file_path: Path, limit: Optional[int] = None, offset: int = 1
) -> Tuple[str, bool]:
    """
    Read file with caching.

    Args:
        file_path: Path to the file
        limit: Maximum number of lines to read
        offset: Line number to start reading from (1-indexed)

    Returns:
        Tuple of (content, from_cache)
    """
    cache = get_file_cache()

    # Try to get from cache first
    cached_result = cache.get(file_path)
    if cached_result is not None:
        content, _ = cached_result
        from_cache = True
    else:
        # Read from disk
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        from_cache = False
        # Cache the result
        cache.put(file_path, content)

    # Apply offset and limit if needed
    if limit is not None or offset > 1:
        lines = content.splitlines(keepends=True)

        # Apply offset (convert to 0-indexed)
        start_idx = max(0, offset - 1)
        lines = lines[start_idx:]

        # Apply limit
        if limit and limit > 0:
            lines = lines[:limit]

        content = "".join(lines)

    return content, from_cache
