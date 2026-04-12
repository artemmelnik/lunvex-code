"""Git integration tools for LunVex Code."""

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
            "command": self.command
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
                command=" ".join(["git"] + args)
            )
        
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace"
            )
            
            return GitResult(
                success=result.returncode == 0,
                output=result.stdout.strip(),
                error=result.stderr.strip() if result.stderr else None,
                exit_code=result.returncode,
                command=" ".join(["git"] + args)
            )
            
        except subprocess.TimeoutExpired:
            return GitResult(
                success=False,
                output="",
                error=f"Git command timed out after {timeout} seconds",
                exit_code=1,
                command=" ".join(["git"] + args)
            )
        except Exception as e:
            return GitResult(
                success=False,
                output="",
                error=f"Failed to execute Git command: {str(e)}",
                exit_code=1,
                command=" ".join(["git"] + args)
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


class GitStatusTool(GitToolBase):
    """Show the working tree status."""
    
    name = "git_status"
    description = "Show the working tree status (staged, unstaged, and untracked files)"
    permission_level = "auto"  # Read-only, safe operation
    
    parameters = {
        "short": {
            "type": "boolean",
            "description": "Give the output in the short-format",
            "required": False,
            "default": False
        },
        "porcelain": {
            "type": "boolean",
            "description": "Give the output in an easy-to-parse format for scripts",
            "required": False,
            "default": False
        },
        "branch": {
            "type": "boolean",
            "description": "Show the branch and tracking info even in short-format",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, short: bool = False, porcelain: bool = False, 
                branch: bool = False, format: str = "text") -> ToolResult:
        args = ["status"]
        
        if short:
            args.append("--short")
        if porcelain:
            args.append("--porcelain")
        if branch:
            args.append("--branch")
        
        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)
        
        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None
        )


class GitDiffTool(GitToolBase):
    """Show changes between commits, commit and working tree, etc."""
    
    name = "git_diff"
    description = "Show changes between commits, commit and working tree, etc"
    permission_level = "auto"  # Read-only, safe operation
    
    parameters = {
        "cached": {
            "type": "boolean",
            "description": "Show diff of staged changes",
            "required": False,
            "default": False
        },
        "staged": {
            "type": "boolean",
            "description": "Synonym for --cached",
            "required": False,
            "default": False
        },
        "file": {
            "type": "string",
            "description": "Show diff for specific file only",
            "required": False
        },
        "stat": {
            "type": "boolean",
            "description": "Generate a diffstat instead of patch",
            "required": False,
            "default": False
        },
        "name_only": {
            "type": "boolean",
            "description": "Show only names of changed files",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, cached: bool = False, staged: bool = False, 
                file: Optional[str] = None, stat: bool = False,
                name_only: bool = False, format: str = "text") -> ToolResult:
        args = ["diff"]
        
        if cached or staged:
            args.append("--cached")
        if stat:
            args.append("--stat")
        if name_only:
            args.append("--name-only")
        if file:
            args.append("--")
            args.append(file)
        
        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)
        
        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None
        )


class GitLogTool(GitToolBase):
    """Show commit logs."""
    
    name = "git_log"
    description = "Show commit logs with various formatting options"
    permission_level = "auto"  # Read-only, safe operation
    
    parameters = {
        "max_count": {
            "type": "integer",
            "description": "Limit the number of commits to output",
            "required": False
        },
        "oneline": {
            "type": "boolean",
            "description": "Show each commit on a single line",
            "required": False,
            "default": False
        },
        "graph": {
            "type": "boolean",
            "description": "Draw a text-based graphical representation",
            "required": False,
            "default": False
        },
        "decorate": {
            "type": "boolean",
            "description": "Print out the ref names of any commits that are shown",
            "required": False,
            "default": False
        },
        "since": {
            "type": "string",
            "description": "Show commits more recent than specific date",
            "required": False
        },
        "author": {
            "type": "string",
            "description": "Limit commits to specific author",
            "required": False
        },
        "grep": {
            "type": "string",
            "description": "Limit commits to those with log message matching pattern",
            "required": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, max_count: Optional[int] = None, oneline: bool = False,
                graph: bool = False, decorate: bool = False, since: Optional[str] = None,
                author: Optional[str] = None, grep: Optional[str] = None,
                format: str = "text") -> ToolResult:
        args = ["log"]
        
        if max_count:
            args.extend(["-n", str(max_count)])
        if oneline:
            args.append("--oneline")
        if graph:
            args.append("--graph")
        if decorate:
            args.append("--decorate")
        if since:
            args.extend(["--since", since])
        if author:
            args.extend(["--author", author])
        if grep:
            args.extend(["--grep", grep])
        
        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)
        
        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None
        )


