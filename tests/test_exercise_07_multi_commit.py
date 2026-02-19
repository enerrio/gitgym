"""End-to-end tests for exercises/02_committing/02_multi_commit."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "02_committing" / "02_multi_commit"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "02_multi_commit"
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
    assert ex.name == "multi_commit"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Committing"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "commit" in ex.title.lower()


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


def test_setup_creates_main_py(work_dir):
    assert (work_dir / "main.py").exists()


def test_setup_creates_utils_py(work_dir):
    assert (work_dir / "utils.py").exists()


def test_setup_has_no_commits(work_dir):
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    assert result.returncode != 0 or result.stdout.strip() == "0"


def test_setup_files_are_untracked(work_dir):
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "??" in result.stdout


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "02_multi_commit"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    assert (d / "README.md").exists()
    assert (d / "main.py").exists()
    assert (d / "utils.py").exists()


# --- verify.sh: before goal is met ---


def test_verify_fails_with_no_commits(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_fails_with_only_one_commit(work_dir):
    subprocess.run(
        ["git", "add", "README.md"],
        check=True,
        cwd=work_dir,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add README"],
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


def test_verify_fails_with_two_commits(work_dir):
    for fname, msg in [("README.md", "Add README"), ("main.py", "Add main")]:
        subprocess.run(
            ["git", "add", fname], check=True, cwd=work_dir, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", msg], check=True, cwd=work_dir, capture_output=True
        )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_commits(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "commit" in combined.lower()


# --- verify.sh: after goal is met ---


def test_verify_succeeds_with_three_commits(work_dir):
    for fname, msg in [
        ("README.md", "Add README"),
        ("main.py", "Add main script"),
        ("utils.py", "Add utility functions"),
    ]:
        subprocess.run(
            ["git", "add", fname], check=True, cwd=work_dir, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", msg], check=True, cwd=work_dir, capture_output=True
        )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_succeeds_with_more_than_three_commits(work_dir):
    """More than 3 commits is also fine."""
    subprocess.run(
        ["git", "add", "README.md"], check=True, cwd=work_dir, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add README"],
        check=True,
        cwd=work_dir,
        capture_output=True,
    )
    subprocess.run(
        ["git", "add", "main.py"], check=True, cwd=work_dir, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add main"],
        check=True,
        cwd=work_dir,
        capture_output=True,
    )
    subprocess.run(
        ["git", "add", "utils.py"], check=True, cwd=work_dir, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add utils"],
        check=True,
        cwd=work_dir,
        capture_output=True,
    )
    # One more commit (amending a file)
    (work_dir / "README.md").write_text("# Updated\n")
    subprocess.run(
        ["git", "add", "README.md"], check=True, cwd=work_dir, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Update README"],
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
    for fname, msg in [
        ("README.md", "Add README"),
        ("main.py", "Add main script"),
        ("utils.py", "Add utility functions"),
    ]:
        subprocess.run(
            ["git", "add", fname], check=True, cwd=work_dir, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", msg], check=True, cwd=work_dir, capture_output=True
        )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert combined.strip()
