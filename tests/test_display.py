from pathlib import Path

from click.testing import CliRunner
import click

from gitgym.display import (
    print_success,
    print_error,
    print_info,
    print_exercise_header,
    print_exercise_list,
    print_progress_summary,
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


# --- print_exercise_list ---


def _make_exercise_with_path(name, topic, title, topic_dir, exercise_dir) -> Exercise:
    return Exercise(
        name=name,
        topic=topic,
        title=title,
        description="A description.",
        goal_summary="A goal.",
        hints=[],
        path=Path(f"/tmp/exercises/{topic_dir}/{exercise_dir}"),
    )


def test_print_exercise_list_shows_topic_header():
    ex = _make_exercise_with_path(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke(print_exercise_list, [ex], {"exercises": {}})
    assert "Basics" in result.output


def test_print_exercise_list_shows_exercise_title():
    ex = _make_exercise_with_path(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke(print_exercise_list, [ex], {"exercises": {}})
    assert "Initialize a Repository" in result.output


def test_print_exercise_list_completed_indicator():
    ex = _make_exercise_with_path(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    progress = {"exercises": {"01_basics/01_init": {"status": "completed"}}}
    result = _invoke(print_exercise_list, [ex], progress)
    assert "✓" in result.output


def test_print_exercise_list_in_progress_indicator():
    ex = _make_exercise_with_path(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    progress = {"exercises": {"01_basics/01_init": {"status": "in_progress"}}}
    result = _invoke(print_exercise_list, [ex], progress)
    assert "→" in result.output


def test_print_exercise_list_not_started_indicator():
    ex = _make_exercise_with_path(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke(print_exercise_list, [ex], {"exercises": {}})
    assert "○" in result.output


def test_print_exercise_list_groups_by_topic():
    ex1 = _make_exercise_with_path(
        "init", "Basics", "Initialize", "01_basics", "01_init"
    )
    ex2 = _make_exercise_with_path(
        "staging", "Basics", "Staging Files", "01_basics", "02_staging"
    )
    ex3 = _make_exercise_with_path(
        "amend", "Committing", "Amend Commit", "02_committing", "01_amend"
    )
    result = _invoke(print_exercise_list, [ex1, ex2, ex3], {"exercises": {}})
    # Topic headers appear once each
    assert result.output.count("Basics") == 1
    assert result.output.count("Committing") == 1


def test_print_exercise_list_exit_zero():
    ex = _make_exercise_with_path(
        "init", "Basics", "Initialize a Repository", "01_basics", "01_init"
    )
    result = _invoke(print_exercise_list, [ex], {"exercises": {}})
    assert result.exit_code == 0


# --- print_progress_summary ---


def test_print_progress_summary_shows_totals():
    ex1 = _make_exercise_with_path(
        "init", "Basics", "Initialize", "01_basics", "01_init"
    )
    ex2 = _make_exercise_with_path(
        "staging", "Basics", "Staging", "01_basics", "02_staging"
    )
    progress = {"exercises": {"01_basics/01_init": {"status": "completed"}}}
    result = _invoke(print_progress_summary, [ex1, ex2], progress)
    assert "1/2" in result.output


def test_print_progress_summary_shows_topic_breakdown():
    ex1 = _make_exercise_with_path(
        "init", "Basics", "Initialize", "01_basics", "01_init"
    )
    ex2 = _make_exercise_with_path(
        "amend", "Committing", "Amend", "02_committing", "01_amend"
    )
    progress = {"exercises": {"01_basics/01_init": {"status": "completed"}}}
    result = _invoke(print_progress_summary, [ex1, ex2], progress)
    assert "Basics" in result.output
    assert "Committing" in result.output


def test_print_progress_summary_zero_completed():
    ex = _make_exercise_with_path(
        "init", "Basics", "Initialize", "01_basics", "01_init"
    )
    result = _invoke(print_progress_summary, [ex], {"exercises": {}})
    assert "0/1" in result.output


def test_print_progress_summary_all_completed():
    ex = _make_exercise_with_path(
        "init", "Basics", "Initialize", "01_basics", "01_init"
    )
    progress = {"exercises": {"01_basics/01_init": {"status": "completed"}}}
    result = _invoke(print_progress_summary, [ex], progress)
    assert "1/1" in result.output


def test_print_progress_summary_exit_zero():
    ex = _make_exercise_with_path(
        "init", "Basics", "Initialize", "01_basics", "01_init"
    )
    result = _invoke(print_progress_summary, [ex], {"exercises": {}})
    assert result.exit_code == 0
