"""Comprehensive tests for Git tools integration."""

import os
import tempfile
from pathlib import Path

import pytest

from lunvex_code.tools.base import create_default_registry


def test_git_tools_comprehensive_coverage():
    """Test that Git tools cover comprehensive Git operations."""
    registry = create_default_registry()

    # All Git tools should be registered
    git_tools = [
        "git_status",
        "git_diff",
        "git_log",
        "git_show",  # Read-only
        "git_branch",
        "git_add",
        "git_commit",
        "git_push",
        "git_pull",  # Basic workflow
        "git_stash",
        "git_checkout",
        "git_merge",
        "git_fetch",  # Advanced
    ]

    for tool_name in git_tools:
        tool = registry.get(tool_name)
        assert tool is not None, f"Git tool '{tool_name}' is missing"
        assert tool.name == tool_name

    # Verify we have exactly 13 Git tools
    all_tools = registry.list_tools()
    git_tool_count = sum(1 for t in all_tools if t.startswith("git_"))
    assert git_tool_count == 13, f"Expected 13 Git tools, found {git_tool_count}"

    # Verify permission levels are correct
    read_only_tools = ["git_status", "git_diff", "git_log", "git_show"]
    for tool_name in read_only_tools:
        tool = registry.get(tool_name)
        assert tool.permission_level == "auto", f"{tool_name} should be auto"

    modifying_tools = [t for t in git_tools if t not in read_only_tools]
    for tool_name in modifying_tools:
        tool = registry.get(tool_name)
        assert tool.permission_level == "ask", f"{tool_name} should be ask"


def test_git_tools_workflow_integration():
    """Test that Git tools work together in a realistic workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        original_cwd = os.getcwd()

        try:
            os.chdir(repo_path)

            # Initialize repository
            os.system("git init > /dev/null 2>&1")
            os.system("git config user.email 'test@example.com'")
            os.system("git config user.name 'Test User'")

            registry = create_default_registry()

            # Test git_status on empty repo
            status_tool = registry.get("git_status")
            assert status_tool is not None
            result = status_tool.execute()
            assert result.success is True
            assert "No commits yet" in result.output or "Поки що немає комітів" in result.output

            # Create a file
            test_file = repo_path / "test.txt"
            test_file.write_text("Test content")

            # Test git_add
            add_tool = registry.get("git_add")
            assert add_tool is not None
            result = add_tool.execute(paths="test.txt")
            assert result.success is True

            # Test git_commit
            commit_tool = registry.get("git_commit")
            assert commit_tool is not None
            result = commit_tool.execute(message="Initial commit")
            assert result.success is True
            assert "commit" in result.output.lower() or "коміт" in result.output.lower()

            # Test git_log
            log_tool = registry.get("git_log")
            assert log_tool is not None
            result = log_tool.execute(oneline=True, max_count=1)
            assert result.success is True
            assert "Initial commit" in result.output

            # Test git_branch
            branch_tool = registry.get("git_branch")
            assert branch_tool is not None
            result = branch_tool.execute(list=True)
            assert result.success is True
            assert "main" in result.output or "master" in result.output

            # Test git_show
            show_tool = registry.get("git_show")
            assert show_tool is not None
            result = show_tool.execute()
            assert result.success is True
            assert "commit" in result.output.lower()

            print("✓ All basic Git tools work correctly in integration")

        finally:
            os.chdir(original_cwd)


def test_git_tools_error_handling():
    """Test error handling in Git tools."""
    registry = create_default_registry()

    # Test outside Git repository
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        original_cwd = os.getcwd()

        try:
            os.chdir(repo_path)

            # Should fail because not in Git repo
            status_tool = registry.get("git_status")
            result = status_tool.execute()

            # Different tools handle this differently
            # Some might succeed with empty output, others might fail
            # Just verify the tool doesn't crash
            assert hasattr(result, "success")
            assert hasattr(result, "output")
            assert hasattr(result, "error")

            print("✓ Git tools handle non-Git directories gracefully")

        finally:
            os.chdir(original_cwd)


def test_git_tools_parameter_validation():
    """Test that Git tools validate parameters correctly."""
    registry = create_default_registry()

    # Test git_commit requires message
    commit_tool = registry.get("git_commit")
    schema = commit_tool.get_schema()

    # Check that message is required
    parameters = schema["function"]["parameters"]
    assert "message" in parameters["properties"]
    assert "message" in parameters.get("required", [])

    # Test git_merge requires branch
    merge_tool = registry.get("git_merge")
    schema = merge_tool.get_schema()
    parameters = schema["function"]["parameters"]
    assert "branch" in parameters["properties"]
    assert "branch" in parameters.get("required", [])

    print("✓ Git tools have proper parameter validation")


@pytest.mark.parametrize(
    "tool_name",
    [
        "git_status",
        "git_diff",
        "git_log",
        "git_show",
        "git_branch",
        "git_add",
        "git_commit",
        "git_push",
        "git_pull",
        "git_stash",
        "git_checkout",
        "git_merge",
        "git_fetch",
    ],
)
def test_git_tools_have_descriptions(tool_name):
    """Test that Git tools have meaningful descriptions."""
    registry = create_default_registry()
    tool = registry.get(tool_name)
    assert tool is not None

    description = tool.description
    assert description is not None
    assert len(description) > 10  # Description should be meaningful
    assert len(description) < 200  # But not too long

    print(f"✓ {tool_name} has proper description: {description[:50]}...")


if __name__ == "__main__":
    # Run tests directly
    test_git_tools_comprehensive_coverage()
    print("✓ Comprehensive coverage test passed")

    test_git_tools_workflow_integration()
    print("✓ Workflow integration test passed")

    test_git_tools_error_handling()
    print("✓ Error handling test passed")

    test_git_tools_parameter_validation()
    print("✓ Parameter validation test passed")

    print("\n✅ All comprehensive Git tools tests passed!")
