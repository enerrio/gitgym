"""End-to-end tests for exercises/05_history/04_show."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "05_history" / "04_show"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "04_show"
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
    assert ex.name == "show"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "History"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert (
        "show" in ex.title.lower()
        or "inspect" in ex.title.lower()
        or "commit" in ex.title.lower()
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


def test_setup_has_add_launch_code_commit(work_dir):
    result = subprocess.run(
        ["git", "log", "--oneline"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "Add launch code" in result.stdout


def test_setup_launch_txt_not_in_working_tree(work_dir):
    """launch.txt should have been removed in the final commit."""
    assert not (work_dir / "launch.txt").exists()


def test_setup_launch_txt_accessible_in_history(work_dir):
    """launch.txt should still be accessible via git show."""
    commit_hash = subprocess.run(
        ["git", "log", "--format=%h %s"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    for line in commit_hash.stdout.splitlines():
        if "Add launch code" in line:
            short = line.split()[0]
            break
    result = subprocess.run(
        ["git", "show", f"{short}:launch.txt"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert "LAUNCH_CODE" in result.stdout


def test_setup_no_answer_file(work_dir):
    assert not (work_dir / "answer.txt").exists()


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "04_show"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    assert not (d / "launch.txt").exists()
    result = subprocess.run(
        ["git", "log", "--oneline"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert "Add launch code" in result.stdout


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


def test_verify_fails_with_wrong_content(work_dir):
    (work_dir / "answer.txt").write_text("WRONG_CODE=123\n")
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


def _get_launch_first_line(work_dir):
    """Helper: retrieve the first line of launch.txt from the 'Add launch code' commit."""
    log_result = subprocess.run(
        ["git", "log", "--format=%h %s"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    for line in log_result.stdout.splitlines():
        if "Add launch code" in line:
            short = line.split()[0]
            break
    content = subprocess.run(
        ["git", "show", f"{short}:launch.txt"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout
    return content.splitlines()[0]


def test_verify_succeeds_with_correct_first_line(work_dir):
    first_line = _get_launch_first_line(work_dir)
    (work_dir / "answer.txt").write_text(first_line + "\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir):
    first_line = _get_launch_first_line(work_dir)
    (work_dir / "answer.txt").write_text(first_line + "\n")
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


def test_verify_fails_with_second_line_instead(work_dir):
    """Verify should fail if the user wrote the second line instead of the first."""
    log_result = subprocess.run(
        ["git", "log", "--format=%h %s"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    for line in log_result.stdout.splitlines():
        if "Add launch code" in line:
            short = line.split()[0]
            break
    content = subprocess.run(
        ["git", "show", f"{short}:launch.txt"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    ).stdout.splitlines()
    second_line = content[1] if len(content) > 1 else "wrong"
    (work_dir / "answer.txt").write_text(second_line + "\n")
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
