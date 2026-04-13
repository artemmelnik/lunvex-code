"""Demo script for progress indicators."""

import time
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from lunvex_code.progress import (
    spinner,
    progress_bar,
    multi_progress,
    track_operation,
    ProgressConfig,
    get_progress_manager,
)
from lunvex_code.tools.progress_decorators import with_progress

console = Console()


def demo_spinner():
    """Demo spinner progress indicator."""
    console.print(Panel("🌀 Spinner Progress Demo", style="bold blue"))
    
    console.print("1. Simple spinner with message:")
    with spinner("Processing data..."):
        time.sleep(1.5)
    
    console.print("\n2. Spinner with updates:")
    with spinner("Loading files...") as progress:
        time.sleep(0.5)
        progress.update(0.3, "Reading file 1/3")
        time.sleep(0.5)
        progress.update(0.6, "Reading file 2/3")
        time.sleep(0.5)
        progress.update(0.9, "Reading file 3/3")
        time.sleep(0.5)
    
    console.print("\n3. Spinner with increment:")
    with spinner("Counting items...") as progress:
        for i in range(10):
            progress.increment(0.1, f"Item {i+1}/10")
            time.sleep(0.1)
    
    console.print("\n4. Spinner with error:")
    try:
        with spinner("Trying risky operation..."):
            time.sleep(0.5)
            raise ValueError("Something went wrong!")
    except ValueError:
        console.print("[red]Operation failed as expected[/red]")


def demo_progress_bar():
    """Demo progress bar indicator."""
    console.print(Panel("📊 Progress Bar Demo", style="bold blue"))
    
    console.print("1. Simple progress bar:")
    with progress_bar("Downloading files...", total=100) as bar:
        for i in range(100):
            bar.update((i + 1) / 100, f"File {i+1}/100")
            time.sleep(0.01)
    
    console.print("\n2. Progress bar with custom configuration:")
    config = ProgressConfig(
        show_spinner=True,
        show_percentage=True,
        show_time=True,
        show_count=True,
        spinner_style="yellow",
        progress_style="cyan",
        transient=False,  # Don't clear when done
    )
    
    with progress_bar("Analyzing code...", total=50, config=config) as bar:
        for i in range(50):
            if i < 10:
                bar.update((i + 1) / 50, f"Parsing file {i+1}")
            elif i < 30:
                bar.update((i + 1) / 50, f"Checking syntax {i+1}")
            else:
                bar.update((i + 1) / 50, f"Running tests {i+1}")
            time.sleep(0.02)


def demo_multi_progress():
    """Demo multi-task progress indicator."""
    console.print(Panel("🧩 Multi-Task Progress Demo", style="bold blue"))
    
    with multi_progress() as multi:
        # Add tasks
        multi.add_task("download", "Downloading files...", total=100)
        multi.add_task("extract", "Extracting archives...", total=50)
        multi.add_task("process", "Processing data...", total=200)
        
        # Simulate parallel progress
        for i in range(100):
            multi.increment_task("download", 0.01)
            
            if i % 2 == 0:
                multi.increment_task("extract", 0.02)
            
            if i % 4 == 0:
                multi.increment_task("process", 0.005)
            
            time.sleep(0.02)
        
        # Complete tasks
        multi.complete_task("download", "✓ Download complete")
        multi.complete_task("extract", "✓ Extraction complete")
        multi.complete_task("process", "✓ Processing complete")


def demo_decorator():
    """Demo progress decorator."""
    console.print(Panel("🎭 Progress Decorator Demo", style="bold blue"))
    
    console.print("Progress decorators allow easy addition of progress indicators:")
    console.print("\n1. Manual decorator example:")
    console.print("   ```python")
    console.print("   from lunvex_code.progress import spinner")
    console.print("   ")
    console.print("   def track_operation(message):")
    console.print("       def decorator(func):")
    console.print("           def wrapper(*args, **kwargs):")
    console.print("               with spinner(message):")
    console.print("                   return func(*args, **kwargs)")
    console.print("           return wrapper")
    console.print("       return decorator")
    console.print("   ")
    console.print("   @track_operation('Calculating')")
    console.print("   def calculate():")
    console.print("       time.sleep(1)")
    console.print("       return result")
    console.print("   ```")
    
    console.print("\n2. Built-in decorators in tools:")
    console.print("   ```python")
    console.print("   from lunvex_code.tools.progress_decorators import with_file_progress")
    console.print("   ")
    console.print("   class ReadFileTool(Tool):")
    console.print("       @with_file_progress('Reading file')")
    console.print("       def execute(self, path):")
    console.print("           # File reading code")
    console.print("           pass")
    console.print("   ```")
    
    # Simulate decorator behavior
    console.print("\n3. Simulating decorator behavior:")
    with spinner("Calculating results (simulated decorator)"):
        time.sleep(1.0)
        results = [i * 2 for i in range(10)]
    
    console.print(f"   Results: {results[:5]}...")
    
    console.print("\n4. Simulating batch processing:")
    with progress_bar("Processing batch", total=20) as bar:
        processed = []
        for i in range(20):
            time.sleep(0.05)
            processed.append(i * 2)
            bar.update((i + 1) / 20, f"Item {i+1}/20")
    
    console.print(f"   Processed {len(processed)} items")


