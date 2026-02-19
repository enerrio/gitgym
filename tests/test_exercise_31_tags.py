"""End-to-end tests for exercises/09_advanced/03_tags."""

import subprocess

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "09_advanced" / "03_tags"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "03_tags"
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
    assert ex.name == "tags"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Advanced"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "tag" in ex.title.lower()


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


def test_setup_no_tags_initially(work_dir):
    result = subprocess.run(
        ["git", "tag", "-l"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == ""


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "03_tags"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "tag", "-l"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert result.stdout.strip() == ""


# --- verify.sh: before goal is met ---


def test_verify_fails_without_tags(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_tag(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "tag" in combined.lower() or "v1.0" in combined


def test_verify_fails_with_only_lightweight_tag(work_dir):
    subprocess.run(
        ["git", "tag", "v1.0"],
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


def test_verify_fails_with_only_annotated_tag(work_dir):
    subprocess.run(
        ["git", "tag", "-a", "v1.0-release", "-m", "Release version 1.0"],
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


def test_verify_fails_wrong_annotated_message(work_dir):
    subprocess.run(
        ["git", "tag", "v1.0"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "tag", "-a", "v1.0-release", "-m", "wrong message"],
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


def test_verify_succeeds_with_both_tags(work_dir):
    subprocess.run(
        ["git", "tag", "v1.0"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "tag", "-a", "v1.0-release", "-m", "Release version 1.0"],
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
        ["git", "tag", "v1.0"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "tag", "-a", "v1.0-release", "-m", "Release version 1.0"],
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
        "well done" in combined.lower()
        or "excellent" in combined.lower()
        or "tag" in combined.lower()
    )


def test_v1_0_is_lightweight_tag(work_dir):
    subprocess.run(
        ["git", "tag", "v1.0"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        ["git", "cat-file", "-t", "v1.0"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "commit"


def test_v1_0_release_is_annotated_tag(work_dir):
    subprocess.run(
        ["git", "tag", "-a", "v1.0-release", "-m", "Release version 1.0"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        ["git", "cat-file", "-t", "v1.0-release"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "tag"
