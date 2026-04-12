"""Dependency analyzer for different ecosystems."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import tomli

from .config import load_config
from .models import Dependency, DependencyReport, DependencyType, Ecosystem


class DependencyAnalyzer:
    """Analyzes dependencies across different ecosystems."""

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.config = load_config(project_root)

    def detect_ecosystem(self) -> List[Ecosystem]:
        """Detect which ecosystems are present in the project."""
        ecosystems = []

        # Check for Python (multiple file types)
        python_files = ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile", "setup.cfg"]
        for file in python_files:
            if (self.project_root / file).exists():
                ecosystems.append(Ecosystem.PYTHON)
                break

        # Check for JavaScript/TypeScript
        if (self.project_root / "package.json").exists():
            ecosystems.append(Ecosystem.JAVASCRIPT)

        # Check for Rust
        if (self.project_root / "Cargo.toml").exists():
            ecosystems.append(Ecosystem.RUST)

        # Check for Go
        if (self.project_root / "go.mod").exists():
            ecosystems.append(Ecosystem.GO)

        # Check for Ruby
        ruby_files = ["Gemfile", "gems.rb"]
        for file in ruby_files:
            if (self.project_root / file).exists():
                ecosystems.append(Ecosystem.RUBY)
                break

        # Check for PHP
        if (self.project_root / "composer.json").exists():
            ecosystems.append(Ecosystem.PHP)

        # Check for Java (Maven)
        if (self.project_root / "pom.xml").exists():
            ecosystems.append(Ecosystem.UNKNOWN)  # TODO: Add Java support

        # Check for .NET
        if (self.project_root / "*.csproj").exists() or (self.project_root / "*.fsproj").exists():
            ecosystems.append(Ecosystem.UNKNOWN)  # TODO: Add .NET support

        return ecosystems if ecosystems else [Ecosystem.UNKNOWN]

    def analyze_python(self) -> DependencyReport:
        """Analyze Python dependencies."""
        dependencies = []
        source_files = []

        # Try pyproject.toml first
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            source_files.append(str(pyproject_path.relative_to(self.project_root)))
            dependencies.extend(self._parse_pyproject_toml(pyproject_path))

        # Try requirements.txt
        requirements_path = self.project_root / "requirements.txt"
        if requirements_path.exists():
            source_files.append(str(requirements_path.relative_to(self.project_root)))
            dependencies.extend(self._parse_requirements_txt(requirements_path))

        # Try setup.py (basic parsing)
        setup_path = self.project_root / "setup.py"
        if setup_path.exists():
            source_files.append(str(setup_path.relative_to(self.project_root)))
            dependencies.extend(self._parse_setup_py(setup_path))

        # Try Pipfile
        pipfile_path = self.project_root / "Pipfile"
        if pipfile_path.exists():
            source_files.append(str(pipfile_path.relative_to(self.project_root)))
            dependencies.extend(self._parse_pipfile(pipfile_path))

        # Remove duplicates (keep first occurrence)
        seen = set()
        unique_deps = []
        for dep in dependencies:
            if dep.name not in seen:
                seen.add(dep.name)
                unique_deps.append(dep)

        return DependencyReport(
            ecosystem=Ecosystem.PYTHON,
            dependencies=unique_deps,
            source_files=source_files,
        )

    def analyze_javascript(self) -> DependencyReport:
        """Analyze JavaScript/TypeScript dependencies."""
        package_json_path = self.project_root / "package.json"
        if not package_json_path.exists():
            return DependencyReport(
                ecosystem=Ecosystem.JAVASCRIPT,
                dependencies=[],
                source_files=[],
            )

        with open(package_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        dependencies = []

        # Production dependencies
        deps = data.get("dependencies", {})
        for name, version in deps.items():
            if self.config.should_ignore_package(name):
                continue

            dep = Dependency(
                name=name,
                version=version,
                ecosystem=Ecosystem.JAVASCRIPT,
                dep_type=DependencyType.PRODUCTION,
            )
            dependencies.append(dep)

        # Development dependencies
        dev_deps = data.get("devDependencies", {})
        for name, version in dev_deps.items():
            if self.config.should_ignore_package(name):
                continue

            dep = Dependency(
                name=name,
                version=version,
                ecosystem=Ecosystem.JAVASCRIPT,
                dep_type=DependencyType.DEVELOPMENT,
            )
            dependencies.append(dep)

        # Peer dependencies
        peer_deps = data.get("peerDependencies", {})
        for name, version in peer_deps.items():
            if self.config.should_ignore_package(name):
                continue

            dep = Dependency(
                name=name,
                version=version,
                ecosystem=Ecosystem.JAVASCRIPT,
                dep_type=DependencyType.PEER,
            )
            dependencies.append(dep)

        return DependencyReport(
            ecosystem=Ecosystem.JAVASCRIPT,
            dependencies=dependencies,
            source_files=[str(package_json_path.relative_to(self.project_root))],
        )

    def analyze_all(self) -> Dict[Ecosystem, DependencyReport]:
        """Analyze all detected ecosystems."""
        ecosystems = self.detect_ecosystem()
        reports = {}

        for ecosystem in ecosystems:
            if ecosystem == Ecosystem.PYTHON:
                reports[ecosystem] = self.analyze_python()
            elif ecosystem == Ecosystem.JAVASCRIPT:
                reports[ecosystem] = self.analyze_javascript()
            elif ecosystem == Ecosystem.RUST:
                reports[ecosystem] = self.analyze_rust()
            elif ecosystem == Ecosystem.GO:
                reports[ecosystem] = self.analyze_go()
            elif ecosystem == Ecosystem.RUBY:
                reports[ecosystem] = self.analyze_ruby()
            elif ecosystem == Ecosystem.PHP:
                reports[ecosystem] = self.analyze_php()

        return reports

    def _parse_pyproject_toml(self, path: Path) -> List[Dependency]:
        """Parse pyproject.toml file."""
        dependencies = []

        try:
            with open(path, "rb") as f:
                data = tomli.load(f)

            # Check for dependencies in [project] section
            project_deps = data.get("project", {}).get("dependencies", [])
            for dep_spec in project_deps:
                dep = self._parse_python_dep_spec(dep_spec, DependencyType.PRODUCTION)
                if dep:
                    dependencies.append(dep)

            # Check for optional dependencies
            optional_deps = data.get("project", {}).get("optional-dependencies", {})
            for group, deps in optional_deps.items():
                for dep_spec in deps:
                    dep = self._parse_python_dep_spec(dep_spec, DependencyType.OPTIONAL)
                    if dep:
                        dependencies.append(dep)

            # Check for [tool.poetry] or [tool.flit] etc.
            # This is a simplified parser - real projects might need more complex logic

        except Exception:
            # Silently fail for now - we'll add logging later
            pass

        return dependencies

    def _parse_requirements_txt(self, path: Path) -> List[Dependency]:
        """Parse requirements.txt file."""
        dependencies = []

        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Skip editable installs and other special cases for now
                    if line.startswith("-e ") or line.startswith("--"):
                        continue

                    dep = self._parse_python_dep_spec(line, DependencyType.PRODUCTION)
                    if dep:
                        dependencies.append(dep)

        except Exception:
            # Silently fail for now
            pass

        return dependencies

    def _parse_setup_py(self, path: Path) -> List[Dependency]:
        """Basic parsing of setup.py - extracts install_requires."""
        dependencies = []

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Very basic regex extraction - this is not robust
            # For MVP, we'll keep it simple
            install_requires_match = re.search(
                r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL
            )

            if install_requires_match:
                deps_text = install_requires_match.group(1)
                # Extract quoted strings
                dep_strings = re.findall(r"['\"]([^'\"]+)['\"]", deps_text)

                for dep_spec in dep_strings:
                    dep = self._parse_python_dep_spec(dep_spec, DependencyType.PRODUCTION)
                    if dep:
                        dependencies.append(dep)

        except Exception:
            # Silently fail
            pass

        return dependencies

    def _parse_pipfile(self, path: Path) -> List[Dependency]:
        """Parse Pipfile."""
        dependencies = []

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Try to parse as TOML
            data = tomli.loads(content)

            # Packages
            packages = data.get("packages", {})
            for name, version in packages.items():
                if isinstance(version, str):
                    dep_spec = f"{name}{version}"
                else:
                    dep_spec = name  # Version might be dict with other info

                dep = self._parse_python_dep_spec(dep_spec, DependencyType.PRODUCTION)
                if dep:
                    dependencies.append(dep)

            # Dev packages
            dev_packages = data.get("dev-packages", {})
            for name, version in dev_packages.items():
                if isinstance(version, str):
                    dep_spec = f"{name}{version}"
                else:
                    dep_spec = name

                dep = self._parse_python_dep_spec(dep_spec, DependencyType.DEVELOPMENT)
                if dep:
                    dependencies.append(dep)

        except Exception:
            # Not TOML or other error
            pass

        return dependencies

    def analyze_rust(self) -> DependencyReport:
        """Analyze Rust dependencies from Cargo.toml."""
        cargo_path = self.project_root / "Cargo.toml"
        if not cargo_path.exists():
            return DependencyReport(
                ecosystem=Ecosystem.RUST,
                dependencies=[],
                source_files=[],
            )

        try:
            with open(cargo_path, "rb") as f:
                data = tomli.load(f)
        except Exception:
            return DependencyReport(
                ecosystem=Ecosystem.RUST,
                dependencies=[],
                source_files=[str(cargo_path.relative_to(self.project_root))],
            )

        dependencies = []

        # Regular dependencies
        deps = data.get("dependencies", {})
        for name, spec in deps.items():
            if self.config.should_ignore_package(name):
                continue

            version = self._parse_rust_dep_spec(spec)
            dep = Dependency(
                name=name,
                version=version,
                ecosystem=Ecosystem.RUST,
                dep_type=DependencyType.PRODUCTION,
            )
            dependencies.append(dep)

        # Dev dependencies
        dev_deps = data.get("dev-dependencies", {})
        for name, spec in dev_deps.items():
            if self.config.should_ignore_package(name):
                continue

            version = self._parse_rust_dep_spec(spec)
            dep = Dependency(
                name=name,
                version=version,
                ecosystem=Ecosystem.RUST,
                dep_type=DependencyType.DEVELOPMENT,
            )
            dependencies.append(dep)

        # Build dependencies
        build_deps = data.get("build-dependencies", {})
        for name, spec in build_deps.items():
            if self.config.should_ignore_package(name):
                continue

            version = self._parse_rust_dep_spec(spec)
            dep = Dependency(
                name=name,
                version=version,
                ecosystem=Ecosystem.RUST,
                dep_type=DependencyType.DEVELOPMENT,  # Treat build deps as development
            )
            dependencies.append(dep)

        return DependencyReport(
            ecosystem=Ecosystem.RUST,
            dependencies=dependencies,
            source_files=[str(cargo_path.relative_to(self.project_root))],
        )

    def analyze_go(self) -> DependencyReport:
        """Analyze Go dependencies from go.mod."""
        go_mod_path = self.project_root / "go.mod"
        if not go_mod_path.exists():
            return DependencyReport(
                ecosystem=Ecosystem.GO,
                dependencies=[],
                source_files=[],
            )

        try:
            with open(go_mod_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return DependencyReport(
                ecosystem=Ecosystem.GO,
                dependencies=[],
                source_files=[str(go_mod_path.relative_to(self.project_root))],
            )

        dependencies = []

        # Parse go.mod - look for require statements
        # Simple regex-based parser for MVP
        require_section = False
        for line in content.split("\n"):
            line = line.strip()

            if line.startswith("require ("):
                require_section = True
                continue
            elif line.startswith(")"):
                require_section = False
                continue
            elif line.startswith("require ") and not require_section:
                # Single line require
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[1]
                    version = parts[2]

                    if self.config.should_ignore_package(name):
                        continue

                    dep = Dependency(
                        name=name,
                        version=version,
                        ecosystem=Ecosystem.GO,
                        dep_type=DependencyType.PRODUCTION,
                    )
                    dependencies.append(dep)
            elif require_section and line and not line.startswith("//"):
                # Inside require block
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    version = parts[1]

                    if self.config.should_ignore_package(name):
                        continue

                    dep = Dependency(
                        name=name,
                        version=version,
                        ecosystem=Ecosystem.GO,
                        dep_type=DependencyType.PRODUCTION,
                    )
                    dependencies.append(dep)

        return DependencyReport(
            ecosystem=Ecosystem.GO,
            dependencies=dependencies,
            source_files=[str(go_mod_path.relative_to(self.project_root))],
        )

    def analyze_ruby(self) -> DependencyReport:
        """Analyze Ruby dependencies from Gemfile."""
        gemfile_path = self.project_root / "Gemfile"
        if not gemfile_path.exists():
            return DependencyReport(
                ecosystem=Ecosystem.RUBY,
                dependencies=[],
                source_files=[],
            )

        try:
            with open(gemfile_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return DependencyReport(
                ecosystem=Ecosystem.RUBY,
                dependencies=[],
                source_files=[str(gemfile_path.relative_to(self.project_root))],
            )

        dependencies = []

        # Simple Gemfile parser
        for line in content.split("\n"):
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Match gem declarations
            match = re.match(r'^\s*gem\s+[\'"]([^\'"]+)[\'"](?:\s*,\s*[\'"]([^\'"]+)[\'"])?', line)
            if match:
                name = match.group(1)
                version = match.group(2) or "*"

                if self.config.should_ignore_package(name):
                    continue

                # Determine dependency type
                dep_type = DependencyType.PRODUCTION
                if "group :development" in content or "group :test" in content:
                    # Simplified - in real implementation would track context
                    dep_type = DependencyType.DEVELOPMENT

                dep = Dependency(
                    name=name,
                    version=version,
                    ecosystem=Ecosystem.RUBY,
                    dep_type=dep_type,
                )
                dependencies.append(dep)

        return DependencyReport(
            ecosystem=Ecosystem.RUBY,
            dependencies=dependencies,
            source_files=[str(gemfile_path.relative_to(self.project_root))],
        )

    def analyze_php(self) -> DependencyReport:
        """Analyze PHP dependencies from composer.json."""
        composer_path = self.project_root / "composer.json"
        if not composer_path.exists():
            return DependencyReport(
                ecosystem=Ecosystem.PHP,
                dependencies=[],
                source_files=[],
            )

        try:
            with open(composer_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return DependencyReport(
                ecosystem=Ecosystem.PHP,
                dependencies=[],
                source_files=[str(composer_path.relative_to(self.project_root))],
            )

        dependencies = []

        # Require dependencies
        deps = data.get("require", {})
        for name, version in deps.items():
            # Skip PHP version itself
            if name == "php":
                continue

            if self.config.should_ignore_package(name):
                continue

            dep = Dependency(
                name=name,
                version=version,
                ecosystem=Ecosystem.PHP,
                dep_type=DependencyType.PRODUCTION,
            )
            dependencies.append(dep)

        # Require-dev dependencies
        dev_deps = data.get("require-dev", {})
        for name, version in dev_deps.items():
            if self.config.should_ignore_package(name):
                continue

            dep = Dependency(
                name=name,
                version=version,
                ecosystem=Ecosystem.PHP,
                dep_type=DependencyType.DEVELOPMENT,
            )
            dependencies.append(dep)

        return DependencyReport(
            ecosystem=Ecosystem.PHP,
            dependencies=dependencies,
            source_files=[str(composer_path.relative_to(self.project_root))],
        )

    def _parse_python_dep_spec(self, spec: str, dep_type: DependencyType) -> Optional[Dependency]:
        """Parse a Python dependency specification."""
        spec = spec.strip()

        # Skip empty
        if not spec:
            return None

        # Extract package name (simplified)
        # This regex handles most common cases: package, package==1.0, package>=1.0, etc.
        match = re.match(r"^([a-zA-Z0-9_-]+)(?:[<>=!~].*)?", spec)
        if not match:
            return None

        name = match.group(1).lower()

        # Check if ignored
        if self.config.should_ignore_package(name):
            return None

        # Extract version if present
        version_match = re.search(r"([<>=!~]=?\s*[0-9a-zA-Z.*+-]+)", spec)
        version = version_match.group(1) if version_match else "*"

        # Clean up version string
        version = version.strip()

        return Dependency(
            name=name,
            version=version,
            ecosystem=Ecosystem.PYTHON,
            dep_type=dep_type,
        )

    def _parse_rust_dep_spec(self, spec: Any) -> str:
        """Parse a Rust dependency specification from Cargo.toml."""
        if isinstance(spec, str):
            return spec
        elif isinstance(spec, dict):
            # Could be version, path, git, etc.
            version = spec.get("version", "*")
            if isinstance(version, str):
                return version
            else:
                return "*"
        else:
            return "*"

    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        reports = self.analyze_all()

        if not reports:
            return "No dependencies found in project."

        lines = ["# Dependency Analysis Summary", ""]

        for ecosystem, report in reports.items():
            lines.extend(
                [
                    f"## {ecosystem.value.title()}",
                    f"- **Total Dependencies**: {report.total_deps}",
                    f"- **Outdated**: {report.outdated_deps}",
                    f"- **Vulnerable**: {report.vulnerable_deps}",
                    f"- **Source Files**: {', '.join(report.source_files) or 'None'}",
                    "",
                ]
            )

            # List top 10 dependencies
            if report.dependencies:
                lines.append("### Top Dependencies:")
                for dep in report.dependencies[:10]:
                    status = []
                    if dep.is_outdated:
                        status.append("outdated")
                    if dep.has_vulnerabilities:
                        status.append("vulnerable")

                    status_str = f" ({', '.join(status)})" if status else ""
                    lines.append(f"- {dep.name} `{dep.version}`{status_str}")

                if len(report.dependencies) > 10:
                    lines.append(f"- ... and {len(report.dependencies) - 10} more")

                lines.append("")

        return "\n".join(lines)
