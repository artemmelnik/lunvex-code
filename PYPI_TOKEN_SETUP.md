# PyPI Token Setup Guide

This guide explains how to set up PyPI tokens for publishing LunVex Code.

## 🔑 Getting PyPI Tokens

### 1. Create PyPI Account (if you don't have one)
- Go to https://pypi.org/account/register/
- Fill in the registration form
- Verify your email address

### 2. Get Production PyPI Token
1. Log in to https://pypi.org
2. Go to https://pypi.org/manage/account/
3. Scroll to "API tokens" section
4. Click "Add API token"
5. Token name: `lunvex-code-publish`
6. Scope: **Entire account** (for first token) or select specific project
7. Click "Create token"
8. **COPY THE TOKEN IMMEDIATELY** - it will only be shown once!

### 3. Get TestPyPI Token (Optional but Recommended)
1. Go to https://test.pypi.org/account/register/ (separate account!)
2. Create account on TestPyPI
3. Go to https://test.pypi.org/manage/account/
4. Create token with same steps as above

## 🔧 Setting Up Environment Variables

### Option 1: Temporary (for current terminal session)
```bash
# For TestPyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YourTestTokenHere

# For Production PyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YourProdTokenHere
```

### Option 2: Permanent (add to shell profile)
Add to `~/.bashrc`, `~/.zshrc`, or `~/.profile`:
```bash
# PyPI Tokens
export PYPI_TEST_TOKEN="pypi-YourTestTokenHere"
export PYPI_PROD_TOKEN="pypi-YourProdTokenHere"

# Aliases for easy switching
alias pypi-test="export TWINE_USERNAME=__token__; export TWINE_PASSWORD=\$PYPI_TEST_TOKEN"
alias pypi-prod="export TWINE_USERNAME=__token__; export TWINE_PASSWORD=\$PYPI_PROD_TOKEN"
```

### Option 3: Using .env file (recommended for project)
Create `.pypi.env` file (add to `.gitignore`!):
```bash
# .pypi.env
TWINE_USERNAME=__token__
TWINE_PASSWORD=pypi-YourProdTokenHere
```

Load it when needed:
```bash
source .pypi.env
```

## 🚀 Publishing Commands

### Using the provided script:
```bash
# Test on TestPyPI
./scripts/publish_to_pypi.sh test

# Publish to Production PyPI
./scripts/publish_to_pypi.sh prod
```

### Manual commands:
```bash
# 1. Clean and build
rm -rf build/ dist/ *.egg-info
python -m build

# 2. Validate
twine check dist/*

# 3. Upload to TestPyPI
twine upload --repository testpypi dist/*

# 4. Upload to Production PyPI
twine upload dist/*
```

## 🧪 Testing Installation

### From TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ lunvex-code
lunvex-code --version
```

### From Production PyPI:
```bash
pip install lunvex-code
lunvex-code --version
```

## 🔒 Security Notes

1. **Never commit tokens to git!**
2. Add token files to `.gitignore`:
   ```
   .pypi.env
   *.token
   *.secret
   ```
3. Use environment variables or secret managers
4. Rotate tokens periodically
5. Use project-scoped tokens for production

## 🆘 Troubleshooting

### "Invalid or non-existent authentication information"
- Check that `TWINE_USERNAME` is set to `__token__`
- Verify token starts with `pypi-`
- Ensure token hasn't expired

### "HTTPError: 403 Forbidden"
- Token might not have required permissions
- Try creating new token with "Entire account" scope

### "Package 'lunvex-code' already exists"
- Increment version in `pyproject.toml`
- Rebuild and upload again

### "Failed to upload"
- Check internet connection
- Verify PyPI service status: https://status.python.org/

## 📚 Additional Resources

- [PyPI API Tokens Documentation](https://pypi.org/help/#apitoken)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [TestPyPI Documentation](https://packaging.python.org/en/latest/guides/using-testpypi/)