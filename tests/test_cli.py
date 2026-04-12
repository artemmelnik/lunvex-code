"""Tests for the CLI surface."""

from typer.testing import CliRunner

from lunvex_code import APP_COMMAND_NAME, APP_DISPLAY_NAME, __version__
from lunvex_code.cli import app

runner = CliRunner()


def test_app_uses_lunvex_command_name():
    """The published CLI should use the Lunvex command name."""
    assert app.info.name == APP_COMMAND_NAME


def test_version_command_uses_lunvex_display_name():
    """The version command should show the Lunvex brand name."""
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert f"{APP_DISPLAY_NAME} v{__version__}" in result.stdout
