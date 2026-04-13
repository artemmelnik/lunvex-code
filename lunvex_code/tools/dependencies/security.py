"""Dependency security tools."""

import json
from pathlib import Path

from lunvex_code.dependencies import DependencyAnalyzer
from lunvex_code.dependencies.security import scan_for_vulnerabilities
from ..base import Tool, ToolResult
from ..progress_decorators import with_dependency_progress, ProgressAwareMixin


class ScanVulnerabilitiesTool(Tool, ProgressAwareMixin):
    """Scan dependencies for security vulnerabilities."""

    name = "scan_vulnerabilities"
    description = "Scan project dependencies for security vulnerabilities"
    permission_level = "auto"  # Read-only operation

    parameters = {
        "ecosystem": {
            "type": "string",
            "description": "Ecosystem to scan (python, javascript, rust, go, ruby, php, all)",
            "required": False,
            "default": "all",
        },
        "format": {
            "type": "string",
            "description": "Output format: 'summary', 'json', or 'markdown'",
            "required": False,
            "default": "summary",
        },
    }

    @with_dependency_progress("Scanning for vulnerabilities")
    def execute(self, ecosystem: str = "all", format: str = "summary") -> ToolResult:
        try:
            cwd = Path.cwd()
            analyzer = DependencyAnalyzer(cwd)

            reports = analyzer.analyze_all()

            if not reports:
                return ToolResult(success=True, output="No dependencies found to scan.")

            all_vulnerabilities = {}
            total_deps_scanned = 0

            for eco, report in reports.items():
                if ecosystem != "all" and eco.value != ecosystem.lower():
                    continue

                # Scan dependencies for vulnerabilities
                scanner_result = scan_for_vulnerabilities(report.dependencies)
                all_vulnerabilities[eco.value] = scanner_result
                total_deps_scanned += scanner_result.dependencies_scanned

            if format == "json":
                result = {
                    "scan_results": {
                        eco: result.to_dict() for eco, result in all_vulnerabilities.items()
                    }
                }
                output = json.dumps(result, indent=2)

            elif format == "markdown":
                output_lines = ["# Vulnerability Scan Report", ""]

                for eco, result in all_vulnerabilities.items():
                    output_lines.append(f"## {eco.title()}")
                    output_lines.append(result.to_markdown())
                    output_lines.append("")

                output = "\n".join(output_lines)

            else:  # summary format
                output_lines = ["# Vulnerability Scan Summary", ""]

                total_vulns = 0
                total_critical = 0
                total_high = 0

                for eco, result in all_vulnerabilities.items():
                    output_lines.append(f"## {eco.title()}")
                    output_lines.append(f"- Dependencies scanned: {result.dependencies_scanned}")
                    output_lines.append(f"- Vulnerabilities found: {result.vulnerabilities_found}")

                    if result.vulnerabilities_found > 0:
                        output_lines.append(f"  - 🔴 Critical: {result.critical_vulnerabilities}")
                        output_lines.append(f"  - 🟠 High: {result.high_vulnerabilities}")
                        output_lines.append(f"  - 🟡 Medium: {result.medium_vulnerabilities}")
                        output_lines.append(f"  - 🟢 Low: {result.low_vulnerabilities}")

                    # List vulnerable packages
                    vulnerable_packages = [
                        name
                        for name, vulns in result.vulnerabilities_by_dependency.items()
                        if vulns
                    ]

                    if vulnerable_packages:
                        output_lines.append(f"- Vulnerable packages ({len(vulnerable_packages)}):")
                        for package in sorted(vulnerable_packages)[:5]:  # Show top 5
                            vuln_count = len(result.vulnerabilities_by_dependency[package])
                            severity_counts = {}
                            for vuln in result.vulnerabilities_by_dependency[package]:
                                severity_counts[vuln.severity] = (
                                    severity_counts.get(vuln.severity, 0) + 1
                                )

                            severity_str = ", ".join(
                                [f"{count} {sev}" for sev, count in severity_counts.items()]
                            )
                            output_lines.append(
                                f"  - {package}: {vuln_count} vulnerabilities ({severity_str})"
                            )

                        if len(vulnerable_packages) > 5:
                            output_lines.append(f"  - ... and {len(vulnerable_packages) - 5} more")

                    output_lines.append("")

                    total_vulns += result.vulnerabilities_found
                    total_critical += result.critical_vulnerabilities
                    total_high += result.high_vulnerabilities

                # Overall summary
                output_lines.insert(2, f"**Total dependencies scanned**: {total_deps_scanned}")
                output_lines.insert(3, f"**Total vulnerabilities found**: {total_vulns}")

                if total_vulns > 0:
                    output_lines.insert(4, f"**Critical vulnerabilities**: {total_critical}")
                    output_lines.insert(5, f"**High vulnerabilities**: {total_high}")
                    output_lines.insert(6, "")

                output = "\n".join(output_lines)

            return ToolResult(
                success=True,
                output=output,
            )

        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to scan for vulnerabilities: {str(e)}"
            )