"""Smoke tests for the LunVex Code system - quick verification that everything works."""

import tempfile
from pathlib import Path

from lunvex_code.tools.file_tools import ReadFileTool, WriteFileTool, EditFileTool
from lunvex_code.tools.search_tools import GlobTool, GrepTool
from lunvex_code.tools.bash_tool import BashTool
from lunvex_code.agent import Agent, AgentConfig
from lunvex_code.llm import LunVexClient
from lunvex_code.context import ProjectContext
from unittest.mock import MagicMock


def test_smoke_file_operations():
    """Smoke test: basic file operations."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Smoke test content\nLine 2\nLine 3")
        temp_file = f.name

    try:
        tool = ReadFileTool()
        result = tool.execute(path=temp_file)

        assert result.success
        assert "Smoke test content" in result.output
        assert "Line 2" in result.output
        assert "Line 3" in result.output

        print("✅ File read: PASSED")
    finally:
        Path(temp_file).unlink()


def test_smoke_write_and_read():
    """Smoke test: write and read file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        test_file = tmpdir_path / "smoke_test.txt"

        # Write file
        write_tool = WriteFileTool()
        write_result = write_tool.execute(
            path=str(test_file),
            content="Smoke test write content\nWith multiple lines"
        )

        assert write_result.success
        assert test_file.exists()

        # Read file
        read_tool = ReadFileTool()
        read_result = read_tool.execute(path=str(test_file))

        assert read_result.success
        assert "Smoke test write content" in read_result.output

        print("✅ Write/read: PASSED")


def test_smoke_search():
    """Smoke test: search operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test files
        (tmpdir_path / "file1.txt").write_text("Search term here\nOther content")
        (tmpdir_path / "file2.txt").write_text("No match here\nJust text")
        (tmpdir_path / "file3.txt").write_text("Another Search term\nMore content")

        tool = GrepTool()
        result = tool.execute(
            pattern="Search term",
            path=str(tmpdir_path),
            include="*.txt"
        )

        assert result.success
        assert "file1.txt" in result.output
        assert "file3.txt" in result.output
        assert "file2.txt" not in result.output  # No match

        print("✅ Grep search: PASSED")


def test_smoke_bash():
    """Smoke test: bash commands."""
    tool = BashTool()

    # Test simple command
    result = tool.execute(command="echo 'Smoke test'")

    assert result.success
    assert "Smoke test" in result.output

    print("✅ Bash command: PASSED")


def test_smoke_agent_import():
    """Smoke test: agent imports."""
    # Test that we can import all agent components
    from lunvex_code.agent import Agent, AgentConfig
    from lunvex_code.cli import create_and_run_agent

    # Create mock components
    mock_client = MagicMock(spec=LunVexClient)
    mock_context = MagicMock(spec=ProjectContext)
    mock_context.working_dir = "."
    mock_context.project_md = None

    # Create agent instance
    config = AgentConfig(max_turns=10, trust_mode=True)
    agent = Agent(
        client=mock_client,
        context=mock_context,
        config=config
    )

    assert agent is not None
    assert agent.config.max_turns == 10
    assert agent.config.trust_mode is True

    print("✅ Agent imports: PASSED")


def test_smoke_tool_registry():
    """Smoke test: tool registry."""
    from lunvex_code.agent import Agent, AgentConfig
    from unittest.mock import MagicMock
    from lunvex_code.llm import LunVexClient
    from lunvex_code.context import ProjectContext

    mock_client = MagicMock(spec=LunVexClient)
    mock_context = MagicMock(spec=ProjectContext)
    mock_context.working_dir = "."
    mock_context.project_md = None

    agent = Agent(
        client=mock_client,
        context=mock_context,
        config=AgentConfig()
    )

    # Check registry was created
    assert agent.registry is not None

    # Check for key tools
    tool_names = [tool.name for tool in agent.registry._tools.values()]

    required_tools = [
        "read_file", "write_file", "edit_file",
        "glob", "grep", "bash", "fetch_url",
        "git_status", "git_diff", "git_log"
    ]

    for tool_name in required_tools:
        assert tool_name in tool_names, f"Missing tool: {tool_name}"

    print("✅ Tool registry: PASSED")


def run_all_smoke_tests():
    """Run all smoke tests."""
    tests = [
        test_smoke_file_operations,
        test_smoke_write_and_read,
        test_smoke_search,
        test_smoke_bash,
        test_smoke_agent_import,
        test_smoke_tool_registry,
    ]

    print("=" * 70)
    print("SYSTEM SMOKE TESTS")
    print("=" * 70)

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n🔍 Running: {test.__name__}")
        print("-" * 40)

        try:
            test()
            print(f"✅ {test.__name__}: PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: FAILED - {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n" + "=" * 70)
    print(f"SMOKE TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 ALL SMOKE TESTS PASSED! System is working correctly.")
    else:
        print(f"\n⚠️  {failed} smoke test(s) failed. Check output above.")

    return failed == 0


if __name__ == "__main__":
    """Run all smoke tests."""
    import sys
    
    success = run_all_smoke_tests()
    sys.exit(0 if success else 1)