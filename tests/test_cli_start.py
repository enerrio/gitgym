"""Integration tests for the `gitgym start` command."""

import json
import stat
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from gitgym.cli import _exercise_key, _find_by_name, _find_next_incomplete, main
from gitgym.exercise import Exercise


def _make_exercise(name, topic, title, topic_dir, exercise_dir, path=None) -> Exercise:
    if path is None:
        path = Path(f"/tmp/exercises/{topic_dir}/{exercise_dir}")
    return Exercise(
        name=name,
        topic=topic,
        title=title,
        description="A description.",
        goal_summary="A goal.",
        hints=["Hint one."],
        path=path,
    )


# --- Unit tests for helper functions ---


def test_exercise_key():
    ex = _make_exercise("init", "Basics", "Init", "01_basics", "01_init")
    assert _exercise_key(ex) == "01_basics/01_init"


def test_find_by_name_found():
    ex = _make_exercise("init", "Basics", "Init", "01_basics", "01_init")
    result = _find_by_name([ex], "init")
    assert result is ex


def test_find_by_name_not_found():
    ex = _make_exercise("init", "Basics", "Init", "01_basics", "01_init")
    result = _find_by_name([ex], "nonexistent")
    assert result is None


def test_find_next_incomplete_not_started():
    ex = _make_exercise("init", "Basics", "Init", "01_basics", "01_init")
    result = _find_next_incomplete([ex], {"exercises": {}})
    assert result is ex


def test_find_next_incomplete_skips_completed():
    ex1 = _make_exercise("init", "Basics", "Init", "01_basics", "01_init")
    ex2 = _make_exercise("staging", "Basics", "Staging", "01_basics", "02_staging")
    progress = {"exercises": {"01_basics/01_init": {"status": "completed"}}}
    result = _find_next_incomplete([ex1, ex2], progress)
    assert result is ex2


def test_find_next_incomplete_returns_in_progress():
    ex1 = _make_exercise("init", "Basics", "Init", "01_basics", "01_init")
    ex2 = _make_exercise("staging", "Basics", "Staging", "01_basics", "02_staging")
    progress = {"exercises": {"01_basics/01_init": {"status": "in_progress"}}}
    result = _find_next_incomplete([ex1, ex2], progress)
    assert result is ex1


def test_find_next_incomplete_all_completed():
    ex = _make_exercise("init", "Basics", "Init", "01_basics", "01_init")
    progress = {"exercises": {"01_basics/01_init": {"status": "completed"}}}
    result = _find_next_incomplete([ex], progress)
    assert result is None


# --- Integration tests for the start command ---


def _make_real_exercise(exercises_dir: Path) -> Exercise:
    """Create a real exercise on disk with a working setup.sh."""
    exercise_dir = exercises_dir / "01_basics" / "01_init"
    exercise_dir.mkdir(parents=True)

    setup_script = exercise_dir / "setup.sh"
    setup_script.write_text(
        '#!/usr/bin/env bash\nset -euo pipefail\nmkdir -p "$1"\ntouch "$1/hello.txt"\n'
    )
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


def _invoke_start(
    exercises, progress, args, workspace_dir, progress_file, exercises_dir
):
    runner = CliRunner()
    with ExitStack() as stack:
        stack.enter_context(
            patch("gitgym.cli.load_all_exercises", return_value=exercises)
        )
        stack.enter_context(patch("gitgym.cli.load_progress", return_value=progress))
        stack.enter_context(patch("gitgym.cli._is_git_installed", return_value=True))
        stack.enter_context(patch("gitgym.cli.WORKSPACE_DIR", workspace_dir))
        stack.enter_context(patch("gitgym.runner.WORKSPACE_DIR", workspace_dir))
        stack.enter_context(patch("gitgym.runner.EXERCISES_DIR", exercises_dir))
        stack.enter_context(patch("gitgym.progress.PROGRESS_FILE", progress_file))
        return runner.invoke(main, ["start"] + args)


