"""Error handling tests for async system."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lunvex_code.async_agent import AsyncAgent, AsyncAgentConfig
from lunvex_code.context import ProjectContext
from lunvex_code.llm import LunVexClient
from lunvex_code.tools.async_bash_tool import AsyncBashTool
from lunvex_code.tools.async_file_tools import (
    AsyncEditFileTool,
    AsyncReadFileTool,
    AsyncWriteFileTool,
)
from lunvex_code.tools.async_search_tools import AsyncGlobTool, AsyncGrepTool
from lunvex_code.tools.async_web_tools import AsyncFetchURLTool


@pytest.mark.asyncio
async def test_async_read_file_nonexistent():
    """Test async read file tool with non-existent file."""
    tool = AsyncReadFileTool()

    result = await tool.execute(path="/nonexistent/path/file.txt")

    assert not result.success
    assert "No such file" in result.error or "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_async_read_file_permission_denied():
    """Test async read file tool with permission denied."""
    tool = AsyncReadFileTool()

    # Try to read a directory (should fail)
    result = await tool.execute(path="/")

    assert not result.success
    # Different systems may give different error messages
    error_lower = result.error.lower()
    assert any(
        word in error_lower
        for word in ["error", "permission", "directory", "access", "denied", "cannot"]
    )


@pytest.mark.asyncio
async def test_async_write_file_invalid_path():
    """Test async write file tool with invalid path."""
    tool = AsyncWriteFileTool()

    # Try to write to root directory (should fail)
    result = await tool.execute(path="/test.txt", content="Test")

    assert not result.success
    # Different systems may give different error messages
    error_lower = result.error.lower()
    assert any(
        word in error_lower
        for word in ["error", "permission", "access", "denied", "cannot", "failed"]
    )


@pytest.mark.asyncio
async def test_async_edit_file_nonexistent():
    """Test async edit file tool with non-existent file."""
    tool = AsyncEditFileTool()

    result = await tool.execute(path="/nonexistent/path/file.txt", old_str="old", new_str="new")

    assert not result.success
    assert "No such file" in result.error or "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_async_edit_file_string_not_found():
    """Test async edit file tool with string not found."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3\n")
        temp_file = f.name

    try:
        tool = AsyncEditFileTool()

        result = await tool.execute(
            path=temp_file, old_str="Non-existent string", new_str="New string"
        )

        assert not result.success
        assert "not found" in result.error.lower() or "unique" in result.error.lower()
    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_async_glob_invalid_pattern():
    """Test async glob tool with invalid pattern."""
    tool = AsyncGlobTool()

    result = await tool.execute(pattern="[invalid", path=".")

    assert not result.success
    # Pattern may or may not cause an error depending on implementation
    # Just check that it didn't succeed
    assert result.error or not result.success


@pytest.mark.asyncio
async def test_async_grep_invalid_regex():
    """Test async grep tool with invalid regex pattern."""
    tool = AsyncGrepTool()

    result = await tool.execute(pattern="[invalid-regex", path=".")

    assert not result.success
    assert "error" in result.error.lower() or "invalid" in result.error.lower()


@pytest.mark.asyncio
async def test_async_bash_dangerous_command():
    """Test async bash tool with dangerous command."""
    tool = AsyncBashTool()

    # Test various dangerous commands
    dangerous_commands = [
        "rm -rf /",
        "rm -rf /*",
        ":(){ :|:& };:",  # Fork bomb
        "mkfs.ext4 /dev/sda1",
        "dd if=/dev/zero of=/dev/sda",
    ]

    for cmd in dangerous_commands:
        result = await tool.execute(command=cmd)
        assert not result.success
        assert (
            "blocked" in result.error.lower()
            or "dangerous" in result.error.lower()
            or "not allowed" in result.error.lower()
        )


@pytest.mark.asyncio
async def test_async_bash_command_not_found():
    """Test async bash tool with non-existent command."""
    tool = AsyncBashTool()

    result = await tool.execute(command="nonexistentcommand12345")

    assert not result.success
    assert "not found" in result.error.lower() or "command" in result.error.lower()


@pytest.mark.asyncio
async def test_async_fetch_url_network_error():
    """Test async fetch URL tool with network error."""
    tool = AsyncFetchURLTool()

    # Mock fetch_url to raise an exception
    with patch("lunvex_code.tools.async_web_tools.fetch_url") as mock_fetch:
        mock_fetch.side_effect = Exception("Simulated network error")

        result = await tool.execute(url="https://example.com")

        assert not result.success
        assert "error" in result.error.lower()


