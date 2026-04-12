# Examples

This document provides practical examples of using LunVex Code for various development tasks.

## Table of Contents
1. [Getting Started Examples](#getting-started-examples)
2. [File Operations](#file-operations)
3. [Code Analysis](#code-analysis)
4. [Refactoring](#refactoring)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Project Management](#project-management)
8. [Real-World Scenarios](#real-world-scenarios)

## Getting Started Examples

### Example 1: First Interaction
```bash
# Start interactive mode
lunvex-code run

# In the interactive session:
LunVex Code> Hello! Can you help me understand this project?
```

### Example 2: Project Exploration
```bash
# One-shot exploration
lunvex-code run "explain the project structure and main components"
```

### Example 3: Quick Help
```bash
# Get help with a specific file
lunvex-code run "what does src/main.py do?"
```

## File Operations

### Example 1: Reading Files
```bash
# Read a specific file
lunvex-code run "read the README.md file"

# Read multiple files
lunvex-code run "read both package.json and pyproject.toml to understand dependencies"
```

### Example 2: Creating Files
```bash
# Create a new Python file
lunvex-code run "create a new file utils/helpers.py with common utility functions"

# Create configuration file
lunvex-code run "create a .env.example file with all required environment variables"
```

### Example 3: Editing Files
```bash
# Fix a typo
lunvex-code run "in config/settings.py, change 'DEBUG = Flase' to 'DEBUG = False'"

# Update version
lunvex-code run "in pyproject.toml, update version from 0.1.0 to 0.1.1"

# Add imports
lunvex-code run "add import statements for missing modules in src/app.py"
```

### Example 4: Batch Operations
```bash
# Update copyright year in all files
lunvex-code run "update copyright year from 2023 to 2024 in all source files"

# Convert tabs to spaces
lunvex-code run "convert all tabs to 4 spaces in Python files"
```

## Code Analysis

### Example 1: Code Review
```bash
# Review specific module
lunvex-code run "review the auth module for security issues and best practices"

# Check for code smells
lunvex-code run "analyze the codebase for common anti-patterns and suggest fixes"
```

### Example 2: Dependency Analysis
```bash
# Find unused imports
lunvex-code run "find and remove unused imports in all Python files"

# Check circular imports
lunvex-code run "check for circular imports in the project and suggest fixes"
```

### Example 3: Complexity Analysis
```bash
# Find complex functions
lunvex-code run "find functions with cyclomatic complexity > 10 and suggest refactoring"

# Analyze class hierarchies
lunvex-code run "analyze the class inheritance hierarchy and suggest improvements"
```

### Example 4: Code Metrics
```bash
# Get code statistics
lunvex-code run "provide statistics: lines of code, number of functions, classes, etc."

# Check test coverage gaps
lunvex-code run "identify code paths not covered by tests"
```

## Refactoring

### Example 1: Function Extraction
```bash
# Extract repeated code
lunvex-code run "extract common validation logic into a separate function"

# Split large function
lunvex-code run "split the process_data function into smaller, focused functions"
```

### Example 2: Renaming
```bash
# Rename variables
lunvex-code run "rename all occurrences of 'temp' to 'temporary' in the utils module"

# Rename functions
lunvex-code run "rename calculate() to calculate_total() for clarity"
```

### Example 3: Code Organization
```bash
# Move functions to appropriate modules
lunvex-code run "move database-related functions from utils.py to database.py"

# Reorganize imports
lunvex-code run "organize imports according to PEP8 guidelines"
```

### Example 4: Design Pattern Implementation
```bash
# Implement singleton
lunvex-code run "refactor the Config class to use singleton pattern"

# Add factory pattern
lunvex-code run "implement factory pattern for creating different types of reports"
```

## Testing

### Example 1: Test Generation
```bash
# Generate unit tests
lunvex-code run "write unit tests for the Calculator class"

# Create integration tests
lunvex-code run "create integration tests for the API endpoints"
```

### Example 2: Test Fixing
```bash
# Fix failing tests
lunvex-code run "the test_user_creation is failing, please fix it"

# Update tests for refactored code
lunvex-code run "update tests to match the refactored auth service"
```

### Example 3: Test Coverage
```bash
# Identify untested code
lunvex-code run "find code that lacks test coverage and suggest test cases"

# Improve test quality
lunvex-code run "review existing tests and suggest improvements for better coverage"
```

### Example 4: Performance Testing
```bash
# Add performance tests
lunvex-code run "add performance tests for the database queries"

# Benchmark critical functions
lunvex-code run "create benchmarks for the image processing functions"
```

## Debugging

### Example 1: Error Analysis
```bash
# Analyze error logs
lunvex-code run "analyze this error log and suggest fixes: [paste error]"

# Debug specific issue
lunvex-code run "users are reporting 500 errors on the login endpoint, help debug"
```

### Example 2: Log Analysis
```bash
# Parse application logs
lunvex-code run "parse the application.log file and identify common errors"

# Find error patterns
lunvex-code run "look for patterns in error messages over the last 24 hours"
```

### Example 3: Performance Debugging
```bash
# Identify performance bottlenecks
lunvex-code run "the application is slow, help identify bottlenecks"

# Memory leak detection
lunvex-code run "check for potential memory leaks in the application"
```

### Example 4: Race Conditions
```bash
# Check for concurrency issues
lunvex-code run "review the code for potential race conditions in multi-threaded sections"
```

## Project Management

### Example 1: Documentation
```bash
# Generate API documentation
lunvex-code run "generate API documentation from docstrings"

# Update README
lunvex-code run "update README.md with latest features and installation instructions"

# Create architecture diagram
lunvex-code run "create an architecture diagram in Mermaid format for the project"
```

### Example 2: Dependency Management
```bash
# Update dependencies
lunvex-code run "update all Python dependencies to latest compatible versions"

# Check for vulnerabilities
lunvex-code run "check dependencies for known security vulnerabilities"

# Clean up requirements
lunvex-code run "remove unused dependencies from requirements.txt"
```

### Example 3: Code Quality
```bash
# Run linters
lunvex-code run "run black, ruff, and mypy on the codebase and fix issues"

# Check style consistency
lunvex-code run "ensure consistent code style across the entire project"
```

### Example 4: Build and Deployment
```bash
# Create Dockerfile
lunvex-code run "create a Dockerfile for the application"

# Set up CI/CD
lunvex-code run "create GitHub Actions workflow for testing and deployment"

# Environment setup
lunvex-code run "create setup scripts for development environment"
```

## Real-World Scenarios

### Scenario 1: New Developer Onboarding
```bash
# Get project overview
lunvex-code run "I'm new to this project. Can you give me an overview and point me to important files?"

# Set up development environment
lunvex-code run "what do I need to set up to start developing on this project?"

# Understand codebase
lunvex-code run "walk me through the main components and how they interact"
```

### Scenario 2: Feature Implementation
```bash
# Plan implementation
lunvex-code run "I need to add user profile pictures. Suggest an implementation approach."

# Review implementation
lunvex-code run "I've implemented profile pictures. Can you review my code?"

# Update documentation
lunvex-code run "update documentation to reflect the new profile picture feature"
```

### Scenario 3: Bug Triage
```bash
# Reproduce bug
lunvex-code run "a user reported bug #123. Help me understand and reproduce it."

# Fix bug
lunvex-code run "here's the stack trace for bug #123. Help me fix it."

# Prevent regression
lunvex-code run "add tests to prevent regression of bug #123"
```

### Scenario 4: Performance Optimization
```bash
# Identify slow queries
lunvex-code run "the database queries are slow. Help me optimize them."

# Cache implementation
lunvex-code run "implement caching for frequently accessed data"

# Load testing
lunvex-code run "help me set up load tests for the API"
```

### Scenario 5: Security Audit
```bash
# Security review
lunvex-code run "perform a security review of the authentication system"

# Vulnerability scanning
lunvex-code run "scan the code for common security vulnerabilities"

# Security headers
lunvex-code run "add security headers to the web application"
```

## Advanced Examples

### Example 1: Multi-Step Refactoring
```bash
# Complex refactoring in steps
lunvex-code run """
I need to refactor the data processing pipeline. Here's the plan:
1. First, analyze the current pipeline structure
2. Identify bottlenecks and tight coupling
3. Suggest a modular design
4. Implement the refactoring in phases
Please help me with step 1.
"""
```

### Example 2: Code Migration
```bash
# Migrate from one library to another
lunvex-code run """
We're migrating from requests to httpx. Please:
1. Find all uses of requests library
2. Suggest equivalent httpx code
3. Help me implement the migration
"""
```

### Example 3: Internationalization
```bash
# Add i18n support
lunvex-code run """
We need to add internationalization support. Please:
1. Identify all user-facing strings
2. Suggest i18n framework (like gettext)
3. Help implement the solution
"""
```

## Interactive Session Examples

### Session 1: Code Review Workflow
```
LunVex Code> I need help reviewing a pull request

User> Can you review the changes in the auth module?

LunVex Code> I've read the auth module changes. I notice:
1. The password validation logic looks good
2. There's a potential SQL injection in line 45
3. Missing error handling for network failures
Would you like me to suggest fixes?

User> Yes, please fix the SQL injection issue

LunVex Code> I've fixed the SQL injection by using parameterized queries.
The changes are in auth/service.py lines 45-50.
Would you like me to add tests for this fix?

User> Yes, add tests too

LunVex Code> Added tests for SQL injection prevention in test_auth.py
```

### Session 2: Learning a Codebase
```
User> I'm new to this codebase. Can you help me understand it?

LunVex Code> Sure! Let me analyze the project structure...
This appears to be a Django web application with:
- Frontend: React in /frontend/
- Backend: Django in /backend/
- Database: PostgreSQL
- Tests: pytest in /tests/

Would you like me to explain any specific part?

User> Tell me about the authentication system

LunVex Code> The authentication system is in /backend/auth/
It uses JWT tokens with:
- Token generation in auth/tokens.py
- Middleware in auth/middleware.py
- Views in auth/views.py
- Models in auth/models.py

Shall I explain any of these files in detail?
```

## Tips for Effective Examples

### 1. Be Specific
**Instead of:**
```bash
lunvex-code run "fix the code"
```

**Try:**
```bash
lunvex-code run "in file src/utils.py, function calculate_total has an off-by-one error on line 23"
```

### 2. Provide Context
```bash
lunvex-code run """
Context: We're building an e-commerce platform.
Task: Add a discount code feature to the shopping cart.
Requirements:
- Discount codes should be stored in the database
- Support percentage and fixed amount discounts
- Validate expiration dates
- Track usage limits
"""
```

### 3. Break Down Complex Tasks
```bash
# Phase 1: Analysis
lunvex-code run "analyze the current user authentication flow"

# Phase 2: Design
lunvex-code run "design an improved authentication flow with 2FA support"

# Phase 3: Implementation
lunvex-code run "implement the 2FA authentication flow"
```

### 4. Use Examples from Your Codebase
```bash
# Reference existing patterns
lunvex-code run "create a new API endpoint similar to /api/users/ but for products"

# Follow existing conventions
lunvex-code run "add error handling following the same pattern used in other services"
```

## Common Patterns

### Pattern 1: "Find and Fix"
```bash
# Find all instances of a pattern and fix them
lunvex-code run "find all print statements and replace with logging"
```

### Pattern 2: "Review and Improve"
```bash
# Review code and suggest improvements
lunvex-code run "review the database models and suggest normalization improvements"
```

### Pattern 3: "Generate and Validate"
```bash
# Generate code and then validate it
lunvex-code run "generate a configuration class and then write tests for it"
```

### Pattern 4: "Migrate and Test"
```bash
# Migrate code and ensure tests pass
lunvex-code run "migrate from Python 3.8 to 3.10 syntax and update tests"
```

## Troubleshooting Examples

### When Things Go Wrong

#### Example 1: Permission Issues
```bash
# If you get permission denied:
lunvex-code run --trust "I need to edit a protected file. Please proceed with caution."
```

#### Example 2: API Limits
```bash
# If hitting API limits:
lunvex-code run "let's work in smaller steps to avoid API limits"
```

#### Example 3: Confusing Results
```bash
# If results aren't what you expected:
lunvex-code run "that's not quite right. Let me clarify: [provide more details]"
```

## Contributing Examples

Have a great example? Contribute it!
1. Fork the repository
2. Add your example to this file
3. Submit a pull request

Please follow these guidelines:
- Examples should be practical and realistic
- Include both the command and expected outcome
- Test your examples before submitting
- Follow the existing formatting style

---

These examples demonstrate the power and flexibility of LunVex Code. The key is to be clear about what you want and provide sufficient context. Happy coding!