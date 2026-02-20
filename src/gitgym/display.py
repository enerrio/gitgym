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


def _exercise_key(exercise: Exercise) -> str:
    """Derive the progress key (topic_dir/exercise_dir) from the exercise path."""
    return f"{exercise.path.parent.name}/{exercise.path.name}"


def print_exercise_list(exercises: list[Exercise], progress: dict) -> None:
    """Print all exercises grouped by topic with completion status indicators."""
    ex_progress = progress.get("exercises", {})
    current_topic = None
    for exercise in exercises:
        if exercise.topic != current_topic:
            current_topic = exercise.topic
            click.echo(click.style(f"\n{exercise.topic}", fg="yellow", bold=True))
        key = _exercise_key(exercise)
        status = ex_progress.get(key, {}).get("status", "not_started")
        if status == "completed":
            indicator = click.style("✓", fg="green")
        elif status == "in_progress":
            indicator = click.style("→", fg="cyan")
        else:
            indicator = click.style("○", fg="white")
        click.echo(f"  {indicator} {exercise.name:<20} {exercise.title}")


def print_progress_summary(exercises: list[Exercise], progress: dict) -> None:
    """Print overall progress stats: completed/total and per-topic breakdown."""
    ex_progress = progress.get("exercises", {})

    total = len(exercises)
    completed_total = sum(
        1
        for ex in exercises
        if ex_progress.get(_exercise_key(ex), {}).get("status") == "completed"
    )

    click.echo(
        click.style(
            f"Progress: {completed_total}/{total} exercises completed", bold=True
        )
    )

    # Group by topic
    topics: dict[str, list[Exercise]] = {}
    for ex in exercises:
        topics.setdefault(ex.topic, []).append(ex)

    for topic, topic_exercises in topics.items():
        completed = sum(
            1
            for ex in topic_exercises
            if ex_progress.get(_exercise_key(ex), {}).get("status") == "completed"
        )
        total_in_topic = len(topic_exercises)
        bar_filled = int(completed / total_in_topic * 10) if total_in_topic else 0
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        click.echo(f"  {topic:<20} [{bar}] {completed}/{total_in_topic}")

    if completed_total == total:
        click.echo()
        click.echo(
            click.style(
                "You've completed all exercises! Congratulations!",
                fg="green",
                bold=True,
            )
        )
        click.echo("Run 'gitgym clean' to remove exercise data from your system.")
