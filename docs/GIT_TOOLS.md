# Git Tools Integration

LunVex Code now includes specialized Git tools that provide structured, safe access to Git operations with better UX than raw bash commands.

## Overview

The Git tools integration provides:

1. **Structured output** - JSON and formatted text output
2. **Safety controls** - Permission levels for different operations
3. **Better UX** - Clean, focused interfaces for common Git tasks
4. **Consistency** - Uniform error handling and parameter validation

## Available Git Tools

### 1. `git_status` - Show Working Tree Status
**Permission Level:** AUTO (read-only, safe)

Shows the working tree status including staged, unstaged, and untracked files.

**Parameters:**
- `short` (bool): Give output in short format
- `porcelain` (bool): Easy-to-parse format for scripts
- `branch` (bool): Show branch and tracking info
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_status
git_status short=true
git_status format="json"
```

### 2. `git_diff` - Show Changes
**Permission Level:** AUTO (read-only, safe)

Shows changes between commits, commit and working tree, etc.

**Parameters:**
- `cached` (bool): Show diff of staged changes
- `staged` (bool): Synonym for --cached
- `file` (str): Show diff for specific file only
- `stat` (bool): Generate diffstat instead of patch
- `name_only` (bool): Show only names of changed files
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_diff
git_diff cached=true
git_diff file="src/main.py" stat=true
```

### 3. `git_log` - Show Commit Logs
**Permission Level:** AUTO (read-only, safe)

Shows commit logs with various formatting options.

**Parameters:**
- `max_count` (int): Limit number of commits to output
- `oneline` (bool): Show each commit on a single line
- `graph` (bool): Draw text-based graphical representation
- `decorate` (bool): Print ref names of commits shown
- `since` (str): Show commits more recent than date
- `author` (str): Limit commits to specific author
- `grep` (str): Limit commits with log message matching pattern
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_log
git_log oneline=true max_count=10
git_log author="john@example.com" since="2024-01-01"
```

### 4. `git_show` - Show Objects
**Permission Level:** AUTO (read-only, safe)

Shows various types of objects (commits, tags, trees, blobs).

**Parameters:**
- `object` (str): Object to show (commit hash, tag, branch). Defaults to HEAD
- `stat` (bool): Show diffstat instead of patch
- `name_only` (bool): Show only names of changed files
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_show
git_show object="v1.0.0"
git_show stat=true
```

### 5. `git_branch` - Manage Branches
**Permission Level:** ASK (can modify branches)

List, create, or delete branches.

**Parameters:**
- `list` (bool): List branches (default action)
- `all` (bool): List both remote-tracking and local branches
- `remote` (bool): List remote-tracking branches
- `verbose` (bool): Show SHA-1 and commit subject line
- `create` (str): Create a new branch with given name
- `delete` (str): Delete a branch (use with caution)
- `force_delete` (bool): Force deletion (unmerged branches)
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_branch list=true
git_branch list=true verbose=true
git_branch create="feature/new-feature"
# Note: delete operations require user confirmation
```

### 6. `git_add` - Stage Changes
**Permission Level:** ASK (modifies staging area)

Add file contents to the index (stage changes).

**Parameters:**
- `paths` (str): Files to add content from. Can be file paths, directories, or '.' for all
- `all` (bool): Add changes from all tracked and untracked files
- `update` (bool): Only match tracked files (skip untracked)
- `dry_run` (bool): Don't actually add, just show what would be added
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_add paths="file.txt"
git_add paths="file1.txt file2.txt"
git_add paths="." all=true
git_add paths="*.py" dry_run=true
```

### 7. `git_commit` - Create Commits
**Permission Level:** ASK (creates commits)

Record changes to the repository.

