"""Basic tests for security vulnerability scanning."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from lunvex_code.dependencies.models import Dependency, DependencyType, Ecosystem, Vulnerability
from lunvex_code.dependencies.security import VulnerabilityScanner
from lunvex_code.dependencies.security_fixed import FixedVulnerabilityScanner


class TestVulnerabilityScanner(unittest.TestCase):
    """Basic tests for the vulnerability scanner."""

    def test_scanner_initialization(self):
        """Test that the scanner can be initialized."""
        scanner = VulnerabilityScanner()
        assert scanner is not None
        assert hasattr(scanner, "_fixed_scanner")

    def test_fixed_scanner_initialization(self):
        """Test that the fixed scanner can be initialized."""
        scanner = FixedVulnerabilityScanner()
        assert scanner is not None

    def test_scan_empty_dependencies(self):
        """Test scanning an empty list of dependencies."""
        scanner = VulnerabilityScanner()
        result = scanner.scan_dependencies([])

        assert result is not None
        assert hasattr(result, "dependencies_scanned")
        assert hasattr(result, "vulnerabilities_found")
        assert result.dependencies_scanned == 0
        assert result.vulnerabilities_found == 0

    def test_dependency_model(self):
        """Test the Dependency model."""
        dep = Dependency(
            name="requests",
            version="2.33.1",
            ecosystem=Ecosystem.PYTHON,
            dep_type=DependencyType.PRODUCTION,
        )

        assert dep.name == "requests"
        assert dep.version == "2.33.1"
        assert dep.ecosystem == Ecosystem.PYTHON
        assert dep.dep_type == DependencyType.PRODUCTION

    def test_vulnerability_model(self):
        """Test the Vulnerability model."""
        vuln = Vulnerability(
            id="CVE-2024-12345",
            severity="medium",
            description="Test vulnerability",
            affected_versions="<2.33.0",
            fixed_versions=["2.33.0", "2.33.1"],
            references=["https://example.com/cve"],
        )

        assert vuln.id == "CVE-2024-12345"
        assert vuln.severity == "medium"
        assert vuln.description == "Test vulnerability"
        assert vuln.affected_versions == "<2.33.0"
        assert len(vuln.fixed_versions) == 2
        assert len(vuln.references) == 1

    def test_scanner_with_cache_dir(self):
        """Test scanner initialization with cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = VulnerabilityScanner(cache_dir=Path(tmpdir))
            assert scanner is not None

    def test_fixed_scanner_with_cache_dir(self):
        """Test fixed scanner initialization with cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = FixedVulnerabilityScanner(cache_dir=Path(tmpdir))
            assert scanner is not None

    @patch("lunvex_code.dependencies.security_fixed.requests.get")
    def test_mock_scan_dependency(self, mock_get):
        """Test scanning a dependency with mocked API response."""
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"vulns": []}
        mock_get.return_value = mock_response

        scanner = FixedVulnerabilityScanner()

        dep = Dependency(
            name="requests",
            version="2.33.1",
            ecosystem=Ecosystem.PYTHON,
            dep_type=DependencyType.PRODUCTION,
        )

        # This should not raise an exception
        vulnerabilities = scanner._scan_dependency(dep)
        assert isinstance(vulnerabilities, list)

    def test_vulnerability_severity_levels(self):
        """Test vulnerability severity levels."""
        severities = ["low", "medium", "high", "critical"]

        for severity in severities:
            vuln = Vulnerability(
                id=f"TEST-{severity}",
                severity=severity,
                description=f"Test {severity} vulnerability",
                affected_versions="*",
                fixed_versions=["1.0.0"],
            )
            assert vuln.severity == severity

    def test_dependency_to_dict(self):
        """Test converting dependency to dictionary."""
        dep = Dependency(
            name="requests",
            version="2.33.1",
            ecosystem=Ecosystem.PYTHON,
            dep_type=DependencyType.PRODUCTION,
        )

        dep_dict = dep.to_dict()
        assert isinstance(dep_dict, dict)
        assert dep_dict["name"] == "requests"
        assert dep_dict["version"] == "2.33.1"
        assert dep_dict["ecosystem"] == "python"

    def test_vulnerability_attributes(self):
        """Test vulnerability attributes."""
        vuln = Vulnerability(
            id="CVE-2024-12345",
            severity="medium",
            description="Test vulnerability",
            affected_versions="<2.33.0",
            fixed_versions=["2.33.0", "2.33.1"],
            references=["https://example.com/cve"],
        )

        assert vuln.id == "CVE-2024-12345"
        assert vuln.severity == "medium"
        assert vuln.description == "Test vulnerability"
        assert vuln.affected_versions == "<2.33.0"
        assert len(vuln.fixed_versions) == 2
        assert len(vuln.references) == 1


if __name__ == "__main__":
    import unittest

    unittest.main()