class GitShowTool(GitToolBase):
    """Show various types of objects."""
    
    name = "git_show"
    description = "Show various types of objects (commits, tags, trees, blobs)"
    permission_level = "auto"  # Read-only, safe operation
    
    parameters = {
        "object": {
            "type": "string",
            "description": "The object to show (commit hash, tag, branch name). Defaults to HEAD",
            "required": False
        },
        "stat": {
            "type": "boolean",
            "description": "Show diffstat instead of patch",
            "required": False,
            "default": False
        },
        "name_only": {
            "type": "boolean",
            "description": "Show only names of changed files",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, object: Optional[str] = None, stat: bool = False,
                name_only: bool = False, format: str = "text") -> ToolResult:
        args = ["show"]
        
        if stat:
            args.append("--stat")
        if name_only:
            args.append("--name-only")
        if object:
            args.append(object)
        
        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)
        
        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None
        )


class GitBranchTool(GitToolBase):
    """List, create, or delete branches."""
    
    name = "git_branch"
    description = "List, create, or delete branches"
    permission_level = "ask"  # Can modify branches
    
    parameters = {
        "list": {
            "type": "boolean",
            "description": "List branches (default action)",
            "required": False,
            "default": True
        },
        "all": {
            "type": "boolean",
            "description": "List both remote-tracking and local branches",
            "required": False,
            "default": False
        },
        "remote": {
            "type": "boolean",
            "description": "List remote-tracking branches",
            "required": False,
            "default": False
        },
        "verbose": {
            "type": "boolean",
            "description": "Show SHA-1 and commit subject line for each head",
            "required": False,
            "default": False
        },
        "create": {
            "type": "string",
            "description": "Create a new branch with given name",
            "required": False
        },
        "delete": {
            "type": "string",
            "description": "Delete a branch (use with caution)",
            "required": False
        },
        "force_delete": {
            "type": "boolean",
            "description": "Force deletion (unmerged branches)",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, list: bool = True, all: bool = False, remote: bool = False,
                verbose: bool = False, create: Optional[str] = None,
                delete: Optional[str] = None, force_delete: bool = False,
                format: str = "text") -> ToolResult:
        args = ["branch"]
        
        if create:
            args.extend(["--create", create])
            if force_delete:
                args.append("-f")
        elif delete:
            if force_delete:
                args.extend(["-D", delete])
            else:
                args.extend(["-d", delete])
        else:
            # Listing branches
            if all:
                args.append("-a")
            if remote:
                args.append("-r")
            if verbose:
                args.append("-v")
        
        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)
        
        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None
        )


class GitAddTool(GitToolBase):
    """Add file contents to the index."""
    
    name = "git_add"
    description = "Add file contents to the index (stage changes)"
    permission_level = "ask"  # Modifies staging area
    
    parameters = {
        "paths": {
            "type": "string",
            "description": "Files to add content from. Can be file paths, directories, or '.' for all",
            "required": True
        },
        "all": {
            "type": "boolean",
            "description": "Add changes from all tracked and untracked files",
            "required": False,
            "default": False
        },
        "update": {
            "type": "boolean",
            "description": "Only match tracked files (skip untracked)",
            "required": False,
            "default": False
        },
        "dry_run": {
            "type": "boolean",
            "description": "Don't actually add the file(s), just show if they exist and/or will be ignored",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, paths: str, all: bool = False, update: bool = False,
                dry_run: bool = False, format: str = "text") -> ToolResult:
        args = ["add"]
        
        if all:
            args.append("--all")
        elif update:
            args.append("--update")
        
        if dry_run:
            args.append("--dry-run")
        
        # Add the paths
        if paths != ".":
            # Split by spaces, but handle quoted paths
            import shlex
            path_list = shlex.split(paths)
            args.extend(path_list)
        else:
            args.append(".")
        
        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)
        
        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None
        )


