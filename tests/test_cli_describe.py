"""Integration tests for the `gitgym describe` command."""

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
        description="A detailed description.",
        goal_summary="The goal summary.",
        hints=["Hint one."],
        path=Path(f"/tmp/exercises/{topic_dir}/{exercise_dir}"),
    )


def _invoke_describe(current_key, exercises):
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=True):
        with patch("gitgym.cli.get_current_exercise", return_value=current_key):
            with patch("gitgym.cli.load_all_exercises", return_value=exercises):
                return runner.invoke(main, ["describe"])


def test_describe_prints_title():
    ex = _make_exercise(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke_describe("01_basics/01_init", [ex])
    assert result.exit_code == 0, result.output
    assert "Initialize a Repository" in result.output


def test_describe_prints_description():
    ex = _make_exercise(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke_describe("01_basics/01_init", [ex])
    assert "A detailed description." in result.output


def test_describe_prints_goal():
    ex = _make_exercise(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke_describe("01_basics/01_init", [ex])
    assert "The goal summary." in result.output


def test_describe_prints_topic():
    ex = _make_exercise(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke_describe("01_basics/01_init", [ex])
    assert "Basics" in result.output


def test_describe_no_exercise_in_progress_exits_nonzero():
    result = _invoke_describe(None, [])
    assert result.exit_code != 0


def test_describe_no_exercise_in_progress_shows_message():
    result = _invoke_describe(None, [])
    assert "No exercise is currently in progress" in result.output


def test_describe_no_exercise_suggests_start():
    result = _invoke_describe(None, [])
    assert "gitgym start" in result.output


def test_describe_exercise_not_in_definitions_exits_nonzero():
    # current key in progress but no matching exercise in definitions
    result = _invoke_describe("01_basics/01_init", [])
    assert result.exit_code != 0


def test_describe_exercise_not_in_definitions_shows_error():
    result = _invoke_describe("01_basics/01_init", [])
    assert "01_basics/01_init" in result.output
