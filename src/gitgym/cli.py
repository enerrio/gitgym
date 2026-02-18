import shutil
import subprocess

import click

from gitgym.config import WORKSPACE_DIR
from gitgym.display import print_exercise_header, print_exercise_list
from gitgym.exercise import Exercise, load_all_exercises
from gitgym.progress import (
    get_current_exercise,
    load_progress,
    mark_completed,
    mark_in_progress,
)
from gitgym.runner import run_setup, run_verify


class GitGymGroup(click.Group):
    """Custom click.Group that checks for git before invoking any command."""

    def invoke(self, ctx: click.Context) -> object:
        if not _is_git_installed():
            click.echo(
                click.style(
                    "Error: git is not installed or not found in PATH.", fg="red"
                ),
                err=True,
            )
            click.echo(
                "Please install git before using gitgym:\n"
                "  macOS:  brew install git\n"
                "  Ubuntu: sudo apt install git\n"
                "  Windows: https://git-scm.com/download/win",
                err=True,
            )
            ctx.exit(1)
        return super().invoke(ctx)


def _is_git_installed() -> bool:
    """Return True if git is available on PATH and responds to --version."""
    if shutil.which("git") is None:
        return False
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


@click.group(cls=GitGymGroup)
def main():
    """gitgym - Learn git through interactive exercises."""


@main.command("list")
def list_exercises():
    """List all exercises grouped by topic, showing completion status."""
    exercises = load_all_exercises()
    progress = load_progress()
    print_exercise_list(exercises, progress)


def _exercise_key(exercise: Exercise) -> str:
    """Derive the progress key (topic_dir/exercise_dir) from the exercise path."""
    return f"{exercise.path.parent.name}/{exercise.path.name}"


def _find_next_incomplete(exercises: list[Exercise], progress: dict) -> Exercise | None:
    """Return the first exercise that is not completed."""
    ex_progress = progress.get("exercises", {})
    for exercise in exercises:
        key = _exercise_key(exercise)
        status = ex_progress.get(key, {}).get("status", "not_started")
        if status != "completed":
            return exercise
    return None


def _find_by_name(exercises: list[Exercise], name: str) -> Exercise | None:
    """Return the exercise with the given name, or None if not found."""
    for exercise in exercises:
        if exercise.name == name:
            return exercise
    return None


@main.command("start")
@click.argument("exercise", required=False)
def start_exercise(exercise: str | None):
    """Set up an exercise repo. If no name given, starts the next incomplete exercise."""
    exercises = load_all_exercises()
    progress = load_progress()

    if exercise:
        target = _find_by_name(exercises, exercise)
        if target is None:
            click.echo(
                click.style(f"Error: No exercise named '{exercise}' found.", fg="red"),
                err=True,
            )
            click.echo("Run 'gitgym list' to see available exercises.", err=True)
            raise SystemExit(1)
    else:
        target = _find_next_incomplete(exercises, progress)
        if target is None:
            click.echo(
                click.style("All exercises are completed! Great work.", fg="green")
            )
            return

    success = run_setup(target)
    if not success:
        raise SystemExit(1)

    key = _exercise_key(target)
    mark_in_progress(key)

    workspace_path = WORKSPACE_DIR / target.path.parent.name / target.path.name
    click.echo(click.style(f"Exercise directory: {workspace_path}", fg="cyan"))
    click.echo(f"  cd {workspace_path}\n")
    print_exercise_header(target)


@main.command("next")
@click.pass_context
def next_exercise(ctx: click.Context):
    """Alias for 'gitgym start' with no argument (starts the next incomplete exercise)."""
    ctx.invoke(start_exercise)


@main.command("describe")
def describe_exercise():
    """Print the current exercise's description and goal."""
    current_key = get_current_exercise()
    if current_key is None:
        click.echo(
            click.style("No exercise is currently in progress.", fg="yellow"),
            err=True,
        )
        click.echo(
            "Run 'gitgym start' or 'gitgym list' to begin an exercise.", err=True
        )
        raise SystemExit(1)

    exercises = load_all_exercises()
    target = None
    for exercise in exercises:
        if _exercise_key(exercise) == current_key:
            target = exercise
            break

    if target is None:
        click.echo(
            click.style(
                f"Error: Exercise '{current_key}' not found in exercise definitions.",
                fg="red",
            ),
            err=True,
        )
        raise SystemExit(1)

    print_exercise_header(target)


@main.command("verify")
def verify_exercise():
    """Check if the current exercise's goal state is met."""
    current_key = get_current_exercise()
    if current_key is None:
        click.echo(
            click.style("No exercise is currently in progress.", fg="yellow"),
            err=True,
        )
        click.echo(
            "Run 'gitgym start' or 'gitgym list' to begin an exercise.", err=True
        )
        raise SystemExit(1)

    exercises = load_all_exercises()
    target = None
    for exercise in exercises:
        if _exercise_key(exercise) == current_key:
            target = exercise
            break

    if target is None:
        click.echo(
            click.style(
                f"Error: Exercise '{current_key}' not found in exercise definitions.",
                fg="red",
            ),
            err=True,
        )
        raise SystemExit(1)

    success, output = run_verify(target)

    if output:
        click.echo(output)

    if success:
        click.echo(click.style("Exercise complete! Great work.", fg="green"))
        mark_completed(current_key)
    else:
        click.echo(
            click.style("Not quite right yet. Keep trying!", fg="yellow"), err=True
        )
        raise SystemExit(1)
