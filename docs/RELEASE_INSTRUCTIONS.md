# LunVex Code Release Instructions

This document provides step-by-step instructions for releasing new versions of LunVex Code to PyPI.

## 📋 Release Checklist

### Before Release
- [ ] **All tests pass**: `pytest`
- [ ] **Code quality**: Run `black`, `isort`, `ruff check`
- [ ] **Documentation updated**: README.md is current
- [ ] **Version bumped**: Update in `pyproject.toml`
- [ ] **Changelog updated**: Add release notes to `CHANGELOG.md`
- [ ] **Dependencies checked**: All dependencies are up-to-date

### Release Process
- [ ] **Build package**: `python -m build`
- [ ] **Validate package**: `twine check dist/*`
- [ ] **Test on TestPyPI**: Upload and test installation
- [ ] **Publish to PyPI**: Upload to production PyPI
- [ ] **Create git tag**: `git tag vX.Y.Z`
- [ ] **Push tag**: `git push --tags`
- [ ] **Update GitHub release**: Create release on GitHub

### After Release
- [ ] **Verify installation**: `pip install lunvex-code`
- [ ] **Test functionality**: Run basic commands
- [ ] **Update documentation**: If needed
- [ ] **Announce release**: Share on relevant channels

## 🚀 Step-by-Step Release Guide

### Step 1: Prepare for Release

```bash
# 1. Ensure you're on main branch and up-to-date
git checkout main
git pull origin main

# 2. Run all tests
pytest

# 3. Check code quality
black lunvex_code tests
isort lunvex_code tests
ruff check lunvex_code tests

# 4. Update version in pyproject.toml
# Change: version = "X.Y.Z"
```

### Step 2: Update Changelog

Edit `CHANGELOG.md`:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature 1
- New feature 2

### Changed
- Improvement 1
- Improvement 2

### Fixed
- Bug fix 1
- Bug fix 2

### Removed
- Deprecated feature removed
```

### Step 3: Build Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build new package
python -m build

# Verify build
ls -la dist/
twine check dist/*
```

### Step 4: Test on TestPyPI

```bash
# Set TestPyPI credentials
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-test-token-here

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ lunvex-code==X.Y.Z
lunvex-code --version
```

### Step 5: Publish to Production PyPI

```bash
# Set Production PyPI credentials
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-prod-token-here

# Upload to PyPI
twine upload dist/*

# Verify on PyPI website
# https://pypi.org/project/lunvex-code/X.Y.Z/
```

### Step 6: Create Git Tag and Release

```bash
# Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release vX.Y.Z"

# Create and push tag
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z

# Push changes
git push origin main
```

### Step 7: Create GitHub Release

1. Go to https://github.com/artemmelnik/lunvex-code/releases
2. Click "Draft a new release"
3. Tag: `vX.Y.Z`
4. Title: `LunVex Code vX.Y.Z`
5. Description: Copy from CHANGELOG.md
6. Attach: `dist/lunvex_code-X.Y.Z-py3-none-any.whl` and `dist/lunvex_code-X.Y.Z.tar.gz`
7. Publish release

### Step 8: Verify Release

```bash
# Clean install from PyPI
pip uninstall -y lunvex-code
pip install lunvex-code==X.Y.Z

# Test basic functionality
lunvex-code --version
lunvex-code --help
lunvex-code run "echo test"
```

## 🔢 Versioning Strategy

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR version (X.0.0)**: Incompatible API changes
- **MINOR version (0.X.0)**: New functionality (backwards compatible)
- **PATCH version (0.0.X)**: Bug fixes (backwards compatible)

### Examples:
- `0.1.0` → `0.2.0`: Added new feature (task planning)
- `0.1.0` → `0.1.1`: Fixed bug in file operations
- `0.1.0` → `1.0.0`: Stable API, production ready

## 🔐 Token Management

### Getting Tokens:
1. **TestPyPI**: https://test.pypi.org/manage/account/
2. **Production PyPI**: https://pypi.org/manage/account/

### Storing Tokens Safely:
```bash
# Option 1: Environment variables (temporary)
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-xxx

# Option 2: .pypi.env file (add to .gitignore!)
echo 'TWINE_USERNAME=__token__' > .pypi.env
echo 'TWINE_PASSWORD=pypi-xxx' >> .pypi.env
source .pypi.env

# Option 3: Use the provided script
./scripts/publish_to_pypi.sh test
./scripts/publish_to_pypi.sh prod
```

## 🐛 Troubleshooting

### Common Issues:

1. **"File already exists" on PyPI**
   ```bash
   # Increment version and rebuild
   # Update pyproject.toml version
   rm -rf build/ dist/
   python -m build
   twine upload dist/*
   ```

2. **"Invalid credentials"**
   ```bash
   # Verify token format (should start with pypi-)
   # Check TWINE_USERNAME is __token__
   # Try creating new token
   ```

3. **Installation fails after publishing**
   ```bash
   # Wait a few minutes for PyPI propagation
   # Clear pip cache
   pip cache purge
   pip install --no-cache-dir lunvex-code
   ```

4. **TestPyPI installation fails**
   ```bash
   # TestPyPI might not have all dependencies
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ lunvex-code
   ```

## 📞 Support

If you encounter issues:
1. Check PyPI status: https://status.python.org/
2. Review Twine docs: https://twine.readthedocs.io/
3. Check GitHub issues: https://github.com/artemmelnik/lunvex-code/issues
4. Email: artemmelnik989@gmail.com

## 🎉 Congratulations!

You've successfully released a new version of LunVex Code! Consider:
- Announcing on relevant forums/channels
- Updating documentation if needed
- Planning next features based on user feedback