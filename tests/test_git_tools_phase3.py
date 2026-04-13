"""Tests for Phase 3 Git tools (stash, checkout, merge, fetch)."""

from unittest.mock import patch

from lunvex_code.tools.git_tools import (
    GitCheckoutTool,
    GitFetchTool,
    GitMergeTool,
    GitResult,
    GitStashTool,
)


class TestGitStashTool:
    """Test GitStashTool."""

    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitStashTool()
        assert tool.name == "git_stash"
        assert tool.permission_level == "ask"
        assert "Stash the changes in a dirty working directory" in tool.description

    @patch.object(GitStashTool, "_run_git_command")
    def test_execute_save(self, mock_run_git):
        """Test git stash save."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Saved working directory and index state",
            error=None,
            exit_code=0,
            command="git stash save 'WIP'",
        )

        tool = GitStashTool()
        result = tool.execute(save="WIP")

        assert result.success is True
        mock_run_git.assert_called_once_with(["stash", "save", "WIP"])

    @patch.object(GitStashTool, "_run_git_command")
    def test_execute_list(self, mock_run_git):
        """Test git stash list."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="stash@{0}: WIP on main: abc123 Initial commit",
            error=None,
            exit_code=0,
            command="git stash list",
        )

        tool = GitStashTool()
        result = tool.execute(list=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["stash", "list"])

    @patch.object(GitStashTool, "_run_git_command")
    def test_execute_pop(self, mock_run_git):
        """Test git stash pop."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Dropped refs/stash@{0}",
            error=None,
            exit_code=0,
            command="git stash pop",
        )

        tool = GitStashTool()
        result = tool.execute(pop="")

        assert result.success is True
        mock_run_git.assert_called_once_with(["stash", "pop"])

    @patch.object(GitStashTool, "_run_git_command")
    def test_execute_apply(self, mock_run_git):
        """Test git stash apply."""
        mock_run_git.return_value = GitResult(
            success=True, output="", error=None, exit_code=0, command="git stash apply"
        )

        tool = GitStashTool()
        result = tool.execute(apply="")

        assert result.success is True
        mock_run_git.assert_called_once_with(["stash", "apply"])

    @patch.object(GitStashTool, "_run_git_command")
    def test_execute_default_save(self, mock_run_git):
        """Test git stash default (save)."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Saved working directory and index state",
            error=None,
            exit_code=0,
            command="git stash save",
        )

        tool = GitStashTool()
        result = tool.execute()

        assert result.success is True
        mock_run_git.assert_called_once_with(["stash", "save"])


class TestGitCheckoutTool:
    """Test GitCheckoutTool."""

    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitCheckoutTool()
        assert tool.name == "git_checkout"
        assert tool.permission_level == "ask"
        assert "Switch branches or restore working tree files" in tool.description

    @patch.object(GitCheckoutTool, "_run_git_command")
    def test_execute_checkout_branch(self, mock_run_git):
        """Test git checkout branch."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Switched to branch 'feature'",
            error=None,
            exit_code=0,
            command="git checkout feature",
        )

        tool = GitCheckoutTool()
        result = tool.execute(branch="feature")

        assert result.success is True
        mock_run_git.assert_called_once_with(["checkout", "feature"])

    @patch.object(GitCheckoutTool, "_run_git_command")
    def test_execute_create_branch(self, mock_run_git):
        """Test git checkout create branch."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Switched to a new branch 'feature'",
            error=None,
            exit_code=0,
            command="git checkout -b feature",
        )

        tool = GitCheckoutTool()
        result = tool.execute(branch="feature", create=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["checkout", "-b", "feature"])

    @patch.object(GitCheckoutTool, "_run_git_command")
    def test_execute_force_checkout(self, mock_run_git):
        """Test git checkout with force."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Switched to branch 'main'",
            error=None,
            exit_code=0,
            command="git checkout --force main",
        )

        tool = GitCheckoutTool()
        result = tool.execute(branch="main", force=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["checkout", "--force", "main"])

    @patch.object(GitCheckoutTool, "_run_git_command")
    def test_execute_checkout_file(self, mock_run_git):
        """Test git checkout file."""
        mock_run_git.return_value = GitResult(
            success=True, output="", error=None, exit_code=0, command="git checkout -- file.txt"
        )

        tool = GitCheckoutTool()
        result = tool.execute(file="file.txt")

        assert result.success is True
        mock_run_git.assert_called_once_with(["checkout", "--", "file.txt"])


class TestGitMergeTool:
    """Test GitMergeTool."""

    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitMergeTool()
        assert tool.name == "git_merge"
        assert tool.permission_level == "ask"
        assert "Join two or more development histories together" in tool.description

    @patch.object(GitMergeTool, "_run_git_command")
    def test_execute_basic_merge(self, mock_run_git):
        """Test basic git merge."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Merge made by the 'recursive' strategy.",
            error=None,
            exit_code=0,
            command="git merge feature",
        )

        tool = GitMergeTool()
        result = tool.execute(branch="feature")

        assert result.success is True
        mock_run_git.assert_called_once_with(["merge", "feature"])

    @patch.object(GitMergeTool, "_run_git_command")
    def test_execute_no_ff(self, mock_run_git):
        """Test git merge with no fast-forward."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Merge made by the 'recursive' strategy.",
            error=None,
            exit_code=0,
            command="git merge --no-ff feature",
        )

        tool = GitMergeTool()
        result = tool.execute(branch="feature", no_ff=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["merge", "--no-ff", "feature"])

    @patch.object(GitMergeTool, "_run_git_command")
    def test_execute_squash(self, mock_run_git):
        """Test git merge with squash."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Squash commit -- not updating HEAD",
            error=None,
            exit_code=0,
            command="git merge --squash feature",
        )

        tool = GitMergeTool()
        result = tool.execute(branch="feature", squash=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["merge", "--squash", "feature"])

    @patch.object(GitMergeTool, "_run_git_command")
    def test_execute_abort(self, mock_run_git):
        """Test git merge abort."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Merge aborted.",
            error=None,
            exit_code=0,
            command="git merge --abort",
        )

        tool = GitMergeTool()
        result = tool.execute(branch="feature", abort=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["merge", "--abort"])

    @patch.object(GitMergeTool, "_run_git_command")
    def test_execute_with_message(self, mock_run_git):
        """Test git merge with custom message."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Merge made by the 'recursive' strategy.",
            error=None,
            exit_code=0,
            command="git merge -m 'Merge feature branch' feature",
        )

        tool = GitMergeTool()
        result = tool.execute(branch="feature", message="Merge feature branch")

        assert result.success is True
        mock_run_git.assert_called_once_with(["merge", "-m", "Merge feature branch", "feature"])


