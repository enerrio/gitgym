import shutil
import subprocess

import click

from gitgym.display import print_exercise_list
from gitgym.exercise import load_all_exercises
from gitgym.progress import load_progress


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
