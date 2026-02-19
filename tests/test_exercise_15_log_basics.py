"""End-to-end tests for exercises/05_history/01_log_basics."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "05_history" / "01_log_basics"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "01_log_basics"
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
    assert ex.name == "log_basics"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "History"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "log" in ex.title.lower() or "history" in ex.title.lower()


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


def test_setup_has_bug_fix_commit(work_dir):
    result = subprocess.run(
        ["git", "log", "--oneline"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "bug #42" in result.stdout


def test_setup_has_multiple_commits(work_dir):
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert int(result.stdout.strip()) >= 3


def test_setup_no_answer_file(work_dir):
    assert not (work_dir / "answer.txt").exists()


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "01_log_basics"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "log", "--oneline"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert "bug #42" in result.stdout


# --- verify.sh: before goal is met ---


def test_verify_fails_without_answer_file(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_answer_txt(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "answer.txt" in combined


def test_verify_fails_with_wrong_hash(work_dir):
    (work_dir / "answer.txt").write_text("0000000\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_fails_with_empty_answer(work_dir):
    (work_dir / "answer.txt").write_text("\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


# --- verify.sh: after goal is met ---


def _write_correct_hash(work_dir):
    """Helper: find the bug-fix commit hash and write it to answer.txt."""
    result = subprocess.run(
        ["git", "log", "--format=%h %s"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    for line in result.stdout.splitlines():
        if "bug #42" in line:
            short_hash = line.split()[0]
            (work_dir / "answer.txt").write_text(short_hash + "\n")
            return short_hash
    raise AssertionError("Bug-fix commit not found")


def test_verify_succeeds_with_correct_short_hash(work_dir):
    _write_correct_hash(work_dir)
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_succeeds_with_full_hash(work_dir):
    """verify.sh should also accept the full 40-char commit hash."""
    short = _write_correct_hash(work_dir)
    full = subprocess.run(
        ["git", "rev-parse", short],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout.strip()
    (work_dir / "answer.txt").write_text(full + "\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    _write_correct_hash(work_dir)
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert (
        "correct" in combined.lower()
        or "well done" in combined.lower()
        or "great" in combined.lower()
    )
