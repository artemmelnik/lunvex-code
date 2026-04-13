"""Tools for managing LLM response cache."""

import time

from ..llm_cache import get_llm_cache, save_llm_cache
from ..tools.base import Tool, ToolResult


class LLMCacheStatsTool(Tool):
    """Get statistics about the LLM response cache."""

    name = "llm_cache_stats"
    description = "Get statistics about the LLM response cache (hit rate, tokens saved, etc.)"
    parameters = {}
    permission_level = "auto"

    def execute(self, **kwargs) -> ToolResult:
        """Execute the cache stats tool."""
        try:
            cache = get_llm_cache()
            stats = cache.get_stats()

            # Format statistics nicely
            output_lines = [
                "📊 LLM Cache Statistics",
                "=" * 40,
                f"Cache hits: {stats['hits']}",
                f"Cache misses: {stats['misses']}",
                f"Total requests: {stats['total_requests']}",
                f"Hit rate: {stats['hit_rate']:.1%}",
                f"Tokens saved: {stats['tokens_saved']:,}",
                f"Current size: {stats['current_size']}/{stats['max_size']}",
                f"TTL: {stats['ttl_seconds']} seconds ({stats['ttl_seconds'] / 3600:.1f} hours)",
            ]

            if stats["current_size"] > 0:
                oldest_age = int(time.time() - stats["oldest_entry"])
                output_lines.extend(
                    [
                        f"Oldest entry: {oldest_age} seconds ago",
                        f"Most accessed entry: {stats['most_accessed']} hits",
                    ]
                )

            output_lines.append("=" * 40)

            return ToolResult(success=True, output="\n".join(output_lines))
        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to get cache stats: {str(e)}"
            )


class ClearLLMCacheTool(Tool):
    """Clear all entries from the LLM response cache."""

    name = "clear_llm_cache"
    description = "Clear all entries from the LLM response cache"
    parameters = {}
    permission_level = "ask"

    def execute(self, **kwargs) -> ToolResult:
        """Execute the clear cache tool."""
        try:
            cache = get_llm_cache()
            cache.clear()

            return ToolResult(success=True, output="✅ LLM cache cleared successfully")
        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to clear LLM cache: {str(e)}"
            )


class ConfigureLLMCacheTool(Tool):
    """Configure LLM cache settings."""

    name = "configure_llm_cache"
    description = "Configure LLM cache settings (max size, TTL)"
    parameters = {
        "max_size": {
            "type": "integer",
            "description": "Maximum number of responses to cache",
            "required": False,
        },
        "ttl_seconds": {
            "type": "integer",
            "description": "Time-to-live for cache entries in seconds",
            "required": False,
        },
    }
    permission_level = "ask"

    def execute(self, **kwargs) -> ToolResult:
        """Execute the configure cache tool."""
        try:
            max_size = kwargs.get("max_size")
            ttl_seconds = kwargs.get("ttl_seconds")

            if max_size is None and ttl_seconds is None:
                return ToolResult(
                    success=False,
                    output="",
                    error="At least one parameter (max_size or ttl_seconds) must be provided",
                )

            # Get current cache to preserve stats
            cache = get_llm_cache()
            current_max_size = cache.max_size
            current_ttl = cache.ttl_seconds

            # Update configuration
            if max_size is not None:
                cache.max_size = max_size
            if ttl_seconds is not None:
                cache.ttl_seconds = ttl_seconds

            # Save to persistent storage
            save_llm_cache()

            output_lines = [
                "⚙️ LLM Cache Configuration Updated",
                "=" * 40,
            ]

            if max_size is not None:
                output_lines.append(f"Max size: {current_max_size} → {max_size}")

            if ttl_seconds is not None:
                output_lines.append(
                    f"TTL: {current_ttl}s → {ttl_seconds}s ({ttl_seconds / 3600:.1f} hours)"
                )

            output_lines.append("=" * 40)
            output_lines.append("✅ Configuration saved to persistent storage")

            return ToolResult(success=True, output="\n".join(output_lines))
        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to configure LLM cache: {str(e)}"
            )


class InvalidateLLMCacheTool(Tool):
    """Invalidate specific entries in the LLM cache."""

    name = "invalidate_llm_cache"
    description = "Invalidate specific entries in the LLM cache by pattern"
    parameters = {
        "pattern": {
            "type": "string",
            "description": "Pattern to match against cache keys (optional, invalidates all if not provided)",
            "required": False,
        },
    }
    permission_level = "ask"

    def execute(self, **kwargs) -> ToolResult:
        """Execute the invalidate cache tool."""
        try:
            pattern = kwargs.get("pattern")
            cache = get_llm_cache()

            count = cache.invalidate(pattern)

            if pattern:
                message = f"Invalidated {count} cache entries matching pattern: {pattern}"
            else:
                message = f"Invalidated all {count} cache entries"

            return ToolResult(success=True, output=f"✅ {message}")
        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Failed to invalidate LLM cache: {str(e)}"
            )
