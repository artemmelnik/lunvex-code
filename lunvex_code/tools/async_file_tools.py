"""Async file operation tools: read, write, edit."""

import asyncio
import os
from pathlib import Path
from typing import Optional

from ..cache import read_file_with_cache
from ..progress import spinner
from .async_base import AsyncTool, AsyncToolResult
from .progress_decorators import with_file_progress, ProgressAwareMixin


class AsyncReadFileTool(AsyncTool, ProgressAwareMixin):
    """Read the contents of a file asynchronously."""

    name = "read_file"
    description = "Read the contents of a file at the specified path."
    permission_level = "auto"  # Safe - read-only operation

    parameters = {
        "path": {
            "type": "string",
            "description": "The path to the file to read",
            "required": True,
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of lines to read (default: all)",
            "required": False,
        },
        "offset": {
            "type": "integer",
            "description": "Line number to start reading from (1-indexed, default: 1)",
            "required": False,
        },
    }

    async def execute(self, path: str, limit: Optional[int] = None, offset: int = 1) -> AsyncToolResult:
        try:
            # Expand user path and resolve
            file_path = Path(path).expanduser().resolve()

            if not file_path.exists():
                return AsyncToolResult(success=False, output="", error=f"File not found: {path}")

            if not file_path.is_file():
                return AsyncToolResult(success=False, output="", error=f"Not a file: {path}")

            # Get file size for progress estimation
            file_size = file_path.stat().st_size

            # Update progress for large files
            if file_size > 1024 * 1024:  # > 1MB
                self._update_progress(0.3, "Reading file...")

            # Read file with caching (run in thread pool for async compatibility)
            loop = asyncio.get_event_loop()
            content, from_cache = await loop.run_in_executor(
                None, read_file_with_cache, file_path, limit, offset
            )

            if file_size > 1024 * 1024:
                self._update_progress(0.7, "Formatting content...")

            # Split into lines for formatting
            lines = content.splitlines(keepends=True)

            # Apply offset (convert to 0-indexed) - already done in cache function
            start_idx = max(0, offset - 1)

            # Format with line numbers
            content_lines = []
            for i, line in enumerate(lines, start=start_idx + 1):
                content_lines.append(f"{i:6d}\t{line.rstrip()}")

            formatted_content = "\n".join(content_lines)

            # Add cache indicator to output
            cache_indicator = " [cached]" if from_cache else ""

            return AsyncToolResult(
                success=True,
                output=f"Contents of {path}{cache_indicator}:\n{formatted_content}" if formatted_content else f"{path} is empty{cache_indicator}",
            )

        except PermissionError:
            return AsyncToolResult(success=False, output="", error=f"Permission denied: {path}")
        except Exception as e:
            return AsyncToolResult(success=False, output="", error=str(e))


class AsyncWriteFileTool(AsyncTool, ProgressAwareMixin):
    """Write content to a file asynchronously (create or overwrite)."""

    name = "write_file"
    description = (
        "Write content to a file. Creates the file if it doesn't exist, overwrites if it does."
    )
    permission_level = "ask"  # Needs permission - modifies filesystem

    parameters = {
        "path": {
            "type": "string",
            "description": "The path to the file to write",
            "required": True,
        },
        "content": {
            "type": "string",
            "description": "The content to write to the file",
            "required": True,
        },
    }

    async def execute(self, path: str, content: str) -> AsyncToolResult:
        try:
            file_path = Path(path).expanduser().resolve()

            # Update progress
            self._update_progress(0.3, "Preparing to write...")

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            self._update_progress(0.6, "Writing content...")

            # Write the file asynchronously
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._write_file_sync, file_path, content
            )

            self._update_progress(0.8, "Updating cache...")

            # Invalidate cache for this file
            from ..cache import get_file_cache
            cache = get_file_cache()
            cache.invalidate(file_path)

            return AsyncToolResult(
                success=True,
                output=f"Successfully wrote {len(content)} characters to {path}",
            )

        except PermissionError:
            return AsyncToolResult(success=False, output="", error=f"Permission denied: {path}")
        except Exception as e:
            return AsyncToolResult(success=False, output="", error=str(e))

    def _write_file_sync(self, file_path: Path, content: str) -> None:
        """Synchronous file write for thread pool execution."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


class AsyncEditFileTool(AsyncTool, ProgressAwareMixin):
    """Make surgical edits to a file using string replacement asynchronously."""

    name = "edit_file"
    description = (
        "Make a precise edit to a file by replacing a unique string with a new string. "
        "The old_str must be unique in the file (appear exactly once)."
    )
    permission_level = "ask"  # Needs permission - modifies filesystem

    parameters = {
        "path": {
            "type": "string",
            "description": "The path to the file to edit",
            "required": True,
        },
        "old_str": {
            "type": "string",
            "description": "The exact string to find and replace (must be unique in the file)",
            "required": True,
        },
        "new_str": {
            "type": "string",
            "description": "The string to replace old_str with",
            "required": True,
        },
    }

    async def execute(self, path: str, old_str: str, new_str: str) -> AsyncToolResult:
        try:
            file_path = Path(path).expanduser().resolve()

            self._update_progress(0.2, "Checking file...")

            if not file_path.exists():
                return AsyncToolResult(success=False, output="", error=f"File not found: {path}")

            if not file_path.is_file():
                return AsyncToolResult(success=False, output="", error=f"Not a file: {path}")

            self._update_progress(0.4, "Reading file...")

            # Read current content asynchronously
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None, self._read_file_sync, file_path
            )

            self._update_progress(0.6, "Finding string...")

            # Check uniqueness
            count = content.count(old_str)
            if count == 0:
                return AsyncToolResult(
                    success=False,
                    output="",
                    error="String not found in file. Make sure old_str exactly matches the file content including whitespace.",
                )
            if count > 1:
                return AsyncToolResult(
                    success=False,
                    output="",
                    error=f"String found {count} times. old_str must be unique. Include more surrounding context to make it unique.",
                )

            self._update_progress(0.8, "Making replacement...")

            # Perform replacement
            new_content = content.replace(old_str, new_str)

            # Write back asynchronously
            await loop.run_in_executor(
                None, self._write_file_sync, file_path, new_content
            )

            self._update_progress(0.9, "Updating cache...")

            # Invalidate cache for this file
            from ..cache import get_file_cache
            cache = get_file_cache()
            cache.invalidate(file_path)

            # Show what changed
            lines_changed = old_str.count("\n") + 1
            return AsyncToolResult(
                success=True,
                output=f"Successfully edited {path} ({lines_changed} line(s) affected)",
            )

        except PermissionError:
            return AsyncToolResult(success=False, output="", error=f"Permission denied: {path}")
        except Exception as e:
            return AsyncToolResult(success=False, output="", error=str(e))

    def _read_file_sync(self, file_path: Path) -> str:
        """Synchronous file read for thread pool execution."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _write_file_sync(self, file_path: Path, content: str) -> None:
        """Synchronous file write for thread pool execution."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)