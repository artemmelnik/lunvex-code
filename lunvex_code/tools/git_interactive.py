"""Interactive Git tools for LunVex Code."""

from typing import Optional

from rich.console import Console

from .git_colors import git_colorizer
from .git_tools import GitToolBase, ToolResult

console = Console()


class GitInteractiveAddTool(GitToolBase):
    """Interactive git add with patch mode."""

    name = "git_add_interactive"
    description = "Interactively stage changes with patch mode"
    permission_level = "ask"  # Modifies staging area

    parameters = {
        "patch": {
            "type": "boolean",
            "description": "Use patch mode (interactive)",
            "required": False,
            "default": True,
        },
        "path": {
            "type": "string",
            "description": "Specific file or directory to add",
            "required": False,
        },
    }

    def execute(self, patch: bool = True, path: Optional[str] = None) -> ToolResult:
        """Execute interactive git add."""
        args = ["add"]

        if patch:
            args.append("--patch")

        if path:
            args.append("--")
            args.append(path)
        else:
            args.append(".")

        git_result = self._run_git_command(args)

        if git_result.success:
            output = git_result.output or "Changes staged successfully."

            # Show status after staging
            status_result = self._run_git_command(["status", "--short"])
            if status_result.success and status_result.output:
                output += "\n\nCurrent status:\n"
                output += git_colorizer.colorize_status(status_result.output, short=True)
        else:
            output = git_result.error or "Failed to stage changes."

        return ToolResult(
            success=git_result.success,
            output=output,
            error=git_result.error if not git_result.success else None,
        )
