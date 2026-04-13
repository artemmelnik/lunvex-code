# Progress Indicators System

## Overview

The Progress Indicators System provides visual feedback for long-running operations in LunVex Code. It helps users understand what's happening during file operations, searches, and other potentially slow tasks.

## Key Features

- **Multiple indicator types**: Spinners, progress bars, and multi-task progress
- **Minimal overhead**: Lightweight implementation with rich formatting
- **Automatic integration**: Built into core tools
- **Customizable**: Configurable styles and behaviors
- **Context managers**: Easy to use with `with` statements
- **Decorators**: Simple addition to functions and methods

## Indicator Types

### 1. Spinner
Simple animated spinner for indeterminate operations.

```python
from lunvex_code.progress import spinner

with spinner("Processing..."):
    # Your code here
    process_data()
```

### 2. Progress Bar
Visual progress bar for operations with known duration.

```python
from lunvex_code.progress import progress_bar

with progress_bar("Downloading...", total=100) as bar:
    for i in range(100):
        download_chunk(i)
        bar.update((i + 1) / 100, f"Chunk {i+1}/100")
```

### 3. Multi-Task Progress
Track multiple parallel operations.

```python
from lunvex_code.progress import multi_progress

with multi_progress() as multi:
    multi.add_task("download", "Downloading files...", total=100)
    multi.add_task("extract", "Extracting archives...", total=50)
    
    # Update tasks independently
    multi.increment_task("download", 0.1)
    multi.update_task("extract", 0.5, "Halfway there!")
```

## Integration with Tools

### File Operations
- `read_file`: Shows progress for large files (>1MB)
- `write_file`: Shows writing progress
- `edit_file`: Shows editing progress with steps

### Search Operations
- `glob`: Shows search progress with file count
- `grep`: Shows progress with files searched and matches found

### Git Operations
- All Git tools show progress during execution

## Usage Examples

### Basic Usage

```python
from lunvex_code.progress import spinner, progress_bar

# Simple spinner
with spinner("Loading configuration..."):
    load_config()

# Progress bar
with progress_bar("Processing items", total=50) as bar:
    for i in range(50):
        process_item(i)
        bar.increment(0.02, f"Item {i+1}/50")
```

### Function Decorators

```python
from lunvex_code.progress import track_operation
from lunvex_code.tools.progress_decorators import with_progress

@track_operation("Calculating statistics")
def calculate_stats(data):
    # Long calculation
    return process_data(data)

@with_progress("Batch processing", use_bar=True, total=100)
def process_batch(self, items):
    for i, item in enumerate(items):
        process_item(item)
        self._update_progress((i + 1) / len(items))
    return results
```

### Tool Integration

Tools automatically show progress when they perform long operations:

```bash
# These will show progress indicators
lunvex-code run "read the large_data.csv file"
lunvex-code run "search for errors in all python files"
lunvex-code run "find all test files in the project"
```

## Configuration

### ProgressConfig

Customize progress indicators with `ProgressConfig`:

```python
from lunvex_code.progress import ProgressConfig, spinner

config = ProgressConfig(
    show_spinner=True,
    show_percentage=True,
    show_time=True,
    spinner_style="cyan",
    progress_style="green",
    transient=False,  # Don't clear when done
    refresh_per_second=20.0,
)

with spinner("Custom progress", config=config):
    process_data()
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_progress` | bool | True | Enable/disable progress indicators |
| `show_spinner` | bool | True | Show spinner animation |
| `show_percentage` | bool | True | Show percentage complete |
| `show_time` | bool | True | Show elapsed time |
| `show_count` | bool | True | Show item count (for progress bars) |
| `spinner_style` | str | "blue" | Spinner color/style |
| `progress_style` | str | "green" | Progress bar color/style |
| `text_style` | str | "white" | Text color/style |
| `error_style` | str | "red" | Error message style |
| `success_style` | str | "green" | Success message style |
| `auto_close` | bool | True | Close progress when done |
| `transient` | bool | True | Clear progress when done |
| `refresh_per_second` | float | 10.0 | Update frequency |
| `width` | int | None | Fixed width (None = auto) |
| `min_width` | int | 40 | Minimum display width |
| `max_width` | int | 80 | Maximum display width |

## Advanced Usage

### ProgressAwareMixin