def test_start_no_arg_sets_up_first_incomplete():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir)

        result = _invoke_start(
            [ex], {"exercises": {}}, [], workspace, progress_file, exercises_dir
        )
        assert result.exit_code == 0, result.output


def test_start_no_arg_prints_exercise_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir)

        result = _invoke_start(
            [ex], {"exercises": {}}, [], workspace, progress_file, exercises_dir
        )
        assert "Exercise directory:" in result.output


def test_start_no_arg_prints_description():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir)

        result = _invoke_start(
            [ex], {"exercises": {}}, [], workspace, progress_file, exercises_dir
        )
        assert "Initialize a git repo." in result.output


def test_start_no_arg_marks_in_progress():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir)

        _invoke_start(
            [ex], {"exercises": {}}, [], workspace, progress_file, exercises_dir
        )

        data = json.loads(progress_file.read_text())
        key = f"{ex.path.parent.name}/{ex.path.name}"
        assert data["exercises"][key]["status"] == "in_progress"


def test_start_with_name_sets_up_named_exercise():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        ex = _make_real_exercise(exercises_dir)

        result = _invoke_start(
            [ex], {"exercises": {}}, ["init"], workspace, progress_file, exercises_dir
        )
        assert result.exit_code == 0, result.output


def test_start_with_unknown_name_exits_nonzero():
    runner = CliRunner()
    with patch("gitgym.cli.load_all_exercises", return_value=[]):
        with patch("gitgym.cli.load_progress", return_value={"exercises": {}}):
            with patch("gitgym.cli._is_git_installed", return_value=True):
                result = runner.invoke(main, ["start", "nonexistent"])
    assert result.exit_code != 0


def test_start_with_unknown_name_shows_error():
    runner = CliRunner()
    with patch("gitgym.cli.load_all_exercises", return_value=[]):
        with patch("gitgym.cli.load_progress", return_value={"exercises": {}}):
            with patch("gitgym.cli._is_git_installed", return_value=True):
                result = runner.invoke(main, ["start", "nonexistent"])
    assert "nonexistent" in result.output


def test_start_all_completed_shows_message():
    ex = _make_exercise("init", "Basics", "Init", "01_basics", "01_init")
    runner = CliRunner()
    progress = {"exercises": {"01_basics/01_init": {"status": "completed"}}}
    with patch("gitgym.cli.load_all_exercises", return_value=[ex]):
        with patch("gitgym.cli.load_progress", return_value=progress):
            with patch("gitgym.cli._is_git_installed", return_value=True):
                result = runner.invoke(main, ["start"])
    assert result.exit_code == 0
    assert "completed" in result.output.lower()


def test_start_skips_completed_exercises():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        workspace = tmpdir / "workspace"
        workspace.mkdir()
        progress_file = tmpdir / "progress.json"
        exercises_dir = tmpdir / "exercises"

        # Two exercises; first is completed, second should be started
        ex1 = _make_real_exercise(exercises_dir)

        ex2_dir = exercises_dir / "01_basics" / "02_staging"
        ex2_dir.mkdir(parents=True)
        setup2 = ex2_dir / "setup.sh"
        setup2.write_text(
            '#!/usr/bin/env bash\nset -euo pipefail\nmkdir -p "$1"\ntouch "$1/file.txt"\n'
        )
        setup2.chmod(setup2.stat().st_mode | stat.S_IEXEC)

        ex2 = Exercise(
            name="staging",
            topic="Basics",
            title="Staging Files",
            description="Stage some files.",
            goal_summary="Files staged.",
            hints=[],
            path=ex2_dir,
        )

        progress = {"exercises": {"01_basics/01_init": {"status": "completed"}}}
        result = _invoke_start(
            [ex1, ex2], progress, [], workspace, progress_file, exercises_dir
        )
        assert result.exit_code == 0
        assert "Staging Files" in result.output
