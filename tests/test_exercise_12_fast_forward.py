"""End-to-end tests for exercises/04_merging/01_fast_forward."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "04_merging" / "01_fast_forward"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "01_fast_forward"
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
    assert ex.name == "fast_forward"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Merging"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "merge" in ex.title.lower() or "forward" in ex.title.lower()


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


def test_setup_feature_branch_exists(work_dir):
    result = subprocess.run(
        ["git", "branch", "--list", "feature"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "feature" in result.stdout


def test_setup_feature_ahead_of_main(work_dir):
    """feature should have commits that main does not (ready for fast-forward)."""
    result = subprocess.run(
        ["git", "log", "--oneline", "main..feature"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() != ""


def test_setup_main_not_ahead_of_feature(work_dir):
    """main should have no commits that feature does not (no divergence)."""
    result = subprocess.run(
        ["git", "log", "--oneline", "feature..main"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == ""


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "01_fast_forward"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "branch", "--list", "feature"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert "feature" in result.stdout


# --- verify.sh: before goal is met ---


def test_verify_fails_before_merge(work_dir):
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


def test_verify_fails_when_on_feature_branch(work_dir):
    subprocess.run(
        ["git", "switch", "feature"],
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


def test_verify_succeeds_after_fast_forward_merge(work_dir):
    subprocess.run(
        ["git", "merge", "feature"],
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


def test_verify_fails_with_no_ff_merge(work_dir):
    """--no-ff creates a merge commit, which should not satisfy fast-forward."""
    subprocess.run(
        ["git", "merge", "--no-ff", "-m", "merge commit", "feature"],
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


def test_verify_success_output_mentions_feature(work_dir):
    subprocess.run(
        ["git", "merge", "feature"],
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
