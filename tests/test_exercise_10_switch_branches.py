"""End-to-end tests for exercises/03_branching/02_switch_branches."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "03_branching" / "02_switch_branches"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "02_switch_branches"
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
    assert ex.name == "switch_branches"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Branching"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "switch" in ex.title.lower() or "branch" in ex.title.lower()


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


def test_setup_starts_on_main(work_dir):
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "main"


def test_setup_bugfix_branch_exists(work_dir):
    result = subprocess.run(
        ["git", "branch", "--list", "bugfix"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "bugfix" in result.stdout


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "02_switch_branches"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "branch", "--list", "bugfix"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert "bugfix" in result.stdout


# --- verify.sh: before goal is met ---


def test_verify_fails_on_main(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_bugfix(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "bugfix" in combined


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_switching(work_dir):
    subprocess.run(
        ["git", "switch", "bugfix"],
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


def test_verify_succeeds_with_checkout(work_dir):
    subprocess.run(
        ["git", "checkout", "bugfix"],
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
        ["git", "switch", "bugfix"],
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
    assert "bugfix" in combined
