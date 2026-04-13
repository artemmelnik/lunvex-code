"""Tests for compatibility between sync and async components."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from lunvex_code.tools.file_tools import ReadFileTool, WriteFileTool, EditFileTool
from lunvex_code.tools.search_tools import GlobTool, GrepTool
from lunvex_code.tools.bash_tool import BashTool
from lunvex_code.tools.web_tools import FetchURLTool

from lunvex_code.tools.async_file_tools import AsyncReadFileTool, AsyncWriteFileTool, AsyncEditFileTool
from lunvex_code.tools.async_search_tools import AsyncGlobTool, AsyncGrepTool
from lunvex_code.tools.async_bash_tool import AsyncBashTool
from lunvex_code.tools.async_web_tools import AsyncFetchURLTool


def test_tool_schema_compatibility():
    """Test that sync and async tools have identical schemas."""
    # Test file tools
    sync_read = ReadFileTool()
    async_read = AsyncReadFileTool()
    
    sync_write = WriteFileTool()
    async_write = AsyncWriteFileTool()
    
    sync_edit = EditFileTool()
    async_edit = AsyncEditFileTool()
    
    # Test search tools
    sync_glob = GlobTool()
    async_glob = AsyncGlobTool()
    
    sync_grep = GrepTool()
    async_grep = AsyncGrepTool()
    
    # Test bash tool
    sync_bash = BashTool()
    async_bash = AsyncBashTool()
    
    # Test web tools
    sync_fetch = FetchURLTool()
    async_fetch = AsyncFetchURLTool()
    
    # Check all tool pairs
    tool_pairs = [
        (sync_read, async_read),
        (sync_write, async_write),
        (sync_edit, async_edit),
        (sync_glob, async_glob),
        (sync_grep, async_grep),
        (sync_bash, async_bash),
        (sync_fetch, async_fetch),
    ]
    
    for sync_tool, async_tool in tool_pairs:
        # Basic properties
        assert sync_tool.name == async_tool.name
        assert sync_tool.description == async_tool.description
        assert sync_tool.permission_level == async_tool.permission_level
        
        # Parameters
        assert set(sync_tool.parameters.keys()) == set(async_tool.parameters.keys())
        
        # Schema
        sync_schema = sync_tool.get_schema()
        async_schema = async_tool.get_schema()
        
        assert sync_schema["function"]["name"] == async_schema["function"]["name"]
        assert sync_schema["function"]["description"] == async_schema["function"]["description"]
        
        # Check parameters in schema
        sync_params = sync_schema["function"]["parameters"]["properties"]
        async_params = async_schema["function"]["parameters"]["properties"]
        
        assert set(sync_params.keys()) == set(async_params.keys())
        
        # Check required parameters
        sync_required = set(sync_schema["function"]["parameters"].get("required", []))
        async_required = set(async_schema["function"]["parameters"].get("required", []))
        
        assert sync_required == async_required


@pytest.mark.asyncio
async def test_sync_async_equivalent_results():
    """Test that sync and async tools produce equivalent results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test files
        test_file = tmpdir_path / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\nSearch term\nLine 5")
        
        # Create another file for glob test
        (tmpdir_path / "test.py").write_text("print('hello')")
        (tmpdir_path / "subdir").mkdir()
        (tmpdir_path / "subdir" / "nested.txt").write_text("nested content")
        
        # Test ReadFileTool
        sync_read = ReadFileTool()
        async_read = AsyncReadFileTool()
        
        sync_result = sync_read.execute(path=str(test_file))
        async_result = await async_read.execute(path=str(test_file))
        
        assert sync_result.success == async_result.success
        assert "Line 1" in sync_result.output
        assert "Line 1" in async_result.output
        
        # Test WriteFileTool
        sync_write = WriteFileTool()
        async_write = AsyncWriteFileTool()
        
        new_file = tmpdir_path / "new.txt"
        sync_write_result = sync_write.execute(path=str(new_file), content="Sync write")
        async_write_result = await async_write.execute(path=str(new_file.with_suffix('.async.txt')), 
                                                      content="Async write")
        
        assert sync_write_result.success == async_write_result.success
        assert (tmpdir_path / "new.txt").read_text() == "Sync write"
        assert (tmpdir_path / "new.async.txt").read_text() == "Async write"
        
        # Test EditFileTool
        sync_edit = EditFileTool()
        async_edit = AsyncEditFileTool()
        
        edit_file = tmpdir_path / "edit.txt"
        edit_file.write_text("Original text to edit")
        
        sync_edit_result = sync_edit.execute(
            path=str(edit_file),
            old_str="Original text",
            new_str="Modified text"
        )
        
        async_edit_file = tmpdir_path / "edit_async.txt"
        async_edit_file.write_text("Original text to edit")
        
        async_edit_result = await async_edit.execute(
            path=str(async_edit_file),
            old_str="Original text",
            new_str="Modified text"
        )
        
        assert sync_edit_result.success == async_edit_result.success
        assert "Modified text" in edit_file.read_text()
        assert "Modified text" in async_edit_file.read_text()
        
        # Test GlobTool
        sync_glob = GlobTool()
        async_glob = AsyncGlobTool()
        
        sync_glob_result = sync_glob.execute(pattern="**/*.txt", path=str(tmpdir_path))
        async_glob_result = await async_glob.execute(pattern="**/*.txt", path=str(tmpdir_path))
        
        assert sync_glob_result.success == async_glob_result.success
        # Both should find the same files
        for filename in ["test.txt", "new.txt", "new.async.txt", "edit.txt", "edit_async.txt", "subdir/nested.txt"]:
            assert filename in sync_glob_result.output
            assert filename in async_glob_result.output
        
        # Test GrepTool
        sync_grep = GrepTool()
        async_grep = AsyncGrepTool()
        
        sync_grep_result = sync_grep.execute(pattern="Search term", path=str(tmpdir_path))
        async_grep_result = await async_grep.execute(pattern="Search term", path=str(tmpdir_path))
        
        assert sync_grep_result.success == async_grep_result.success
        assert "test.txt" in sync_grep_result.output
        assert "test.txt" in async_grep_result.output
        
        # Test BashTool (simple command)
        sync_bash = BashTool()
        async_bash = AsyncBashTool()
        
        sync_bash_result = sync_bash.execute(command="echo 'Hello'")
        async_bash_result = await async_bash.execute(command="echo 'Hello'")
        
        assert sync_bash_result.success == async_bash_result.success
        assert "Hello" in sync_bash_result.output
        assert "Hello" in async_bash_result.output


