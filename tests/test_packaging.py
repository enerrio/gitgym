"""Tests that `uv build` produces a wheel and sdist that include exercises/."""

import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest

# Root of the project (one level up from tests/)
PROJECT_ROOT = Path(__file__).parent.parent

TOPIC_DIRS = [
    "01_basics",
    "02_committing",
    "03_branching",
    "04_merging",
    "05_history",
    "06_undoing",
    "07_rebase",
    "08_stashing",
    "09_advanced",
]

EXPECTED_EXERCISE_FILES_PER_EXERCISE = {"exercise.toml", "setup.sh", "verify.sh"}


@pytest.fixture(scope="module")
def dist_dir(tmp_path_factory):
    """Build the package once and return the output directory."""
    out = tmp_path_factory.mktemp("dist")
    result = subprocess.run(
        ["uv", "build", "--out-dir", str(out)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"uv build failed:\n{result.stderr}"
    return out


@pytest.fixture(scope="module")
def wheel_path(dist_dir):
    wheels = list(dist_dir.glob("*.whl"))
    assert wheels, "No wheel found in dist directory"
    return wheels[0]


@pytest.fixture(scope="module")
def sdist_path(dist_dir):
    sdists = list(dist_dir.glob("*.tar.gz"))
    assert sdists, "No sdist found in dist directory"
    return sdists[0]


# --- build produces both artifacts ---


def test_build_produces_wheel(dist_dir):
    assert list(dist_dir.glob("*.whl")), "uv build did not produce a wheel"


def test_build_produces_sdist(dist_dir):
    assert list(dist_dir.glob("*.tar.gz")), "uv build did not produce an sdist"


# --- wheel contains exercises/ ---


def test_wheel_contains_exercises_directory(wheel_path):
    with zipfile.ZipFile(wheel_path) as whl:
        names = whl.namelist()
    exercise_entries = [n for n in names if "exercises" in n]
    assert exercise_entries, "Wheel does not contain any exercises/ entries"


def test_wheel_contains_all_topic_dirs(wheel_path):
    with zipfile.ZipFile(wheel_path) as whl:
        names = whl.namelist()
    for topic in TOPIC_DIRS:
        assert any(topic in n for n in names), f"Wheel missing topic directory: {topic}"


def test_wheel_exercises_have_required_files(wheel_path):
    with zipfile.ZipFile(wheel_path) as whl:
        names = whl.namelist()

    # Collect all exercise directories from source
    exercises_root = PROJECT_ROOT / "exercises"
    for topic_dir in sorted(exercises_root.iterdir()):
        if not topic_dir.is_dir():
            continue
        for exercise_dir in sorted(topic_dir.iterdir()):
            if not exercise_dir.is_dir():
                continue
            rel = f"{topic_dir.name}/{exercise_dir.name}"
            for fname in EXPECTED_EXERCISE_FILES_PER_EXERCISE:
                expected = f"gitgym/exercises/{rel}/{fname}"
                assert expected in names, f"Wheel missing: {expected}"


def test_wheel_exercise_count_matches_source(wheel_path):
    with zipfile.ZipFile(wheel_path) as whl:
        names = whl.namelist()
    # Count exercise.toml files in the wheel
    wheel_tomls = [n for n in names if n.endswith("exercise.toml")]

    exercises_root = PROJECT_ROOT / "exercises"
    source_tomls = list(exercises_root.rglob("exercise.toml"))

    assert len(wheel_tomls) == len(source_tomls), (
        f"Wheel has {len(wheel_tomls)} exercise.toml files, "
        f"source has {len(source_tomls)}"
    )


# --- sdist contains exercises/ ---


def test_sdist_contains_exercises_directory(sdist_path):
    with tarfile.open(sdist_path) as tar:
        names = tar.getnames()
    exercise_entries = [n for n in names if "exercises" in n]
    assert exercise_entries, "Sdist does not contain any exercises/ entries"


def test_sdist_contains_all_topic_dirs(sdist_path):
    with tarfile.open(sdist_path) as tar:
        names = tar.getnames()
    for topic in TOPIC_DIRS:
        assert any(topic in n for n in names), f"Sdist missing topic directory: {topic}"


def test_sdist_exercises_have_required_files(sdist_path):
    with tarfile.open(sdist_path) as tar:
        names = tar.getnames()

    exercises_root = PROJECT_ROOT / "exercises"
    for topic_dir in sorted(exercises_root.iterdir()):
        if not topic_dir.is_dir():
            continue
        for exercise_dir in sorted(topic_dir.iterdir()):
            if not exercise_dir.is_dir():
                continue
            rel = f"{topic_dir.name}/{exercise_dir.name}"
            for fname in EXPECTED_EXERCISE_FILES_PER_EXERCISE:
                # sdist paths are like gitgym-0.1.0/exercises/...
                assert any(f"exercises/{rel}/{fname}" in n for n in names), (
                    f"Sdist missing: exercises/{rel}/{fname}"
                )


def test_sdist_exercise_count_matches_source(sdist_path):
    with tarfile.open(sdist_path) as tar:
        names = tar.getnames()
    sdist_tomls = [n for n in names if n.endswith("exercise.toml")]

    exercises_root = PROJECT_ROOT / "exercises"
    source_tomls = list(exercises_root.rglob("exercise.toml"))

    assert len(sdist_tomls) == len(source_tomls), (
        f"Sdist has {len(sdist_tomls)} exercise.toml files, "
        f"source has {len(source_tomls)}"
    )
