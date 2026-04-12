#!/usr/bin/env python3
"""Fix git colors methods to use console.capture()."""

import re

def fix_git_colors():
    with open('lunvex_code/tools/git_colors.py', 'r') as f:
        content = f.read()
    
    # Find all colorize methods and fix their return statements
    pattern = r'(def colorize_\w+\(.*?\) -> str:.*?\n        return )console\.render_str\(result\)'
    
    def replace_return(match):
        return match.group(1) + """# Convert Text to string with ANSI codes
        with console.capture() as capture:
            console.print(result, end="")
        return capture.get()"""
    
    # Update all colorize methods
    new_content = re.sub(pattern, replace_return, content, flags=re.DOTALL)
    
    with open('lunvex_code/tools/git_colors.py', 'w') as f:
        f.write(new_content)
    
    print("Fixed git colors methods!")

if __name__ == "__main__":
    fix_git_colors()