class GitCommitTool(GitToolBase):
    """Record changes to the repository."""
    
    name = "git_commit"
    description = "Record changes to the repository"
    permission_level = "ask"  # Creates commits
    
    parameters = {
        "message": {
            "type": "string",
            "description": "Commit message",
            "required": True
        },
        "all": {
            "type": "boolean",
            "description": "Automatically stage files that have been modified and deleted",
            "required": False,
            "default": False
        },
        "amend": {
            "type": "boolean",
            "description": "Amend previous commit",
            "required": False,
            "default": False
        },
        "no_verify": {
            "type": "boolean",
            "description": "Bypass pre-commit and commit-msg hooks",
            "required": False,
            "default": False
        },
        "allow_empty": {
            "type": "boolean",
            "description": "Allow empty commit (no changes)",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, message: str, all: bool = False, amend: bool = False,
                no_verify: bool = False, allow_empty: bool = False,
                format: str = "text") -> ToolResult:
        args = ["commit"]
        
        if all:
            args.append("--all")
        if amend:
            args.append("--amend")
        if no_verify:
            args.append("--no-verify")
        if allow_empty:
            args.append("--allow-empty")
        
        # Add message
        args.extend(["-m", message])
        
        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)
        
        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None
        )


class GitPushTool(GitToolBase):
    """Update remote refs along with associated objects."""
    
    name = "git_push"
    description = "Update remote refs along with associated objects"
    permission_level = "ask"  # Modifies remote repository
    
    parameters = {
        "remote": {
            "type": "string",
            "description": "Remote repository to push to (default: origin)",
            "required": False,
            "default": "origin"
        },
        "branch": {
            "type": "string",
            "description": "Branch to push (default: current branch)",
            "required": False
        },
        "force": {
            "type": "boolean",
            "description": "Force push (dangerous - can lose remote history)",
            "required": False,
            "default": False
        },
        "force_with_lease": {
            "type": "boolean",
            "description": "Force push with lease (safer than --force)",
            "required": False,
            "default": False
        },
        "tags": {
            "type": "boolean",
            "description": "Push all tags",
            "required": False,
            "default": False
        },
        "dry_run": {
            "type": "boolean",
            "description": "Do everything except actually send the updates",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, remote: str = "origin", branch: Optional[str] = None,
                force: bool = False, force_with_lease: bool = False,
                tags: bool = False, dry_run: bool = False,
                format: str = "text") -> ToolResult:
        args = ["push"]
        
        if force:
            args.append("--force")
        elif force_with_lease:
            args.append("--force-with-lease")
        
        if tags:
            args.append("--tags")
        
        if dry_run:
            args.append("--dry-run")
        
        # Add remote and branch
        if branch:
            args.extend([remote, branch])
        else:
            args.append(remote)
        
        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)
        
        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None
        )


class GitPullTool(GitToolBase):
    """Fetch from and integrate with another repository or a local branch."""
    
    name = "git_pull"
    description = "Fetch from and integrate with another repository or a local branch"
    permission_level = "ask"  # Modifies local repository
    
    parameters = {
        "remote": {
            "type": "string",
            "description": "Remote repository to pull from (default: origin)",
            "required": False,
            "default": "origin"
        },
        "branch": {
            "type": "string",
            "description": "Branch to pull (default: current branch)",
            "required": False
        },
        "rebase": {
            "type": "boolean",
            "description": "Use rebase instead of merge",
            "required": False,
            "default": False
        },
        "no_commit": {
            "type": "boolean",
            "description": "Do not create a merge commit",
            "required": False,
            "default": False
        },
        "ff_only": {
            "type": "boolean",
            "description": "Allow only fast-forward merges",
            "required": False,
            "default": False
        },
        "dry_run": {
            "type": "boolean",
            "description": "Show what would be done without actually doing it",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, remote: str = "origin", branch: Optional[str] = None,
                rebase: bool = False, no_commit: bool = False,
                ff_only: bool = False, dry_run: bool = False,
                format: str = "text") -> ToolResult:
        args = ["pull"]
        
        if rebase:
            args.append("--rebase")
        if no_commit:
            args.append("--no-commit")
        if ff_only:
            args.append("--ff-only")
        if dry_run:
            args.append("--dry-run")
        
        # Add remote and branch
        if branch:
            args.extend([remote, branch])
        else:
            args.append(remote)
        
        git_result = self._run_git_command(args)
        output = self._format_output(git_result, format)
        
        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None
        )


