#!/usr/bin/env python3
"""Script to safely update project dependencies."""

import subprocess
from pathlib import Path
from typing import Dict, Tuple

import tomli
import tomli_w


def read_pyproject() -> Dict:
    """Read pyproject.toml file."""
    with open("pyproject.toml", "rb") as f:
        return tomli.load(f)


def write_pyproject(data: Dict) -> None:
    """Write pyproject.toml file."""
    with open("pyproject.toml", "wb") as f:
        tomli_w.dump(data, f)


def get_latest_version(package: str) -> str:
    """Get latest version of a package from PyPI."""
    try:
        result = subprocess.run(
            ["pip", "index", "versions", package],
            capture_output=True,
            text=True,
            check=True,
        )
        # Parse output to get latest version
        for line in result.stdout.split("\n"):
            if "Available versions:" in line:
                versions = line.split(":")[1].strip().split(", ")
                if versions:
                    return versions[0]  # First is latest
    except subprocess.CalledProcessError:
        pass

    # Fallback: check with pip install --dry-run
    try:
        result = subprocess.run(
            ["pip", "install", "--dry-run", f"{package}==999.0.0"],
            capture_output=True,
            text=True,
        )
        for line in result.stderr.split("\n"):
            if "from versions:" in line:
                versions = line.split(":")[1].strip().split(", ")
                if versions:
                    return versions[-1]  # Last is latest
    except Exception:
        pass

    return "unknown"


def parse_version_spec(spec: str) -> Tuple[str, str]:
    """Parse version specification like '>=2.31.0' or 'openai>=2.31.0'."""
    # Remove package name if present
    if ">=" in spec:
        parts = spec.split(">=")
        if len(parts) == 2:
            return parts[0].strip(), f">={parts[1].strip()}"
    elif "==" in spec:
        parts = spec.split("==")
        if len(parts) == 2:
            return parts[0].strip(), f"=={parts[1].strip()}"
    elif "~=" in spec:
        parts = spec.split("~=")
        if len(parts) == 2:
            return parts[0].strip(), f"~={parts[1].strip()}"

    # If no version spec, assume it's just a package name
    return spec.strip(), ""


def update_dependency_versions() -> Dict[str, str]:
    """Update dependency versions in pyproject.toml."""
    print("📦 Checking for dependency updates...")

    data = read_pyproject()
    updates = {}

    # Update production dependencies
    deps = data.get("project", {}).get("dependencies", [])
    updated_deps = []

    for dep_spec in deps:
        package, version_spec = parse_version_spec(dep_spec)

        if package and version_spec:
            latest = get_latest_version(package)
            if latest != "unknown":
                # Keep the same version spec type but update version
                if version_spec.startswith(">="):
                    new_spec = f"{package}>={latest}"
                    updates[package] = f"{version_spec} -> >= {latest}"
                elif version_spec.startswith("=="):
                    new_spec = f"{package}=={latest}"
                    updates[package] = f"{version_spec} -> == {latest}"
                elif version_spec.startswith("~="):
                    new_spec = f"{package}~={latest}"
                    updates[package] = f"{version_spec} -> ~= {latest}"
                else:
                    new_spec = f"{package}{version_spec}"
            else:
                new_spec = dep_spec
        else:
            new_spec = dep_spec

        updated_deps.append(new_spec)

    if updated_deps:
        data["project"]["dependencies"] = updated_deps

    # Update development dependencies
    dev_deps = data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    if dev_deps:
        updated_dev_deps = []

        for dep_spec in dev_deps:
            package, version_spec = parse_version_spec(dep_spec)

            if package and version_spec:
                latest = get_latest_version(package)
                if latest != "unknown":
                    if version_spec.startswith(">="):
                        new_spec = f"{package}>={latest}"
                        updates[package] = f"{version_spec} -> >= {latest}"
                    elif version_spec.startswith("=="):
                        new_spec = f"{package}=={latest}"
                        updates[package] = f"{version_spec} -> == {latest}"
                    elif version_spec.startswith("~="):
                        new_spec = f"{package}~={latest}"
                        updates[package] = f"{version_spec} -> ~= {latest}"
                    else:
                        new_spec = f"{package}{version_spec}"
                else:
                    new_spec = dep_spec
            else:
                new_spec = dep_spec

            updated_dev_deps.append(new_spec)

        data["project"]["optional-dependencies"]["dev"] = updated_dev_deps

    # Write updated pyproject.toml
    write_pyproject(data)

    return updates


def run_tests() -> bool:
    """Run tests to ensure updates don't break anything."""
    print("\n🧪 Running tests to verify updates...")
    try:
        result = subprocess.run(
            ["pytest", "tests/", "-v"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Tests failed after updates:")
            print(result.stdout[-1000:])  # Last 1000 chars
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main() -> None:
    """Main function."""
    print("🔄 Dependency Updater")
    print("=" * 60)

    # Backup original pyproject.toml
    backup_path = Path("pyproject.toml.backup")
    if not backup_path.exists():
        with open("pyproject.toml", "rb") as src, open(backup_path, "wb") as dst:
            dst.write(src.read())
        print("📋 Created backup: pyproject.toml.backup")

    # Update dependencies
    updates = update_dependency_versions()

    if updates:
        print("\n📝 Updates made:")
        for package, change in updates.items():
            print(f"  • {package}: {change}")

        # Ask for confirmation before installing
        print("\n⚠️  These updates will be written to pyproject.toml")
        response = input("Do you want to install the updated dependencies? (y/N): ")

        if response.lower() == "y":
            print("\n📥 Installing updated dependencies...")
            try:
                # Install production dependencies
                subprocess.run(["pip", "install", "-e", ".[dev]"], check=True)
                print("✅ Dependencies installed successfully!")

                # Run tests
                if run_tests():
                    print("\n🎉 Dependency update completed successfully!")
                else:
                    print("\n⚠️  Tests failed. Consider reverting changes.")
                    revert = input("Revert to backup? (y/N): ")
                    if revert.lower() == "y":
                        with open(backup_path, "rb") as src, open("pyproject.toml", "wb") as dst:
                            dst.write(src.read())
                        print("✅ Reverted to backup.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error installing dependencies: {e}")
                print("Reverting changes...")
                with open(backup_path, "rb") as src, open("pyproject.toml", "wb") as dst:
                    dst.write(src.read())
                print("✅ Reverted to backup.")
    else:
        print("✅ All dependencies are up to date!")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
