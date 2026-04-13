"""Simple tests for async Git tools."""


def test_git_tool_imports():
    """Test that Git tools can be imported."""
    from lunvex_code.tools.git_tools import (
        GitAddTool,
        GitBranchTool,
        GitCheckoutTool,
        GitCommitTool,
        GitDiffTool,
        GitFetchTool,
        GitLogTool,
        GitMergeTool,
        GitPullTool,
        GitPushTool,
        GitShowTool,
        GitStashTool,
        GitStatusTool,
    )

    # Create instances
    tools = [
        GitStatusTool(),
        GitDiffTool(),
        GitLogTool(),
        GitShowTool(),
        GitAddTool(),
        GitCommitTool(),
        GitBranchTool(),
        GitCheckoutTool(),
        GitMergeTool(),
        GitPushTool(),
        GitPullTool(),
        GitFetchTool(),
        GitStashTool(),
    ]

    # Check basic properties
    for tool in tools:
        assert tool.name is not None
        assert tool.description is not None
        assert hasattr(tool, "execute")

    print(f"✅ Successfully imported {len(tools)} Git tools")


def test_git_tool_schemas():
    """Test Git tool schema generation."""
    from lunvex_code.tools.git_tools import GitDiffTool, GitLogTool, GitStatusTool

    tools = [
        GitStatusTool(),
        GitDiffTool(),
        GitLogTool(),
    ]

    for tool in tools:
        schema = tool.get_schema()

        assert schema["function"]["name"] == tool.name
        assert schema["function"]["description"] == tool.description
        assert "parameters" in schema["function"]

    print("✅ Git tool schemas generated correctly")


def test_git_tool_compatibility():
    """Test compatibility between Git tools and async system."""
    from lunvex_code.tools.git_tools import GitStatusTool

    # Git tools are sync, not async
    git_tool = GitStatusTool()

    # But they have similar interface
    assert hasattr(git_tool, "name")
    assert hasattr(git_tool, "description")
    assert hasattr(git_tool, "execute")
    assert hasattr(git_tool, "get_schema")

    print("✅ Git tools have compatible interface")


if __name__ == "__main__":
    # Run tests
    tests = [
        test_git_tool_imports,
        test_git_tool_schemas,
        test_git_tool_compatibility,
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
