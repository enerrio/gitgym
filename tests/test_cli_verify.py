"""Integration tests for the `gitgym verify` command."""

import json
import stat
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


def _make_real_exercise(
    exercises_dir: Path, verify_exits_zero: bool = True
) -> Exercise:
    """Create a real exercise on disk with a verify.sh script."""
    exercise_dir = exercises_dir / "01_basics" / "01_init"
    exercise_dir.mkdir(parents=True)

    if verify_exits_zero:
        verify_content = (
            '#!/usr/bin/env bash\nset -euo pipefail\necho "Goal met!"\nexit 0\n'
        )
    else:
        verify_content = (
            '#!/usr/bin/env bash\nset -euo pipefail\necho "Not done yet."\nexit 1\n'
        )

    verify_script = exercise_dir / "verify.sh"
    verify_script.write_text(verify_content)
    verify_script.chmod(verify_script.stat().st_mode | stat.S_IEXEC)

    return Exercise(
        name="init",
        topic="Basics",
        title="Initialize a Repository",
        description="Initialize a git repo.",
        goal_summary="Repo initialized.",
        hints=["Run git init"],
        path=exercise_dir,
    )


def _invoke_verify(current_key, exercises):
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=True):
        with patch("gitgym.cli.get_current_exercise", return_value=current_key):
            with patch("gitgym.cli.load_all_exercises", return_value=exercises):
                return runner.invoke(main, ["verify"])


def _invoke_verify_with_real_runner(
    current_key, exercises, workspace_dir, progress_file, exercises_dir
):
    # Ensure the workspace exercise directory exists so run_verify doesn't
    # fail with a "repo not found" error before reaching the script check.
    (workspace_dir / current_key).mkdir(parents=True, exist_ok=True)
    runner = CliRunner()
    with ExitStack() as stack:
        stack.enter_context(patch("gitgym.cli._is_git_installed", return_value=True))
        stack.enter_context(
            patch("gitgym.cli.get_current_exercise", return_value=current_key)
        )
        stack.enter_context(
            patch("gitgym.cli.load_all_exercises", return_value=exercises)
        )
        stack.enter_context(patch("gitgym.runner.WORKSPACE_DIR", workspace_dir))
        stack.enter_context(patch("gitgym.runner.EXERCISES_DIR", exercises_dir))
        stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
        return runner.invoke(main, ["verify"])


# --- Tests for "no exercise in progress" ---


def test_verify_no_exercise_in_progress_exits_nonzero():
    result = _invoke_verify(None, [])
    assert result.exit_code != 0


def test_verify_no_exercise_in_progress_shows_message():
    result = _invoke_verify(None, [])
    assert "No exercise is currently in progress" in result.output


def test_verify_no_exercise_in_progress_suggests_start():
    result = _invoke_verify(None, [])
    assert "gitgym start" in result.output


# --- Tests for exercise key not found in definitions ---


def test_verify_exercise_not_in_definitions_exits_nonzero():
    result = _invoke_verify("01_basics/01_init", [])
    assert result.exit_code != 0


def test_verify_exercise_not_in_definitions_shows_error():
    result = _invoke_verify("01_basics/01_init", [])
    assert "01_basics/01_init" in result.output


# --- Tests for successful verification ---


def test_verify_success_exits_zero():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=True)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert result.exit_code == 0, result.output


def test_verify_success_prints_success_message():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=True)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert "Exercise complete" in result.output


def test_verify_success_prints_verify_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=True)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert "Goal met!" in result.output


def test_verify_success_marks_completed():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=True)

        # Seed an in_progress entry so mark_completed has something to update
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {"01_basics/01_init": {"status": "in_progress"}},
                }
            )
        )

        _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )

        data = json.loads(progress_file.read_text())
        assert data["exercises"]["01_basics/01_init"]["status"] == "completed"


# --- Tests for failed verification ---


def test_verify_failure_exits_nonzero():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=False)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert result.exit_code != 0


def test_verify_failure_prints_verify_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=False)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert "Not done yet." in result.output


def test_verify_failure_prints_keep_trying_message():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=False)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert "Keep trying" in result.output


def test_verify_failure_does_not_mark_completed():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=False)

        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {"01_basics/01_init": {"status": "in_progress"}},
                }
            )
        )

        _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )

        data = json.loads(progress_file.read_text())
        assert data["exercises"]["01_basics/01_init"]["status"] == "in_progress"


# --- Tests for missing/corrupted exercise repo ---


def test_verify_missing_workspace_exits_nonzero():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        # Do NOT create the workspace exercise subdirectory
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=True)

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
            stack.enter_context(patch("gitgym.runner.WORKSPACE_DIR", workspace))
            stack.enter_context(patch("gitgym.runner.EXERCISES_DIR", exercises_dir))
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            result = runner.invoke(main, ["verify"])

        assert result.exit_code != 0


def test_verify_missing_workspace_suggests_reset():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        # Do NOT create the workspace exercise subdirectory
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=True)

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
            stack.enter_context(patch("gitgym.runner.WORKSPACE_DIR", workspace))
            stack.enter_context(patch("gitgym.runner.EXERCISES_DIR", exercises_dir))
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
            result = runner.invoke(main, ["verify"])

        assert "gitgym reset" in result.output


# --- Tests for unexpected verify.sh crash (script error) ---


def _make_crashing_exercise(exercises_dir: Path, exit_code: int = 2) -> Exercise:
    """Create a real exercise on disk with a verify.sh that exits with an unexpected code."""
    exercise_dir = exercises_dir / "01_basics" / "01_init"
    exercise_dir.mkdir(parents=True)

    verify_content = f"#!/usr/bin/env bash\necho 'Script crashed!'\nexit {exit_code}\n"
    verify_script = exercise_dir / "verify.sh"
    verify_script.write_text(verify_content)
    verify_script.chmod(verify_script.stat().st_mode | stat.S_IEXEC)

    return Exercise(
        name="init",
        topic="Basics",
        title="Initialize a Repository",
        description="Initialize a git repo.",
        goal_summary="Repo initialized.",
        hints=["Run git init"],
        path=exercise_dir,
    )


def test_verify_script_error_exits_nonzero():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_crashing_exercise(exercises_dir, exit_code=2)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert result.exit_code != 0


def test_verify_script_error_prints_error_message():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_crashing_exercise(exercises_dir, exit_code=2)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert "unexpected error" in result.output.lower()


def test_verify_script_error_suggests_reset():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_crashing_exercise(exercises_dir, exit_code=2)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert "gitgym reset" in result.output


def test_verify_script_error_does_not_show_keep_trying():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_crashing_exercise(exercises_dir, exit_code=2)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert "Keep trying" not in result.output


def test_verify_script_error_does_not_mark_completed():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_crashing_exercise(exercises_dir, exit_code=2)

        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {"01_basics/01_init": {"status": "in_progress"}},
                }
            )
        )

        _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )

        data = json.loads(progress_file.read_text())
        assert data["exercises"]["01_basics/01_init"]["status"] == "in_progress"


def test_verify_exit_1_does_not_show_unexpected_error():
    """Exit code 1 should show 'Keep trying', not the script error message."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir, verify_exits_zero=False)

        result = _invoke_verify_with_real_runner(
            "01_basics/01_init", [ex], workspace, progress_file, exercises_dir
        )
        assert "Keep trying" in result.output
        assert "unexpected error" not in result.output.lower()
