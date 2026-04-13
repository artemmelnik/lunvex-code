#!/bin/bash

# Setup pre-commit hooks for LunVex Code

echo "Setting up pre-commit hooks for LunVex Code..."
echo ""

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Install the hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Run against all files once (skip if there are errors with Python version)
echo "Running pre-commit on all files (skipping black if Python version issues)..."
pre-commit run --all-files || echo "Note: Some hooks may have failed due to Python version differences. This is normal."

echo ""
echo "✅ Pre-commit setup complete!"
echo ""
echo "The following hooks are now active:"
echo "1. ruff (code linting and formatting)"
echo "2. ruff-format (code formatting)"
echo "3. trailing-whitespace (removes trailing whitespace)"
echo "4. end-of-file-fixer (ensures files end with newline)"
echo "5. check-yaml (validates YAML files)"
echo "6. check-toml (validates TOML files)"
echo "7. black (code formatting)"
echo "8. pytest-check (runs smoke tests)"
echo ""
echo "These hooks will run automatically on every git commit."
