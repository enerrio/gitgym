import os
import stat
import textwrap
from pathlib import Path
from unittest import mock

import pytest

from gitgym.exercise import Exercise
from gitgym.runner import run_setup


def _make_exercise(exercise_dir: Path, name: str = "test_exercise") -> Exercise:
    """Create an Exercise instance pointing at exercise_dir."""
    return Exercise(
        name=name,
        topic="Test",
        title="Test Exercise",
        description="A test exercise.",
        goal_summary="A test goal.",
        hints=[],
        path=exercise_dir,
    )


def _write_script(path: Path, content: str, executable: bool = True) -> None:
    path.write_text(content)
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


# --- run_setup tests ---


def test_run_setup_returns_true_on_success(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    _write_script(
        exercises_dir / "setup.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            set -euo pipefail
            EXERCISE_DIR="$1"
            mkdir -p "$EXERCISE_DIR"
            touch "$EXERCISE_DIR/hello.txt"
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        result = run_setup(exercise)

    assert result is True


def test_run_setup_creates_expected_file(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    _write_script(
        exercises_dir / "setup.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            set -euo pipefail
            EXERCISE_DIR="$1"
            mkdir -p "$EXERCISE_DIR"
            echo "Hello, git!" > "$EXERCISE_DIR/hello.txt"
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        run_setup(exercise)

    expected_file = workspace_dir / "01_basics" / "01_init" / "hello.txt"
    assert expected_file.exists()
    assert expected_file.read_text().strip() == "Hello, git!"


def test_run_setup_missing_script_returns_false(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        result = run_setup(exercise)

    assert result is False


def test_run_setup_non_executable_script_returns_false(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    # Write the script but do NOT make it executable
    _write_script(
        exercises_dir / "setup.sh",
        "#!/usr/bin/env bash\necho hello\n",
        executable=False,
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        result = run_setup(exercise)

    assert result is False


def test_run_setup_nonzero_exit_returns_false(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    _write_script(
        exercises_dir / "setup.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            exit 1
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        result = run_setup(exercise)

    assert result is False


def test_run_setup_creates_workspace_dir_if_missing(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    _write_script(
        exercises_dir / "setup.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            set -euo pipefail
            mkdir -p "$1"
        """),
    )

    exercise = _make_exercise(exercises_dir)

    assert not workspace_dir.exists()

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        run_setup(exercise)

    assert (workspace_dir / "01_basics" / "01_init").is_dir()


def test_run_setup_passes_workspace_path_as_argument(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    # The script writes its $1 argument to a file so we can verify it
    marker = tmp_path / "received_arg.txt"
    _write_script(
        exercises_dir / "setup.sh",
        textwrap.dedent(f"""\
            #!/usr/bin/env bash
            set -euo pipefail
            echo "$1" > "{marker}"
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        run_setup(exercise)

    expected_path = workspace_dir / "01_basics" / "01_init"
    received = marker.read_text().strip()
    assert received == str(expected_path)


def test_run_setup_missing_script_prints_error(tmp_path, capsys):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        run_setup(exercise)

    captured = capsys.readouterr()
    assert "Error" in captured.out
    assert "setup.sh" in captured.out


def test_run_setup_nonexecutable_script_prints_error(tmp_path, capsys):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    _write_script(
        exercises_dir / "setup.sh", "#!/usr/bin/env bash\necho hi\n", executable=False
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        run_setup(exercise)

    captured = capsys.readouterr()
    assert "Error" in captured.out
    assert "not executable" in captured.out


def test_run_setup_failure_prints_exit_code(tmp_path, capsys):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    _write_script(exercises_dir / "setup.sh", "#!/usr/bin/env bash\nexit 42\n")

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        run_setup(exercise)

    captured = capsys.readouterr()
    assert "42" in captured.out


def test_run_setup_is_idempotent(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    _write_script(
        exercises_dir / "setup.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            set -euo pipefail
            EXERCISE_DIR="$1"
            mkdir -p "$EXERCISE_DIR"
            echo "content" > "$EXERCISE_DIR/file.txt"
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        result1 = run_setup(exercise)
        result2 = run_setup(exercise)

    assert result1 is True
    assert result2 is True
