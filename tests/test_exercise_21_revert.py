"""End-to-end tests for exercises/06_undoing/03_revert."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "06_undoing" / "03_revert"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "03_revert"
    d.mkdir()
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(d)],
        capture_output=True,
        check=True,
    )
    return d


def _get_debug_commit_hash(work_dir):
    result = subprocess.run(
        ["git", "log", "--format=%h %s"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    for line in result.stdout.splitlines():
        if "Add debug output" in line:
            return line.split()[0]
    return None


# --- exercise.toml parsing ---


def test_exercise_toml_loads():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.name == "revert"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Undoing Changes"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.title.strip()


def test_exercise_description_not_empty():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.description.strip()


def test_exercise_goal_summary_not_empty():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.goal_summary.strip()


def test_exercise_has_hints():
    ex = load_exercise(EXERCISE_DIR)
    assert len(ex.hints) >= 1


# --- setup.sh initial state ---


def test_setup_creates_git_repo(work_dir):
    assert (work_dir / ".git").is_dir()


def test_setup_has_debug_commit(work_dir):
    assert _get_debug_commit_hash(work_dir) is not None


def test_setup_app_py_has_debug_line(work_dir):
    content = (work_dir / "app.py").read_text()
    assert "DEBUG:" in content


def test_setup_has_readme(work_dir):
    assert (work_dir / "README.md").exists()


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "03_revert"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "log", "--oneline"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert "Add debug output" in result.stdout


# --- verify.sh: before goal is met ---


def test_verify_fails_before_revert(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_revert(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "revert" in combined.lower()


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_revert(work_dir):
    debug_hash = _get_debug_commit_hash(work_dir)
    subprocess.run(
        ["git", "revert", "--no-edit", debug_hash],
        cwd=work_dir,
        check=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    debug_hash = _get_debug_commit_hash(work_dir)
    subprocess.run(
        ["git", "revert", "--no-edit", debug_hash],
        cwd=work_dir,
        check=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert (
        "correct" in combined.lower()
        or "excellent" in combined.lower()
        or "well done" in combined.lower()
        or "great" in combined.lower()
        or "reverted" in combined.lower()
    )


def test_original_commit_still_in_history_after_revert(work_dir):
    """git revert should not remove the original commit from history."""
    debug_hash = _get_debug_commit_hash(work_dir)
    subprocess.run(
        ["git", "revert", "--no-edit", debug_hash],
        cwd=work_dir,
        check=True,
    )
    result = subprocess.run(
        ["git", "log", "--oneline"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "Add debug output" in result.stdout
