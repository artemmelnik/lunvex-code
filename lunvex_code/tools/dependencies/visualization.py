"""Dependency visualization tools."""

import tempfile
from pathlib import Path
from typing import Optional

from lunvex_code.dependencies import DependencyAnalyzer
from lunvex_code.dependencies.visualizer import DependencyVisualizer

from ..base import Tool, ToolResult


class VisualizeDependenciesTool(Tool):
    """Visualize project dependencies."""

    name = "visualize_dependencies"
    description = "Visualize project dependencies as a graph or interactive HTML"
    permission_level = "auto"  # Read-only operation

    parameters = {
        "format": {
            "type": "string",
            "description": "Output format: 'dot' (Graphviz), 'html' (interactive), or 'summary'",
            "required": False,
            "default": "summary",
        },
        "output_file": {
            "type": "string",
            "description": "Path to save visualization file (optional)",
            "required": False,
        },
        "open_browser": {
            "type": "boolean",
            "description": "Open visualization in browser (HTML format only)",
            "required": False,
            "default": False,
        },
    }

    def execute(
        self, format: str = "summary", output_file: Optional[str] = None, open_browser: bool = False
    ) -> ToolResult:
        try:
            cwd = Path.cwd()
            analyzer = DependencyAnalyzer(cwd)

            visualizer = DependencyVisualizer(analyzer)

            if format == "dot":
                dot_content = visualizer.generate_dot_graph()

                if output_file:
                    output_path = Path(output_file)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(dot_content)

                    output = f"Graphviz DOT file saved to: {output_path}\n"
                    output += "You can render it with: dot -Tpng -o graph.png graph.dot"
                else:
                    output = dot_content

            elif format == "html":
                if output_file:
                    output_path = Path(output_file)
                    success = visualizer.save_visualization(output_path, format="html")

                    if success:
                        output = f"HTML visualization saved to: {output_path}\n"

                        if open_browser:
                            import webbrowser

                            webbrowser.open(f"file://{output_path.absolute()}")
                            output += "Opened in browser."
                        else:
                            output += "Open it in your browser to view the visualization."
                    else:
                        return ToolResult(
                            success=False,
                            output="",
                            error=f"Failed to save HTML visualization to {output_file}",
                        )
                elif open_browser:
                    success = visualizer.open_in_browser(format="html")

                    if success:
                        output = "Opening interactive visualization in browser..."
                    else:
                        return ToolResult(
                            success=False,
                            output="",
                            error="Failed to open visualization in browser",
                        )
                else:
                    # Generate HTML but don't save
                    html_content = visualizer.generate_simple_html()

                    # Save to temp file
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".html", delete=False, encoding="utf-8"
                    ) as f:
                        f.write(html_content)
                        temp_path = f.name

                    output = f"HTML visualization generated at: {temp_path}\n"
                    output += "Open this file in your browser to view the visualization."

            else:  # summary format
                reports = analyzer.analyze_all()

                if not reports:
                    return ToolResult(success=True, output="No dependencies found to visualize.")

                output_lines = ["# Dependency Visualization Summary", ""]

                for ecosystem, report in reports.items():
                    output_lines.append(f"## {ecosystem.value.title()} Dependencies")
                    output_lines.append(f"Total: {report.total_deps} dependencies")

                    if report.dependencies:
                        # Group by type for visualization
                        deps_by_type = {}
                        for dep in report.dependencies:
                            deps_by_type.setdefault(dep.dep_type.value, []).append(dep)

                        for dep_type, deps in deps_by_type.items():
                            output_lines.append(f"### {dep_type.title()} ({len(deps)})")

                            # Show first few dependencies
                            for dep in deps[:5]:
                                status = []
                                if dep.has_vulnerabilities:
                                    status.append("🔴")
                                if dep.is_outdated:
                                    status.append("⚠️")

                                status_str = " " + " ".join(status) if status else ""
                                output_lines.append(f"- {dep.name} `{dep.version}`{status_str}")

                            if len(deps) > 5:
                                output_lines.append(f"- ... and {len(deps) - 5} more")

                        output_lines.append("")

                output_lines.append("## Visualization Options")
                output_lines.append("")
                output_lines.append("To create visualizations, use:")
                output_lines.append(
                    '- `visualize_dependencies(format="dot")` - Graphviz DOT format'
                )
                output_lines.append(
                    '- `visualize_dependencies(format="html", open_browser=true)` - Interactive HTML'
                )
                output_lines.append("")
                output_lines.append("Example commands:")
                output_lines.append('- "visualize dependencies as graphviz dot"')
                output_lines.append('- "create interactive dependency graph"')

                output = "\n".join(output_lines)

            return ToolResult(
                success=True,
                output=output,
            )

        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to visualize dependencies: {str(e)}"
            )
