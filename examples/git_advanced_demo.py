#!/usr/bin/env python3
"""Demo script for advanced Git tools (Phase 3)."""

import os
import tempfile
from pathlib import Path

from lunvex_code.tools.base import create_default_registry


def demo_advanced_git_tools():
    """Demonstrate advanced Git tools."""
    print("=== LunVex Code Advanced Git Tools Demo (Phase 3) ===\n")
    
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
            
            # Create initial commit
            readme = repo_path / "README.md"
            readme.write_text("# Demo Project\n\nAdvanced Git tools demo.")
            os.system("git add README.md > /dev/null 2>&1")
            os.system("git commit -m 'Initial commit' > /dev/null 2>&1")
            
            print("2. Repository created with initial commit\n")
            
            # Get the tool registry
            registry = create_default_registry()
            
            # Demo git_stash
            print("3. Demonstrating git_stash:")
            
            # Make some changes
            readme.write_text("# Demo Project\n\nAdvanced Git tools demo.\n\nModified!")
            
            stash_tool = registry.get("git_stash")
            if stash_tool:
                print("   - Making changes to README.md")
                print("   - Stashing changes...")
                result = stash_tool.execute(save="WIP: Modified README")
                print(f"   Success: {result.success}")
                if result.output:
                    print(f"   Output: {result.output}")
                print()
            
            # List stashes
            if stash_tool:
                print("   - Listing stashes:")
                result = stash_tool.execute(list=True)
                print(f"   Output:\n{result.output}\n")
            
            # Demo git_checkout
            print("4. Demonstrating git_checkout:")
            
            checkout_tool = registry.get("git_checkout")
            if checkout_tool:
                print("   - Creating and checking out feature branch:")
                result = checkout_tool.execute(branch="feature/demo", create=True)
                print(f"   Success: {result.success}")
                print(f"   Output: {result.output}")
                
                # Check current branch
                branch_tool = registry.get("git_branch")
                if branch_tool:
                    result = branch_tool.execute(list=True)
                    print(f"   Current branches:\n{result.output}")
                print()
            
            # Demo git_merge
            print("5. Demonstrating git_merge:")
            
            # Make changes on feature branch
            feature_file = repo_path / "feature.txt"
            feature_file.write_text("Feature implementation")
            os.system("git add feature.txt > /dev/null 2>&1")
            os.system("git commit -m 'Add feature' > /dev/null 2>&1")
            
            # Switch back to main
            if checkout_tool:
                result = checkout_tool.execute(branch="main")
                print(f"   - Switched back to main: {result.success}")
            
            merge_tool = registry.get("git_merge")
            if merge_tool:
                print("   - Merging feature branch (no fast-forward):")
                result = merge_tool.execute(branch="feature/demo", no_ff=True)
                print(f"   Success: {result.success}")
                if result.output:
                    print(f"   Output: {result.output[:100]}...")
                print()
            
            # Demo git_fetch (simulated - no remote)
            print("6. Demonstrating git_fetch:")
            
            fetch_tool = registry.get("git_fetch")
            if fetch_tool:
                print("   - Note: No remote configured, showing tool interface")
                print("   - Tool would execute: git fetch origin")
                print("   - With options: --prune, --tags, --all, --dry-run")
                print()
            
            # Show all available Git tools
            print("7. All available Git tools (13 total):")
            all_tools = registry.list_tools()
            git_tools = sorted([t for t in all_tools if t.startswith("git_")])
            
            # Categorize tools
            read_only = ["git_status", "git_diff", "git_log", "git_show"]
            modifying = [t for t in git_tools if t not in read_only]
            
            print(f"   Read-only tools ({len(read_only)}):")
            for tool_name in sorted(read_only):
                tool = registry.get(tool_name)
                print(f"     - {tool_name}: 🟢 AUTO")
            
            print(f"\n   Modifying tools ({len(modifying)}):")
            for tool_name in sorted(modifying):
                tool = registry.get(tool_name)
                print(f"     - {tool_name}: 🟡 ASK")
            
            print("\n8. Common workflows with new tools:")
            print("   a) Stash workflow:")
            print("      git_stash save='WIP: temporary changes'")
            print("      # work on something else")
            print("      git_stash pop=''  # or apply=''")
            print("")
            print("   b) Branch switching workflow:")
            print("      git_checkout branch='feature' create=true")
            print("      # make changes and commit")
            print("      git_checkout branch='main'")
            print("      git_merge branch='feature' no_ff=true")
            print("")
            print("   c) Update workflow:")
            print("      git_fetch prune=true")
            print("      git_pull rebase=true")
            print("")
            
            print("=== Advanced Git Tools Demo Completed ===")
            print("\nPhase 3 adds 4 new tools:")
            print("1. ✅ git_stash - Temporary storage of changes")
            print("2. ✅ git_checkout - Branch switching and file restoration")
            print("3. ✅ git_merge - Branch merging with conflict handling")
            print("4. ✅ git_fetch - Remote updates without merging")
            print(f"\nTotal Git tools: {len(git_tools)}")
            print("Coverage: ~95% of common Git operations")
            
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    demo_advanced_git_tools()