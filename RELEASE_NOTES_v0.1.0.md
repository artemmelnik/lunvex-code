# LunVex Code v0.1.0 Release Notes

## 🎉 First Public Release!

LunVex Code is now officially available as an open-source AI coding assistant for your terminal. This initial release provides a comprehensive set of tools for everyday development tasks with safety and usability at its core.

## ✨ Key Features

### 🤖 AI-Powered Coding Assistant
- **DeepSeek API Integration**: Connect to state-of-the-art AI models
- **Project Context Awareness**: Understands your codebase through `LUNVEX.md` files
- **Conversation Memory**: Remains context between sessions

### 🔧 Comprehensive Toolset
- **13 Git Tools**: Complete Git workflow coverage (status, diff, commit, push, pull, merge, etc.)
- **File Operations**: Safe read/write/edit with permission prompts
- **Search & Navigation**: Find files and code quickly
- **Dependency Management**: Python package tools
- **Web Tools**: Fetch and summarize external documentation

### 🛡️ Safety First
- **Permission System**: AUTO/ASK/DENY levels for different operations
- **Trust Modes**: Interactive, trust, and YOLO modes for different workflows
- **Confirmation Prompts**: Always asks before making changes
- **Safety Checks**: Blocks dangerous operations automatically

### 🎨 UX Excellence
- **Color Highlighting**: Beautiful, readable Git output with syntax highlighting
- **Interactive Mode**: Natural conversation with the assistant
- **One-Shot Tasks**: Run specific commands directly
- **Rich Terminal UI**: Professional, polished interface

## 🚀 Quick Start

### Installation
```bash
# Clone and install
git clone https://github.com/artemmelnik/lunvex-code.git
cd lunvex-code
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# Set your API key
export DEEPSEEK_API_KEY=your_key_here
```

### Basic Usage
```bash
# Interactive mode
lunvex-code run

# One-shot task
lunvex-code run "help me understand this project"

# With Git tools
lunvex-code run "show me recent changes and create a commit"
```

## 📊 Technical Highlights

- **212 Passing Tests**: Comprehensive test coverage
- **Modular Architecture**: Easy to extend with new tools
- **Structured Output**: JSON and text formats
- **CI/CD Pipeline**: GitHub Actions for quality assurance
- **Full Documentation**: User guides, API reference, examples

## 🛠️ Git Tools Coverage (~95%)

### Read-Only Operations (AUTO permission)
- `git_status` - Check repository status
- `git_diff` - View changes
- `git_log` - Browse commit history
- `git_show` - Show commit details

### Basic Workflow (ASK permission)
- `git_branch` - List/create/delete branches
- `git_add` - Stage changes
- `git_commit` - Create commits
- `git_push` - Push to remote
- `git_pull` - Pull from remote

### Advanced Operations (ASK permission)
- `git_stash` - Stash changes
- `git_checkout` - Switch branches
- `git_merge` - Merge branches
- `git_fetch` - Fetch from remote

## 🔮 What's Next

This release establishes a solid foundation. Future releases will focus on:

1. **Extended Language Support**: More programming languages and frameworks
2. **Enhanced AI Models**: Support for additional AI providers
3. **Plugin System**: Community-contributed tools
4. **Visualizations**: Code graphs and dependency diagrams
5. **Team Features**: Collaboration and sharing capabilities

## 🙏 Acknowledgments

Thank you to the open-source community for inspiration and to all early testers who provided feedback. Special thanks to the DeepSeek team for their excellent API.

## 📄 License

LunVex Code is released under the MIT License. See the LICENSE file for details.

## 🤝 Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## 🐛 Reporting Issues

Found a bug or have a feature request? Please open an issue on GitHub.

---

**Happy coding with your new AI assistant!** 🚀

*The LunVex Code Team*