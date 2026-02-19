"""End-to-end tests for exercises/09_advanced/01_cherry_pick."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "09_advanced" / "01_cherry_pick"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "01_cherry_pick"
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
    assert ex.name == "cherry_pick"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Advanced"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "cherry" in ex.title.lower() or "pick" in ex.title.lower()


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


def test_setup_on_main_branch(work_dir):
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "main"


def test_setup_creates_hotfix_branch(work_dir):
    result = subprocess.run(
        ["git", "branch", "--list", "hotfix"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "hotfix" in result.stdout


def test_setup_cherry_pick_this_txt_exists(work_dir):
    assert (work_dir / "cherry_pick_this.txt").exists()


def test_setup_cherry_pick_hash_is_valid(work_dir):
    commit_hash = (work_dir / "cherry_pick_this.txt").read_text().strip()
    result = subprocess.run(
        ["git", "rev-parse", "--verify", commit_hash],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    assert result.returncode == 0


def test_setup_login_fix_not_on_main(work_dir):
    assert not (work_dir / "login_fix.py").exists()


def test_setup_hotfix_has_login_fix_commit(work_dir):
    result = subprocess.run(
        ["git", "log", "hotfix", "--oneline"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "login" in result.stdout.lower() or "fix" in result.stdout.lower()


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "01_cherry_pick"
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
    assert result.stdout.strip() == "main"


# --- verify.sh: before goal is met ---


def test_verify_fails_before_cherry_pick(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_cherry_pick(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "cherry" in combined.lower() or "login" in combined.lower()


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_cherry_pick(work_dir):
    commit_hash = (work_dir / "cherry_pick_this.txt").read_text().strip()
    subprocess.run(
        ["git", "cherry-pick", commit_hash],
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
    commit_hash = (work_dir / "cherry_pick_this.txt").read_text().strip()
    subprocess.run(
        ["git", "cherry-pick", commit_hash],
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
        "cherry" in combined.lower()
        or "excellent" in combined.lower()
        or "well done" in combined.lower()
    )


def test_verify_login_fix_present_after_cherry_pick(work_dir):
    commit_hash = (work_dir / "cherry_pick_this.txt").read_text().strip()
    subprocess.run(
        ["git", "cherry-pick", commit_hash],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    assert (work_dir / "login_fix.py").exists()


def test_verify_cleanup_absent_after_cherry_pick(work_dir):
    """Cleanup commit should NOT be on main after cherry-picking just the fix."""
    commit_hash = (work_dir / "cherry_pick_this.txt").read_text().strip()
    subprocess.run(
        ["git", "cherry-pick", commit_hash],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    assert not (work_dir / "cleanup.txt").exists()
