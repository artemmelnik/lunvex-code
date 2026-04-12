# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-12

### Added
- Initial release of LunVex Code - terminal AI coding assistant
- Core AI assistant functionality with DeepSeek API integration
- Comprehensive Git tools integration (13 specialized tools)
- Permission system with AUTO/ASK/DENY levels and safety controls
- Project context support via LUNVEX.md files
- File operations: read, write, edit with confirmation prompts
- Search tools: grep and glob for file navigation
- Dependency management tools for Python projects
- Web tools: fetch_url for external content access
- Color highlighting for Git command outputs (Phase 4 UX improvements)
- Interactive mode and one-shot task execution
- Trust and YOLO modes for different permission levels
- Conversation history between sessions
- Comprehensive documentation with user guides and API reference
- 212 passing tests with ~95% coverage of common operations
- GitHub Actions CI/CD pipeline with linting, testing, and security checks
- Examples and demo scripts for different workflows
- Support for Python 3.10+

### Technical
- Modular architecture with tool registry system
- Structured JSON and text output formats
- Error handling and parameter validation
- Timeout protection for long-running operations
- ANSI color support with fallback to plain text
- Project root detection for Git and other operations
- Environment variable configuration (DEEPSEEK_API_KEY)
- Package management via pyproject.toml and hatchling
