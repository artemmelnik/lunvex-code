"""Tests for dependency management functionality."""

import json

import pytest

from lunvex_code.dependencies.analyzer import DependencyAnalyzer
from lunvex_code.dependencies.config import DependencyConfig, UpdateLevel
from lunvex_code.dependencies.models import DependencyType, Ecosystem
from lunvex_code.tools.dependency_tools import (
    AnalyzeDependenciesTool,
    CheckDependencyConfigTool,
    ListDependenciesTool,
)


class TestDependencyModels:
    """Test dependency data models."""

    def test_dependency_to_dict(self):
        """Test Dependency to_dict method."""
        from lunvex_code.dependencies.models import Dependency

        dep = Dependency(
            name="requests",
            version=">=2.28.0",
            ecosystem=Ecosystem.PYTHON,
            dep_type=DependencyType.PRODUCTION,
            license="Apache-2.0",
            homepage="https://docs.python-requests.org/",
            description="Python HTTP for Humans.",
            latest_version="2.31.0",
            is_outdated=True,
            has_vulnerabilities=False,
        )

        data = dep.to_dict()

        assert data["name"] == "requests"
        assert data["version"] == ">=2.28.0"
        assert data["ecosystem"] == "python"
        assert data["type"] == "production"
        assert data["license"] == "Apache-2.0"
        assert data["is_outdated"] is True
        assert data["has_vulnerabilities"] is False
        assert data["vulnerability_count"] == 0

    def test_dependency_report_summary(self):
        """Test DependencyReport summary calculations."""
        from lunvex_code.dependencies.models import Dependency, DependencyReport

        deps = [
            Dependency(name="dep1", version="1.0.0", ecosystem=Ecosystem.PYTHON),
            Dependency(name="dep2", version="2.0.0", ecosystem=Ecosystem.PYTHON, is_outdated=True),
            Dependency(
                name="dep3", version="3.0.0", ecosystem=Ecosystem.PYTHON, has_vulnerabilities=True
            ),
        ]

        report = DependencyReport(
            ecosystem=Ecosystem.PYTHON,
            dependencies=deps,
        )

        assert report.total_deps == 3
        assert report.outdated_deps == 1
        assert report.vulnerable_deps == 1


class TestDependencyConfig:
    """Test dependency configuration."""

    def test_default_config(self):
        """Test default configuration creation."""
        config = DependencyConfig()

        assert config.security.scan_on_change is True
        assert config.security.fail_on_critical is False
        assert "MIT" in config.security.allowed_licenses
        assert "GPL-3.0" in config.security.blocked_licenses

        assert config.updates.enabled is True
        assert config.updates.level == UpdateLevel.PATCH
        assert config.updates.auto_apply is False

    def test_config_serialization(self, tmp_path):
        """Test configuration save/load."""
        config = DependencyConfig()
        config_path = tmp_path / "test-config.yaml"

        # Save config
        config.save(config_path)
        assert config_path.exists()

        # Load config
        loaded_config = DependencyConfig.from_file(config_path)

        assert loaded_config.security.scan_on_change == config.security.scan_on_change
        assert loaded_config.updates.level == config.updates.level

    def test_license_checking(self):
        """Test license allowance checking."""
        config = DependencyConfig()

        # Allowed licenses
        assert config.is_license_allowed("MIT") is True
        assert config.is_license_allowed("Apache-2.0") is True

        # Blocked licenses
        assert config.is_license_allowed("GPL-3.0") is False
        assert config.is_license_allowed("AGPL-3.0") is False

        # Unknown license (allowed by default)
        assert config.is_license_allowed("Custom License") is True

        # Case insensitive
        assert config.is_license_allowed("mit license") is True
        assert config.is_license_allowed("gpl-3.0-only") is False