class GitStashTool(GitToolBase):
    """Stash the changes in a dirty working directory away."""
    
    name = "git_stash"
    description = "Stash the changes in a dirty working directory away"
    permission_level = "ask"  # Modifies working directory
    
    parameters = {
        "save": {
            "type": "string",
            "description": "Save stash with custom message",
            "required": False
        },
        "list": {
            "type": "boolean",
            "description": "List stash entries",
            "required": False,
            "default": False
        },
        "show": {
            "type": "string",
            "description": "Show the changes recorded in the stash (default: latest)",
            "required": False
        },
        "pop": {
            "type": "string",
            "description": "Remove and apply a single stashed state (default: latest)",
            "required": False
        },
        "apply": {
            "type": "string",
            "description": "Apply the changes recorded in the stash (default: latest)",
            "required": False
        },
        "drop": {
            "type": "string",
            "description": "Remove a single stash entry (default: latest)",
            "required": False
        },
        "clear": {
            "type": "boolean",
            "description": "Remove all stash entries",
            "required": False,
            "default": False
        },
        "include_untracked": {
            "type": "boolean",
            "description": "Include untracked files in stash",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, save: Optional[str] = None, list: bool = False,
                show: Optional[str] = None, pop: Optional[str] = None,
                apply: Optional[str] = None, drop: Optional[str] = None,
                clear: bool = False, include_untracked: bool = False,
                format: str = "text") -> ToolResult:
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
            error=git_result.error if not git_result.success else None
        )


class GitCheckoutTool(GitToolBase):
    """Switch branches or restore working tree files."""
    
    name = "git_checkout"
    description = "Switch branches or restore working tree files"
    permission_level = "ask"  # Can modify working directory
    
    parameters = {
        "branch": {
            "type": "string",
            "description": "Branch to checkout",
            "required": False
        },
        "create": {
            "type": "boolean",
            "description": "Create and checkout new branch",
            "required": False,
            "default": False
        },
        "force": {
            "type": "boolean",
            "description": "Force checkout (discard local changes)",
            "required": False,
            "default": False
        },
        "file": {
            "type": "string",
            "description": "Restore specific file from index",
            "required": False
        },
        "theirs": {
            "type": "boolean",
            "description": "Checkout 'their' version for unmerged paths",
            "required": False,
            "default": False
        },
        "ours": {
            "type": "boolean",
            "description": "Checkout 'our' version for unmerged paths",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, branch: Optional[str] = None, create: bool = False,
                force: bool = False, file: Optional[str] = None,
                theirs: bool = False, ours: bool = False,
                format: str = "text") -> ToolResult:
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
            error=git_result.error if not git_result.success else None
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
            "required": True
        },
        "no_ff": {
            "type": "boolean",
            "description": "Create a merge commit even if fast-forward is possible",
            "required": False,
            "default": False
        },
        "ff_only": {
            "type": "boolean",
            "description": "Allow only fast-forward merges",
            "required": False,
            "default": False
        },
        "squash": {
            "type": "boolean",
            "description": "Create a single commit instead of merging",
            "required": False,
            "default": False
        },
        "no_commit": {
            "type": "boolean",
            "description": "Perform merge but don't commit",
            "required": False,
            "default": False
        },
        "abort": {
            "type": "boolean",
            "description": "Abort the current conflict resolution process",
            "required": False,
            "default": False
        },
        "continue": {
            "type": "boolean",
            "description": "Continue after resolving merge conflicts",
            "required": False,
            "default": False
        },
        "message": {
            "type": "string",
            "description": "Merge commit message",
            "required": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, branch: str, no_ff: bool = False, ff_only: bool = False,
                squash: bool = False, no_commit: bool = False,
                abort: bool = False, continue_: bool = False,
                message: Optional[str] = None, format: str = "text") -> ToolResult:
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
            error=git_result.error if not git_result.success else None
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
            "default": "origin"
        },
        "all": {
            "type": "boolean",
            "description": "Fetch all remotes",
            "required": False,
            "default": False
        },
        "prune": {
            "type": "boolean",
            "description": "Remove remote-tracking references that no longer exist",
            "required": False,
            "default": False
        },
        "tags": {
            "type": "boolean",
            "description": "Fetch all tags",
            "required": False,
            "default": False
        },
        "dry_run": {
            "type": "boolean",
            "description": "Show what would be done without making changes",
            "required": False,
            "default": False
        },
        "format": {
            "type": "string",
            "description": "Output format: 'text' (default) or 'json'",
            "required": False,
            "default": "text"
        }
    }
    
    def execute(self, remote: str = "origin", all: bool = False,
                prune: bool = False, tags: bool = False,
                dry_run: bool = False, format: str = "text") -> ToolResult:
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
            error=git_result.error if not git_result.success else None
        )
