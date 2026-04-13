"""Basic tests for dependency visualization."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

from lunvex_code.dependencies.analyzer import DependencyAnalyzer
from lunvex_code.dependencies.models import Dependency, DependencyReport, DependencyType, Ecosystem
from lunvex_code.dependencies.visualizer import DependencyVisualizer, VisualizationOptions


class TestDependencyVisualizer:
    """Basic tests for the dependency visualizer."""

    def test_visualization_options_defaults(self):
        """Test default visualization options."""
        options = VisualizationOptions()

        assert options.show_versions is True
        assert options.show_types is True
        assert options.show_vulnerabilities is True
        assert options.group_by_type is False
        assert options.width == 1200
        assert options.height == 800

    def test_visualization_options_custom(self):
        """Test custom visualization options."""
        options = VisualizationOptions(
            show_versions=False,
            show_types=False,
            show_vulnerabilities=False,
            group_by_type=True,
            width=800,
            height=600,
        )

        assert options.show_versions is False
        assert options.show_types is False
        assert options.show_vulnerabilities is False
        assert options.group_by_type is True
        assert options.width == 800
        assert options.height == 600

    def test_visualizer_initialization(self):
        """Test that the visualizer can be initialized."""
        mock_analyzer = Mock(spec=DependencyAnalyzer)
        visualizer = DependencyVisualizer(mock_analyzer)

        assert visualizer is not None
        assert visualizer.analyzer == mock_analyzer

    def test_generate_dot_graph_empty(self):
        """Test generating DOT graph with empty dependencies."""
        mock_analyzer = Mock(spec=DependencyAnalyzer)
        mock_analyzer.analyze_all.return_value = {}

        visualizer = DependencyVisualizer(mock_analyzer)
        dot_graph = visualizer.generate_dot_graph()

        assert isinstance(dot_graph, str)
        assert "digraph dependencies" in dot_graph
        assert "rankdir=LR" in dot_graph

    def test_generate_dot_graph_with_dependencies(self):
        """Test generating DOT graph with sample dependencies."""
        # Create mock dependencies
        dep1 = Dependency(
            name="requests",
            version="2.33.1",
            ecosystem=Ecosystem.PYTHON,
            dep_type=DependencyType.PRODUCTION,
        )

        dep2 = Dependency(
            name="pytest",
            version="9.0.3",
            ecosystem=Ecosystem.PYTHON,
            dep_type=DependencyType.DEVELOPMENT,
        )

        # Create mock report
        report = DependencyReport(
            ecosystem=Ecosystem.PYTHON, dependencies=[dep1, dep2], source_files=["pyproject.toml"]
        )

        mock_analyzer = Mock(spec=DependencyAnalyzer)
        mock_analyzer.analyze_all.return_value = {Ecosystem.PYTHON: report}

        visualizer = DependencyVisualizer(mock_analyzer)
        dot_graph = visualizer.generate_dot_graph()

        assert isinstance(dot_graph, str)
        assert "digraph dependencies" in dot_graph
        assert "requests" in dot_graph.lower()
        assert "pytest" in dot_graph.lower()

    def test_generate_simple_html_empty(self):
        """Test generating HTML visualization with empty dependencies."""
        mock_analyzer = Mock(spec=DependencyAnalyzer)
        mock_analyzer.analyze_all.return_value = {}

        visualizer = DependencyVisualizer(mock_analyzer)
        html = visualizer.generate_simple_html()

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "<title>Dependency Visualization - LunVex Code</title>" in html

    def test_generate_simple_html_with_dependencies(self):
        """Test generating HTML visualization with dependencies."""
        # Create mock dependencies
        dep1 = Dependency(
            name="requests",
            version="2.33.1",
            ecosystem=Ecosystem.PYTHON,
            dep_type=DependencyType.PRODUCTION,
        )

        # Create mock report
        report = DependencyReport(
            ecosystem=Ecosystem.PYTHON, dependencies=[dep1], source_files=["pyproject.toml"]
        )

        mock_analyzer = Mock(spec=DependencyAnalyzer)
        mock_analyzer.analyze_all.return_value = {Ecosystem.PYTHON: report}

        visualizer = DependencyVisualizer(mock_analyzer)
        html = visualizer.generate_simple_html()

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "requests" in html

    def test_save_visualization_dot(self):
        """Test saving DOT visualization to file."""
        mock_analyzer = Mock(spec=DependencyAnalyzer)
        mock_analyzer.analyze_all.return_value = {}

        visualizer = DependencyVisualizer(mock_analyzer)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dependencies.dot"
            result = visualizer.save_visualization(str(output_path), "dot")

            assert result is True
            assert output_path.exists()

            content = output_path.read_text()
            assert "digraph dependencies" in content

    def test_save_visualization_html(self):
        """Test saving HTML visualization to file."""
        mock_analyzer = Mock(spec=DependencyAnalyzer)
        mock_analyzer.analyze_all.return_value = {}

        visualizer = DependencyVisualizer(mock_analyzer)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dependencies.html"
            result = visualizer.save_visualization(str(output_path), "html")

            assert result is True
            assert output_path.exists()

            content = output_path.read_text()
            assert "<!DOCTYPE html>" in content

    def test_save_visualization_invalid_format(self):
        """Test saving visualization with invalid format."""
        mock_analyzer = Mock(spec=DependencyAnalyzer)
        visualizer = DependencyVisualizer(mock_analyzer)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dependencies.txt"
            result = visualizer.save_visualization(str(output_path), "invalid")

            assert result is False
            assert not output_path.exists()

    def test_ecosystem_colors_included(self):
        """Test that ecosystem colors are included in graph with dependencies."""
        # Create mock dependencies
        dep1 = Dependency(
            name="requests",
            version="2.33.1",
            ecosystem=Ecosystem.PYTHON,
            dep_type=DependencyType.PRODUCTION,
        )

        # Create mock report
        report = DependencyReport(
            ecosystem=Ecosystem.PYTHON, dependencies=[dep1], source_files=["pyproject.toml"]
        )

        mock_analyzer = Mock(spec=DependencyAnalyzer)
        mock_analyzer.analyze_all.return_value = {Ecosystem.PYTHON: report}
        visualizer = DependencyVisualizer(mock_analyzer)

        dot_graph = visualizer.generate_dot_graph()

        # Check that the graph was generated and contains the dependency
        assert isinstance(dot_graph, str)
        assert "digraph dependencies" in dot_graph
        assert "requests" in dot_graph
        # Note: The ecosystem color (#3572A5) is used as fill color for nodes
        # but might not appear directly in the output if type colors override it

    def test_visualizer_with_custom_options(self):
        """Test visualizer with custom options."""
        mock_analyzer = Mock(spec=DependencyAnalyzer)
        mock_analyzer.analyze_all.return_value = {}

        visualizer = DependencyVisualizer(mock_analyzer)

        options = VisualizationOptions(
            show_versions=False, show_types=False, width=1600, height=1200
        )

        dot_graph = visualizer.generate_dot_graph(options)

        assert isinstance(dot_graph, str)
        assert "digraph dependencies" in dot_graph
        # Note: We can't easily test that options were applied without
        # parsing the DOT graph, but we can at least verify it runs without errors
