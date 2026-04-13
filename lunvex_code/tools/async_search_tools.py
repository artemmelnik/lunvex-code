"""Async search tools: glob and grep."""

import asyncio
import re
from pathlib import Path

from .async_base import AsyncTool, AsyncToolResult
from .progress_decorators import ProgressAwareMixin


class AsyncGlobTool(AsyncTool, ProgressAwareMixin):
    """Find files matching a pattern asynchronously."""

    name = "glob"
    description = (
        "Find files matching a glob pattern. "
        "Supports ** for recursive matching (e.g., '**/*.py' finds all Python files)."
    )
    permission_level = "auto"  # Safe - read-only operation

    parameters = {
        "pattern": {
            "type": "string",
            "description": "Glob pattern to match (e.g., '**/*.py', 'src/**/*.ts')",
            "required": True,
        },
        "path": {
            "type": "string",
            "description": "Base directory to search in (default: current directory)",
            "required": False,
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of results to return (default: 100)",
            "required": False,
        },
    }

    # Directories to skip
    SKIP_DIRS = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        ".env",
        "dist",
        "build",
        ".next",
        ".cache",
        "target",  # Rust
    }

    async def execute(self, pattern: str, path: str = ".", limit: int = 100) -> AsyncToolResult:
        try:
            base_path = Path(path).expanduser().resolve()

            if not base_path.exists():
                return AsyncToolResult(success=False, output="", error=f"Path not found: {path}")

            matches = []
            total_scanned = 0

            self._update_progress(0.1, "Starting search...")

            # Use pathlib's glob for pattern matching
            # Run glob in thread pool since it's I/O bound
            loop = asyncio.get_event_loop()
            all_matches = await loop.run_in_executor(None, lambda: list(base_path.glob(pattern)))

            for i, match in enumerate(all_matches):
                total_scanned += 1

                # Update progress every 100 files
                if i % 100 == 0:
                    self._update_progress(min(0.9, i / 1000), f"Scanned {i} files...")

                # Skip directories we don't care about
                parts = match.parts
                if any(skip in parts for skip in self.SKIP_DIRS):
                    continue

                # Only include files
                if match.is_file():
                    try:
                        rel_path = match.relative_to(base_path)
                        matches.append(str(rel_path))
                    except ValueError:
                        matches.append(str(match))

                if len(matches) >= limit:
                    break

            self._update_progress(0.9, f"Found {len(matches)} matches, sorting...")

            # Sort by modification time (most recent first)
            def get_mtime(p: str) -> float:
                try:
                    return (base_path / p).stat().st_mtime
                except Exception:
                    return 0

            matches.sort(key=get_mtime, reverse=True)

            if not matches:
                return AsyncToolResult(
                    success=True,
                    output=f"No files found matching '{pattern}' in {path}",
                )

            result = f"Found {len(matches)} file(s) matching '{pattern}' (scanned {total_scanned} items):\n"
            result += "\n".join(f"  {m}" for m in matches)

            if len(matches) >= limit:
                result += f"\n  ... (limited to {limit} results)"

            return AsyncToolResult(success=True, output=result)

        except Exception as e:
            return AsyncToolResult(success=False, output="", error=str(e))


