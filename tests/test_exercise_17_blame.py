"""End-to-end tests for exercises/05_history/03_blame."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "05_history" / "03_blame"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "03_blame"
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
    assert ex.name == "blame"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "History"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert (
        "blame" in ex.title.lower()
        or "author" in ex.title.lower()
        or "changed" in ex.title.lower()
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


def test_setup_creates_poem_txt(work_dir):
    assert (work_dir / "poem.txt").exists()


def test_setup_poem_has_four_lines(work_dir):
    lines = (work_dir / "poem.txt").read_text().splitlines()
    assert len(lines) == 4


def test_setup_blame_shows_multiple_authors(work_dir):
    result = subprocess.run(
        ["git", "blame", "poem.txt"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    # Should show at least two distinct author names
    blame_output = result.stdout
    assert "Alice" in blame_output
    assert "Charlie" in blame_output


def test_setup_line3_author_is_charlie(work_dir):
    result = subprocess.run(
        ["git", "blame", "poem.txt"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    line3 = result.stdout.splitlines()[2]
    assert "Charlie" in line3


def test_setup_no_answer_file(work_dir):
    assert not (work_dir / "answer.txt").exists()


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "03_blame"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "blame", "poem.txt"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert "Charlie" in result.stdout


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


def test_verify_fails_with_wrong_name(work_dir):
    (work_dir / "answer.txt").write_text("Alice\n")
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


def test_verify_succeeds_with_correct_author(work_dir):
    (work_dir / "answer.txt").write_text("Charlie\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    (work_dir / "answer.txt").write_text("Charlie\n")
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


def test_verify_success_mentions_author_name(work_dir):
    (work_dir / "answer.txt").write_text("Charlie\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "Charlie" in combined
