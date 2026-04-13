"""Progress indicators for long-running operations."""

import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Generator, Optional

from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.spinner import Spinner


@dataclass
class ProgressConfig:
    """Configuration for progress indicators."""

    # Display options
    show_progress: bool = True
    show_spinner: bool = True
    show_percentage: bool = True
    show_time: bool = True
    show_count: bool = True

    # Style options
    spinner_style: str = "blue"
    progress_style: str = "green"
    text_style: str = "white"
    error_style: str = "red"
    success_style: str = "green"

    # Behavior options
    auto_close: bool = True  # Close progress when done
    transient: bool = True  # Clear progress when done
    refresh_per_second: float = 10.0  # How often to update

    # Size options
    width: Optional[int] = None
    min_width: int = 40
    max_width: int = 80


class BaseProgressIndicator(ABC):
    """Base class for all progress indicators."""

    def __init__(self, config: Optional[ProgressConfig] = None):
        self.config = config or ProgressConfig()
        self.console = Console()
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None

    @abstractmethod
    def start(self, message: str = "") -> None:
        """Start the progress indicator."""
        pass

    @abstractmethod
    def update(self, progress: float, message: str = "") -> None:
        """Update progress (0.0 to 1.0)."""
        pass

    @abstractmethod
    def increment(self, amount: float = 0.01, message: str = "") -> None:
        """Increment progress by amount."""
        pass

    @abstractmethod
    def stop(self, message: str = "", success: bool = True) -> None:
        """Stop the progress indicator."""
        pass

    @contextmanager
    def track(
        self, message: str = "", total: float = 1.0
    ) -> Generator[Callable[[float, str], None], None, None]:
        """Context manager for tracking progress."""
        self.start(message)
        try:
            yield lambda p, m="": self.update(p, m)
        finally:
            self.stop(success=True)

    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        if self._start_time is None:
            return 0.0
        end = self._end_time or time.time()
        return end - self._start_time


class SpinnerProgress(BaseProgressIndicator):
    """Simple spinner progress indicator."""

    def __init__(self, config: Optional[ProgressConfig] = None):
        super().__init__(config)
        self._live: Optional[Live] = None
        self._current_message: str = ""
        self._current_progress: float = 0.0
        self._spinner = Spinner("dots", style=self.config.spinner_style)

    def _render(self) -> str:
        """Render the current progress state."""
        parts = []

        if self.config.show_spinner:
            parts.append(f"[{self.config.spinner_style}]{self._spinner}[/]")

        if self._current_message:
            parts.append(f"[{self.config.text_style}]{self._current_message}[/]")

        if self.config.show_percentage and self._current_progress > 0:
            percentage = int(self._current_progress * 100)
            parts.append(f"[{self.config.progress_style}]{percentage}%[/]")

        if self.config.show_time and self._start_time:
            elapsed = self.elapsed_time()
            if elapsed > 0:
                parts.append(f"[dim]{elapsed:.1f}s[/]")

        return " ".join(parts)

    def start(self, message: str = "") -> None:
        """Start the spinner."""
        self._start_time = time.time()
        self._current_message = message
        self._current_progress = 0.0

        if self.config.show_progress:
            self._live = Live(
                self._render(),
                console=self.console,
                refresh_per_second=self.config.refresh_per_second,
                transient=self.config.transient,
            )
            self._live.start()

    def update(self, progress: float, message: str = "") -> None:
        """Update progress."""
        self._current_progress = max(0.0, min(1.0, progress))
        if message:
            self._current_message = message

        if self._live:
            self._live.update(self._render())

    def increment(self, amount: float = 0.01, message: str = "") -> None:
        """Increment progress."""
        self.update(self._current_progress + amount, message)

    def stop(self, message: str = "", success: bool = True) -> None:
        """Stop the spinner."""
        self._end_time = time.time()

        if message:
            self._current_message = message

        # Final update
        if self._live:
            if success:
                style = self.config.success_style
                icon = "✓"
            else:
                style = self.config.error_style
                icon = "✗"

            final_message = f"[{style}]{icon}[/] {self._current_message}"
            if self.config.show_time:
                elapsed = self.elapsed_time()
                final_message += f" [{style}]{elapsed:.2f}s[/]"

            self._live.update(final_message)

            if self.config.auto_close:
                self._live.stop()
                self._live = None


