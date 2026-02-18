"""Integration tests for the `gitgym hint` command."""

import json
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from gitgym.cli import main
from gitgym.exercise import Exercise


def _make_exercise(hints: list[str], path=None) -> Exercise:
    if path is None:
        path = Path("/tmp/exercises/01_basics/01_init")
    return Exercise(
        name="init",
        topic="Basics",
        title="Initialize a Repository",
        description="A detailed description.",
        goal_summary="The goal summary.",
        hints=hints,
        path=path,
    )


def _invoke_hint(current_key, exercises, progress_file=None):
    runner = CliRunner()
    with ExitStack() as stack:
        stack.enter_context(patch("gitgym.cli._is_git_installed", return_value=True))
        stack.enter_context(
            patch("gitgym.cli.get_current_exercise", return_value=current_key)
        )
        stack.enter_context(
            patch("gitgym.cli.load_all_exercises", return_value=exercises)
        )
        if progress_file is not None:
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            stack.enter_context(
                patch(
                    "gitgym.cli.load_progress",
                    side_effect=lambda: (
                        json.loads(progress_file.read_text())
                        if progress_file.exists()
                        else {"version": 1, "exercises": {}}
                    ),
                )
            )
        return runner.invoke(main, ["hint"])


def _invoke_hint_with_real_progress(current_key, exercises, progress_file):
    runner = CliRunner()
    with ExitStack() as stack:
        stack.enter_context(patch("gitgym.cli._is_git_installed", return_value=True))
        stack.enter_context(
            patch("gitgym.cli.get_current_exercise", return_value=current_key)
        )
        stack.enter_context(
            patch("gitgym.cli.load_all_exercises", return_value=exercises)
        )
        stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
        stack.enter_context(
            patch(
                "gitgym.cli.load_progress",
                side_effect=lambda: (
                    json.loads(progress_file.read_text())
                    if progress_file.exists()
                    else {"version": 1, "exercises": {}}
                ),
            )
        )
        return runner.invoke(main, ["hint"])


# --- Tests for "no exercise in progress" ---


def test_hint_no_exercise_in_progress_exits_nonzero():
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=True):
        with patch("gitgym.cli.get_current_exercise", return_value=None):
            result = runner.invoke(main, ["hint"])
    assert result.exit_code != 0


def test_hint_no_exercise_in_progress_shows_message():
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=True):
        with patch("gitgym.cli.get_current_exercise", return_value=None):
            result = runner.invoke(main, ["hint"])
    assert "No exercise is currently in progress" in result.output


def test_hint_no_exercise_in_progress_suggests_start():
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=True):
        with patch("gitgym.cli.get_current_exercise", return_value=None):
            result = runner.invoke(main, ["hint"])
    assert "gitgym start" in result.output


# --- Tests for exercise key not found in definitions ---


def test_hint_exercise_not_in_definitions_exits_nonzero():
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=True):
        with patch("gitgym.cli.get_current_exercise", return_value="01_basics/01_init"):
            with patch("gitgym.cli.load_all_exercises", return_value=[]):
                result = runner.invoke(main, ["hint"])
    assert result.exit_code != 0


def test_hint_exercise_not_in_definitions_shows_error():
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=True):
        with patch("gitgym.cli.get_current_exercise", return_value="01_basics/01_init"):
            with patch("gitgym.cli.load_all_exercises", return_value=[]):
                result = runner.invoke(main, ["hint"])
    assert "01_basics/01_init" in result.output


# --- Tests for showing hints ---


def test_hint_shows_first_hint():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        progress_file = tmpdir / "progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {
                        "01_basics/01_init": {"status": "in_progress", "hints_used": 0}
                    },
                }
            )
        )

        ex = _make_exercise(hints=["Hint one.", "Hint two.", "Hint three."])

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
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            stack.enter_context(
                patch(
                    "gitgym.cli.load_progress",
                    side_effect=lambda: json.loads(progress_file.read_text()),
                )
            )
            result = CliRunner().invoke(main, ["hint"])

        assert "Hint 1/3: Hint one." in result.output


def test_hint_shows_second_hint_after_one_used():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        progress_file = tmpdir / "progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {
                        "01_basics/01_init": {"status": "in_progress", "hints_used": 1}
                    },
                }
            )
        )

        ex = _make_exercise(hints=["Hint one.", "Hint two.", "Hint three."])

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
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            stack.enter_context(
                patch(
                    "gitgym.cli.load_progress",
                    side_effect=lambda: json.loads(progress_file.read_text()),
                )
            )
            result = CliRunner().invoke(main, ["hint"])

        assert "Hint 2/3: Hint two." in result.output


def test_hint_last_hint_shows_no_more_available():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        progress_file = tmpdir / "progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {
                        "01_basics/01_init": {"status": "in_progress", "hints_used": 2}
                    },
                }
            )
        )

        ex = _make_exercise(hints=["Hint one.", "Hint two.", "Hint three."])

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
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            stack.enter_context(
                patch(
                    "gitgym.cli.load_progress",
                    side_effect=lambda: json.loads(progress_file.read_text()),
                )
            )
            result = CliRunner().invoke(main, ["hint"])

        assert "Hint 3/3: Hint three." in result.output
        assert "No more hints available" in result.output


def test_hint_increments_hints_used():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        progress_file = tmpdir / "progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {
                        "01_basics/01_init": {"status": "in_progress", "hints_used": 0}
                    },
                }
            )
        )

        ex = _make_exercise(hints=["Hint one.", "Hint two."])

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
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            stack.enter_context(
                patch(
                    "gitgym.cli.load_progress",
                    side_effect=lambda: json.loads(progress_file.read_text()),
                )
            )
            CliRunner().invoke(main, ["hint"])

        data = json.loads(progress_file.read_text())
        assert data["exercises"]["01_basics/01_init"]["hints_used"] == 1


def test_hint_all_hints_exhausted_shows_no_more():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        progress_file = tmpdir / "progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {
                        "01_basics/01_init": {"status": "in_progress", "hints_used": 3}
                    },
                }
            )
        )

        ex = _make_exercise(hints=["Hint one.", "Hint two.", "Hint three."])

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
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            stack.enter_context(
                patch(
                    "gitgym.cli.load_progress",
                    side_effect=lambda: json.loads(progress_file.read_text()),
                )
            )
            result = CliRunner().invoke(main, ["hint"])

        assert "No more hints available" in result.output


def test_hint_all_hints_exhausted_exits_zero():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        progress_file = tmpdir / "progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {
                        "01_basics/01_init": {"status": "in_progress", "hints_used": 3}
                    },
                }
            )
        )

        ex = _make_exercise(hints=["Hint one.", "Hint two.", "Hint three."])

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
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            stack.enter_context(
                patch(
                    "gitgym.cli.load_progress",
                    side_effect=lambda: json.loads(progress_file.read_text()),
                )
            )
            result = CliRunner().invoke(main, ["hint"])

        assert result.exit_code == 0


def test_hint_no_hints_used_defaults_to_zero():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        progress_file = tmpdir / "progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        # No hints_used field in progress
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {"01_basics/01_init": {"status": "in_progress"}},
                }
            )
        )

        ex = _make_exercise(hints=["First hint."])

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
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            stack.enter_context(
                patch(
                    "gitgym.cli.load_progress",
                    side_effect=lambda: json.loads(progress_file.read_text()),
                )
            )
            result = CliRunner().invoke(main, ["hint"])

        assert "Hint 1/1: First hint." in result.output
