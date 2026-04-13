# LunVex Code PyPI Publishing Guide

This comprehensive guide explains how to publish LunVex Code to PyPI.

## 📦 Current Status

✅ **Package Name Available**: `lunvex-code` is available on PyPI  
✅ **Configuration Ready**: `pyproject.toml` is properly configured  
✅ **Build System Ready**: Uses `hatchling` build backend  
✅ **Scripts Created**: Automation scripts available in `scripts/`  
✅ **Documentation Updated**: README.md includes PyPI installation  

## 🚀 Quick Start Publishing

### Option 1: Using Automated Script (Recommended)

```bash
# 1. Prepare for release (bump version, run tests, update changelog)
python scripts/prepare_release.py 0.2.0

# 2. Publish to TestPyPI (for testing)
./scripts/publish_to_pypi.sh test

# 3. Publish to Production PyPI
./scripts/publish_to_pypi.sh prod
```

### Option 2: Manual Publishing

```bash
# 1. Clean and build
rm -rf build/ dist/ *.egg-info
python -m build

# 2. Validate
twine check dist/*

# 3. Set credentials
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here

# 4. Upload
twine upload dist/*
```

## 🔑 Prerequisites

### 1. PyPI Account
- **Production PyPI**: https://pypi.org/account/register/
- **TestPyPI**: https://test.pypi.org/account/register/ (separate account!)

### 2. API Tokens
Get tokens from:
- **Production**: https://pypi.org/manage/account/#api-tokens
- **TestPyPI**: https://test.pypi.org/manage/account/#api-tokens

### 3. Required Tools
```bash
pip install twine build
```

## 📁 Project Structure for Publishing

```
lunvex-code/
├── pyproject.toml          # Package configuration
├── README.md              # Package description
├── LICENSE               # MIT License
├── lunvex_code/          # Source code
│   ├── __init__.py
│   ├── cli.py
│   ├── agent.py
│   └── ...
├── scripts/              # Publishing scripts
│   ├── publish_to_pypi.sh
│   └── prepare_release.py
└── dist/                 # Built packages (generated)
```

## ⚙️ Configuration Details

### pyproject.toml Key Sections:

```toml
[project]
name = "lunvex-code"           # Package name on PyPI
version = "0.1.0"              # Current version
description = "Terminal AI coding assistant for real projects"
readme = "README.md"           # Documentation file
requires-python = ">=3.10"     # Python version requirement
license = "MIT"                # License type

# Dependencies
dependencies = [
    "openai>=2.31.0",
    "typer>=0.24.1",
    "rich>=14.3.4",
    # ... other dependencies
]

# CLI commands
[project.scripts]
lunvex-code = "lunvex_code.cli:main"
lvc = "lunvex_code.cli:main"   # Short alias

# Build system
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## 🔄 Release Workflow

### Phase 1: Preparation
```bash
# Update version (e.g., 0.1.0 → 0.1.1)
python scripts/prepare_release.py 0.1.1

# Or manually:
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Run tests: pytest
# 4. Build: python -m build
```

### Phase 2: Testing (TestPyPI)
```bash
# Set TestPyPI credentials
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-test-token-here

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ lunvex-code==0.1.1
lunvex-code --version
```

### Phase 3: Production (PyPI)
```bash
# Set Production PyPI credentials
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-prod-token-here

# Upload to PyPI
twine upload dist/*

# Verify installation
pip install lunvex-code==0.1.1
lunvex-code --version
```

### Phase 4: Tagging and Release
```bash
# Create git tag
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1

# Create GitHub release
# Go to: https://github.com/artemmelnik/lunvex-code/releases/new
```

## 🧪 Testing After Publishing

### Test Script
```bash
# Run comprehensive test
python test_installation.py

# Or test specific installation
python test_installation.py testpypi   # Test from TestPyPI
python test_installation.py pypi       # Test from PyPI
```

### Manual Testing
```bash
# Fresh install
pip uninstall -y lunvex-code
pip install lunvex-code

# Test commands
lunvex-code --version
lunvex-code --help
lunvex-code run "echo Hello from PyPI!"
```

## 🛡️ Security Best Practices

### Token Security
1. **Never commit tokens to git**
2. Use environment variables or `.pypi.env` (in `.gitignore`)
3. Rotate tokens periodically
4. Use project-scoped tokens for production

### .gitignore Additions
```
# PyPI tokens
.pypi.env
*.token
*.secret
pypi_credentials.txt
```

### Safe Credential Usage
```bash
# Option 1: Environment variables (temporary)
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-xxx

# Option 2: .pypi.env file
echo 'TWINE_USERNAME=__token__' > .pypi.env
echo 'TWINE_PASSWORD=pypi-xxx' >> .pypi.env
source .pypi.env

# Option 3: Direct in command (not recommended for scripts)
twine upload --username __token__ --password pypi-xxx dist/*
```

## 🐛 Troubleshooting

### Common Issues and Solutions:

1. **"File already exists"**
   ```bash
   # Solution: Increment version
   # Update version in pyproject.toml
   # Rebuild and upload
   ```

2. **"Invalid credentials"**
   ```bash
   # Solution: Verify token format
   # Token should start with 'pypi-'
   # TWINE_USERNAME must be '__token__'
   ```

3. **"Package not found" after installation**
   ```bash
   # Solution: Wait for PyPI propagation (1-5 minutes)
   pip cache purge
   pip install --no-cache-dir lunvex-code
   ```

4. **Dependency issues on TestPyPI**
   ```bash
   # Solution: Use both indexes
   pip install --index-url https://test.pypi.org/simple/ \
              --extra-index-url https://pypi.org/simple/ \
              lunvex-code
   ```

5. **Build fails**
   ```bash
   # Solution: Check pyproject.toml syntax
   python -m py_compile pyproject.toml
   # Ensure all required fields are present
   ```

## 📊 Package Statistics

After publishing, you can:
- View statistics: https://pypi.org/project/lunvex-code/#statistics
- Download counts: https://pypi.org/project/lunvex-code/#files
- User reviews: https://pypi.org/project/lunvex-code/#reviews

## 🔗 Useful Links

- **PyPI Project**: https://pypi.org/project/lunvex-code/
- **TestPyPI Project**: https://test.pypi.org/project/lunvex-code/
- **GitHub Releases**: https://github.com/artemmelnik/lunvex-code/releases
- **Python Packaging Guide**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/

## 🎯 Versioning Strategy

Follow **Semantic Versioning**:
- **Patch (0.0.X)**: Bug fixes, no new features
- **Minor (0.X.0)**: New features, backwards compatible
- **Major (X.0.0)**: Breaking changes

### Example Release Sequence:
```
0.1.0  # Initial release (current)
0.1.1  # Bug fixes
0.2.0  # New features (task planning, async)
1.0.0  # Stable API, production ready
```

## 📞 Support

If you encounter issues:
1. Check PyPI status: https://status.python.org/
2. Review error messages carefully
3. Check existing issues: https://github.com/artemmelnik/lunvex-code/issues
4. Email: artemmelnik989@gmail.com

## 🎉 Congratulations!

You're ready to publish LunVex Code to PyPI! The package will be available to millions of Python developers worldwide with a simple:

```bash
pip install lunvex-code
```

This makes installation much easier for users and increases the project's visibility in the Python ecosystem.