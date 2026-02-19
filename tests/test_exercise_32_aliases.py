"""End-to-end tests for exercises/09_advanced/04_aliases."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "09_advanced" / "04_aliases"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "04_aliases"
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
    assert ex.name == "aliases"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Advanced"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "alias" in ex.title.lower()


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


def test_setup_has_commits(work_dir):
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert int(result.stdout.strip()) >= 1


def test_setup_no_aliases_initially(work_dir):
    st = subprocess.run(
        ["git", "config", "alias.st"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    co = subprocess.run(
        ["git", "config", "alias.co"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    # Neither alias should be set after a fresh setup
    assert st.returncode != 0 or st.stdout.strip() == ""
    assert co.returncode != 0 or co.stdout.strip() == ""


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "04_aliases"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()


# --- verify.sh: before goal is met ---


def test_verify_fails_without_aliases(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_alias(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "alias" in combined.lower() or "st" in combined.lower()


def test_verify_fails_with_only_st_alias(work_dir):
    subprocess.run(
        ["git", "config", "alias.st", "status"],
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


def test_verify_fails_with_only_co_alias(work_dir):
    subprocess.run(
        ["git", "config", "alias.co", "checkout"],
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


def test_verify_fails_with_wrong_st_value(work_dir):
    subprocess.run(
        ["git", "config", "alias.st", "log"],  # wrong value
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "alias.co", "checkout"],
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


def test_verify_succeeds_with_both_aliases(work_dir):
    subprocess.run(
        ["git", "config", "alias.st", "status"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "alias.co", "checkout"],
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
        ["git", "config", "alias.st", "status"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "alias.co", "checkout"],
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
        or "alias" in combined.lower()
    )


def test_verify_aliases_work_after_configuration(work_dir):
    """Configured aliases should actually work (git st, git co)."""
    subprocess.run(
        ["git", "config", "alias.st", "status"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "alias.co", "checkout"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    # git st should work like git status
    st_result = subprocess.run(
        ["git", "st"],
        cwd=work_dir,
        capture_output=True,
        text=True,
    )
    assert st_result.returncode == 0
