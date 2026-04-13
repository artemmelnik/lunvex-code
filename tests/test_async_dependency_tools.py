"""Tests for async dependency tools."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_async_dependency_analysis():
    """Test async dependency analysis tool."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create a simple requirements.txt
        (tmpdir_path / "requirements.txt").write_text("pytest>=7.0.0\nrequests==2.28.0\n")

        # Create a simple package.json
        (tmpdir_path / "package.json").write_text("""
        {
          "name": "test-project",
          "dependencies": {
            "react": "^18.0.0",
            "lodash": "~4.17.0"
          },
          "devDependencies": {
            "jest": "^29.0.0"
          }
        }
        """)

        # Test that we can import dependency tools
        # Note: Dependency tools might be sync, but we test in async context

        # Mock the actual analysis to avoid external calls
        with patch("lunvex_code.tools.dependency_tools.analyze_dependencies") as mock_analyze:
            mock_analyze.return_value = {
                "summary": "Found 2 Python packages, 3 JavaScript packages",
                "python": ["pytest>=7.0.0", "requests==2.28.0"],
                "javascript": ["react@^18.0.0", "lodash@~4.17.0", "jest@^29.0.0"],
            }

            # Import and run in async context
            from lunvex_code.tools.dependency_tools import analyze_dependencies

            # Run sync tool in async context
            result = await asyncio.to_thread(
                lambda: analyze_dependencies.execute(format="summary", path=str(tmpdir_path))
            )

            assert result.success
            assert "summary" in result.output.lower() or "python" in result.output.lower()

            # Verify mock was called
            mock_analyze.assert_called_once()


@pytest.mark.asyncio
async def test_async_dependency_list():
    """Test async dependency list tool."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create a simple pyproject.toml
        (tmpdir_path / "pyproject.toml").write_text("""
        [project]
        name = "test-project"
        dependencies = [
            "pytest>=7.0.0",
            "requests==2.28.0"
        ]

        [project.optional-dependencies]
        dev = [
            "black>=23.0.0"
        ]
        """)

        # Mock dependency listing
        with patch("lunvex_code.tools.dependency_tools.list_dependencies") as mock_list:
            mock_list.return_value = {
                "python": [
                    {"name": "pytest", "version": ">=7.0.0", "type": "production"},
                    {"name": "requests", "version": "==2.28.0", "type": "production"},
                    {"name": "black", "version": ">=23.0.0", "type": "development"},
                ]
            }

            from lunvex_code.tools.dependency_tools import list_dependencies

            # Run sync tool in async context
            result = await asyncio.to_thread(
                lambda: list_dependencies.execute(ecosystem="python", path=str(tmpdir_path))
            )

            assert result.success
            assert "pytest" in result.output
            assert "requests" in result.output

            mock_list.assert_called_once_with(ecosystem="python", path=str(tmpdir_path))


@pytest.mark.asyncio
async def test_async_vulnerability_scan():
    """Test async vulnerability scan tool."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create a simple requirements.txt with potentially vulnerable package
        (tmpdir_path / "requirements.txt").write_text("django==3.2.0\nflask==2.0.0\n")

        # Mock vulnerability scan
        with patch("lunvex_code.tools.dependency_tools.scan_vulnerabilities") as mock_scan:
            mock_scan.return_value = {
                "summary": "Found 1 vulnerability",
                "vulnerabilities": [
                    {
                        "package": "django",
                        "version": "3.2.0",
                        "severity": "medium",
                        "advisory": "Cross-site scripting vulnerability",
                    }
                ],
            }

            from lunvex_code.tools.dependency_tools import scan_vulnerabilities

            # Run sync tool in async context
            result = await asyncio.to_thread(
                lambda: scan_vulnerabilities.execute(
                    ecosystem="python", format="summary", path=str(tmpdir_path)
                )
            )

            assert result.success
            assert "vulnerability" in result.output.lower() or "django" in result.output.lower()

            mock_scan.assert_called_once()


