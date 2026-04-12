"""Tests for project context loading."""

from pathlib import Path

from lunvex_code.context import APP_CONTEXT_FILENAME, LEGACY_CONTEXT_FILENAME, get_project_context


def test_project_context_prefers_lunvex_md(tmp_path: Path):
    """LUNVEX.md should override the legacy DEEPSEEK.md file."""
    (tmp_path / APP_CONTEXT_FILENAME).write_text("new context", encoding="utf-8")
    (tmp_path / LEGACY_CONTEXT_FILENAME).write_text("old context", encoding="utf-8")

    context = get_project_context(str(tmp_path))

    assert context.project_md == "new context"


def test_project_context_falls_back_to_legacy_deepseek_md(tmp_path: Path):
    """DEEPSEEK.md should still load when LUNVEX.md is missing."""
    (tmp_path / LEGACY_CONTEXT_FILENAME).write_text("legacy context", encoding="utf-8")

    context = get_project_context(str(tmp_path))

    assert context.project_md == "legacy context"
