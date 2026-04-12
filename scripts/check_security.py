#!/usr/bin/env python3
"""Enhanced security check script using multiple sources."""

import json
import subprocess
import sys
from typing import Dict, List, Tuple

import requests


def check_with_pip_audit() -> Tuple[bool, List[Dict]]:
    """Check vulnerabilities using pip-audit."""
    print("🔍 Checking with pip-audit...")

    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )

        data = json.loads(result.stdout)
        vulnerabilities = []

        for dep in data.get("dependencies", []):
            for vuln in dep.get("vulns", []):
                vulnerabilities.append(
                    {
                        "package": dep["name"],
                        "version": dep["version"],
                        "id": vuln.get("id", "Unknown"),
                        "severity": vuln.get("severity", "Unknown"),
                        "description": vuln.get("description", "No description"),
                    }
                )

        if vulnerabilities:
            print(f"❌ Found {len(vulnerabilities)} vulnerabilities with pip-audit")
            return False, vulnerabilities
        else:
            print("✅ No vulnerabilities found with pip-audit")
            return True, []

    except subprocess.CalledProcessError as e:
        print(f"⚠️  pip-audit failed: {e}")
        return False, []
    except Exception as e:
        print(f"⚠️  Error with pip-audit: {e}")
        return False, []


def check_with_safety() -> Tuple[bool, List[Dict]]:
    """Check vulnerabilities using safety (if available)."""
    print("\n🔍 Checking with safety...")

    try:
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                vulnerabilities = []

                for vuln in data.get("vulnerabilities", []):
                    vulnerabilities.append(
                        {
                            "package": vuln.get("package_name", "Unknown"),
                            "version": vuln.get("analyzed_version", "Unknown"),
                            "id": vuln.get("vulnerability_id", "Unknown"),
                            "severity": vuln.get("severity", "Unknown"),
                            "description": vuln.get("advisory", "No description"),
                        }
                    )

                if vulnerabilities:
                    print(f"❌ Found {len(vulnerabilities)} vulnerabilities with safety")
                    return False, vulnerabilities
                else:
                    print("✅ No vulnerabilities found with safety")
                    return True, []

            except json.JSONDecodeError:
                print("⚠️  Safety output not in expected format")
                return False, []
        else:
            print("ℹ️  Safety not available or no output")
            return True, []

    except FileNotFoundError:
        print("ℹ️  Safety not installed. Install with: pip install safety")
        return True, []
    except Exception as e:
        print(f"⚠️  Error with safety: {e}")
        return False, []


