"""Dependency analysis tools."""

import json
from pathlib import Path

from lunvex_code.dependencies import DependencyAnalyzer
from ..base import Tool, ToolResult
from ..progress_decorators import with_dependency_progress, ProgressAwareMixin


class AnalyzeDependenciesTool(Tool, ProgressAwareMixin):
    """Analyze project dependencies across different ecosystems."""

    name = "analyze_dependencies"
    description = (
        "Analyze project dependencies across different ecosystems (Python, JavaScript, etc.)"
    )
    permission_level = "auto"  # Read-only operation

    parameters = {
        "format": {
            "type": "string",
            "description": "Output format: 'summary', 'json', or 'markdown'",
            "required": False,
            "default": "summary",
        },
        "ecosystem": {
            "type": "string",
            "description": "Specific ecosystem to analyze (python, javascript, etc.) or 'all' for all",
            "required": False,
            "default": "all",
        },
    }

    @with_dependency_progress("Analyzing dependencies")
    def execute(self, format: str = "summary", ecosystem: str = "all") -> ToolResult:
        try:
            # Get current working directory from context
            # For now, use current directory - we'll integrate with context later
            cwd = Path.cwd()

            analyzer = DependencyAnalyzer(cwd)

            if ecosystem.lower() == "all":
                reports = analyzer.analyze_all()

                if format == "json":
                    # Convert all reports to JSON
                    result = {
                        "reports": {eco.value: report.to_dict() for eco, report in reports.items()}
                    }
                    output = json.dumps(result, indent=2)

                elif format == "markdown":
                    # Generate markdown for all reports
                    output_lines = ["# Dependency Analysis Report", ""]
                    for eco, report in reports.items():
                        output_lines.append(f"## {eco.value.title()}")
                        output_lines.append(report.to_markdown())
                        output_lines.append("")
                    output = "\n".join(output_lines)

                else:  # summary format
                    output = analyzer.generate_summary_report()

            else:
                # Analyze specific ecosystem
                # For MVP, we'll handle Python and JavaScript
                if ecosystem.lower() == "python":
                    report = analyzer.analyze_python()
                elif ecosystem.lower() == "javascript":
                    report = analyzer.analyze_javascript()
                else:
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"Unsupported ecosystem: {ecosystem}. Supported: python, javascript, all",
                    )

                if format == "json":
                    output = json.dumps(report.to_dict(), indent=2)
                elif format == "markdown":
                    output = report.to_markdown()
                else:  # summary
                    output = f"## {ecosystem.title()} Dependencies\n\n"
                    output += f"Total: {report.total_deps}\n"
                    output += f"Outdated: {report.outdated_deps}\n"
                    output += f"Vulnerable: {report.vulnerable_deps}\n\n"

                    if report.dependencies:
                        output += "### Dependencies:\n"
                        for dep in report.dependencies:
                            status = []
                            if dep.is_outdated:
                                status.append("outdated")
                            if dep.has_vulnerabilities:
                                status.append("vulnerable")

                            status_str = f" ({', '.join(status)})" if status else ""
                            output += f"- {dep.name} `{dep.version}`{status_str}\n"

            return ToolResult(
                success=True,
                output=output,
            )

        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to analyze dependencies: {str(e)}"
            )


class ListDependenciesTool(Tool):
    """List all dependencies in the project."""

    name = "list_dependencies"
    description = "List all dependencies in the project with basic information"
    permission_level = "auto"  # Read-only operation

    parameters = {
        "ecosystem": {
            "type": "string",
            "description": "Ecosystem to list (python, javascript, or 'all')",
            "required": False,
            "default": "all",
        },
        "type": {
            "type": "string",
            "description": "Filter by dependency type (production, development, optional, peer, all)",
            "required": False,
            "default": "all",
        },
    }

    def execute(self, ecosystem: str = "all", type: str = "all") -> ToolResult:
        try:
            cwd = Path.cwd()
            analyzer = DependencyAnalyzer(cwd)

            reports = analyzer.analyze_all()

            if not reports:
                return ToolResult(success=True, output="No dependencies found in project.")

            output_lines = ["# Project Dependencies", ""]

            for eco, report in reports.items():
                if ecosystem != "all" and eco.value != ecosystem.lower():
                    continue

                output_lines.append(f"## {eco.value.title()}")
                output_lines.append(f"Total: {report.total_deps} dependencies")
                output_lines.append("")

                # Group by type
                deps_by_type = {}
                for dep in report.dependencies:
                    if type != "all" and dep.dep_type.value != type.lower():
                        continue

                    deps_by_type.setdefault(dep.dep_type.value, []).append(dep)

                for dep_type, deps in deps_by_type.items():
                    if not deps:
                        continue

                    output_lines.append(f"### {dep_type.title()} ({len(deps)})")
                    for dep in sorted(deps, key=lambda d: d.name):
                        status = []
                        if dep.is_outdated:
                            status.append("⚠️")
                        if dep.has_vulnerabilities:
                            status.append("🔴")

                        status_str = " " + " ".join(status) if status else ""
                        output_lines.append(f"- {dep.name} `{dep.version}`{status_str}")

                    output_lines.append("")

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
            )

        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to list dependencies: {str(e)}"
            )