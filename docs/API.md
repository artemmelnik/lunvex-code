# API Reference

> **Note**: This API documentation is a work in progress. More details will be added as the project evolves.

## Overview

This document describes the public API of LunVex Code for developers who want to extend or integrate with the system.

## Core Modules

### `deepseek_code.cli`
Command-line interface entry point.

#### `main()`
```python
def main() -> None:
    """Main entry point for the CLI."""
```

#### `app`
```python
app: typer.Typer
"""
Typer application instance.
Commands:
- run: Run LunVex Code with a task or in interactive mode
- init: Initialize a LUNVEX.md file
- history: Show recent conversation history
- version: Show version information
"""
```

### `deepseek_code.agent`
Core agent implementation.

#### `Agent`
```python
class Agent:
    """Main agent that orchestrates the LLM and tools."""
    
    def __init__(
        self,
        client: LunVexClient,
        context: ProjectContext,
        config: AgentConfig | None = None,
        registry: ToolRegistry | None = None,
    ):
        """
        Initialize agent.
        
        Args:
            client: LLM client instance
            context: Project context
            config: Agent configuration
            registry: Tool registry
        """
    
    def run(self, user_input: str) -> str:
        """
        Run a single turn of conversation.
        
        Args:
            user_input: User's message
            
        Returns:
            Agent's response
        """
    
    def run_interactive(self) -> None:
        """Run interactive REPL loop."""
```

#### `AgentConfig`
```python
@dataclass
class AgentConfig:
    """Configuration for the agent."""
    
    max_turns: int = 50
    trust_mode: bool = False
    yolo_mode: bool = False
    verbose: bool = False
```

### `deepseek_code.llm`
LLM client interface.

#### `LunVexClient`
```python
class LunVexClient:
    """Client for LunVex API."""
    
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize DeepSeek client.
        
        Args:
            api_key: API key (defaults to LUNVEX_API_KEY env var)
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
    
    def complete(self, messages: List[Dict[str, str]]) -> LLMResponse:
        """
        Get completion from LLM.
        
        Args:
            messages: Conversation history
            
        Returns:
            LLM response
        """
    
    def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
    ) -> LLMResponse:
        """
        Get completion with tool support.
        
        Args:
            messages: Conversation history
            tools: List of tool schemas
            
        Returns:
            LLM response with potential tool calls
        """
```

#### `LLMResponse`
```python
@dataclass
class LLMResponse:
    """Response from LLM."""
    
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
```

#### `ToolCall`
```python
@dataclass
class ToolCall:
    """Tool call from LLM."""
    
    id: str
    name: str
    arguments: Dict[str, Any]
```

### `deepseek_code.permissions`
Permission system.

#### `PermissionManager`
```python
class PermissionManager:
    """Manages permissions for tool execution."""
    
    def __init__(self, trust_mode: bool = False, yolo_mode: bool = False):
        """
        Initialize permission manager.
        
        Args:
            trust_mode: Auto-approve non-blocked operations
            yolo_mode: Skip most permission prompts
        """
    
    def check_permission(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
    ) -> PermissionRequest:
        """
        Check permission for tool execution.
        
        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters
            
        Returns:
            Permission request with decision
        """
    
    def add_rule(self, rule: PermissionRule) -> None:
        """Add a custom permission rule."""
    
    def add_to_allowlist(self, pattern: str) -> None:
        """Add pattern to session allowlist."""
    
    def add_to_denylist(self, pattern: str) -> None:
        """Add pattern to session denylist."""
    
    def format_permission_prompt(self, request: PermissionRequest) -> str:
        """Format permission prompt for user."""
```

#### `PermissionLevel`
```python
class PermissionLevel(Enum):
    """Permission levels for operations."""
    
    AUTO = "auto"  # Automatically allowed
    ASK = "ask"    # Requires user confirmation
    DENY = "deny"  # Blocked entirely
```

#### `PermissionRequest`
```python
@dataclass
class PermissionRequest:
    """A request for permission to perform an action."""
    
    tool_name: str
    tool_input: Dict[str, Any]
    level: PermissionLevel
    reason: Optional[str] = None
```

