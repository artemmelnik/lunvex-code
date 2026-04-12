# User Guide

Welcome to LunVex Code! This guide will help you get started with using LunVex Code for your development tasks.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Project Context](#project-context)
5. [Permission System](#permission-system)
6. [Tools Reference](#tools-reference)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Quick Start

### 1. Install LunVex Code
```bash
# Clone and install
git clone https://github.com/artemmelnik/lunvex-code.git
cd lunvex-code
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### 2. Set API Key
```bash
export DEEPSEEK_API_KEY=your_key_here
# Add to ~/.bashrc or ~/.zshrc for persistence
```

### 3. Run Your First Task
```bash
# Interactive mode
lunvex-code run

# One-shot task
lunvex-code run "list all Python files in the project"
```

## Installation

### Method 1: From Source (Recommended for Development)
```bash
git clone https://github.com/artemmelnik/lunvex-code.git
cd lunvex-code
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Method 2: From PyPI (Coming Soon)
```bash
pip install lunvex-code
```

### Method 3: Global Installation
```bash
# Add to PATH
echo 'export PATH="/path/to/lunvex-code/.venv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Verification
```bash
# Check installation
lunvex-code --version

# Test with simple command
lunvex-code run "echo Hello from LunVex"
```

## Basic Usage

### Interactive Mode
Start an interactive session:
```bash
lunvex-code run
```

You'll see a prompt where you can ask LunVex to help with tasks:
```
LunVex Code> Please help me understand this project
```

### One-Shot Tasks
Run a single task without entering interactive mode:
```bash
lunvex-code run "add type hints to the auth module"
```

### Common Commands

#### Get Help
```bash
lunvex-code --help
lunvex-code run --help
```

#### Initialize Project Context
```bash
lunvex-code init
# Creates LUNVEX.md in current directory
```

#### View History
```bash
lunvex-code history
# Shows recent conversations
```

#### Check Version
```bash
lunvex-code version
```

### Modes of Operation

#### Default Mode
Asks for permission before file modifications and shell commands:
```bash
lunvex-code run "refactor the user model"
```

#### Trust Mode
Auto-approves non-blocked operations:
```bash
lunvex-code run --trust "run tests and fix failures"
```

#### YOLO Mode
Skips most permission prompts (use with caution):
```bash
lunvex-code run --yolo "deploy to staging"
```

## Project Context

### What is Project Context?
Project context helps LunVex understand your project better. It includes:
- Project structure and architecture
- Important commands and scripts
- Coding conventions and standards
- Known issues and workarounds

### Creating LUNVEX.md
Run the init command in your project root:
```bash
cd /path/to/your/project
lunvex-code init
```

This creates a `LUNVEX.md` file with a template.

### Example LUNVEX.md
```markdown
# Project: My Awesome App

## Key Commands
- Development: `npm run dev`
- Testing: `npm test`
- Linting: `npm run lint`
- Building: `npm run build`

## Architecture
- Frontend: React + TypeScript
- Backend: Node.js + Express
- Database: PostgreSQL
- Cache: Redis

## Conventions
- Use TypeScript strict mode
- Write tests for new features
- Follow Airbnb style guide
- Document public APIs

## Known Issues
- Auth tests require local env vars
- Database migrations must run in order
- API rate limiting is enabled in production

## Important Files
- `src/index.ts` - Application entry point
- `.env.example` - Environment variables template
- `docker-compose.yml` - Local development setup
```

### How Context is Used
LunVex automatically:
1. Detects your project root (looks for `.git`, `LUNVEX.md`, etc.)
2. Loads `LUNVEX.md` if present
3. Includes context in system prompts
4. Uses project-specific knowledge for better assistance

## Permission System

### Understanding Permission Levels

#### AUTO (Automatic Approval)
Safe operations that don't require confirmation:
- Reading files (`read_file`)
- Searching files (`glob`, `grep`)
- Safe shell commands (`ls`, `git status`, `npm test`)

#### ASK (Requires Confirmation)
Operations that need your approval:
- Writing files (`write_file`, `edit_file`)
- Most shell commands (`python script.py`, `touch file.txt`)
- File modifications

#### DENY (Blocked)
Dangerous operations that are always blocked:
- `rm -rf /` (recursive delete from root)
- `sudo` commands
- Piping to shell (`curl | bash`)
- Fork bombs

### Safe Commands (Auto-Approved)
These commands are automatically approved:
```bash
# File operations
ls, cat, head, tail, find, grep

# Version control
git status, git diff, git log, git pull, git fetch

# Package management
npm test, npm install, npm run dev

# Testing
python -m pytest, make test

# System info
pwd, whoami, date, ps, top
```

### Session Rules
You can temporarily modify permissions during a session:

#### Allowlist
Auto-approve specific patterns:
```bash
# In your LUNVEX.md or during session:
# Auto-approve all npm commands
ALLOW: bash(npm:*)

# Auto-approve writes to test files
ALLOW: write_file(*test.py)
```

#### Denylist
Block specific patterns:
```bash
# Block rm commands
DENY: bash(rm:*)

# Block writes to config files
DENY: write_file(*.env)
```

### Trust and YOLO Modes

#### Trust Mode (`--trust`)
- Auto-approves all non-blocked operations
- Still blocks dangerous commands (DENY level)
- Useful for automated tasks

#### YOLO Mode (`--yolo`)
- Skips almost all permission prompts
- Only blocks extremely dangerous operations
- Use with extreme caution

## Tools Reference

### File Operations

#### Read File
Reads the contents of a file.
```
read_file(path="src/main.py")
```

#### Write File
Writes content to a file (creates or overwrites).
```
write_file(path="test.txt", content="Hello World")
```

#### Edit File
Makes precise edits by replacing text.
```
edit_file(
    path="config.py",
    old_str="DEBUG = False",
    new_str="DEBUG = True"
)
```

### Search Operations

#### Glob
Finds files matching a pattern.
```
glob(pattern="**/*.py")
```

#### Grep
Searches for text patterns in files.
```
grep(pattern="def test_", path="tests/")
```

### Shell Operations

#### Bash
Executes shell commands.
```
bash(command="python -m pytest tests/")
```

### Tool Combinations
LunVex can chain tools together:
```
1. glob(pattern="**/*.py") to find Python files
2. grep(pattern="TODO", path="src/") to find TODOs
3. edit_file(...) to fix issues found
```

## Advanced Features

### Conversation History
LunVex maintains conversation history between sessions:

#### View History
```bash
lunvex-code history
```

#### Sample Output
```
Session 1 (2024-01-15 10:30:00):
- Fixed type hints in auth module
- Added missing imports

Session 2 (2024-01-15 14:45:00):
- Refactored database models
- Updated tests
```

#### History Location
History is stored in `~/.lunvex-code/conversations/`

### Custom Tools (Advanced)
You can extend LunVex with custom tools. See [Developer Guide](DEVELOPER_GUIDE.md) for details.

### Project Detection
LunVex automatically detects project roots by looking for:
1. `.git` directory
2. `LUNVEX.md` file
3. `pyproject.toml` (Python)
4. `package.json` (Node.js)
5. `Cargo.toml` (Rust)

### Environment Variables

#### Required
- `DEEPSEEK_API_KEY`: Your DeepSeek API key

#### Optional
- `LUNVEX_DEBUG`: Enable debug logging
- `LUNVEX_HISTORY_DIR`: Custom history directory
- `LUNVEX_MAX_TOKENS`: Maximum tokens per request

### Configuration Files

#### User Configuration
`~/.lunvex-code/config.yaml` (Future):
```yaml
default_mode: ask
trusted_projects:
  - /path/to/trusted/project
theme: dark
```

#### Project Configuration
`LUNVEX.md` in project root (Current).

## Troubleshooting

### Common Issues

#### "DEEPSEEK_API_KEY environment variable not set"
```bash
# Set the API key
export DEEPSEEK_API_KEY=your_key_here

# Verify it's set
echo $DEEPSEEK_API_KEY
```

#### "lunvex-code: command not found"
```bash
# Activate virtual environment
source /path/to/lunvex-code/.venv/bin/activate

# Or use full path
/path/to/lunvex-code/.venv/bin/lunvex-code run
```

#### Permission Denied Errors
```bash
# Check file permissions
ls -la /path/to/file

# Run with appropriate permissions
# Or fix file permissions
chmod +x /path/to/script
```

#### API Rate Limits
If you hit API rate limits:
- Wait a few minutes
- Check your API plan limits
- Use `--verbose` flag to see API responses

### Debug Mode
Enable verbose output for debugging:
```bash
lunvex-code run --verbose "your task"
```

### Logs
Check logs in:
- Console output (with `--verbose`)
- `~/.lunvex-code/logs/` (Future)

## FAQ

### Q: Is LunVex Code free to use?
A: LunVex Code itself is open source and free. However, you need a DeepSeek API key, which may have usage costs depending on your plan.

### Q: What programming languages does it support?
A: LunVex Code is language-agnostic. It works with any text-based files. It has special awareness for:
- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- Markdown (.md)
- JSON (.json)
- YAML (.yml, .yaml)
- And many others

### Q: How does it compare to GitHub Copilot?
A: LunVex Code is:
- Terminal-based (not IDE-integrated)
- Project-aware (understands your entire codebase)
- Interactive (conversational interface)
- Open source and extensible

### Q: Is my code sent to external servers?
A: Only when interacting with the LLM (DeepSeek API). File operations and tool execution happen locally on your machine.

### Q: Can I use it offline?
A: Partial offline support:
- File operations work offline
- Search and analysis work offline
- LLM interactions require internet connection

### Q: How do I report bugs or request features?
A: Use the GitHub Issues page:
https://github.com/artemmelnik/lunvex-code/issues

### Q: Can I contribute to the project?
A: Yes! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Best Practices

### 1. Start Small
Begin with simple tasks:
```bash
lunvex-code run "explain this project structure"
lunvex-code run "find all TODO comments"
```

### 2. Use Project Context
Create a detailed `LUNVEX.md` for better assistance.

### 3. Review Changes
Always review changes before committing:
```bash
git diff
# Or use your preferred diff tool
```

### 4. Use Trust Mode Wisely
Only use `--trust` for tasks you understand and trust.

### 5. Keep Conversations Focused
Break complex tasks into smaller conversations.

### 6. Learn the Tools
Understand what each tool does to give better instructions.

## Examples

### Example 1: Code Review
```bash
lunvex-code run "review the auth module for security issues"
```

### Example 2: Refactoring
```bash
lunvex-code run "refactor the user model to use dependency injection"
```

### Example 3: Testing
```bash
lunvex-code run "write tests for the new payment processor"
```

### Example 4: Documentation
```bash
lunvex-code run "add docstrings to all public functions"
```

### Example 5: Debugging
```bash
lunvex-code run "help me debug why the login test is failing"
```

## Tips and Tricks

### 1. Be Specific
Instead of:
```
"fix the bug"
```
Try:
```
"The login test is failing with error 'invalid credentials'. 
Please check the auth service and fix the issue."
```

### 2. Use Step-by-Step Instructions
```
1. First, find all files that import the user model
2. Then, check for type errors
3. Finally, fix any issues found
```

### 3. Provide Context
```
"In the file src/auth/service.py, there's a function called 
validate_token that's returning false positives. Please review 
and fix it."
```

### 4. Ask for Explanations
```
"Please explain how this caching system works and suggest improvements."
```

### 5. Combine Tools
```
"Find all Python files with more than 100 lines and suggest 
how to split them into smaller functions."
```

## Support

### Getting Help
- Check this User Guide
- Review [GitHub Issues](https://github.com/artemmelnik/lunvex-code/issues)
- Look for similar problems and solutions

### Community
- GitHub Discussions (Coming Soon)
- Discord/Slack (Coming Soon)

### Updates
- Watch the GitHub repository for updates
- Check `CHANGELOG.md` for release notes
- Run `lunvex-code version` to check your version

## License
LunVex Code is released under the MIT License. See [LICENSE](../LICENSE) for details.

---

Thank you for using LunVex Code! We hope it makes your development workflow more productive and enjoyable.
