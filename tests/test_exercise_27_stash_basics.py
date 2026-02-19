"""End-to-end tests for exercises/08_stashing/01_stash_basics."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "08_stashing" / "01_stash_basics"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "01_stash_basics"
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
    assert ex.name == "stash_basics"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Stashing"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "stash" in ex.title.lower()


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


def test_setup_creates_notes_txt(work_dir):
    assert (work_dir / "notes.txt").exists()


def test_setup_creates_stash_entry(work_dir):
    result = subprocess.run(
        ["git", "stash", "list"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() != ""


def test_setup_working_dir_is_clean(work_dir):
    """After setup, working dir should be clean (changes are stashed)."""
    result = subprocess.run(
        ["git", "diff", "--quiet"],
        cwd=work_dir,
        capture_output=True,
    )
    assert result.returncode == 0


def test_setup_notes_missing_stashed_content(work_dir):
    """notes.txt should not have the Action items content before the stash is popped."""
    content = (work_dir / "notes.txt").read_text()
    assert "Action items" not in content


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "01_stash_basics"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "stash", "list"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert result.stdout.strip() != ""


# --- verify.sh: before goal is met ---


def test_verify_fails_before_pop(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_stash(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "stash" in combined.lower()


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_stash_pop(work_dir):
    subprocess.run(
        ["git", "stash", "pop"],
        cwd=work_dir,
        capture_output=True,
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
        ["git", "stash", "pop"],
        cwd=work_dir,
        capture_output=True,
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
        or "excellent" in combined.lower()
        or "stash" in combined.lower()
    )


def test_verify_stash_is_empty_after_pop(work_dir):
    subprocess.run(
        ["git", "stash", "pop"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        ["git", "stash", "list"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == ""


def test_verify_notes_has_action_items_after_pop(work_dir):
    subprocess.run(
        ["git", "stash", "pop"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    content = (work_dir / "notes.txt").read_text()
    assert "Action items" in content
