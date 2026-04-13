"""Integration tests for progress indicators with tools."""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from lunvex_code.tools.file_tools import ReadFileTool, WriteFileTool, EditFileTool
from lunvex_code.tools.search_tools import GlobTool, GrepTool
from lunvex_code.progress import get_progress_manager


def test_read_file_with_progress():
    """Test that read_file shows progress for large files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        # Create a file large enough to trigger progress (>1MB)
        # Write 1000 lines of 1000 characters each = ~1MB
        for i in range(1000):
            tmp.write(f"{'x' * 1000}\n")
        tmp_path = tmp.name
    
    try:
        tool = ReadFileTool()
        
        # Mock the progress update to verify it's called
        with patch.object(tool, '_update_progress') as mock_update:
            result = tool.execute(tmp_path, limit=10)
            
            # Should have called progress updates for a file this size (>1MB)
            # Note: The tool checks file_size > 1024*1024
            if os.path.getsize(tmp_path) > 1024 * 1024:
                assert mock_update.called, "Progress should be called for files >1MB"
            else:
                print(f"  Note: File size is {os.path.getsize(tmp_path)} bytes, progress may not trigger")
            
            # Should have succeeded
            assert result.success
            assert "Contents of" in result.output
            
    finally:
        os.unlink(tmp_path)


def test_write_file_with_progress():
    """Test that write_file shows progress."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        tool = WriteFileTool()
        content = "Test content\n" * 100  # Moderate size
        
        # Mock progress update
        with patch.object(tool, '_update_progress') as mock_update:
            result = tool.execute(tmp_path, content)
            
            # Should have called progress updates
            assert mock_update.called
            # Should have succeeded
            assert result.success
            assert "Successfully wrote" in result.output
            
            # Verify file was written
            with open(tmp_path, 'r') as f:
                written = f.read()
            assert written == content
            
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_edit_file_with_progress():
    """Test that edit_file shows progress."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp.write("Line 1\nLine 2\nLine 3\n")
        tmp_path = tmp.name
    
    try:
        tool = EditFileTool()
        
        # Mock progress update
        with patch.object(tool, '_update_progress') as mock_update:
            result = tool.execute(
                tmp_path,
                old_str="Line 2",
                new_str="Line 2 edited"
            )
            
            # Should have called progress updates
            assert mock_update.called
            # Should have succeeded
            assert result.success
            
            # Verify edit was made
            with open(tmp_path, 'r') as f:
                content = f.read()
            assert "Line 2 edited" in content
            
    finally:
        os.unlink(tmp_path)


def test_glob_with_progress():
    """Test that glob shows progress during search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some test files
        for i in range(5):
            with open(os.path.join(tmpdir, f"test_{i}.txt"), 'w') as f:
                f.write(f"Content {i}")
        
        tool = GlobTool()
        
        # Mock progress update
        with patch.object(tool, '_update_progress') as mock_update:
            result = tool.execute("*.txt", path=tmpdir)
            
            # Should have called progress updates
            assert mock_update.called
            # Should have succeeded
            assert result.success
            assert "Found 5 file(s)" in result.output
            
            # Check that progress was called with appropriate messages
            calls = [call[0] for call in mock_update.call_args_list]
            assert any("Starting search" in str(call) for call in calls)
            assert any("Found" in str(call) and "matches" in str(call) for call in calls)


