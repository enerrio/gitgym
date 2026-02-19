"""End-to-end tests for exercises/06_undoing/04_reset_soft."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "06_undoing" / "04_reset_soft"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "04_reset_soft"
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
    assert ex.name == "reset_soft"


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


def test_setup_has_wip_commit(work_dir):
    result = subprocess.run(
        ["git", "log", "--oneline"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "WIP: half-done feature" in result.stdout


def test_setup_has_feature_py(work_dir):
    assert (work_dir / "feature.py").exists()


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "04_reset_soft"
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
    assert "WIP: half-done feature" in result.stdout


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
    assert "reset" in combined.lower() or "WIP" in combined


def test_verify_fails_after_reset_hard(work_dir):
    """--hard removes the changes entirely — verify should fail."""
    subprocess.run(
        ["git", "reset", "--hard", "HEAD~1"],
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


def test_verify_succeeds_after_reset_soft(work_dir):
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
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
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
    combined = result.stdout + result.stderr
    assert (
        "perfect" in combined.lower()
        or "correct" in combined.lower()
        or "well done" in combined.lower()
        or "great" in combined.lower()
        or "staged" in combined.lower()
    )


def test_feature_py_still_staged_after_reset_soft(work_dir):
    subprocess.run(
        ["git", "reset", "--soft", "HEAD~1"],
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
    assert "feature.py" in result.stdout
