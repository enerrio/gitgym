"""Integration tests for the `gitgym list` command."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from gitgym.cli import main
from gitgym.exercise import Exercise


def _make_exercise(name, topic, title, topic_dir, exercise_dir) -> Exercise:
    return Exercise(
        name=name,
        topic=topic,
        title=title,
        description="A description.",
        goal_summary="A goal.",
        hints=[],
        path=Path(f"/tmp/exercises/{topic_dir}/{exercise_dir}"),
    )


def _invoke_list(exercises, progress):
    runner = CliRunner()
    with patch("gitgym.cli.load_all_exercises", return_value=exercises):
        with patch("gitgym.cli.load_progress", return_value=progress):
            with patch("gitgym.cli._is_git_installed", return_value=True):
                return runner.invoke(main, ["list"])


def test_list_exits_zero():
    ex = _make_exercise(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke_list([ex], {"exercises": {}})
    assert result.exit_code == 0


def test_list_shows_topic():
    ex = _make_exercise(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke_list([ex], {"exercises": {}})
    assert "Basics" in result.output


def test_list_shows_exercise_title():
    ex = _make_exercise(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke_list([ex], {"exercises": {}})
    assert "Initialize a Repository" in result.output


def test_list_shows_not_started_indicator():
    ex = _make_exercise(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke_list([ex], {"exercises": {}})
    assert "○" in result.output


def test_list_shows_completed_indicator():
    ex = _make_exercise(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    progress = {"exercises": {"01_basics/01_init": {"status": "completed"}}}
    result = _invoke_list([ex], progress)
    assert "✓" in result.output


def test_list_shows_in_progress_indicator():
    ex = _make_exercise(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    progress = {"exercises": {"01_basics/01_init": {"status": "in_progress"}}}
    result = _invoke_list([ex], progress)
    assert "→" in result.output


def test_list_multiple_topics():
    ex1 = _make_exercise("init", "Basics", "Initialize", "01_basics", "01_init")
    ex2 = _make_exercise(
        "amend", "Committing", "Amend Commit", "02_committing", "01_amend"
    )
    result = _invoke_list([ex1, ex2], {"exercises": {}})
    assert "Basics" in result.output
    assert "Committing" in result.output


def test_list_empty_exercises():
    result = _invoke_list([], {"exercises": {}})
    assert result.exit_code == 0


def test_list_mixed_statuses():
    ex1 = _make_exercise("init", "Basics", "Initialize", "01_basics", "01_init")
    ex2 = _make_exercise(
        "staging", "Basics", "Staging Files", "01_basics", "02_staging"
    )
    progress = {"exercises": {"01_basics/01_init": {"status": "completed"}}}
    result = _invoke_list([ex1, ex2], progress)
    assert "✓" in result.output
    assert "○" in result.output