**Parameters:**
- `message` (str): Commit message (required)
- `all` (bool): Automatically stage files that have been modified and deleted
- `amend` (bool): Amend previous commit
- `no_verify` (bool): Bypass pre-commit and commit-msg hooks
- `allow_empty` (bool): Allow empty commit (no changes)
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_commit message="Fix bug in authentication"
git_commit message="Update documentation" all=true
git_commit message="Fix typo" amend=true
```

### 8. `git_push` - Push to Remote
**Permission Level:** ASK (modifies remote repository)

Update remote refs along with associated objects.

**Parameters:**
- `remote` (str): Remote repository to push to (default: origin)
- `branch` (str): Branch to push (default: current branch)
- `force` (bool): Force push (dangerous - can lose remote history)
- `force_with_lease` (bool): Force push with lease (safer than --force)
- `tags` (bool): Push all tags
- `dry_run` (bool): Do everything except actually send the updates
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_push
git_push remote="upstream" branch="main"
git_push tags=true
git_push dry_run=true  # Safe check before actual push
```

### 9. `git_pull` - Pull from Remote
**Permission Level:** ASK (modifies local repository)

Fetch from and integrate with another repository or a local branch.

**Parameters:**
- `remote` (str): Remote repository to pull from (default: origin)
- `branch` (str): Branch to pull (default: current branch)
- `rebase` (bool): Use rebase instead of merge
- `no_commit` (bool): Do not create a merge commit
- `ff_only` (bool): Allow only fast-forward merges
- `dry_run` (bool): Show what would be done without actually doing it
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_pull
git_pull rebase=true
git_pull remote="upstream" branch="develop"
git_pull dry_run=true  # Check before pulling
```

### 10. `git_stash` - Stash Changes
**Permission Level:** ASK (modifies working directory)

Stash the changes in a dirty working directory away.

**Parameters:**
- `save` (str): Save stash with custom message
- `list` (bool): List stash entries
- `show` (str): Show changes recorded in stash (default: latest)
- `pop` (str): Remove and apply stashed state (default: latest)
- `apply` (str): Apply changes recorded in stash (default: latest)
- `drop` (str): Remove stash entry (default: latest)
- `clear` (bool): Remove all stash entries
- `include_untracked` (bool): Include untracked files in stash
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_stash save="WIP: temporary changes"
git_stash list=true
git_stash pop=""  # Apply and remove latest stash
git_stash apply="stash@{1}"  # Apply specific stash
git_stash clear=true  # Remove all stashes
```

### 11. `git_checkout` - Switch Branches
**Permission Level:** ASK (can modify working directory)

Switch branches or restore working tree files.

**Parameters:**
- `branch` (str): Branch to checkout
- `create` (bool): Create and checkout new branch
- `force` (bool): Force checkout (discard local changes)
- `file` (str): Restore specific file from index
- `theirs` (bool): Checkout 'their' version for unmerged paths
- `ours` (bool): Checkout 'our' version for unmerged paths
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_checkout branch="feature"
git_checkout branch="new-feature" create=true
git_checkout file="src/main.py"  # Restore file from index
git_checkout branch="main" force=true  # Discard changes
```

### 12. `git_merge` - Merge Branches
**Permission Level:** ASK (modifies repository history)

Join two or more development histories together.

**Parameters:**
- `branch` (str): Branch to merge into current branch (required)
- `no_ff` (bool): Create merge commit even if fast-forward is possible
- `ff_only` (bool): Allow only fast-forward merges
- `squash` (bool): Create single commit instead of merging
- `no_commit` (bool): Perform merge but don't commit
- `abort` (bool): Abort current conflict resolution process
- `continue` (bool): Continue after resolving merge conflicts
- `message` (str): Merge commit message
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_merge branch="feature"
git_merge branch="feature" no_ff=true  # Always create merge commit
git_merge branch="feature" squash=true  # Squash into single commit
git_merge abort=true  # Abort conflicted merge
git_merge continue=true  # Continue after resolving conflicts
```

### 13. `git_fetch` - Fetch from Remote
**Permission Level:** ASK (updates local refs)

Download objects and refs from another repository.

**Parameters:**
- `remote` (str): Remote repository to fetch from (default: origin)
- `all` (bool): Fetch all remotes
- `prune` (bool): Remove remote-tracking references that no longer exist
- `tags` (bool): Fetch all tags
- `dry_run` (bool): Show what would be done without making changes
- `format` (str): Output format: 'text' or 'json'