class AsyncGrepTool(AsyncTool, ProgressAwareMixin):
    """Search for patterns in file contents asynchronously."""

    name = "grep"
    description = (
        "Search for a regex pattern in files. "
        "Returns matching lines with file paths and line numbers."
    )
    permission_level = "auto"  # Safe - read-only operation

    parameters = {
        "pattern": {
            "type": "string",
            "description": "Regex pattern to search for",
            "required": True,
        },
        "path": {
            "type": "string",
            "description": "File or directory to search in (default: current directory)",
            "required": False,
        },
        "include": {
            "type": "string",
            "description": "Glob pattern for files to include (e.g., '*.py', default: '*')",
            "required": False,
        },
        "ignore_case": {
            "type": "boolean",
            "description": "Case-insensitive search (default: false)",
            "required": False,
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of matches to return (default: 50)",
            "required": False,
        },
    }

    # Directories to skip
    SKIP_DIRS = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        ".env",
        "dist",
        "build",
        ".next",
        ".cache",
        "target",
    }

    # Binary file extensions to skip
    BINARY_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".webp",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".zip",
        ".tar",
        ".gz",
        ".rar",
        ".7z",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".pyc",
        ".pyo",
        ".class",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".mp3",
        ".mp4",
        ".wav",
        ".avi",
        ".mov",
    }

    async def execute(
        self,
        pattern: str,
        path: str = ".",
        include: str = "*",
        ignore_case: bool = False,
        limit: int = 50,
    ) -> AsyncToolResult:
        try:
            base_path = Path(path).expanduser().resolve()

            if not base_path.exists():
                return AsyncToolResult(success=False, output="", error=f"Path not found: {path}")

            # Compile regex
            flags = re.IGNORECASE if ignore_case else 0
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                return AsyncToolResult(
                    success=False, output="", error=f"Invalid regex pattern: {e}"
                )

            matches = []
            files_searched = 0

            self._update_progress(0.1, "Finding files to search...")

            # Get files to search asynchronously
            loop = asyncio.get_event_loop()
            if base_path.is_file():
                files_to_search = [base_path]
            else:
                # Use glob to find files in thread pool
                files_to_search = await loop.run_in_executor(
                    None, lambda: list(base_path.glob(f"**/{include}"))
                )

            self._update_progress(0.3, f"Found {len(files_to_search)} files to search")

            # Process files in batches for better performance
            batch_size = 10
            for batch_start in range(0, len(files_to_search), batch_size):
                batch = files_to_search[batch_start : batch_start + batch_size]

                # Process batch in parallel
                batch_tasks = []
                for file_path in batch:
                    task = self._search_file(file_path, base_path, regex, limit - len(matches))
                    batch_tasks.append(task)

                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, Exception):
                        continue
                    files_searched += 1
                    matches.extend(result)

                    if len(matches) >= limit:
                        break

                # Update progress
                progress = 0.3 + (batch_start / len(files_to_search)) * 0.6
                self._update_progress(
                    progress,
                    f"Searching {batch_start + len(batch)}/{len(files_to_search)} files...",
                )

                if len(matches) >= limit:
                    break

            if not matches:
                return AsyncToolResult(
                    success=True,
                    output=f"No matches found for '{pattern}' in {path}",
                )

            result = f"Found {len(matches)} match(es) for '{pattern}':\n\n"
            for m in matches:
                result += f"{m['file']}:{m['line']}: {m['content']}\n"

            if len(matches) >= limit:
                result += f"\n... (limited to {limit} results)"

            return AsyncToolResult(success=True, output=result)

        except Exception as e:
            return AsyncToolResult(success=False, output="", error=str(e))

    async def _search_file(
        self, file_path: Path, base_path: Path, regex: re.Pattern, remaining_limit: int
    ) -> list:
        """Search a single file for matches."""
        if not file_path.is_file():
            return []

        # Skip directories we don't care about
        if any(skip in file_path.parts for skip in self.SKIP_DIRS):
            return []

        # Skip binary files
        if file_path.suffix.lower() in self.BINARY_EXTENSIONS:
            return []

        matches = []
        try:
            # Read file asynchronously
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, self._read_file_sync, file_path)

            # Search in content
            lines = content.splitlines()
            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    try:
                        rel_path = file_path.relative_to(base_path)
                    except ValueError:
                        rel_path = file_path

                    matches.append(
                        {
                            "file": str(rel_path),
                            "line": line_num,
                            "content": line.rstrip()[:200],  # Truncate long lines
                        }
                    )

                    if len(matches) >= remaining_limit:
                        break

        except (IOError, UnicodeDecodeError):
            pass

        return matches

    def _read_file_sync(self, file_path: Path) -> str:
        """Synchronous file read for thread pool execution."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
