"""End-to-end tests for exercises/07_rebase/02_interactive_rebase."""

import os
import subprocess
import textwrap

import pytest

from gitgym.config import EXERCISES_DIR
from gitgym.exercise import load_exercise

EXERCISE_DIR = EXERCISES_DIR / "07_rebase" / "02_interactive_rebase"


@pytest.fixture
def work_dir(tmp_path):
    """Run setup.sh and return the exercise workspace directory."""
    d = tmp_path / "02_interactive_rebase"
    d.mkdir()
    subprocess.run(
        [str(EXERCISE_DIR / "setup.sh"), str(d)],
        capture_output=True,
        check=True,
    )
    return d


def _squash_wip_commits(work_dir, tmp_path):
    """Helper: squash all WIP commits into one using GIT_SEQUENCE_EDITOR."""
    squash_editor = tmp_path / "squash_editor.sh"
    squash_editor.write_text(
        textwrap.dedent("""\
            #!/usr/bin/env bash
            sed -i.bak '2,$s/^pick/squash/' "$1"
        """)
    )
    squash_editor.chmod(0o755)

    msg_editor = tmp_path / "msg_editor.sh"
    msg_editor.write_text(
        textwrap.dedent("""\
            #!/usr/bin/env bash
            echo "Implement feature" > "$1"
        """)
    )
    msg_editor.chmod(0o755)

    subprocess.run(
        ["git", "rebase", "-i", "main"],
        cwd=work_dir,
        capture_output=True,
        check=True,
        env={
            **os.environ,
            "GIT_SEQUENCE_EDITOR": str(squash_editor),
            "GIT_EDITOR": str(msg_editor),
        },
    )


# --- exercise.toml parsing ---


def test_exercise_toml_loads():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.name == "interactive_rebase"


def test_exercise_topic():
    ex = load_exercise(EXERCISE_DIR)
    assert ex.topic == "Rebase"


def test_exercise_title():
    ex = load_exercise(EXERCISE_DIR)
    assert "rebase" in ex.title.lower() or "squash" in ex.title.lower()


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


def test_setup_starts_on_feature(work_dir):
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    assert result.stdout.strip() == "feature"


def test_setup_has_three_wip_commits(work_dir):
    result = subprocess.run(
        ["git", "log", "main..feature", "--oneline"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    lines = result.stdout.strip().splitlines()
    assert len(lines) == 3


def test_setup_wip_commits_have_wip_in_message(work_dir):
    result = subprocess.run(
        ["git", "log", "main..feature", "--format=%s"],
        capture_output=True,
        text=True,
        cwd=work_dir,
        check=True,
    )
    messages = result.stdout.strip().splitlines()
    assert all("WIP" in msg for msg in messages)


def test_setup_is_idempotent(tmp_path):
    d = tmp_path / "02_interactive_rebase"
    d.mkdir()
    script = str(EXERCISE_DIR / "setup.sh")
    arg = str(d)
    subprocess.run([script, arg], capture_output=True, check=True)
    subprocess.run([script, arg], capture_output=True, check=True)
    assert (d / ".git").is_dir()
    result = subprocess.run(
        ["git", "log", "main..feature", "--oneline"],
        capture_output=True,
        text=True,
        cwd=d,
        check=True,
    )
    assert len(result.stdout.strip().splitlines()) == 3


# --- verify.sh: before goal is met ---


def test_verify_fails_before_squash(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_verify_failure_mentions_squash_or_commit_count(work_dir):
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert "squash" in combined.lower() or "commit" in combined.lower()


# --- verify.sh: after goal is met ---


def test_verify_succeeds_after_squash(work_dir, tmp_path):
    _squash_wip_commits(work_dir, tmp_path)
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_verify_success_output_is_congratulatory(work_dir, tmp_path):
    _squash_wip_commits(work_dir, tmp_path)
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    assert (
        "well done" in combined.lower()
        or "great" in combined.lower()
        or "squash" in combined.lower()
        or "excellent" in combined.lower()
    )


def test_verify_fails_if_commit_message_still_has_wip(work_dir):
    """verify should fail if the squashed commit message still says WIP."""
    # Squash but keep a WIP message
    import textwrap

    squash_editor = work_dir / "squash_editor.sh"
    squash_editor.write_text(
        textwrap.dedent("""\
            #!/usr/bin/env bash
            sed -i.bak '2,$s/^pick/squash/' "$1"
        """)
    )
    squash_editor.chmod(0o755)

    msg_editor = work_dir / "msg_editor.sh"
    msg_editor.write_text(
        textwrap.dedent("""\
            #!/usr/bin/env bash
            echo "WIP: all combined" > "$1"
        """)
    )
    msg_editor.chmod(0o755)

    subprocess.run(
        ["git", "rebase", "-i", "main"],
        cwd=work_dir,
        capture_output=True,
        env={
            **os.environ,
            "GIT_SEQUENCE_EDITOR": str(squash_editor),
            "GIT_EDITOR": str(msg_editor),
        },
    )
    result = subprocess.run(
        [str(EXERCISE_DIR / "verify.sh"), str(work_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
