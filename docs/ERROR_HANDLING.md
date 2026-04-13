# Error Handling Guide

This guide describes the error handling patterns used in LunVex Code.

## Philosophy

1. **Fail Fast**: Detect errors as early as possible
2. **Graceful Degradation**: Recover when possible, fail gracefully when not
3. **Informative Messages**: Provide clear, actionable error messages
4. **Structured Logging**: Log errors with context for debugging
5. **User-Friendly**: Don't expose implementation details to users

## Error Hierarchy

### Base Exception Classes
```python
class LunVexError(Exception):
    """Base exception for all LunVex Code errors."""
    pass

class ConfigurationError(LunVexError):
    """Errors related to configuration."""
    pass

class PermissionError(LunVexError):
    """Errors related to permissions."""
    pass

class ToolExecutionError(LunVexError):
    """Errors during tool execution."""
    pass

class LLMError(LunVexError):
    """Errors from LLM API calls."""
    pass

class ValidationError(LunVexError):
    """Data validation errors."""
    pass
```

## Error Handling Patterns

### 1. Try-Except with Specific Exceptions
```python
try:
    result = tool.execute(**arguments)
except ToolExecutionError as e:
    # Handle known tool errors
    ui.print_error(f"Tool failed: {e}")
    return fallback_result
except Exception as e:
    # Handle unexpected errors
    logger.exception("Unexpected error in tool execution")
    ui.print_error("An unexpected error occurred")
    return safe_default
```

### 2. Context Managers for Resources
```python
from contextlib import contextmanager

@contextmanager
def safe_file_operation(path: str):
    """Context manager for safe file operations."""
    try:
        yield
    except FileNotFoundError:
        raise ToolExecutionError(f"File not found: {path}")
    except PermissionError:
        raise ToolExecutionError(f"Permission denied: {path}")
    except Exception as e:
        raise ToolExecutionError(f"File operation failed: {str(e)}")

# Usage
with safe_file_operation(filepath):
    content = read_file(filepath)
```

### 3. Retry with Exponential Backoff
```python
import time
from typing import Callable, TypeVar

T = TypeVar('T')

def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: tuple = (Exception,)
) -> T:
    """Retry a function with exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
            time.sleep(delay)

    raise RuntimeError("Should never reach here")

# Usage
response = retry_with_backoff(
    lambda: llm_client.chat(messages),
    exceptions=(LLMError, ConnectionError)
)
```

## Error Messages

### Good Error Messages
- **Clear**: "Cannot write to file: permission denied"
- **Actionable**: "Please check your API key in .env file"
- **Contextual**: "Failed to parse JSON in config.yaml at line 10"
- **User-friendly**: "The file appears to be locked by another process"

### Bad Error Messages
- ❌ `"Error: -13"`
- ❌ `"Something went wrong"`
- ❌ `"PermissionError: [Errno 13]"`
- ❌ Stack traces shown to users

## Logging Errors

### Structured Logging
```python
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def log_error(error: Exception, context: dict = None):
    """Log an error with structured context."""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
    }

    logger.error(json.dumps(log_data))

    # Also print user-friendly message
    ui.print_error(f"Error: {get_user_friendly_message(error)}")

# Usage
try:
    risky_operation()
except Exception as e:
    log_error(e, {"operation": "risky_operation", "user": current_user})
```

## Tool Error Handling

### Tool Result Pattern
```python
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ToolResult:
    """Standardized result from tool execution."""
    success: bool
    output: str
    error: Optional[str] = None
    data: Optional[Any] = None

    @classmethod
    def success(cls, output: str, data: Any = None) -> 'ToolResult':
        return cls(success=True, output=output, error=None, data=data)

    @classmethod
    def error(cls, error: str, output: str = "") -> 'ToolResult':
        return cls(success=False, output=output, error=error, data=None)
```

