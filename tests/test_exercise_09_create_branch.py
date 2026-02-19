"""End-to-end tests for exercises/03_branching/01_create_branch."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "03_branching" / "01_create_branch"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "01_create_branch"
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
    assert ex.name == "create_branch"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Branching"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "branch" in ex.title.lower()


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


def test_setup_creates_readme(work_dir):
    assert (work_dir / "README.md").exists()


def test_setup_has_one_commit(work_dir):
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "1"


def test_setup_starts_on_main(work_dir):
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "main"


def test_setup_no_feature_branch_yet(work_dir):
    result = subprocess.run(
        ["git", "branch", "--list", "feature"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == ""


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "01_create_branch"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert result.stdout.strip() == "1"


# --- verify.sh: before goal is met ---


def test_verify_fails_without_feature_branch(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_feature(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "feature" in combined


def test_verify_fails_when_branch_exists_but_not_checked_out(work_dir):
    subprocess.run(
        ["git", "branch", "feature"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_create_and_switch(work_dir):
    subprocess.run(
        ["git", "switch", "-c", "feature"],
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


def test_verify_succeeds_with_checkout_b(work_dir):
    subprocess.run(
        ["git", "checkout", "-b", "feature"],
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


def test_verify_success_output_mentions_feature(work_dir):
    subprocess.run(
        ["git", "switch", "-c", "feature"],
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
    assert "feature" in combined
