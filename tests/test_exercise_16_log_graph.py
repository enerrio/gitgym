"""End-to-end tests for exercises/05_history/02_log_graph."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "05_history" / "02_log_graph"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "02_log_graph"
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
    assert ex.name == "log_graph"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "History"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert (
        "graph" in ex.title.lower()
        or "history" in ex.title.lower()
        or "branch" in ex.title.lower()
    )


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


def test_setup_branches_have_diverged(work_dir):
    """Both main and feature should have commits the other doesn't."""
    main_only = subprocess.run(
        ["git", "log", "--oneline", "feature..main"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout.strip()
    feature_only = subprocess.run(
        ["git", "log", "--oneline", "main..feature"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout.strip()
    assert main_only != ""
    assert feature_only != ""


def test_setup_total_commit_count(work_dir):
    result = subprocess.run(
        ["git", "rev-list", "--all", "--count"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert int(result.stdout.strip()) == 4


def test_setup_no_answer_file(work_dir):
    assert not (work_dir / "answer.txt").exists()


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "02_log_graph"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "rev-list", "--all", "--count"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert int(result.stdout.strip()) == 4


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


def test_verify_fails_with_wrong_count(work_dir):
    (work_dir / "answer.txt").write_text("99\n")
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


def test_verify_succeeds_with_correct_count(work_dir):
    count = subprocess.run(
        ["git", "rev-list", "--all", "--count"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout.strip()
    (work_dir / "answer.txt").write_text(count + "\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    count = subprocess.run(
        ["git", "rev-list", "--all", "--count"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout.strip()
    (work_dir / "answer.txt").write_text(count + "\n")
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
