"""Integration tests for the `gitgym reset` command."""

import json
import stat
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from gitgym.cli import main
from gitgym.exercise import Exercise


def _make_exercise(
    name="init", topic_dir="01_basics", exercise_dir="01_init", path=None
) -> Exercise:
    if path is None:
        path = Path(f"/tmp/exercises/{topic_dir}/{exercise_dir}")
    return Exercise(
        name=name,
        topic="Basics",
        title="Initialize a Repository",
        description="A detailed description.",
        goal_summary="The goal summary.",
        hints=["Hint one."],
        path=path,
    )


def _make_real_exercise(exercises_dir: Path) -> Exercise:
    """Create a real exercise on disk with a setup.sh script."""
    exercise_dir = exercises_dir / "01_basics" / "01_init"
    exercise_dir.mkdir(parents=True)

    setup_content = (
        "#!/usr/bin/env bash\nset -euo pipefail\n"
        'EXERCISE_DIR="$1"\nmkdir -p "$EXERCISE_DIR"\n'
        'touch "$EXERCISE_DIR/reset_marker.txt"\n'
    )
    setup_script = exercise_dir / "setup.sh"
    setup_script.write_text(setup_content)
    setup_script.chmod(setup_script.stat().st_mode | stat.S_IEXEC)

    return Exercise(
        name="init",
        topic="Basics",
        title="Initialize a Repository",
        description="Initialize a git repo.",
        goal_summary="Repo initialized.",
        hints=["Run git init"],
        path=exercise_dir,
    )


_UNSET = object()


def _invoke_reset(
    args,
    exercises=None,
    current_key=_UNSET,
    workspace_dir=None,
    progress_file=None,
    exercises_dir=None,
):
    runner = CliRunner()
    with ExitStack() as stack:
        stack.enter_context(patch("gitgym.cli._is_git_installed", return_value=True))
        if exercises is not None:
            stack.enter_context(
                patch("gitgym.cli.load_all_exercises", return_value=exercises)
            )
        if current_key is not _UNSET:
            stack.enter_context(
                patch("gitgym.cli.get_current_exercise", return_value=current_key)
            )
        if workspace_dir is not None:
            stack.enter_context(patch("gitgym.runner.WORKSPACE_DIR", workspace_dir))
            stack.enter_context(patch("gitgym.cli.WORKSPACE_DIR", workspace_dir))
        if progress_file is not None:
            stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
        if exercises_dir is not None:
            stack.enter_context(patch("gitgym.runner.EXERCISES_DIR", exercises_dir))
        return runner.invoke(main, ["reset"] + args)


# --- Tests for reset --all ---


def test_reset_all_exits_zero():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {"01_basics/01_init": {"status": "completed"}},
                }
            )
        )

        result = _invoke_reset(
            ["--all"], workspace_dir=workspace, progress_file=progress_file
        )
        assert result.exit_code == 0, result.output


def test_reset_all_prints_confirmation():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        progress_file.write_text(json.dumps({"version": 1, "exercises": {}}))

        result = _invoke_reset(
            ["--all"], workspace_dir=workspace, progress_file=progress_file
        )
        assert "reset" in result.output.lower() or "cleared" in result.output.lower()


def test_reset_all_deletes_workspace():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        # Put something in the workspace
        (workspace / "some_exercise").mkdir()

        _invoke_reset(
            ["--all"], workspace_dir=workspace, progress_file=tmpdir / "progress.json"
        )
        assert not workspace.exists()


def test_reset_all_deletes_progress_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {"01_basics/01_init": {"status": "completed"}},
                }
            )
        )

        _invoke_reset(["--all"], workspace_dir=workspace, progress_file=progress_file)
        assert not progress_file.exists()


def test_reset_all_no_workspace_still_exits_zero():
    """reset --all should succeed even if workspace doesn't exist yet."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "nonexistent_workspace"

        result = _invoke_reset(
            ["--all"], workspace_dir=workspace, progress_file=tmpdir / "progress.json"
        )
        assert result.exit_code == 0


def test_reset_all_no_progress_file_still_exits_zero():
    """reset --all should succeed even if progress file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"  # does not exist

        result = _invoke_reset(
            ["--all"], workspace_dir=workspace, progress_file=progress_file
        )
        assert result.exit_code == 0


