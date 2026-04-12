"""Context management for project-specific configuration."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from . import APP_CONTEXT_FILENAME


@dataclass
class ProjectContext:
    """Context information about the current project."""

    working_dir: str
    project_md: str | None = None
    git_branch: str | None = None
    git_repo: bool = False


def find_project_root(start_path: str = ".") -> Path:
    """
    Find the project root by looking for common indicators.

    Looks for (in order):
    1. .git directory
    2. LUNVEX.md file
    3. pyproject.toml
    4. package.json
    5. Cargo.toml
    """
    current = Path(start_path).resolve()

    indicators = [
        ".git",
        APP_CONTEXT_FILENAME,
        "pyproject.toml",
        "package.json",
        "Cargo.toml",
    ]

    while current != current.parent:
        for indicator in indicators:
            if (current / indicator).exists():
                return current
        current = current.parent

    # Fallback to start path
    return Path(start_path).resolve()


def load_project_md(project_root: Path) -> tuple[str | None, str | None]:
    """Load project context markdown from LUNVEX.md."""
    md_path = project_root / APP_CONTEXT_FILENAME
    if md_path.exists():
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                return f.read(), APP_CONTEXT_FILENAME
        except Exception:
            return None, None

    return None, None


def get_git_branch(project_root: Path) -> str | None:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def is_git_repo(project_root: Path) -> bool:
    """Check if the directory is a git repository."""
    return (project_root / ".git").exists()


def get_project_context(working_dir: str = ".") -> ProjectContext:
    """
    Get full project context.

    Args:
        working_dir: Starting directory (default: current directory)

    Returns:
        ProjectContext with all gathered information
    """
    project_root = find_project_root(working_dir)

    project_md, _ = load_project_md(project_root)

    return ProjectContext(
        working_dir=str(project_root),
        project_md=project_md,
        git_branch=get_git_branch(project_root),
        git_repo=is_git_repo(project_root),
    )


def build_system_prompt(context: ProjectContext, tools_description: str = "") -> str:
    """
    Build the system prompt with context.

    Args:
        context: Project context
        tools_description: Optional description of available tools

    Returns:
        Complete system prompt
    """
    parts = []

    # Base instructions
    parts.append(
        """You are LunVex Code, an AI coding assistant that helps with software development tasks.

You have access to tools that let you read files, write files, edit files, run commands, and search the codebase.

## Guidelines

### Before making changes:
1. Understand the task fully before acting
2. Read relevant files to understand context
3. Plan your approach

### When editing code:
1. Use edit_file for small changes (preferred) - it's more precise
2. Use write_file only for new files or complete rewrites
3. Run tests after changes when possible
4. If tests fail, analyze the error and iterate

### General principles:
- Be concise but thorough
- Explain your reasoning briefly
- Ask for clarification if the task is ambiguous
- If you're stuck, say so instead of guessing
- Don't make unnecessary changes to files
- Preserve existing code style and conventions"""
    )

    # Add working directory
    parts.append(f"\n## Working Directory\n{context.working_dir}")

    # Add git info
    if context.git_repo:
        branch_info = f" (branch: {context.git_branch})" if context.git_branch else ""
        parts.append(f"\n## Git Repository\nThis is a git repository{branch_info}.")

    # Add project context markdown
    if context.project_md:
        parts.append(f"\n## Project Context (from {APP_CONTEXT_FILENAME})\n\n{context.project_md}")

    return "\n".join(parts)
