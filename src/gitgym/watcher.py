"""Filesystem watcher for gitgym watch mode.

Polls the exercise workspace directory every POLL_INTERVAL seconds and checks
for file modification time changes.
"""

import time
from pathlib import Path

import click

from gitgym.config import EXERCISES_DIR, WORKSPACE_DIR
from gitgym.display import print_error, print_success
from gitgym.exercise import Exercise
from gitgym.runner import run_verify

POLL_INTERVAL = 1  # seconds


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


def watch(exercise: Exercise, poll_interval: float = POLL_INTERVAL) -> None:
    """Poll the exercise workspace directory for file changes.

    Checks file modification times every *poll_interval* seconds.  When a
    change is detected the caller-supplied on_change callback is invoked.
    This function runs until it is interrupted (KeyboardInterrupt) or until
    the watcher decides to stop (e.g. when the exercise is completed).

    Parameters
    ----------
    exercise:
        The exercise whose workspace directory should be watched.
    poll_interval:
        Seconds between each poll. Defaults to POLL_INTERVAL (1 second).
    """
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
