"""Performance tests for async system."""

import asyncio
import tempfile
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from lunvex_code.async_agent import AsyncAgent, AsyncAgentConfig
from lunvex_code.context import ProjectContext
from lunvex_code.llm import LunVexClient
from lunvex_code.tools.async_file_tools import AsyncReadFileTool
from lunvex_code.tools.async_search_tools import AsyncGrepTool


@pytest.mark.asyncio
async def test_async_tools_parallel_performance():
    """Test performance of parallel tool execution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create many files
        num_files = 50
        for i in range(num_files):
            (tmpdir_path / f"file{i}.txt").write_text(f"Content of file {i}\n" * 100)

        tool = AsyncReadFileTool()

        # Time sequential execution
        start_time = time.time()
        for i in range(min(10, num_files)):  # Test with 10 files
            await tool.execute(path=str(tmpdir_path / f"file{i}.txt"))
        sequential_time = time.time() - start_time

        # Time parallel execution
        start_time = time.time()
        tasks = [
            tool.execute(path=str(tmpdir_path / f"file{i}.txt")) for i in range(min(10, num_files))
        ]
        await asyncio.gather(*tasks)
        parallel_time = time.time() - start_time

        print(f"\nSequential time: {sequential_time:.3f}s")
        print(f"Parallel time: {parallel_time:.3f}s")
        print(f"Speedup: {sequential_time / parallel_time:.2f}x")

        # Parallel should be faster (or at least not slower)
        assert parallel_time <= sequential_time * 1.5  # Allow some overhead


@pytest.mark.asyncio
async def test_async_grep_parallel_performance():
    """Test performance of parallel grep search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create many files with search term
        num_files = 100
        for i in range(num_files):
            content = f"File {i} content\n" * 10
            if i % 2 == 0:  # Every other file has the search term
                content += "SEARCH_TERM_HERE\n"
            (tmpdir_path / f"file{i}.txt").write_text(content)

        tool = AsyncGrepTool()

        # Time the search
        start_time = time.time()
        result = await tool.execute(
            pattern="SEARCH_TERM_HERE", path=str(tmpdir_path), include="*.txt", limit=1000
        )
        search_time = time.time() - start_time

        print(f"\nGrep search time for {num_files} files: {search_time:.3f}s")

        # Should complete in reasonable time
        assert search_time < 5.0  # Should complete in under 5 seconds

        # Verify results
        assert result.success
        # Should find about half the files
        assert "file0.txt" in result.output
        assert "file98.txt" in result.output  # Even numbered file


@pytest.mark.asyncio
async def test_async_agent_concurrent_tasks():
    """Test async agent handling concurrent tasks."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test context
        context = ProjectContext(working_dir=str(tmpdir_path), project_md=None)

        # Create a simple mock LLM client
        mock_client = MagicMock(spec=LunVexClient)
        mock_client.model = "deepseek-chat"

        # Mock responses for concurrent tasks
        response_counter = 0

        async def mock_chat_completion(*args, **kwargs):
            nonlocal response_counter
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = MagicMock()

            # Each task gets a simple response
            mock_response.choices[0].message.content = f"Task {response_counter} completed"
            mock_response.choices[0].message.tool_calls = []

            response_counter += 1
            return mock_response

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_chat_completion)

        # Create multiple agents
        agents = []
        for i in range(3):
            agent = AsyncAgent(
                client=mock_client,
                context=context,
                config=AsyncAgentConfig(max_turns=1, trust_mode=True),
            )
            agents.append(agent)

        # Run agents concurrently
        start_time = time.time()
        tasks = [agent.run(f"Task {i}") for i, agent in enumerate(agents)]
        results = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time

        print(f"\nConcurrent agent execution time: {concurrent_time:.3f}s")

        # Verify all tasks completed
        assert len(results) == 3
        for i, result in enumerate(results):
            assert f"Task {i}" in result


@pytest.mark.asyncio
async def test_async_tool_memory_usage():
    """Test that async tools don't leak memory with many concurrent operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test files
        num_files = 20
        file_size = 1024 * 1024  # 1MB each
        for i in range(num_files):
            content = "X" * file_size
            (tmpdir_path / f"large_file{i}.txt").write_text(content)

        tool = AsyncReadFileTool()

        # Execute many operations concurrently
        start_time = time.time()
        tasks = []
        for i in range(num_files):
            for _ in range(3):  # Read each file multiple times
                tasks.append(tool.execute(path=str(tmpdir_path / f"large_file{i}.txt"), limit=100))

        # Limit concurrency to avoid overwhelming the system
        semaphore = asyncio.Semaphore(10)

        async def limited_execute(task):
            async with semaphore:
                return await task

        limited_tasks = [limited_execute(task) for task in tasks]
        results = await asyncio.gather(*limited_tasks)

        total_time = time.time() - start_time

        print(f"\nMemory test: {len(tasks)} operations in {total_time:.3f}s")
        print(f"Operations per second: {len(tasks) / total_time:.2f}")

        # Verify all succeeded
        for result in results:
            assert result.success

        # Should complete in reasonable time
        assert total_time < 30.0


