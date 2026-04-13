"""Simplified tests for Git tools."""

from unittest.mock import Mock, patch

from lunvex_code.tools.git_tools import (
    GitBranchTool,
    GitDiffTool,
    GitLogTool,
    GitResult,
    GitShowTool,
    GitStatusTool,
    GitToolBase,
)


class TestGitToolBaseSimple:
    """Test GitToolBase functionality with mocks."""

    def test_format_output_json(self):
        """Test JSON output formatting."""

        # Create a concrete subclass for testing
        class TestGitTool(GitToolBase):
            def execute(self, **kwargs):
                return Mock()

        tool = TestGitTool()
        git_result = Mock()
        git_result.success = True
        git_result.output = "test output"
        git_result.error = None
        git_result.exit_code = 0
        git_result.command = "git status"
        git_result.to_dict.return_value = {
            "success": True,
            "output": "test output",
            "error": None,
            "exit_code": 0,
            "command": "git status",
        }

        output = tool._format_output(git_result, "json")
        assert "test output" in output
        assert '"success": true' in output

    def test_format_output_text_success(self):
        """Test text output formatting for successful command."""

        # Create a concrete subclass for testing
        class TestGitTool(GitToolBase):
            def execute(self, **kwargs):
                return Mock()

        tool = TestGitTool()
        git_result = Mock()
        git_result.success = True
        git_result.output = "test output"
        git_result.error = None

        output = tool._format_output(git_result, "text")
        assert output == "test output"

    def test_format_output_text_failure(self):
        """Test text output formatting for failed command."""

        # Create a concrete subclass for testing
        class TestGitTool(GitToolBase):
            def execute(self, **kwargs):
                return Mock()

        tool = TestGitTool()
        git_result = Mock()
        git_result.success = False
        git_result.output = ""
        git_result.error = "command failed"
        git_result.exit_code = 1

        output = tool._format_output(git_result, "text")
        assert "command failed" in output
        assert "exit code: 1" in output


class TestGitStatusToolSimple:
    """Test GitStatusTool with mocks."""

    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitStatusTool()
        assert tool.name == "git_status"
        assert tool.permission_level == "auto"
        assert "working tree status" in tool.description

    @patch.object(GitStatusTool, "_run_git_command")
    def test_execute_basic(self, mock_run_git):
        """Test basic git status execution."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="On branch main\nnothing to commit, working tree clean",
            error=None,
            exit_code=0,
            command="git status",
        )

        tool = GitStatusTool()
        result = tool.execute()

        assert result.success is True
        assert "On branch main" in result.output
        mock_run_git.assert_called_once_with(["status"])

    @patch.object(GitStatusTool, "_run_git_command")
    def test_execute_short_format(self, mock_run_git):
        """Test git status with short format."""
        mock_run_git.return_value = GitResult(
            success=True, output="", error=None, exit_code=0, command="git status --short"
        )

        tool = GitStatusTool()
        result = tool.execute(short=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["status", "--short"])


class TestGitDiffToolSimple:
    """Test GitDiffTool with mocks."""

    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitDiffTool()
        assert tool.name == "git_diff"
        assert tool.permission_level == "auto"
        assert "changes between commits" in tool.description

    @patch.object(GitDiffTool, "_run_git_command")
    def test_execute_basic(self, mock_run_git):
        """Test basic git diff execution."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="diff --git a/file.txt b/file.txt\nnew file mode 100644",
            error=None,
            exit_code=0,
            command="git diff",
        )

        tool = GitDiffTool()
        result = tool.execute()

        assert result.success is True
        mock_run_git.assert_called_once_with(["diff"])

    @patch.object(GitDiffTool, "_run_git_command")
    def test_execute_cached(self, mock_run_git):
        """Test git diff with cached/staged changes."""
        mock_run_git.return_value = GitResult(
            success=True, output="", error=None, exit_code=0, command="git diff --cached"
        )

        tool = GitDiffTool()
        result = tool.execute(cached=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["diff", "--cached"])


class TestGitLogToolSimple:
    """Test GitLogTool with mocks."""

    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitLogTool()
        assert tool.name == "git_log"
        assert tool.permission_level == "auto"
        assert "commit logs" in tool.description

    @patch.object(GitLogTool, "_run_git_command")
    def test_execute_basic(self, mock_run_git):
        """Test basic git log execution."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="commit abc123\nAuthor: Test <test@example.com>\nDate:   Mon Jan 1 00:00:00 2024 +0000",
            error=None,
            exit_code=0,
            command="git log",
        )

        tool = GitLogTool()
        result = tool.execute()

        assert result.success is True
        mock_run_git.assert_called_once_with(["log"])

    @patch.object(GitLogTool, "_run_git_command")
    def test_execute_oneline(self, mock_run_git):
        """Test git log with oneline format."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="abc123 Initial commit",
            error=None,
            exit_code=0,
            command="git log --oneline",
        )

        tool = GitLogTool()
        result = tool.execute(oneline=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["log", "--oneline"])


class TestGitShowToolSimple:
    """Test GitShowTool with mocks."""

    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitShowTool()
        assert tool.name == "git_show"
        assert tool.permission_level == "auto"
        assert "Show various types of objects" in tool.description

    @patch.object(GitShowTool, "_run_git_command")
    def test_execute_basic(self, mock_run_git):
        """Test basic git show execution."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="commit abc123\nAuthor: Test <test@example.com>",
            error=None,
            exit_code=0,
            command="git show",
        )

        tool = GitShowTool()
        result = tool.execute()

        assert result.success is True
        mock_run_git.assert_called_once_with(["show"])


class TestGitBranchToolSimple:
    """Test GitBranchTool with mocks."""

    def test_tool_attributes(self):
        """Test tool metadata."""
        tool = GitBranchTool()
        assert tool.name == "git_branch"
        assert tool.permission_level == "ask"  # Can modify branches
        assert "List, create, or delete branches" in tool.description

    @patch.object(GitBranchTool, "_run_git_command")
    def test_execute_list_branches(self, mock_run_git):
        """Test listing branches."""
        mock_run_git.return_value = GitResult(
            success=True, output="* main\n  feature", error=None, exit_code=0, command="git branch"
        )

        tool = GitBranchTool()
        result = tool.execute(list=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["branch"])

    @patch.object(GitBranchTool, "_run_git_command")
    def test_execute_list_verbose(self, mock_run_git):
        """Test listing branches with verbose output."""
        mock_run_git.return_value = GitResult(
            success=True,
            output="* main abc123 Initial commit",
            error=None,
            exit_code=0,
            command="git branch -v",
        )

        tool = GitBranchTool()
        result = tool.execute(list=True, verbose=True)

        assert result.success is True
        mock_run_git.assert_called_once_with(["branch", "-v"])
