"""Tests for async Git tools."""

import asyncio
import tempfile
from pathlib import Path
import subprocess

import pytest

# Note: Git tools are sync, but we test them in async context


@pytest.mark.asyncio
async def test_git_status_async_context():
    """Test git_status tool in async context."""
    import os
    original_cwd = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], 
                      cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], 
                      cwd=tmpdir, capture_output=True)
        
        # Create a file
        (tmpdir_path / "test.txt").write_text("Test content")
        
        # Change to temp directory
        os.chdir(tmpdir)
        
        try:
            # Import and test git_status tool
            from lunvex_code.tools.git_tools import GitStatusTool
            git_status = GitStatusTool()
            
            # Run in async context (tool is sync, but we can await it)
            result = await asyncio.to_thread(lambda: git_status.execute())
            
            assert result.success
            assert "test.txt" in result.output or "untracked" in result.output.lower()
        finally:
            # Restore original directory
            os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_git_diff_async_context():
    """Test git_diff tool in async context."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"],
                      cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"],
                      cwd=tmpdir, capture_output=True)
        
        # Create and commit a file
        (tmpdir_path / "test.txt").write_text("Initial content")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"],
                      cwd=tmpdir, capture_output=True)
        
        # Modify the file
        (tmpdir_path / "test.txt").write_text("Modified content")
        
        # Import and test git_diff tool
        from lunvex_code.tools.git_tools import GitDiffTool
        git_diff = GitDiffTool()
        
        # Run in async context
        result = await asyncio.to_thread(lambda: git_diff.execute(path=tmpdir))
        
        assert result.success
        # Should show diff
        assert "diff" in result.output.lower() or "modified" in result.output.lower()


@pytest.mark.asyncio
async def test_git_log_async_context():
    """Test git_log tool in async context."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"],
                      cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"],
                      cwd=tmpdir, capture_output=True)
        
        # Create and commit files
        (tmpdir_path / "file1.txt").write_text("File 1")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add file 1"],
                      cwd=tmpdir, capture_output=True)
        
        (tmpdir_path / "file2.txt").write_text("File 2")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add file 2"],
                      cwd=tmpdir, capture_output=True)
        
        # Import and test git_log tool
        from lunvex_code.tools.git_tools import GitLogTool
        git_log = GitLogTool()
        
        # Run in async context
        result = await asyncio.to_thread(lambda: git_log.execute(path=tmpdir, max_count=2))
        
        assert result.success
        assert "commit" in result.output.lower()
        assert "Add file 1" in result.output or "Add file 2" in result.output


@pytest.mark.asyncio
async def test_git_tools_concurrent():
    """Test concurrent execution of git tools."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"],
                      cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"],
                      cwd=tmpdir, capture_output=True)
        
        # Create some files
        for i in range(3):
            (tmpdir_path / f"file{i}.txt").write_text(f"Content {i}")
        
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial files"],
                      cwd=tmpdir, capture_output=True)
        
        # Import git tools
        from lunvex_code.tools.git_tools import GitStatusTool, GitLogTool
        git_status = GitStatusTool()
        git_log = GitLogTool()
        
        # Run tools concurrently
        tasks = [
            asyncio.to_thread(lambda: git_status.execute(path=tmpdir)),
            asyncio.to_thread(lambda: git_log.execute(path=tmpdir, max_count=1)),
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify both succeeded
        for result in results:
            assert result.success
        
        # Check git_status
        assert "file0.txt" in results[0].output or "nothing to commit" in results[0].output.lower()
        
        # Check git_log
        assert "commit" in results[1].output.lower()
        assert "Initial files" in results[1].output


@pytest.mark.asyncio
async def test_git_tool_error_handling():
    """Test git tool error handling in async context."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Not a git repo
        
        from lunvex_code.tools.git_tools import GitStatusTool
        git_status = GitStatusTool()
        
        # Run in async context - should handle error
        result = await asyncio.to_thread(lambda: git_status.execute(path=tmpdir))
        
        # May fail or succeed with empty repo message
        if not result.success:
            assert "error" in result.error.lower() or "not a git" in result.error.lower()
        else:
            # Some git versions might succeed with empty repo message
            assert "not a git repository" in result.output.lower() or "fatal" not in result.output.lower()


@pytest.mark.asyncio
async def test_git_show_async_context():
    """Test git_show tool in async context."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"],
                      cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"],
                      cwd=tmpdir, capture_output=True)
        
        # Create and commit a file with specific content
        (tmpdir_path / "special.txt").write_text("Special content for git show")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        result = subprocess.run(["git", "commit", "-m", "Special commit"],
                               cwd=tmpdir, capture_output=True, text=True)
        
        # Get commit hash
        commit_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=tmpdir, capture_output=True, text=True
        ).stdout.strip()
        
        # Import and test git_show tool
        from lunvex_code.tools.git_tools import GitShowTool
        git_show = GitShowTool()
        
        # Run in async context
        result = await asyncio.to_thread(lambda: git_show.execute(object=commit_hash[:8], path=tmpdir))
        
        assert result.success
        assert "Special content" in result.output or "special.txt" in result.output


if __name__ == "__main__":
    # Run tests
    import sys
    
    async def run_all_tests():
        """Run all async git tool tests."""
        tests = [
            test_git_status_async_context,
            test_git_diff_async_context,
            test_git_log_async_context,
            test_git_tools_concurrent,
            test_git_tool_error_handling,
            test_git_show_async_context,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            print(f"\n{'='*60}")
            print(f"Running: {test.__name__}")
            print('='*60)
            
            try:
                await test()
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