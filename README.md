# lunvex-code

Terminal AI coding assistant for working inside real projects from your shell.

[![CI](https://img.shields.io/github/actions/workflow/status/artemmelnik/lunvex-code/ci.yml?branch=main&label=ci)](https://github.com/artemmelnik/lunvex-code/actions)
![License](https://img.shields.io/github/license/artemmelnik/lunvex-code)
![Last Commit](https://img.shields.io/github/last-commit/artemmelnik/lunvex-code)
![Repo Size](https://img.shields.io/github/repo-size/artemmelnik/lunvex-code)

## What It Does

`lunvex-code` runs in your terminal and helps with everyday development tasks:

- reads and searches files in the current project
- edits files with confirmation prompts
- runs shell commands when needed
- keeps conversation history between sessions
- uses project context from the current working directory

The app uses the DeepSeek API, but with LunVex-specific naming:

- API key env var: `LUNVEX_API_KEY` (or `DEEPSEEK_API_KEY` for backward compatibility)
- optional project context file: `LUNVEX.md`
- Python package/module name: `lunvex_code`

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/artemmelnik/lunvex-code.git
cd lunvex-code

python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### 2. Set your API key

```bash
export LUNVEX_API_KEY=your_key_here
```

For backward compatibility, you can also use:
```bash
export DEEPSEEK_API_KEY=your_key_here
```

You can put that line in `~/.zshrc` if you want it available in every new shell.

### 3. Start the assistant

```bash
lunvex-code run
```

If `lunvex-code` is not in your `PATH`, run it directly:

```bash
./.venv/bin/lunvex-code run
```

## Use It In Any Project

`lunvex-code` works against the directory you launch it from.

Example:

```bash
cd ~/dev/my-app
lunvex-code run
```

Or run one task directly:

```bash
cd ~/dev/my-app
lunvex-code run "read the project and fix failing tests"
```

If you installed LunVex only inside this repository's virtualenv, you can still use it anywhere:

```bash
cd ~/dev/my-app
/Users/artemmelnik/dev/lunvex-code/.venv/bin/lunvex-code run
```

## Common Commands

### Interactive mode

```bash
lunvex-code run
```

### One-shot task

```bash
lunvex-code run "add type hints to the auth module"
```

### Trust mode

Auto-approves non-blocked operations.

```bash
lunvex-code run --trust "run the tests and fix the failures"
```

### YOLO mode

Skips most permission prompts. Use carefully.

```bash
lunvex-code run --yolo "refactor the module and update tests"
```

### Create a project context file

```bash
lunvex-code init
```

This creates `LUNVEX.md` in the current directory.

### Show saved sessions

```bash
lunvex-code history
```

### Show version

```bash
lunvex-code version
```

## How Project Detection Works

When you launch LunVex in a folder, it tries to find the project root by walking upward until it sees one of these markers:

- `.git`
- `LUNVEX.md`
- `DEEPSEEK.md` (legacy)
- `pyproject.toml`
- `package.json`
- `Cargo.toml`

That detected directory becomes the working project context.

## Permissions Model

The CLI has a simple safety model:

- file reads and search operations are auto-approved
- file writes and edits ask for permission
- shell commands ask for permission by default
- `--trust` auto-approves non-blocked operations
- `--yolo` skips prompts, but still blocks obviously dangerous commands like destructive root deletes

## Project Context With `LUNVEX.md`

If a `LUNVEX.md` file exists in the project root, LunVex loads it and includes it in the system prompt. If only the older `DEEPSEEK.md` exists, LunVex still reads it as a fallback. This is the right place for:

- important project commands
- architecture notes
- coding conventions
- known gotchas

Minimal example:

```md
# LUNVEX.md

## Key Commands
- `make test`
- `make lint`
- `npm run dev`

## Conventions
- Prefer small focused functions
- Add tests for bug fixes

## Known Issues
- Auth tests require local env vars
```

## Shell Tips

If you want `lunvex-code` available from any terminal without activating the virtualenv every time, add this to `~/.zshrc`:

```bash
export PATH="/Users/artemmelnik/dev/lunvex-code/.venv/bin:$PATH"
```

Then reload your shell:

```bash
source ~/.zshrc
```

## Development

Run tests:

```bash
source .venv/bin/activate
pytest
```

Run the CLI module directly:

```bash
source .venv/bin/activate
python -m deepseek_code.cli --help
```

## Repository Layout

```text
.
|-- deepseek_code/       # CLI, agent, context, permissions, tools
|-- tests/               # Test suite
|-- docs/                # Additional documentation
|-- examples/            # Example code and configurations
|-- README.md
|-- pyproject.toml
```

## Documentation

### Getting Started
- [User Guide](docs/USER_GUIDE.md) - Complete guide for users
- [Examples](docs/EXAMPLES.md) - Practical examples and use cases

### For Developers
- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Contributing and extending
- [Permission System](docs/PermissionSystem.md) - Security and permissions
- [Dependency Management](docs/DEPENDENCY_MANAGEMENT.md) - Managing project dependencies

### Project Information
- [Roadmap](docs/ROADMAP.md) - Future plans and milestones
- [Changelog](CHANGELOG.md) - Release history
- [Contributing](CONTRIBUTING.md) - How to contribute
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines

## Troubleshooting

### `API key environment variable not set`

Set the API key first:

```bash
export LUNVEX_API_KEY=your_key_here
```

For backward compatibility, you can also use:
```bash
export DEEPSEEK_API_KEY=your_key_here
```

### `lunvex-code: command not found`

Either activate the virtualenv:

```bash
source .venv/bin/activate
```

or run the binary directly:

```bash
./.venv/bin/lunvex-code run
```

### I started it in the wrong folder

Exit and restart from the correct project directory:

```bash
cd /path/to/project
lunvex-code run
```

## License

This project is released under the MIT License.
