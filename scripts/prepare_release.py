#!/usr/bin/env python3
"""
Script to prepare LunVex Code for release.
This script helps with version bumping, changelog updates, and validation.
"""

import re
import sys
import subprocess
import tomli
import tomli_w
from datetime import datetime
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command."""
    print(f"🚀 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {result.stderr}")
        sys.exit(1)
    return result

def get_current_version():
    """Get current version from pyproject.toml."""
    with open("pyproject.toml", "rb") as f:
        data = tomli.load(f)
    return data["project"]["version"]

def update_version(new_version):
    """Update version in pyproject.toml."""
    with open("pyproject.toml", "rb") as f:
        data = tomli.load(f)
    
    old_version = data["project"]["version"]
    data["project"]["version"] = new_version
    
    with open("pyproject.toml", "wb") as f:
        tomli_w.dump(data, f)
    
    print(f"✅ Updated version: {old_version} → {new_version}")
    return old_version

def validate_version(new_version):
    """Validate version format (semantic versioning)."""
    pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(pattern, new_version):
        print(f"❌ Invalid version format: {new_version}")
        print("   Expected format: X.Y.Z (e.g., 0.1.0)")
        return False
    
    parts = list(map(int, new_version.split('.')))
    if parts[0] == 0 and parts[1] == 0 and parts[2] == 0:
        print("❌ Version cannot be 0.0.0")
        return False
    
    return True

def run_tests():
    """Run all tests."""
    print("\n🧪 Running tests...")
    result = run_command("pytest", check=False)
    if result.returncode != 0:
        print("❌ Tests failed!")
        print(result.stdout)
        print(result.stderr)
        return False
    print("✅ All tests passed!")
    return True

def check_code_quality():
    """Check code quality with black, isort, ruff."""
    print("\n🔍 Checking code quality...")
    
    # Check with black
    result = run_command("black --check lunvex_code tests", check=False)
    if result.returncode != 0:
        print("⚠️  Code formatting issues found")
        print("   Run: black lunvex_code tests")
        return False
    
    # Check with isort
    result = run_command("isort --check-only lunvex_code tests", check=False)
    if result.returncode != 0:
        print("⚠️  Import sorting issues found")
        print("   Run: isort lunvex_code tests")
        return False
    
    # Check with ruff
    result = run_command("ruff check lunvex_code tests", check=False)
    if result.returncode != 0:
        print("⚠️  Linting issues found")
        print("   Run: ruff check --fix lunvex_code tests")
        return False
    
    print("✅ Code quality checks passed!")
    return True

def update_changelog(old_version, new_version):
    """Update CHANGELOG.md with new version."""
    changelog_path = Path("CHANGELOG.md")
    
    if not changelog_path.exists():
        print("⚠️  CHANGELOG.md not found, creating...")
        changelog_content = f"""# Changelog

All notable changes to LunVex Code will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release

## [{new_version}] - {datetime.now().strftime('%Y-%m-%d')}

### Added
- Initial release of LunVex Code
"""
    else:
        with open(changelog_path, "r") as f:
            content = f.read()
        
        # Find Unreleased section
        unreleased_pattern = r'## \[Unreleased\](.*?)(?=## \[|\Z)'
        match = re.search(unreleased_pattern, content, re.DOTALL)
        
        if not match:
            print("❌ Could not find [Unreleased] section in CHANGELOG.md")
            return False
        
        unreleased_content = match.group(1).strip()
        
        # Create new version section
        new_section = f"""## [{new_version}] - {datetime.now().strftime('%Y-%m-%d')}

{unreleased_content}

"""
        
        # Replace [Unreleased] with new version and add empty [Unreleased]
        new_content = content.replace(
            f"## [Unreleased]{match.group(1)}",
            f"## [Unreleased]\n\n### Added\n- \n\n### Changed\n- \n\n### Fixed\n- \n\n### Removed\n- \n\n{new_section}"
        )
        
        content = new_content
    
    with open(changelog_path, "w") as f:
        f.write(content)
    
    print(f"✅ Updated CHANGELOG.md for version {new_version}")
    return True

def build_package():
    """Build the package."""
    print("\n🔨 Building package...")
    
    # Clean previous builds
    run_command("rm -rf build/ dist/ *.egg-info 2>/dev/null || true", check=False)
    
    # Build
    result = run_command("python -m build", check=False)
    if result.returncode != 0:
        print("❌ Build failed!")
        print(result.stderr)
        return False
    
    # Check build results
    result = run_command("ls -la dist/", check=False)
    print(result.stdout)
    
    # Validate with twine
    result = run_command("twine check dist/*", check=False)
    if result.returncode != 0:
        print("❌ Package validation failed!")
        print(result.stderr)
        return False
    
    print("✅ Package built and validated successfully!")
    return True

def main():
    """Main function."""
    print("=" * 60)
    print("🚀 LunVex Code Release Preparation Script")
    print("=" * 60)
    
    if len(sys.argv) != 2:
        print("Usage: python scripts/prepare_release.py <new_version>")
        print("Example: python scripts/prepare_release.py 0.2.0")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Step 1: Validate version
    if not validate_version(new_version):
        sys.exit(1)
    
    current_version = get_current_version()
    print(f"📦 Current version: {current_version}")
    print(f"🎯 Target version: {new_version}")
    
    if new_version == current_version:
        print("❌ New version is same as current version")
        sys.exit(1)
    
    # Step 2: Confirm with user
    print(f"\n⚠️  This will:")
    print(f"   1. Update version from {current_version} to {new_version}")
    print(f"   2. Run all tests")
    print(f"   3. Check code quality")
    print(f"   4. Update CHANGELOG.md")
    print(f"   5. Build package")
    
    response = input(f"\nContinue? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Release preparation cancelled")
        sys.exit(0)
    
    # Step 3: Update version
    old_version = update_version(new_version)
    
    # Step 4: Run tests
    if not run_tests():
        print("❌ Release preparation failed: Tests did not pass")
        # Revert version
        update_version(old_version)
        sys.exit(1)
    
    # Step 5: Check code quality
    if not check_code_quality():
        response = input("\n⚠️  Code quality issues found. Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Release preparation cancelled")
            # Revert version
            update_version(old_version)
            sys.exit(1)
    
    # Step 6: Update changelog
    if not update_changelog(old_version, new_version):
        response = input("\n⚠️  Changelog update failed. Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Release preparation cancelled")
            # Revert version
            update_version(old_version)
            sys.exit(1)
    
    # Step 7: Build package
    if not build_package():
        print("❌ Release preparation failed: Build failed")
        # Revert version
        update_version(old_version)
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Release preparation completed successfully!")
    print("=" * 60)
    print(f"\n📦 Version: {new_version}")
    print("📁 Built packages in: dist/")
    print("\n📋 Next steps:")
    print("1. Review CHANGELOG.md and update release notes if needed")
    print("2. Test on TestPyPI: ./scripts/publish_to_pypi.sh test")
    print("3. Publish to PyPI: ./scripts/publish_to_pypi.sh prod")
    print("4. Create git tag: git tag -a v{new_version} -m 'Release v{new_version}'")
    print("5. Push tag: git push origin v{new_version}")
    print("6. Create GitHub release")
    print("\n🔗 PyPI URL: https://pypi.org/project/lunvex-code/")
    print("🔗 GitHub Releases: https://github.com/artemmelnik/lunvex-code/releases")

if __name__ == "__main__":
    main()