"""Tests for file caching system."""

import tempfile
import time
from pathlib import Path

from lunvex_code.cache import FileCache, configure_cache, get_file_cache, read_file_with_cache


class TestFileCache:
    """Test the FileCache class."""

    def test_cache_initialization(self):
        """Test cache initialization with default parameters."""
        cache = FileCache()
        assert cache.max_size == 100
        assert cache.ttl_seconds == 300
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0

    def test_cache_initialization_custom(self):
        """Test cache initialization with custom parameters."""
        cache = FileCache(max_size=50, ttl_seconds=60)
        assert cache.max_size == 50
        assert cache.ttl_seconds == 60

    def test_put_and_get(self, tmp_path):
        """Test putting and getting files from cache."""
        cache = FileCache()

        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        # Put in cache
        cache.put(test_file, "Hello, World!")

        # Get from cache
        result = cache.get(test_file)
        assert result is not None
        content, from_cache = result
        assert content == "Hello, World!"
        assert from_cache is True

    def test_cache_miss(self, tmp_path):
        """Test cache miss when file not in cache."""
        cache = FileCache()

        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        # Try to get from cache (should miss)
        result = cache.get(test_file)
        assert result is None
        assert cache.misses == 1
        assert cache.hits == 0

    def test_cache_invalidation(self, tmp_path):
        """Test cache invalidation."""
        cache = FileCache()

        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        # Put in cache
        cache.put(test_file, "Hello, World!")

        # Invalidate
        cache.invalidate(test_file)

        # Should miss after invalidation
        result = cache.get(test_file)
        assert result is None

    def test_cache_ttl_expiration(self, tmp_path):
        """Test cache TTL expiration."""
        cache = FileCache(ttl_seconds=1)  # Very short TTL

        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        # Put in cache
        cache.put(test_file, "Hello, World!")

        # Should be in cache initially
        result = cache.get(test_file)
        assert result is not None

        # Wait for TTL to expire
        time.sleep(1.1)

        # Should miss after TTL expiration
        result = cache.get(test_file)
        assert result is None

    def test_cache_max_size(self):
        """Test cache max size enforcement."""
        cache = FileCache(max_size=2)

        # Create temporary files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Add 3 files to cache (exceeding max_size)
            for i in range(3):
                test_file = tmp_path / f"test{i}.txt"
                test_file.write_text(f"Content {i}")
                cache.put(test_file, f"Content {i}")

            # Cache should only contain 2 files (max_size)
            assert len(cache.cache) == 2

            # The first file (test0.txt) should have been evicted (LRU)
            test_file0 = tmp_path / "test0.txt"
            result = cache.get(test_file0)
            assert result is None

            # The last two files should still be in cache
            test_file1 = tmp_path / "test1.txt"
            test_file2 = tmp_path / "test2.txt"
            assert cache.get(test_file1) is not None
            assert cache.get(test_file2) is not None

    def test_cache_stats(self, tmp_path):
        """Test cache statistics."""
        cache = FileCache()

        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        # Initial stats
        stats = cache.get_stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0

        # Miss
        cache.get(test_file)
        stats = cache.get_stats()
        assert stats["misses"] == 1

        # Put and hit
        cache.put(test_file, "Hello, World!")
        cache.get(test_file)
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["size"] == 1

    def test_cache_clear(self, tmp_path):
        """Test clearing cache."""
        cache = FileCache()

        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        # Put in cache
        cache.put(test_file, "Hello, World!")
        assert len(cache.cache) == 1

        # Clear cache
        cache.clear()
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0


class TestReadFileWithCache:
    """Test the read_file_with_cache function."""

    def test_read_file_with_cache_hit(self, tmp_path):
        """Test reading file with cache hit."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

        # First read (should miss)
        content1, from_cache1 = read_file_with_cache(test_file)
        assert from_cache1 is False
        assert "Line 1" in content1

        # Second read (should hit)
        content2, from_cache2 = read_file_with_cache(test_file)
        assert from_cache2 is True
        assert content1 == content2

    def test_read_file_with_cache_limit_offset(self, tmp_path):
        """Test reading file with limit and offset."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

        # Read with limit
        content, from_cache = read_file_with_cache(test_file, limit=2)
        assert from_cache is False
        assert content == "Line 1\nLine 2"

        # Read with offset
        content, from_cache = read_file_with_cache(test_file, offset=3)
        assert content == "Line 3\nLine 4\nLine 5"

        # Read with both limit and offset
        content, from_cache = read_file_with_cache(test_file, limit=2, offset=2)
        assert content == "Line 2\nLine 3"

    def test_cache_invalidation_on_file_change(self, tmp_path):
        """Test that cache is invalidated when file changes."""
        test_file = tmp_path / "test.txt"

        # Write initial content
        test_file.write_text("Initial content")

        # First read (miss)
        content1, from_cache1 = read_file_with_cache(test_file)
        assert from_cache1 is False

        # Second read (hit)
        content2, from_cache2 = read_file_with_cache(test_file)
        assert from_cache2 is True

        # Change file content
        test_file.write_text("Modified content")

        # Third read (should miss due to file change)
        content3, from_cache3 = read_file_with_cache(test_file)
        assert from_cache3 is False
        assert content3 == "Modified content"


class TestGlobalCache:
    """Test global cache functions."""

    def test_get_file_cache(self):
        """Test getting global cache instance."""
        cache1 = get_file_cache()
        cache2 = get_file_cache()
        assert cache1 is cache2  # Should be the same instance

    def test_configure_cache(self):
        """Test configuring global cache."""
        # Get original cache
        original_cache = get_file_cache()

        # Configure with new settings
        configure_cache(max_size=200, ttl_seconds=600)

        # Get new cache
        new_cache = get_file_cache()

        # Should be different instance
        assert original_cache is not new_cache

        # Check new settings
        assert new_cache.max_size == 200
        assert new_cache.ttl_seconds == 600


class TestCacheToolsIntegration:
    """Test integration of cache tools with the tool system."""

    def test_cache_stats_tool(self):
        """Test cache_stats tool."""
        from lunvex_code.tools.cache_tools import CacheStatsTool

        tool = CacheStatsTool()
        result = tool.execute()

        assert result.success is True
        assert "File Cache Statistics" in result.output
        assert "Hit Rate" in result.output

    def test_clear_cache_tool(self):
        """Test clear_cache tool."""
        from lunvex_code.tools.cache_tools import ClearCacheTool

        tool = ClearCacheTool()
        result = tool.execute()

        assert result.success is True
        assert "cleared" in result.output.lower()

    def test_configure_cache_tool(self):
        """Test configure_cache tool."""
        from lunvex_code.tools.cache_tools import ConfigureCacheTool

        tool = ConfigureCacheTool()
        result = tool.execute(max_size=150, ttl_seconds=450)

        assert result.success is True
        assert "max_size=150" in result.output
        assert "ttl_seconds=450" in result.output

        # Test validation
        result = tool.execute(max_size=0)
        assert result.success is False
        assert "must be positive" in result.error

    def test_invalidate_cache_tool(self, tmp_path):
        """Test invalidate_cache tool."""
        from lunvex_code.tools.cache_tools import InvalidateCacheTool

        tool = InvalidateCacheTool()

        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        # Invalidate single file
        result = tool.execute(path=str(test_file))
        assert result.success is True
        assert "invalidated" in result.output.lower()

        # Create test directory
        test_dir = tmp_path / "subdir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("File 1")
        (test_dir / "file2.txt").write_text("File 2")

        # Invalidate directory recursively
        result = tool.execute(path=str(test_dir), recursive=True)
        assert result.success is True
        assert "2 files" in result.output
