# Troubleshooting Guide

This guide helps you diagnose and fix common issues with LunVex Code.

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Configuration Problems](#configuration-problems)
3. [Permission Errors](#permission-errors)
4. [API and Network Issues](#api-and-network-issues)
5. [Tool Execution Problems](#tool-execution-problems)
6. [Performance Issues](#performance-issues)
7. [Common Error Messages](#common-error-messages)
8. [Debugging Techniques](#debugging-techniques)
9. [Getting Help](#getting-help)

## Installation Issues

### "Command not found: lunvex-code"
**Problem:** The `lunvex-code` command is not in your PATH.

**Solutions:**
1. **Activate virtual environment:**
   ```bash
   source /path/to/lunvex-code/.venv/bin/activate
   ```

2. **Use full path:**
   ```bash
   /path/to/lunvex-code/.venv/bin/lunvex-code run
   ```

3. **Add to PATH permanently:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   echo 'export PATH="/path/to/lunvex-code/.venv/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

### "Module not found" errors
**Problem:** Python cannot find the LunVex Code modules.

**Solutions:**
1. **Install in development mode:**
   ```bash
   pip install -e .
   ```

2. **Check Python path:**
   ```bash
   python -c "import sys; print(sys.path)"
   ```

3. **Recreate virtual environment:**
   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

### Dependency conflicts
**Problem:** Package version conflicts.

**Solutions:**
1. **Update pip:**
   ```bash
   pip install --upgrade pip
   ```

2. **Clean install:**
   ```bash
   pip uninstall lunvex-code -y
   pip cache purge
   pip install -e .[dev]
   ```

3. **Check compatibility:**
   ```bash
   pip check
   ```

## Configuration Problems

### "DEEPSEEK_API_KEY environment variable not set"
**Problem:** API key is missing.

**Solutions:**
1. **Set environment variable:**
   ```bash
   export DEEPSEEK_API_KEY=your_key_here
   ```

2. **Create .env file:**
   ```bash
   echo "DEEPSEEK_API_KEY=your_key_here" > .env
   ```

3. **Check if set:**
   ```bash
   echo $DEEPSEEK_API_KEY
   ```

### Invalid API key
**Problem:** API key is incorrect or expired.

**Solutions:**
1. **Verify key:**
   - Check DeepSeek platform for valid key
   - Ensure no typos or extra spaces

2. **Test API key:**
   ```bash
   curl -X POST https://api.deepseek.com/v1/chat/completions \
     -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "Hello"}]}'
   ```

### Project context not loading
**Problem:** `LUNVEX.md` not being detected.

**Solutions:**
1. **Check file location:**
   ```bash
   ls -la LUNVEX.md
   ```

2. **Initialize context:**
   ```bash
   lunvex-code init
   ```

3. **Check project detection:**
   ```bash
   # Run from project root
   cd /path/to/project
   lunvex-code run "test"
   ```

## Permission Errors

### "Permission denied" for file operations
**Problem:** Insufficient file permissions.

**Solutions:**
1. **Check file permissions:**
   ```bash
   ls -la /path/to/file
   ```

2. **Fix permissions:**
   ```bash
   chmod +w /path/to/file  # Add write permission
   chown $USER /path/to/file  # Change ownership
   ```

3. **Use trust mode:**
   ```bash
   lunvex-code run --trust "your task"
   ```

### Unexpected permission prompts
**Problem:** Too many permission requests.

**Solutions:**
1. **Use safe commands:** Commands like `ls`, `git status` are auto-approved.

2. **Add to allowlist:**
   ```bash
   # In LUNVEX.md or during session
   ALLOW: bash(git:*)
   ALLOW: write_file(*test.py)
   ```

3. **Review permission rules:** Check `docs/PermissionSystem.md` for rule configuration.

### Dangerous commands blocked
**Problem:** Legitimate commands being blocked.

**Solutions:**
1. **Check command syntax:**
   ```bash
   # Instead of: rm -rf *
   # Use: rm -rf specific_directory
   ```

2. **Temporarily allow:**
   ```bash
   # Use trust mode for specific command
   lunvex-code run --trust "rm -rf build/"
   ```

3. **Review safety rules:** Some patterns are always blocked for safety.

## API and Network Issues

### API rate limits
**Problem:** Too many requests to LunVex API.

**Solutions:**
1. **Wait and retry:**
   ```bash
   # Wait 60 seconds
   sleep 60
   lunvex-code run "continue"
   ```

2. **Reduce request size:**
   ```bash
   # Break large tasks into smaller ones
   lunvex-code run "first part of task"
   lunvex-code run "second part of task"
   ```

3. **Check API plan:** Upgrade if needed.

### Network timeouts
**Problem:** Slow or unstable network connection.

**Solutions:**
1. **Increase timeout:**
   ```bash
   # Not currently configurable via CLI
   # Check network connection first
   ping api.deepseek.com
   ```

2. **Use offline features:**
   - File operations work offline
   - Search and analysis work offline

3. **Retry later:** Network issues are often temporary.

### SSL certificate errors
**Problem:** SSL verification failures.

**Solutions:**
1. **Update certificates:**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install ca-certificates
   
   # macOS
   brew install ca-certificates
   ```

2. **Check system time:**
   ```bash
   date  # Ensure correct date/time
   ```

3. **Temporary workaround (not recommended):**
   ```python
   # Set environment variable (insecure)
   export SSL_CERT_FILE=/path/to/cert.pem
   ```

## Tool Execution Problems

### File not found errors
**Problem:** Tools cannot find specified files.

**Solutions:**
1. **Check file path:**
   ```bash
   pwd  # Current directory
   ls -la path/to/file  # Verify file exists
   ```

2. **Use absolute paths:**
   ```bash
   # Instead of: file.txt
   # Use: /full/path/to/file.txt
   ```

3. **Check working directory:** LunVex works from project root.

### Command execution failures
**Problem:** Shell commands failing.

**Solutions:**
1. **Test command manually:**
   ```bash
   # Run the command yourself
   your-command --options
   ```

2. **Check command syntax:**
   ```bash
   # Ensure proper quoting
   lunvex-code run 'find . -name "*.py" -type f'
   ```

3. **Check dependencies:**
   ```bash
   which command-name  # Ensure command exists
   command-name --version  # Check version
   ```

### Large file handling
**Problem:** Performance issues with large files.

**Solutions:**
1. **Use grep for searching:**
   ```bash
   # Instead of reading entire file
   lunvex-code run "grep pattern large_file.txt"
   ```

2. **Process in chunks:**
   ```bash
   lunvex-code run "analyze first 1000 lines of large_file.txt"
   ```

3. **Exclude large files:**
   ```bash
   # In LUNVEX.md
   EXCLUDE: *.log
   EXCLUDE: node_modules/
   ```

## Performance Issues

### Slow response times
**Problem:** LunVex is responding slowly.

**Solutions:**
1. **Check system resources:**
   ```bash
   top  # CPU and memory usage
   df -h  # Disk space
   ```

2. **Reduce context size:**
   ```bash
   # Simplify LUNVEX.md
   # Remove unnecessary information
   ```

3. **Limit file operations:**
   ```bash
   # Be specific about which files to process
   lunvex-code run "check src/main.py only"
   ```

### High memory usage
**Problem:** LunVex using too much memory.

**Solutions:**
1. **Limit conversation history:**
   ```bash
   # Start new session
   exit
   lunvex-code run
   ```

2. **Clear cache:**
   ```bash
   rm -rf ~/.lunvex-code/cache/
   ```

3. **Process smaller batches:**
   ```bash
   # Instead of: process all files
   # Use: process 10 files at a time
   ```

### Startup delays
**Problem:** Slow startup time.

**Solutions:**
1. **Preload project:**
   ```bash
   # Keep LunVex running in background
   # Use same session for multiple tasks
   ```

2. **Optimize LUNVEX.md:**
   - Keep it concise
   - Remove large code samples
   - Use references instead of full text

3. **Check disk I/O:**
   ```bash
   iostat  # Disk performance
   ```

## Common Error Messages

### "Error: API call failed"
**Possible causes:**
- Invalid API key
- Network issues
- API service down
- Rate limiting

**Debug steps:**
1. Check API key
2. Test network connectivity
3. Check DeepSeek status page
4. Wait and retry

### "Tool execution failed"
**Possible causes:**
- Invalid parameters
- Missing dependencies
- Permission issues
- Tool bugs

**Debug steps:**
1. Check tool parameters
2. Test command manually
3. Check permissions
4. Review tool implementation

### "Permission denied by rule: [reason]"
**Possible causes:**
- Dangerous command pattern
- Session denylist match
- Custom rule blocking

**Debug steps:**
1. Review command safety
2. Check session rules
3. Review custom rules
4. Use trust mode if appropriate

### "File not found: [path]"
**Possible causes:**
- Incorrect path
- File doesn't exist
- Permission issues
- Wrong working directory

**Debug steps:**
1. Verify file exists
2. Check path spelling
3. Check permissions
4. Verify working directory

## Debugging Techniques

### Verbose Mode
Enable detailed logging:
```bash
lunvex-code run --verbose "your task"
```

### Debug Logs
Check log files (if enabled):
```bash
# Default log location
ls -la ~/.lunvex-code/logs/
```

### Manual Testing
Test components individually:
```bash
# Test file reading
python -c "from lunvex_code.tools.file_tools import ReadFileTool; t=ReadFileTool(); print(t.execute(path='README.md'))"

# Test permission system
python -c "from lunvex_code.permissions import PermissionManager; m=PermissionManager(); print(m.check_permission('bash', {'command': 'ls -la'}))"
```

### Environment Inspection
Check your environment:
```bash
# Python version
python --version

# Installed packages
pip list | grep lunvex

# Environment variables
env | grep DEEPSEEK
env | grep LUNVEX
```

### Network Debugging
Test API connectivity:
```bash
# Test curl to API
curl -I https://api.deepseek.com

# Test with API key
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "test"}]}' \
  -w "\nTime: %{time_total}s\n"
```

## Getting Help

### Before Asking for Help
1. **Check documentation:**
   - [User Guide](USER_GUIDE.md)
   - [Examples](EXAMPLES.md)
   - This troubleshooting guide

2. **Search existing issues:**
   ```bash
   # Check GitHub issues
   # Search for similar problems
   ```

3. **Create minimal reproduction:**
   - Smallest example that reproduces issue
   - Exact commands and outputs
   - Environment details

### How to Report Issues
When creating a GitHub issue, include:

1. **Environment:**
   ```bash
   lunvex-code version
   python --version
   uname -a
   ```

2. **Steps to reproduce:**
   ```bash
   # Exact commands
   # Expected vs actual behavior
   ```

3. **Error messages:**
   ```bash
   # Full error output
   # Stack traces if available
   ```

4. **Debug information:**
   ```bash
   # With --verbose flag
   # Log files if available
   ```

### Community Support
- GitHub Discussions (coming soon)
- Discord/Slack (coming soon)
- Stack Overflow (tag: lunvex-code)

### Emergency Workarounds
For critical issues:

1. **Restart fresh:**
   ```bash
   # Clear all state
   rm -rf ~/.lunvex-code/
   # Reinstall
   pip install --force-reinstall -e .
   ```

2. **Use alternative approach:**
   - Manual file editing
   - Direct command execution
   - Other tools temporarily

3. **Downgrade version:**
   ```bash
   git checkout previous-version-tag
   pip install -e .
   ```

## Prevention Tips

### Regular Maintenance
1. **Keep updated:**
   ```bash
   git pull
   pip install --upgrade -e .
   ```

2. **Clean cache:**
   ```bash
   rm -rf ~/.lunvex-code/cache/
   ```

3. **Review logs:**
   ```bash
   tail -f ~/.lunvex-code/logs/app.log
   ```

### Best Practices
1. **Backup before major changes:**
   ```bash
   git commit -a -m "backup before lunvex changes"
   ```

2. **Test in safe environment:**
   ```bash
   # Use test directory
   mkdir test_project && cd test_project
   lunvex-code run "test task"
   ```

3. **Monitor resource usage:**
   ```bash
   # Keep eye on system resources
   htop
   ```

### Configuration Management
1. **Version control LUNVEX.md:**
   ```bash
   git add LUNVEX.md
   git commit -m "update project context"
   ```

2. **Backup configuration:**
   ```bash
   cp ~/.lunvex-code/config.yaml ~/.lunvex-code/config.yaml.backup
   ```

3. **Document custom rules:**
   ```bash
   # Keep record of permission rules
   # Document in project README
   ```

---

Remember: When in doubt, start simple and build up complexity. LunVex Code is designed to help you, not hinder you. If something isn't working, there's usually a straightforward solution.