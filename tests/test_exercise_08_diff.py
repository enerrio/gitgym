"""End-to-end tests for exercises/02_committing/03_diff."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "02_committing" / "03_diff"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "03_diff"
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
    assert ex.name == "diff"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Committing"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "diff" in ex.title.lower()


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


def test_setup_creates_app_py(work_dir):
    assert (work_dir / "app.py").exists()


def test_setup_has_one_commit(work_dir):
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "1"


def test_setup_app_py_has_unstaged_changes(work_dir):
    """app.py should have unstaged modifications after setup."""
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "app.py" in result.stdout


def test_setup_app_py_contains_f_string(work_dir):
    """The modified (unstaged) app.py should use an f-string."""
    content = (work_dir / "app.py").read_text()
    assert "{name}" in content


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "03_diff"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    assert (d / "app.py").exists()
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert result.stdout.strip() == "1"


# --- verify.sh: before goal is met ---


def test_verify_fails_with_unstaged_changes(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_app_py(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "app.py" in combined


def test_verify_fails_with_staged_but_uncommitted(work_dir):
    subprocess.run(
        ["git", "add", "app.py"],
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


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_staging_and_committing(work_dir):
    subprocess.run(
        ["git", "add", "app.py"], check=True, cwd=work_dir, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Use f-string in greet"],
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
        ["git", "add", "app.py"], check=True, cwd=work_dir, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Update greet to use f-string"],
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


def test_verify_committed_app_py_has_f_string(work_dir):
    subprocess.run(
        ["git", "add", "app.py"], check=True, cwd=work_dir, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Update greet"],
        check=True,
        cwd=work_dir,
        capture_output=True,
    )
    # Verify the committed content contains the f-string
    result = subprocess.run(
        ["git", "show", "HEAD:app.py"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "{name}" in result.stdout
