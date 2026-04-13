"""Simple tests for async agent."""

from lunvex_code.async_agent import AsyncAgent, AsyncAgentConfig


def test_async_agent_config():
    """Test async agent configuration."""
    config = AsyncAgentConfig(max_turns=20, trust_mode=True, yolo_mode=False, verbose=True)

    assert config.max_turns == 20
    assert config.trust_mode is True
    assert config.yolo_mode is False
    assert config.verbose is True

    # Test defaults
    default_config = AsyncAgentConfig()
    assert default_config.max_turns == 50
    assert default_config.trust_mode is False
    assert default_config.yolo_mode is False
    assert default_config.verbose is False


def test_async_agent_initialization():
    """Test async agent initialization."""
    from unittest.mock import MagicMock

    from lunvex_code.context import ProjectContext
    from lunvex_code.llm import LunVexClient

    # Create mocks
    mock_client = MagicMock(spec=LunVexClient)
    mock_context = MagicMock(spec=ProjectContext)
    mock_context.working_dir = "."
    mock_context.project_md = None

    # Create agent with default config
    agent = AsyncAgent(client=mock_client, context=mock_context)

    assert agent.client == mock_client
    assert agent.context == mock_context
    assert isinstance(agent.config, AsyncAgentConfig)
    assert agent.config.max_turns == 50  # Default value

    # Create agent with custom config
    config = AsyncAgentConfig(max_turns=30, trust_mode=True)
    agent = AsyncAgent(client=mock_client, context=mock_context, config=config)

    assert agent.config == config
    assert agent.config.max_turns == 30
    assert agent.config.trust_mode is True


def test_async_agent_tool_registry():
    """Test async agent tool registry creation."""
    from unittest.mock import MagicMock

    from lunvex_code.context import ProjectContext
    from lunvex_code.llm import LunVexClient

    # Create mocks
    mock_client = MagicMock(spec=LunVexClient)
    mock_context = MagicMock(spec=ProjectContext)
    mock_context.working_dir = "."
    mock_context.project_md = None

    # Create agent
    agent = AsyncAgent(client=mock_client, context=mock_context)

    # Check that registry was created
    assert agent.registry is not None

    # Check that it contains expected tools
    tool_names = [tool.name for tool in agent.registry._tools.values()]

    # Check for async tools
    expected_tools = ["read_file", "write_file", "edit_file", "glob", "grep", "bash", "fetch_url"]

    for tool_name in expected_tools:
        assert tool_name in tool_names, f"Missing tool: {tool_name}"

    # Check for sync Git tools (they should be there too)
    git_tools = ["git_status", "git_diff", "git_log"]
    for git_tool in git_tools:
        assert git_tool in tool_names, f"Missing git tool: {git_tool}"


def test_async_agent_system_prompt():
    """Test async agent system prompt generation."""
    from unittest.mock import MagicMock

    from lunvex_code.context import ProjectContext
    from lunvex_code.llm import LunVexClient

    # Create mocks
    mock_client = MagicMock(spec=LunVexClient)
    mock_context = MagicMock(spec=ProjectContext)
    mock_context.working_dir = "/test/path"
    mock_context.project_md = "# Test Project\n\nTest description"

    # Create agent
    agent = AsyncAgent(client=mock_client, context=mock_context)

    # Check system prompt was created
    assert agent.system_prompt is not None
    assert isinstance(agent.system_prompt, str)
    assert len(agent.system_prompt) > 0

    # Should contain context information
    assert "/test/path" in agent.system_prompt
    assert "Test Project" in agent.system_prompt


if __name__ == "__main__":
    # Run tests
    tests = [
        test_async_agent_config,
        test_async_agent_initialization,
        test_async_agent_tool_registry,
        test_async_agent_system_prompt,
    ]

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n{'=' * 60}")
        print(f"Running: {test.__name__}")
        print("=" * 60)

        try:
            test()
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

    import sys

    sys.exit(0 if failed == 0 else 1)
