"""End-to-end tests for exercises/01_basics/03_status."""

import subprocess
from pathlib import Path

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "01_basics" / "03_status"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "03_status"
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
    assert ex.name == "status"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Basics"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "status" in ex.title.lower()


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


def test_setup_creates_feature_txt(work_dir):
    assert (work_dir / "feature.txt").exists()


def test_setup_creates_notes_txt(work_dir):
    assert (work_dir / "notes.txt").exists()


def test_setup_creates_readme_txt(work_dir):
    assert (work_dir / "readme.txt").exists()


def test_setup_feature_txt_is_untracked(work_dir):
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    assert "feature.txt" not in result.stdout


def test_setup_notes_txt_is_untracked(work_dir):
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    assert "notes.txt" not in result.stdout


def test_setup_readme_txt_is_modified_not_staged(work_dir):
    """readme.txt has a committed version and has been modified but not staged."""
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    ).stdout
    unstaged = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    ).stdout
    assert "readme.txt" not in staged
    assert "readme.txt" in unstaged


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "03_status"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    assert (d / "feature.txt").exists()
    assert (d / "notes.txt").exists()


# --- verify.sh: before goal is met ---


def test_verify_fails_with_nothing_staged(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_fails_if_only_feature_staged(work_dir):
    subprocess.run(
        ["git", "add", "feature.txt"], check=True, cwd=work_dir, capture_output=True
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_fails_if_only_readme_staged(work_dir):
    subprocess.run(
        ["git", "add", "readme.txt"], check=True, cwd=work_dir, capture_output=True
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_fails_if_notes_staged(work_dir):
    subprocess.run(
        ["git", "add", "feature.txt", "readme.txt", "notes.txt"],
        check=True,
        cwd=work_dir,
        capture_output=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_file(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    # Should mention at least one of the files that need staging
    assert "feature.txt" in combined or "readme.txt" in combined


# --- verify.sh: after goal is met ---


def test_verify_succeeds_with_correct_files_staged(work_dir):
    subprocess.run(
        ["git", "add", "feature.txt", "readme.txt"],
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


def test_verify_success_output_is_congratulatory(work_dir):
    subprocess.run(
        ["git", "add", "feature.txt", "readme.txt"],
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