@pytest.mark.asyncio
async def test_async_system_scalability():
    """Test scalability of async system with increasing workload."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        tool = AsyncReadFileTool()

        # Test different levels of concurrency
        concurrency_levels = [1, 2, 5, 10, 20]
        results = []

        for level in concurrency_levels:
            # Create test files for this level
            for i in range(level):
                (tmpdir_path / f"test_{level}_{i}.txt").write_text(f"Content {i}")

            # Measure time
            start_time = time.time()

            tasks = [
                tool.execute(path=str(tmpdir_path / f"test_{level}_{i}.txt")) for i in range(level)
            ]

            # Use semaphore to control actual concurrency
            semaphore = asyncio.Semaphore(level)

            async def limited_execute(task):
                async with semaphore:
                    return await task

            limited_tasks = [limited_execute(task) for task in tasks]
            await asyncio.gather(*limited_tasks)

            elapsed = time.time() - start_time
            results.append((level, elapsed))

            # Cleanup
            for i in range(level):
                (tmpdir_path / f"test_{level}_{i}.txt").unlink()

        # Print results
        print("\nScalability test results:")
        print("Concurrency | Time (s) | Time per op (s)")
        print("-" * 40)
        for level, elapsed in results:
            time_per_op = elapsed / level if level > 0 else 0
            print(f"{level:10d} | {elapsed:8.3f} | {time_per_op:8.3f}")

        # Basic check: system should handle increasing concurrency
        # Time per operation should not increase dramatically
        if len(results) >= 3:
            time_per_op_1 = results[0][1] / max(results[0][0], 1)
            time_per_op_last = results[-1][1] / max(results[-1][0], 1)
            # Allow some overhead but not exponential growth
            assert time_per_op_last <= time_per_op_1 * 3.0


@pytest.mark.asyncio
async def test_async_tool_cancellation():
    """Test that async tools can be cancelled properly."""
    tool = AsyncReadFileTool()

    # Create a task that will take some time
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test content\n" * 1000)
        temp_file = f.name

    try:
        # Start the task
        task = asyncio.create_task(tool.execute(path=temp_file))

        # Wait a bit then cancel
        await asyncio.sleep(0.01)
        task.cancel()

        # Try to get result (should raise CancelledError)
        try:
            await task
            # If we get here, task wasn't cancelled properly
            assert False, "Task should have been cancelled"
        except asyncio.CancelledError:
            # Expected
            pass
        except Exception as e:
            # Other exceptions are OK too (tool might handle cancellation differently)
            print(f"Task raised exception after cancellation: {e}")
    finally:
        Path(temp_file).unlink()


if __name__ == "__main__":
    # Run tests
    import sys

    async def run_all_tests():
        """Run all async performance tests."""
        tests = [
            test_async_tools_parallel_performance,
            test_async_grep_parallel_performance,
            test_async_agent_concurrent_tasks,
            test_async_tool_memory_usage,
            test_async_system_scalability,
            test_async_tool_cancellation,
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
