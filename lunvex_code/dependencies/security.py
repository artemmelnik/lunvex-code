"""Security vulnerability scanning for dependencies."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Dependency, Vulnerability


class VulnerabilitySource(Enum):
    """Sources for vulnerability data."""

    OSV = "osv"  # Open Source Vulnerabilities
    NVD = "nvd"  # National Vulnerability Database
    GITHUB = "github"  # GitHub Advisory Database
    SNYK = "snyk"  # Snyk (requires API key)


@dataclass
class VulnerabilityScanResult:
    """Result of a vulnerability scan."""

    dependencies_scanned: int
    vulnerabilities_found: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    low_vulnerabilities: int
    vulnerabilities_by_dependency: Dict[str, List[Vulnerability]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "dependencies_scanned": self.dependencies_scanned,
            "vulnerabilities_found": self.vulnerabilities_found,
            "severity_breakdown": {
                "critical": self.critical_vulnerabilities,
                "high": self.high_vulnerabilities,
                "medium": self.medium_vulnerabilities,
                "low": self.low_vulnerabilities,
            },
            "vulnerabilities_by_dependency": {
                dep_name: [
                    {
                        "id": vuln.id,
                        "severity": vuln.severity,
                        "description": (
                            vuln.description[:100] + "..."
                            if len(vuln.description) > 100
                            else vuln.description
                        ),
                        "affected_versions": vuln.affected_versions,
                    }
                    for vuln in vulns
                ]
                for dep_name, vulns in self.vulnerabilities_by_dependency.items()
            },
        }

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            "# Vulnerability Scan Report",
            f"**Dependencies Scanned**: {self.dependencies_scanned}",
            f"**Vulnerabilities Found**: {self.vulnerabilities_found}",
            "",
            "## Severity Breakdown",
            f"- 🔴 **Critical**: {self.critical_vulnerabilities}",
            f"- 🟠 **High**: {self.high_vulnerabilities}",
            f"- 🟡 **Medium**: {self.medium_vulnerabilities}",
            f"- 🟢 **Low**: {self.low_vulnerabilities}",
            "",
            "## Vulnerabilities by Dependency",
        ]

        for dep_name, vulns in self.vulnerabilities_by_dependency.items():
            if vulns:
                lines.append(f"### {dep_name}")
                for vuln in vulns:
                    severity_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(vuln.severity, "⚪")

                    lines.append(f"**{severity_emoji} {vuln.id}** ({vuln.severity})")
                    lines.append(f"- **Affected**: {vuln.affected_versions}")
                    lines.append(f"- **Description**: {vuln.description[:200]}...")
                    if vuln.references:
                        lines.append(f"- **References**: {vuln.references[0]}")
                    lines.append("")

        if not self.vulnerabilities_by_dependency or all(
            not v for v in self.vulnerabilities_by_dependency.values()
        ):
            lines.append("✅ No vulnerabilities found!")

        return "\n".join(lines)


class VulnerabilityScanner:
    """Scanner for dependency vulnerabilities."""

    def __init__(self, cache_dir: Optional[Path] = None):
        # Use the fixed scanner internally to avoid false positives
        from .security_fixed import FixedVulnerabilityScanner
        self._fixed_scanner = FixedVulnerabilityScanner(cache_dir)

    def scan_dependencies(self, dependencies: List[Dependency]) -> VulnerabilityScanResult:
        """Scan a list of dependencies for vulnerabilities."""
        return self._fixed_scanner.scan_dependencies(dependencies)

    def _scan_dependency(self, dependency: Dependency) -> List[Vulnerability]:
        """Scan a single dependency for vulnerabilities."""
        return self._fixed_scanner._scan_dependency(dependency)

    # The following methods are kept for backward compatibility
    # but delegate to the fixed scanner implementation

    def _check_osv(self, dependency: Dependency) -> List[Vulnerability]:
        """Check Open Source Vulnerabilities database."""
        return self._fixed_scanner._check_osv_fixed(dependency)

    def _check_github(self, dependency: Dependency) -> List[Vulnerability]:
        """Check GitHub Advisory Database."""
        return self._fixed_scanner._check_github_fixed(dependency)

    def _parse_osv_response(self, data: Dict[str, Any], dependency: Dependency) -> List[Vulnerability]:
        """Parse OSV API response."""
        return self._fixed_scanner._parse_osv_response_fixed(data, dependency)

    def _parse_github_response(self, data: List[Dict[str, Any]], dependency: Dependency) -> List[Vulnerability]:
        """Parse GitHub Advisory API response."""
        return self._fixed_scanner._parse_github_response_fixed(data, dependency)

    def _extract_base_version(self, version_str: str) -> str:
        """Extract base version from version string."""
        return self._fixed_scanner._extract_base_version(version_str)


def scan_for_vulnerabilities(dependencies: List[Dependency]) -> VulnerabilityScanResult:
    """Convenience function to scan dependencies for vulnerabilities."""
    # Use the fixed scanner to avoid false positives
    from .security_fixed import FixedVulnerabilityScanner
    scanner = FixedVulnerabilityScanner()
    return scanner.scan_dependencies(dependencies)
