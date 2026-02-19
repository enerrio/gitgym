"""Integration tests for the `gitgym watch` command."""

import json
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from gitgym.cli import main
from gitgym.exercise import Exercise


def _make_exercise(name, topic, title, topic_dir, exercise_dir, path=None) -> Exercise:
    if path is None:
        path = Path(f"/tmp/exercises/{topic_dir}/{exercise_dir}")
    return Exercise(
        name=name,
        topic=topic,
        title=title,
        description="A detailed description.",
        goal_summary="The goal summary.",
        hints=["Hint one."],
        path=path,
    )


def _invoke_watch(current_key, exercises):
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=True):
        with patch("gitgym.cli.get_current_exercise", return_value=current_key):
            with patch("gitgym.cli.load_all_exercises", return_value=exercises):
                with patch("gitgym.cli.watch_and_verify"):
                    return runner.invoke(main, ["watch"])


# --- Tests for "no exercise in progress" ---


def test_watch_no_exercise_exits_nonzero():
    result = _invoke_watch(None, [])
    assert result.exit_code != 0


def test_watch_no_exercise_shows_message():
    result = _invoke_watch(None, [])
    assert "No exercise is currently in progress" in result.output


def test_watch_no_exercise_suggests_start():
    result = _invoke_watch(None, [])
    assert "gitgym start" in result.output


# --- Tests for exercise key not found in definitions ---


def test_watch_exercise_not_in_definitions_exits_nonzero():
    result = _invoke_watch("01_basics/01_init", [])
    assert result.exit_code != 0


def test_watch_exercise_not_in_definitions_shows_error():
    result = _invoke_watch("01_basics/01_init", [])
    assert "01_basics/01_init" in result.output


# --- Tests for successful watch setup ---


def test_watch_calls_watch_and_verify():
    """watch command delegates to watch_and_verify with the correct exercise."""
    ex = _make_exercise(
        "init",
        "Basics",
        "Initialize a Repository",
        "01_basics",
        "01_init",
        path=Path("/tmp/exercises/01_basics/01_init"),
    )
    runner = CliRunner()
    watch_calls = []

    def fake_watch_and_verify(exercise, **kwargs):
        watch_calls.append(exercise)

    with patch("gitgym.cli._is_git_installed", return_value=True):
        with patch("gitgym.cli.get_current_exercise", return_value="01_basics/01_init"):
            with patch("gitgym.cli.load_all_exercises", return_value=[ex]):
                with patch(
                    "gitgym.cli.watch_and_verify", side_effect=fake_watch_and_verify
                ):
                    result = runner.invoke(main, ["watch"])

    assert result.exit_code == 0
    assert len(watch_calls) == 1
    assert watch_calls[0] is ex


def test_watch_exits_zero_on_normal_completion():
    """watch command exits zero when watch_and_verify returns normally."""
    ex = _make_exercise(
        "init",
        "Basics",
        "Initialize a Repository",
        "01_basics",
        "01_init",
        path=Path("/tmp/exercises/01_basics/01_init"),
    )
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=True):
        with patch("gitgym.cli.get_current_exercise", return_value="01_basics/01_init"):
            with patch("gitgym.cli.load_all_exercises", return_value=[ex]):
                with patch("gitgym.cli.watch_and_verify"):
                    result = runner.invoke(main, ["watch"])

    assert result.exit_code == 0


def test_watch_on_completed_marks_exercise_completed():
    """watch command passes an on_completed callback that marks exercise completed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        progress_file = tmpdir / "progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {"01_basics/01_init": {"status": "in_progress"}},
                }
            )
        )

        ex = _make_exercise(
            "init",
            "Basics",
            "Initialize a Repository",
            "01_basics",
            "01_init",
            path=Path("/tmp/exercises/01_basics/01_init"),
        )

        captured_callback = []

        def fake_watch_and_verify(exercise, on_completed=None, **kwargs):
            # Simulate the watcher calling on_completed when goal is met
            if on_completed is not None:
                captured_callback.append(on_completed)
                on_completed()

        runner = CliRunner()
        with ExitStack() as stack:
            stack.enter_context(
                patch("gitgym.cli._is_git_installed", return_value=True)
            )
            stack.enter_context(
                patch(
                    "gitgym.cli.get_current_exercise", return_value="01_basics/01_init"
                )
            )
            stack.enter_context(
                patch("gitgym.cli.load_all_exercises", return_value=[ex])
            )
            stack.enter_context(
                patch("gitgym.cli.watch_and_verify", side_effect=fake_watch_and_verify)
            )
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            runner.invoke(main, ["watch"])

        data = json.loads(progress_file.read_text())
        assert data["exercises"]["01_basics/01_init"]["status"] == "completed"
        assert len(captured_callback) == 1
