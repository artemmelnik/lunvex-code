# LunVex Code Documentation

Welcome to the LunVex Code documentation! This directory contains comprehensive guides, references, and examples for using and extending LunVex Code.

## Documentation Index

### Getting Started
- **[User Guide](USER_GUIDE.md)** - Complete guide for end users
- **[Examples](EXAMPLES.md)** - Practical examples and use cases
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

### For Developers
- **[Architecture](ARCHITECTURE.md)** - System design and components
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Contributing and extending
- **[API Reference](API.md)** - Public API documentation
- **[Permission System](PermissionSystem.md)** - Security and permissions

### Project Information
- **[Roadmap](ROADMAP.md)** - Future plans and milestones
- **[Changelog](../CHANGELOG.md)** - Release history
- **[Contributing](../CONTRIBUTING.md)** - How to contribute
- **[Code of Conduct](../CODE_OF_CONDUCT.md)** - Community guidelines

## Quick Links

### Installation
```bash
# Clone and install
git clone https://github.com/artemmelnik/lunvex-code.git
cd lunvex-code
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# Set API key
export DEEPSEEK_API_KEY=your_key_here
```

### Basic Usage
```bash
# Interactive mode
lunvex-code run

# One-shot task
lunvex-code run "help me understand this project"

# With trust mode
lunvex-code run --trust "fix all linting errors"
```

## Documentation Philosophy

### For Users
Our user documentation focuses on:
- **Practical examples** - Real-world use cases
- **Step-by-step guides** - Clear instructions
- **Troubleshooting** - Common problems and solutions
- **Best practices** - Recommended workflows

### For Developers
Our developer documentation emphasizes:
- **Architecture** - Understanding the system
- **Extensibility** - Adding custom features
- **API reference** - Detailed interface documentation
- **Contribution guidelines** - How to help improve LunVex

## Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| User Guide | ✅ Complete | 2024-01-15 |
| Examples | ✅ Complete | 2024-01-15 |
| Troubleshooting | ✅ Complete | 2024-01-15 |
| Architecture | ✅ Complete | 2024-01-15 |
| Developer Guide | ✅ Complete | 2024-01-15 |
| API Reference | ⚠️ Partial | 2024-01-15 |
| Permission System | ✅ Complete | 2024-01-15 |
| Roadmap | ✅ Complete | 2024-01-15 |

## Contributing to Documentation

We welcome contributions to improve our documentation! Here's how:

### Reporting Issues
Found an error or missing information?
1. Check if issue already exists
2. Create new issue with:
   - Document name and section
   - Description of problem
   - Suggested fix (if known)

### Suggesting Improvements
Have ideas for better documentation?
1. Open discussion issue
2. Describe what could be improved
3. Provide examples if possible

### Submitting Changes
Want to fix documentation directly?
1. Fork the repository
2. Make your changes
3. Submit pull request with:
   - Description of changes
   - Reference to related issue
   - Before/after examples if applicable

### Documentation Standards
When contributing:
- Use clear, concise language
- Include practical examples
- Follow existing formatting
- Test all code examples
- Update related documents if needed

## Documentation Structure

### File Organization
```
docs/
├── README.md              # This file
├── USER_GUIDE.md          # End user documentation
├── EXAMPLES.md            # Usage examples
├── TROUBLESHOOTING.md     # Problem solving
├── ARCHITECTURE.md        # System design
├── DEVELOPER_GUIDE.md     # Development guide
├── API.md                 # API reference
├── PermissionSystem.md    # Permission system
└── ROADMAP.md            # Project roadmap
```

### Writing Style
- **Clarity over cleverness** - Be clear, not clever
- **Examples first** - Show, then tell
- **Progressive disclosure** - Start simple, add complexity
- **Consistent terminology** - Use same terms throughout

### Formatting Guidelines
- Use Markdown with GitHub Flavored Markdown extensions
- Code blocks with language specification
- Tables for comparisons
- Lists for step-by-step instructions
- Bold for important concepts
- Italics for emphasis

## Building Documentation (Future)

We plan to add:
- Automated documentation generation from docstrings
- Searchable documentation website
- Versioned documentation
- Multi-language support

## Getting Help

### Documentation Issues
For problems with documentation:
1. Check if issue is already documented
2. Search existing issues
3. Ask in community channels

### Using LunVex
For help using LunVex Code:
1. Read the User Guide
2. Check Examples
3. Review Troubleshooting
4. Ask in community channels

### Development Questions
For development questions:
1. Read Developer Guide
2. Check API Reference
3. Review source code
4. Ask in community channels

## Community Resources

### Official Channels
- **GitHub Repository**: https://github.com/artemmelnik/lunvex-code
- **Issue Tracker**: https://github.com/artemmelnik/lunvex-code/issues
- **Discussions** (coming soon)
- **Discord/Slack** (coming soon)

### External Resources
- **Stack Overflow**: Use tag `lunvex-code`
- **Python Package Index**: (coming soon)
- **Blog Posts**: (coming soon)

## License

Documentation is licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

Code examples are licensed under the same [MIT License](../LICENSE) as the LunVex Code project.

## Acknowledgments

Thanks to all contributors who have helped improve LunVex Code documentation. Your efforts make the project more accessible to everyone.

---

*Last updated: 2024-01-15*  
*Documentation version: 1.0*