# LunVex Code Test System

This directory contains comprehensive tests for the LunVex Code AI assistant system.

## Test Structure

### Core Tests
- `test_agent.py` - Main agent functionality tests
- `test_tools.py` - Tool system tests
- `test_llm.py` - LLM client tests
- `test_context.py` - Project context tests
- `test_cli.py` - CLI interface tests

### Async System Tests
- `test_async_agent.py` - Async agent implementation tests
- `test_async_tools.py` - Async tool system tests
- `test_async_smoke.py` - Async system smoke tests

### Integration Tests
- `test_integration.py` - End-to-end integration tests
- `test_smoke.py` - System smoke tests

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Core tests
pytest tests/test_agent.py tests/test_tools.py tests/test_llm.py tests/test_context.py tests/test_cli.py

# Async tests
pytest tests/test_async_agent.py tests/test_async_tools.py tests/test_async_smoke.py

# Integration tests
pytest tests/test_integration.py tests/test_smoke.py
```

### Run with Coverage
```bash
pytest --cov=lunvex_code --cov-report=html
```

### Run Smoke Tests Only
```bash
# Run all smoke tests
python tests/test_smoke.py

# Run async smoke tests
python tests/test_async_smoke.py
```

## Test Design Principles

### 1. Isolation
- Tests should be independent and not rely on external services
- Use mocks for LLM API calls
- Use temporary files and directories for file operations

### 2. Coverage
- Test both success and error cases
- Test edge cases and boundary conditions
- Test sync and async implementations

### 3. Readability
- Clear test names that describe what is being tested
- Minimal setup code
- Assertions should be clear and meaningful

### 4. Performance
- Tests should run quickly
- Avoid unnecessary I/O operations
- Use appropriate fixtures for expensive setup

## Async Testing Guidelines

### Using pytest-asyncio
All async tests are marked with `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result.success
```

### Mocking Async Functions
Use `AsyncMock` for mocking async functions:

```python
from unittest.mock import AsyncMock

mock_client = AsyncMock(spec=LunVexClient)
mock_client.chat_completion.return_value = mock_response
```

### Testing Parallel Execution
Test async parallel operations using `asyncio.gather()`:

```python
tasks = [async_tool.execute(param) for _ in range(5)]
results = await asyncio.gather(*tasks)
assert all(r.success for r in results)
```

## Tool Testing Patterns

### File Operations
```python
with tempfile.TemporaryDirectory() as tmpdir:
    test_file = Path(tmpdir) / "test.txt"
    test_file.write_text("test content")
    
    result = await tool.execute(path=str(test_file))
    assert result.success
```

### Mocking LLM Responses
```python
from unittest.mock import MagicMock

mock_response = MagicMock()
mock_response.choices = [MagicMock()]
mock_response.choices[0].message.content = "Test response"

mock_client = MagicMock(spec=LunVexClient)
mock_client.chat_completion.return_value = mock_response
```

## Integration Testing

### End-to-End Tests
Integration tests verify that components work together correctly:

```python
def test_end_to_end_workflow():
    # Setup
    agent = create_test_agent()
    
    # Execute
    result = agent.run_task("Test task")
    
    # Verify
    assert result.success
    assert "expected output" in result.output
```

### Smoke Tests
Smoke tests provide quick verification that the system works:

```python
def test_smoke_basic_operations():
    """Quick test to verify system is functional."""
    assert can_import_modules()
    assert can_create_agent()
    assert can_execute_basic_tools()
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `mock_llm_client` - Mock LLM client
- `test_context` - Test project context
- `temp_dir` - Temporary directory
- `async_agent` - Async agent instance

## Continuous Integration

Tests are automatically run on:
- Push to main branch
- Pull requests
- Scheduled runs

## Debugging Tests

### Verbose Output
```bash
pytest -v
```

### Debug on Failure
```bash
pytest --pdb
```

### Show Logs
```bash
pytest --log-cli-level=DEBUG
```

## Adding New Tests

1. Follow existing patterns and conventions
2. Add appropriate test markers
3. Ensure tests are isolated and fast
4. Include both success and failure cases
5. Update this README if adding new test categories

## Test Coverage Goals

- Core functionality: 90%+
- Tool implementations: 85%+
- Async system: 85%+
- Integration: 80%+

Current coverage can be checked with:
```bash
pytest --cov=lunvex_code --cov-report=term-missing
```