# --- Tests for reset <exercise> ---


def test_reset_named_exercise_exits_zero():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir)

        result = _invoke_reset(
            ["init"],
            exercises=[ex],
            workspace_dir=workspace,
            progress_file=progress_file,
            exercises_dir=exercises_dir,
        )
        assert result.exit_code == 0, result.output


def test_reset_named_exercise_prints_reset_message():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir)

        result = _invoke_reset(
            ["init"],
            exercises=[ex],
            workspace_dir=workspace,
            progress_file=progress_file,
            exercises_dir=exercises_dir,
        )
        assert "reset" in result.output.lower()


def test_reset_named_exercise_reruns_setup():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir)

        _invoke_reset(
            ["init"],
            exercises=[ex],
            workspace_dir=workspace,
            progress_file=progress_file,
            exercises_dir=exercises_dir,
        )
        # setup.sh creates reset_marker.txt in the workspace exercise dir
        marker = workspace / "01_basics" / "01_init" / "reset_marker.txt"
        assert marker.exists()


def test_reset_named_exercise_clears_progress():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        exercises_dir = tmpdir / "exercises"
        progress_file = tmpdir / "progress.json"
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {"01_basics/01_init": {"status": "completed"}},
                }
            )
        )

        ex = _make_real_exercise(exercises_dir)

        _invoke_reset(
            ["init"],
            exercises=[ex],
            workspace_dir=workspace,
            progress_file=progress_file,
            exercises_dir=exercises_dir,
        )
        data = json.loads(progress_file.read_text())
        assert "01_basics/01_init" not in data["exercises"]


def test_reset_named_exercise_not_found_exits_nonzero():
    result = _invoke_reset(["nonexistent"], exercises=[], current_key=None)
    assert result.exit_code != 0


def test_reset_named_exercise_not_found_shows_error():
    result = _invoke_reset(["nonexistent"], exercises=[])
    assert "nonexistent" in result.output


# --- Tests for reset (no argument, current exercise) ---


def test_reset_no_arg_no_exercise_in_progress_exits_nonzero():
    result = _invoke_reset([], exercises=[], current_key=None)
    assert result.exit_code != 0


def test_reset_no_arg_no_exercise_in_progress_shows_message():
    result = _invoke_reset([], exercises=[], current_key=None)
    assert "No exercise is currently in progress" in result.output


def test_reset_no_arg_no_exercise_in_progress_suggests_start():
    result = _invoke_reset([], exercises=[], current_key=None)
    assert "gitgym start" in result.output


def test_reset_no_arg_current_exercise_not_in_definitions_exits_nonzero():
    result = _invoke_reset([], exercises=[], current_key="01_basics/01_init")
    assert result.exit_code != 0


def test_reset_no_arg_resets_current_exercise():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        exercises_dir = tmpdir / "exercises"
        progress_file = tmpdir / "progress.json"
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {"01_basics/01_init": {"status": "in_progress"}},
                }
            )
        )

        ex = _make_real_exercise(exercises_dir)

        result = _invoke_reset(
            [],
            exercises=[ex],
            current_key="01_basics/01_init",
            workspace_dir=workspace,
            progress_file=progress_file,
            exercises_dir=exercises_dir,
        )
        assert result.exit_code == 0, result.output


def test_reset_no_arg_clears_progress_for_current_exercise():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        exercises_dir = tmpdir / "exercises"
        progress_file = tmpdir / "progress.json"
        progress_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "exercises": {"01_basics/01_init": {"status": "in_progress"}},
                }
            )
        )

        ex = _make_real_exercise(exercises_dir)

        _invoke_reset(
            [],
            exercises=[ex],
            current_key="01_basics/01_init",
            workspace_dir=workspace,
            progress_file=progress_file,
            exercises_dir=exercises_dir,
        )
        data = json.loads(progress_file.read_text())
        assert "01_basics/01_init" not in data["exercises"]
