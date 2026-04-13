"""Progress decorators for tools."""

from functools import wraps
from typing import Any, Callable, Optional

from ..progress import ProgressConfig, progress_bar, spinner


def with_progress(
    message: Optional[str] = None,
    use_bar: bool = False,
    total: float = 100.0,
    config: Optional[ProgressConfig] = None,
) -> Callable:
    """
    Decorator to add progress tracking to tool execution.

    Args:
        message: Progress message (defaults to tool name)
        use_bar: Use progress bar instead of spinner
        total: Total for progress bar
        config: Progress configuration
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Determine message
            progress_message = (
                message or getattr(self, "name", func.__name__).replace("_", " ").title()
            )

            # Choose progress indicator
            if use_bar:
                with progress_bar(progress_message, total, config) as progress:
                    # Update progress based on execution
                    result = func(self, *args, **kwargs)
                    progress.update(1.0, "Complete")
                    return result
            else:
                with spinner(progress_message, config) as progress:
                    result = func(self, *args, **kwargs)
                    progress.stop(f"✓ {progress_message}", success=True)
                    return result

        return wrapper

    return decorator


def with_file_progress(message: Optional[str] = None) -> Callable:
    """Decorator for file operations with progress."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, path: str, *args, **kwargs) -> Any:
            from pathlib import Path

            progress_message = message or f"Processing {Path(path).name}"

            with spinner(progress_message) as progress:
                try:
                    result = func(self, path, *args, **kwargs)
                    progress.stop(f"✓ {progress_message}", success=True)
                    return result
                except Exception as e:
                    progress.stop(f"✗ {progress_message}: {str(e)}", success=False)
                    raise

        return wrapper

    return decorator


def with_search_progress(message: Optional[str] = None) -> Callable:
    """Decorator for search operations with progress."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            progress_message = message or "Searching..."

            with spinner(progress_message) as progress:
                try:
                    result = func(self, *args, **kwargs)
                    progress.stop(
                        f"✓ Found {len(result.output.splitlines()) if hasattr(result, 'output') else 'results'}",
                        success=True,
                    )
                    return result
                except Exception as e:
                    progress.stop(f"✗ {progress_message}: {str(e)}", success=False)
                    raise

        return wrapper

    return decorator


def with_git_progress(message: Optional[str] = None) -> Callable:
    """Decorator for Git operations with progress."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            from .git_tools import GitResult

            progress_message = (
                message or f"Git {getattr(self, 'name', func.__name__).replace('_', ' ')}"
            )

            with spinner(progress_message) as progress:
                try:
                    result = func(self, *args, **kwargs)

                    if isinstance(result, GitResult):
                        if result.success:
                            progress.stop(f"✓ {progress_message}", success=True)
                        else:
                            progress.stop(f"✗ {progress_message}: {result.error}", success=False)
                    else:
                        progress.stop(f"✓ {progress_message}", success=True)

                    return result
                except Exception as e:
                    progress.stop(f"✗ {progress_message}: {str(e)}", success=False)
                    raise

        return wrapper

    return decorator


def with_batch_progress(
    item_name: str = "items",
    message: Optional[str] = None,
) -> Callable:
    """
    Decorator for batch operations with progress bar.

    Args:
        item_name: Name of items being processed
        message: Progress message
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, items, *args, **kwargs) -> Any:
            progress_message = message or f"Processing {item_name}"

            with progress_bar(progress_message, total=len(items)) as progress:
                results = []
                for i, item in enumerate(items, 1):
                    progress.update(i / len(items), f"Processing {i}/{len(items)}")
                    result = func(self, item, *args, **kwargs)
                    results.append(result)

                progress.stop(f"✓ Processed {len(items)} {item_name}", success=True)
                return results

        return wrapper

    return decorator


# Progress-aware versions of common operations
class ProgressAwareMixin:
    """Mixin class for progress-aware tools."""

    def _update_progress(self, progress: float, message: str = "") -> None:
        """Update progress if a progress indicator is active."""
        from ..progress import get_progress_manager

        manager = get_progress_manager()
        current = manager.get_current()
        if current:
            current.update(progress, message)

    def _increment_progress(self, amount: float = 0.01, message: str = "") -> None:
        """Increment progress if a progress indicator is active."""
        from ..progress import get_progress_manager

        manager = get_progress_manager()
        current = manager.get_current()
        if current:
            current.increment(amount, message)

    def _stop_progress(self, message: str = "", success: bool = True) -> None:
        """Stop progress if a progress indicator is active."""
        from ..progress import get_progress_manager

        manager = get_progress_manager()
        manager.stop_current(message, success)


def with_dependency_progress(message: Optional[str] = None) -> Callable:
    """Decorator for dependency operations with progress."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            progress_message = message or "Analyzing dependencies..."

            with spinner(progress_message) as progress:
                try:
                    result = func(self, *args, **kwargs)

                    # Try to extract meaningful info from result
                    if hasattr(result, "output"):
                        output = result.output
                        if "Total:" in output or "dependencies" in output.lower():
                            # Extract summary from output
                            lines = output.split("\n")
                            summary = next(
                                (
                                    line
                                    for line in lines
                                    if "Total:" in line or "dependencies" in line.lower()
                                ),
                                "",
                            )
                            if summary:
                                progress.stop(f"✓ {summary}", success=True)
                            else:
                                progress.stop(f"✓ {progress_message}", success=True)
                        else:
                            progress.stop(f"✓ {progress_message}", success=True)
                    else:
                        progress.stop(f"✓ {progress_message}", success=True)

                    return result
                except Exception as e:
                    progress.stop(f"✗ {progress_message}: {str(e)}", success=False)
                    raise

        return wrapper

    return decorator
