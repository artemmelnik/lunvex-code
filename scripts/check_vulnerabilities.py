#!/usr/bin/env python3
"""Script to check for vulnerabilities in dependencies."""

import subprocess
import sys
from pathlib import Path


def run_pip_audit():
    """Run pip-audit and return results."""
    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json"], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running pip-audit: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("pip-audit not found. Install it with: pip install pip-audit")
        return None


def check_dependencies():
    """Check dependencies for vulnerabilities."""
    print("🔍 Checking dependencies for vulnerabilities...")
    print("=" * 60)

    # Run pip-audit
    output = run_pip_audit()

    if output:
        import json

        try:
            data = json.loads(output)
            vulnerabilities_found = False

            for dep in data.get("dependencies", []):
                vulns = dep.get("vulns", [])
                if vulns:
                    vulnerabilities_found = True
                    print(f"\n⚠️  Vulnerabilities found in {dep['name']}=={dep['version']}:")
                    for vuln in vulns:
                        print(
                            f"   • {vuln.get('id', 'Unknown')}: {vuln.get('description', 'No description')}"
                        )
                        print(f"     Severity: {vuln.get('severity', 'Unknown')}")

            if not vulnerabilities_found:
                print("✅ No known vulnerabilities found!")
            else:
                print("\n🔴 Vulnerabilities detected. Consider updating packages.")
                return False
        except json.JSONDecodeError as e:
            print(f"Error parsing pip-audit output: {e}")
            return False
    else:
        return False

    return True


def check_pyproject_toml():
    """Check if pyproject.toml has minimum version requirements."""
    print("\n📋 Checking pyproject.toml version requirements...")
    print("=" * 60)

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return False

    try:
        import tomli

        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)

        deps = data.get("project", {}).get("dependencies", [])
        dev_deps = data.get("project", {}).get("optional-dependencies", {}).get("dev", [])

        print(f"Production dependencies: {len(deps)}")
        print(f"Development dependencies: {len(dev_deps)}")

        # Check for minimum versions
        print("\nMinimum version requirements:")
        for dep in deps + dev_deps:
            if ">=" in dep:
                print(f"  ✓ {dep}")

        return True
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
        return False


def main():
    """Main function."""
    print("🛡️  Dependency Security Check")
    print("=" * 60)

    success = True

    # Check vulnerabilities
    if not check_dependencies():
        success = False

    # Check pyproject.toml
    if not check_pyproject_toml():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("✅ All checks passed!")
    else:
        print("❌ Some checks failed. Review the issues above.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
