"""End-to-end tests for exercises/02_committing/01_amend."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "02_committing" / "01_amend"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "01_amend"
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
    assert ex.name == "amend"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Committing"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "amend" in ex.title.lower()


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


def test_setup_creates_hello_txt(work_dir):
    assert (work_dir / "hello.txt").exists()


def test_setup_has_one_commit(work_dir):
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "1"


def test_setup_commit_message_has_typo(work_dir):
    result = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "worlt" in result.stdout


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "01_amend"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    assert (d / "hello.txt").exists()
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert result.stdout.strip() == "1"


# --- verify.sh: before goal is met ---


def test_verify_fails_with_typo_commit(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_typo(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "worlt" in combined


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_amend(work_dir):
    subprocess.run(
        ["git", "commit", "--amend", "-m", "Add hello world"],
        check=True,
        cwd=work_dir,
        capture_output=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_mentions_new_message(work_dir):
    subprocess.run(
        ["git", "commit", "--amend", "-m", "Add hello world"],
        check=True,
        cwd=work_dir,
        capture_output=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "Add hello world" in combined


def test_verify_succeeds_with_any_non_typo_message(work_dir):
    """Any message without 'worlt' should pass."""
    subprocess.run(
        ["git", "commit", "--amend", "-m", "Initial commit"],
        check=True,
        cwd=work_dir,
        capture_output=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_still_has_one_commit_after_amend(work_dir):
    """Amend should not create a second commit."""
    subprocess.run(
        ["git", "commit", "--amend", "-m", "Add hello world"],
        check=True,
        cwd=work_dir,
        capture_output=True,
    )
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "1"
