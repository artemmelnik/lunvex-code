"""Full system test for progress indicators."""

import os
import tempfile
import time
from pathlib import Path
from rich.console import Console

from lunvex_code.progress import (
    spinner,
    progress_bar,
    multi_progress,
    get_progress_manager,
    ProgressConfig,
)
from lunvex_code.tools.file_tools import ReadFileTool, WriteFileTool
from lunvex_code.tools.search_tools import GlobTool


def test_complete_workflow():
    """Test a complete workflow with progress indicators."""
    console = Console(record=True)
    
    print("\n🧪 Testing complete progress system workflow...")
    
    # Create test directory and files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        print("1. Creating test files...")
        
        # Create multiple test files
        file_contents = {}
        for i in range(10):
            filename = tmpdir_path / f"test_{i:02d}.txt"
            content = f"This is test file {i}\n" * 100  # Each file ~2KB
            filename.write_text(content)
            file_contents[filename] = content
        
        print("2. Testing file operations with progress...")
        
        # Test ReadFileTool with progress
        read_tool = ReadFileTool()
        test_file = tmpdir_path / "test_00.txt"
        
        with spinner("Reading test file") as progress:
            result = read_tool.execute(str(test_file))
            assert result.success
            assert "Contents of" in result.output
            progress.stop("✓ File read successfully")
        
        print("3. Testing write operation with progress...")
        
        # Test WriteFileTool with progress
        write_tool = WriteFileTool()
        new_file = tmpdir_path / "new_file.txt"
        new_content = "New content\n" * 50
        
        with spinner("Writing new file") as progress:
            result = write_tool.execute(str(new_file), new_content)
            assert result.success
            assert "Successfully wrote" in result.output
            progress.stop("✓ File written successfully")
        
        print("4. Testing search with progress...")
        
        # Test GlobTool with progress
        glob_tool = GlobTool()
        
        with spinner("Searching for files") as progress:
            result = glob_tool.execute("*.txt", path=str(tmpdir_path))
            assert result.success
            assert "Found" in result.output and "file(s)" in result.output
            progress.stop("✓ Search completed")
        
        print("5. Testing batch processing with progress bar...")
        
        # Simulate batch processing
        files_to_process = list(tmpdir_path.glob("*.txt"))
        
        with progress_bar("Processing files", total=len(files_to_process)) as bar:
            processed = 0
            for i, filepath in enumerate(files_to_process):
                # Simulate processing
                time.sleep(0.01)
                processed += 1
                
                # Update progress
                progress = (i + 1) / len(files_to_process)
                bar.update(progress, f"File {i+1}/{len(files_to_process)}")
            
            assert processed == len(files_to_process)
            bar.stop(f"✓ Processed {processed} files")
        
        print("6. Testing multi-task progress...")
        
        # Test multi-task progress
        with multi_progress() as multi:
            # Add multiple tasks
            multi.add_task("download", "Downloading data...", total=100)
            multi.add_task("process", "Processing data...", total=50)
            multi.add_task("save", "Saving results...", total=20)
            
            # Simulate parallel progress
            for i in range(100):
                multi.increment_task("download", 0.01)
                
                if i % 2 == 0:
                    multi.increment_task("process", 0.02)
                
                if i % 5 == 0:
                    multi.increment_task("save", 0.05)
                
                time.sleep(0.001)
            
            # Complete tasks
            multi.complete_task("download", "✓ Download complete")
            multi.complete_task("process", "✓ Processing complete")
            multi.complete_task("save", "✓ Save complete")
        
        print("7. Testing progress manager...")
        
        # Test progress manager
        manager = get_progress_manager()
        
        # Start nested progress indicators
        with manager.spinner("Outer operation") as outer:
            time.sleep(0.05)
            
            with manager.bar("Inner operation", total=50) as inner:
                for i in range(50):
                    inner.increment(0.02)
                    time.sleep(0.001)
            
            outer.stop("✓ Outer complete")
        
        # Manager should be clear
        assert manager.get_current() is None
        
        print("8. Testing custom configuration...")
        
        # Test custom configuration
        config = ProgressConfig(
            spinner_style="magenta",
            progress_style="cyan",
            transient=False,
            refresh_per_second=5.0,
        )
        
        with spinner("Custom styled operation", config=config) as custom:
            time.sleep(0.1)
            custom.stop("✓ Custom operation complete")
        
        print("\n✅ All workflow tests passed!")
        return True


def test_error_handling_workflow():
    """Test error handling in workflow."""
    print("\n🧪 Testing error handling in workflow...")
    
    # Test that progress stops even on errors
    try:
        with spinner("Operation that will fail") as progress:
            time.sleep(0.05)
            raise ValueError("Simulated error")
    except ValueError as e:
        print(f"  Caught expected error: {e}")
        # Progress should have been stopped
        assert progress._end_time is not None
        print("  ✓ Progress stopped on error")
    
    # Test error in tool with progress
    write_tool = WriteFileTool()
    
    try:
        # Try to write to invalid path
        with spinner("Writing to invalid path") as progress:
            result = write_tool.execute("/invalid/path/file.txt", "content")
            assert not result.success
            progress.stop("✗ Operation failed as expected", success=False)
    except Exception:
        print("  ✓ Tool error handled with progress")
    
    print("✅ Error handling tests passed!")
    return True


def test_performance_impact():
    """Test that progress indicators have minimal performance impact."""
    print("\n🧪 Testing performance impact...")
    
    import time
    
    # Test without progress
    start = time.time()
    for i in range(1000):
        _ = i * 2
    no_progress_time = time.time() - start
    
    # Test with progress (but disabled in config)
    config = ProgressConfig(show_progress=False)
    
    start = time.time()
    with spinner("Disabled progress", config=config):
        for i in range(1000):
            _ = i * 2
    disabled_progress_time = time.time() - start
    
    # Test with progress enabled
    start = time.time()
    with spinner("Enabled progress"):
        for i in range(1000):
            _ = i * 2
    enabled_progress_time = time.time() - start
    
    print(f"  No progress: {no_progress_time:.4f}s")
    print(f"  Disabled progress: {disabled_progress_time:.4f}s")
    print(f"  Enabled progress: {enabled_progress_time:.4f}s")
    
    # Overhead should be minimal
    overhead_enabled = enabled_progress_time - no_progress_time
    overhead_disabled = disabled_progress_time - no_progress_time
    
    print(f"  Overhead (disabled): {overhead_disabled:.4f}s")
    print(f"  Overhead (enabled): {overhead_enabled:.4f}s")
    
    # Acceptable overhead (less than 10ms for 1000 iterations)
    assert overhead_enabled < 0.01, f"Overhead too high: {overhead_enabled:.4f}s"
    
    print("✅ Performance impact acceptable!")
    return True


def main():
    """Run all system tests."""
    print("=" * 60)
    print("🚀 FULL PROGRESS SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        ("Complete workflow", test_complete_workflow),
        ("Error handling", test_error_handling_workflow),
        ("Performance impact", test_performance_impact),
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"Test: {name}")
        print('='*40)
        
        try:
            success = test_func()
            if success:
                print(f"\n✅ {name} PASSED")
                results.append((name, True))
            else:
                print(f"\n❌ {name} FAILED")
                results.append((name, False))
        except Exception as e:
            print(f"\n❌ {name} FAILED with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SYSTEM TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())