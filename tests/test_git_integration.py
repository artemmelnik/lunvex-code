"""Integration tests for Git tools."""

from lunvex_code.tools.base import create_default_registry


def test_git_tools_registered():
    """Test that Git tools are registered in the default registry."""
    registry = create_default_registry()
    
    git_tools = [
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
    ]
    
    for tool_name in git_tools:
        tool = registry.get(tool_name)
        assert tool is not None, f"Git tool '{tool_name}' should be registered"
        assert tool.name == tool_name
    
    # Check that we have at least these Git tools
    all_tools = registry.list_tools()
    for tool_name in git_tools:
        assert tool_name in all_tools, f"Git tool '{tool_name}' should be in tool list"


def test_git_tools_schemas():
    """Test that Git tools have proper schemas."""
    registry = create_default_registry()
    
    git_tools = [
        "git_status", "git_diff", "git_log", "git_show", "git_branch",
        "git_add", "git_commit", "git_push", "git_pull",
        "git_stash", "git_checkout", "git_merge", "git_fetch"
    ]
    
    for tool_name in git_tools:
        tool = registry.get(tool_name)
        schema = tool.get_schema()
        
        assert schema["type"] == "function"
        assert schema["function"]["name"] == tool_name
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]


def test_git_tools_permission_levels():
    """Test that Git tools have appropriate permission levels."""
    registry = create_default_registry()
    
    # Read-only tools should have "auto" permission
    read_only_tools = ["git_status", "git_diff", "git_log", "git_show"]
    for tool_name in read_only_tools:
        tool = registry.get(tool_name)
        assert tool.permission_level == "auto", f"{tool_name} should have 'auto' permission"
    
    # Tools that modify state should have "ask" permission
    modifying_tools = [
        "git_branch", "git_add", "git_commit", "git_push", "git_pull",
        "git_stash", "git_checkout", "git_merge", "git_fetch"
    ]
    for tool_name in modifying_tools:
        tool = registry.get(tool_name)
        assert tool.permission_level == "ask", f"{tool_name} should have 'ask' permission"