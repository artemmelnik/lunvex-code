# Developer Guide

This guide is for developers who want to contribute to LunVex Code or extend its functionality.

## Development Environment Setup

### Prerequisites
- Python 3.10 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/artemmelnik/lunvex-code.git
cd lunvex-code

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Set up pre-commit hooks (optional)
pre-commit install
```

### Configuration
Create a `.env` file in the project root:
```bash
DEEPSEEK_API_KEY=your_api_key_here
```

## Project Structure

```
lunvex-code/
├── lunvex_code/          # Main package
│   ├── __init__.py        # Package exports and constants
│   ├── cli.py             # Command-line interface
│   ├── agent.py           # Core agent logic
│   ├── llm.py             # LLM client interface
│   ├── permissions.py     # Permission system
│   ├── context.py         # Project context management
│   ├── conversation.py    # Conversation history
│   ├── ui.py              # User interface components
│   └── tools/             # Tool implementations
│       ├── __init__.py    # Tool exports
│       ├── base.py        # Tool base class
│       ├── file_tools.py  # File operations
│       ├── search_tools.py # Search operations
│       └── bash_tool.py   # Shell command execution
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Example code
├── pyproject.toml         # Project configuration
└── README.md              # Project overview
```

## Architecture Overview

### Core Concepts
1. **Agent**: Orchestrates LLM interactions and tool execution
2. **Tools**: Modular components that perform specific actions
3. **Permissions**: Rule-based system controlling tool access
4. **Context**: Project-specific information and configuration
5. **Conversation**: Persistent chat history management

### Data Flow
```
User Input → CLI → Agent → LLM → Tool Calls → Permission Check → Execution → Results → Response
```

## Creating Custom Tools

### Tool Base Class
All tools inherit from `lunvex_code.tools.base.Tool`:

```python
from lunvex_code.tools.base import Tool, ToolResult

class MyCustomTool(Tool):
    name = "my_tool"
    description = "Description of what this tool does"
    parameters = {
        "param1": {
            "type": "string",
            "description": "Description of parameter 1",
            "required": True
        },
        "param2": {
            "type": "integer", 
            "description": "Description of parameter 2",
            "required": False
        }
    }
    permission_level = "ask"  # or "auto" or "deny"

    def execute(self, **kwargs) -> ToolResult:
        # Your tool logic here
        try:
            result = self._do_something(kwargs["param1"], kwargs.get("param2"))
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(success=False, output=str(e), error=str(e))
```

### Tool Registration
Tools are automatically registered when imported. Ensure your tool is imported in `lunvex_code/tools/__init__.py`:

```python
# In lunvex_code/tools/__init__.py
from .my_custom_tool import MyCustomTool

__all__ = [
    # ... existing tools ...
    "MyCustomTool",
]
```

### Example: Simple Calculator Tool
```python
from lunvex_code.tools.base import Tool, ToolResult

class CalculatorTool(Tool):
    name = "calculator"
    description = "Perform basic arithmetic operations"
    parameters = {
        "operation": {
            "type": "string",
            "description": "Operation to perform: add, subtract, multiply, divide",
            "required": True
        },
        "a": {
            "type": "number",
            "description": "First number",
            "required": True
        },
        "b": {
            "type": "number",
            "description": "Second number",
            "required": True
        }
    }
    permission_level = "auto"

    def execute(self, **kwargs) -> ToolResult:
        operation = kwargs["operation"]
        a = kwargs["a"]
        b = kwargs["b"]
        
        try:
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    return ToolResult(success=False, output="Division by zero", error="Division by zero")
                result = a / b
            else:
                return ToolResult(success=False, output=f"Unknown operation: {operation}")
            
            return ToolResult(success=True, output=f"Result: {result}")
        except Exception as e:
            return ToolResult(success=False, output=str(e), error=str(e))