class TestDependencyAnalyzer:
    """Test dependency analyzer."""

    def test_ecosystem_detection(self, tmp_path):
        """Test ecosystem detection."""
        # Create test files
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "package.json").write_text('{"name": "test"}')

        analyzer = DependencyAnalyzer(tmp_path)
        ecosystems = analyzer.detect_ecosystem()

        assert Ecosystem.PYTHON in ecosystems
        assert Ecosystem.JAVASCRIPT in ecosystems

    def test_python_analysis_pyproject(self, tmp_path):
        """Test Python analysis with pyproject.toml."""
        pyproject_content = """
[project]
name = "test-project"
dependencies = [
    "requests>=2.28.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
]
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        analyzer = DependencyAnalyzer(tmp_path)
        report = analyzer.analyze_python()

        assert report.ecosystem == Ecosystem.PYTHON
        assert report.total_deps == 3

        dep_names = {dep.name for dep in report.dependencies}
        assert "requests" in dep_names
        assert "pydantic" in dep_names
        assert "pytest" in dep_names

        # Check dependency types
        for dep in report.dependencies:
            if dep.name == "pytest":
                assert dep.dep_type == DependencyType.OPTIONAL
            else:
                assert dep.dep_type == DependencyType.PRODUCTION

    def test_javascript_analysis(self, tmp_path):
        """Test JavaScript analysis."""
        package_json = {
            "name": "test",
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "^4.17.0",
            },
            "devDependencies": {
                "jest": "^29.0.0",
            },
            "peerDependencies": {
                "react": "^18.0.0",
            },
        }

        (tmp_path / "package.json").write_text(json.dumps(package_json))

        analyzer = DependencyAnalyzer(tmp_path)
        report = analyzer.analyze_javascript()

        assert report.ecosystem == Ecosystem.JAVASCRIPT
        assert report.total_deps == 4

        # Check dependency types
        type_counts = {}
        for dep in report.dependencies:
            type_counts[dep.dep_type] = type_counts.get(dep.dep_type, 0) + 1

        assert type_counts.get(DependencyType.PRODUCTION, 0) == 2
        assert type_counts.get(DependencyType.DEVELOPMENT, 0) == 1
        assert type_counts.get(DependencyType.PEER, 0) == 1


class TestDependencyTools:
    """Test dependency tools."""

    @pytest.fixture
    def test_project(self, tmp_path):
        """Create a test project with dependencies."""
        # Python dependencies
        pyproject = """
[project]
name = "test"
dependencies = ["requests>=2.28.0"]
"""
        (tmp_path / "pyproject.toml").write_text(pyproject)

        # JavaScript dependencies
        package_json = {"name": "test", "dependencies": {"express": "^4.18.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_json))

        return tmp_path

    def test_analyze_dependencies_tool(self, test_project, monkeypatch):
        """Test AnalyzeDependenciesTool."""
        # Mock current directory
        monkeypatch.chdir(test_project)

        tool = AnalyzeDependenciesTool()

        # Test summary format
        result = tool.execute(format="summary")
        assert result.success is True
        assert "Python" in result.output
        assert "Javascript" in result.output
        assert "requests" in result.output
        assert "express" in result.output

        # Test JSON format
        result = tool.execute(format="json")
        assert result.success is True

        data = json.loads(result.output)
        assert "reports" in data
        assert "python" in data["reports"]
        assert "javascript" in data["reports"]

    def test_list_dependencies_tool(self, test_project, monkeypatch):
        """Test ListDependenciesTool."""
        monkeypatch.chdir(test_project)

        tool = ListDependenciesTool()

        # List all
        result = tool.execute()
        assert result.success is True
        assert "Python" in result.output
        assert "Javascript" in result.output

        # List only Python
        result = tool.execute(ecosystem="python")
        assert result.success is True
        assert "Python" in result.output
        assert "Javascript" not in result.output

        # List only production
        result = tool.execute(type="production")
        assert result.success is True
        # Should list requests and express

    def test_check_dependency_config_tool(self, test_project, monkeypatch):
        """Test CheckDependencyConfigTool."""
        monkeypatch.chdir(test_project)

        tool = CheckDependencyConfigTool()

        # Check without creating (should say not found)
        result = tool.execute(create_if_missing=False)
        assert result.success is True
        assert "No dependency configuration found" in result.output

        # Check with creating
        result = tool.execute(create_if_missing=True)
        assert result.success is True
        assert "Created default configuration" in result.output

        # Verify file was created
        config_path = test_project / ".lunvex-deps.yaml"
        assert config_path.exists()

        # Check again (should show config)
        result = tool.execute(create_if_missing=False)
        assert result.success is True
        assert "Configuration loaded from" in result.output
