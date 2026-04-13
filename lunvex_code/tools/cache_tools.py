"""Cache management tools."""

from pathlib import Path

from ..cache import configure_cache, get_file_cache
from .base import Tool, ToolResult


class CacheStatsTool(Tool):
    """Get cache statistics."""

    name = "cache_stats"
    description = "Get statistics about the file cache (hit rate, size, etc.)."
    permission_level = "auto"  # Safe - read-only operation

    parameters = {}

    def execute(self) -> ToolResult:
        try:
            cache = get_file_cache()
            stats = cache.get_stats()

            # Format stats as a readable string
            stats_lines = [
                "File Cache Statistics:",
                f"  Size: {stats['size']}/{stats['max_size']} files",
                f"  Hits: {stats['hits']}",
                f"  Misses: {stats['misses']}",
                f"  Hit Rate: {stats['hit_rate']}",
                f"  TTL: {stats['ttl_seconds']} seconds",
            ]

            return ToolResult(
                success=True,
                output="\n".join(stats_lines),
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class ClearCacheTool(Tool):
    """Clear the file cache."""

    name = "clear_cache"
    description = "Clear all entries from the file cache."
    permission_level = "auto"  # Safe - doesn't affect filesystem

    parameters = {}

    def execute(self) -> ToolResult:
        try:
            cache = get_file_cache()
            cache.clear()

            return ToolResult(
                success=True,
                output="File cache cleared successfully.",
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class ConfigureCacheTool(Tool):
    """Configure cache settings."""

    name = "configure_cache"
    description = "Configure file cache settings (size, TTL)."
    permission_level = "auto"  # Safe - configuration only

    parameters = {
        "max_size": {
            "type": "integer",
            "description": "Maximum number of files to cache (default: 100)",
            "required": False,
        },
        "ttl_seconds": {
            "type": "integer",
            "description": "Time-to-live for cache entries in seconds (default: 300)",
            "required": False,
        },
    }

    def execute(self, max_size: int | None = None, ttl_seconds: int | None = None) -> ToolResult:
        try:
            # Use defaults if not specified
            max_size = max_size if max_size is not None else 100
            ttl_seconds = ttl_seconds if ttl_seconds is not None else 300

            # Validate parameters
            if max_size <= 0:
                return ToolResult(success=False, output="", error="max_size must be positive")
            if ttl_seconds <= 0:
                return ToolResult(success=False, output="", error="ttl_seconds must be positive")

            # Configure cache
            configure_cache(max_size=max_size, ttl_seconds=ttl_seconds)

            return ToolResult(
                success=True,
                output=f"Cache configured: max_size={max_size}, ttl_seconds={ttl_seconds}",
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class InvalidateCacheTool(Tool):
    """Invalidate cache for specific files."""

    name = "invalidate_cache"
    description = "Invalidate cache entries for specific files or directories."
    permission_level = "auto"  # Safe - cache operation only

    parameters = {
        "path": {
            "type": "string",
            "description": "Path to file or directory to invalidate",
            "required": True,
        },
        "recursive": {
            "type": "boolean",
            "description": "Recursively invalidate files in directories (default: false)",
            "required": False,
        },
    }

    def execute(self, path: str, recursive: bool = False) -> ToolResult:
        try:
            file_path = Path(path).expanduser().resolve()
            cache = get_file_cache()

            if not file_path.exists():
                return ToolResult(success=False, output="", error=f"Path not found: {path}")

            if file_path.is_file():
                # Invalidate single file
                cache.invalidate(file_path)
                return ToolResult(
                    success=True,
                    output=f"Cache invalidated for file: {path}",
                )
            elif file_path.is_dir() and recursive:
                # Recursively invalidate all files in directory
                invalidated_count = 0
                for child in file_path.rglob("*"):
                    if child.is_file():
                        cache.invalidate(child)
                        invalidated_count += 1

                return ToolResult(
                    success=True,
                    output=f"Cache invalidated for {invalidated_count} files in directory: {path}",
                )
            elif file_path.is_dir():
                # Invalidate directory itself (if cached as a path)
                cache.invalidate(file_path)
                return ToolResult(
                    success=True,
                    output=f"Cache invalidated for directory: {path}",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Invalid path type: {path}",
                )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