@pytest.mark.asyncio
async def test_async_agent_tool_execution_error():
    """Test async agent handling tool execution errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test context
        context = ProjectContext(working_dir=str(tmpdir_path), project_md=None)

        # Create mock LLM client
        mock_client = MagicMock(spec=LunVexClient)
        mock_client.model = "deepseek-chat"

        # Mock the chat completion to request reading non-existent file
        async def mock_chat_completion(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = MagicMock()
            mock_response.choices[0].message.content = None
            mock_response.choices[0].message.tool_calls = [
                MagicMock(
                    function=MagicMock(
                        name="read_file", arguments='{"path": "/nonexistent/file.txt"}'
                    )
                )
            ]
            return mock_response

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_chat_completion)

        # Create agent
        agent = AsyncAgent(
            client=mock_client,
            context=context,
            config=AsyncAgentConfig(max_turns=3, trust_mode=True),
        )

        # Run agent - should handle the error gracefully
        result = await agent.run("Try to read a non-existent file")

        # Agent should report the error
        assert result is not None
        assert (
            "error" in result.lower() or "not found" in result.lower() or "failed" in result.lower()
        )


@pytest.mark.asyncio
async def test_async_agent_llm_error():
    """Test async agent handling LLM errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test context
        context = ProjectContext(working_dir=str(tmpdir_path), project_md=None)

        # Create mock LLM client that raises an error
        mock_client = MagicMock(spec=LunVexClient)
        mock_client.model = "deepseek-chat"
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("LLM API error: Rate limit exceeded")
        )

        # Create agent
        agent = AsyncAgent(
            client=mock_client,
            context=context,
            config=AsyncAgentConfig(max_turns=3, trust_mode=True),
        )

        # Run agent - should handle the LLM error
        result = await agent.run("Simple task")

        # Agent should report the error
        assert result is not None
        assert "error" in result.lower() or "failed" in result.lower() or "LLM" in result


@pytest.mark.asyncio
async def test_async_tool_timeout_propagation():
    """Test that timeouts are properly propagated in async tools."""
    tool = AsyncBashTool()

    # Test a command that would timeout
    result = await tool.execute(command="sleep 10", timeout=0.1)

    assert not result.success
    assert "timeout" in result.error.lower() or "timed out" in result.error.lower()


@pytest.mark.asyncio
async def test_async_agent_with_failing_tools_continues():
    """Test that async agent continues after tool failures."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test context
        context = ProjectContext(working_dir=str(tmpdir_path), project_md=None)

        # Create mock LLM client
        mock_client = MagicMock(spec=LunVexClient)
        mock_client.model = "deepseek-chat"

        call_count = 0

        async def mock_chat_completion(*args, **kwargs):
            nonlocal call_count
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = MagicMock()

            call_count += 1

            if call_count == 1:
                # First: try to read non-existent file (will fail)
                mock_response.choices[0].message.content = None
                mock_response.choices[0].message.tool_calls = [
                    MagicMock(
                        function=MagicMock(
                            name="read_file", arguments='{"path": "/nonexistent/file.txt"}'
                        )
                    )
                ]
            elif call_count == 2:
                # Second: after error, create a file instead
                mock_response.choices[0].message.content = "Let me create a file instead."
                mock_response.choices[0].message.tool_calls = [
                    MagicMock(
                        function=MagicMock(
                            name="write_file",
                            arguments='{"path": "recovery.txt", "content": "Recovered!"}',
                        )
                    )
                ]
            else:
                # Final response
                mock_response.choices[0].message.content = "Task completed with recovery."
                mock_response.choices[0].message.tool_calls = []

            return mock_response

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_chat_completion)

        # Create agent
        agent = AsyncAgent(
            client=mock_client,
            context=context,
            config=AsyncAgentConfig(max_turns=5, trust_mode=True),
        )

        # Run agent
        result = await agent.run("Try to read non-existent file, then recover")

        # Verify recovery happened
        assert "recovery.txt" in result or "Recovered" in result or "completed" in result.lower()
        assert (tmpdir_path / "recovery.txt").exists()
        assert (tmpdir_path / "recovery.txt").read_text() == "Recovered!"


@pytest.mark.asyncio
async def test_async_tool_concurrent_errors():
    """Test handling of concurrent errors in async tools."""
    tool = AsyncReadFileTool()

    # Create tasks that will all fail
    tasks = [tool.execute(path=f"/nonexistent/file{i}.txt") for i in range(5)]

    # Execute all concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # All should have failed
    for result in results:
        if isinstance(result, Exception):
            # Exception was raised (not caught by tool)
            pass
        else:
            # Tool caught the error and returned error result
            assert not result.success
            assert "error" in result.error.lower() or "not found" in result.error.lower()


if __name__ == "__main__":
    # Run tests
    import sys

    async def run_all_tests():
        """Run all async error handling tests."""
        tests = [
            test_async_read_file_nonexistent,
            test_async_read_file_permission_denied,
            test_async_write_file_invalid_path,
            test_async_edit_file_nonexistent,
            test_async_edit_file_string_not_found,
            test_async_glob_invalid_pattern,
            test_async_grep_invalid_regex,
            test_async_bash_dangerous_command,
            test_async_bash_command_not_found,
            test_async_fetch_url_network_error,
            test_async_agent_tool_execution_error,
            test_async_agent_llm_error,
            test_async_tool_timeout_propagation,
            test_async_agent_with_failing_tools_continues,
            test_async_tool_concurrent_errors,
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