### Tool Execution Wrapper
```python
def execute_tool_safely(tool, **kwargs) -> ToolResult:
    """Execute a tool with comprehensive error handling."""
    try:
        # Validate inputs
        validate_tool_inputs(tool, kwargs)

        # Check permissions
        if not check_permissions(tool, kwargs):
            return ToolResult.error(
                "Permission denied",
                f"Cannot execute {tool.name} with given arguments"
            )

        # Execute tool
        result = tool.execute(**kwargs)

        # Validate output
        if validate_tool_output(result):
            return ToolResult.success(str(result), data=result)
        else:
            return ToolResult.error("Tool returned invalid output")

    except ValidationError as e:
        return ToolResult.error(f"Invalid input: {e}")
    except PermissionError as e:
        return ToolResult.error(f"Permission error: {e}")
    except ToolExecutionError as e:
        return ToolResult.error(f"Tool execution failed: {e}")
    except Exception as e:
        logger.exception("Unexpected error in tool execution")
        return ToolResult.error(f"Unexpected error: {type(e).__name__}")
```

## LLM Error Handling

### API Error Handling
```python
class LLMClient:
    def chat(self, messages, **kwargs) -> LLMResponse:
        try:
            response = self._make_api_call(messages, **kwargs)
            return self._parse_response(response)

        except openai.APIConnectionError as e:
            raise LLMError(f"Connection failed: {e}. Please check your internet.")

        except openai.RateLimitError as e:
            raise LLMError(f"Rate limit exceeded: {e}. Please wait before retrying.")

        except openai.APIStatusError as e:
            if e.status_code == 401:
                raise LLMError("Invalid API key. Please check your DEEPSEEK_API_KEY.")
            elif e.status_code == 429:
                raise LLMError("Too many requests. Please wait before retrying.")
            else:
                raise LLMError(f"API error: {e}")

        except Exception as e:
            raise LLMError(f"Unexpected error: {e}")
```

## User Interface Error Display

### Error Display Functions
```python
def display_error(error: Exception, suggestion: str = None):
    """Display an error to the user in a friendly way."""
    console.print(f"[red]Error:[/red] {get_user_friendly_message(error)}")

    if suggestion:
        console.print(f"[yellow]Suggestion:[/yellow] {suggestion}")

    # Show debug info only in verbose mode
    if config.verbose:
        console.print(f"[dim]Debug: {type(error).__name__}: {str(error)}[/dim]")

def get_user_friendly_message(error: Exception) -> str:
    """Convert technical errors to user-friendly messages."""
    error_map = {
        "FileNotFoundError": "The file was not found",
        "PermissionError": "You don't have permission to access this file",
        "ConnectionError": "Cannot connect to the server. Check your internet.",
        "JSONDecodeError": "The configuration file contains invalid JSON",
        "KeyError": "A required setting is missing from the configuration",
    }

    error_name = type(error).__name__
    return error_map.get(error_name, str(error))
```

## Testing Error Handling

### Error Test Cases
```python
import pytest

def test_tool_error_handling():
    """Test that tools handle errors gracefully."""
    tool = ReadFileTool()

    # Test file not found
    result = tool.execute(path="/nonexistent/file.txt")
    assert not result.success
    assert "not found" in result.error.lower()

    # Test permission error
    result = tool.execute(path="/root/.bashrc")
    assert not result.success
    assert "permission" in result.error.lower()

def test_error_recovery():
    """Test that the system recovers from errors."""
    agent = create_agent()

    # First operation fails
    with pytest.raises(ToolExecutionError):
        agent.run("Read /nonexistent/file.txt")

    # System should still work for next operation
    result = agent.run("List files in current directory")
    assert "README.md" in result
```

## Best Practices

### Do's
- ✅ Use specific exception types
- ✅ Provide context in error messages
- ✅ Log errors with structured data
- ✅ Test error scenarios
- ✅ Gracefully degrade when possible

### Don'ts
- ❌ Catch generic `Exception` without re-raising
- ❌ Swallow errors silently
- ❌ Expose stack traces to users
- ❌ Use error codes without explanations
- ❌ Assume errors won't happen

## Monitoring and Alerting

### Error Metrics
```python
from prometheus_client import Counter, Histogram

ERROR_COUNTER = Counter(
    'lunvex_errors_total',
    'Total number of errors',
    ['error_type', 'tool_name']
)

ERROR_DURATION = Histogram(
    'lunvex_error_duration_seconds',
    'Time spent handling errors',
    ['error_type']
)

def track_error(error: Exception, tool_name: str = None):
    """Track error metrics."""
    error_type = type(error).__name__
    ERROR_COUNTER.labels(error_type=error_type, tool_name=tool_name or '').inc()
```

This error handling approach ensures that LunVex Code is robust, user-friendly, and easy to debug.
