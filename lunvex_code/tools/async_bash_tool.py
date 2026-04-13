"""Async bash command execution tool."""

import asyncio
import re
import subprocess

from .async_base import AsyncTool, AsyncToolResult


class AsyncBashTool(AsyncTool):
    """Execute bash commands asynchronously."""

    name = "bash"
    description = (
        "Execute a bash command in the shell. Use for running scripts, "
        "git commands, package managers, build tools, etc."
    )
    permission_level = "ask"  # Most commands need permission

    parameters = {
        "command": {
            "type": "string",
            "description": "The bash command to execute",
            "required": True,
        },
        "timeout": {
            "type": "integer",
            "description": "Timeout in seconds (default: 120)",
            "required": False,
        },
    }

    # Patterns that indicate very dangerous commands
    BLOCKED_PATTERNS = [
        "rm -rf /",
        "rm -rf /*",
        ":(){ :|:& };:",  # Fork bomb
        "> /dev/sda",
        "dd if=/dev/zero of=/dev/",
        "mkfs.",
    ]

    # Patterns that require extra caution
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf?",
        r"sudo\s+",
        r"chmod\s+777",
        r">\s*/dev/",
        r"\|\s*sh",
        r"\|\s*bash",
        r"curl.*\|.*sh",
        r"wget.*\|.*sh",
        r"mv\s+/",
        r"cp\s+.*\s+/",
    ]

    def is_blocked(self, command: str) -> bool:
        """Check if command is completely blocked."""
        cmd_lower = command.lower()
        return any(pattern in cmd_lower for pattern in self.BLOCKED_PATTERNS)

    def is_dangerous(self, command: str) -> bool:
        """Check if command matches dangerous patterns."""
        return any(re.search(pattern, command) for pattern in self.DANGEROUS_PATTERNS)

    async def execute(self, command: str, timeout: int = 120) -> AsyncToolResult:
        # Check for blocked commands
        if self.is_blocked(command):
            return AsyncToolResult(
                success=False,
                output="",
                error="This command is blocked for safety reasons.",
            )

        try:
            # Run the command asynchronously
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=None,  # Use current working directory
                env=None,  # Inherit environment
            )

            try:
                # Wait for process to complete with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                # Kill the process if it times out
                process.kill()
                await process.wait()
                return AsyncToolResult(
                    success=False,
                    output="",
                    error=f"Command timed out after {timeout} seconds",
                )

            # Decode output
            output_parts = []
            if stdout:
                output_parts.append(stdout.decode('utf-8', errors='replace'))
            if stderr:
                output_parts.append(stderr.decode('utf-8', errors='replace'))

            output = "\n".join(output_parts).strip()

            # Truncate very long output
            max_len = 50000
            if len(output) > max_len:
                output = output[:max_len] + f"\n... (output truncated, {len(output)} total chars)"

            if process.returncode == 0:
                return AsyncToolResult(
                    success=True,
                    output=f"$ {command}\n{output}" if output else f"$ {command}\n(no output)",
                )
            else:
                return AsyncToolResult(
                    success=False,
                    output=f"$ {command}\n{output}",
                    error=f"Command exited with code {process.returncode}",
                )

        except Exception as e:
            return AsyncToolResult(success=False, output="", error=str(e))