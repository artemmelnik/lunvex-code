"""Dependency visualization tools."""

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .analyzer import DependencyAnalyzer


@dataclass
class VisualizationOptions:
    """Options for dependency visualization."""

    show_versions: bool = True
    show_types: bool = True
    show_vulnerabilities: bool = True
    group_by_type: bool = False
    width: int = 1200
    height: int = 800


class DependencyVisualizer:
    """Visualize dependency relationships."""

    def __init__(self, analyzer: DependencyAnalyzer):
        self.analyzer = analyzer

    def generate_dot_graph(self, options: Optional[VisualizationOptions] = None) -> str:
        """Generate Graphviz DOT format graph."""
        options = options or VisualizationOptions()
        reports = self.analyzer.analyze_all()

        lines = [
            "digraph dependencies {",
            "  rankdir=LR;",
            '  node [shape=box, style=filled, fontname="Helvetica"];',
            '  edge [color="#666666"];',
            "",
        ]

        # Define color schemes
        ecosystem_colors = {
            "python": "#3572A5",
            "javascript": "#f1e05a",
            "rust": "#dea584",
            "go": "#00ADD8",
            "ruby": "#701516",
            "php": "#4F5D95",
        }

        type_colors = {
            "production": "#4CAF50",
            "development": "#2196F3",
            "optional": "#FF9800",
            "peer": "#9C27B0",
        }

        # Add nodes for each dependency
        node_id = 0
        node_map = {}  # dependency name -> node id

        for ecosystem, report in reports.items():
            eco_color = ecosystem_colors.get(ecosystem.value, "#CCCCCC")

            for dep in report.dependencies:
                node_id += 1
                node_map[dep.name] = node_id

                # Build node label
                label_parts = [dep.name]

                if options.show_versions:
                    label_parts.append(f"\\n{dep.version}")

                if options.show_types and dep.dep_type.value != "production":
                    label_parts.append(f"\\n({dep.dep_type.value})")

                label = "".join(label_parts)

                # Determine node color
                fill_color = eco_color

                if options.show_vulnerabilities and dep.has_vulnerabilities:
                    fill_color = "#FF5252"
                elif options.show_types:
                    fill_color = type_colors.get(dep.dep_type.value, eco_color)

                # Node attributes
                attrs = [
                    f'label="{label}"',
                    f'fillcolor="{fill_color}"',
                    'fontcolor="white"',
                ]

                if dep.has_vulnerabilities:
                    attrs.append("penwidth=3")
                    attrs.append('color="#FF0000"')

                if dep.is_outdated:
                    attrs.append('style="filled,dashed"')

                lines.append(f"  node{node_id} [{', '.join(attrs)}];")

        # Group by ecosystem if not grouping by type
        if not options.group_by_type:
            for ecosystem, report in reports.items():
                if report.dependencies:
                    lines.append(f"  subgraph cluster_{ecosystem.value} {{")
                    lines.append(f'    label="{ecosystem.value.title()} Dependencies";')
                    lines.append("    style=filled;")
                    lines.append('    color="#F0F0F0";')

                    for dep in report.dependencies:
                        lines.append(f"    node{node_map[dep.name]};")

                    lines.append("  }")
                    lines.append("")

        # Add legend
        lines.append("  subgraph cluster_legend {")
        lines.append('    label="Legend";')
        lines.append("    style=filled;")
        lines.append('    color="#F8F8F8";')
        lines.append("    fontsize=12;")
        lines.append("    rank=sink;")

        if options.show_types:
            lines.append("    node [shape=plaintext, width=0.5, height=0.3];")
            lines.append('    legend_types [label="Types:\\l')
            for type_name, color in type_colors.items():
                lines.append(f"    {type_name.title()}\\l")
            lines.append('    "];')

        if options.show_vulnerabilities:
            lines.append("    node [shape=plaintext, width=0.5, height=0.3];")
            lines.append('    legend_vulns [label="Vulnerabilities:\\l')
            lines.append("    🔴 Has vulnerabilities\\l")
            lines.append("    ⚪ No vulnerabilities\\l")
            lines.append('    "];')

        lines.append("  }")

        lines.append("}")

        return "\n".join(lines)

    def generate_simple_html(self, options: Optional[VisualizationOptions] = None) -> str:
        """Generate simple HTML visualization."""
        options = options or VisualizationOptions()
        reports = self.analyzer.analyze_all()

        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Dependency Visualization - LunVex Code</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 20px;
        }

        .ecosystem-section {
            margin-bottom: 30px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }

        .ecosystem-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }

        .dependencies-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }

        .dependency-card {
            padding: 10px;
            border-radius: 4px;
            background: white;
            border: 1px solid #ddd;
            position: relative;
        }

        .dependency-name {
            font-weight: bold;
            margin-bottom: 5px;
        }

        .dependency-version {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }

        .dependency-type {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            color: white;
            margin-right: 5px;
        }

        .production { background: #4CAF50; }
        .development { background: #2196F3; }
        .optional { background: #FF9800; }
        .peer { background: #9C27B0; }

        .vulnerability-badge {
            position: absolute;
            top: 5px;
            right: 5px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #FF5252;
        }

        .outdated-badge {
            position: absolute;
            top: 5px;
            right: 20px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #FF9800;
        }

        .legend {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            font-size: 14px;
        }

        .legend-item {
            display: inline-block;
            margin-right: 20px;
        }

        .legend-color {
            display: inline-block;
            width: 15px;
            height: 15px;
            margin-right: 5px;
            vertical-align: middle;
            border-radius: 3px;
        }

        .stats {
            margin-bottom: 20px;
            padding: 15px;
            background: #e8f4fd;
            border-radius: 6px;
        }

        .stat-item {
            display: inline-block;
            margin-right: 20px;
            font-size: 14px;
        }

        .stat-value {
            font-weight: bold;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Dependency Visualization</h1>
        <div class="subtitle">Visual overview of project dependencies</div>

        <div class="stats" id="stats">
            <!-- Stats will be populated by JavaScript -->
        </div>

        <div id="visualization">
            <!-- Visualization will be populated by JavaScript -->
        </div>

        <div class="legend">
            <div class="legend-item">
                <span class="legend-color" style="background: #4CAF50;"></span>
                Production
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #2196F3;"></span>
                Development
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #FF9800;"></span>
                Optional
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #9C27B0;"></span>
                Peer
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #FF5252;"></span>
                Has vulnerabilities
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #FF9800;"></span>
                Outdated
            </div>
        </div>
    </div>

    <script>
        // Dependency data injected by Python
        const dependencyData = {{DEPENDENCY_DATA}};

        // Calculate statistics
        function calculateStats() {
            let totalDeps = 0;
            let vulnerableDeps = 0;
            let outdatedDeps = 0;
            let ecosystems = new Set();

            for (const [ecosystem, deps] of Object.entries(dependencyData)) {
                ecosystems.add(ecosystem);
                totalDeps += deps.length;

                for (const dep of deps) {
                    if (dep.has_vulnerabilities) vulnerableDeps++;
                    if (dep.is_outdated) outdatedDeps++;
                }
            }

            return {
                totalDeps,
                vulnerableDeps,
                outdatedDeps,
                ecosystemCount: ecosystems.size
            };
        }

        // Render statistics
        function renderStats(stats) {
            const statsDiv = document.getElementById('stats');
            statsDiv.innerHTML = `
                <div class="stat-item">
                    <div class="stat-value">${stats.totalDeps}</div>
                    <div>Total Dependencies</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.ecosystemCount}</div>
                    <div>Ecosystems</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.vulnerableDeps}</div>
                    <div>Vulnerable</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.outdatedDeps}</div>
                    <div>Outdated</div>
                </div>
            `;
        }

        // Render visualization
        function renderVisualization() {
            const vizDiv = document.getElementById('visualization');
            let html = '';

            for (const [ecosystem, deps] of Object.entries(dependencyData)) {
                if (deps.length === 0) continue;

                html += `
                    <div class="ecosystem-section">
                        <div class="ecosystem-title">${ecosystem.toUpperCase()} (${deps.length} dependencies)</div>
                        <div class="dependencies-grid">
                `;

                for (const dep of deps) {
                    const typeClass = dep.dep_type.toLowerCase();

                    html += `
                        <div class="dependency-card">
                            ${dep.has_vulnerabilities ? '<div class="vulnerability-badge" title="Has vulnerabilities"></div>' : ''}
                            ${dep.is_outdated ? '<div class="outdated-badge" title="Outdated"></div>' : ''}
                            <div class="dependency-name">${dep.name}</div>
                            <div class="dependency-version">${dep.version}</div>
                            <div>
                                <span class="dependency-type ${typeClass}">${dep.dep_type}</span>
                            </div>
                        </div>
                    `;
                }

                html += `
                        </div>
                    </div>
                `;
            }

            vizDiv.innerHTML = html;
        }

        // Initialize
        const stats = calculateStats();
        renderStats(stats);
        renderVisualization();
    </script>
</body>
</html>
        """

        # Prepare data for JavaScript
        dependency_data = {}
        for ecosystem, report in reports.items():
            dependency_data[ecosystem.value] = [
                {
                    "name": dep.name,
                    "version": dep.version,
                    "dep_type": dep.dep_type.value,
                    "has_vulnerabilities": dep.has_vulnerabilities,
                    "is_outdated": dep.is_outdated,
                }
                for dep in report.dependencies
            ]

        # Inject data into HTML
        html = html.replace("{{DEPENDENCY_DATA}}", json.dumps(dependency_data))

        return html

    def save_visualization(
        self,
        output_path: Path,
        format: str = "html",
        options: Optional[VisualizationOptions] = None,
    ) -> bool:
        """Save visualization to file."""
        try:
            if format == "dot":
                content = self.generate_dot_graph(options)
            elif format == "html":
                content = self.generate_simple_html(options)
            else:
                return False

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True

        except Exception:
            return False

    def open_in_browser(
        self, format: str = "html", options: Optional[VisualizationOptions] = None
    ) -> bool:
        """Generate and open visualization in browser."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=f".{format}", delete=False, encoding="utf-8"
            ) as f:
                if format == "dot":
                    content = self.generate_dot_graph(options)
                elif format == "html":
                    content = self.generate_simple_html(options)
                else:
                    return False

                f.write(content)
                temp_path = f.name

            # Open in browser
            import webbrowser

            webbrowser.open(f"file://{temp_path}")

            return True

        except Exception:
            return False
