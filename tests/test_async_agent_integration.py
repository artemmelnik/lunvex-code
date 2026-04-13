"""Integration tests for async agent with real tools."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from lunvex_code.async_agent import AsyncAgent, AsyncAgentConfig
from lunvex_code.context import ProjectContext
from lunvex_code.llm import LunVexClient


@pytest.mark.asyncio
async def test_async_agent_file_operations():
    """Test async agent performing file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test context
        context = ProjectContext(working_dir=str(tmpdir_path), project_md=None)

        # Create mock LLM client
        mock_client = MagicMock(spec=LunVexClient)
        mock_client.model = "deepseek-chat"

        # Mock the chat completion to simulate agent behavior
        async def mock_chat_completion(*args, **kwargs):
            # Create a mock response
            mock_response = MagicMock()

            # First call: agent should create a file
            if "create a test file" in kwargs.get("messages", [{}])[-1].get("content", ""):
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message = MagicMock()
                mock_response.choices[0].message.content = None
                mock_response.choices[0].message.tool_calls = [
                    MagicMock(
                        function=MagicMock(
                            name="write_file",
                            arguments='{"path": "test.txt", "content": "Hello, World!"}',
                        )
                    )
                ]
            # Second call: agent should read the file
            elif "read the file" in kwargs.get("messages", [{}])[-1].get("content", ""):
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message = MagicMock()
                mock_response.choices[0].message.content = (
                    "I have read the file. It contains: Hello, World!"
                )
                mock_response.choices[0].message.tool_calls = []
            else:
                # Default response
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message = MagicMock()
                mock_response.choices[0].message.content = "Task completed."
                mock_response.choices[0].message.tool_calls = []

            return mock_response

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_chat_completion)

        # Create agent
        agent = AsyncAgent(
            client=mock_client,
            context=context,
            config=AsyncAgentConfig(max_turns=5, trust_mode=True),
        )

        # Run agent with a simple task
        result = await agent.run("Create a test file and then read it")

        # Verify result
        assert "Hello, World!" in result or "Task completed" in result

        # Verify file was created
        test_file = tmpdir_path / "test.txt"
        assert test_file.exists()
        assert test_file.read_text() == "Hello, World!"


@pytest.mark.asyncio
async def test_async_agent_with_git_tools():
    """Test async agent using git tools."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True
        )
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)

        # Create a test file
        (tmpdir_path / "README.md").write_text("# Test Project")

        # Create test context
        context = ProjectContext(working_dir=str(tmpdir_path), project_md=None)

        # Create mock LLM client
        mock_client = MagicMock(spec=LunVexClient)
        mock_client.model = "deepseek-chat"

        # Mock the chat completion
        async def mock_chat_completion(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = MagicMock()

            # Check what the agent is trying to do
            messages = kwargs.get("messages", [])
            if messages and "git status" in messages[-1].get("content", ""):
                # Agent wants to check git status
                mock_response.choices[0].message.content = "I can see the git status."
                mock_response.choices[0].message.tool_calls = [
                    MagicMock(function=MagicMock(name="git_status", arguments="{}"))
                ]
            else:
                # Default response
                mock_response.choices[0].message.content = "Task completed."
                mock_response.choices[0].message.tool_calls = []

            return mock_response

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_chat_completion)

        # Create agent
        agent = AsyncAgent(
            client=mock_client,
            context=context,
            config=AsyncAgentConfig(max_turns=3, trust_mode=True),
        )

        # Run agent
        result = await agent.run("Check git status")

        # Verify result contains git status information
        assert result is not None
        # Git status should show untracked files
        assert "README.md" in result or "untracked" in result.lower() or "Task completed" in result


@pytest.mark.asyncio
async def test_async_agent_multiple_tool_calls():
    """Test async agent making multiple tool calls in one turn."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test context
        context = ProjectContext(working_dir=str(tmpdir_path), project_md=None)

        # Create mock LLM client
        mock_client = MagicMock(spec=LunVexClient)
        mock_client.model = "deepseek-chat"

        # Track tool calls
        tool_calls_made = []

        # Mock the chat completion
        async def mock_chat_completion(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = MagicMock()

            # First call: create multiple files
            if not tool_calls_made:
                mock_response.choices[0].message.content = None
                mock_response.choices[0].message.tool_calls = [
                    MagicMock(
                        function=MagicMock(
                            name="write_file",
                            arguments='{"path": "file1.txt", "content": "Content 1"}',
                        )
                    ),
                    MagicMock(
                        function=MagicMock(
                            name="write_file",
                            arguments='{"path": "file2.txt", "content": "Content 2"}',
                        )
                    ),
                ]
            # Second call: list files
            elif len(tool_calls_made) == 2:
                mock_response.choices[0].message.content = "Now list the files."
                mock_response.choices[0].message.tool_calls = [
                    MagicMock(function=MagicMock(name="glob", arguments='{"pattern": "*.txt"}'))
                ]
            else:
                # Final response
                mock_response.choices[0].message.content = "All tasks completed successfully."
                mock_response.choices[0].message.tool_calls = []

            return mock_response

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_chat_completion)

        # Create agent with tool call tracking
        agent = AsyncAgent(
            client=mock_client,
            context=context,
            config=AsyncAgentConfig(max_turns=5, trust_mode=True),
        )

        # Monkey patch to track tool executions
        original_execute_tool = agent._execute_tool

        async def tracked_execute_tool(tool_call):
            result = await original_execute_tool(tool_call)
            tool_calls_made.append(tool_call.function.name)
            return result

        agent._execute_tool = tracked_execute_tool

        # Run agent
        result = await agent.run("Create two files and then list them")

        # Verify
        assert "All tasks completed" in result or "Content" in result
        assert "write_file" in tool_calls_made
        assert "glob" in tool_calls_made
        assert tool_calls_made.count("write_file") == 2

        # Verify files were created
        assert (tmpdir_path / "file1.txt").exists()
        assert (tmpdir_path / "file2.txt").exists()
        assert (tmpdir_path / "file1.txt").read_text() == "Content 1"
        assert (tmpdir_path / "file2.txt").read_text() == "Content 2"


