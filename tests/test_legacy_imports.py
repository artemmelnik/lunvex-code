"""Tests for the legacy ``deepseek_code`` import path."""

import importlib

from lunvex_code.cli import main as lunvex_main


def test_legacy_cli_module_still_resolves():
    """Old console scripts should keep working after the rename."""
    legacy_cli = importlib.import_module("deepseek_code.cli")

    assert legacy_cli.main is lunvex_main


def test_legacy_nested_modules_are_available():
    """Legacy nested imports should resolve to the renamed package modules."""
    legacy_analyzer = importlib.import_module("deepseek_code.dependencies.analyzer")
    current_analyzer = importlib.import_module("lunvex_code.dependencies.analyzer")

    assert legacy_analyzer.DependencyAnalyzer is current_analyzer.DependencyAnalyzer
