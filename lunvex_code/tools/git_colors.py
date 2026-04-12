"""Color highlighting for Git output."""

import re
from typing import Optional, Tuple, List, Dict
from rich.text import Text
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table

console = Console(force_terminal=True, color_system="auto")


class GitColorizer:
    """Colorize Git command output."""
    
    # Git diff patterns
    DIFF_HEADER_PATTERN = r'^diff --git'
    DIFF_INDEX_PATTERN = r'^index [a-f0-9]+\.\.[a-f0-9]+'
    DIFF_MODE_PATTERN = r'^(new|deleted) file mode \d+'
    DIFF_FROM_FILE_PATTERN = r'^--- (a/)?'
    DIFF_TO_FILE_PATTERN = r'^\+\+\+ (b/)?'
    DIFF_HUNK_PATTERN = r'^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@'
    DIFF_ADDED_LINE_PATTERN = r'^\+'
    DIFF_REMOVED_LINE_PATTERN = r'^-'
    DIFF_CONTEXT_LINE_PATTERN = r'^ '
    
    # Git status patterns
    STATUS_STAGED_PATTERN = r'^[MADRC]'
    STATUS_UNSTAGED_PATTERN = r'^.[MADRC]'
    STATUS_UNTRACKED_PATTERN = r'^\?\?'
    STATUS_RENAMED_PATTERN = r'^R'
    STATUS_BRANCH_PATTERN = r'^##? '
    
    # Git branch patterns
    BRANCH_CURRENT_PATTERN = r'^\* '
    BRANCH_REMOTE_PATTERN = r'^  remotes/'
    BRANCH_LOCAL_PATTERN = r'^  '
    
    # Git log patterns
    LOG_COMMIT_PATTERN = r'^commit [a-f0-9]{40}'
    LOG_AUTHOR_PATTERN = r'^Author:'
    LOG_DATE_PATTERN = r'^Date:'
    LOG_MESSAGE_PATTERN = r'^    '
    
    def _text_to_ansi(self, text_obj: Text) -> str:
        """Convert Rich Text object to string with ANSI codes."""
        with console.capture() as capture:
            console.print(text_obj, end="")
        return capture.get()
    
    def colorize_diff(self, diff_output: str) -> str:
        """Colorize git diff output and return string with ANSI codes."""
        lines = diff_output.split('\n')
        result = Text()
        
        for i, line in enumerate(lines):
            if re.match(self.DIFF_HEADER_PATTERN, line):
                result.append(line + '\n', style="bold cyan")
            elif re.match(self.DIFF_INDEX_PATTERN, line):
                result.append(line + '\n', style="dim cyan")
            elif re.match(self.DIFF_MODE_PATTERN, line):
                result.append(line + '\n', style="yellow")
            elif re.match(self.DIFF_FROM_FILE_PATTERN, line):
                result.append(line + '\n', style="red")
            elif re.match(self.DIFF_TO_FILE_PATTERN, line):
                result.append(line + '\n', style="green")
            elif re.match(self.DIFF_HUNK_PATTERN, line):
                result.append(line + '\n', style="bold magenta")
            elif re.match(self.DIFF_ADDED_LINE_PATTERN, line):
                result.append(line + '\n', style="green")
            elif re.match(self.DIFF_REMOVED_LINE_PATTERN, line):
                result.append(line + '\n', style="red")
            elif re.match(self.DIFF_CONTEXT_LINE_PATTERN, line):
                result.append(line + '\n', style="dim")
            else:
                result.append(line + '\n')
        
        return self._text_to_ansi(result)
    
    def colorize_status(self, status_output: str, short: bool = False) -> str:
        """Colorize git status output and return string with ANSI codes."""
        lines = status_output.split('\n')
        result = Text()
        
        for line in lines:
            if not line:
                continue
                
            if short:
                # Short format: XY filename
                if len(line) >= 2:
                    status = line[:2]
                    filename = line[3:] if len(line) > 2 else ""
                    
                    if status[0] in 'MADRC':
                        # Staged changes
                        result.append(status[0], style="green")
                    else:
                        result.append(status[0], style="dim")
                        
                    if status[1] in 'MADRC':
                        # Unstaged changes
                        result.append(status[1], style="red")
                    elif status[1] == '?':
                        # Untracked
                        result.append(status[1], style="yellow")
                    else:
                        result.append(status[1], style="dim")
                        
                    result.append(f" {filename}\n")
                else:
                    result.append(line + '\n')
            else:
                # Long format
                if re.match(self.STATUS_BRANCH_PATTERN, line):
                    # Branch info
                    result.append(line + '\n', style="bold cyan")
                elif re.match(self.STATUS_STAGED_PATTERN, line):
                    # Staged changes
                    result.append(line + '\n', style="green")
                elif re.match(self.STATUS_UNSTAGED_PATTERN, line):
                    # Unstaged changes
                    result.append(line + '\n', style="red")
                elif re.match(self.STATUS_UNTRACKED_PATTERN, line):
                    # Untracked files
                    result.append(line + '\n', style="yellow")
                elif re.match(self.STATUS_RENAMED_PATTERN, line):
                    # Renamed files
                    result.append(line + '\n', style="magenta")
                else:
                    result.append(line + '\n')
        
        return self._text_to_ansi(result)
    
    def colorize_branch(self, branch_output: str) -> str:
        """Colorize git branch output and return string with ANSI codes."""
        lines = branch_output.split('\n')
        result = Text()
        
        for line in lines:
            if not line:
                continue
                
            if re.match(self.BRANCH_CURRENT_PATTERN, line):
                # Current branch
                result.append(line + '\n', style="bold green")
            elif re.match(self.BRANCH_REMOTE_PATTERN, line):
                # Remote branches
                result.append(line + '\n', style="dim cyan")
            elif re.match(self.BRANCH_LOCAL_PATTERN, line):
                # Local branches
                result.append(line + '\n', style="cyan")
            else:
                result.append(line + '\n')
        
        return self._text_to_ansi(result)
    
    def colorize_log(self, log_output: str, oneline: bool = False) -> str:
        """Colorize git log output and return string with ANSI codes."""
        lines = log_output.split('\n')
        result = Text()
        
        if oneline:
            # One-line format
            for line in lines:
                if not line:
                    continue
                    
                # Parse one-line format: commit_hash (branch/tag) author date message
                parts = line.split(' ', 1)
                if len(parts) >= 2:
                    commit_hash = parts[0]
                    rest = parts[1]
                    
                    # Color commit hash
                    result.append(commit_hash[:7], style="yellow")
                    result.append(commit_hash[7:] + ' ', style="dim yellow")
                    
                    # Color the rest
                    result.append(rest + '\n')
                else:
                    result.append(line + '\n')
        else:
            # Multi-line format
            in_message = False
            for line in lines:
                if not line:
                    if in_message:
                        in_message = False
                    result.append('\n')
                    continue
                    
                if re.match(self.LOG_COMMIT_PATTERN, line):
                    # Commit hash
                    result.append(line + '\n', style="bold yellow")
                    in_message = False
                elif re.match(self.LOG_AUTHOR_PATTERN, line):
                    # Author
                    result.append(line + '\n', style="cyan")
                    in_message = False
                elif re.match(self.LOG_DATE_PATTERN, line):
                    # Date
                    result.append(line + '\n', style="magenta")
                    in_message = False
                elif re.match(self.LOG_MESSAGE_PATTERN, line):
                    # Message (indented)
                    result.append(line + '\n', style="white")
                    in_message = True
                elif in_message:
                    # Continuation of message
                    result.append(line + '\n', style="white")
                else:
                    result.append(line + '\n')
        
        return self._text_to_ansi(result)
    
    def colorize_show(self, show_output: str) -> str:
        """Colorize git show output and return string with ANSI codes."""
        # git show output is similar to diff + log
        lines = show_output.split('\n')
        result = Text()
        
        in_diff = False
        for i, line in enumerate(lines):
            if not line:
                result.append('\n')
                continue
                
            # Check if we're in diff section
            if re.match(self.DIFF_HEADER_PATTERN, line):
                in_diff = True
                
            if in_diff:
                # Use diff coloring
                if re.match(self.DIFF_HEADER_PATTERN, line):
                    result.append(line + '\n', style="bold cyan")
                elif re.match(self.DIFF_HUNK_PATTERN, line):
                    result.append(line + '\n', style="bold magenta")
                elif re.match(self.DIFF_ADDED_LINE_PATTERN, line):
                    result.append(line + '\n', style="green")
                elif re.match(self.DIFF_REMOVED_LINE_PATTERN, line):
                    result.append(line + '\n', style="red")
                else:
                    result.append(line + '\n')
            else:
                # Use log coloring
                if re.match(self.LOG_COMMIT_PATTERN, line):
                    result.append(line + '\n', style="bold yellow")
                elif re.match(self.LOG_AUTHOR_PATTERN, line):
                    result.append(line + '\n', style="cyan")
                elif re.match(self.LOG_DATE_PATTERN, line):
                    result.append(line + '\n', style="magenta")
                else:
                    result.append(line + '\n')
        
        return self._text_to_ansi(result)
    
    def create_branch_table(self, branches: List[str]) -> Table:
        """Create a rich table for branch listing."""
        table = Table(title="Branches", show_header=True, header_style="bold magenta")
        table.add_column("Current", style="cyan", width=8)
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Upstream", style="dim", width=20)
        
        for branch in branches:
            if not branch.strip():
                continue
                
            current = "*" if branch.startswith("* ") else ""
            name = branch[2:] if branch.startswith("* ") else branch[2:] if branch.startswith("  ") else branch
            
            branch_type = "local"
            upstream = ""
            
            if "remotes/" in name:
                branch_type = "remote"
                name = name.replace("  ", "")
            elif "->" in name:
                # Tracking branch
                parts = name.split("->")
                name = parts[0].strip()
                upstream = parts[1].strip()
                branch_type = "tracking"
            
            table.add_row(current, name.strip(), branch_type, upstream)
        
        return table
    
    def create_status_summary(self, status_output: str) -> Panel:
        """Create a summary panel for git status."""
        lines = status_output.split('\n')
        
        staged = 0
        unstaged = 0
        untracked = 0
        branch_info = ""
        
        for line in lines:
            if line.startswith("## "):
                branch_info = line[3:]
            elif line.startswith("Changes to be committed:"):
                # Next lines will be staged changes
                pass
            elif line.startswith("Changes not staged for commit:"):
                # Next lines will be unstaged changes
                pass
            elif line.startswith("Untracked files:"):
                # Next lines will be untracked files
                pass
            elif line.startswith("\t") or line.startswith("  "):
                # Actual file entries
                if "new file:" in line or "modified:" in line or "deleted:" in line:
                    if "Changes to be committed" in '\n'.join(lines[:lines.index(line)]):
                        staged += 1
                    else:
                        unstaged += 1
                elif "Untracked files" in '\n'.join(lines[:lines.index(line)]):
                    untracked += 1
        
        summary_text = Text()
        if branch_info:
            summary_text.append(f"Branch: {branch_info}\n", style="bold cyan")
        
        summary_text.append(f"Staged: {staged} ", style="green")
        summary_text.append(f"Unstaged: {unstaged} ", style="red")
        summary_text.append(f"Untracked: {untracked}", style="yellow")
        
        return Panel(summary_text, title="Git Status Summary", border_style="cyan")


# Singleton instance
git_colorizer = GitColorizer()