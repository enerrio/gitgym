"""End-to-end tests for exercises/07_rebase/03_rebase_conflict."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "07_rebase" / "03_rebase_conflict"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "03_rebase_conflict"
    d.mkdir()
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(d)],
        capture_output=True,
        check=True,
    )
    return d


def _rebase_and_resolve(work_dir):
    """Helper: start rebase, resolve conflict, continue."""
    # Start rebase (will conflict)
    subprocess.run(
        ["git", "rebase", "main"],
        cwd=work_dir,
        capture_output=True,
    )
    # Resolve conflict: pick a value for config.txt
    (work_dir / "config.txt").write_text("timeout=60\n")
    subprocess.run(
        ["git", "add", "config.txt"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "rebase", "--continue"],
        cwd=work_dir,
        capture_output=True,
        check=True,
        env={"GIT_EDITOR": "true", **__import__("os").environ},
    )


# --- exercise.toml parsing ---


def test_exercise_toml_loads():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.name == "rebase_conflict"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Rebase"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "conflict" in ex.title.lower() or "rebase" in ex.title.lower()


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


def test_setup_creates_config_txt(work_dir):
    assert (work_dir / "config.txt").exists()


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


def test_setup_rebase_produces_conflict(work_dir):
    """Rebasing feature onto main should produce a conflict."""
    result = subprocess.run(
        ["git", "rebase", "main"],
        cwd=work_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    # Abort so the fixture dir is clean
    subprocess.run(
        ["git", "rebase", "--abort"],
        cwd=work_dir,
        capture_output=True,
    )


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "03_rebase_conflict"
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


def test_verify_fails_during_unresolved_conflict(work_dir):
    """If rebase is paused due to conflict, verify should fail."""
    subprocess.run(
        ["git", "rebase", "main"],
        cwd=work_dir,
        capture_output=True,
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    # Clean up
    subprocess.run(
        ["git", "rebase", "--abort"],
        cwd=work_dir,
        capture_output=True,
    )


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_resolving_conflict(work_dir):
    _rebase_and_resolve(work_dir)
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    _rebase_and_resolve(work_dir)
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert (
        "great" in combined.lower()
        or "excellent" in combined.lower()
        or "conflict" in combined.lower()
        or "rebase" in combined.lower()
    )


def test_verify_fails_with_conflict_markers_remaining(work_dir):
    """verify should fail if config.txt still has conflict markers."""
    subprocess.run(
        ["git", "rebase", "main"],
        cwd=work_dir,
        capture_output=True,
    )
    # Write conflict markers back
    (work_dir / "config.txt").write_text(
        "<<<<<<< HEAD\ntimeout=45\n=======\ntimeout=60\n>>>>>>> feature\n"
    )
    subprocess.run(
        ["git", "add", "config.txt"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    # Force commit with markers to simulate a bad resolution
    subprocess.run(
        ["git", "rebase", "--continue"],
        cwd=work_dir,
        capture_output=True,
        env={"GIT_EDITOR": "true", **__import__("os").environ},
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
