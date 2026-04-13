"""Tests for async system components."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from lunvex_code.tools.async_file_tools import AsyncReadFileTool, AsyncWriteFileTool, AsyncEditFileTool
from lunvex_code.tools.async_search_tools import AsyncGlobTool, AsyncGrepTool
from lunvex_code.tools.async_bash_tool import AsyncBashTool
from lunvex_code.tools.async_web_tools import AsyncFetchURLTool


@pytest.mark.asyncio
async def test_async_read_file_tool():
    """Test async read file tool."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3\n")
        temp_file = f.name
    
    try:
        tool = AsyncReadFileTool()
        result = await tool.execute(path=temp_file)
        
        assert result.success
        assert "Contents of" in result.output
        assert "Line 1" in result.output
        assert "Line 2" in result.output
        assert "Line 3" in result.output
    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_async_write_file_tool():
    """Test async write file tool."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = Path(tmpdir) / "test.txt"
        
        tool = AsyncWriteFileTool()
        result = await tool.execute(path=str(temp_file), content="Test content\nSecond line")
        
        assert result.success
        assert "Successfully wrote" in result.output
        assert temp_file.exists()
        
        # Verify content
        content = temp_file.read_text()
        assert content == "Test content\nSecond line"


@pytest.mark.asyncio
async def test_async_edit_file_tool():
    """Test async edit file tool."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Original line 1\nOriginal line 2\nOriginal line 3\n")
        temp_file = f.name
    
    try:
        tool = AsyncEditFileTool()
        result = await tool.execute(
            path=temp_file,
            old_str="Original line 2",
            new_str="Modified line 2"
        )
        
        assert result.success
        assert "Successfully edited" in result.output
        
        # Verify content
        with open(temp_file, 'r') as f:
            content = f.read()
        
        assert "Modified line 2" in content
        assert "Original line 1" in content
        assert "Original line 3" in content
        assert "Original line 2" not in content
    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_async_glob_tool():
    """Test async glob tool."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test files
        (tmpdir_path / "test1.txt").write_text("Content 1")
        (tmpdir_path / "test2.py").write_text("Content 2")
        (tmpdir_path / "subdir").mkdir()
        (tmpdir_path / "subdir" / "test3.txt").write_text("Content 3")
        
        tool = AsyncGlobTool()
        
        # Test glob all files
        result = await tool.execute(pattern="**/*", path=tmpdir)
        assert result.success
        assert "Found" in result.output
        assert "test1.txt" in result.output
        assert "test2.py" in result.output
        
        # Test glob specific pattern
        result = await tool.execute(pattern="*.txt", path=tmpdir)
        assert result.success
        assert "test1.txt" in result.output
        assert "test2.py" not in result.output  # Should not match .py files


@pytest.mark.asyncio
async def test_async_grep_tool():
    """Test async grep tool."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test files
        (tmpdir_path / "file1.txt").write_text("Hello world\nThis is a test\nGoodbye world")
        (tmpdir_path / "file2.txt").write_text("Another test file\nWith different content")
        
        tool = AsyncGrepTool()
        
        # Test grep for "test"
        result = await tool.execute(pattern="test", path=tmpdir)
        assert result.success
        assert "Found" in result.output
        assert "file1.txt" in result.output
        assert "file2.txt" in result.output
        
        # Test case-insensitive grep
        result = await tool.execute(pattern="TEST", path=tmpdir, ignore_case=True)
        assert result.success
        assert "Found" in result.output


@pytest.mark.asyncio
async def test_async_bash_tool():
    """Test async bash tool."""
    tool = AsyncBashTool()
    
    # Test simple command
    result = await tool.execute(command="echo 'Hello, world!'")
    assert result.success
    assert "Hello, world!" in result.output
    
    # Test command with error
    result = await tool.execute(command="ls /nonexistent/directory")
    assert not result.success
    assert "Command exited with code" in result.error or "No such file" in result.output


@pytest.mark.asyncio
async def test_async_bash_tool_timeout():
    """Test async bash tool timeout."""
    tool = AsyncBashTool()
    
    # Test command that would timeout
    result = await tool.execute(command="sleep 2", timeout=1)
    assert not result.success
    assert "timed out" in result.error.lower()


@pytest.mark.asyncio
async def test_async_bash_tool_blocked_commands():
    """Test async bash tool blocked commands."""
    tool = AsyncBashTool()
    
    # Test blocked command
    result = await tool.execute(command="rm -rf /")
    assert not result.success
    assert "blocked for safety" in result.error.lower()


@pytest.mark.asyncio
async def test_async_tools_parallel_execution():
    """Test that async tools can execute in parallel."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create multiple files
        files = []
        for i in range(5):
            file_path = tmpdir_path / f"file{i}.txt"
            file_path.write_text(f"Content of file {i}\n" * 10)
            files.append(str(file_path))
        
        # Create tasks for reading all files in parallel
        tool = AsyncReadFileTool()
        tasks = [tool.execute(path=file) for file in files]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        assert len(results) == 5
        for result in results:
            assert result.success
            assert "Contents of" in result.output


@pytest.mark.asyncio
async def test_async_grep_parallel_search():
    """Test parallel search with async grep tool."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create many test files
        for i in range(20):
            (tmpdir_path / f"file{i}.txt").write_text(f"This is file {i}\nSearch term here\nMore content")
        
        tool = AsyncGrepTool()
        
        # Search in all files (should use parallel processing)
        result = await tool.execute(
            pattern="Search term",
            path=tmpdir,
            include="*.txt",
            limit=100
        )
        
        assert result.success
        assert "Found" in result.output
        # Should find matches in all 20 files
        assert "file0.txt" in result.output
        assert "file19.txt" in result.output


def test_sync_and_async_tool_compatibility():
    """Test that sync and async tools have compatible interfaces."""
    from lunvex_code.tools.file_tools import ReadFileTool
    from lunvex_code.tools.async_file_tools import AsyncReadFileTool
    
    # Check that both have the same schema
    sync_tool = ReadFileTool()
    async_tool = AsyncReadFileTool()
    
    assert sync_tool.name == async_tool.name
    assert sync_tool.description == async_tool.description
    assert sync_tool.permission_level == async_tool.permission_level
    
    # Check parameters
    assert set(sync_tool.parameters.keys()) == set(async_tool.parameters.keys())
    
    # Check schema generation
    sync_schema = sync_tool.get_schema()
    async_schema = async_tool.get_schema()
    
    assert sync_schema["function"]["name"] == async_schema["function"]["name"]
    assert sync_schema["function"]["description"] == async_schema["function"]["description"]


if __name__ == "__main__":
    # Run tests
    import sys
    
    async def run_all_tests():
        """Run all async tests."""
        tests = [
            test_async_read_file_tool,
            test_async_write_file_tool,
            test_async_edit_file_tool,
            test_async_glob_tool,
            test_async_grep_tool,
            test_async_bash_tool,
            test_async_bash_tool_timeout,
            test_async_bash_tool_blocked_commands,
            test_async_tools_parallel_execution,
            test_async_grep_parallel_search,
            test_sync_and_async_tool_compatibility,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            print(f"\n{'='*60}")
            print(f"Running: {test.__name__}")
            print('='*60)
            
            try:
                if test.__name__.startswith('test_async'):
                    await test()
                else:
                    test()
                
                print(f"✅ {test.__name__} PASSED")
                passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} FAILED: {e}")
                import traceback
                traceback.print_exc()
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {passed} passed, {failed} failed")
        print('='*60)
        
        return failed == 0
    
    # Run async tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)