# Extensible Permission System

## Overview

The LunVex Code permission system has been refactored to provide a highly extensible, rule-based architecture. This allows developers to easily add custom permission rules, integrate with external systems, and create complex permission logic.

## Architecture

### Core Components

1. **PermissionManager** - Main entry point for permission checking
2. **PermissionRule** - Abstract base class for all permission rules
3. **Rule Implementations** - Concrete rule classes for different matching strategies
4. **SessionRule** - Special rule for session-specific allow/deny lists

### Rule Types

#### 1. ToolNameRule
Matches tools by exact name.

```python
from deepseek_code.permissions import ToolNameRule, PermissionLevel

rule = ToolNameRule(
    "deploy_tool",
    PermissionLevel.DENY,
    "Deployment requires special approval"
)
```

#### 2. ToolNamePatternRule
Matches tools by regex pattern.

```python
import re
from deepseek_code.permissions import ToolNamePatternRule, PermissionLevel

pattern = re.compile(r"^api_.*")
rule = ToolNamePatternRule(
    pattern,
    PermissionLevel.AUTO,
    "API tools are auto-approved"
)
```

#### 3. InputPatternRule
Matches tool input values by regex pattern.

```python
import re
from deepseek_code.permissions import InputPatternRule, PermissionLevel

pattern = re.compile(r".*\.env$", re.IGNORECASE)
rule = InputPatternRule(
    "write_file",
    "path",
    pattern,
    PermissionLevel.DENY,
    "Protected .env files"
)
```

#### 4. CompositeRule
Combines multiple rules with logical operators (AND/OR).

```python
from deepseek_code.permissions import CompositeRule, InputPatternRule, PermissionLevel
import re

rule = CompositeRule([
    InputPatternRule(
        "bash",
        "command",
        re.compile(r"production", re.IGNORECASE),
        PermissionLevel.DENY,
        "Production environment"
    ),
    InputPatternRule(
        "bash",
        "command",
        re.compile(r"\bdrop\b", re.IGNORECASE),
        PermissionLevel.DENY,
        "DROP operation"
    )
], "AND")  # Deny if BOTH conditions match
```

#### 5. SessionRule
Manages session-specific allow/deny lists with pattern matching.

```python
manager = PermissionManager()
manager.add_to_allowlist("bash(npm:*)")  # Auto-approve npm commands
manager.add_to_denylist("bash(rm:*)")    # Block rm commands
```

## Usage Examples

### Basic Usage

```python
from deepseek_code.permissions import PermissionManager

# Create permission manager
manager = PermissionManager()

# Check permission for a tool
request = manager.check_permission(
    "write_file",
    {"path": "/tmp/test.txt", "content": "Hello"}
)

if request.level == PermissionLevel.AUTO:
    print("Auto-approved")
elif request.level == PermissionLevel.ASK:
    print(f"Need permission: {manager.format_permission_prompt(request)}")
elif request.level == PermissionLevel.DENY:
    print(f"Denied: {request.reason}")
```

### Adding Custom Rules

```python
from deepseek_code.permissions import PermissionManager, ToolNameRule, PermissionLevel

manager = PermissionManager()

# Add custom rule
custom_rule = ToolNameRule(
    "custom_deploy",
    PermissionLevel.DENY,
    "Custom deployment tool blocked"
)
manager.add_rule(custom_rule)

# The rule will be checked along with all other rules
```

### Creating Complex Rule Logic

```python
import re
from deepseek_code.permissions import (
    PermissionManager,
    CompositeRule,
    InputPatternRule,
    ToolNameRule,
    PermissionLevel
)

manager = PermissionManager()

# Create a rule that blocks dangerous operations during business hours
# (This is a simplified example - in practice you'd check actual time)
business_hours_rule = CompositeRule([
    ToolNameRule("bash", PermissionLevel.ASK, "Tool check"),
    InputPatternRule(
        "bash",
        "command",
        re.compile(r"\b(rm\s+-rf|shutdown|reboot)\b"),
        PermissionLevel.DENY,
        "Dangerous operation during business hours"
    )
], "AND")

manager.add_rule(business_hours_rule)
```

### Integration with External Systems

```python
from abc import ABC, abstractmethod
from deepseek_code.permissions import PermissionRule, PermissionLevel

class ExternalSystemRule(PermissionRule, ABC):
    """Base class for rules that integrate with external systems."""
    
    def __init__(self, external_client):
        self.client = external_client
    
    @abstractmethod
    def check_external(self, tool_name, tool_input):
        """Check with external system."""
        pass
    
    def check(self, tool_name, tool_input):
        result = self.check_external(tool_name, tool_input)
        if result == "allow":
            return PermissionLevel.AUTO
        elif result == "deny":
            return PermissionLevel.DENY
        elif result == "ask":
            return PermissionLevel.ASK
        return None
    
    def get_reason(self):
        return "External system rule"

# Example implementation
class LDAPRule(ExternalSystemRule):
    """Rule that checks permissions against LDAP."""
    
    def check_external(self, tool_name, tool_input):
        # Check with LDAP server
        user_groups = self.client.get_user_groups()
        
        if "admin" in user_groups:
            return "allow"
        elif "restricted" in user_groups and tool_name == "bash":
            return "deny"
        else:
            return "ask"
```

## Rule Evaluation Order

Rules are evaluated in the order they were added to the PermissionManager. The first rule that returns a non-None result determines the permission level.

