# Dependency Management

This document describes how to manage dependencies in LunVex Code, including security practices, version control, and update procedures.

## Overview

LunVex Code uses modern Python dependency management with `pyproject.toml` as the primary configuration file. We follow security best practices to ensure the project remains secure and up-to-date.

## Files

### Primary Configuration
- `pyproject.toml` - Main dependency specification with version ranges
- `requirements.txt` - Pinned versions for reproducible environments

### Security Tools
- `check_vulnerabilities.py` - Script to check for security vulnerabilities
- `.github/workflows/ci.yml` - CI pipeline with security scanning

## Dependency Categories

### Production Dependencies
These are required for the core functionality:

```toml
dependencies = [
    "openai>=2.31.0",           # AI API client
    "typer>=0.24.0",           # CLI framework
    "rich>=14.3.0",            # Terminal formatting
    "prompt-toolkit>=3.0.52",  # Interactive prompts
    "pydantic>=2.12.0",        # Data validation
    "python-dotenv>=1.2.0",    # Environment variables
    "pyyaml>=6.0.3",           # YAML parsing
    "tomli>=2.4.0",            # TOML parsing (Python <3.11)
    "requests>=2.33.0",        # HTTP requests
    "tomli-w>=1.2.0",          # TOML writing
]
```

### Development Dependencies
These are only needed for development:

```toml
dev = [
    "pytest>=9.0.0",           # Testing framework
    "pytest-asyncio>=1.3.0",   # Async testing support
    "black>=26.3.0",           # Code formatting
    "ruff>=0.15.0",            # Linting and formatting
    "pip-audit>=2.10.0",       # Security vulnerability scanning
]
```

## Security Practices

### Regular Vulnerability Scanning
We use `pip-audit` to scan for known vulnerabilities:

```bash
# Install pip-audit
pip install pip-audit

# Run vulnerability scan
pip-audit

# Run with JSON output
pip-audit --format json
```

### Automated Security Checks
Security scanning is integrated into our CI pipeline:
- Runs on every push and pull request
- Uses `pip-audit` to check all dependencies
- Fails the build if critical vulnerabilities are found

### Minimum Version Requirements
We specify minimum versions to ensure security patches are included:
- All dependencies have minimum version requirements
- Regular updates to latest secure versions
- Avoid overly restrictive upper bounds

## Update Procedures

### Regular Updates
1. **Check for outdated packages:**
   ```bash
   pip list --outdated
   ```

2. **Update dependencies:**
   ```bash
   pip install --upgrade package-name
   ```

3. **Update pyproject.toml:**
   - Update version requirements
   - Ensure compatibility with other dependencies

4. **Update requirements.txt:**
   ```bash
   pip freeze | grep -E "package-name" > requirements.txt
   ```

5. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

6. **Check for vulnerabilities:**
   ```bash
   python check_vulnerabilities.py
   ```

### Major Version Updates
For major version updates (e.g., pydantic 1.x → 2.x):

1. **Read release notes:** Check for breaking changes
2. **Test in isolation:** Update one package at a time
3. **Run comprehensive tests:** Ensure all functionality works
4. **Update documentation:** Document any API changes
5. **Create migration guide:** If needed for users

## Version Pinning Strategy

### Development
- Use version ranges in `pyproject.toml` (e.g., `>=2.31.0`)
- Allows for automatic updates within compatible ranges
- Enables security patch installation

### Production/Deployment
- Use pinned versions in `requirements.txt`
- Ensures reproducible builds
- Can be generated from current environment

### Generating requirements.txt
```bash
# Generate from current environment
pip freeze | grep -E "package1|package2" > requirements.txt

# Or install from requirements.txt
pip install -r requirements.txt
```

## CI/CD Integration

### Security Scanning
The CI pipeline includes:
1. **Dependency installation** with dev extras
2. **Vulnerability scanning** using `pip-audit`
3. **Test execution** to ensure updates don't break functionality
4. **Package building** to verify installability

### Automated Updates
Consider setting up:
- Dependabot for automatic PRs on dependency updates
- Scheduled security scans (weekly/monthly)
- Automatic testing of dependency updates

## Troubleshooting

### Dependency Conflicts
If you encounter dependency conflicts:

1. **Check compatibility:**
   ```bash
   pip check
   ```

2. **Create fresh environment:**
   ```bash
   python -m venv .venv-new
   source .venv-new/bin/activate
   pip install -e ".[dev]"
   ```

3. **Use dependency resolver:**
   ```bash
   pip install --upgrade-strategy eager -e ".[dev]"
   ```

### Security Vulnerabilities
If vulnerabilities are found:

1. **Check affected versions:**
   ```bash
   pip-audit --desc
   ```

2. **Update to patched version:**
   ```bash
   pip install --upgrade vulnerable-package
   ```

3. **If no patch available:**
   - Consider alternative packages
   - Implement workarounds
   - Document the risk

## Best Practices

1. **Regular Updates:** Update dependencies at least monthly
2. **Security First:** Prioritize security updates over features
3. **Testing:** Always run tests after dependency updates
4. **Documentation:** Keep version requirements up-to-date
5. **Monitoring:** Subscribe to security advisories for key dependencies

## Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Security](https://pypi.org/security/)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)
- [GitHub Dependabot](https://docs.github.com/en/code-security/dependabot)

## Changelog

### 2024-04-11
- Added `pip-audit` to dev dependencies
- Created security checking script
- Updated all dependencies to latest secure versions
- Added security scanning to CI pipeline
- Created this documentation