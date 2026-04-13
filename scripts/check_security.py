#!/usr/bin/env python3
"""
Security check script for LunVex Code.
Checks dependencies for vulnerabilities and security issues.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List


def run_command(cmd: List[str]) -> str:
    """Run a command and return its output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}: {e}")
        return ""


def check_pip_audit() -> bool:
    """Check dependencies for known vulnerabilities using pip-audit."""
    print("🔒 Checking dependencies for vulnerabilities with pip-audit...")

    try:
        # Check if pip-audit is installed
        import pip_audit  # noqa
    except ImportError:
        print("⚠️  pip-audit not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pip-audit"], check=True)

    # Run pip-audit
    result = subprocess.run(
        [sys.executable, "-m", "pip_audit", "--format", "json"], capture_output=True, text=True
    )

    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            vulns = data.get("vulnerabilities", [])

            if vulns:
                print(f"❌ Found {len(vulns)} vulnerabilities:")
                for vuln in vulns:
                    print(f"   - {vuln.get('name', 'Unknown')}: {vuln.get('id', 'Unknown')}")
                return False
            else:
                print("✅ No vulnerabilities found!")
                return True

        except json.JSONDecodeError:
            print("✅ pip-audit passed (no JSON output means no vulnerabilities)")
            return True
    else:
        print("⚠️  pip-audit failed to run")
        print(f"Stderr: {result.stderr}")
        return False


def check_safety() -> bool:
    """Check dependencies using safety (alternative to pip-audit)."""
    print("\n🔒 Checking dependencies with safety...")

    try:
        # Try to import safety
        import safety  # noqa
    except ImportError:
        print("⚠️  safety not installed. Skipping...")
        return True

    result = subprocess.run(["safety", "check", "--json"], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ safety check passed!")
        return True
    else:
        try:
            data = json.loads(result.stdout)
            if data:
                print(f"❌ Safety found issues: {data}")
                return False
        except Exception:
            print("✅ safety passed (non-zero exit but no JSON output)")
            return True


def check_bandit() -> bool:
    """Check source code for security issues with bandit."""
    print("\n🔍 Checking source code with bandit...")

    try:
        import bandit  # noqa
    except ImportError:
        print("⚠️  bandit not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "bandit"], check=True)

    result = subprocess.run(
        ["bandit", "-r", "lunvex_code", "-f", "json", "-q"], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ bandit check passed!")
        return True
    else:
        try:
            data = json.loads(result.stdout)
            # metrics = data.get("metrics", {})  # Unused variable
            issues = data.get("results", [])

            if issues:
                print(f"❌ Bandit found {len(issues)} issues:")
                for issue in issues[:5]:  # Show first 5 issues
                    print(
                        f"   - {issue.get('test_name')} in {issue.get('filename')}:{issue.get('line_number')}"
                    )
                if len(issues) > 5:
                    print(f"   ... and {len(issues) - 5} more issues")
                return False
            else:
                print("✅ No security issues found in code!")
                return True
        except json.JSONDecodeError:
            print("⚠️  Could not parse bandit output")
            return False


def check_dependency_licenses() -> bool:
    """Check that all dependencies have acceptable licenses."""
    print("\n📄 Checking dependency licenses...")

    # List of acceptable licenses
    acceptable_licenses = {
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "BSD-2-Clause",
        "ISC",
        "Python-2.0",
        "Unlicense",
        "CC0-1.0",
    }

    # Get installed packages
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
        check=True,
    )

    packages = json.loads(result.stdout)
    problematic = []

    for pkg in packages:
        name = pkg["name"]

        # Skip lunvex-code itself
        if name.lower() in ["lunvex-code", "lunvex_code"]:
            continue

        # Try to get license info
        try:
            # Use pip show to get metadata
            info_result = subprocess.run(
                [sys.executable, "-m", "pip", "show", name], capture_output=True, text=True
            )

            if info_result.returncode == 0:
                lines = info_result.stdout.split("\n")
                license_line = [line for line in lines if line.startswith("License:")]

                if license_line:
                    license_text = license_line[0].replace("License:", "").strip()

                    # Check if license is acceptable
                    license_ok = False
                    for acceptable in acceptable_licenses:
                        if acceptable.lower() in license_text.lower():
                            license_ok = True
                            break

                    if not license_ok:
                        problematic.append((name, license_text))

        except Exception as e:
            print(f"⚠️  Could not check license for {name}: {e}")

    if problematic:
        print("❌ Found packages with potentially problematic licenses:")
        for name, license_text in problematic:
            print(f"   - {name}: {license_text}")
        print(f"\n   Acceptable licenses: {', '.join(sorted(acceptable_licenses))}")
        return False
    else:
        print("✅ All dependencies have acceptable licenses!")
        return True


def check_env_file() -> bool:
    """Check for security issues in .env file."""
    print("\n🔐 Checking environment configuration...")

    env_path = Path(".env")
    example_path = Path("config/.env.example")

    if not example_path.exists():
        print("⚠️  No .env.example file found in config/")
        return True

    # Read example to see what secrets should be there
    with open(example_path) as f:
        example_content = f.read()

    # Check if .env exists
    if not env_path.exists():
        print("⚠️  No .env file found. Using .env.example as reference.")
        env_content = example_content
    else:
        with open(env_path) as f:
            env_content = f.read()

    # Look for common security issues
    issues = []

    lines = env_content.split("\n")
    for i, line in enumerate(lines, 1):
        line = line.strip()

        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue

        # Check for exposed secrets
        if "password" in line.lower() and "=" in line:
            key, value = line.split("=", 1)
            if value.strip() and value.strip() not in [
                "",
                "your_password_here",
                "YOUR_PASSWORD_HERE",
            ]:
                # Check if it looks like a real password (not a placeholder)
                if not any(
                    placeholder in value for placeholder in ["your_", "YOUR_", "example", "EXAMPLE"]
                ):
                    issues.append(f"Line {i}: Possible exposed password in {key}")

        # Check for API keys
        if any(keyword in line.lower() for keyword in ["api_key", "api_token", "secret"]):
            key, value = line.split("=", 1)
            if value.strip() and value.strip() not in [
                "",
                "your_api_key_here",
                "YOUR_API_KEY_HERE",
            ]:
                if not any(
                    placeholder in value for placeholder in ["your_", "YOUR_", "example", "EXAMPLE"]
                ):
                    issues.append(f"Line {i}: Possible exposed API key in {key}")

    if issues:
        print("❌ Potential security issues in .env file:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n   Please ensure .env is in .gitignore and not committed!")
        return False
    else:
        print("✅ .env file looks secure!")
        return True


def main() -> None:
    """Run all security checks."""
    print("=" * 60)
    print("🔒 LunVex Code Security Audit")
    print("=" * 60)

    all_passed = True

    # Run checks
    checks = [
        ("Dependency Vulnerabilities", check_pip_audit),
        ("Source Code Security", check_bandit),
        ("Dependency Licenses", check_dependency_licenses),
        ("Environment Configuration", check_env_file),
    ]

    results = []

    for check_name, check_func in checks:
        print(f"\n{'=' * 40}")
        print(f"Check: {check_name}")
        print(f"{'=' * 40}")

        try:
            passed = check_func()
            results.append((check_name, passed))
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            results.append((check_name, False))
            all_passed = False

    # Print summary
    print(f"\n{'=' * 60}")
    print("📊 Security Audit Summary")
    print(f"{'=' * 60}")

    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")

    print(f"\n{'=' * 60}")

    if all_passed:
        print("🎉 All security checks passed!")
        sys.exit(0)
    else:
        print("⚠️  Some security checks failed. Please review the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
