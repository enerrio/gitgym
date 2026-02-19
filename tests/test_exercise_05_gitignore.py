"""End-to-end tests for exercises/01_basics/05_gitignore."""

import subprocess
from pathlib import Path

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "01_basics" / "05_gitignore"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "05_gitignore"
    d.mkdir()
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(d)],
        capture_output=True,
        check=True,
    )
    return d


def _write_gitignore(work_dir: Path, content: str) -> None:
    (work_dir / ".gitignore").write_text(content)


# --- exercise.toml parsing ---


def test_exercise_toml_loads():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.name == "gitignore"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Basics"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "gitignore" in ex.title.lower() or "ignore" in ex.title.lower()


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


def test_setup_creates_build_log(work_dir):
    assert (work_dir / "build.log").exists()


def test_setup_creates_secret_key(work_dir):
    assert (work_dir / "secret.key").exists()


def test_setup_creates_main_py(work_dir):
    assert (work_dir / "main.py").exists()


def test_setup_does_not_create_gitignore(work_dir):
    assert not (work_dir / ".gitignore").exists()


def test_setup_build_log_is_untracked(work_dir):
    result = subprocess.run(
        ["git", "status", "--porcelain", "build.log"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    # Untracked files appear as "?? build.log"
    assert "??" in result.stdout


def test_setup_main_py_is_committed(work_dir):
    result = subprocess.run(
        ["git", "log", "--oneline"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    assert result.returncode == 0
    assert result.stdout.strip()  # At least one commit


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "05_gitignore"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    # Simulate user adding a .gitignore, then re-running setup
    (d / ".gitignore").write_text("build.log\nsecret.key\n")
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    assert (d / "build.log").exists()
    assert (d / "secret.key").exists()
    assert not (d / ".gitignore").exists()


# --- verify.sh: no .gitignore at all ---


def test_verify_fails_without_gitignore(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_gitignore(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert ".gitignore" in combined


# --- verify.sh: partial .gitignore ---


def test_verify_fails_if_only_build_log_ignored(work_dir):
    _write_gitignore(work_dir, "build.log\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_fails_if_only_secret_key_ignored(work_dir):
    _write_gitignore(work_dir, "secret.key\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


# --- verify.sh: correct .gitignore ---


def test_verify_succeeds_with_correct_gitignore(work_dir):
    _write_gitignore(work_dir, "build.log\nsecret.key\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    _write_gitignore(work_dir, "build.log\nsecret.key\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert combined.strip()
