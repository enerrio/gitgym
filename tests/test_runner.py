import os
import stat
import textwrap
from pathlib import Path
from unittest import mock

from gitgym.exercise import Exercise
from gitgym.runner import run_setup, run_verify


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


def test_run_setup_failure_suggests_filing_bug(tmp_path, capsys):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    _write_script(
        exercises_dir / "setup.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            echo "something went wrong" >&2
            exit 1
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        run_setup(exercise)

    captured = capsys.readouterr()
    assert "bug" in captured.out.lower()


def test_run_setup_failure_prints_stderr(tmp_path, capsys):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"

    _write_script(
        exercises_dir / "setup.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            echo "detailed error output" >&2
            exit 1
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        run_setup(exercise)

    captured = capsys.readouterr()
    assert "detailed error output" in captured.out


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


# --- run_verify tests ---


def test_run_verify_returns_true_on_success(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    (workspace_dir / "01_basics" / "01_init").mkdir(parents=True)

    _write_script(
        exercises_dir / "verify.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            set -euo pipefail
            echo "Great job!"
            exit 0
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        success, output, is_script_error = run_verify(exercise)

    assert success is True
    assert "Great job!" in output
    assert is_script_error is False


def test_run_verify_returns_false_on_failure(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    (workspace_dir / "01_basics" / "01_init").mkdir(parents=True)

    _write_script(
        exercises_dir / "verify.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            echo "Not done yet."
            exit 1
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        success, output, is_script_error = run_verify(exercise)

    assert success is False
    assert "Not done yet." in output
    assert is_script_error is False


def test_run_verify_missing_script_returns_false(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    (workspace_dir / "01_basics" / "01_init").mkdir(parents=True)

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        success, output, is_script_error = run_verify(exercise)

    assert success is False
    assert "Error" in output
    assert "verify.sh" in output
    assert is_script_error is True


def test_run_verify_non_executable_script_returns_false(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    (workspace_dir / "01_basics" / "01_init").mkdir(parents=True)

    _write_script(
        exercises_dir / "verify.sh",
        "#!/usr/bin/env bash\nexit 0\n",
        executable=False,
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        success, output, is_script_error = run_verify(exercise)

    assert success is False
    assert "not executable" in output
    assert is_script_error is True


def test_run_verify_captures_stdout_and_stderr(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    (workspace_dir / "01_basics" / "01_init").mkdir(parents=True)

    _write_script(
        exercises_dir / "verify.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            echo "stdout message"
            echo "stderr message" >&2
            exit 1
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        success, output, is_script_error = run_verify(exercise)

    assert success is False
    assert "stdout message" in output
    assert "stderr message" in output


def test_run_verify_exit_1_is_not_script_error(tmp_path):
    """Exit code 1 is the conventional 'goal not met' signal — not a script error."""
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    (workspace_dir / "01_basics" / "01_init").mkdir(parents=True)

    _write_script(
        exercises_dir / "verify.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            echo "Not done yet."
            exit 1
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        _success, _output, is_script_error = run_verify(exercise)

    assert is_script_error is False


def test_run_verify_exit_2_is_script_error(tmp_path):
    """Exit codes other than 0 or 1 indicate an unexpected script crash."""
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    (workspace_dir / "01_basics" / "01_init").mkdir(parents=True)

    _write_script(
        exercises_dir / "verify.sh",
        textwrap.dedent("""\
            #!/usr/bin/env bash
            set -euo pipefail
            # Referencing an unbound variable causes bash to exit with code 1
            # under set -e; use an explicit exit 2 to simulate a crash.
            exit 2
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        success, _output, is_script_error = run_verify(exercise)

    assert success is False
    assert is_script_error is True


def test_run_verify_exit_42_is_script_error(tmp_path):
    """Any high exit code (not 0 or 1) is flagged as a script error."""
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    (workspace_dir / "01_basics" / "01_init").mkdir(parents=True)

    _write_script(
        exercises_dir / "verify.sh",
        "#!/usr/bin/env bash\nexit 42\n",
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        success, _output, is_script_error = run_verify(exercise)

    assert success is False
    assert is_script_error is True


def test_run_verify_passes_workspace_path_as_argument(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    (workspace_dir / "01_basics" / "01_init").mkdir(parents=True)

    marker = tmp_path / "received_arg.txt"
    _write_script(
        exercises_dir / "verify.sh",
        textwrap.dedent(f"""\
            #!/usr/bin/env bash
            set -euo pipefail
            echo "$1" > "{marker}"
            exit 0
        """),
    )

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        run_verify(exercise)

    expected_path = workspace_dir / "01_basics" / "01_init"
    received = marker.read_text().strip()
    assert received == str(expected_path)


# --- run_verify: missing workspace tests ---


def test_run_verify_missing_workspace_returns_false(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    # Do NOT create the workspace exercise subdirectory

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        success, output, is_script_error = run_verify(exercise)

    assert success is False
    assert is_script_error is True


def test_run_verify_missing_workspace_suggests_reset(tmp_path):
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace"
    # Do NOT create the workspace exercise subdirectory

    exercise = _make_exercise(exercises_dir)

    with (
        mock.patch("gitgym.runner.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.runner.WORKSPACE_DIR", workspace_dir),
    ):
        _success, output, _is_script_error = run_verify(exercise)

    assert "gitgym reset" in output
