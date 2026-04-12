"""Fixed security vulnerability scanning for dependencies."""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
from packaging import version as pkg_version

from .models import Dependency, Ecosystem, Vulnerability


class VulnerabilitySource(Enum):
    """Sources for vulnerability data."""

    OSV = "osv"  # Open Source Vulnerabilities
    NVD = "nvd"  # National Vulnerability Database
    GITHUB = "github"  # GitHub Advisory Database


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


class FixedVulnerabilityScanner:
    """Fixed scanner for dependency vulnerabilities."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".cache" / "lunvex-code" / "vulnerabilities"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "LunVex-Code/1.0",
                "Accept": "application/json",
            }
        )

    def scan_dependencies(self, dependencies: List[Dependency]) -> VulnerabilityScanResult:
        """Scan a list of dependencies for vulnerabilities."""
        vulnerabilities_by_dep: Dict[str, List[Vulnerability]] = {}

        critical = high = medium = low = 0

        for dep in dependencies:
            vulns = self._scan_dependency(dep)
            if vulns:
                vulnerabilities_by_dep[dep.name] = vulns

                for vuln in vulns:
                    if vuln.severity == "critical":
                        critical += 1
                    elif vuln.severity == "high":
                        high += 1
                    elif vuln.severity == "medium":
                        medium += 1
                    else:
                        low += 1

        return VulnerabilityScanResult(
            dependencies_scanned=len(dependencies),
            vulnerabilities_found=critical + high + medium + low,
            critical_vulnerabilities=critical,
            high_vulnerabilities=high,
            medium_vulnerabilities=medium,
            low_vulnerabilities=low,
            vulnerabilities_by_dependency=vulnerabilities_by_dep,
        )

    def _scan_dependency(self, dependency: Dependency) -> List[Vulnerability]:
        """Scan a single dependency for vulnerabilities."""
        vulnerabilities = []

        # Try OSV API first (free, no API key required)
        osv_vulns = self._check_osv_fixed(dependency)
        vulnerabilities.extend(osv_vulns)

        # Try GitHub Advisory Database
        github_vulns = self._check_github_fixed(dependency)
        vulnerabilities.extend(github_vulns)

        return vulnerabilities

    def _check_osv_fixed(self, dependency: Dependency) -> List[Vulnerability]:
        """Check Open Source Vulnerabilities database with proper filtering."""
        cache_key = f"osv_{dependency.ecosystem.value}_{dependency.name}_{dependency.version}"
        cache_file = self.cache_dir / f"{cache_key}.json"

        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(hours=24):  # Cache for 24 hours
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return self._parse_osv_response_fixed(data, dependency)
                except Exception:
                    pass

        # Map ecosystem to OSV ecosystem
        ecosystem_map = {
            Ecosystem.PYTHON: "PyPI",
            Ecosystem.JAVASCRIPT: "npm",
            Ecosystem.RUST: "crates.io",
            Ecosystem.GO: "Go",
            Ecosystem.RUBY: "RubyGems",
            Ecosystem.PHP: "Packagist",
        }

        osv_ecosystem = ecosystem_map.get(dependency.ecosystem)
        if not osv_ecosystem:
            return []

        try:
            # OSV Query API
            query = {
                "package": {
                    "name": dependency.name,
                    "ecosystem": osv_ecosystem,
                },
                "version": self._extract_base_version(dependency.version),
            }

            response = self.session.post(
                "https://api.osv.dev/v1/query",
                json=query,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()

                # Cache the response
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f)

                return self._parse_osv_response_fixed(data, dependency)

        except Exception:
            pass

        return []

    def _check_github_fixed(self, dependency: Dependency) -> List[Vulnerability]:
        """Check GitHub Advisory Database with proper filtering."""
        cache_key = f"github_{dependency.ecosystem.value}_{dependency.name}"
        cache_file = self.cache_dir / f"{cache_key}.json"

        # Check cache
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(hours=24):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return self._parse_github_response_fixed(data, dependency)
                except Exception:
                    pass

        # Map ecosystem to GitHub ecosystem
        ecosystem_map = {
            Ecosystem.PYTHON: "pip",
            Ecosystem.JAVASCRIPT: "npm",
            Ecosystem.RUST: "cargo",
            Ecosystem.GO: "go",
            Ecosystem.RUBY: "rubygems",
            Ecosystem.PHP: "composer",
        }

        github_ecosystem = ecosystem_map.get(dependency.ecosystem)
        if not github_ecosystem:
            return []

        try:
            # GitHub Advisory API (public, no authentication for read)
            package_name_encoded = quote(dependency.name, safe="")
            url = f"https://api.github.com/advisories?ecosystem={github_ecosystem}&package={package_name_encoded}"

            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Cache the response
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f)

                return self._parse_github_response_fixed(data, dependency)

        except Exception:
            pass

        return []

    def _parse_osv_response_fixed(
        self, data: Dict[str, Any], dependency: Dependency
    ) -> List[Vulnerability]:
        """Parse OSV API response with proper filtering."""
        vulnerabilities = []

        if "vulns" not in data:
            return vulnerabilities

        for vuln_data in data["vulns"]:
            try:
                # Check if this vulnerability affects our specific package
                if not self._is_vulnerability_for_package(vuln_data, dependency):
                    continue

                vuln_id = vuln_data.get("id", "")
                summary = vuln_data.get("summary", "")
                details = vuln_data.get("details", "")
                description = summary or details or "No description available"

                # Check if our version is affected
                if not self._is_version_affected(vuln_data, dependency.version):
                    continue

                # Extract severity
                severity = self._extract_severity(vuln_data)

                # Extract affected versions
                affected_versions = self._extract_affected_versions(vuln_data)

                # Extract references
                references = []
                if "references" in vuln_data:
                    for ref in vuln_data["references"]:
                        if "url" in ref:
                            references.append(ref["url"])

                vulnerability = Vulnerability(
                    id=vuln_id,
                    severity=severity,
                    description=description,
                    affected_versions=affected_versions,
                    fixed_versions=self._extract_fixed_versions(vuln_data),
                    references=references,
                )

                vulnerabilities.append(vulnerability)

            except Exception:
                continue

        return vulnerabilities

    def _parse_github_response_fixed(
        self, data: List[Dict[str, Any]], dependency: Dependency
    ) -> List[Vulnerability]:
        """Parse GitHub Advisory API response with proper filtering."""
        vulnerabilities = []

        if not isinstance(data, list):
            return vulnerabilities

        for advisory in data:
            try:
                # Check if advisory is for our package
                if not self._is_github_advisory_for_package(advisory, dependency):
                    continue

                vuln_id = advisory.get("ghsa_id", "")
                summary = advisory.get("summary", "")
                description = summary or "No description available"

                # Check if our version is affected
                if not self._is_version_affected_github(advisory, dependency.version):
                    continue

                # Extract severity
                severity = advisory.get("severity", "medium").lower()

                # Extract vulnerable version range
                vulnerable_version_range = "Unknown"
                if "vulnerable_version_range" in advisory:
                    vulnerable_version_range = advisory["vulnerable_version_range"]

                # Extract fixed versions
                fixed_versions = []
                if "patched_versions" in advisory:
                    fixed_versions = advisory["patched_versions"]

                # Extract references
                references = []
                if "references" in advisory:
                    for ref in advisory["references"]:
                        if "url" in ref:
                            references.append(ref["url"])

                vulnerability = Vulnerability(
                    id=vuln_id,
                    severity=severity,
                    description=description,
                    affected_versions=vulnerable_version_range,
                    fixed_versions=fixed_versions,
                    references=references,
                )

                vulnerabilities.append(vulnerability)

            except Exception:
                continue

        return vulnerabilities

    def _is_vulnerability_for_package(
        self, vuln_data: Dict[str, Any], dependency: Dependency
    ) -> bool:
        """Check if vulnerability is for our specific package."""
        if "affected" not in vuln_data:
            return False

        for affected in vuln_data["affected"]:
            package_info = affected.get("package", {})
            if package_info.get("name") == dependency.name:
                # Map ecosystem
                ecosystem_map = {
                    "PyPI": Ecosystem.PYTHON,
                    "npm": Ecosystem.JAVASCRIPT,
                    "crates.io": Ecosystem.RUST,
                    "Go": Ecosystem.GO,
                    "RubyGems": Ecosystem.RUBY,
                    "Packagist": Ecosystem.PHP,
                }

                if package_info.get("ecosystem") in ecosystem_map:
                    return ecosystem_map[package_info["ecosystem"]] == dependency.ecosystem

        return False

    def _is_github_advisory_for_package(
        self, advisory: Dict[str, Any], dependency: Dependency
    ) -> bool:
        """Check if GitHub advisory is for our package."""
        # GitHub advisories are already filtered by package in the API query
        # but we double-check here
        package_name = advisory.get("package", {}).get("name", "")
        return package_name.lower() == dependency.name.lower()

    def _is_version_affected(self, vuln_data: Dict[str, Any], version: str) -> bool:
        """Check if our version is affected by the vulnerability."""
        if "affected" not in vuln_data:
            return True  # If no affected info, assume it's affected

        try:
            our_version = pkg_version.parse(self._extract_base_version(version))

            for affected in vuln_data["affected"]:
                if "ranges" not in affected:
                    continue

                for range_data in affected["ranges"]:
                    if range_data.get("type") != "ECOSYSTEM":
                        continue

                    events = range_data.get("events", [])

                    # Simple check: if version is mentioned in events
                    for event in events:
                        if "introduced" in event:
                            intro_version = pkg_version.parse(event["introduced"])
                            if our_version >= intro_version:
                                # Check if fixed
                                if "fixed" in event:
                                    fixed_version = pkg_version.parse(event["fixed"])
                                    if our_version < fixed_version:
                                        return True
                                else:
                                    return True

        except Exception:
            # If we can't parse versions, assume affected
            return True

        return False

    def _is_version_affected_github(self, advisory: Dict[str, Any], version: str) -> bool:
        """Check if our version is affected by GitHub advisory."""
        # GitHub provides vulnerable_version_range which we could parse
        # For now, assume affected if advisory exists for the package
        return True

    def _extract_severity(self, vuln_data: Dict[str, Any]) -> str:
        """Extract severity from vulnerability data."""
        severity = "medium"  # default

        if "severity" in vuln_data:
            for sev in vuln_data["severity"]:
                if sev.get("type") == "CVSS_V3":
                    score = float(sev.get("score", 0))
                    if score >= 9.0:
                        severity = "critical"
                    elif score >= 7.0:
                        severity = "high"
                    elif score >= 4.0:
                        severity = "medium"
                    else:
                        severity = "low"
                    break

        return severity

    def _extract_affected_versions(self, vuln_data: Dict[str, Any]) -> str:
        """Extract affected versions from vulnerability data."""
        affected_ranges = []

        if "affected" in vuln_data:
            for affected in vuln_data["affected"]:
                if "ranges" in affected:
                    for range_data in affected["ranges"]:
                        if "events" in range_data:
                            for event in range_data["events"]:
                                if "introduced" in event:
                                    affected_ranges.append(event["introduced"])

        return ", ".join(affected_ranges) if affected_ranges else "Unknown"

    def _extract_fixed_versions(self, vuln_data: Dict[str, Any]) -> List[str]:
        """Extract fixed versions from vulnerability data."""
        fixed_versions = []

        if "affected" in vuln_data:
            for affected in vuln_data["affected"]:
                if "ranges" in affected:
                    for range_data in affected["ranges"]:
                        if "events" in range_data:
                            for event in range_data["events"]:
                                if "fixed" in event:
                                    fixed_versions.append(event["fixed"])

        return fixed_versions

    def _extract_base_version(self, version_str: str) -> str:
        """Extract base version from version string."""
        # Remove build metadata and local version
        version_str = version_str.split("+")[0]
        version_str = version_str.split("-")[0]
        return version_str
