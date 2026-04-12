# Architecture

LunVex Code is a terminal-based AI coding assistant that helps developers work inside real projects from their shell. This document describes the system components, boundaries, dependencies, and runtime flow.

## System Overview

LunVex Code follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    CLI      │  │     UI      │  │  Conversation       │  │
│  │  (typer)    │  │   (rich)    │  │   History          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Core Business Logic                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Agent    │  │   Context   │  │   Permissions       │  │
│  │             │  │  Management │  │    System           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     External Integration                     │
│  ┌─────────────┐  ┌───────────────────────────────────────┐  │
│  │    LLM      │  │              Tools                    │  │
│  │  (DeepSeek) │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     │  │
│  └─────────────┘  │  │File │ │Bash │ │Edit │ │Search│ ... │  │
│                   │  └─────┘ └─────┘ └─────┘ └─────┘     │  │
│                   └───────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CLI (Command Line Interface)
**File:** `lunvex_code/cli.py`
- Entry point for the application using Typer
- Handles command parsing and routing
- Manages interactive REPL mode and one-shot tasks
- Supports different modes: default, trust, YOLO

### 2. Agent
**File:** `lunvex_code/agent.py`
- Orchestrates the interaction between LLM and tools
- Manages conversation flow and turn limits
- Handles tool execution with permission checks
- Maintains conversation state and history

### 3. LLM Client
**File:** `lunvex_code/llm.py`
- Interface to LunVex API (OpenAI-compatible)
- Handles API communication, error handling, and retries
- Manages token limits and response parsing
- Supports tool calling with function definitions

### 4. Permission System
**File:** `lunvex_code/permissions.py`
- Extensible rule-based permission management
- Three permission levels: AUTO, ASK, DENY
- Default rules for common operations
- Session-specific allow/deny lists
- Support for custom permission rules

### 5. Tools System
**Directory:** `lunvex_code/tools/`
- **Base:** `base.py` - Abstract base class for tools
- **File Operations:** `file_tools.py` - read_file, write_file, edit_file
- **Search Operations:** `search_tools.py` - glob, grep
- **Shell Operations:** `bash_tool.py` - bash command execution
- **Cache Operations:** `cache_tools.py` - cache management tools
- **Tool Registry:** Manages tool registration and discovery

### 6. Context Management
**File:** `lunvex_code/context.py`
- Detects project root based on markers (.git, LUNVEX.md, etc.)
- Loads and manages project context from LUNVEX.md
- Builds system prompts with project-specific information
- Handles working directory and project boundaries

### 7. User Interface
**File:** `lunvex_code/ui.py`
- Rich terminal output with formatting
- Permission prompts and user confirmation
- Progress indicators and status messages
- Color-coded output for different message types

### 8. Cache System
**File:** `lunvex_code/cache.py`
- LRU cache for file contents with TTL expiration
- Automatic invalidation when files are modified
- Metadata validation for cache consistency
- Configurable via environment variables or CLI
- Global cache instance with statistics tracking

### 9. Conversation Management
**File:** `lunvex_code/conversation.py`
- Maintains conversation history between sessions
- Serializes/deserializes conversation state
- Manages message history for LLM context
- Supports persistent storage in user home directory

## Data Flow

### 1. Startup Sequence
```
User Command → CLI Parser → Project Detection → Context Loading → Agent Initialization
```

### 2. Interactive Loop
```
1. User Input → Agent
2. Agent → LLM (with conversation history + tools)
3. LLM → Tool Calls (if any)
4. Permission Check → User Approval (if needed)
5. Tool Execution → Results
6. Results → LLM → Response
7. Response → User
8. Repeat
```

### 3. Tool Execution Flow
```
Tool Call → Permission Check → Input Validation → Execution → Result Formatting → Agent
```

## Dependencies

### Core Dependencies
- `openai>=1.0.0` - LLM API client
- `typer>=0.9.0` - CLI framework
- `rich>=13.0.0` - Terminal formatting
- `prompt-toolkit>=3.0.0` - Interactive prompts
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment management

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing
- `black>=23.0.0` - Code formatting
- `ruff>=0.1.0` - Linting

## Configuration

### Environment Variables
- `DEEPSEEK_API_KEY` - API key for DeepSeek
- (Optional) Project-specific settings in `LUNVEX.md`

### Configuration Files
- `LUNVEX.md` - Project context and instructions
- `~/.lunvex-code/` - User state directory
  - `prompt_history` - Command history
  - `conversations/` - Saved conversations

## Security Considerations

### Permission Model
1. **Read Operations**: Auto-approved (read_file, glob, grep)
2. **Write Operations**: Ask by default (write_file, edit_file)
3. **Shell Commands**: Ask by default, with safe commands auto-approved
4. **Dangerous Operations**: Always denied (rm -rf /, sudo, etc.)

### Safety Features
- Input validation for all tool parameters
- Path traversal prevention
- Dangerous command pattern matching
- Session isolation
- No automatic execution of untrusted code

## Extension Points

### 1. Custom Tools
Create new tools by extending the `Tool` base class and registering them with the tool registry.

### 2. Custom Permission Rules
Implement custom `PermissionRule` classes for specialized permission logic.

### 3. Project Context
Add project-specific instructions and commands in `LUNVEX.md`.

### 4. LLM Providers
Swap out the LLM client for different providers (requires API compatibility).

## Performance Considerations

### Memory Management
- Conversation history limited by token count
- File operations handle large files with streaming
- Tool results are summarized when large

### Network Optimization
- API calls with timeout and retry logic
- Connection pooling for frequent requests
- Caching of project context

### Disk I/O
- Asynchronous file operations where appropriate
- Buffered reading/writing for large files
- Temporary file cleanup

## Error Handling

### Graceful Degradation
- Network failures: Retry with exponential backoff
- API errors: Fallback responses with error context
- Tool failures: Detailed error messages for debugging
- Permission denials: Clear explanations to users

### Logging
- Structured logging for debugging
- Error reporting with context
- Performance metrics collection

## Testing Strategy

### Unit Tests
- Individual component testing
- Mock external dependencies
- Permission rule validation

### Integration Tests
- End-to-end workflow testing
- Tool execution scenarios
- Permission system integration

### System Tests
- Full CLI command testing
- Interactive session simulation
- Error condition handling

## Deployment

### Installation Methods
1. **Local Development**: `pip install -e .[dev]`
2. **Production**: `pip install lunvex-code`
3. **Docker**: Containerized deployment

### Distribution
- PyPI package distribution
- Docker images
- System packages (deb, rpm)

## Monitoring and Observability

### Metrics
- API call latency and success rates
- Tool execution times
- User interaction patterns
- Error rates and types

### Health Checks
- API connectivity verification
- Disk space monitoring
- Permission system validation
- Tool availability checks

## Future Architecture Considerations

### Scalability
- Support for multiple concurrent sessions
- Distributed tool execution
- Load balancing for LLM requests

### Extensibility
- Plugin system for third-party tools
- Configuration-driven rule sets
- Custom UI themes and layouts

### Integration
- IDE plugin support
- CI/CD pipeline integration
- Version control system hooks