@pytest.mark.asyncio
async def test_mixed_sync_async_workflow():
    """Test workflow using both sync and async tools together."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Use sync tool to create files
        sync_write = WriteFileTool()
        
        files_to_create = ["file1.txt", "file2.txt", "file3.txt"]
        for filename in files_to_create:
            sync_write.execute(
                path=str(tmpdir_path / filename),
                content=f"Content of {filename}\nWith some text to search"
            )
        
        # Use async tool to search in all files concurrently
        async_grep = AsyncGrepTool()
        
        # Search for text that appears in all files
        result = await async_grep.execute(
            pattern="text to search",
            path=str(tmpdir_path),
            include="*.txt"
        )
        
        assert result.success
        for filename in files_to_create:
            assert filename in result.output
        
        # Use sync tool to verify files exist
        sync_glob = GlobTool()
        glob_result = sync_glob.execute(pattern="*.txt", path=str(tmpdir_path))
        
        assert glob_result.success
        for filename in files_to_create:
            assert filename in glob_result.output
        
        # Use async tool to read all files in parallel
        async_read = AsyncReadFileTool()
        
        tasks = [async_read.execute(path=str(tmpdir_path / filename)) 
                for filename in files_to_create]
        read_results = await asyncio.gather(*tasks)
        
        # Verify all reads succeeded
        for i, result in enumerate(read_results):
            assert result.success
            assert files_to_create[i] in result.output
            assert "Content of" in result.output


def test_tool_registry_compatibility():
    """Test that sync and async tools can be used in the same registry."""
    from lunvex_code.tools.base import ToolRegistry
    
    registry = ToolRegistry()
    
    # Register both sync and async tools
    from lunvex_code.tools.file_tools import ReadFileTool
    from lunvex_code.tools.async_file_tools import AsyncReadFileTool
    
    # They should have the same name, so we need to handle this carefully
    # In practice, the registry would use one or the other, not both
    sync_tool = ReadFileTool()
    
    # Check that the tool can be registered
    registry.register(sync_tool)
    
    assert "read_file" in registry._tools
    assert registry._tools["read_file"].name == "read_file"
    
    # The async version would have the same name
    async_tool = AsyncReadFileTool()
    assert async_tool.name == "read_file"  # Same name as sync version


@pytest.mark.asyncio
async def test_async_wrapper_for_sync_tools():
    """Test that sync tools can be wrapped for async use."""
    from lunvex_code.tools.file_tools import ReadFileTool
    import asyncio
    
    # Create a sync tool
    sync_tool = ReadFileTool()
    
    # Wrap it for async use
    async def async_wrapped_execute(**kwargs):
        # Run sync tool in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: sync_tool.execute(**kwargs))
    
    # Test the wrapped version
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content for async wrapper\n")
        temp_file = f.name
    
    try:
        result = await async_wrapped_execute(path=temp_file)
        assert result.success
        assert "Test content" in result.output
    finally:
        Path(temp_file).unlink()


if __name__ == "__main__":
    # Run tests
    import sys
    
    async def run_all_tests():
        """Run all compatibility tests."""
        tests = [
            # Sync test
            test_tool_schema_compatibility,
            # Async tests
            test_sync_async_equivalent_results,
            test_mixed_sync_async_workflow,
            test_async_wrapper_for_sync_tools,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            print(f"\n{'='*60}")
            print(f"Running: {test.__name__}")
            print('='*60)
            
            try:
                if test.__name__.startswith('test_async') or 'async' in test.__name__:
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
        
        # Run sync test separately
        print(f"\n{'='*60}")
        print(f"Running: test_tool_registry_compatibility")
        print('='*60)
        try:
            test_tool_registry_compatibility()
            print(f"✅ test_tool_registry_compatibility PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ test_tool_registry_compatibility FAILED: {e}")
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