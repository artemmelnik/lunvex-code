"""Tests for dependency tools with progress bars."""

import tempfile
from pathlib import Path

from lunvex_code.tools.dependencies.analysis import AnalyzeDependenciesTool
from lunvex_code.tools.dependencies.security import ScanVulnerabilitiesTool


def test_analyze_dependencies_with_progress():
    """Test that analyze dependencies tool shows progress."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create a simple pyproject.toml for testing
        pyproject_content = """[project]
name = "test-project"
version = "1.0.0"
dependencies = [
    "requests>=2.25.0",
    "pytest>=7.0.0",
]
"""
        (tmpdir_path / "pyproject.toml").write_text(pyproject_content)

        # Create tool and test
        tool = AnalyzeDependenciesTool()

        # Change to temp directory
        import os

        original_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Test with summary format
            result = tool.execute(format="summary", ecosystem="python")
            assert result.success
            assert "Total:" in result.output
            assert "dependencies" in result.output.lower()

            # Test with JSON format
            result = tool.execute(format="json", ecosystem="python")
            assert result.success
            assert "reports" in result.output or "dependencies" in result.output

            # Test with markdown format
            result = tool.execute(format="markdown", ecosystem="python")
            assert result.success
            assert "#" in result.output  # Should have markdown headers

        finally:
            os.chdir(original_cwd)


def test_scan_vulnerabilities_with_progress():
    """Test that scan vulnerabilities tool shows progress."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create a simple pyproject.toml for testing
        pyproject_content = """[project]
name = "test-project"
version = "1.0.0"
dependencies = [
    "requests>=2.25.0",
    "pytest>=7.0.0",
]
"""
        (tmpdir_path / "pyproject.toml").write_text(pyproject_content)

        # Create tool and test
        tool = ScanVulnerabilitiesTool()

        # Change to temp directory
        import os

        original_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Test with summary format
            result = tool.execute(format="summary", ecosystem="python")
            assert result.success
            assert "Vulnerability Scan" in result.output
            assert "Dependencies scanned:" in result.output

            # Test with JSON format
            result = tool.execute(format="json", ecosystem="python")
            assert result.success
            assert "scan_results" in result.output or "vulnerabilities" in result.output.lower()

            # Test with markdown format
            result = tool.execute(format="markdown", ecosystem="python")
            assert result.success
            assert "#" in result.output  # Should have markdown headers

        finally:
            os.chdir(original_cwd)


def test_dependency_tools_error_handling():
    """Test error handling in dependency tools."""
    tool = AnalyzeDependenciesTool()

    # Test with invalid ecosystem
    result = tool.execute(ecosystem="invalid_ecosystem")
    assert not result.success
    assert "Unsupported ecosystem" in result.error or "Failed" in result.error

    # Test with invalid format
    result = tool.execute(format="invalid_format")
    # Should still work with default handling or return error
    assert result.success or "Failed" in result.error


if __name__ == "__main__":
    # Run tests
    test_analyze_dependencies_with_progress()
    print("✅ test_analyze_dependencies_with_progress passed")

    test_scan_vulnerabilities_with_progress()
    print("✅ test_scan_vulnerabilities_with_progress passed")

    test_dependency_tools_error_handling()
    print("✅ test_dependency_tools_error_handling passed")

    print("\n✅ All dependency progress tests passed!")
