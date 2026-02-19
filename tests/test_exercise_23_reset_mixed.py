"""End-to-end tests for exercises/06_undoing/05_reset_mixed."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "06_undoing" / "05_reset_mixed"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "05_reset_mixed"
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
    assert ex.name == "reset_mixed"


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


def test_setup_has_big_commit(work_dir):
    result = subprocess.run(
        ["git", "log", "--oneline"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "Add everything at once" in result.stdout


def test_setup_has_utils_and_styles(work_dir):
    assert (work_dir / "utils.py").exists()
    assert (work_dir / "styles.css").exists()


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "05_reset_mixed"
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
    assert "Add everything at once" in result.stdout


# --- verify.sh: before goal is met ---


def test_verify_fails_before_reset(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_reset(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "reset" in combined.lower() or "everything at once" in combined


def test_verify_fails_after_reset_soft(work_dir):
    """--soft leaves changes staged — verify should fail (nothing should be staged)."""
    subprocess.run(
        ["git", "reset", "--soft", "HEAD~1"],
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


def test_verify_succeeds_after_reset_mixed(work_dir):
    subprocess.run(
        ["git", "reset", "HEAD~1"],
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
        ["git", "reset", "HEAD~1"],
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
        "great" in combined.lower()
        or "correct" in combined.lower()
        or "well done" in combined.lower()
        or "work" in combined.lower()
    )


def test_files_present_in_working_dir_after_reset_mixed(work_dir):
    subprocess.run(
        ["git", "reset", "HEAD~1"],
        cwd=work_dir,
        check=True,
    )
    assert (work_dir / "utils.py").exists()
    assert (work_dir / "styles.css").exists()


def test_nothing_staged_after_reset_mixed(work_dir):
    subprocess.run(
        ["git", "reset", "HEAD~1"],
        cwd=work_dir,
        check=True,
    )
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == ""
