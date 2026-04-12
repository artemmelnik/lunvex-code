#!/usr/bin/env python3
"""
Example demonstrating the extensible permission system.

This example shows how to create custom permission rules and integrate them
with the LunVex Code permission system.
"""

import re

from lunvex_code.permissions import (
    CompositeRule,
    InputPatternRule,
    PermissionLevel,
    PermissionManager,
    ToolNamePatternRule,
    ToolNameRule,
)


def example_basic_rules():
    """Example of basic permission rules."""
    print("=== Basic Permission Rules Example ===")

    # Create a permission manager
    manager = PermissionManager()

    # Add a custom rule for a specific tool
    custom_tool_rule = ToolNameRule(
        "deploy_tool", PermissionLevel.DENY, "Deployment tool requires special approval"
    )
    manager.add_rule(custom_tool_rule)

    # Check permission for the custom tool
    request = manager.check_permission("deploy_tool", {"environment": "production"})
    print(f"Deploy tool permission: {request.level.value} - {request.reason}")

    # Add a pattern-based rule
    api_pattern = re.compile(r"^api_.*")
    api_rule = ToolNamePatternRule(api_pattern, PermissionLevel.AUTO, "API tools are auto-approved")
    manager.add_rule(api_rule)

    # Check permission for API tools
    request = manager.check_permission("api_users", {"action": "get"})
    print(f"API tool permission: {request.level.value} - {request.reason}")

    print()


def example_input_pattern_rules():
    """Example of input pattern rules."""
    print("=== Input Pattern Rules Example ===")

    manager = PermissionManager()

    # Block writing to sensitive files
    sensitive_files = re.compile(r".*\.(env|secret|key|pem)$", re.IGNORECASE)
    file_rule = InputPatternRule(
        "write_file", "path", sensitive_files, PermissionLevel.DENY, "Sensitive file protection"
    )
    manager.add_rule(file_rule)

    # Test the rule
    request1 = manager.check_permission("write_file", {"path": "/app/.env"})
    print(f"Write to .env: {request1.level.value} - {request1.reason}")

    request2 = manager.check_permission("write_file", {"path": "/app/config.json"})
    print(f"Write to config.json: {request2.level.value} - {request2.reason}")

    print()


def example_composite_rules():
    """Example of composite rules."""
    print("=== Composite Rules Example ===")

    manager = PermissionManager()

    # Create a composite rule: deny production database operations
    production_db_rule = CompositeRule(
        [
            InputPatternRule(
                "bash",
                "command",
                re.compile(r"\b(drop|alter|truncate)\b", re.IGNORECASE),
                PermissionLevel.DENY,
                "Dangerous database operation",
            ),
            InputPatternRule(
                "bash",
                "command",
                re.compile(r"production", re.IGNORECASE),
                PermissionLevel.DENY,
                "Production environment",
            ),
        ],
        "AND",
    )

    manager.add_rule(production_db_rule)

    # Test the composite rule
    test_cases = [
        ("DROP TABLE users", "Should be allowed (not production)"),
        ("DROP TABLE production.users", "Should be denied (production + DROP)"),
        ("SELECT * FROM production.users", "Should be allowed (safe operation)"),
        ("ALTER TABLE staging.users", "Should be allowed (not production)"),
    ]

    for command, description in test_cases:
        request = manager.check_permission("bash", {"command": command})
        print(f"{description}: {request.level.value}")

    print()


def example_session_rules():
    """Example of session-specific rules."""
    print("=== Session Rules Example ===")

    manager = PermissionManager()

    # Add to session allowlist
    manager.add_to_allowlist("bash(npm:*")
    manager.add_to_allowlist("write(*.test.py)")

    # Add to session denylist
    manager.add_to_denylist("bash(rm:*)")

    # Test session rules
    test_cases = [
        ("bash", {"command": "npm install"}, "npm command"),
        ("bash", {"command": "rm file.txt"}, "rm command"),
        ("write_file", {"path": "test.test.py"}, "Test file"),
        ("write_file", {"path": "production.py"}, "Production file"),
    ]

    for tool, input_data, description in test_cases:
        request = manager.check_permission(tool, input_data)
        print(f"{description}: {request.level.value}")

    print()


def example_custom_rule_integration():
    """Example of integrating custom rules into an application."""
    print("=== Custom Rule Integration Example ===")

    # Define a custom rule class
    class TimeBasedRule:
        """Custom rule that restricts operations during business hours."""

        def __init__(self, business_hours_start=9, business_hours_end=17):
            self.start = business_hours_start
            self.end = business_hours_end

        def check(self, tool_name, tool_input):
            # In a real implementation, you would check current time
            # For this example, we'll simulate outside business hours
            current_hour = 18  # 6 PM

            if self.start <= current_hour <= self.end:
                # During business hours, restrict dangerous operations
                if tool_name == "bash":
                    command = tool_input.get("command", "")
                    dangerous_patterns = [
                        r"rm\s+-rf",
                        r"shutdown",
                        r"reboot",
                    ]

                    for pattern in dangerous_patterns:
                        if re.search(pattern, command, re.IGNORECASE):
                            return PermissionLevel.DENY

            return None

        def get_reason(self):
            return "Business hours restriction"

    # Create manager and add custom rule
    PermissionManager()

    # Note: For this to work with the actual PermissionManager,
    # TimeBasedRule would need to inherit from PermissionRule
    # This is just a conceptual example

    print("Custom rule integration demonstrated")
    print("(In practice, custom rules should inherit from PermissionRule)")
    print()


def main():
    """Run all examples."""
    print("LunVex Code - Extensible Permission System Examples")
    print("=" * 60)
    print()

    example_basic_rules()
    example_input_pattern_rules()
    example_composite_rules()
    example_session_rules()
    example_custom_rule_integration()

    print("=" * 60)
    print("All examples completed successfully!")


if __name__ == "__main__":
    main()