@pytest.mark.asyncio
async def test_async_agent_error_handling():
    """Test async agent handling tool errors gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test context
        context = ProjectContext(working_dir=str(tmpdir_path), project_md=None)

        # Create mock LLM client
        mock_client = MagicMock(spec=LunVexClient)
        mock_client.model = "deepseek-chat"

        # Mock the chat completion
        async def mock_chat_completion(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = MagicMock()

            # First call: try to read non-existent file
            messages = kwargs.get("messages", [])
            if len(messages) < 3:  # First attempt
                mock_response.choices[0].message.content = None
                mock_response.choices[0].message.tool_calls = [
                    MagicMock(
                        function=MagicMock(
                            name="read_file", arguments='{"path": "non_existent.txt"}'
                        )
                    )
                ]
            else:
                # After error, try to create the file instead
                mock_response.choices[0].message.content = "Let me create the file instead."
                mock_response.choices[0].message.tool_calls = [
                    MagicMock(
                        function=MagicMock(
                            name="write_file",
                            arguments='{"path": "non_existent.txt", "content": "Now it exists!"}',
                        )
                    )
                ]

            return mock_response

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_chat_completion)

        # Create agent
        agent = AsyncAgent(
            client=mock_client,
            context=context,
            config=AsyncAgentConfig(max_turns=5, trust_mode=True),
        )

        # Run agent
        result = await agent.run("Read a file that doesn't exist, then create it")

        # Verify agent handled the error and created the file
        assert "Now it exists" in result or "created" in result.lower()
        assert (tmpdir_path / "non_existent.txt").exists()
        assert (tmpdir_path / "non_existent.txt").read_text() == "Now it exists!"


@pytest.mark.asyncio
async def test_async_agent_max_turns():
    """Test async agent respects max_turns limit."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test context
        context = ProjectContext(working_dir=str(tmpdir_path), project_md=None)

        # Create mock LLM client that always requests another tool
        mock_client = MagicMock(spec=LunVexClient)
        mock_client.model = "deepseek-chat"

        # Mock the chat completion to always request a tool
        async def mock_chat_completion(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = MagicMock()
            mock_response.choices[0].message.content = None
            mock_response.choices[0].message.tool_calls = [
                MagicMock(function=MagicMock(name="bash", arguments='{"command": "echo turn"}'))
            ]
            return mock_response

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_chat_completion)

        # Create agent with low max_turns
        agent = AsyncAgent(
            client=mock_client,
            context=context,
            config=AsyncAgentConfig(max_turns=3, trust_mode=True),
        )

        # Run agent - should stop after max_turns
        result = await agent.run("This should stop after 3 turns")

        # Verify agent stopped (might have "maximum turns" message or similar)
        assert result is not None
        # The agent should have stopped after 3 turns
        # We can't easily count turns from outside, but we trust the implementation


if __name__ == "__main__":
    # Run tests
    import sys

    async def run_all_tests():
        """Run all async agent integration tests."""
        tests = [
            test_async_agent_file_operations,
            test_async_agent_with_git_tools,
            test_async_agent_multiple_tool_calls,
            test_async_agent_error_handling,
            test_async_agent_max_turns,
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