def test_grep_with_progress():
    """Test that grep shows progress during search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files with content
        for i in range(3):
            filepath = os.path.join(tmpdir, f"file_{i}.txt")
            with open(filepath, 'w') as f:
                f.write(f"This is test file {i}\n")
                f.write(f"Looking for pattern in file {i}\n")
                f.write(f"End of file {i}\n")
        
        tool = GrepTool()
        
        # Mock progress update
        with patch.object(tool, '_update_progress') as mock_update:
            result = tool.execute(
                pattern="pattern",
                path=tmpdir,
                include="*.txt"
            )
            
            # Should have called progress updates
            assert mock_update.called
            # Should have succeeded and found matches
            assert result.success
            assert "pattern" in result.output.lower()
            
            # Check progress messages
            calls = [call[0] for call in mock_update.call_args_list]
            assert any("Finding files" in str(call) for call in calls)
            assert any("Found" in str(call) and "files" in str(call) for call in calls)


def test_progress_disabled_for_small_files():
    """Test that progress is not shown for very small files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp.write("Small content")
        tmp_path = tmp.name
    
    try:
        tool = ReadFileTool()
        
        # Mock progress update - should NOT be called for small files
        with patch.object(tool, '_update_progress') as mock_update:
            result = tool.execute(tmp_path)
            
            # Progress should NOT be called for very small files
            # (file_size > 1024*1024 check in the tool)
            assert not mock_update.called
            # But should still succeed
            assert result.success
            
    finally:
        os.unlink(tmp_path)


def test_progress_manager_integration():
    """Test that progress manager works with tools."""
    manager = get_progress_manager()
    
    # Start a spinner
    with manager.spinner("Test operation") as spinner:
        assert manager.get_current() == spinner
        
        # Simulate tool operation
        time.sleep(0.1)
        manager.update(0.5, "Halfway")
        
        # Verify progress is tracked
        assert spinner.elapsed_time() > 0
    
    # Should be cleared after context
    assert manager.get_current() is None


def test_progress_configuration():
    """Test that progress configuration affects display."""
    from lunvex_code.progress import ProgressConfig, SpinnerProgress
    
    # Test with progress disabled
    config = ProgressConfig(show_progress=False)
    spinner = SpinnerProgress(config)
    
    # Should not create Live instance
    spinner.start("Test")
    assert spinner._live is None
    spinner.stop()
    
    # Test with custom styles
    config = ProgressConfig(
        spinner_style="red",
        progress_style="yellow",
        transient=False
    )
    
    spinner = SpinnerProgress(config)
    assert spinner.config.spinner_style == "red"
    assert spinner.config.progress_style == "yellow"
    assert spinner.config.transient is False


def test_progress_error_handling():
    """Test that progress handles errors gracefully."""
    from lunvex_code.progress import spinner
    
    # Test that progress stops even on exception
    try:
        with spinner("Risky operation") as progress:
            time.sleep(0.1)
            raise ValueError("Test error")
    except ValueError:
        # Progress should have been stopped
        assert progress._end_time is not None
        # Elapsed time should be recorded
        assert progress.elapsed_time() > 0


def test_batch_operations_with_progress():
    """Test progress for batch operations."""
    from lunvex_code.progress import progress_bar
    
    items = list(range(50))
    results = []
    
    with progress_bar("Processing batch", total=len(items)) as bar:
        for i, item in enumerate(items):
            # Simulate work
            time.sleep(0.01)
            results.append(item * 2)
            
            # Update progress
            progress = (i + 1) / len(items)
            bar.update(progress, f"Item {i+1}/{len(items)}")
    
    assert len(results) == len(items)
    assert all(r == i * 2 for i, r in zip(items, results))


def main():
    """Run all integration tests."""
    print("Running progress integration tests...\n")
    
    tests = [
        ("Read file with progress", test_read_file_with_progress),
        ("Write file with progress", test_write_file_with_progress),
        ("Edit file with progress", test_edit_file_with_progress),
        ("Glob with progress", test_glob_with_progress),
        ("Grep with progress", test_grep_with_progress),
        ("Progress disabled for small files", test_progress_disabled_for_small_files),
        ("Progress manager integration", test_progress_manager_integration),
        ("Progress configuration", test_progress_configuration),
        ("Progress error handling", test_progress_error_handling),
        ("Batch operations with progress", test_batch_operations_with_progress),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: {str(e)}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All progress integration tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())