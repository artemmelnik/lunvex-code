#!/bin/bash

# Script to publish LunVex Code to PyPI
# Usage: ./scripts/publish_to_pypi.sh [test|prod]

set -e  # Exit on error

MODE="${1:-test}"

echo "🚀 LunVex Code PyPI Publishing Script"
echo "====================================="

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo "❌ twine is not installed. Installing..."
    pip install twine build
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info 2>/dev/null || true

# Build the package
echo "🔨 Building package..."
python -m build

# Check build results
echo "📦 Build results:"
ls -la dist/

# Validate package
echo "🔍 Validating package..."
twine check dist/*

if [ "$MODE" = "test" ]; then
    echo "🧪 Uploading to TestPyPI..."
    echo ""
    echo "⚠️  IMPORTANT: For TestPyPI, you need to:"
    echo "   1. Create account at https://test.pypi.org/account/register/"
    echo "   2. Get API token from https://test.pypi.org/manage/account/"
    echo "   3. Set environment variables:"
    echo "      export TWINE_USERNAME=__token__"
    echo "      export TWINE_PASSWORD=your_test_pypi_token_here"
    echo ""
    read -p "Have you set the TestPyPI credentials? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Uploaded to TestPyPI!"
        echo "📦 Test installation:"
        echo "   pip install --index-url https://test.pypi.org/simple/ lunvex-code"
    else
        echo "❌ Skipping TestPyPI upload. Set credentials and run again."
        exit 1
    fi
    
elif [ "$MODE" = "prod" ]; then
    echo "🚀 Uploading to Production PyPI..."
    echo ""
    echo "⚠️  IMPORTANT: For Production PyPI, you need to:"
    echo "   1. Create account at https://pypi.org/account/register/"
    echo "   2. Get API token from https://pypi.org/manage/account/"
    echo "   3. Set environment variables:"
    echo "      export TWINE_USERNAME=__token__"
    echo "      export TWINE_PASSWORD=your_pypi_token_here"
    echo ""
    read -p "Have you set the PyPI credentials? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        twine upload dist/*
        echo ""
        echo "🎉 Successfully published to PyPI!"
        echo "📦 Installation:"
        echo "   pip install lunvex-code"
        echo ""
        echo "🔗 Package URL: https://pypi.org/project/lunvex-code/"
    else
        echo "❌ Skipping PyPI upload. Set credentials and run again."
        exit 1
    fi
else
    echo "❌ Invalid mode. Use 'test' or 'prod'"
    echo "Usage: $0 [test|prod]"
    exit 1
fi