"""End-to-end tests for exercises/07_rebase/01_basic_rebase."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "07_rebase" / "01_basic_rebase"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "01_basic_rebase"
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
    assert ex.name == "basic_rebase"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Rebase"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "rebase" in ex.title.lower()


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


def test_setup_starts_on_feature(work_dir):
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "feature"


def test_setup_main_branch_exists(work_dir):
    result = subprocess.run(
        ["git", "branch", "--list", "main"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "main" in result.stdout


def test_setup_feature_has_commits_beyond_initial(work_dir):
    # feature should have commits that are not on main
    result = subprocess.run(
        ["git", "log", "main..feature", "--oneline"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() != ""


def test_setup_main_has_diverged(work_dir):
    # main should have commits not reachable from feature's original base
    result = subprocess.run(
        ["git", "log", "feature..main", "--oneline"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() != ""


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "01_basic_rebase"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert result.stdout.strip() == "feature"


# --- verify.sh: before goal is met ---


def test_verify_fails_before_rebase(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_rebase(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "rebase" in combined.lower()


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_rebase(work_dir):
    subprocess.run(
        ["git", "rebase", "main"],
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
        ["git", "rebase", "main"],
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
        "excellent" in combined.lower()
        or "great" in combined.lower()
        or "success" in combined.lower()
        or "rebase" in combined.lower()
    )


def test_verify_feature_linear_after_rebase(work_dir):
    """After rebase, merge-base of feature and main should equal main's HEAD."""
    subprocess.run(
        ["git", "rebase", "main"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    merge_base = subprocess.run(
        ["git", "merge-base", "feature", "main"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout.strip()
    main_head = subprocess.run(
        ["git", "rev-parse", "main"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout.strip()
    assert merge_base == main_head
