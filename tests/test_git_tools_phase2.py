"""Tests for Phase 2 Git tools (add, commit, push, pull)."""

from unittest.mock import Mock, patch
import pytest

from lunvex_code.tools.git_tools import (
    GitAddTool,
    GitCommitTool,
    GitPushTool,
    GitPullTool,
    GitResult,
)


class TestGitAddTool:
    """Test GitAddTool."""
    
    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitAddTool()
        assert tool.name == "git_add"
        assert tool.permission_level == "ask"
        assert "Add file contents to the index" in tool.description
    
    @patch.object(GitAddTool, '_run_git_command')
    def test_execute_basic(self, mock_run_git):
        """Test basic git add execution."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="",
            error=None,
            exit_code=0,
            command="git add file.txt"
        )
        
        tool = GitAddTool()
        result = tool.execute(paths="file.txt")
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['add', 'file.txt'])
    
    @patch.object(GitAddTool, '_run_git_command')
    def test_execute_all(self, mock_run_git):
        """Test git add with --all flag."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="",
            error=None,
            exit_code=0,
            command="git add --all"
        )
        
        tool = GitAddTool()
        result = tool.execute(paths=".", all=True)
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['add', '--all', '.'])
    
    @patch.object(GitAddTool, '_run_git_command')
    def test_execute_dry_run(self, mock_run_git):
        """Test git add with dry run."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="add 'file.txt'",
            error=None,
            exit_code=0,
            command="git add --dry-run file.txt"
        )
        
        tool = GitAddTool()
        result = tool.execute(paths="file.txt", dry_run=True)
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['add', '--dry-run', 'file.txt'])
    
    @patch.object(GitAddTool, '_run_git_command')
    def test_execute_multiple_files(self, mock_run_git):
        """Test git add with multiple files."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="",
            error=None,
            exit_code=0,
            command="git add file1.txt file2.txt"
        )
        
        tool = GitAddTool()
        result = tool.execute(paths="file1.txt file2.txt")
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['add', 'file1.txt', 'file2.txt'])


class TestGitCommitTool:
    """Test GitCommitTool."""
    
    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitCommitTool()
        assert tool.name == "git_commit"
        assert tool.permission_level == "ask"
        assert "Record changes to the repository" in tool.description
    
    @patch.object(GitCommitTool, '_run_git_command')
    def test_execute_basic(self, mock_run_git):
        """Test basic git commit execution."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="[main abc123] Test commit",
            error=None,
            exit_code=0,
            command="git commit -m 'Test commit'"
        )
        
        tool = GitCommitTool()
        result = tool.execute(message="Test commit")
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['commit', '-m', 'Test commit'])
    
    @patch.object(GitCommitTool, '_run_git_command')
    def test_execute_with_all(self, mock_run_git):
        """Test git commit with --all flag."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="[main abc123] Test commit",
            error=None,
            exit_code=0,
            command="git commit --all -m 'Test commit'"
        )
        
        tool = GitCommitTool()
        result = tool.execute(message="Test commit", all=True)
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['commit', '--all', '-m', 'Test commit'])
    
    @patch.object(GitCommitTool, '_run_git_command')
    def test_execute_amend(self, mock_run_git):
        """Test git commit with amend."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="[main abc123] Updated commit",
            error=None,
            exit_code=0,
            command="git commit --amend -m 'Updated commit'"
        )
        
        tool = GitCommitTool()
        result = tool.execute(message="Updated commit", amend=True)
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['commit', '--amend', '-m', 'Updated commit'])
    
    @patch.object(GitCommitTool, '_run_git_command')
    def test_execute_no_verify(self, mock_run_git):
        """Test git commit with no verify."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="[main abc123] Test commit",
            error=None,
            exit_code=0,
            command="git commit --no-verify -m 'Test commit'"
        )
        
        tool = GitCommitTool()
        result = tool.execute(message="Test commit", no_verify=True)
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['commit', '--no-verify', '-m', 'Test commit'])


