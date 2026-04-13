"""Phase 3 Git tools (stash, checkout, merge, fetch)."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Tool, ToolResult


@dataclass
class GitResult:
    """Structured result from Git command execution."""

    success: bool
    output: str
    error: Optional[str] = None
    exit_code: int = 0
    command: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "exit_code": self.exit_code,
            "command": self.command,
        }


class GitToolBase(Tool):
    """Base class for Git tools."""

    def __init__(self):
        self.project_root = None
        # Don't find git root in __init__ to avoid issues in tests
        # It will be found lazily when needed

    def _find_git_root(self) -> Optional[Path]:
        """Find the Git repository root from current directory."""
        try:
            current = Path.cwd()
        except FileNotFoundError:
            # Can happen in tests when temp directory is cleaned up
            return None

        # Walk up the directory tree looking for .git directory
        while current != current.parent:  # Stop at root
            git_dir = current / ".git"
            if git_dir.exists():
                return current
            current = current.parent

        return None

    def _ensure_git_root(self) -> Optional[Path]:
        """Ensure git root is found, find it if not already found."""
        if self.project_root is None:
            self.project_root = self._find_git_root()
        return self.project_root

    def _run_git_command(self, args: List[str], timeout: int = 30) -> GitResult:
        """Execute a Git command and return structured result."""
        project_root = self._ensure_git_root()
        if not project_root:
            return GitResult(
                success=False,
                output="",
                error="Not in a Git repository",
                exit_code=1,
                command=" ".join(["git"] + args),
            )

        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )

            return GitResult(
                success=result.returncode == 0,
                output=result.stdout.strip(),
                error=result.stderr.strip() if result.stderr else None,
                exit_code=result.returncode,
                command=" ".join(["git"] + args),
            )

        except subprocess.TimeoutExpired:
            return GitResult(
                success=False,
                output="",
                error=f"Git command timed out after {timeout} seconds",
                exit_code=1,
                command=" ".join(["git"] + args),
            )
        except Exception as e:
            return GitResult(
                success=False,
                output="",
                error=f"Failed to execute Git command: {str(e)}",
                exit_code=1,
                command=" ".join(["git"] + args),
            )

    def _format_output(self, git_result: GitResult, format_type: str = "text") -> str:
        """Format Git result for output."""
        if format_type == "json":
            return json.dumps(git_result.to_dict(), indent=2, ensure_ascii=False)

        # Default text format
        if not git_result.success:
            error_msg = f"Git command failed (exit code: {git_result.exit_code})"
            if git_result.error:
                error_msg += f"\nError: {git_result.error}"
            return error_msg

        if git_result.output:
            return git_result.output

        return "Command executed successfully (no output)"


class GitStashTool(GitToolBase):
    """Stash the changes in a dirty working directory away."""

    name = "git_stash"
    description = "Stash the changes in a dirty working directory away"
    permission_level = "ask"  # Modifies working directory

    parameters = {
        "save": {
            "type": "string",
            "description": "Save stash with custom message",
            "required": False,
        },
        "list": {
            "type": "boolean",
            "description": "List stash entries",
            "required": False,
            "default": False,
        },
        "show": {
            "type": "string",
            "description": "Show the changes recorded in the stash (default: latest)",
            "required": False,
        },
        "pop": {
            "type": "string",
            "description": "Remove and apply a single stashed state (default: latest)",
            "required": False,
        },
        "apply": {
            "type": "string",
            "description": "Apply the changes recorded in the stash (default: latest)",
            "required": False,
        },
        "drop": {
            "type": "string",
            "description": "Remove a single stash entry (default: latest)",
            "required": False,
        },
        "clear": {
            "type": "boolean",
            "description": "Remove all stash entries",
            "required": False,
            "default": False,
        },
        "include_untracked": {
            "type": "boolean",
            "description": "Include untracked files in stash",
            "required": False,
            "default": False,
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text",
        },
    }

    def execute(
        self,
        save: Optional[str] = None,
        list: bool = False,
        show: Optional[str] = None,
        pop: Optional[str] = None,
        apply: Optional[str] = None,
        drop: Optional[str] = None,
        clear: bool = False,
        include_untracked: bool = False,
        format: str = "text",
    ) -> ToolResult:
        args = ["stash"]

        if save:
            args.extend(["save", save])
        elif list:
            args.append("list")
        elif show is not None:
            if show:
                args.extend(["show", show])
            else:
                args.append("show")
        elif pop is not None:
            if pop:
                args.extend(["pop", pop])
            else:
                args.append("pop")
        elif apply is not None:
            if apply:
                args.extend(["apply", apply])
            else:
                args.append("apply")
        elif drop is not None:
            if drop:
                args.extend(["drop", drop])
            else:
                args.append("drop")
        elif clear:
            args.append("clear")
        else:
            # Default: save with default message
            args.append("save")

        if include_untracked and (save or (not any([list, show, pop, apply, drop, clear]))):
            args.append("--include-untracked")

        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)

        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None,
        )


class GitCheckoutTool(GitToolBase):
    """Switch branches or restore working tree files."""

    name = "git_checkout"
    description = "Switch branches or restore working tree files"
    permission_level = "ask"  # Can modify working directory

    parameters = {
        "branch": {"type": "string", "description": "Branch to checkout", "required": False},
        "create": {
            "type": "boolean",
            "description": "Create and checkout new branch",
            "required": False,
            "default": False,
        },
        "force": {
            "type": "boolean",
            "description": "Force checkout (discard local changes)",
            "required": False,
            "default": False,
        },
        "file": {
            "type": "string",
            "description": "Restore specific file from index",
            "required": False,
        },
        "theirs": {
            "type": "boolean",
            "description": "Checkout 'their' version for unmerged paths",
            "required": False,
            "default": False,
        },
        "ours": {
            "type": "boolean",
            "description": "Checkout 'our' version for unmerged paths",
            "required": False,
            "default": False,
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text",
        },
    }

    def execute(
        self,
        branch: Optional[str] = None,
        create: bool = False,
        force: bool = False,
        file: Optional[str] = None,
        theirs: bool = False,
        ours: bool = False,
        format: str = "text",
    ) -> ToolResult:
        args = ["checkout"]

        if force:
            args.append("--force")

        if branch:
            if create:
                args.extend(["-b", branch])
            else:
                args.append(branch)
        elif file:
            if theirs:
                args.append("--theirs")
            elif ours:
                args.append("--ours")
            args.append("--")
            args.append(file)

        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)

        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None,
        )


class GitMergeTool(GitToolBase):
    """Join two or more development histories together."""

    name = "git_merge"
    description = "Join two or more development histories together"
    permission_level = "ask"  # Modifies repository history

    parameters = {
        "branch": {
            "type": "string",
            "description": "Branch to merge into current branch",
            "required": True,
        },
        "no_ff": {
            "type": "boolean",
            "description": "Create a merge commit even if fast-forward is possible",
            "required": False,
            "default": False,
        },
        "ff_only": {
            "type": "boolean",
            "description": "Allow only fast-forward merges",
            "required": False,
            "default": False,
        },
        "squash": {
            "type": "boolean",
            "description": "Create a single commit instead of merging",
            "required": False,
            "default": False,
        },
        "no_commit": {
            "type": "boolean",
            "description": "Perform merge but don't commit",
            "required": False,
            "default": False,
        },
        "abort": {
            "type": "boolean",
            "description": "Abort the current conflict resolution process",
            "required": False,
            "default": False,
        },
        "continue": {
            "type": "boolean",
            "description": "Continue after resolving merge conflicts",
            "required": False,
            "default": False,
        },
        "message": {"type": "string", "description": "Merge commit message", "required": False},
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text",
        },
    }

    def execute(
        self,
        branch: str,
        no_ff: bool = False,
        ff_only: bool = False,
        squash: bool = False,
        no_commit: bool = False,
        abort: bool = False,
        continue_: bool = False,
        message: Optional[str] = None,
        format: str = "text",
    ) -> ToolResult:
        args = ["merge"]

        if abort:
            args.append("--abort")
            git_result = self._run_git_command(args)
        elif continue_:
            args.append("--continue")
            git_result = self._run_git_command(args)
        else:
            if no_ff:
                args.append("--no-ff")
            if ff_only:
                args.append("--ff-only")
            if squash:
                args.append("--squash")
            if no_commit:
                args.append("--no-commit")
            if message:
                args.extend(["-m", message])

            args.append(branch)
            git_result = self._run_git_command(args)

        output = self._format_output(git_result, format)

        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None,
        )


class GitFetchTool(GitToolBase):
    """Download objects and refs from another repository."""

    name = "git_fetch"
    description = "Download objects and refs from another repository"
    permission_level = "ask"  # Updates local refs

    parameters = {
        "remote": {
            "type": "string",
            "description": "Remote repository to fetch from (default: origin)",
            "required": False,
            "default": "origin",
        },
        "all": {
            "type": "boolean",
            "description": "Fetch all remotes",
            "required": False,
            "default": False,
        },
        "prune": {
            "type": "boolean",
            "description": "Remove remote-tracking references that no longer exist",
            "required": False,
            "default": False,
        },
        "tags": {
            "type": "boolean",
            "description": "Fetch all tags",
            "required": False,
            "default": False,
        },
        "dry_run": {
            "type": "boolean",
            "description": "Show what would be done without making changes",
            "required": False,
            "default": False,
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text",
        },
    }

    def execute(
        self,
        remote: str = "origin",
        all: bool = False,
        prune: bool = False,
        tags: bool = False,
        dry_run: bool = False,
        format: str = "text",
    ) -> ToolResult:
        args = ["fetch"]

        if all:
            args.append("--all")
        if prune:
            args.append("--prune")
        if tags:
            args.append("--tags")
        if dry_run:
            args.append("--dry-run")

        if not all:
            args.append(remote)

        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)

        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None,
        )
