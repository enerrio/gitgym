"""End-to-end tests for exercises/01_basics/04_first_commit."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "01_basics" / "04_first_commit"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "04_first_commit"
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
    assert ex.name == "first_commit"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Basics"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "commit" in ex.title.lower()


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


def test_setup_hello_txt_is_staged(work_dir):
    """hello.txt must be staged after setup so the user only needs to commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    assert "hello.txt" in result.stdout


def test_setup_has_no_commits(work_dir):
    """There should be no commits yet — the user must create the first one."""
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    # Command exits non-zero when there is no HEAD (no commits)
    assert result.returncode != 0 or result.stdout.strip() == "0"


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "04_first_commit"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    assert (d / "hello.txt").exists()
    # After second run, hello.txt should be staged again (no commits)
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=d,
    )
    assert "hello.txt" in result.stdout


# --- verify.sh: before goal is met ---


def test_verify_fails_with_no_commits(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_commit(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "commit" in combined.lower()


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_commit(work_dir):
    subprocess.run(
        ["git", "commit", "-m", "Add hello.txt"],
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


def test_verify_success_echoes_commit_message(work_dir):
    subprocess.run(
        ["git", "commit", "-m", "Add hello.txt"],
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
    assert "Add hello.txt" in combined


def test_verify_success_output_is_congratulatory(work_dir):
    subprocess.run(
        ["git", "commit", "-m", "My first commit"],
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
    assert combined.strip()