class TestGitPushTool:
    """Test GitPushTool."""
    
    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitPushTool()
        assert tool.name == "git_push"
        assert tool.permission_level == "ask"
        assert "Update remote refs" in tool.description
    
    @patch.object(GitPushTool, '_run_git_command')
    def test_execute_basic(self, mock_run_git):
        """Test basic git push execution."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Everything up-to-date",
            error=None,
            exit_code=0,
            command="git push origin"
        )
        
        tool = GitPushTool()
        result = tool.execute()
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['push', 'origin'])
    
    @patch.object(GitPushTool, '_run_git_command')
    def test_execute_with_branch(self, mock_run_git):
        """Test git push with specific branch."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="",
            error=None,
            exit_code=0,
            command="git push origin main"
        )
        
        tool = GitPushTool()
        result = tool.execute(branch="main")
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['push', 'origin', 'main'])
    
    @patch.object(GitPushTool, '_run_git_command')
    def test_execute_with_tags(self, mock_run_git):
        """Test git push with tags."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="",
            error=None,
            exit_code=0,
            command="git push --tags origin"
        )
        
        tool = GitPushTool()
        result = tool.execute(tags=True)
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['push', '--tags', 'origin'])
    
    @patch.object(GitPushTool, '_run_git_command')
    def test_execute_dry_run(self, mock_run_git):
        """Test git push with dry run."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Would push to origin",
            error=None,
            exit_code=0,
            command="git push --dry-run origin"
        )
        
        tool = GitPushTool()
        result = tool.execute(dry_run=True)
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['push', '--dry-run', 'origin'])
    
    @patch.object(GitPushTool, '_run_git_command')
    def test_execute_custom_remote(self, mock_run_git):
        """Test git push with custom remote."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="",
            error=None,
            exit_code=0,
            command="git push upstream"
        )
        
        tool = GitPushTool()
        result = tool.execute(remote="upstream")
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['push', 'upstream'])


class TestGitPullTool:
    """Test GitPullTool."""
    
    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitPullTool()
        assert tool.name == "git_pull"
        assert tool.permission_level == "ask"
        assert "Fetch from and integrate" in tool.description
    
    @patch.object(GitPullTool, '_run_git_command')
    def test_execute_basic(self, mock_run_git):
        """Test basic git pull execution."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Already up to date.",
            error=None,
            exit_code=0,
            command="git pull origin"
        )
        
        tool = GitPullTool()
        result = tool.execute()
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['pull', 'origin'])
    
    @patch.object(GitPullTool, '_run_git_command')
    def test_execute_with_rebase(self, mock_run_git):
        """Test git pull with rebase."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="",
            error=None,
            exit_code=0,
            command="git pull --rebase origin"
        )
        
        tool = GitPullTool()
        result = tool.execute(rebase=True)
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['pull', '--rebase', 'origin'])
    
    @patch.object(GitPullTool, '_run_git_command')
    def test_execute_with_branch(self, mock_run_git):
        """Test git pull with specific branch."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="",
            error=None,
            exit_code=0,
            command="git pull origin feature"
        )
        
        tool = GitPullTool()
        result = tool.execute(branch="feature")
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['pull', 'origin', 'feature'])
    
    @patch.object(GitPullTool, '_run_git_command')
    def test_execute_dry_run(self, mock_run_git):
        """Test git pull with dry run."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Would pull from origin",
            error=None,
            exit_code=0,
            command="git pull --dry-run origin"
        )
        
        tool = GitPullTool()
        result = tool.execute(dry_run=True)
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['pull', '--dry-run', 'origin'])
    
    @patch.object(GitPullTool, '_run_git_command')
    def test_execute_ff_only(self, mock_run_git):
        """Test git pull with fast-forward only."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="",
            error=None,
            exit_code=0,
            command="git pull --ff-only origin"
        )
        
        tool = GitPullTool()
        result = tool.execute(ff_only=True)
        
        assert result.success is True
        mock_run_git.assert_called_once_with(['pull', '--ff-only', 'origin'])