#### `PermissionRule` (Abstract Base Class)
```python
class PermissionRule(ABC):
    """Base class for permission rules."""
    
    @abstractmethod
    def check(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
    ) -> Optional[PermissionLevel]:
        """
        Check if this rule applies.
        
        Returns:
            PermissionLevel if rule applies, None otherwise
        """
    
    @abstractmethod
    def get_reason(self) -> Optional[str]:
        """Get reason for the decision."""
```

### `deepseek_code.tools`
Tool system.

#### `Tool` (Abstract Base Class)
```python
class Tool(ABC):
    """Base class for all tools."""
    
    name: str
    description: str
    parameters: Dict[str, Any]
    permission_level: str = "ask"
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the OpenAI-compatible tool schema."""
```

#### `ToolResult`
```python
@dataclass
class ToolResult:
    """Result from tool execution."""
    
    success: bool
    output: str
    error: Optional[str] = None
```

#### `ToolRegistry`
```python
class ToolRegistry:
    """Registry for managing tools."""
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name."""
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all registered tools."""
```

#### `create_default_registry()`
```python
def create_default_registry() -> ToolRegistry:
    """Create registry with default tools."""
```

### `deepseek_code.context`
Context management.

#### `ProjectContext`
```python
@dataclass
class ProjectContext:
    """Project context information."""
    
    root_path: str
    context_text: Optional[str] = None
    markers: List[str] = field(default_factory=list)
```

#### `get_project_context()`
```python
def get_project_context(start_path: str = ".") -> ProjectContext:
    """
    Get project context for a directory.
    
    Args:
        start_path: Starting directory
        
    Returns:
        Project context
    """
```

#### `build_system_prompt()`
```python
def build_system_prompt(context: ProjectContext) -> str:
    """
    Build system prompt from project context.
    
    Args:
        context: Project context
        
    Returns:
        System prompt
    """
```

### `deepseek_code.conversation`
Conversation management.

#### `ConversationHistory`
```python
class ConversationHistory:
    """Manages conversation history."""
    
    def __init__(self, system_prompt: str):
        """
        Initialize conversation history.
        
        Args:
            system_prompt: System prompt for the conversation
        """
    
    def add_message(self, role: str, content: str) -> None:
        """Add message to history."""
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages."""
    
    def save(self, session_id: str) -> None:
        """Save conversation to disk."""
    
    @classmethod
    def load(cls, session_id: str) -> "ConversationHistory":
        """Load conversation from disk."""
```

### `deepseek_code.ui`
User interface.

#### `print_message()`
```python
def print_message(role: str, content: str) -> None:
    """
    Print formatted message.
    
    Args:
        role: Message role (user, assistant, system)
        content: Message content
    """
```

#### `ask_permission()`
```python
def ask_permission(prompt: str) -> bool:
    """
    Ask user for permission.
    
    Args:
        prompt: Permission prompt
        
    Returns:
        True if approved, False otherwise
    """
```

#### `show_progress()`
```python
def show_progress(description: str) -> ContextManager:
    """
    Show progress indicator.
    
    Args:
        description: Progress description
        
    Returns:
        Context manager for progress display
    """
```

## Constants

### Application Constants
```python
APP_COMMAND_NAME: str = "lunvex-code"
APP_DISPLAY_NAME: str = "LunVex Code"
APP_CONTEXT_FILENAME: str = "LUNVEX.md"
LEGACY_CONTEXT_FILENAME: str = "DEEPSEEK.md"
APP_STATE_DIRNAME: str = ".lunvex-code"
```

### Version
```python
__version__: str = "0.1.0"
```

## Tool Reference

### Built-in Tools

#### `read_file`
Reads file contents.

**Parameters:**
- `path` (string, required): Path to file

**Permission:** AUTO

#### `write_file`
Writes content to file.

**Parameters:**
- `path` (string, required): Path to file
- `content` (string, required): Content to write

**Permission:** ASK (AUTO for safe files)

#### `edit_file`
Edits file by replacing text.

**Parameters:**
- `path` (string, required): Path to file
- `old_str` (string, required): Text to replace
- `new_str` (string, required): New text

**Permission:** ASK (AUTO for safe files)

#### `glob`
Finds files matching pattern.

**Parameters:**
- `pattern` (string, required): Glob pattern

**Permission:** AUTO

