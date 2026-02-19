"""End-to-end tests for exercises/01_basics/01_init."""

import subprocess
from pathlib import Path

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "01_basics" / "01_init"


@pytest.fixture
def work_dir(tmp_path):
    """Return an empty temp directory that acts as the exercise workspace."""
    d = tmp_path / "01_init"
    d.mkdir()
    return d


# --- exercise.toml parsing ---


def test_exercise_toml_loads():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.name == "init"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Basics"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.title == "Initialize a Repository"


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


def test_setup_creates_hello_txt(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert (work_dir / "hello.txt").exists()


def test_setup_hello_txt_content(work_dir):
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(work_dir)],
        capture_output=True,
        check=True,
    )
    assert (work_dir / "hello.txt").read_text().strip() == "Hello, git!"


def test_setup_does_not_create_git_repo(work_dir):
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(work_dir)],
        capture_output=True,
        check=True,
    )
    assert not (work_dir / ".git").exists()


def test_setup_is_idempotent(work_dir):
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(work_dir)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (work_dir / "hello.txt").exists()
    assert not (work_dir / ".git").exists()


def test_setup_removes_existing_git_repo(work_dir):
    """setup.sh resets to the initial (non-repo) state even if git init was run."""
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(work_dir)],
        capture_output=True,
        check=True,
    )
    subprocess.run(["git", "init", str(work_dir)], capture_output=True, check=True)
    assert (work_dir / ".git").exists()

    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(work_dir)],
        capture_output=True,
        check=True,
    )
    assert not (work_dir / ".git").exists()


# --- verify.sh: before goal is met ---


def test_verify_fails_before_git_init(work_dir):
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(work_dir)],
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_output_mentions_git_init(work_dir):
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(work_dir)],
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "git init" in combined


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_git_init(work_dir):
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(work_dir)],
        capture_output=True,
        check=True,
    )
    subprocess.run(["git", "init", str(work_dir)], capture_output=True, check=True)
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(work_dir)],
        capture_output=True,
        check=True,
    )
    subprocess.run(["git", "init", str(work_dir)], capture_output=True, check=True)
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert combined.strip()