class TestGitFetchTool:
    """Test GitFetchTool."""

    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitFetchTool()
        assert tool.name == "git_fetch"
        assert tool.permission_level == "ask"
        assert "Download objects and refs from another repository" in tool.description

    @patch.object(GitFetchTool, "_run_git_command")
    def test_execute_basic_fetch(self, mock_run_git):
        """Test basic git fetch."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="From github.com:user/repo",
            error=None,
            exit_code=0,
            command="git fetch origin",
        )

        tool = GitFetchTool()
        result = tool.execute()

        assert result.success is True
        mock_run_git.assert_called_once_with(["fetch", "origin"])

    @patch.object(GitFetchTool, "_run_git_command")
    def test_execute_fetch_all(self, mock_run_git):
        """Test git fetch all."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Fetching origin\nFetching upstream",
            error=None,
            exit_code=0,
            command="git fetch --all",
        )

        tool = GitFetchTool()
        result = tool.execute(all=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["fetch", "--all"])

    @patch.object(GitFetchTool, "_run_git_command")
    def test_execute_fetch_prune(self, mock_run_git):
        """Test git fetch with prune."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="From github.com:user/repo",
            error=None,
            exit_code=0,
            command="git fetch --prune origin",
        )

        tool = GitFetchTool()
        result = tool.execute(prune=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["fetch", "--prune", "origin"])

    @patch.object(GitFetchTool, "_run_git_command")
    def test_execute_fetch_tags(self, mock_run_git):
        """Test git fetch with tags."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="From github.com:user/repo",
            error=None,
            exit_code=0,
            command="git fetch --tags origin",
        )

        tool = GitFetchTool()
        result = tool.execute(tags=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["fetch", "--tags", "origin"])

    @patch.object(GitFetchTool, "_run_git_command")
    def test_execute_fetch_dry_run(self, mock_run_git):
        """Test git fetch with dry run."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="Would fetch from origin",
            error=None,
            exit_code=0,
            command="git fetch --dry-run origin",
        )

        tool = GitFetchTool()
        result = tool.execute(dry_run=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["fetch", "--dry-run", "origin"])

    @patch.object(GitFetchTool, "_run_git_command")
    def test_execute_fetch_custom_remote(self, mock_run_git):
        """Test git fetch with custom remote."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="From github.com:user/repo",
            error=None,
            exit_code=0,
            command="git fetch upstream",
        )

        tool = GitFetchTool()
        result = tool.execute(remote="upstream")

        assert result.success is True
        mock_run_git.assert_called_once_with(["fetch", "upstream"])