### Default Rule Order

1. **SessionRule** - Session allow/deny lists
2. **Read-only tool rules** - Auto-approve read_file, glob, grep
3. **File modification rules** - Ask for write_file, edit_file
4. **Dangerous pattern rules** - Deny dangerous bash patterns
5. **Blocked command rules** - Deny completely blocked commands
6. **Default bash rule** - Ask for bash commands
7. **Custom rules** - Any rules added via `add_rule()`

### Override Behavior

- Later rules can override earlier rules
- DENY cannot be overridden by trust mode
- YOLO mode still respects DENY rules (safety first)

## Configuration

### Environment Variables

```bash
# No specific environment variables for permission system
# Configuration is done programmatically
```

### Programmatic Configuration

```python
from deepseek_code.permissions import PermissionManager

# Create with different modes
manager1 = PermissionManager()                    # Default mode
manager2 = PermissionManager(trust_mode=True)     # Auto-approve non-blocked
manager3 = PermissionManager(yolo_mode=True)      # Skip all prompts (except DENY)

# Add rules
manager1.add_rule(custom_rule)
manager1.add_to_allowlist("bash(git:*)")
manager1.add_to_denylist("bash(rm:*)")
```

## Best Practices

### 1. Rule Specificity
Create specific rules before general ones. Specific rules should be added first.

### 2. Safety First
Always add safety rules (DENY) before permissive rules (AUTO).

### 3. Testing
Test rules thoroughly, especially composite rules with complex logic.

### 4. Documentation
Document custom rules with clear reasons and examples.

### 5. Performance
For rules that make external calls (API, database), consider caching or async operations.

## Migration from Old System

The new system is fully backward compatible. Existing code using `PermissionManager` will continue to work without changes.

### Changes in Behavior

1. **Rule evaluation** is now more explicit and predictable
2. **Custom rules** can be added without modifying core code
3. **Composite logic** allows for more complex permission scenarios

### Code Comparison

**Before (old system):**
```python
# Logic was hardcoded in PermissionManager.check_permission()
# No easy way to add custom rules
```

**After (new system):**
```python
from deepseek_code.permissions import PermissionManager, InputPatternRule
import re

manager = PermissionManager()

# Add custom rule easily
rule = InputPatternRule(
    "bash",
    "command",
    re.compile(r"dangerous_operation"),
    PermissionLevel.DENY,
    "Custom dangerous operation"
)
manager.add_rule(rule)
```

## Extending the System

### Creating Custom Rule Classes

```python
from deepseek_code.permissions import PermissionRule, PermissionLevel
from typing import Optional, Dict, Any

class TimeOfDayRule(PermissionRule):
    """Rule that restricts operations based on time of day."""
    
    def __init__(self, allowed_hours: range):
        self.allowed_hours = allowed_hours
    
    def check(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[PermissionLevel]:
        from datetime import datetime
        
        current_hour = datetime.now().hour
        
        if current_hour not in self.allowed_hours:
            # Outside allowed hours, restrict dangerous operations
            if tool_name == "bash":
                command = tool_input.get("command", "")
                if "deploy" in command.lower() or "migrate" in command.lower():
                    return PermissionLevel.DENY
        
        return None
    
    def get_reason(self) -> Optional[str]:
        return "Time-based restriction"
```

### Plugin System Integration

```python
# Example of how a plugin system could integrate with permissions
class PluginPermissionSystem:
    def __init__(self):
        self.manager = PermissionManager()
        self.load_plugin_rules()
    
    def load_plugin_rules(self):
        # Load rules from plugins
        for plugin in self.get_plugins():
            rules = plugin.get_permission_rules()
            for rule in rules:
                self.manager.add_rule(rule)
    
    def check_permission(self, tool_name, tool_input):
        return self.manager.check_permission(tool_name, tool_input)
```

## Troubleshooting

### Common Issues

1. **Rule not firing**: Check rule order - earlier rules may be matching first
2. **Unexpected AUTO approval**: Check trust_mode and YOLO mode settings
3. **DENY being overridden**: DENY cannot be overridden - check for rule conflicts
4. **Pattern not matching**: Test regex patterns independently

### Debugging

```python
# Enable verbose debugging
manager = PermissionManager()

# Check what rules are registered
print(f"Total rules: {len(manager.rules)}")
for i, rule in enumerate(manager.rules):
    print(f"Rule {i}: {rule.__class__.__name__} - {rule.get_reason()}")

# Test specific tool/input
request = manager.check_permission("bash", {"command": "test"})
print(f"Result: {request.level} - {request.reason}")
```

## Security Considerations

1. **Default deny**: Unknown tools default to ASK (or AUTO in trust mode)
2. **No override for DENY**: Trust and YOLO modes cannot override DENY
3. **Input validation**: All user input should be validated before rule evaluation
4. **Rule injection**: Ensure rules come from trusted sources
5. **Performance**: Complex rules should not create denial of service

## Future Enhancements

Planned improvements for the permission system:

1. **Rule persistence** - Save/load rules from configuration files
2. **Rule priorities** - Explicit priority levels for rules
3. **Audit logging** - Log all permission decisions
4. **Machine learning** - Adaptive rules based on usage patterns
5. **Multi-user support** - User-specific permission rules
6. **Temporal rules** - Rules that change based on time/date
7. **Geographic rules** - Location-based restrictions