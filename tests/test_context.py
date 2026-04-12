"""Tests for project context loading."""

from pathlib import Path

from lunvex_code.context import APP_CONTEXT_FILENAME, get_project_context


def test_project_context_loads_lunvex_md(tmp_path: Path):
    """LUNVEX.md should be loaded when present."""
    (tmp_path / APP_CONTEXT_FILENAME).write_text("new context", encoding="utf-8")

    context = get_project_context(str(tmp_path))

    assert context.project_md == "new context"


def test_project_context_is_empty_without_lunvex_md(tmp_path: Path):
    """Project context should be empty when LUNVEX.md is missing."""
    context = get_project_context(str(tmp_path))

    assert context.project_md is None