@pytest.mark.asyncio
async def test_async_dependency_update():
    """Test async dependency update tool."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create requirements.txt
        (tmpdir_path / "requirements.txt").write_text("pytest==7.0.0\nrequests==2.28.0\n")

        # Mock dependency update
        with patch("lunvex_code.tools.dependency_tools.update_dependency") as mock_update:
            mock_update.return_value = {
                "success": True,
                "message": "Updated pytest from 7.0.0 to 7.4.0",
                "package": "pytest",
                "old_version": "7.0.0",
                "new_version": "7.4.0",
            }

            from lunvex_code.tools.dependency_tools import update_dependency

            # Run sync tool in async context
            result = await asyncio.to_thread(
                lambda: update_dependency.execute(
                    package="pytest", version="7.4.0", ecosystem="python", path=str(tmpdir_path)
                )
            )

            assert result.success
            assert "updated" in result.output.lower() or "pytest" in result.output.lower()

            mock_update.assert_called_once_with(
                package="pytest", version="7.4.0", ecosystem="python", path=str(tmpdir_path)
            )


@pytest.mark.asyncio
async def test_async_dependency_concurrent_operations():
    """Test concurrent dependency operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create multiple dependency files
        (tmpdir_path / "requirements.txt").write_text("pytest\nrequests\n")
        (tmpdir_path / "package.json").write_text('{"dependencies": {"react": "^18.0.0"}}')

        # Mock functions
        with patch("lunvex_code.tools.dependency_tools.analyze_dependencies") as mock_analyze:
            mock_analyze.return_value = {"summary": "Test analysis"}

            with patch("lunvex_code.tools.dependency_tools.list_dependencies") as mock_list:
                mock_list.return_value = {
                    "python": [{"name": "pytest", "version": "", "type": "production"}]
                }

                from lunvex_code.tools.dependency_tools import (
                    analyze_dependencies,
                    list_dependencies,
                )

                # Run concurrent operations
                tasks = [
                    asyncio.to_thread(
                        lambda: analyze_dependencies.execute(
                            format="summary", path=str(tmpdir_path)
                        )
                    ),
                    asyncio.to_thread(
                        lambda: list_dependencies.execute(ecosystem="python", path=str(tmpdir_path))
                    ),
                ]

                results = await asyncio.gather(*tasks)

                # Verify both succeeded
                for result in results:
                    assert result.success

                # Verify mocks were called
                assert mock_analyze.called
                assert mock_list.called


@pytest.mark.asyncio
async def test_async_dependency_error_handling():
    """Test dependency tool error handling in async context."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # No dependency files

        from lunvex_code.tools.dependency_tools import analyze_dependencies

        # Run sync tool in async context
        result = await asyncio.to_thread(
            lambda: analyze_dependencies.execute(format="summary", path=str(tmpdir_path))
        )

        # Should succeed even with no dependencies (empty analysis)
        assert result.success
        assert (
            "analysis" in result.output.lower()
            or "dependencies" in result.output.lower()
            or "summary" in result.output.lower()
        )


if __name__ == "__main__":
    # Run tests
    import sys

    async def run_all_tests():
        """Run all async dependency tool tests."""
        tests = [
            test_async_dependency_analysis,
            test_async_dependency_list,
            test_async_vulnerability_scan,
            test_async_dependency_update,
            test_async_dependency_concurrent_operations,
            test_async_dependency_error_handling,
        ]

        passed = 0
        failed = 0

        for test in tests:
            print(f"\n{'=' * 60}")
            print(f"Running: {test.__name__}")
            print("=" * 60)

            try:
                await test()
                print(f"✅ {test.__name__} PASSED")
                passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} FAILED: {e}")
                import traceback

                traceback.print_exc()
                failed += 1

        print(f"\n{'=' * 60}")
        print(f"TEST SUMMARY: {passed} passed, {failed} failed")
        print("=" * 60)

        return failed == 0

    # Run async tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
