"""Smoke tests for async system - quick verification that everything works."""

import asyncio
import tempfile
from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_smoke_async_file_operations():
    """Smoke test: basic async file operations."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Smoke test content\nLine 2\nLine 3")
        temp_file = f.name

    try:
        from lunvex_code.tools.async_file_tools import AsyncReadFileTool

        tool = AsyncReadFileTool()
        result = await tool.execute(path=temp_file)

        assert result.success
        assert "Smoke test content" in result.output
        assert "Line 2" in result.output
        assert "Line 3" in result.output

        print("✅ Async file read: PASSED")
    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_smoke_async_write_and_read():
    """Smoke test: write and read file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        test_file = tmpdir_path / "smoke_test.txt"

        from lunvex_code.tools.async_file_tools import AsyncReadFileTool, AsyncWriteFileTool

        # Write file
        write_tool = AsyncWriteFileTool()
        write_result = await write_tool.execute(
            path=str(test_file), content="Smoke test write content\nWith multiple lines"
        )

        assert write_result.success
        assert test_file.exists()

        # Read file
        read_tool = AsyncReadFileTool()
        read_result = await read_tool.execute(path=str(test_file))

        assert read_result.success
        assert "Smoke test write content" in read_result.output

        print("✅ Async write/read: PASSED")


@pytest.mark.asyncio
async def test_smoke_async_search():
    """Smoke test: async search operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test files
        (tmpdir_path / "file1.txt").write_text("Search term here\nOther content")
        (tmpdir_path / "file2.txt").write_text("No match here\nJust text")
        (tmpdir_path / "file3.txt").write_text("Another Search term\nMore content")

        from lunvex_code.tools.async_search_tools import AsyncGrepTool

        tool = AsyncGrepTool()
        result = await tool.execute(pattern="Search term", path=str(tmpdir_path), include="*.txt")

        assert result.success
        assert "file1.txt" in result.output
        assert "file3.txt" in result.output
        assert "file2.txt" not in result.output  # No match

        print("✅ Async grep search: PASSED")


@pytest.mark.asyncio
async def test_smoke_async_bash():
    """Smoke test: async bash commands."""
    from lunvex_code.tools.async_bash_tool import AsyncBashTool

    tool = AsyncBashTool()

    # Test simple command
    result = await tool.execute(command="echo 'Smoke test'")

    assert result.success
    assert "Smoke test" in result.output

    print("✅ Async bash command: PASSED")


@pytest.mark.asyncio
async def test_smoke_async_agent_import():
    """Smoke test: async agent imports."""
    # Test that we can import all async agent components
    # Create mock components
    from unittest.mock import MagicMock

    from lunvex_code.async_agent import AsyncAgent, AsyncAgentConfig
    from lunvex_code.context import ProjectContext
    from lunvex_code.llm import LunVexClient

    mock_client = MagicMock(spec=LunVexClient)
    mock_context = MagicMock(spec=ProjectContext)
    mock_context.working_dir = "."
    mock_context.project_md = None

    # Create agent instance
    config = AsyncAgentConfig(max_turns=10, trust_mode=True)
    agent = AsyncAgent(client=mock_client, context=mock_context, config=config)

    assert agent is not None
    assert agent.config.max_turns == 10
    assert agent.config.trust_mode is True

    print("✅ Async agent imports: PASSED")


@pytest.mark.asyncio
async def test_smoke_async_tool_registry():
    """Smoke test: async tool registry."""
    from unittest.mock import MagicMock

    from lunvex_code.async_agent import AsyncAgent, AsyncAgentConfig
    from lunvex_code.context import ProjectContext
    from lunvex_code.llm import LunVexClient

    mock_client = MagicMock(spec=LunVexClient)
    mock_context = MagicMock(spec=ProjectContext)
    mock_context.working_dir = "."
    mock_context.project_md = None

    agent = AsyncAgent(client=mock_client, context=mock_context, config=AsyncAgentConfig())

    # Check registry was created
    assert agent.registry is not None

    # Check for key tools
    tool_names = [tool.name for tool in agent.registry._tools.values()]

    required_tools = [
        "read_file",
        "write_file",
        "edit_file",
        "glob",
        "grep",
        "bash",
        "fetch_url",
        "git_status",
        "git_diff",
        "git_log",
    ]

    for tool_name in required_tools:
        assert tool_name in tool_names, f"Missing tool: {tool_name}"

    print("✅ Async tool registry: PASSED")


@pytest.mark.asyncio
async def test_smoke_async_parallel_execution():
    """Smoke test: parallel execution of async tools."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create multiple files
        num_files = 5
        for i in range(num_files):
            (tmpdir_path / f"parallel_{i}.txt").write_text(f"Content {i}")

        from lunvex_code.tools.async_file_tools import AsyncReadFileTool

        tool = AsyncReadFileTool()

        # Create tasks
        tasks = [
            tool.execute(path=str(tmpdir_path / f"parallel_{i}.txt")) for i in range(num_files)
        ]

        # Execute in parallel
        results = await asyncio.gather(*tasks)

        # Verify all succeeded
        assert len(results) == num_files
        for i, result in enumerate(results):
            assert result.success
            assert f"Content {i}" in result.output

        print("✅ Async parallel execution: PASSED")


def test_smoke_sync_async_compatibility():
    """Smoke test: sync/async tool compatibility."""
    from lunvex_code.tools.async_file_tools import AsyncReadFileTool
    from lunvex_code.tools.file_tools import ReadFileTool

    sync_tool = ReadFileTool()
    async_tool = AsyncReadFileTool()

    # Check they have the same interface
    assert sync_tool.name == async_tool.name
    assert sync_tool.description == async_tool.description
    assert sync_tool.permission_level == async_tool.permission_level

    # Check parameters
    assert set(sync_tool.parameters.keys()) == set(async_tool.parameters.keys())

    print("✅ Sync/async compatibility: PASSED")


if __name__ == "__main__":
    """Run all smoke tests."""
    import sys

    async def run_all_smoke_tests():
        """Run all smoke tests."""
        tests = [
            test_smoke_async_file_operations,
            test_smoke_async_write_and_read,
            test_smoke_async_search,
            test_smoke_async_bash,
            test_smoke_async_agent_import,
            test_smoke_async_tool_registry,
            test_smoke_async_parallel_execution,
        ]

        print("=" * 70)
        print("ASYNC SYSTEM SMOKE TESTS")
        print("=" * 70)

        passed = 0
        failed = 0

        for test in tests:
            print(f"\n🔍 Running: {test.__name__}")
            print("-" * 40)

            try:
                await test()
                print(f"✅ {test.__name__}: PASSED")
                passed += 1
            except Exception as e:
                print(f"❌ {test.__name__}: FAILED - {e}")
                import traceback

                traceback.print_exc()
                failed += 1

        # Run sync test
        print("\n🔍 Running: test_smoke_sync_async_compatibility")
        print("-" * 40)
        try:
            test_smoke_sync_async_compatibility()
            print("✅ test_smoke_sync_async_compatibility: PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ test_smoke_sync_async_compatibility: FAILED - {e}")
            import traceback

            traceback.print_exc()
            failed += 1

        print("\n" + "=" * 70)
        print(f"SMOKE TEST SUMMARY: {passed} passed, {failed} failed")
        print("=" * 70)

        if failed == 0:
            print("\n🎉 ALL SMOKE TESTS PASSED! Async system is working correctly.")
        else:
            print(f"\n⚠️  {failed} smoke test(s) failed. Check output above.")

        return failed == 0

    # Run smoke tests
    success = asyncio.run(run_all_smoke_tests())
    sys.exit(0 if success else 1)