Add progress awareness to your tools:

```python
from lunvex_code.tools.progress_decorators import ProgressAwareMixin
from lunvex_code.tools.base import Tool

class MyTool(Tool, ProgressAwareMixin):
    @with_progress("My operation")
    def execute(self, *args, **kwargs):
        self._update_progress(0.3, "Starting...")
        # Your code
        self._update_progress(0.7, "Processing...")
        # More code
        self._update_progress(1.0, "Complete!")
```

### Manual Progress Control

```python
from lunvex_code.progress import get_progress_manager

manager = get_progress_manager()

# Start a spinner
with manager.spinner("Working..."):
    # Do work
    manager.update(0.5, "Halfway there")
    # More work

# Or control manually
spinner = manager.create_spinner()
spinner.start("Processing")
spinner.update(0.3, "Step 1")
spinner.update(0.6, "Step 2")
spinner.stop("✓ Complete")
```

## Performance Considerations

### Overhead
Progress indicators add minimal overhead:
- Spinner: ~0.1ms per update
- Progress bar: ~0.2ms per update
- Multi-progress: ~0.3ms per update per task

### When to Use
- **Use progress indicators for**: File I/O, network operations, large searches, batch processing
- **Skip progress indicators for**: Very fast operations (<100ms), CPU-bound loops, real-time updates

### Best Practices
1. **Update frequency**: Update progress every 100ms or after significant work
2. **Meaningful messages**: Use descriptive messages that help users understand progress
3. **Progress estimation**: Provide accurate totals when possible
4. **Error handling**: Show error states clearly
5. **Cleanup**: Always stop progress indicators, even on errors

## Tool-Specific Progress

### File Tools
- **Large files**: Show progress for files >1MB
- **Multiple files**: Show progress per file in batch operations
- **Cache operations**: Indicate cache hits/misses

### Search Tools
- **File count**: Show number of files found/scanned
- **Match count**: Show number of matches found
- **Progress estimation**: Estimate based on file system traversal

### Git Tools
- **Command execution**: Show progress during Git operations
- **Output processing**: Show progress while parsing Git output
- **Network operations**: Show progress for push/pull operations

## Custom Progress Indicators

### Creating Custom Indicators

```python
from lunvex_code.progress import BaseProgressIndicator

class CustomProgress(BaseProgressIndicator):
    def start(self, message=""):
        self.console.print(f"[blue]▶[/] Starting: {message}")
    
    def update(self, progress, message=""):
        bar = "█" * int(progress * 20)
        space = " " * (20 - len(bar))
        self.console.print(f"[green]{bar}{space}[/] {int(progress*100)}% {message}")
    
    def stop(self, message="", success=True):
        icon = "✓" if success else "✗"
        color = "green" if success else "red"
        self.console.print(f"[{color}]{icon}[/] {message}")
```

### Integration with Existing Systems

```python
# Wrap existing functions
from functools import wraps
from lunvex_code.progress import spinner

def with_progress(message):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with spinner(message):
                return func(*args, **kwargs)
        return wrapper
    return decorator

@with_progress("Processing")
def existing_function():
    # Your existing code
    pass
```

## Troubleshooting

### Common Issues

1. **Progress not showing**
   - Check `show_progress` configuration
   - Ensure operation takes >100ms
   - Verify console supports rich output

2. **Progress flickering**
   - Reduce `refresh_per_second`
   - Use `transient=False` for debugging
   - Check for rapid progress updates

3. **Performance issues**
   - Reduce update frequency
   - Batch progress updates
   - Disable progress for very fast operations

4. **Progress not stopping**
   - Ensure `stop()` is called
   - Use context managers for automatic cleanup
   - Handle exceptions properly

### Debugging

```python
from lunvex_code.progress import get_progress_manager

manager = get_progress_manager()
current = manager.get_current()
if current:
    print(f"Current progress: {current.elapsed_time():.2f}s")
```

## See Also

- [Rich Documentation](https://rich.readthedocs.io/) - Underlying library for progress indicators
- [File Tools](docs/FILE_TOOLS.md) - File operations with progress
- [Search Tools](docs/SEARCH_TOOLS.md) - Search operations with progress
- [CLI Reference](../README.md) - Command-line interface
- [API Documentation](API.md) - Developer API details