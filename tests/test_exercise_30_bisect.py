"""End-to-end tests for exercises/09_advanced/02_bisect."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "09_advanced" / "02_bisect"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "02_bisect"
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
    assert ex.name == "bisect"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Advanced"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "bisect" in ex.title.lower()


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


def test_setup_has_seven_commits(work_dir):
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert int(result.stdout.strip()) == 7


def test_setup_creates_calc_sh(work_dir):
    assert (work_dir / "calc.sh").exists()


def test_setup_creates_test_sh(work_dir):
    assert (work_dir / "test.sh").exists()


def test_setup_test_sh_is_executable(work_dir):
    assert (work_dir / "test.sh").stat().st_mode & 0o111


def test_setup_head_calc_returns_wrong_result(work_dir):
    """HEAD has the bug - calc.sh returns 41, not 42."""
    result = subprocess.run(
        ["./calc.sh"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    assert result.stdout.strip() == "41"


def test_setup_test_sh_fails_on_head(work_dir):
    """test.sh should exit non-zero on HEAD (which has the bug)."""
    result = subprocess.run(
        ["./test.sh"],
        capture_output=True,
        text=True,
        cwd=work_dir,
    )
    assert result.returncode != 0


def test_setup_has_bug_commit_in_history(work_dir):
    result = subprocess.run(
        ["git", "log", "--format=%s"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "Optimize calculation algorithm" in result.stdout


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "02_bisect"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert int(result.stdout.strip()) == 7


# --- verify.sh: before goal is met ---


def test_verify_fails_without_found_commit_txt(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_found_commit(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "found_commit" in combined.lower() or "bisect" in combined.lower()


def test_verify_fails_with_invalid_hash(work_dir):
    (work_dir / "found_commit.txt").write_text("notahash\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_fails_with_wrong_commit(work_dir):
    # Use the first commit (which is good, not the bad one)
    first_commit = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout.strip()
    (work_dir / "found_commit.txt").write_text(first_commit + "\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


# --- verify.sh: after goal is met ---


def _get_bad_commit(work_dir):
    """Return the full hash of the expected bad commit."""
    result = subprocess.run(
        ["git", "log", "--format=%H", "--grep=Optimize calculation algorithm"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    return result.stdout.strip()


def test_verify_succeeds_with_correct_full_hash(work_dir):
    bad = _get_bad_commit(work_dir)
    (work_dir / "found_commit.txt").write_text(bad + "\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_succeeds_with_abbreviated_hash(work_dir):
    bad = _get_bad_commit(work_dir)
    abbrev = subprocess.run(
        ["git", "rev-parse", "--short", bad],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout.strip()
    (work_dir / "found_commit.txt").write_text(abbrev + "\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    bad = _get_bad_commit(work_dir)
    (work_dir / "found_commit.txt").write_text(bad + "\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert (
        "correct" in combined.lower()
        or "bisect" in combined.lower()
        or "found" in combined.lower()
    )


def test_bisect_run_finds_correct_commit(work_dir):
    """Full end-to-end: git bisect run should identify the bad commit."""
    subprocess.run(
        ["git", "bisect", "start"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "bisect", "bad", "HEAD"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "bisect", "good", "HEAD~6"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    run_result = subprocess.run(
        ["git", "bisect", "run", "./test.sh"],
        cwd=work_dir,
        capture_output=True,
        text=True,
    )
    assert "Optimize calculation algorithm" in run_result.stdout

    subprocess.run(
        ["git", "bisect", "reset"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