class BarProgress(BaseProgressIndicator):
    """Progress bar with rich formatting."""

    def __init__(self, config: Optional[ProgressConfig] = None):
        super().__init__(config)
        self._progress: Optional[Progress] = None
        self._task_id: Optional[int] = None
        self._current_message: str = ""

    def _create_progress(self) -> Progress:
        """Create a rich Progress instance."""
        columns = []

        if self.config.show_spinner:
            columns.append(SpinnerColumn(style=self.config.spinner_style))

        columns.append(TextColumn("[progress.description]{task.description}"))

        if self.config.show_percentage:
            columns.append(TaskProgressColumn())

        columns.append(
            BarColumn(style=self.config.progress_style, complete_style=self.config.progress_style)
        )

        if self.config.show_count:
            columns.append(MofNCompleteColumn())

        if self.config.show_time:
            columns.append(TimeElapsedColumn())
            columns.append(TimeRemainingColumn())

        return Progress(
            *columns,
            console=self.console,
            transient=self.config.transient,
            refresh_per_second=self.config.refresh_per_second,
        )

    def start(self, message: str = "", total: float = 100.0) -> None:
        """Start the progress bar."""
        self._start_time = time.time()
        self._current_message = message

        if self.config.show_progress:
            self._progress = self._create_progress()
            self._progress.start()
            self._task_id = self._progress.add_task(
                description=message or "Working...",
                total=total,
            )

    def update(self, progress: float, message: str = "") -> None:
        """Update progress."""
        if message:
            self._current_message = message

        if self._progress and self._task_id is not None:
            self._progress.update(
                self._task_id,
                completed=progress * 100,
                description=message or self._current_message,
            )

    def increment(self, amount: float = 0.01, message: str = "") -> None:
        """Increment progress."""
        if self._progress and self._task_id is not None:
            current = self._progress.tasks[self._task_id].completed
            self.update((current + amount * 100) / 100, message)

    def stop(self, message: str = "", success: bool = True) -> None:
        """Stop the progress bar."""
        self._end_time = time.time()

        if self._progress and self._task_id is not None:
            # Complete the task
            self._progress.update(self._task_id, completed=100)

            if message:
                self._progress.update(self._task_id, description=message)

            if self.config.auto_close:
                self._progress.stop()
                self._progress = None
                self._task_id = None

            # Show final message
            if message and not self.config.transient:
                style = self.config.success_style if success else self.config.error_style
                icon = "✓" if success else "✗"
                self.console.print(f"[{style}]{icon}[/] {message}")


class MultiProgress(BaseProgressIndicator):
    """Progress indicator for multiple parallel tasks."""

    def __init__(self, config: Optional[ProgressConfig] = None):
        super().__init__(config)
        self._progress: Optional[Progress] = None
        self._tasks: dict[str, int] = {}  # task_name -> task_id
        self._task_messages: dict[str, str] = {}

    def _create_progress(self) -> Progress:
        """Create a rich Progress instance for multiple tasks."""
        columns = [
            SpinnerColumn(style=self.config.spinner_style),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(style=self.config.progress_style, complete_style=self.config.progress_style),
            TaskProgressColumn(),
            TimeElapsedColumn(),
        ]

        return Progress(
            *columns,
            console=self.console,
            transient=self.config.transient,
            refresh_per_second=self.config.refresh_per_second,
        )

    def add_task(self, name: str, message: str = "", total: float = 100.0) -> None:
        """Add a new task to track."""
        if not self._progress:
            self._progress = self._create_progress()
            self._progress.start()
            self._start_time = time.time()

        task_id = self._progress.add_task(
            description=message or name,
            total=total,
        )
        self._tasks[name] = task_id
        self._task_messages[name] = message or name

    def update_task(self, name: str, progress: float, message: str = "") -> None:
        """Update a specific task."""
        if name in self._tasks and self._progress:
            if message:
                self._task_messages[name] = message

            self._progress.update(
                self._tasks[name],
                completed=progress * 100,
                description=self._task_messages[name],
            )

    def increment_task(self, name: str, amount: float = 0.01, message: str = "") -> None:
        """Increment a specific task."""
        if name in self._tasks and self._progress:
            current = self._progress.tasks[self._tasks[name]].completed
            self.update_task(name, (current + amount * 100) / 100, message)

    def complete_task(self, name: str, message: str = "") -> None:
        """Mark a task as complete."""
        self.update_task(name, 1.0, message or f"✓ {name}")

    def start(self, message: str = "") -> None:
        """Start the multi-progress (does nothing for MultiProgress)."""
        pass

    def update(self, progress: float, message: str = "") -> None:
        """Update overall progress (not used for MultiProgress)."""
        pass

    def increment(self, amount: float = 0.01, message: str = "") -> None:
        """Increment overall progress (not used for MultiProgress)."""
        pass

    def stop(self, message: str = "", success: bool = True) -> None:
        """Stop all progress tracking."""
        self._end_time = time.time()

        if self._progress:
            # Complete all tasks
            for name in list(self._tasks.keys()):
                self.complete_task(name)

            if self.config.auto_close:
                self._progress.stop()
                self._progress = None
                self._tasks.clear()
                self._task_messages.clear()

            # Show final message
            if message and not self.config.transient:
                style = self.config.success_style if success else self.config.error_style
                icon = "✓" if success else "✗"
                self.console.print(f"[{style}]{icon}[/] {message}")


