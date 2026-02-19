"""Filesystem watcher for gitgym watch mode.

Uses watchdog for efficient event-based watching when available, falling back
to polling the exercise workspace directory every POLL_INTERVAL seconds.
"""

import time
from pathlib import Path

import click

from gitgym.config import EXERCISES_DIR, WORKSPACE_DIR
from gitgym.display import print_error, print_success
from gitgym.exercise import Exercise
from gitgym.runner import run_verify

POLL_INTERVAL = 1  # seconds

try:
    from watchdog.events import FileSystemEventHandler as _BaseEventHandler
    from watchdog.observers import Observer as _Observer

    class _ChangeHandler(_BaseEventHandler):
        """Signal a threading.Event whenever any filesystem event is received."""

        def __init__(self, change_event):
            super().__init__()
            self._change_event = change_event

        def on_any_event(self, event):
            self._change_event.set()

    _HAS_WATCHDOG = True
except ImportError:
    _HAS_WATCHDOG = False


def _workspace_path(exercise: Exercise) -> Path:
    """Return the workspace directory for the given exercise."""
    relative = exercise.path.relative_to(EXERCISES_DIR)
    return WORKSPACE_DIR / relative


def _collect_mtimes(directory: Path) -> dict[Path, float]:
    """Return a mapping of file path -> mtime for all files under directory.

    Returns an empty dict if the directory does not exist.
    """
    mtimes: dict[Path, float] = {}
    if not directory.exists():
        return mtimes
    for path in directory.rglob("*"):
        if path.is_file():
            try:
                mtimes[path] = path.stat().st_mtime
            except OSError:
                pass
    return mtimes


def _has_changed(previous: dict[Path, float], current: dict[Path, float]) -> bool:
    """Return True if any file was added, removed, or modified."""
    return previous != current


def _watch_with_polling(exercise: Exercise, poll_interval: float = POLL_INTERVAL):
    """Generator: yield whenever a file change is detected via mtime polling."""
    workspace = _workspace_path(exercise)
    previous_mtimes = _collect_mtimes(workspace)

    while True:
        time.sleep(poll_interval)
        current_mtimes = _collect_mtimes(workspace)

        if _has_changed(previous_mtimes, current_mtimes):
            previous_mtimes = current_mtimes
            yield  # signal that a change was detected

        else:
            previous_mtimes = current_mtimes


def _watch_with_watchdog(exercise: Exercise):
    """Generator: yield whenever a filesystem event is received via watchdog."""
    import threading

    workspace = _workspace_path(exercise)
    workspace.mkdir(parents=True, exist_ok=True)

    changed = threading.Event()
    handler = _ChangeHandler(changed)
    observer = _Observer()
    observer.schedule(handler, str(workspace), recursive=True)
    observer.start()

    try:
        while True:
            changed.wait()
            changed.clear()
            yield
    finally:
        observer.stop()
        observer.join()


def watch(exercise: Exercise, poll_interval: float = POLL_INTERVAL):
    """Yield whenever a change is detected in the exercise workspace directory.

    Uses watchdog for event-based detection when available; falls back to
    polling file modification times every *poll_interval* seconds.

    Parameters
    ----------
    exercise:
        The exercise whose workspace directory should be watched.
    poll_interval:
        Seconds between each poll (polling fallback only). Defaults to
        POLL_INTERVAL (1 second).
    """
    if _HAS_WATCHDOG:
        yield from _watch_with_watchdog(exercise)
    else:
        yield from _watch_with_polling(exercise, poll_interval)


def watch_and_verify(
    exercise: Exercise,
    poll_interval: float = POLL_INTERVAL,
    *,
    on_completed=None,
) -> None:
    """Watch the exercise workspace and run verify.sh whenever a change is detected.

    Displays the verify output after each change.  Stops (returns) when
    verification succeeds.  Call ``on_completed(exercise_key)`` callback (if
    provided) so the caller can update progress without this module needing to
    import ``progress``.

    Parameters
    ----------
    exercise:
        The exercise to watch and verify.
    poll_interval:
        Seconds between each filesystem poll. Defaults to POLL_INTERVAL.
    on_completed:
        Optional zero-argument callable invoked when the exercise is verified
        successfully (e.g. to mark it completed in progress tracking).
    """
    workspace = _workspace_path(exercise)
    if not workspace.exists():
        click.echo(
            click.style(
                f"Exercise repo not found at {workspace}.\n"
                f"Run 'gitgym reset' to re-create it.",
                fg="red",
            ),
            err=True,
        )
        return

    click.echo(
        click.style(
            f"Watching '{exercise.title}' — press Ctrl+C to stop.",
            fg="cyan",
        )
    )

    try:
        for _ in watch(exercise, poll_interval=poll_interval):
            success, output = run_verify(exercise)

            if output:
                click.echo(output)

            if success:
                print_success("Exercise complete! Great work.")
                if on_completed is not None:
                    on_completed()
                return
            else:
                print_error("Not quite right yet. Keep trying!")
    except KeyboardInterrupt:
        click.echo("\nWatch mode stopped.")
