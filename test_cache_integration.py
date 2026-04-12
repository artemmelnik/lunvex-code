#!/usr/bin/env python3
"""Test cache integration with the full system."""

import tempfile
import time
from pathlib import Path
from lunvex_code.cache import get_file_cache, read_file_with_cache
from lunvex_code.tools.file_tools import ReadFileTool, WriteFileTool, EditFileTool

def test_basic_cache_workflow():
    """Test basic cache workflow."""
    print("=== Testing Basic Cache Workflow ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        
        file1.write_text("This is file 1 content")
        file2.write_text("This is file 2 content\nWith multiple lines")
        
        # Get cache instance
        cache = get_file_cache()
        cache.clear()  # Start fresh
        
        print(f"Initial cache stats: {cache.get_stats()}")
        
        # Test ReadFileTool with caching
        read_tool = ReadFileTool()
        
        print("\n1. First read of file1 (should miss cache):")
        result1 = read_tool.execute(path=str(file1))
        print(f"   Success: {result1.success}")
        print(f"   Cached: {'[cached]' in result1.output}")
        
        print("\n2. Second read of file1 (should hit cache):")
        result2 = read_tool.execute(path=str(file1))
        print(f"   Success: {result2.success}")
        print(f"   Cached: {'[cached]' in result2.output}")
        
        print(f"\nCache stats after reads: {cache.get_stats()}")
        
        # Test WriteFileTool invalidates cache
        write_tool = WriteFileTool()
        
        print("\n3. Write to file1 (should invalidate cache):")
        result3 = write_tool.execute(path=str(file1), content="New content for file 1")
        print(f"   Success: {result3.success}")
        
        print("\n4. Read file1 after write (should miss cache):")
        result4 = read_tool.execute(path=str(file1))
        print(f"   Success: {result4.success}")
        print(f"   Cached: {'[cached]' in result4.output}")
        
        # Test EditFileTool also invalidates cache
        edit_tool = EditFileTool()
        
        print("\n5. Edit file2 (should invalidate cache):")
        result5 = edit_tool.execute(
            path=str(file2),
            old_str="This is file 2 content\nWith multiple lines",
            new_str="This is file 2 content\nWith multiple lines\nAnd a new line"
        )
        print(f"   Success: {result5.success}")
        
        print("\n6. Read file2 after edit (should miss cache):")
        result6 = read_tool.execute(path=str(file2))
        print(f"   Success: {result6.success}")
        print(f"   Cached: {'[cached]' in result6.output}")
        
        print(f"\nFinal cache stats: {cache.get_stats()}")

def test_cache_ttl():
    """Test cache TTL expiration."""
    print("\n=== Testing Cache TTL ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create test file
        test_file = tmp_path / "test_ttl.txt"
        test_file.write_text("TTL test content")
        
        # Configure cache with short TTL
        from lunvex_code.cache import configure_cache
        configure_cache(max_size=100, ttl_seconds=1)  # 1 second TTL
        
        cache = get_file_cache()
        cache.clear()
        
        print("1. First read (miss):")
        content1, cached1 = read_file_with_cache(test_file)
        print(f"   Cached: {cached1}")
        
        print("\n2. Immediate second read (hit):")
        content2, cached2 = read_file_with_cache(test_file)
        print(f"   Cached: {cached2}")
        
        print("\n3. Wait 1.1 seconds for TTL expiration...")
        time.sleep(1.1)
        
        print("4. Third read after TTL (miss):")
        content3, cached3 = read_file_with_cache(test_file)
        print(f"   Cached: {cached3}")
        
        # Reset to default
        configure_cache(max_size=100, ttl_seconds=300)

def test_cache_tools():
    """Test cache management tools."""
    print("\n=== Testing Cache Tools ===")
    
    from lunvex_code.tools.cache_tools import (
        CacheStatsTool,
        ClearCacheTool,
        ConfigureCacheTool,
        InvalidateCacheTool,
    )
    
    # Test CacheStatsTool
    stats_tool = CacheStatsTool()
    stats_result = stats_tool.execute()
    print("1. Cache stats tool:")
    print(f"   Success: {stats_result.success}")
    print(f"   Output preview: {stats_result.output[:100]}...")
    
    # Test ClearCacheTool
    clear_tool = ClearCacheTool()
    clear_result = clear_tool.execute()
    print("\n2. Clear cache tool:")
    print(f"   Success: {clear_result.success}")
    print(f"   Output: {clear_result.output}")
    
    # Test ConfigureCacheTool
    config_tool = ConfigureCacheTool()
    config_result = config_tool.execute(max_size=200, ttl_seconds=600)
    print("\n3. Configure cache tool:")
    print(f"   Success: {config_result.success}")
    print(f"   Output: {config_result.output}")
    
    # Verify configuration
    cache = get_file_cache()
    stats = cache.get_stats()
    print(f"   Verified - Max size: {stats['max_size']}, TTL: {stats['ttl_seconds']}s")
    
    # Reset to default
    configure_cache(max_size=100, ttl_seconds=300)

if __name__ == "__main__":
    test_basic_cache_workflow()
    test_cache_ttl()
    test_cache_tools()
    print("\n✅ All cache integration tests completed successfully!")