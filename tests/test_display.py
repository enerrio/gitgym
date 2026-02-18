from pathlib import Path

from click.testing import CliRunner
import click

from gitgym.display import (
    print_success,
    print_error,
    print_info,
    print_exercise_header,
)
from gitgym.exercise import Exercise


def _invoke(func, *args, **kwargs):
    """Invoke a display function inside a Click CLI context and capture output."""
    runner = CliRunner()

    @click.command()
    def cmd():
        func(*args, **kwargs)

    result = runner.invoke(cmd, catch_exceptions=False)
    return result


def _make_exercise(**overrides) -> Exercise:
    defaults = dict(
        name="init",
        topic="Basics",
        title="Initialize a Repository",
        description="Every git journey starts with `git init`.",
        goal_summary="The directory should be a valid git repository.",
        hints=["Look at `git init`.", "Run `git init` inside the directory."],
        path=Path("/tmp/exercises/01_basics/01_init"),
    )
    defaults.update(overrides)
    return Exercise(**defaults)


# --- print_success ---


def test_print_success_outputs_message():
    result = _invoke(print_success, "All done!")
    assert "All done!" in result.output


def test_print_success_exit_zero():
    result = _invoke(print_success, "Great job!")
    assert result.exit_code == 0


# --- print_error ---


def test_print_error_outputs_message():
    result = _invoke(print_error, "Something went wrong.")
    assert "Something went wrong." in result.output


def test_print_error_exit_zero():
    result = _invoke(print_error, "oops")
    assert result.exit_code == 0


# --- print_info ---


def test_print_info_outputs_message():
    result = _invoke(print_info, "Here is some info.")
    assert "Here is some info." in result.output


def test_print_info_exit_zero():
    result = _invoke(print_info, "info")
    assert result.exit_code == 0


# --- print_exercise_header ---


def test_print_exercise_header_shows_title():
    ex = _make_exercise()
    result = _invoke(print_exercise_header, ex)
    assert "Initialize a Repository" in result.output


def test_print_exercise_header_shows_topic():
    ex = _make_exercise()
    result = _invoke(print_exercise_header, ex)
    assert "Basics" in result.output


def test_print_exercise_header_shows_description():
    ex = _make_exercise()
    result = _invoke(print_exercise_header, ex)
    assert "git init" in result.output


def test_print_exercise_header_shows_goal():
    ex = _make_exercise()
    result = _invoke(print_exercise_header, ex)
    assert "The directory should be a valid git repository." in result.output


def test_print_exercise_header_multiline_description():
    ex = _make_exercise(description="Line one.\nLine two.\n")
    result = _invoke(print_exercise_header, ex)
    assert "Line one." in result.output
    assert "Line two." in result.output


def test_print_exercise_header_exit_zero():
    ex = _make_exercise()
    result = _invoke(print_exercise_header, ex)
    assert result.exit_code == 0