# Global progress manager
_progress_manager: Optional["ProgressManager"] = None


class ProgressManager:
    """Manager for progress indicators."""

    def __init__(self):
        self.console = Console()
        self._current_indicator: Optional[BaseProgressIndicator] = None
        self._indicator_stack: list[BaseProgressIndicator] = []

    def create_spinner(self, config: Optional[ProgressConfig] = None) -> SpinnerProgress:
        """Create a spinner progress indicator."""
        return SpinnerProgress(config)

    def create_bar(self, config: Optional[ProgressConfig] = None) -> BarProgress:
        """Create a progress bar indicator."""
        return BarProgress(config)

    def create_multi(self, config: Optional[ProgressConfig] = None) -> MultiProgress:
        """Create a multi-task progress indicator."""
        return MultiProgress(config)

    @contextmanager
    def spinner(
        self, message: str = "", config: Optional[ProgressConfig] = None
    ) -> Generator[SpinnerProgress, None, None]:
        """Context manager for spinner progress."""
        spinner = self.create_spinner(config)
        spinner.start(message)
        self._push_indicator(spinner)
        try:
            yield spinner
        finally:
            spinner.stop()
            self._pop_indicator()

    @contextmanager
    def bar(
        self, message: str = "", total: float = 100.0, config: Optional[ProgressConfig] = None
    ) -> Generator[BarProgress, None, None]:
        """Context manager for progress bar."""
        bar = self.create_bar(config)
        bar.start(message, total)
        self._push_indicator(bar)
        try:
            yield bar
        finally:
            bar.stop()
            self._pop_indicator()

    @contextmanager
    def multi(
        self, config: Optional[ProgressConfig] = None
    ) -> Generator[MultiProgress, None, None]:
        """Context manager for multi-task progress."""
        multi = self.create_multi(config)
        self._push_indicator(multi)
        try:
            yield multi
        finally:
            multi.stop()
            self._pop_indicator()

    def _push_indicator(self, indicator: BaseProgressIndicator) -> None:
        """Push indicator to stack."""
        if self._current_indicator:
            self._indicator_stack.append(self._current_indicator)
        self._current_indicator = indicator

    def _pop_indicator(self) -> Optional[BaseProgressIndicator]:
        """Pop indicator from stack."""
        old = self._current_indicator
        if self._indicator_stack:
            self._current_indicator = self._indicator_stack.pop()
        else:
            self._current_indicator = None
        return old

    def get_current(self) -> Optional[BaseProgressIndicator]:
        """Get current progress indicator."""
        return self._current_indicator

    def update(self, progress: float, message: str = "") -> None:
        """Update current progress indicator."""
        if self._current_indicator:
            self._current_indicator.update(progress, message)

    def increment(self, amount: float = 0.01, message: str = "") -> None:
        """Increment current progress indicator."""
        if self._current_indicator:
            self._current_indicator.increment(amount, message)

    def stop_current(self, message: str = "", success: bool = True) -> None:
        """Stop current progress indicator."""
        if self._current_indicator:
            self._current_indicator.stop(message, success)
            self._pop_indicator()


def get_progress_manager() -> ProgressManager:
    """Get or create the global progress manager."""
    global _progress_manager
    if _progress_manager is None:
        _progress_manager = ProgressManager()
    return _progress_manager


# Convenience functions
@contextmanager
def spinner(
    message: str = "", config: Optional[ProgressConfig] = None
) -> Generator[SpinnerProgress, None, None]:
    """Convenience function for spinner progress."""
    manager = get_progress_manager()
    with manager.spinner(message, config) as spinner:
        yield spinner


@contextmanager
def progress_bar(
    message: str = "", total: float = 100.0, config: Optional[ProgressConfig] = None
) -> Generator[BarProgress, None, None]:
    """Convenience function for progress bar."""
    manager = get_progress_manager()
    with manager.bar(message, total, config) as bar:
        yield bar


@contextmanager
def multi_progress(config: Optional[ProgressConfig] = None) -> Generator[MultiProgress, None, None]:
    """Convenience function for multi-task progress."""
    manager = get_progress_manager()
    with manager.multi(config) as multi:
        yield multi


def track_operation(message: str = "") -> Callable:
    """Decorator for tracking function execution with progress."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            with spinner(message) as progress:
                try:
                    result = func(*args, **kwargs)
                    progress.stop(f"✓ {message}", success=True)
                    return result
                except Exception as e:
                    progress.stop(f"✗ {message}: {str(e)}", success=False)
                    raise

        return wrapper