```

## Extending the Permission System

### Permission Rule Types
The permission system supports several rule types:

1. **ToolNameRule**: Match tools by exact name
2. **ToolNamePatternRule**: Match tools by regex pattern
3. **InputPatternRule**: Match tool input by regex pattern
4. **CompositeRule**: Combine multiple rules with AND/OR logic
5. **SessionRule**: Session-specific allow/deny lists

### Creating Custom Permission Rules
```python
from lunvex_code.permissions import PermissionRule, PermissionLevel
from typing import Optional, Dict, Any

class TimeBasedRule(PermissionRule):
    """Restrict operations during business hours."""
    
    def __init__(self, business_hours_start=9, business_hours_end=17):
        self.start = business_hours_start
        self.end = business_hours_end
    
    def check(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[PermissionLevel]:
        from datetime import datetime
        
        current_hour = datetime.now().hour
        
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
                    import re
                    if re.search(pattern, command, re.IGNORECASE):
                        return PermissionLevel.DENY
        
        return None
    
    def get_reason(self) -> Optional[str]:
        return "Business hours restriction"
```

### Registering Custom Rules
```python
from lunvex_code.permissions import PermissionManager

manager = PermissionManager()
custom_rule = TimeBasedRule(business_hours_start=9, business_hours_end=17)
manager.add_rule(custom_rule)
```

## Working with the LLM Client

### Basic Usage
```python
from lunvex_code.llm import LunVexClient

client = LunVexClient(api_key="your_api_key")

# Simple completion
response = client.complete("What is Python?")
print(response.content)

# With tools
tools = [...]  # List of tool schemas
response = client.complete_with_tools(
    "Please list files in the current directory",
    tools=tools
)
```

### Customizing LLM Behavior
```python
from lunvex_code.llm import LunVexClient

client = LunVexClient(
    api_key="your_api_key",
    model="deepseek-chat",
    temperature=0.7,
    max_tokens=2000,
    timeout=30,
    max_retries=3
)
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_permissions.py

# Run with coverage
pytest --cov=lunvex_code

# Run with verbose output
pytest -v

# Run with specific test
pytest tests/test_tools.py::TestReadFileTool::test_read_file_success
```

### Writing Tests
```python
import pytest
from lunvex_code.tools.file_tools import ReadFileTool

class TestMyCustomTool:
    def test_tool_success(self):
        tool = MyCustomTool()
        result = tool.execute(param1="value1", param2=42)
        assert result.success is True
        assert "expected output" in result.output
    
    def test_tool_failure(self):
        tool = MyCustomTool()
        result = tool.execute(param1="invalid")
        assert result.success is False
        assert result.error is not None
    
    @pytest.fixture
    def sample_data(self):
        return {"key": "value"}
    
    def test_with_fixture(self, sample_data):
        tool = MyCustomTool()
        result = tool.execute(**sample_data)
        # assertions...
```

### Mocking External Dependencies
```python
from unittest.mock import Mock, patch
import pytest

class TestLLMClient:
    @patch('lunvex_code.llm.openai.OpenAI')
    def test_completion(self, mock_openai):
        # Setup mock
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Mock response"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Test
        client = LunVexClient(api_key="test")
        response = client.complete("test prompt")
        
        assert response.content == "Mock response"
```

## Debugging

### Logging
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger("lunvex_code")
logger.setLevel(logging.DEBUG)
```

### Debug Mode
Run the CLI with debug flags:
```bash
lunvex-code run --verbose "your task"
```

### Interactive Debugging
```python
# Add breakpoints
import pdb; pdb.set_trace()

# Or use IPython
from IPython import embed; embed()
```

## Code Style and Quality

### Formatting
```bash
# Format code with black
black lunvex_code tests

# Sort imports with isort
isort lunvex_code tests

# Check formatting
black --check lunvex_code tests
```

### Linting
```bash
# Run ruff linter
ruff check lunvex_code tests

# Fix linting issues
ruff check --fix lunvex_code tests

# Type checking with mypy (if configured)
mypy lunvex_code
```

### Pre-commit Hooks
Install pre-commit to automatically check code quality:
```bash
pre-commit install
pre-commit run --all-files
```

## Building and Distribution

### Building the Package
```bash
# Build wheel and source distribution
python -m build

# Check build
twine check dist/*
```

### Local Installation
```bash
# Install in development mode
pip install -e .

# Install with all dependencies
pip install -e .[dev]
```

### Testing Installation
```bash
# Create clean virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from local build
pip install dist/lunvex_code-*.whl

# Test installation
lunvex-code --version
```

## Contributing Workflow

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/lunvex-code.git
cd lunvex-code
git remote add upstream https://github.com/artemmelnik/lunvex-code.git
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Write code
- Add tests
- Update documentation
- Ensure all tests pass

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add your feature

Detailed description of changes:
- Change 1
- Change 2
- Fixes #123"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
# Then create PR on GitHub
```

### Commit Message Convention
Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

## Performance Optimization

### Profiling
```python
import cProfile
import pstats
from lunvex_code.cli import main

# Profile CLI execution
profiler = cProfile.Profile()
profiler.enable()
main(["run", "test task"])
profiler.disable()

# Save results
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Memory Profiling
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Your code here
    pass
```

### Benchmarking
```python
import timeit

def benchmark_tool():
    tool = ReadFileTool()
    return tool.execute(path="README.md")

execution_time = timeit.timeit(benchmark_tool, number=100)
print(f"Average execution time: {execution_time/100:.4f} seconds")
```

## Security Considerations

### Input Validation
Always validate tool inputs:
```python
def execute(self, **kwargs) -> ToolResult:
    path = kwargs.get("path")
    if not path:
        return ToolResult(success=False, error="Path is required")
    
    # Prevent path traversal
    if ".." in path or path.startswith("/"):
        return ToolResult(success=False, error="Invalid path")
    
    # Rest of implementation...
```

### Safe Command Execution
```python
import subprocess
import shlex

def execute_safe_command(command):
    # Validate command
    if any(dangerous in command for dangerous in ["rm -rf", "sudo", "| sh"]):
        raise ValueError("Dangerous command detected")
    
    # Use shell=False and explicit arguments
    args = shlex.split(command)
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    
    return result
```

### Environment Isolation
```python
import os

# Run in isolated environment
env = os.environ.copy()
env.pop("SENSITIVE_VAR", None)  # Remove sensitive variables

subprocess.run(command, env=env, ...)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check Python version (>=3.10)
   - Run `pip install -e .[dev]`

2. **API Key Issues**
   - Set `DEEPSEEK_API_KEY` environment variable
   - Check API key validity
   - Verify network connectivity

3. **Permission Denied**
   - Check file permissions
   - Verify working directory
   - Review permission rules

4. **Test Failures**
   - Run tests with `pytest -v` for details
   - Check test dependencies
   - Ensure clean test environment

### Getting Help
- Check existing GitHub issues
- Review documentation
- Ask in community channels
- Create minimal reproducible example

## Advanced Topics

### Plugin System (Future)
```python
# Example plugin structure
class MyPlugin:
    def get_tools(self):
        return [MyCustomTool()]
    
    def get_permission_rules(self):
        return [MyPermissionRule()]
    
    def initialize(self, context):
        # Plugin initialization
        pass
```

### Custom LLM Providers
```python
from lunvex_code.llm import BaseLLMClient

class CustomLLMClient(BaseLLMClient):
    def complete(self, messages, tools=None):
        # Custom implementation
        pass
    
    def complete_with_tools(self, messages, tools):
        # Custom implementation
        pass
```

### Event System (Future)
```python
from lunvex_code.events import EventBus

# Subscribe to events
event_bus.subscribe("tool_executed", handle_tool_execution)

# Publish events
event_bus.publish("permission_checked", {"tool": "bash", "allowed": True})
```

## Resources

### Documentation
- [Architecture](ARCHITECTURE.md)
- [Permission System](PermissionSystem.md)
- [Roadmap](ROADMAP.md)
- [API Reference](API.md) (TODO)

### External Resources
- [LunVex API Documentation](https://platform.deepseek.com/api-docs/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Community
- [GitHub Issues](https://github.com/artemmelnik/lunvex-code/issues)
- [Discord/Slack](TODO)
- [Stack Overflow](TODO) tag: lunvex-code
