"""End-to-end tests for exercises/01_basics/02_staging."""

import subprocess
from pathlib import Path

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "01_basics" / "02_staging"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "02_staging"
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
    assert ex.name == "staging"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Basics"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.title == "Stage a File"


def test_exercise_description_not_empty():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.description.strip()


def test_exercise_goal_summary_not_empty():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.goal_summary.strip()


def test_exercise_has_hints():
    ex = load_exercise(EXERCISE_DIR)
    assert len(ex.hints) >= 1


# --- setup.sh ---


def test_setup_creates_git_repo(work_dir):
    assert (work_dir / ".git").is_dir()


def test_setup_creates_hello_txt(work_dir):
    assert (work_dir / "hello.txt").exists()


def test_setup_hello_txt_is_untracked(work_dir):
    """hello.txt must NOT be staged after setup — user has to stage it."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    assert "hello.txt" not in result.stdout


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "02_staging"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    assert (d / "hello.txt").exists()


def test_setup_resets_staged_file(tmp_path):
    """Running setup.sh again should un-stage hello.txt if user had staged it."""
    d = tmp_path / "02_staging"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    # Stage the file (simulate the user completing the exercise)
    subprocess.run(["git", "add", "hello.txt"], capture_output=True, check=True, cwd=d)
    # Reset
    subprocess.run([script, arg], capture_output=True, check=True)
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=d,
    )
    assert "hello.txt" not in result.stdout


# --- verify.sh: before goal is met ---


def test_verify_fails_before_staging(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_output_mentions_git_add(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "git add" in combined


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_git_add(work_dir):
    subprocess.run(
        ["git", "add", "hello.txt"], capture_output=True, check=True, cwd=work_dir
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    subprocess.run(
        ["git", "add", "hello.txt"], capture_output=True, check=True, cwd=work_dir
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert combined.strip()
