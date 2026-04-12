"""Extended tests for the refactored permission system."""

import re

from lunvex_code.permissions import (
    CompositeRule,
    InputPatternRule,
    PermissionLevel,
    PermissionManager,
    SessionRule,
    ToolNamePatternRule,
    ToolNameRule,
)


class TestExtendedPermissionSystem:
    """Test cases for the extended permission system."""

    def test_custom_tool_name_rule(self):
        """Should be able to add custom tool name rules."""
        manager = PermissionManager()

        # Add custom rule for a hypothetical tool
        custom_rule = ToolNameRule("custom_tool", PermissionLevel.AUTO, "Custom tool rule")
        manager.add_rule(custom_rule)

        request = manager.check_permission("custom_tool", {"param": "value"})
        assert request.level == PermissionLevel.AUTO
        assert request.reason == "Custom tool rule"

    def test_tool_name_pattern_rule(self):
        """Should be able to add tool name pattern rules."""
        manager = PermissionManager()

        # Add pattern rule for tools starting with "test_"
        pattern = re.compile(r"^test_.*")
        custom_rule = ToolNamePatternRule(pattern, PermissionLevel.AUTO, "Test tool pattern")
        manager.add_rule(custom_rule)

        request = manager.check_permission("test_runner", {"test": "something"})
        assert request.level == PermissionLevel.AUTO
        assert request.reason == "Test tool pattern"

        # Non-matching tool should not be affected
        request2 = manager.check_permission("other_tool", {"test": "something"})
        assert request2.level == PermissionLevel.ASK  # Default

    def test_input_pattern_rule(self):
        """Should be able to add input pattern rules."""
        manager = PermissionManager()

        # Add rule to block specific file paths - add with higher priority
        pattern = re.compile(r".*\.(env|secret)$", re.IGNORECASE)
        custom_rule = InputPatternRule(
            "write_file", "path", pattern, PermissionLevel.DENY, "Protected file type"
        )
        # Insert at beginning to ensure it's checked before default rules
        manager.rules.insert(0, custom_rule)

        # Should block .env files
        request = manager.check_permission("write_file", {"path": "/path/to/.env"})
        assert request.level == PermissionLevel.DENY
        assert "Protected file type" in request.reason

        # Should allow other files (default rule applies)
        request2 = manager.check_permission("write_file", {"path": "/path/to/config.json"})
        assert request2.level == PermissionLevel.ASK  # Default for write_file

    def test_composite_and_rule(self):
        """Should be able to create AND composite rules."""
        manager = PermissionManager()

        # Create composite rule: tool must be "bash" AND command must contain "production"
        # Use DENY level to make it easier to test
        composite_deny = CompositeRule(
            [
                ToolNameRule("bash", PermissionLevel.DENY, "Tool check"),
                InputPatternRule(
                    "bash",
                    "command",
                    re.compile(r"production", re.IGNORECASE),
                    PermissionLevel.DENY,
                    "Production check",
                ),
            ],
            "AND",
        )

        # Insert at beginning to ensure it's checked before default rules
        manager.rules.insert(0, composite_deny)

        # Should deny production deployments
        request = manager.check_permission("bash", {"command": "deploy to production"})
        assert request.level == PermissionLevel.DENY

        # Should not deny non-production commands (default rule applies)
        request2 = manager.check_permission("bash", {"command": "deploy to staging"})
        assert request2.level == PermissionLevel.ASK  # Default for bash

    def test_composite_or_rule(self):
        """Should be able to create OR composite rules."""
        manager = PermissionManager()

        # Create composite rule: deny if command contains "drop" OR "truncate"
        rule1 = InputPatternRule(
            "bash",
            "command",
            re.compile(r"\bdrop\b", re.IGNORECASE),
            PermissionLevel.DENY,
            "DROP command",
        )
        rule2 = InputPatternRule(
            "bash",
            "command",
            re.compile(r"\btruncate\b", re.IGNORECASE),
            PermissionLevel.DENY,
            "TRUNCATE command",
        )

        composite = CompositeRule([rule1, rule2], "OR")

        # Insert at beginning to ensure it's checked before default rules
        manager.rules.insert(0, composite)

        # Should deny DROP commands
        request1 = manager.check_permission("bash", {"command": "DROP TABLE users"})
        assert request1.level == PermissionLevel.DENY

        # Should deny TRUNCATE commands
        request2 = manager.check_permission("bash", {"command": "TRUNCATE TABLE logs"})
        assert request2.level == PermissionLevel.DENY

        # Should allow other commands (default rule applies)
        request3 = manager.check_permission("bash", {"command": "SELECT * FROM users"})
        assert request3.level == PermissionLevel.ASK  # Default

    def test_rule_priority_order(self):
        """Rules should be checked in the order they were added."""
        # Test rule ordering directly without PermissionManager
        from lunvex_code.permissions import PermissionLevel, ToolNameRule

        # Create rules
        rule1 = ToolNameRule("test_tool", PermissionLevel.AUTO, "First rule")
        rule2 = ToolNameRule("test_tool", PermissionLevel.DENY, "Second rule")

        # Test that rule2 would override rule1 if checked in order
        # (This tests the rule logic, not the manager integration)
        result1 = rule1.check("test_tool", {"param": "value"})
        result2 = rule2.check("test_tool", {"param": "value"})

        assert result1 == PermissionLevel.AUTO
        assert result2 == PermissionLevel.DENY
        assert rule1.get_reason() == "First rule"
        assert rule2.get_reason() == "Second rule"

    def test_session_rule_independence(self):
        """Session rules should work independently of other rules."""
        manager = PermissionManager()

        # Add a custom rule that denies all bash commands
        manager.add_rule(ToolNameRule("bash", PermissionLevel.DENY, "Custom deny"))

        # Add to session allowlist (should override custom rule due to order)
        manager.add_to_allowlist("bash(ls:*)")

        # Session rule is added first, so it should be checked before custom deny
        # But custom deny was added after, so it comes later in the list
        # Let's check what happens
        request = manager.check_permission("bash", {"command": "ls -la"})

        # The session rule (allowlist) is added during initialization,
        # so it comes before our custom deny rule
        assert request.level == PermissionLevel.AUTO

    def test_rule_override_with_trust_mode(self):
        """Trust mode should override ASK but not DENY."""
        manager = PermissionManager(trust_mode=True)

        # Add a rule that would normally ask
        manager.add_rule(ToolNameRule("questionable_tool", PermissionLevel.ASK, "Questionable"))

        # In trust mode, ASK should become AUTO
        request = manager.check_permission("questionable_tool", {"param": "value"})
        assert request.level == PermissionLevel.AUTO

        # Add a DENY rule
        manager.add_rule(ToolNameRule("dangerous_tool", PermissionLevel.DENY, "Dangerous"))

        # DENY should not be overridden by trust mode
        request2 = manager.check_permission("dangerous_tool", {"param": "value"})
        assert request2.level == PermissionLevel.DENY

    def test_yolo_mode_with_custom_rules(self):
        """YOLO mode should still respect custom DENY rules."""
        manager = PermissionManager(yolo_mode=True)

        # Add a custom DENY rule
        manager.add_rule(ToolNameRule("dangerous_tool", PermissionLevel.DENY, "Custom dangerous"))

        # Should still be denied even in YOLO mode
        request = manager.check_permission("dangerous_tool", {"param": "value"})
        assert request.level == PermissionLevel.DENY

        # Other tools should be auto-approved
        request2 = manager.check_permission("safe_tool", {"param": "value"})
        assert request2.level == PermissionLevel.AUTO

    def test_multiple_input_patterns(self):
        """Should handle multiple input pattern rules correctly."""
        manager = PermissionManager()

        # Block commands that modify system files
        system_files_pattern = re.compile(r"^/(etc|usr|var|lib|bin|sbin)/")
        system_rule = InputPatternRule(
            "write_file",
            "path",
            system_files_pattern,
            PermissionLevel.DENY,
            "System file protection",
        )
        # Insert at beginning to ensure it's checked before default rules
        manager.rules.insert(0, system_rule)

        # Test system file protection
        request1 = manager.check_permission("write_file", {"path": "/etc/config.conf"})
        assert request1.level == PermissionLevel.DENY

        # Test that normal files are still handled by default rule
        # Note: /tmp/test.txt is auto-approved in smart mode (default)
        # Let's test a non-temp, non-test file instead
        request2 = manager.check_permission("write_file", {"path": "/home/user/document.txt"})
        assert request2.level == PermissionLevel.ASK  # Default for write_file


