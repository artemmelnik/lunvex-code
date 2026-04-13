# Project Structure

This document describes the organization of the LunVex Code project.

## Directory Layout

```
lunvex-code/
├── lunvex_code/              # Main Python package
│   ├── __init__.py           # Package exports and constants
│   ├── agent.py              # Synchronous agent implementation
│   ├── async_agent.py        # Asynchronous agent implementation
│   ├── cli.py                # Synchronous CLI entry point
│   ├── async_cli.py          # Asynchronous CLI entry point
│   ├── llm.py                # LLM client interface
│   ├── permissions.py        # Permission system
│   ├── context.py            # Project context management
│   ├── conversation.py       # Conversation history
│   ├── cache.py              # File caching system
│   ├── llm_cache.py          # LLM response caching
│   ├── progress.py           # Progress tracking and UI
│   ├── task_planner.py       # Intelligent task planning
│   ├── ui.py                 # User interface components
│   └── tools/                # Tool implementations
│       ├── __init__.py       # Tool exports
│       ├── base.py           # Tool base class
│       ├── async_base.py     # Async tool base class
│       ├── file_tools.py     # File operations (sync)
│       ├── async_file_tools.py # File operations (async)
│       ├── search_tools.py   # Search operations (sync)
│       ├── async_search_tools.py # Search operations (async)
│       ├── bash_tool.py      # Bash execution (sync)
│       ├── async_bash_tool.py # Bash execution (async)
│       ├── web_tools.py      # Web operations (sync)
│       ├── async_web_tools.py # Web operations (async)
│       ├── git_tools.py      # Git integration
│       ├── cache_tools.py    # Cache management
│       ├── llm_cache_tools.py # LLM cache management
│       ├── progress_decorators.py # Progress indicators
│       └── dependencies/     # Dependency management tools
│
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── performance/        # Performance tests
│   └── __init__.py
│
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md     # System architecture
│   ├── DEVELOPER_GUIDE.md  # Development guide
│   ├── USER_GUIDE.md       # User guide
│   ├── API.md              # API reference
│   └── ...                 # Other documentation files
│
├── examples/               # Usage examples
│   ├── demo_cache_performance.py
│   ├── demo_llm_cache.py
│   ├── demo_progress.py
│   ├── task_planning_example.py
│   └── ...
│
├── scripts/               # Utility scripts
│   ├── setup_pre_commit.sh
│   ├── test_installation.py
│   ├── prepare_release.py
│   └── ...
│
├── config/                # Configuration files
│   ├── .env.example       # Environment variables template
│   └── .lunvex-deps.yaml  # Dependency configuration
│
├── data/                  # Test data and resources
│
├── .pre-commit-config.yaml # Pre-commit hooks
├── pyproject.toml         # Project configuration
├── requirements.txt       # Python dependencies
├── README.md             # Main documentation
├── LICENSE               # MIT License
└── ...
```

## Key Directories Explained

### `lunvex_code/` - Main Package
Contains all the core functionality:
- **Agent**: Orchestrates LLM interactions and tool usage
- **CLI**: Command-line interfaces (sync and async)
- **Tools**: Individual tool implementations
- **LLM**: Interface to DeepSeek API
- **Cache**: File and LLM response caching
- **UI**: Rich terminal interface components

### `tests/` - Test Suite
Organized by test type:
- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **Performance tests**: Benchmark async operations

### `docs/` - Documentation
Comprehensive documentation covering:
- Architecture and design decisions
- User guides and examples
- API references
- Development workflows

### `examples/` - Usage Examples
Practical examples demonstrating:
- Cache performance optimization
- LLM cache usage
- Progress tracking
- Task planning system
- Git integration

### `scripts/` - Utility Scripts
Automation scripts for:
- Development setup
- Testing
- Release preparation
- Security checks

### `config/` - Configuration
Configuration files:
- Environment variables template
- Dependency management configuration

## File Naming Conventions

1. **Python files**: Use snake_case (e.g., `file_tools.py`)
2. **Test files**: Prefix with `test_` (e.g., `test_agent.py`)
3. **Documentation**: Use UPPER_CASE.md (e.g., `ARCHITECTURE.md`)
4. **Configuration**: Use dot-prefix for hidden files (e.g., `.env.example`)

## Import Structure

```python
# Absolute imports within the package
from lunvex_code.agent import Agent
from lunvex_code.tools.file_tools import ReadFileTool

# Relative imports within the same module
from .base import Tool
from ..llm import LunVexClient
```

## Adding New Components

When adding new components:

1. **Tools**: Add to `lunvex_code/tools/` with both sync and async versions
2. **Tests**: Add corresponding tests in `tests/`
3. **Documentation**: Update relevant `.md` files in `docs/`
4. **Examples**: Add usage examples in `examples/`
