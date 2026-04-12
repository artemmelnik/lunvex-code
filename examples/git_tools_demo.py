#!/usr/bin/env python3
"""Demo script for Git tools integration."""

import os
import tempfile
from pathlib import Path

from lunvex_code.tools.base import create_default_registry


def demo_git_tools():
    """Demonstrate the new Git tools."""
    print("=== LunVex Code Git Tools Demo ===\n")
    
    # Create a temporary Git repository for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        original_cwd = os.getcwd()
        
        try:
            os.chdir(repo_path)
            
            # Initialize Git repository
            print("1. Creating a test Git repository...")
            os.system("git init > /dev/null 2>&1")
            os.system("git config user.email 'demo@example.com'")
            os.system("git config user.name 'Demo User'")
            
            # Create and commit a file
            test_file = repo_path / "demo.txt"
            test_file.write_text("Hello, Git tools!\nThis is a demo file.")
            os.system("git add demo.txt > /dev/null 2>&1")
            os.system("git commit -m 'Initial commit' > /dev/null 2>&1")
            
            # Create another file but don't commit
            another_file = repo_path / "another.txt"
            another_file.write_text("Uncommitted changes")
            
            print("2. Repository created with one commit and uncommitted changes\n")
            
            # Get the tool registry
            registry = create_default_registry()
            
            # Demo git_status
            print("3. Testing git_status tool:")
            status_tool = registry.get("git_status")
            if status_tool:
                result = status_tool.execute()
                print(f"   Success: {result.success}")
                print(f"   Output:\n{result.output}\n")
            
            # Demo git_diff
            print("4. Testing git_diff tool:")
            diff_tool = registry.get("git_diff")
            if diff_tool:
                result = diff_tool.execute()
                print(f"   Success: {result.success}")
                if result.output:
                    print(f"   Output (first 200 chars):\n{result.output[:200]}...\n")
                else:
                    print(f"   Output: (no changes)\n")
            
            # Demo git_log
            print("5. Testing git_log tool:")
            log_tool = registry.get("git_log")
            if log_tool:
                result = log_tool.execute(oneline=True, max_count=3)
                print(f"   Success: {result.success}")
                print(f"   Output:\n{result.output}\n")
            
            # Demo git_show
            print("6. Testing git_show tool:")
            show_tool = registry.get("git_show")
            if show_tool:
                result = show_tool.execute()
                print(f"   Success: {result.success}")
                if result.output:
                    lines = result.output.split('\n')
                    print(f"   Output (first 5 lines):")
                    for line in lines[:5]:
                        print(f"   {line}")
                    print()
            
            # Demo git_branch (list only)
            print("7. Testing git_branch tool (list):")
            branch_tool = registry.get("git_branch")
            if branch_tool:
                result = branch_tool.execute(list=True)
                print(f"   Success: {result.success}")
                print(f"   Output:\n{result.output}\n")
            
            # Show all registered Git tools
            print("8. All registered Git tools:")
            all_tools = registry.list_tools()
            git_tools = [t for t in all_tools if t.startswith("git_")]
            for tool_name in sorted(git_tools):
                tool = registry.get(tool_name)
                print(f"   - {tool_name}: {tool.description}")
                print(f"     Permission level: {tool.permission_level}")
            
            print("\n=== Demo completed successfully ===")
            
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    demo_git_tools()