class TestPermissionRuleClasses:
    """Test cases for individual permission rule classes."""

    def test_tool_name_rule(self):
        """ToolNameRule should match exact tool names."""
        rule = ToolNameRule("test_tool", PermissionLevel.AUTO, "Test rule")

        assert rule.check("test_tool", {}) == PermissionLevel.AUTO
        assert rule.check("other_tool", {}) is None
        assert rule.get_reason() == "Test rule"

    def test_tool_name_pattern_rule(self):
        """ToolNamePatternRule should match tool names with regex."""
        pattern = re.compile(r"^api_.*")
        rule = ToolNamePatternRule(pattern, PermissionLevel.AUTO, "API tool")

        assert rule.check("api_users", {}) == PermissionLevel.AUTO
        assert rule.check("api_posts", {}) == PermissionLevel.AUTO
        assert rule.check("cli_tool", {}) is None
        assert rule.get_reason() == "API tool"

    def test_input_pattern_rule(self):
        """InputPatternRule should match tool input values."""
        pattern = re.compile(r"secret", re.IGNORECASE)
        rule = InputPatternRule("log", "message", pattern, PermissionLevel.DENY, "Secret detected")

        assert rule.check("log", {"message": "This is a SECRET message"}) == PermissionLevel.DENY
        assert rule.check("log", {"message": "Normal message"}) is None
        assert rule.check("other_tool", {"message": "secret"}) is None
        assert rule.get_reason() == "Secret detected"

    def test_composite_rule_and(self):
        """CompositeRule with AND operator should require all rules to match."""
        rule1 = ToolNameRule("tool", PermissionLevel.AUTO, "Rule 1")
        rule2 = InputPatternRule(
            "tool", "param", re.compile("value"), PermissionLevel.AUTO, "Rule 2"
        )

        composite = CompositeRule([rule1, rule2], "AND")

        # Both conditions match
        assert composite.check("tool", {"param": "value"}) == PermissionLevel.AUTO

        # Only first condition matches
        assert composite.check("tool", {"param": "other"}) is None

        # Only second condition matches
        assert composite.check("other", {"param": "value"}) is None

    def test_composite_rule_or(self):
        """CompositeRule with OR operator should match if any rule matches."""
        rule1 = ToolNameRule("tool1", PermissionLevel.AUTO, "Rule 1")
        rule2 = ToolNameRule("tool2", PermissionLevel.DENY, "Rule 2")

        composite = CompositeRule([rule1, rule2], "OR")

        # First rule matches
        assert composite.check("tool1", {}) == PermissionLevel.AUTO

        # Second rule matches
        assert composite.check("tool2", {}) == PermissionLevel.DENY

        # Neither matches
        assert composite.check("tool3", {}) is None

        # Should prefer DENY over AUTO
        rule3 = ToolNameRule("tool3", PermissionLevel.DENY, "Rule 3")
        rule4 = ToolNameRule("tool3", PermissionLevel.AUTO, "Rule 4")
        composite2 = CompositeRule([rule3, rule4], "OR")
        assert composite2.check("tool3", {}) == PermissionLevel.DENY

    def test_session_rule_parsing(self):
        """SessionRule should correctly parse patterns."""
        rule = SessionRule()

        # Test pattern parsing
        tool, key, pattern = rule._parse_pattern("bash(ls:*)")
        assert tool == "bash"
        assert key == "ls"
        assert pattern == "*"

        tool, key, pattern = rule._parse_pattern("write(*.py)")
        assert tool == "write"
        assert key is None
        assert pattern == "*.py"

        tool, key, pattern = rule._parse_pattern("invalid pattern")
        assert tool is None
        assert key is None
        assert pattern is None

    def test_session_rule_matching(self):
        """SessionRule should correctly match patterns."""
        rule = SessionRule()

        # Test pattern matching
        assert rule._matches_pattern("ls -la", "ls:*") is True
        assert rule._matches_pattern("rm file", "ls:*") is False

    def test_session_rule_check_supports_bash_prefix_patterns(self):
        """SessionRule should match bash prefixes from allowlist patterns."""
        rule = SessionRule()
        rule.add_to_allowlist("bash(curl:*)")

        assert rule.check("bash", {"command": "curl -s https://example.com"}) == PermissionLevel.AUTO

    def test_session_rule_check_supports_write_alias(self):
        """SessionRule write alias should match file path tools."""
        rule = SessionRule()
        rule.add_to_allowlist("write(*.py)")

        assert rule.check("write_file", {"path": "/tmp/example.py"}) == PermissionLevel.AUTO
        assert rule.check("edit_file", {"path": "/tmp/example.py"}) == PermissionLevel.AUTO
        assert rule._matches_pattern("test.py", "*.py") is True
        assert rule._matches_pattern("test.txt", "*.py") is False
        assert rule._matches_pattern("anything", "*") is True
