"""Progress bar utilities using Rich.

Provides visual feedback during installation and configuration operations.
"""

from typing import Callable, Iterator, TypeVar

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)

console = Console()

T = TypeVar("T")


def create_progress() -> Progress:
    """Create a progress bar with standard OhMyClaude styling.

    Returns:
        Configured Rich Progress instance.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )


def install_progress(
    items: list[T],
    description: str = "Installing",
    callback: Callable[[T], None] | None = None,
) -> list[T]:
    """Show progress while installing a list of items.

    Args:
        items: List of items to process.
        description: Description shown in progress bar.
        callback: Optional callback function for each item.

    Returns:
        The original items list (for chaining).
    """
    with create_progress() as progress:
        task = progress.add_task(description, total=len(items))

        for item in items:
            if callback:
                callback(item)
            progress.advance(task)

    return items


def track_progress(
    items: Iterator[T],
    total: int,
    description: str = "Processing",
) -> Iterator[T]:
    """Wrap an iterator with progress tracking.

    Args:
        items: Iterator to track.
        total: Total number of items.
        description: Description shown in progress bar.

    Yields:
        Items from the original iterator.
    """
    with create_progress() as progress:
        task = progress.add_task(description, total=total)

        for item in items:
            yield item
            progress.advance(task)


class InstallationProgress:
    """Context manager for multi-step installation progress.

    Example:
        with InstallationProgress() as progress:
            progress.add_step("Installing MCP servers", 3)
            progress.add_step("Configuring hooks", 2)

            progress.advance("Installing MCP servers")
            # ... do work ...
            progress.advance("Installing MCP servers")
    """

    def __init__(self) -> None:
        self._progress: Progress | None = None
        self._tasks: dict[str, TaskID] = {}

    def __enter__(self) -> "InstallationProgress":
        self._progress = create_progress()
        self._progress.__enter__()
        return self

    def __exit__(self, *args) -> None:
        if self._progress:
            self._progress.__exit__(*args)

    def add_step(self, description: str, total: int) -> None:
        """Add a new step to track.

        Args:
            description: Step description.
            total: Total sub-steps.
        """
        if self._progress:
            task_id = self._progress.add_task(description, total=total)
            self._tasks[description] = task_id

    def advance(self, description: str, amount: int = 1) -> None:
        """Advance a step's progress.

        Args:
            description: Step description (must match add_step).
            amount: Amount to advance.
        """
        if self._progress and description in self._tasks:
            self._progress.advance(self._tasks[description], amount)

    def complete(self, description: str) -> None:
        """Mark a step as complete.

        Args:
            description: Step description.
        """
        if self._progress and description in self._tasks:
            task_id = self._tasks[description]
            self._progress.update(task_id, completed=self._progress.tasks[task_id].total)


def show_spinner(message: str) -> Progress:
    """Create a simple spinner for indeterminate operations.

    Args:
        message: Message to show next to spinner.

    Returns:
        Progress instance (use as context manager).

    Example:
        with show_spinner("Loading configuration..."):
            load_config()
    """
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]{message}"),
        console=console,
        transient=True,
    )


if __name__ == "__main__":
    # Test progress bars
    import time

    print("Testing progress bar...")

    items = ["MCP 1", "MCP 2", "MCP 3", "Hook 1", "Command 1"]
    install_progress(
        items,
        description="Installing components",
        callback=lambda x: time.sleep(0.5),
    )

    print("\nTesting multi-step progress...")

    with InstallationProgress() as progress:
        progress.add_step("Installing MCP servers", 3)
        progress.add_step("Configuring hooks", 2)

        for i in range(3):
            time.sleep(0.3)
            progress.advance("Installing MCP servers")

        for i in range(2):
            time.sleep(0.3)
            progress.advance("Configuring hooks")

    print("\nDone!")