#### `grep`
Searches for text in files.

**Parameters:**
- `pattern` (string, required): Regex pattern
- `path` (string, required): Path to search
- `include` (string, optional): File pattern to include
- `ignore_case` (boolean, optional): Case-insensitive search
- `limit` (integer, optional): Maximum matches

**Permission:** AUTO

#### `bash`
Executes shell command.

**Parameters:**
- `command` (string, required): Command to execute
- `timeout` (integer, optional): Timeout in seconds

**Permission:** ASK (AUTO for safe commands, DENY for dangerous)

## Error Handling

### Common Exceptions

#### `LLMError`
```python
class LLMError(Exception):
    """Error from LLM API."""
```

#### `ToolError`
```python
class ToolError(Exception):
    """Error from tool execution."""
```

#### `PermissionDeniedError`
```python
class PermissionDeniedError(Exception):
    """Permission denied for operation."""
```

#### `ConfigurationError`
```python
class ConfigurationError(Exception):
    """Configuration error."""
```

### Error Recovery
The system includes automatic retry for:
- Network timeouts
- API rate limits
- Temporary failures

## Configuration

### Environment Variables
```python
# Required
LUNVEX_API_KEY: str

# Optional
LUNVEX_DEBUG: bool = False
LUNVEX_HISTORY_DIR: Optional[str] = None
LUNVEX_MAX_TOKENS: int = 2000
```

### Configuration Files
- `LUNVEX.md`: Project context file
- `~/.lunvex-code/config.yaml`: User configuration (future)

## Examples

### Basic Usage
```python
from deepseek_code.llm import LunVexClient
from deepseek_code.context import get_project_context
from deepseek_code.agent import Agent, AgentConfig

# Initialize components
client = LunVexClient()
context = get_project_context()
config = AgentConfig()

# Create agent
agent = Agent(client, context, config)

# Run task
response = agent.run("List all Python files in the project")
print(response)
```

### Custom Tool Integration
```python
from deepseek_code.tools.base import Tool, ToolResult
from deepseek_code.tools.base import create_default_registry

class CustomTool(Tool):
    name = "custom_tool"
    description = "My custom tool"
    parameters = {
        "input": {"type": "string", "description": "Input value", "required": True}
    }
    
    def execute(self, **kwargs) -> ToolResult:
        input_val = kwargs["input"]
        # Process input
        return ToolResult(success=True, output=f"Processed: {input_val}")

# Register tool
registry = create_default_registry()
registry.register(CustomTool())
```

### Custom Permission Rules
```python
from deepseek_code.permissions import PermissionManager, PermissionRule, PermissionLevel

class TimeBasedRule(PermissionRule):
    def check(self, tool_name, tool_input):
        from datetime import datetime
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Business hours
            if tool_name == "bash" and "deploy" in tool_input.get("command", ""):
                return PermissionLevel.DENY
        return None
    
    def get_reason(self):
        return "Business hours restriction"

# Add rule
manager = PermissionManager()
manager.add_rule(TimeBasedRule())
```

## Best Practices

### 1. Tool Design
- Keep tools focused and single-purpose
- Validate all input parameters
- Provide clear error messages
- Handle edge cases gracefully

### 2. Permission Rules
- Default to ASK for safety
- Be specific with patterns
- Document rule reasons
- Test rules thoroughly

### 3. Error Handling
- Use appropriate exception types
- Include context in error messages
- Implement retry logic for transient failures
- Log errors for debugging

### 4. Performance
- Cache expensive operations
- Use streaming for large files
- Limit memory usage
- Profile critical paths

## Version Compatibility

### Python Version
- Minimum: Python 3.10
- Tested: Python 3.10, 3.11, 3.12
- Future: Python 3.13+

### API Stability
- Public API marked in this document is stable
- Internal APIs may change without notice
- Breaking changes will be documented in CHANGELOG

## Contributing to API Documentation

To update this documentation:
1. Update the relevant code with docstrings
2. Update this file to reflect changes
3. Ensure examples are accurate
4. Test documentation changes

## Support

For API-related questions:
1. Check this documentation
2. Review source code
3. Open GitHub issue
4. Check existing issues for similar questions

---

This API reference is maintained alongside the code. Last updated for version 0.1.0.