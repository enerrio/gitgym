"""End-to-end tests for exercises/04_merging/03_merge_conflict."""

import os
import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "04_merging" / "03_merge_conflict"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "03_merge_conflict"
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
    assert ex.name == "merge_conflict"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Merging"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "conflict" in ex.title.lower() or "merge" in ex.title.lower()


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


def test_setup_merge_produces_conflict(work_dir):
    """Merging feature into main should produce a conflict (exit non-zero)."""
    result = subprocess.run(
        ["git", "merge", "feature"],
        cwd=work_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    # Abort the merge so the work_dir is clean for the fixture teardown
    subprocess.run(
        ["git", "merge", "--abort"],
        cwd=work_dir,
        capture_output=True,
    )


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "03_merge_conflict"
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


def test_verify_fails_during_unresolved_conflict(work_dir):
    """If a merge is in progress (conflict markers present), verify should fail."""
    subprocess.run(
        ["git", "merge", "feature"],
        cwd=work_dir,
        capture_output=True,
    )
    # MERGE_HEAD file should exist — verify must fail
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    # Clean up
    subprocess.run(
        ["git", "merge", "--abort"],
        cwd=work_dir,
        capture_output=True,
    )


# --- verify.sh: after goal is met ---


def _resolve_and_merge(work_dir):
    """Helper: start merge, resolve conflict, commit."""
    subprocess.run(
        ["git", "merge", "feature"],
        cwd=work_dir,
        capture_output=True,
    )
    # Resolve conflict by writing a clean version of README.md
    readme = work_dir / "README.md"
    readme.write_text("Project version: 2.0\n")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "--no-edit"],
        cwd=work_dir,
        capture_output=True,
        check=True,
        env={**os.environ, "GIT_EDITOR": "true"},
    )


def test_verify_succeeds_after_resolving_conflict(work_dir):
    _resolve_and_merge(work_dir)
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    _resolve_and_merge(work_dir)
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "conflict" in combined.lower() or "merge" in combined.lower()


def test_verify_fails_with_conflict_markers_remaining(work_dir):
    """verify should fail if README.md still has conflict markers after committing."""
    subprocess.run(
        ["git", "merge", "feature"],
        cwd=work_dir,
        capture_output=True,
    )
    # Write conflict markers back (simulate unresolved file being staged)
    readme = work_dir / "README.md"
    readme.write_text(
        "<<<<<<< HEAD\nProject version: 1.1-main\n=======\nProject version: 2.0-feature\n>>>>>>> feature\n"
    )
    subprocess.run(
        ["git", "add", "README.md"], cwd=work_dir, capture_output=True, check=True
    )
    subprocess.run(
        ["git", "commit", "--no-edit"],
        cwd=work_dir,
        capture_output=True,
        env={**os.environ, "GIT_EDITOR": "true"},
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
