import click

from gitgym.exercise import Exercise


def print_success(msg: str) -> None:
    """Print a success message in green."""
    click.echo(click.style(msg, fg="green"))


def print_error(msg: str) -> None:
    """Print an error message in red."""
    click.echo(click.style(msg, fg="red"), err=True)


def print_info(msg: str) -> None:
    """Print an informational message in cyan."""
    click.echo(click.style(msg, fg="cyan"))


def print_exercise_header(exercise: Exercise) -> None:
    """Print a formatted header for an exercise."""
    click.echo(click.style(f"── {exercise.topic} ──", fg="yellow"))
    click.echo(click.style(f"{exercise.title}", fg="bright_white", bold=True))
    click.echo(f"\n{exercise.description.strip()}\n")
    click.echo(click.style(f"Goal: {exercise.goal_summary}", fg="yellow"))
