#!/usr/bin/env python3
"""Test git tools integration."""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project to path
sys.path.insert(0, '.')

from lunvex_code.tools.git_tools import (
    GitStatusTool, GitDiffTool, GitBranchTool, GitLogTool, GitShowTool
)
from lunvex_code.tools.git_colors import git_colorizer

def create_test_repo():
    """Create a test git repository."""
    temp_dir = tempfile.mkdtemp(prefix="test_git_")
    repo_path = Path(temp_dir) / "test_repo"
    repo_path.mkdir(parents=True)
    
    os.chdir(repo_path)
    
    # Initialize git repo
    os.system("git init")
    os.system("git config user.email 'test@example.com'")
    os.system("git config user.name 'Test User'")
    
    # Create initial commit
    (repo_path / "file1.txt").write_text("Hello World\n")
    (repo_path / "file2.py").write_text("def hello():\n    print('Hello')\n")
    
    os.system("git add .")
    os.system("git commit -m 'Initial commit'")
    
    # Make some changes
    (repo_path / "file1.txt").write_text("Hello Universe\n")
    (repo_path / "new_file.txt").write_text("New file\n")
    
    # Create a branch
    os.system("git checkout -b feature/test")
    (repo_path / "file2.py").write_text("def hello():\n    print('Hello World!')\n")
    os.system("git add .")
    os.system("git commit -m 'Update greeting'")
    
    os.system("git checkout main")
    
    return repo_path, temp_dir

def test_git_tools():
    """Test git tools with color highlighting."""
    repo_path, temp_dir = create_test_repo()
    
    try:
        print(f"Testing in repository: {repo_path}")
        print("=" * 60)
        
        # Test GitStatusTool
        print("\n1. Testing git_status:")
        tool = GitStatusTool()
        result = tool.execute()
        print(f"Success: {result.success}")
        if result.output:
            print("Output (with colors):")
            print(result.output)
        
        print("\n" + "=" * 60)
        
        # Test GitDiffTool
        print("\n2. Testing git_diff:")
        tool = GitDiffTool()
        result = tool.execute()
        print(f"Success: {result.success}")
        if result.output:
            print("Output (with colors):")
            print(result.output)
        
        print("\n" + "=" * 60)
        
        # Test GitBranchTool
        print("\n3. Testing git_branch:")
        tool = GitBranchTool()
        result = tool.execute(list=True)
        print(f"Success: {result.success}")
        if result.output:
            print("Output (with colors):")
            print(result.output)
        
        print("\n" + "=" * 60)
        
        # Test GitLogTool
        print("\n4. Testing git_log:")
        tool = GitLogTool()
        result = tool.execute(oneline=True, max_count=5)
        print(f"Success: {result.success}")
        if result.output:
            print("Output (with colors):")
            print(result.output)
        
        print("\n" + "=" * 60)
        
        # Test GitShowTool
        print("\n5. Testing git_show:")
        tool = GitShowTool()
        result = tool.execute()
        print(f"Success: {result.success}")
        if result.output:
            print("Output (with colors):")
            # Show first 200 chars
            print(result.output[:200] + "..." if len(result.output) > 200 else result.output)
        
        print("\n" + "=" * 60)
        
        # Test colorizer directly
        print("\n6. Testing git_colorizer directly:")
        os.system("git status --short > status_short.txt")
        with open("status_short.txt", "r") as f:
            status_output = f.read()
        
        colored = git_colorizer.colorize_status(status_output, short=True)
        print("Colored status (short):")
        print(colored)
        
    finally:
        # Cleanup
        os.chdir("/")
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up: {temp_dir}")

if __name__ == "__main__":
    test_git_tools()