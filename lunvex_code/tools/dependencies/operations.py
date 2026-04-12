"""Dependency operation tools (add, remove, update)."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

import tomli
import tomli_w

from lunvex_code.dependencies import DependencyAnalyzer
from ..base import Tool, ToolResult


class AddDependencyTool(Tool):
    """Add a new dependency to the project."""

    name = "add_dependency"
    description = "Add a new dependency to the project"
    permission_level = "ask"  # Modifies files

    parameters = {
        "package": {
            "type": "string",
            "description": "Package name to add",
            "required": True,
        },
        "version": {
            "type": "string",
            "description": "Version specification (e.g., '^1.0.0', '>=2.0.0')",
            "required": False,
            "default": "latest",
        },
        "ecosystem": {
            "type": "string",
            "description": "Ecosystem (python, javascript, rust, go, ruby, php)",
            "required": True,
        },
        "dep_type": {
            "type": "string",
            "description": "Dependency type (production, development, optional, peer)",
            "required": False,
            "default": "production",
        },
    }

    def execute(
        self, package: str, ecosystem: str, version: str = "latest", dep_type: str = "production"
    ) -> ToolResult:
        try:
            cwd = Path.cwd()
            ecosystem_lower = ecosystem.lower()

            if ecosystem_lower == "python":
                return self._add_python_dependency(cwd, package, version, dep_type)
            elif ecosystem_lower == "javascript":
                return self._add_javascript_dependency(cwd, package, version, dep_type)
            elif ecosystem_lower == "rust":
                return self._add_rust_dependency(cwd, package, version, dep_type)
            elif ecosystem_lower == "go":
                return self._add_go_dependency(cwd, package, version)
            elif ecosystem_lower == "ruby":
                return self._add_ruby_dependency(cwd, package, version, dep_type)
            elif ecosystem_lower == "php":
                return self._add_php_dependency(cwd, package, version, dep_type)
            else:
                return ToolResult(
                    success=False, output="", error=f"Unsupported ecosystem: {ecosystem}"
                )

        except Exception as e:
            return ToolResult(success=False, output="", error=f"Failed to add dependency: {str(e)}")

    def _add_python_dependency(
        self, cwd: Path, package: str, version: str, dep_type: str
    ) -> ToolResult:
        """Add dependency to Python project."""
        # Try pyproject.toml first
        pyproject_path = cwd / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, "rb") as f:
                    data = tomli.load(f)

                # Build dependency spec
                if version == "latest":
                    dep_spec = package
                else:
                    dep_spec = f"{package}{version}"

                # Add to appropriate section
                if dep_type == "development":
                    # Add to optional-dependencies.dev
                    optional_deps = data.setdefault("project", {}).setdefault(
                        "optional-dependencies", {}
                    )
                    dev_deps = optional_deps.setdefault("dev", [])
                    if dep_spec not in dev_deps:
                        dev_deps.append(dep_spec)
                else:
                    # Add to regular dependencies
                    deps = data.setdefault("project", {}).setdefault("dependencies", [])
                    if dep_spec not in deps:
                        deps.append(dep_spec)

                # Write back
                with open(pyproject_path, "wb") as f:
                    tomli_w.dump(data, f)

                return ToolResult(
                    success=True,
                    output=f"Added {package}{version} to pyproject.toml ({dep_type})",
                )

            except Exception as e:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Failed to update pyproject.toml: {str(e)}",
                )

        # Fall back to requirements.txt
        requirements_path = cwd / "requirements.txt"
        if requirements_path.exists():
            try:
                with open(requirements_path, "a") as f:
                    if version == "latest":
                        f.write(f"\n{package}")
                    else:
                        f.write(f"\n{package}{version}")

                return ToolResult(
                    success=True,
                    output=f"Added {package}{version} to requirements.txt",
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Failed to update requirements.txt: {str(e)}",
                )

        # No Python dependency file found
        return ToolResult(
            success=False,
            output="",
            error="No Python dependency file found (pyproject.toml or requirements.txt)",
        )

    def _add_javascript_dependency(
        self, cwd: Path, package: str, version: str, dep_type: str
    ) -> ToolResult:
        """Add dependency to JavaScript/Node.js project."""
        package_json_path = cwd / "package.json"
        if not package_json_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No package.json found in project",
            )

        try:
            with open(package_json_path, "r") as f:
                data = json.load(f)

            # Build version spec
            if version == "latest":
                version_spec = "latest"
            else:
                version_spec = version

            # Add to appropriate section
            if dep_type == "development":
                dev_deps = data.setdefault("devDependencies", {})
                dev_deps[package] = version_spec
            elif dep_type == "peer":
                peer_deps = data.setdefault("peerDependencies", {})
                peer_deps[package] = version_spec
            elif dep_type == "optional":
                optional_deps = data.setdefault("optionalDependencies", {})
                optional_deps[package] = version_spec
            else:  # production
                deps = data.setdefault("dependencies", {})
                deps[package] = version_spec

            # Write back
            with open(package_json_path, "w") as f:
                json.dump(data, f, indent=2)

            return ToolResult(
                success=True,
                output=f"Added {package}@{version_spec} to package.json ({dep_type})",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update package.json: {str(e)}",
            )

    def _add_rust_dependency(
        self, cwd: Path, package: str, version: str, dep_type: str
    ) -> ToolResult:
        """Add dependency to Rust project."""
        cargo_toml_path = cwd / "Cargo.toml"
        if not cargo_toml_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No Cargo.toml found in project",
            )

        try:
            # For Rust, we'll use a simple approach - append to Cargo.toml
            # In a real implementation, we'd parse and update the TOML properly
            with open(cargo_toml_path, "a") as f:
                if version == "latest":
                    f.write(f'\n{dep_type} = {{ package = "{package}" }}\n')
                else:
                    f.write(f'\n{dep_type} = {{ package = "{package}", version = "{version}" }}\n')

            return ToolResult(
                success=True,
                output=f"Added {package}{version} to Cargo.toml ({dep_type})",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update Cargo.toml: {str(e)}",
            )

    def _add_go_dependency(self, cwd: Path, package: str, version: str) -> ToolResult:
        """Add dependency to Go project."""
        go_mod_path = cwd / "go.mod"
        if not go_mod_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No go.mod found in project",
            )

        try:
            # For Go, we can run go get
            cmd = ["go", "get"]
            if version != "latest":
                cmd.append(f"{package}@{version}")
            else:
                cmd.append(package)

            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    output=f"Added {package}{version} to go.mod\n{result.stdout}",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Failed to add Go dependency: {result.stderr}",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to add Go dependency: {str(e)}",
            )

    def _add_ruby_dependency(
        self, cwd: Path, package: str, version: str, dep_type: str
    ) -> ToolResult:
        """Add dependency to Ruby project."""
        gemfile_path = cwd / "Gemfile"
        if not gemfile_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No Gemfile found in project",
            )

        try:
            with open(gemfile_path, "a") as f:
                if dep_type == "development":
                    f.write(f'\ngem "{package}"')
                    if version != "latest":
                        f.write(f', "{version}"')
                    f.write(", group: :development\n")
                else:
                    f.write(f'\ngem "{package}"')
                    if version != "latest":
                        f.write(f', "{version}"')
                    f.write("\n")

            return ToolResult(
                success=True,
                output=f"Added {package}{version} to Gemfile ({dep_type})",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update Gemfile: {str(e)}",
            )

    def _add_php_dependency(
        self, cwd: Path, package: str, version: str, dep_type: str
    ) -> ToolResult:
        """Add dependency to PHP project."""
        composer_json_path = cwd / "composer.json"
        if not composer_json_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No composer.json found in project",
            )

        try:
            with open(composer_json_path, "r") as f:
                data = json.load(f)

            # Build version spec
            if version == "latest":
                version_spec = "*"
            else:
                version_spec = version

            # Add to appropriate section
            if dep_type == "development":
                dev_deps = data.setdefault("require-dev", {})
                dev_deps[package] = version_spec
            else:
                deps = data.setdefault("require", {})
                deps[package] = version_spec

            # Write back
            with open(composer_json_path, "w") as f:
                json.dump(data, f, indent=2)

            return ToolResult(
                success=True,
                output=f"Added {package}:{version_spec} to composer.json ({dep_type})",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update composer.json: {str(e)}",
            )


class RemoveDependencyTool(Tool):
    """Remove a dependency from the project."""

    name = "remove_dependency"
    description = "Remove a dependency from the project"
    permission_level = "ask"  # Modifies files

    parameters = {
        "package": {
            "type": "string",
            "description": "Package name to remove",
            "required": True,
        },
        "ecosystem": {
            "type": "string",
            "description": "Ecosystem (python, javascript, rust, go, ruby, php)",
            "required": True,
        },
    }

    def execute(self, package: str, ecosystem: str) -> ToolResult:
        try:
            cwd = Path.cwd()
            ecosystem_lower = ecosystem.lower()

            if ecosystem_lower == "python":
                return self._remove_python_dependency(cwd, package)
            elif ecosystem_lower == "javascript":
                return self._remove_javascript_dependency(cwd, package)
            elif ecosystem_lower == "rust":
                return self._remove_rust_dependency(cwd, package)
            elif ecosystem_lower == "go":
                return self._remove_go_dependency(cwd, package)
            elif ecosystem_lower == "ruby":
                return self._remove_ruby_dependency(cwd, package)
            elif ecosystem_lower == "php":
                return self._remove_php_dependency(cwd, package)
            else:
                return ToolResult(
                    success=False, output="", error=f"Unsupported ecosystem: {ecosystem}"
                )

        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to remove dependency: {str(e)}"
            )

    def _remove_python_dependency(self, cwd: Path, package: str) -> ToolResult:
        """Remove dependency from Python project."""
        removed_from = []

        # Try pyproject.toml
        pyproject_path = cwd / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, "rb") as f:
                    data = tomli.load(f)

                removed = False

                # Check regular dependencies
                deps = data.get("project", {}).get("dependencies", [])
                new_deps = [d for d in deps if not d.startswith(package)]
                if len(new_deps) != len(deps):
                    data["project"]["dependencies"] = new_deps
                    removed = True

                # Check dev dependencies
                optional_deps = data.get("project", {}).get("optional-dependencies", {})
                dev_deps = optional_deps.get("dev", [])
                new_dev_deps = [d for d in dev_deps if not d.startswith(package)]
                if len(new_dev_deps) != len(dev_deps):
                    optional_deps["dev"] = new_dev_deps
                    removed = True

                if removed:
                    with open(pyproject_path, "wb") as f:
                        tomli_w.dump(data, f)
                    removed_from.append("pyproject.toml")

            except Exception:
                pass  # Continue to requirements.txt

        # Try requirements.txt
        requirements_path = cwd / "requirements.txt"
        if requirements_path.exists():
            try:
                with open(requirements_path, "r") as f:
                    lines = f.readlines()

                new_lines = []
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped and not line_stripped.startswith(package):
                        new_lines.append(line)

                if len(new_lines) != len(lines):
                    with open(requirements_path, "w") as f:
                        f.writelines(new_lines)
                    removed_from.append("requirements.txt")

            except Exception:
                pass

        if removed_from:
            return ToolResult(
                success=True,
                output=f"Removed {package} from {', '.join(removed_from)}",
            )
        else:
            return ToolResult(
                success=False,
                output="",
                error=f"Dependency {package} not found in Python project",
            )

    def _remove_javascript_dependency(self, cwd: Path, package: str) -> ToolResult:
        """Remove dependency from JavaScript/Node.js project."""
        package_json_path = cwd / "package.json"
        if not package_json_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No package.json found in project",
            )

        try:
            with open(package_json_path, "r") as f:
                data = json.load(f)

            removed = False

            # Check all dependency sections
            for section in ["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"]:
                if section in data and package in data[section]:
                    del data[section][package]
                    removed = True

            if removed:
                with open(package_json_path, "w") as f:
                    json.dump(data, f, indent=2)

                return ToolResult(
                    success=True,
                    output=f"Removed {package} from package.json",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Dependency {package} not found in package.json",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update package.json: {str(e)}",
            )

    def _remove_rust_dependency(self, cwd: Path, package: str) -> ToolResult:
        """Remove dependency from Rust project."""
        cargo_toml_path = cwd / "Cargo.toml"
        if not cargo_toml_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No Cargo.toml found in project",
            )

        try:
            # Simple approach - remove lines containing the package
            with open(cargo_toml_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            skip_next = False
            for i, line in enumerate(lines):
                if skip_next:
                    skip_next = False
                    continue

                # Check if line contains the package
                if package in line:
                    # Check if next line might be part of the dependency definition
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith("["):
                        # Keep the line if it's a table header
                        new_lines.append(line)
                    else:
                        skip_next = True
                else:
                    new_lines.append(line)

            if len(new_lines) != len(lines):
                with open(cargo_toml_path, "w") as f:
                    f.writelines(new_lines)

                return ToolResult(
                    success=True,
                    output=f"Removed {package} from Cargo.toml",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Dependency {package} not found in Cargo.toml",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update Cargo.toml: {str(e)}",
            )

    def _remove_go_dependency(self, cwd: Path, package: str) -> ToolResult:
        """Remove dependency from Go project."""
        go_mod_path = cwd / "go.mod"
        if not go_mod_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No go.mod found in project",
            )

        try:
            # Run go mod tidy to remove unused dependencies
            result = subprocess.run(
                ["go", "mod", "tidy"],
                cwd=cwd,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    output=f"Ran go mod tidy to clean up dependencies\n{result.stdout}",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Failed to run go mod tidy: {result.stderr}",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to remove Go dependency: {str(e)}",
            )

    def _remove_ruby_dependency(self, cwd: Path, package: str) -> ToolResult:
        """Remove dependency from Ruby project."""
        gemfile_path = cwd / "Gemfile"
        if not gemfile_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No Gemfile found in project",
            )

        try:
            with open(gemfile_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if f'gem "{package}"' not in line:
                    new_lines.append(line)

            if len(new_lines) != len(lines):
                with open(gemfile_path, "w") as f:
                    f.writelines(new_lines)

                return ToolResult(
                    success=True,
                    output=f"Removed {package} from Gemfile",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Dependency {package} not found in Gemfile",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update Gemfile: {str(e)}",
            )

    def _remove_php_dependency(self, cwd: Path, package: str) -> ToolResult:
        """Remove dependency from PHP project."""
        composer_json_path = cwd / "composer.json"
        if not composer_json_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No composer.json found in project",
            )

        try:
            with open(composer_json_path, "r") as f:
                data = json.load(f)

            removed = False

            # Check both require and require-dev sections
            for section in ["require", "require-dev"]:
                if section in data and package in data[section]:
                    del data[section][package]
                    removed = True

            if removed:
                with open(composer_json_path, "w") as f:
                    json.dump(data, f, indent=2)

                return ToolResult(
                    success=True,
                    output=f"Removed {package} from composer.json",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Dependency {package} not found in composer.json",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update composer.json: {str(e)}",
            )


class UpdateDependencyTool(Tool):
    """Update a dependency to a specific version."""

    name = "update_dependency"
    description = "Update a dependency to a specific version"
    permission_level = "ask"  # Modifies files

    parameters = {
        "package": {
            "type": "string",
            "description": "Package name to update",
            "required": True,
        },
        "version": {
            "type": "string",
            "description": "New version specification",
            "required": True,
        },
        "ecosystem": {
            "type": "string",
            "description": "Ecosystem (python, javascript, rust, go, ruby, php)",
            "required": True,
        },
    }

    def execute(self, package: str, version: str, ecosystem: str) -> ToolResult:
        try:
            cwd = Path.cwd()
            ecosystem_lower = ecosystem.lower()

            if ecosystem_lower == "python":
                return self._update_python_dependency(cwd, package, version)
            elif ecosystem_lower == "javascript":
                return self._update_javascript_dependency(cwd, package, version)
            elif ecosystem_lower == "rust":
                return self._update_rust_dependency(cwd, package, version)
            elif ecosystem_lower == "go":
                return self._update_go_dependency(cwd, package, version)
            elif ecosystem_lower == "ruby":
                return self._update_ruby_dependency(cwd, package, version)
            elif ecosystem_lower == "php":
                return self._update_php_dependency(cwd, package, version)
            else:
                return ToolResult(
                    success=False, output="", error=f"Unsupported ecosystem: {ecosystem}"
                )

        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to update dependency: {str(e)}"
            )

    def _update_python_dependency(self, cwd: Path, package: str, version: str) -> ToolResult:
        """Update dependency in Python project."""
        updated_in = []

        # Try pyproject.toml
        pyproject_path = cwd / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, "rb") as f:
                    data = tomli.load(f)

                updated = False

                # Update regular dependencies
                deps = data.get("project", {}).get("dependencies", [])
                for i, dep in enumerate(deps):
                    if dep.startswith(package):
                        deps[i] = f"{package}{version}"
                        updated = True

                # Update dev dependencies
                optional_deps = data.get("project", {}).get("optional-dependencies", {})
                dev_deps = optional_deps.get("dev", [])
                for i, dep in enumerate(dev_deps):
                    if dep.startswith(package):
                        dev_deps[i] = f"{package}{version}"
                        updated = True

                if updated:
                    with open(pyproject_path, "wb") as f:
                        tomli_w.dump(data, f)
                    updated_in.append("pyproject.toml")

            except Exception:
                pass  # Continue to requirements.txt

        # Try requirements.txt
        requirements_path = cwd / "requirements.txt"
        if requirements_path.exists():
            try:
                with open(requirements_path, "r") as f:
                    lines = f.readlines()

                new_lines = []
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped and line_stripped.startswith(package):
                        new_lines.append(f"{package}{version}\n")
                    else:
                        new_lines.append(line)

                if new_lines != lines:
                    with open(requirements_path, "w") as f:
                        f.writelines(new_lines)
                    updated_in.append("requirements.txt")

            except Exception:
                pass

        if updated_in:
            return ToolResult(
                success=True,
                output=f"Updated {package} to {version} in {', '.join(updated_in)}",
            )
        else:
            return ToolResult(
                success=False,
                output="",
                error=f"Dependency {package} not found in Python project",
            )

    def _update_javascript_dependency(self, cwd: Path, package: str, version: str) -> ToolResult:
        """Update dependency in JavaScript/Node.js project."""
        package_json_path = cwd / "package.json"
        if not package_json_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No package.json found in project",
            )

        try:
            with open(package_json_path, "r") as f:
                data = json.load(f)

            updated = False

            # Update in all dependency sections
            for section in ["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"]:
                if section in data and package in data[section]:
                    data[section][package] = version
                    updated = True

            if updated:
                with open(package_json_path, "w") as f:
                    json.dump(data, f, indent=2)

                return ToolResult(
                    success=True,
                    output=f"Updated {package} to {version} in package.json",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Dependency {package} not found in package.json",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update package.json: {str(e)}",
            )

    def _update_rust_dependency(self, cwd: Path, package: str, version: str) -> ToolResult:
        """Update dependency in Rust project."""
        cargo_toml_path = cwd / "Cargo.toml"
        if not cargo_toml_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No Cargo.toml found in project",
            )

        try:
            with open(cargo_toml_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if package in line and "version" in line:
                    # Simple regex-like replacement
                    import re
                    pattern = rf'version\s*=\s*"[^"]*"'
                    replacement = f'version = "{version}"'
                    new_line = re.sub(pattern, replacement, line)
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)

            if new_lines != lines:
                with open(cargo_toml_path, "w") as f:
                    f.writelines(new_lines)

                return ToolResult(
                    success=True,
                    output=f"Updated {package} to {version} in Cargo.toml",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Dependency {package} not found in Cargo.toml",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update Cargo.toml: {str(e)}",
            )

    def _update_go_dependency(self, cwd: Path, package: str, version: str) -> ToolResult:
        """Update dependency in Go project."""
        go_mod_path = cwd / "go.mod"
        if not go_mod_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No go.mod found in project",
            )

        try:
            # Run go get to update dependency
            result = subprocess.run(
                ["go", "get", f"{package}@{version}"],
                cwd=cwd,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    output=f"Updated {package} to {version} in go.mod\n{result.stdout}",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Failed to update Go dependency: {result.stderr}",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update Go dependency: {str(e)}",
            )

    def _update_ruby_dependency(self, cwd: Path, package: str, version: str) -> ToolResult:
        """Update dependency in Ruby project."""
        gemfile_path = cwd / "Gemfile"
        if not gemfile_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No Gemfile found in project",
            )

        try:
            with open(gemfile_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if f'gem "{package}"' in line:
                    # Update version in gem line
                    import re
                    pattern = rf'gem "{package}"(?:,\s*"[^"]*")?'
                    replacement = f'gem "{package}", "{version}"'
                    new_line = re.sub(pattern, replacement, line)
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)

            if new_lines != lines:
                with open(gemfile_path, "w") as f:
                    f.writelines(new_lines)

                return ToolResult(
                    success=True,
                    output=f"Updated {package} to {version} in Gemfile",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Dependency {package} not found in Gemfile",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update Gemfile: {str(e)}",
            )

    def _update_php_dependency(self, cwd: Path, package: str, version: str) -> ToolResult:
        """Update dependency in PHP project."""
        composer_json_path = cwd / "composer.json"
        if not composer_json_path.exists():
            return ToolResult(
                success=False,
                output="",
                error="No composer.json found in project",
            )

        try:
            with open(composer_json_path, "r") as f:
                data = json.load(f)

            updated = False

            # Update in both require and require-dev sections
            for section in ["require", "require-dev"]:
                if section in data and package in data[section]:
                    data[section][package] = version
                    updated = True

            if updated:
                with open(composer_json_path, "w") as f:
                    json.dump(data, f, indent=2)

                return ToolResult(
                    success=True,
                    output=f"Updated {package} to {version} in composer.json",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Dependency {package} not found in composer.json",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update composer.json: {str(e)}",
            )