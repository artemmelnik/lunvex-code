#!/usr/bin/env python3
"""Demo script for Git workflow tools."""

import os
import tempfile
from pathlib import Path

from lunvex_code.tools.base import create_default_registry


def demo_git_workflow():
    """Demonstrate the complete Git workflow."""
    print("=== LunVex Code Git Workflow Demo ===\n")
    
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
            
            print("2. Repository created\n")
            
            # Get the tool registry
            registry = create_default_registry()
            
            # Create initial files
            print("3. Creating initial files...")
            readme = repo_path / "README.md"
            readme.write_text("# Demo Project\n\nThis is a demo project.")
            
            main_py = repo_path / "main.py"
            main_py.write_text("print('Hello, World!')\n")
            
            # Demo git_status - show untracked files
            print("\n4. Checking status (untracked files):")
            status_tool = registry.get("git_status")
            if status_tool:
                result = status_tool.execute()
                print(f"   Output:\n{result.output}\n")
            
            # Demo git_add - stage files
            print("5. Staging files with git_add:")
            add_tool = registry.get("git_add")
            if add_tool:
                result = add_tool.execute(paths="README.md main.py")
                print(f"   Success: {result.success}")
                if result.output:
                    print(f"   Output: {result.output}")
                print()
            
            # Check status after add
            print("6. Checking status after git_add:")
            if status_tool:
                result = status_tool.execute()
                print(f"   Output:\n{result.output}\n")
            
            # Demo git_commit - create commit
            print("7. Creating commit with git_commit:")
            commit_tool = registry.get("git_commit")
            if commit_tool:
                result = commit_tool.execute(message="Initial commit: Add README and main.py")
                print(f"   Success: {result.success}")
                print(f"   Output: {result.output}\n")
            
            # Check status after commit
            print("8. Checking status after commit:")
            if status_tool:
                result = status_tool.execute()
                print(f"   Output:\n{result.output}\n")
            
            # Demo git_log - show commit history
            print("9. Showing commit history with git_log:")
            log_tool = registry.get("git_log")
            if log_tool:
                result = log_tool.execute(oneline=True)
                print(f"   Output:\n{result.output}\n")
            
            # Make some changes
            print("10. Making changes to files...")
            readme.write_text("# Demo Project\n\nThis is a demo project.\n\nUpdated!")
            
            # Demo git_diff - show changes
            print("\n11. Showing changes with git_diff:")
            diff_tool = registry.get("git_diff")
            if diff_tool:
                result = diff_tool.execute()
                print(f"   Success: {result.success}")
                if result.output:
                    print(f"   Output (first 200 chars):\n{result.output[:200]}...")
                else:
                    print(f"   Output: (no changes)")
                print()
            
            # Demo git_diff with stat
            print("12. Showing diffstat:")
            if diff_tool:
                result = diff_tool.execute(stat=True)
                print(f"   Output:\n{result.output}\n")
            
            # Demo git_branch - create feature branch
            print("13. Creating feature branch with git_branch:")
            branch_tool = registry.get("git_branch")
            if branch_tool:
                result = branch_tool.execute(create="feature/demo")
                print(f"   Success: {result.success}")
                print(f"   Output: {result.output}\n")
            
            # List branches
            print("14. Listing branches:")
            if branch_tool:
                result = branch_tool.execute(list=True, verbose=True)
                print(f"   Output:\n{result.output}\n")
            
            # Demo git_show - show commit details
            print("15. Showing commit details with git_show:")
            show_tool = registry.get("git_show")
            if show_tool:
                result = show_tool.execute()
                print(f"   Success: {result.success}")
                lines = result.output.split('\n')
                print(f"   Output (first 10 lines):")
                for line in lines[:10]:
                    print(f"   {line}")
                print()
            
            # Show all available Git tools
            print("16. All available Git tools:")
            all_tools = registry.list_tools()
            git_tools = sorted([t for t in all_tools if t.startswith("git_")])
            
            for tool_name in git_tools:
                tool = registry.get(tool_name)
                permission = "🟢 AUTO" if tool.permission_level == "auto" else "🟡 ASK"
                print(f"   - {tool_name}: {permission}")
                print(f"     {tool.description[:60]}...")
            
            print("\n=== Git Workflow Demo Completed ===")
            print("\nWorkflow demonstrated:")
            print("1. ✅ Repository initialization")
            print("2. ✅ File creation")
            print("3. ✅ Status checking")
            print("4. ✅ Staging changes (git_add)")
            print("5. ✅ Committing changes (git_commit)")
            print("6. ✅ Viewing history (git_log)")
            print("7. ✅ Viewing changes (git_diff)")
            print("8. ✅ Branch management (git_branch)")
            print("9. ✅ Commit inspection (git_show)")
            
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    demo_git_workflow()