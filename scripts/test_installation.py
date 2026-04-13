#!/usr/bin/env python3
"""
Test script to verify LunVex Code installation from PyPI.
Run this after publishing to verify the package works correctly.
"""

import subprocess
import sys
import os

def run_command(cmd, capture_output=True):
    """Run a shell command and return result."""
    print(f"🚀 Running: {cmd}")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, shell=True, text=True)
        return result
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return None

def test_installation():
    """Test that lunvex-code is properly installed."""
    print("=" * 60)
    print("🧪 Testing LunVex Code Installation")
    print("=" * 60)
    
    # Test 1: Check if command exists
    print("\n1. Testing 'lunvex-code --version'")
    result = run_command("lunvex-code --version")
    if result and result.returncode == 0:
        print(f"✅ Version: {result.stdout.strip()}")
    else:
        print(f"❌ Failed: {result.stderr if result else 'Command not found'}")
        return False
    
    # Test 2: Check help command
    print("\n2. Testing 'lunvex-code --help'")
    result = run_command("lunvex-code --help")
    if result and result.returncode == 0:
        print("✅ Help command works")
        # Check for expected commands
        expected_commands = ['run', 'init', 'history', 'version']
        output = result.stdout.lower()
        missing = [cmd for cmd in expected_commands if cmd not in output]
        if not missing:
            print("✅ All expected commands found")
        else:
            print(f"⚠️  Missing commands: {missing}")
    else:
        print(f"❌ Help command failed")
        return False
    
    # Test 3: Check short alias
    print("\n3. Testing short alias 'lvc --version'")
    result = run_command("lvc --version")
    if result and result.returncode == 0:
        print(f"✅ Short alias works: {result.stdout.strip()}")
    else:
        print("⚠️  Short alias not working (this might be OK)")
    
    # Test 4: Test Python import
    print("\n4. Testing Python import")
    try:
        import lunvex_code
        print(f"✅ Python import successful: lunvex_code v{lunvex_code.__version__}")
        
        # Check key modules
        modules = ['agent', 'async_agent', 'cli', 'llm', 'tools']
        for module in modules:
            try:
                __import__(f'lunvex_code.{module}')
                print(f"  ✅ Module 'lunvex_code.{module}' available")
            except ImportError as e:
                print(f"  ⚠️  Module 'lunvex_code.{module}' not available: {e}")
                
    except ImportError as e:
        print(f"❌ Python import failed: {e}")
        return False
    
    # Test 5: Check package metadata
    print("\n5. Checking package metadata")
    try:
        import importlib.metadata
        metadata = importlib.metadata.metadata('lunvex-code')
        print(f"✅ Package: {metadata['Name']}")
        print(f"✅ Version: {metadata['Version']}")
        print(f"✅ Author: {metadata['Author']}")
        print(f"✅ Description: {metadata['Summary']}")
    except Exception as e:
        print(f"⚠️  Could not read metadata: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Installation test completed successfully!")
    print("=" * 60)
    return True

def test_from_testpypi():
    """Test installation from TestPyPI."""
    print("\n" + "=" * 60)
    print("🧪 Testing installation from TestPyPI")
    print("=" * 60)
    
    # First uninstall if exists
    print("\n1. Uninstalling existing version...")
    run_command("pip uninstall -y lunvex-code", capture_output=False)
    
    # Install from TestPyPI
    print("\n2. Installing from TestPyPI...")
    result = run_command("pip install --index-url https://test.pypi.org/simple/ lunvex-code")
    if result and result.returncode == 0:
        print("✅ Installed from TestPyPI")
        return test_installation()
    else:
        print(f"❌ Failed to install from TestPyPI: {result.stderr if result else 'Unknown error'}")
        return False

def test_from_pypi():
    """Test installation from Production PyPI."""
    print("\n" + "=" * 60)
    print("🧪 Testing installation from Production PyPI")
    print("=" * 60)
    
    # First uninstall if exists
    print("\n1. Uninstalling existing version...")
    run_command("pip uninstall -y lunvex-code", capture_output=False)
    
    # Install from PyPI
    print("\n2. Installing from PyPI...")
    result = run_command("pip install lunvex-code")
    if result and result.returncode == 0:
        print("✅ Installed from PyPI")
        return test_installation()
    else:
        print(f"❌ Failed to install from PyPI: {result.stderr if result else 'Unknown error'}")
        return False

if __name__ == "__main__":
    print("LunVex Code Installation Test Script")
    print("Usage: python test_installation.py [testpypi|pypi|local]")
    print()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "testpypi":
            success = test_from_testpypi()
        elif mode == "pypi":
            success = test_from_pypi()
        elif mode == "local":
            success = test_installation()
        else:
            print(f"❌ Unknown mode: {mode}")
            success = False
    else:
        # Default: test local installation
        success = test_installation()
    
    sys.exit(0 if success else 1)