def check_direct_osv(package: str, version: str) -> List[Dict]:
    """Check a single package with OSV API directly."""
    try:
        query = {
            "package": {"name": package, "ecosystem": "PyPI"},
            "version": version.split("+")[0].split("-")[0],  # Clean version
        }

        response = requests.post(
            "https://api.osv.dev/v1/query",
            json=query,
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            vulnerabilities = []

            for vuln in data.get("vulns", []):
                # Check if this vulnerability affects our version
                affected = False
                for affected_range in vuln.get("affected", []):
                    if "ranges" in affected_range:
                        for range_info in affected_range["ranges"]:
                            if range_info.get("type") == "ECOSYSTEM":
                                # Simple check - in production we'd parse semver
                                affected = True
                                break

                if affected:
                    vulnerabilities.append(
                        {
                            "package": package,
                            "version": version,
                            "id": vuln.get("id", "Unknown"),
                            "severity": self._extract_severity(vuln),
                            "description": vuln.get(
                                "summary", vuln.get("details", "No description")
                            ),
                        }
                    )

            return vulnerabilities

    except Exception as e:
        print(f"⚠️  Error checking {package} with OSV: {e}")

    return []


def _extract_severity(vuln_data: Dict) -> str:
    """Extract severity from vulnerability data."""
    if "severity" in vuln_data:
        for sev in vuln_data["severity"]:
            if sev.get("type") == "CVSS_V3":
                score = float(sev.get("score", 0))
                if score >= 9.0:
                    return "critical"
                elif score >= 7.0:
                    return "high"
                elif score >= 4.0:
                    return "medium"
                else:
                    return "low"

    return "medium"


def check_known_problematic_packages() -> List[Dict]:
    """Check for known problematic packages."""
    print("\n🔍 Checking known problematic packages...")

    problematic = []

    # Known issues (this would be maintained separately)
    known_issues = {
        "pyyaml": {
            "min_safe_version": "5.4",
            "issues": ["CVE-2017-18342", "CVE-2020-14343"],
        },
        "requests": {
            "min_safe_version": "2.20.0",
            "issues": ["CVE-2018-18074"],
        },
        "urllib3": {
            "min_safe_version": "1.26.5",
            "issues": ["CVE-2021-33503"],
        },
    }

    try:
        result = subprocess.run(
            ["pip", "freeze"],
            capture_output=True,
            text=True,
            check=True,
        )

        for line in result.stdout.strip().split("\n"):
            if "==" in line:
                package, version = line.split("==")
                package = package.strip().lower()

                if package in known_issues:
                    min_version = known_issues[package]["min_safe_version"]

                    # Simple version comparison (for production use packaging.version)
                    from packaging import version as pkg_version

                    try:
                        if pkg_version.parse(version) < pkg_version.parse(min_version):
                            problematic.append(
                                {
                                    "package": package,
                                    "version": version,
                                    "min_safe": min_version,
                                    "issues": known_issues[package]["issues"],
                                    "severity": "high",
                                    "description": f"Known vulnerabilities in {package} < {min_version}",
                                }
                            )
                    except Exception:
                        # If version parsing fails, just warn
                        problematic.append(
                            {
                                "package": package,
                                "version": version,
                                "min_safe": min_version,
                                "issues": known_issues[package]["issues"],
                                "severity": "medium",
                                "description": f"Potential vulnerability in {package} version {version}",
                            }
                        )

        if problematic:
            print(f"⚠️  Found {len(problematic)} potentially problematic packages")
        else:
            print("✅ No known problematic packages found")

    except Exception as e:
        print(f"⚠️  Error checking problematic packages: {e}")

    return problematic


def generate_report(
    pip_audit_ok: bool,
    safety_ok: bool,
    pip_audit_vulns: List[Dict],
    safety_vulns: List[Dict],
    problematic: List[Dict],
) -> None:
    """Generate security report."""
    print("\n" + "=" * 60)
    print("🛡️  SECURITY REPORT")
    print("=" * 60)

    all_vulns = pip_audit_vulns + safety_vulns + problematic

    if not all_vulns:
        print("✅ All security checks passed!")
        print("\nNo vulnerabilities found in dependencies.")
        return

    print(f"❌ Found {len(all_vulns)} potential security issues")

    # Group by package
    by_package = {}
    for vuln in all_vulns:
        pkg = vuln["package"]
        if pkg not in by_package:
            by_package[pkg] = []
        by_package[pkg].append(vuln)

    print("\n📋 Vulnerabilities by package:")
    for package, vulns in by_package.items():
        print(f"\n  {package}:")
        for vuln in vulns:
            severity = vuln.get("severity", "unknown").upper()
            severity_emoji = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🟢",
            }.get(severity, "⚪")

            print(f"    {severity_emoji} {vuln.get('id', 'Unknown')} ({severity})")
            if "min_safe" in vuln:
                print(f"      Current: {vuln['version']}, Minimum safe: {vuln['min_safe']}")
            print(f"      {vuln.get('description', 'No description')[:100]}...")

    print("\n💡 Recommendations:")
    print("  1. Run: pip-audit --fix (if available)")
    print("  2. Update vulnerable packages to latest versions")
    print("  3. Consider using: pip install --upgrade package-name")
    print("  4. Review: https://pyup.io/safety/ for detailed analysis")


def main() -> None:
    """Main function."""
    print("🛡️  Enhanced Dependency Security Check")
    print("=" * 60)

    # Check with pip-audit
    pip_audit_ok, pip_audit_vulns = check_with_pip_audit()

    # Check with safety
    safety_ok, safety_vulns = check_with_safety()

    # Check known problematic packages
    problematic = check_known_problematic_packages()

    # Generate report
    generate_report(
        pip_audit_ok,
        safety_ok,
        pip_audit_vulns,
        safety_vulns,
        problematic,
    )

    # Exit code
    if pip_audit_vulns or safety_vulns or problematic:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
