# Type Hints Guide

This guide explains how to use type hints in the LunVex Code project and why they're important.

## Why Type Hints?

Type hints provide several benefits:

1. **Better Documentation**: Types serve as documentation that's always up-to-date
2. **Early Error Detection**: Catch type-related errors before runtime
3. **Improved IDE Support**: Better autocomplete, navigation, and refactoring
4. **Maintainability**: Makes code easier to understand and modify
5. **Tooling Support**: Enables static analysis with mypy, pyright, etc.

## Type Hint Standards

### Required Type Hints
- All public functions and methods
- All class attributes (using `ClassVar` or type comments)
- Function return types
- Method parameters (except `self` and `cls`)

### Optional Type Hints
- Private methods (starting with `_`)
- Local variables (when it improves clarity)
- Complex type relationships

## Basic Examples

### Function with Type Hints
```python
from typing import List, Optional, Dict, Any

def read_file(path: str, limit: Optional[int] = None) -> str:
    """
    Read contents of a file.

    Args:
        path: Path to the file
        limit: Maximum number of lines to read

    Returns:
        File contents as string
    """
    # Implementation
```

### Class with Type Hints
```python
from dataclasses import dataclass
from typing import ClassVar, List

@dataclass
class AgentConfig:
    """Configuration for the agent."""

    max_turns: int = 50
    trust_mode: bool = False
    verbose: bool = False

    # Class variable with type hint
    DEFAULT_MODEL: ClassVar[str] = "deepseek-coder"
```

### Async Functions
```python
from typing import Awaitable

async def read_file_async(path: str) -> Awaitable[str]:
    """Async version of read_file."""
    # Implementation
```

## Common Type Patterns

### Collections
```python
from typing import List, Dict, Set, Tuple, Optional

# Lists
files: List[str] = ["file1.py", "file2.py"]

# Dictionaries
config: Dict[str, Any] = {"key": "value"}

# Sets
unique_names: Set[str] = {"alice", "bob"}

# Tuples (fixed length)
coordinates: Tuple[float, float] = (10.5, 20.3)

# Optional values
maybe_value: Optional[str] = None
```

### Union Types
```python
from typing import Union

# Value can be string or integer
identifier: Union[str, int] = "user123"
identifier = 123  # Also valid
```

### Type Aliases
```python
from typing import Dict, List, TypeAlias

# Create a type alias for complex types
FileCache: TypeAlias = Dict[str, Tuple[str, float]]
SearchResults: TypeAlias = List[Dict[str, str]]
```

## Advanced Patterns

### Generics
```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()
```

### Callable Types
```python
from typing import Callable, List

# Function that takes int and returns str
int_to_str: Callable[[int], str] = str

# Function with keyword arguments
processor: Callable[..., str] = some_processing_function
```

### Literal Types
```python
from typing import Literal

# Only specific string values allowed
mode: Literal["read", "write", "append"] = "read"
permission: Literal["auto", "ask", "deny"] = "ask"
```

## Tools for Type Checking

### mypy
```bash
# Basic check
python -m mypy lunvex_code/

# With strict mode
python -m mypy lunvex_code/ --strict

# Ignore missing imports
python -m mypy lunvex_code/ --ignore-missing-imports
```

### pyright (VS Code Pylance)
```bash
# Install
pip install pyright

# Run
pyright lunvex_code/
```

### ruff
```bash
# Check for missing type hints
ruff check lunvex_code/ --select ANN

# Auto-fix where possible
ruff check --fix lunvex_code/ --select ANN
```

## Common Issues and Solutions

### Circular Imports
```python
# Instead of importing at top level
from .other_module import SomeClass  # Causes circular import

# Use string literals or TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .other_module import SomeClass

def process(obj: 'SomeClass') -> None:
    # Implementation
```

### Forward References
```python
from __future__ import annotations  # Python 3.7+

class Node:
    def connect(self, other: Node) -> None:  # Works with future import
        pass
```

### Dynamic Types
```python
from typing import Any, cast

# When type is truly dynamic
def process_any(data: Any) -> Any:
    return data

# When you know the type but checker doesn't
result = some_untyped_function()
typed_result = cast(List[str], result)
```

## Project Standards

### Minimum Coverage
- **Public API**: 100% type hints required
- **Internal functions**: At least 80% type hints
- **New code**: 100% type hints required

### Checking Type Coverage
```bash
# Run the type coverage check
python scripts/check_typing.py

# Output shows which files need improvement
```

### Pre-commit Hook
The project includes a pre-commit hook that checks type hint coverage. It runs on every commit and blocks commits if type coverage drops below 80%.

## Resources

- [Python Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [Real Python Type Hints Guide](https://realpython.com/python-type-checking/)
- [Python Type Checking (Book)](https://www.amazon.com/Python-Type-Checking-Dane-Hillard/dp/1617299885)
