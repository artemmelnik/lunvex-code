"""Tests for Git tool permissions."""

from lunvex_code.permissions import PermissionManager, PermissionLevel


def test_git_tools_permission_rules():
    """Test that Git tools have correct permission rules."""
    manager = PermissionManager()
    
    # Test read-only Git tools - should be AUTO
    read_only_tools = ["git_status", "git_diff", "git_log", "git_show"]
    for tool_name in read_only_tools:
        request = manager.check_permission(tool_name, {})
        assert request.level == PermissionLevel.AUTO, f"{tool_name} should be AUTO"
        assert "read-only" in request.reason.lower()
    
    # Test tools that modify state - should be ASK
    modifying_tools = [
        "git_branch", "git_add", "git_commit", "git_push", "git_pull",
        "git_stash", "git_checkout", "git_merge", "git_fetch"
    ]
    for tool_name in modifying_tools:
        request = manager.check_permission(tool_name, {})
        assert request.level == PermissionLevel.ASK, f"{tool_name} should be ASK"
        assert "modif" in request.reason.lower() or "creates" in request.reason.lower() or "updates" in request.reason.lower()


def test_git_tools_with_trust_mode():
    """Test Git tools in trust mode."""
    manager = PermissionManager(trust_mode=True)
    
    # In trust mode, ASK operations are auto-approved (converted to AUTO)
    request = manager.check_permission("git_branch", {})
    assert request.level == PermissionLevel.AUTO, "git_branch should be AUTO in trust mode (auto-approved)"
    
    # Read-only tools should still be AUTO
    request = manager.check_permission("git_status", {})
    assert request.level == PermissionLevel.AUTO, "git_status should be AUTO"


def test_git_tools_with_yolo_mode():
    """Test Git tools in YOLO mode."""
    manager = PermissionManager(yolo_mode=True)
    
    # In YOLO mode, everything is auto-approved except DENY operations
    request = manager.check_permission("git_branch", {})
    assert request.level == PermissionLevel.AUTO, "git_branch should be AUTO in YOLO mode (auto-approved)"
    
    request = manager.check_permission("git_status", {})
    assert request.level == PermissionLevel.AUTO, "git_status should be AUTO"


def test_git_tools_permission_consistency():
    """Test consistency between tool permission_level and permission rules."""
    from lunvex_code.tools.base import create_default_registry
    
    registry = create_default_registry()
    manager = PermissionManager()
    
    git_tools = ["git_status", "git_diff", "git_log", "git_show", "git_branch"]
    
    for tool_name in git_tools:
        tool = registry.get(tool_name)
        request = manager.check_permission(tool_name, {})
        
        # Convert tool.permission_level to PermissionLevel
        tool_level = PermissionLevel(tool.permission_level)
        
        # They should match
        assert request.level == tool_level, \
            f"Permission mismatch for {tool_name}: tool says {tool_level}, rules say {request.level}"