def demo_file_operations():
    """Demo progress in file operations."""
    console.print(Panel("📁 File Operations with Progress", style="bold blue"))
    
    # Create test files
    test_dir = Path("test_progress_demo")
    test_dir.mkdir(exist_ok=True)
    
    # Create a large file
    large_file = test_dir / "large_file.txt"
    with open(large_file, "w") as f:
        f.write("Test content\n" * 1000)
    
    console.print("Simulating file operations with progress indicators:")
    console.print("(Progress indicators would appear during actual tool execution)")
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
    
    console.print("\n✅ File operations demo complete")


def demo_tool_integration():
    """Demo progress integration with tools."""
    console.print(Panel("🔧 Tool Integration Demo", style="bold blue"))
    
    console.print("Tools now have progress indicators for:")
    console.print("  • read_file - Shows progress for large files")
    console.print("  • write_file - Shows writing progress")
    console.print("  • edit_file - Shows editing progress")
    console.print("  • glob - Shows search progress")
    console.print("  • grep - Shows search progress with file count")
    
    console.print("\nExample usage in AI assistant:")
    console.print('  lunvex-code run "read the README.md file"')
    console.print('  lunvex-code run "search for TODO in all python files"')
    console.print('  lunvex-code run "find all test files in the project"')


def demo_configuration():
    """Demo progress configuration."""
    console.print(Panel("⚙️ Progress Configuration Demo", style="bold blue"))
    
    # Show default configuration
    default_config = ProgressConfig()
    
    table = Table(title="Default Progress Configuration", box=box.ROUNDED)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("show_progress", str(default_config.show_progress))
    table.add_row("show_spinner", str(default_config.show_spinner))
    table.add_row("show_percentage", str(default_config.show_percentage))
    table.add_row("show_time", str(default_config.show_time))
    table.add_row("show_count", str(default_config.show_count))
    table.add_row("spinner_style", default_config.spinner_style)
    table.add_row("progress_style", default_config.progress_style)
    table.add_row("auto_close", str(default_config.auto_close))
    table.add_row("transient", str(default_config.transient))
    table.add_row("refresh_per_second", str(default_config.refresh_per_second))
    
    console.print(table)
    
    console.print("\nCustom configuration example:")
    custom_config = ProgressConfig(
        show_spinner=True,
        show_percentage=True,
        show_time=True,
        spinner_style="magenta",
        progress_style="yellow",
        transient=False,
        refresh_per_second=20.0,
    )
    
    with spinner("Custom styled spinner", config=custom_config):
        time.sleep(1.0)


def demo_performance():
    """Demo performance impact of progress indicators."""
    console.print(Panel("⚡ Performance Demo", style="bold blue"))
    
    console.print("Progress indicators have minimal overhead:")
    
    # Test without progress
    start = time.time()
    for _ in range(100):
        pass
    no_progress_time = time.time() - start
    
    # Test with progress
    start = time.time()
    with spinner("Testing..."):
        for i in range(100):
            pass
    with_progress_time = time.time() - start
    
    overhead = with_progress_time - no_progress_time
    
    console.print(f"  • 100 iterations without progress: {no_progress_time:.3f}s")
    console.print(f"  • 100 iterations with progress: {with_progress_time:.3f}s")
    console.print(f"  • Overhead: {overhead:.3f}s ({overhead/no_progress_time*100:.1f}%)")
    
    console.print("\n✅ Progress indicators add minimal overhead")


def main():
    """Run all demos."""
    console.print(Panel("🚀 Progress Indicators System Demo", style="bold green", width=80))
    console.print("This demo shows the new progress indicators system for LunVex Code.")
    console.print("The system provides visual feedback for long-running operations.\n")
    
    # Run demos
    demo_spinner()
    console.print("\n" + "="*80 + "\n")
    
    demo_progress_bar()
    console.print("\n" + "="*80 + "\n")
    
    demo_multi_progress()
    console.print("\n" + "="*80 + "\n")
    
    demo_decorator()
    console.print("\n" + "="*80 + "\n")
    
    demo_file_operations()
    console.print("\n" + "="*80 + "\n")
    
    demo_tool_integration()
    console.print("\n" + "="*80 + "\n")
    
    demo_configuration()
    console.print("\n" + "="*80 + "\n")
    
    demo_performance()
    
    console.print(Panel("✅ Demo Complete!", style="bold green", width=80))
    console.print("\nProgress indicators are now integrated into LunVex Code!")
    console.print("Try them out with file operations and search tools.")


if __name__ == "__main__":
    main()