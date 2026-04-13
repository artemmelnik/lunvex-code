"""Tests for async CLI."""

import asyncio
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from lunvex_code.async_agent import AsyncAgent, AsyncAgentConfig
from lunvex_code.async_cli import create_and_run_agent_async
from lunvex_code.async_cli import interactive_loop_async as async_cli_interactive_loop_async
from lunvex_code.context import ProjectContext
from lunvex_code.llm import LunVexClient
from lunvex_code.main import interactive_loop_async as main_interactive_loop_async


class FakeAsyncPromptSession:
    """Minimal async prompt session for REPL tests."""

    def __init__(self, responses):
        self._responses = iter(responses)
        self.prompt_calls = 0
        self.prompt_async_calls = 0

    def prompt(self, *_args, **_kwargs):
        self.prompt_calls += 1
        raise AssertionError("interactive async loop should not use sync prompt()")

    async def prompt_async(self, *_args, **_kwargs):
        self.prompt_async_calls += 1
        return next(self._responses)


@pytest.mark.asyncio
async def test_async_cli_agent_creation():
    """Test async CLI agent creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create a simple LUNVEX.md for context
        lunvex_content = """# Test Project

## Project Overview
Test project for async CLI testing.
"""
        (tmpdir_path / "LUNVEX.md").write_text(lunvex_content)

        # Mock the API key
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"}):
            # Mock the LunVexClient to avoid actual API calls
            with patch("lunvex_code.async_cli.LunVexClient") as mock_client:
                mock_instance = MagicMock(spec=LunVexClient)
                mock_instance.model = "deepseek-chat"
                mock_client.return_value = mock_instance

                # Mock the agent run method
                with patch("lunvex_code.async_cli.AsyncAgent") as mock_agent_class:
                    mock_agent = MagicMock(spec=AsyncAgent)

                    # Make run method async
                    async def async_run(task):
                        return "Test response"

                    mock_agent.run = MagicMock(side_effect=async_run)
                    mock_agent_class.return_value = mock_agent

                    # Test single task mode
                    try:
                        await create_and_run_agent_async(
                            task="Test task",
                            model="deepseek-chat",
                            trust=False,
                            yolo=False,
                            max_turns=10,
                            verbose=False,
                            no_context=False,
                            no_animation=True,
                        )
                    except SystemExit:
                        pass  # Expected exit after task completion

                    # Verify agent was created
                    mock_agent_class.assert_called_once()
                    mock_agent.run.assert_called_once_with("Test task")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("interactive_loop", "session_patch", "goodbye_patch"),
    [
        (
            main_interactive_loop_async,
            "lunvex_code.main.get_prompt_session",
            "lunvex_code.main.ui.print_goodbye",
        ),
        (
            async_cli_interactive_loop_async,
            "lunvex_code.async_cli.get_prompt_session",
            "lunvex_code.async_cli.ui.print_goodbye",
        ),
    ],
)
async def test_interactive_loops_use_async_prompt(interactive_loop, session_patch, goodbye_patch):
    """Interactive mode should use the async prompt API inside the running event loop."""

    async def async_chat(_message):
        return None

    mock_agent = SimpleNamespace(
        permissions=SimpleNamespace(yolo_mode=False, trust_mode=False),
        config=SimpleNamespace(yolo_mode=False, trust_mode=False),
        client=SimpleNamespace(model="deepseek-chat"),
        chat=MagicMock(side_effect=async_chat),
    )

    session = FakeAsyncPromptSession(["help", "quit"])

    with patch(session_patch, return_value=session):
        with patch(goodbye_patch):
            await interactive_loop(mock_agent)

    assert session.prompt_calls == 0
    assert session.prompt_async_calls == 2
    mock_agent.chat.assert_not_called()


@pytest.mark.asyncio
async def test_async_agent_config():
    """Test async agent configuration."""
    config = AsyncAgentConfig(max_turns=20, trust_mode=True, yolo_mode=False, verbose=True)

    assert config.max_turns == 20
    assert config.trust_mode is True
    assert config.yolo_mode is False
    assert config.verbose is True


@pytest.mark.asyncio
async def test_async_agent_creation():
    """Test async agent creation."""
    # Create mocks
    mock_client = MagicMock(spec=LunVexClient)
    mock_context = MagicMock(spec=ProjectContext)
    mock_context.working_dir = "."
    mock_context.project_md = None

    config = AsyncAgentConfig(trust_mode=True)

    # Create agent
    agent = AsyncAgent(client=mock_client, context=mock_context, config=config)

    assert agent.client == mock_client
    assert agent.context == mock_context
    assert agent.config == config
    assert agent.permissions.trust_mode is True
    assert agent.permissions.yolo_mode is False


def test_async_cli_imports():
    """Test that async CLI imports work correctly."""
    # Test that we can import all async components
    from lunvex_code.async_agent import AsyncAgent, AsyncAgentConfig
    from lunvex_code.async_cli import app, console, get_prompt_session
    from lunvex_code.tools.async_bash_tool import AsyncBashTool
    from lunvex_code.tools.async_file_tools import AsyncReadFileTool, AsyncWriteFileTool
    from lunvex_code.tools.async_search_tools import AsyncGlobTool, AsyncGrepTool
    from lunvex_code.tools.async_web_tools import AsyncFetchURLTool

    # Verify imports
    assert app is not None
    assert console is not None
    assert get_prompt_session is not None
    assert AsyncAgent is not None
    assert AsyncAgentConfig is not None
    assert AsyncReadFileTool is not None
    assert AsyncWriteFileTool is not None
    assert AsyncGlobTool is not None
    assert AsyncGrepTool is not None
    assert AsyncBashTool is not None
    assert AsyncFetchURLTool is not None


@pytest.mark.asyncio
async def test_async_tool_registry():
    """Test that async agent creates proper tool registry."""
    from lunvex_code.async_agent import AsyncAgent

    # Create mocks
    mock_client = MagicMock(spec=LunVexClient)
    mock_context = MagicMock(spec=ProjectContext)
    mock_context.working_dir = "."
    mock_context.project_md = None

    # Create agent
    agent = AsyncAgent(client=mock_client, context=mock_context, config=AsyncAgentConfig())

    # Check that registry was created
    assert agent.registry is not None

    # Check that it contains expected tools
    tool_names = [tool.name for tool in agent.registry._tools.values()]

    # Check for async tools
    assert "read_file" in tool_names
    assert "write_file" in tool_names
    assert "edit_file" in tool_names
    assert "glob" in tool_names
    assert "grep" in tool_names
    assert "bash" in tool_names
    assert "fetch_url" in tool_names

    # Check for sync Git tools
    assert "git_status" in tool_names
    assert "git_diff" in tool_names
    assert "git_log" in tool_names


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_async_cli_agent_creation())
    print("✅ test_async_cli_agent_creation passed")

    asyncio.run(test_async_agent_config())
    print("✅ test_async_agent_config passed")

    asyncio.run(test_async_agent_creation())
    print("✅ test_async_agent_creation passed")

    test_async_cli_imports()
    print("✅ test_async_cli_imports passed")

    asyncio.run(test_async_tool_registry())
    print("✅ test_async_tool_registry passed")

    print("\n✅ All async CLI tests passed!")