**Example:**
```bash
# In LunVex Code session
git_fetch
git_fetch all=true  # Fetch all remotes
git_fetch prune=true  # Clean up deleted remote branches
git_fetch tags=true  # Fetch tags
git_fetch dry_run=true  # Safe check before fetching
```

## Permission System

Git tools integrate with LunVex Code's permission system:

### Permission Levels:
- **AUTO**: Read-only operations (`git_status`, `git_diff`, `git_log`, `git_show`)
- **ASK**: Operations that modify state (`git_branch`, `git_add`, `git_commit`, `git_push`, `git_pull`)
- **DENY**: Dangerous operations (handled at bash level for raw git commands)

### Safety Features:
1. **Read-only by default**: Most Git tools are read-only
2. **Structured validation**: Parameters are validated before execution
3. **Error handling**: Consistent error messages and recovery
4. **Session safety**: Operations respect trust/yolo modes

## Comparison with Bash Tool

### Advantages of Git Tools:
1. **Structured output**: JSON format available for programmatic use
2. **Better error handling**: Consistent error messages
3. **Parameter validation**: Type checking and validation
4. **Focused interfaces**: Each tool does one thing well
5. **Permission granularity**: Fine-grained control per operation

### When to Use Bash Tool:
- Uncommon Git operations not covered by specialized tools
- Complex Git command chains
- Operations needing shell features (pipes, redirects)

## Usage Examples

### Basic Workflow:
```bash
# Check status
git_status

# See what changed
git_diff

# Review recent commits
git_log oneline=true max_count=5

# Create a feature branch
git_branch create="feature/authentication"
```

### JSON Output:
```bash
# Get structured output
git_status format="json"
# Returns: {"success": true, "output": "...", "error": null, ...}
```

### Integration with Other Tools:
```bash
# Combine with file tools
read_file path="CHANGELOG.md"
git_status
git_diff stat=true
```

## Implementation Details

### Architecture:
- **Base Class**: `GitToolBase` handles Git root detection and command execution
- **Result Formatting**: Consistent text and JSON output formatting
- **Error Handling**: Structured error results with exit codes
- **Permission Integration**: Tools declare their permission levels

### Safety:
1. **Git root detection**: Automatically finds repository root
2. **Command validation**: Validates parameters before execution
3. **Timeout handling**: Commands timeout after 30 seconds by default
4. **Output limits**: Very long output is truncated with indication

## Future Enhancements

### Completed Tools:
1. ✅ `git_status` - Check repository status
2. ✅ `git_diff` - View changes
3. ✅ `git_log` - Browse commit history
4. ✅ `git_show` - Show commit details
5. ✅ `git_branch` - List/create/delete branches
6. ✅ `git_add` - Stage changes
7. ✅ `git_commit` - Create commits with messages
8. ✅ `git_push` - Push to remote (with safety checks)
9. ✅ `git_pull` - Pull from remote
10. ✅ `git_stash` - Stash changes
11. ✅ `git_checkout` - Switch branches or restore files
12. ✅ `git_merge` - Merge branches (with conflict detection)
13. ✅ `git_fetch` - Download objects and refs from remote

### Future Tools (Phase 4):
1. `git_tag` - Create, list, delete tags
2. `git_rebase` - Reapply commits on top of another base tip
3. `git_reset` - Reset current HEAD to specified state
4. `git_remote` - Manage set of tracked repositories
5. `git_config` - Get and set repository options

### Advanced Features:
1. **Conflict resolution helpers**
2. **Interactive rebase support**
3. **GitHub/GitLab API integration**
4. **Visual branch diagrams**
5. **Commit message generation**

## Migration from Bash

### For Existing Users:
- Git tools are additive, not replacing bash
- Can use both approaches in same session
- Permission rules work consistently across both
- Output format is compatible

### Recommendation:
- Use Git tools for common operations
- Use bash for complex or uncommon operations
- Mix and match based on needs