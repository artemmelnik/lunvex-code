#!/usr/bin/env python3
"""Test git color highlighting."""

import sys
sys.path.insert(0, '.')

from lunvex_code.tools.git_colors import git_colorizer
from rich.console import Console

console = Console()

# Test data
test_diff = """diff --git a/test.py b/test.py
index abc123..def456 100644
--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
 def hello():
-    print("Hello, World!")
+    print("Hello, Universe!")
 
 def goodbye():
     print("Goodbye!")
"""

test_status = """On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   test.py

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
	modified:   another.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	new_file.py
"""

test_status_short = """M  test.py
 M another.py
?? new_file.py
"""

test_branch = """* main
  feature/login
  feature/api
  remotes/origin/main
  remotes/origin/feature/login
"""

test_log = """commit abc123def4567890abcdef1234567890abcdef12
Author: John Doe <john@example.com>
Date:   Mon Jan 1 12:00:00 2024 +0000

    Initial commit

    This is the first commit message.
    It has multiple lines.

commit def456abc1237890defabc4567890abc123def45
Author: Jane Smith <jane@example.com>
Date:   Tue Jan 2 12:00:00 2024 +0000

    Add new feature

    Implemented the new API endpoint.
"""

test_log_oneline = """abc123d Initial commit
def456a Add new feature
ghi789b Fix bug
"""

test_show = """commit abc123def4567890abcdef1234567890abcdef12
Author: John Doe <john@example.com>
Date:   Mon Jan 1 12:00:00 2024 +0000

    Initial commit

diff --git a/test.py b/test.py
index 0000000..abc1234 100644
--- a/test.py
+++ b/test.py
@@ -0,0 +1,3 @@
+def hello():
+    print("Hello!")
+
"""

def test_all():
    """Test all colorization functions."""
    console.print("\n[bold cyan]=== Testing Git Colorizer ===[/bold cyan]\n")
    
    # Test diff
    console.print("[bold]1. Git Diff:[/bold]")
    colored_diff = git_colorizer.colorize_diff(test_diff)
    # Print raw to see ANSI codes
    print("Raw output with ANSI codes (first 200 chars):")
    print(repr(colored_diff[:200]))
    print("\nRendered:")
    console.print(colored_diff, markup=False)
    
    # Test status
    console.print("\n[bold]2. Git Status (long):[/bold]")
    colored_status = git_colorizer.colorize_status(test_status)
    console.print(colored_status, markup=False)
    
    # Test status short
    console.print("\n[bold]3. Git Status (short):[/bold]")
    colored_status_short = git_colorizer.colorize_status(test_status_short, short=True)
    console.print(colored_status_short, markup=False)
    
    # Test branch
    console.print("\n[bold]4. Git Branch:[/bold]")
    colored_branch = git_colorizer.colorize_branch(test_branch)
    console.print(colored_branch, markup=False)
    
    # Test log
    console.print("\n[bold]5. Git Log (multi-line):[/bold]")
    colored_log = git_colorizer.colorize_log(test_log)
    console.print(colored_log, markup=False)
    
    # Test log oneline
    console.print("\n[bold]6. Git Log (one-line):[/bold]")
    colored_log_oneline = git_colorizer.colorize_log(test_log_oneline, oneline=True)
    console.print(colored_log_oneline, markup=False)
    
    # Test show
    console.print("\n[bold]7. Git Show:[/bold]")
    colored_show = git_colorizer.colorize_show(test_show)
    console.print(colored_show, markup=False)
    
    # Test table
    console.print("\n[bold]8. Branch Table:[/bold]")
    branches = test_branch.strip().split('\n')
    table = git_colorizer.create_branch_table(branches)
    console.print(table)
    
    # Test status summary
    console.print("\n[bold]9. Status Summary:[/bold]")
    summary = git_colorizer.create_status_summary(test_status)
    console.print(summary)
    
    console.print("\n[bold green]✓ All tests completed![/bold green]")

if __name__ == "__main__":
    test_all()