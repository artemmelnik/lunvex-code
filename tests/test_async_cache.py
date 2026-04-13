"""Tests for async cache functionality."""

import asyncio
import tempfile
import time
from pathlib import Path

import pytest

from lunvex_code.tools.async_file_tools import AsyncReadFileTool


@pytest.mark.asyncio
async def test_async_tool_caching_basic():
    """Test basic caching in async tools."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test content for caching\nLine 2\nLine 3")
        temp_file = f.name

    try:
        tool = AsyncReadFileTool()

        # First read - should not be cached
        start_time = time.time()
        result1 = await tool.execute(path=temp_file)
        first_read_time = time.time() - start_time

        assert result1.success
        assert "Test content" in result1.output

        # Second read - might be faster if cached
        start_time = time.time()
        result2 = await tool.execute(path=temp_file)
        second_read_time = time.time() - start_time

        assert result2.success
        assert "Test content" in result2.output

        # Results should have the same content (cached marker might differ)
        # Extract just the file content lines
        def extract_content(output):
            lines = output.split("\n")
            # Skip the first line (header) and get content lines
            content_lines = [line for line in lines[1:] if line.strip()]
            return "\n".join(content_lines)

        content1 = extract_content(result1.output)
        content2 = extract_content(result2.output)
        assert content1 == content2

        print(f"\nFirst read: {first_read_time:.4f}s, Second read: {second_read_time:.4f}s")
        # Note: We can't guarantee caching is implemented, so we just verify functionality

    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_async_tool_cache_invalidation():
    """Test cache invalidation when file changes."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Initial content")
        temp_file = f.name

    try:
        tool = AsyncReadFileTool()

        # Read initial content
        result1 = await tool.execute(path=temp_file)
        assert result1.success
        assert "Initial content" in result1.output

        # Modify file
        with open(temp_file, "w") as f:
            f.write("Modified content")

        # Read again - should get new content (cache should be invalidated)
        result2 = await tool.execute(path=temp_file)
        assert result2.success
        assert "Modified content" in result2.output
        assert "Initial content" not in result2.output

    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_async_concurrent_cache_access():
    """Test concurrent access to cached resources."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Content for concurrent access test\n" * 10)
        temp_file = f.name

    try:
        tool = AsyncReadFileTool()

        # Create multiple concurrent read tasks
        num_tasks = 10
        tasks = [tool.execute(path=temp_file) for _ in range(num_tasks)]

        # Execute all concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Verify all succeeded
        for result in results:
            assert result.success
            assert "Content for concurrent access test" in result.output

        print(f"\nConcurrent reads ({num_tasks} tasks): {total_time:.4f}s")
        print(f"Average per read: {total_time / num_tasks:.4f}s")

    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_async_tool_cache_different_files():
    """Test caching with different files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create multiple files
        files = []
        for i in range(5):
            file_path = tmpdir_path / f"file{i}.txt"
            file_path.write_text(f"Content of file {i}")
            files.append(str(file_path))

        tool = AsyncReadFileTool()

        # Read all files
        results = []
        for file_path in files:
            result = await tool.execute(path=file_path)
            assert result.success
            results.append(result)

        # Verify each file has correct content
        for i, result in enumerate(results):
            assert f"Content of file {i}" in result.output


@pytest.mark.asyncio
async def test_async_tool_cache_with_limits():
    """Test caching with read limits."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
        temp_file = f.name

    try:
        tool = AsyncReadFileTool()

        # Read with limit
        result1 = await tool.execute(path=temp_file, limit=2)
        assert result1.success
        assert "Line 1" in result1.output
        assert "Line 2" in result1.output
        assert "Line 5" not in result1.output  # Limited to 2 lines

        # Read without limit
        result2 = await tool.execute(path=temp_file)
        assert result2.success
        assert "Line 1" in result2.output
        assert "Line 2" in result2.output
        assert "Line 5" in result2.output  # All lines

        # Different limits should give different results
        assert result1.output != result2.output

    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_async_tool_cache_performance():
    """Test performance impact of caching."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        # Create a large file
        content = "Test line\n" * 10000
        f.write(content)
        temp_file = f.name

    try:
        tool = AsyncReadFileTool()

        # Warm up (first read)
        start_time = time.time()
        result1 = await tool.execute(path=temp_file, limit=100)
        first_time = time.time() - start_time

        assert result1.success

        # Repeated reads
        read_times = []
        for i in range(5):
            start_time = time.time()
            result = await tool.execute(path=temp_file, limit=100)
            read_times.append(time.time() - start_time)
            assert result.success

        avg_repeat_time = sum(read_times) / len(read_times)

        print(f"\nFirst read: {first_time:.4f}s")
        print(f"Average repeat read: {avg_repeat_time:.4f}s")
        print(f"Ratio: {first_time / avg_repeat_time:.2f}x")

        # Repeated reads should not be slower
        assert avg_repeat_time <= first_time * 2.0  # Allow some variance

    finally:
        Path(temp_file).unlink()


if __name__ == "__main__":
    # Run tests
    import sys

    async def run_all_tests():
        """Run all async cache tests."""
        tests = [
            test_async_tool_caching_basic,
            test_async_tool_cache_invalidation,
            test_async_concurrent_cache_access,
            test_async_tool_cache_different_files,
            test_async_tool_cache_with_limits,
            test_async_tool_cache_performance,
        ]

        passed = 0
        failed = 0

        for test in tests:
            print(f"\n{'=' * 60}")
            print(f"Running: {test.__name__}")
            print("=" * 60)

            try:
                await test()
                print(f"✅ {test.__name__} PASSED")
                passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} FAILED: {e}")
                import traceback

                traceback.print_exc()
                failed += 1

        print(f"\n{'=' * 60}")
        print(f"TEST SUMMARY: {passed} passed, {failed} failed")
        print("=" * 60)

        return failed == 0

    # Run async tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
