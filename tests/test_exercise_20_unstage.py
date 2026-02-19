"""End-to-end tests for exercises/06_undoing/02_unstage."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "06_undoing" / "02_unstage"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "02_unstage"
    d.mkdir()
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(d)],
        capture_output=True,
        check=True,
    )
    return d


# --- exercise.toml parsing ---


def test_exercise_toml_loads():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.name == "unstage"


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


def test_setup_notes_txt_is_staged(work_dir):
    """notes.txt changes should be staged after setup."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "notes.txt" in result.stdout


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "02_unstage"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert "notes.txt" in result.stdout


# --- verify.sh: before goal is met ---


def test_verify_fails_when_file_is_staged(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_staged(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "staged" in combined.lower() or "notes.txt" in combined


def test_verify_fails_when_changes_discarded_entirely(work_dir):
    """Discarding all changes (--hard equivalent) should also fail since WD changes are gone."""
    subprocess.run(
        ["git", "restore", "--staged", "notes.txt"],
        cwd=work_dir,
        check=True,
    )
    subprocess.run(
        ["git", "restore", "notes.txt"],
        cwd=work_dir,
        check=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_unstage(work_dir):
    subprocess.run(
        ["git", "restore", "--staged", "notes.txt"],
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
    subprocess.run(
        ["git", "restore", "--staged", "notes.txt"],
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
        or "well done" in combined.lower()
        or "great" in combined.lower()
        or "unstaged" in combined.lower()
    )
