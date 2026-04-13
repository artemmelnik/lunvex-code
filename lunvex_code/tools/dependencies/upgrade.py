"""Dependency upgrade tools."""

from pathlib import Path

from lunvex_code.dependencies import DependencyAnalyzer

from ..base import Tool, ToolResult


class UpgradeDependenciesTool(Tool):
    """Upgrade all dependencies to their latest versions."""

    name = "upgrade_dependencies"
    description = "Upgrade all dependencies to their latest versions"
    permission_level = "ask"  # Modifies files

    parameters = {
        "ecosystem": {
            "type": "string",
            "description": "Ecosystem to upgrade (python, javascript, rust, go, ruby, php, all)",
            "required": False,
            "default": "all",
        },
        "level": {
            "type": "string",
            "description": "Upgrade level: patch, minor, or major",
            "required": False,
            "default": "patch",
        },
    }

    def execute(self, ecosystem: str = "all", level: str = "patch") -> ToolResult:
        try:
            cwd = Path.cwd()
            analyzer = DependencyAnalyzer(cwd)

            reports = analyzer.analyze_all()

            if not reports:
                return ToolResult(success=True, output="No dependencies found to upgrade.")

            output_lines = ["# Dependency Upgrade Report", ""]
            upgraded_count = 0

            for eco, report in reports.items():
                if ecosystem != "all" and eco.value != ecosystem.lower():
                    continue

                output_lines.append(f"## {eco.value.title()}")

                if not report.dependencies:
                    output_lines.append("No dependencies found.")
                    output_lines.append("")
                    continue

                # For MVP, we'll just report what would be upgraded
                # In a real implementation, we would:
                # 1. Check latest versions from package registries
                # 2. Apply updates based on semver and level
                # 3. Update dependency files

                upgradable = []
                for dep in report.dependencies:
                    if dep.is_outdated:
                        upgradable.append(dep.name)

                if upgradable:
                    output_lines.append(f"Dependencies that could be upgraded ({level} level):")
                    for name in sorted(upgradable):
                        output_lines.append(f"- {name}")
                        upgraded_count += 1
                else:
                    output_lines.append("All dependencies are up to date.")

                output_lines.append("")

            if upgraded_count > 0:
                output_lines.append(f"**Total: {upgraded_count} dependencies could be upgraded**")
                output_lines.append("")
                output_lines.append("Note: This is a preview. To actually upgrade dependencies,")
                output_lines.append("use the `update_dependency` tool for specific packages.")
            else:
                output_lines.append("✅ All dependencies are up to date!")

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
            )

        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to check for dependency upgrades: {str(e)}"
            )
