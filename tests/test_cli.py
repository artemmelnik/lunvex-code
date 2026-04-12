"""Tests for the CLI surface."""

import builtins

from prompt_toolkit.history import InMemoryHistory
from typer.testing import CliRunner

from lunvex_code import APP_COMMAND_NAME, APP_DISPLAY_NAME, __version__
from lunvex_code.cli import app, get_prompt_session

runner = CliRunner()


def test_app_uses_lunvex_command_name():
    """The published CLI should use the Lunvex command name."""
    assert app.info.name == APP_COMMAND_NAME


def test_version_command_uses_lunvex_display_name():
    """The version command should show the Lunvex brand name."""
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert f"{APP_DISPLAY_NAME} v{__version__}" in result.stdout


def test_run_requires_deepseek_api_key(monkeypatch):
    """The CLI should direct users to the current provider environment variable."""
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = runner.invoke(app, ["run", "hello"])

    assert result.exit_code == 1
    assert result.stdout.count("DEEPSEEK_API_KEY") == 1


def test_prompt_session_falls_back_to_memory_history(monkeypatch):
    """Prompt history should not crash in restricted environments."""

    def deny_history_write(*args, **kwargs):
        raise PermissionError("history is not writable")

    monkeypatch.setattr(builtins, "open", deny_history_write)

    session = get_prompt_session()

    assert isinstance(session.history, InMemoryHistory)
