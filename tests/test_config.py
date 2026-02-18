from pathlib import Path

from gitgym.config import EXERCISES_DIR, GITGYM_HOME, PROGRESS_FILE, WORKSPACE_DIR


def test_gitgym_home_under_user_home():
    assert GITGYM_HOME == Path.home() / ".gitgym"


def test_workspace_dir():
    assert WORKSPACE_DIR == Path.home() / ".gitgym" / "exercises"


def test_progress_file():
    assert PROGRESS_FILE == Path.home() / ".gitgym" / "progress.json"


def test_exercises_dir_is_absolute():
    assert EXERCISES_DIR.is_absolute()


def test_exercises_dir_points_to_exercises_folder():
    assert EXERCISES_DIR.name == "exercises"


def test_exercises_dir_exists():
    # The exercises/ directory may not exist yet during development,
    # but the path should resolve to the project root's exercises/ folder.
    # Check that it is relative to the package source.
    import gitgym.config as config_module

    package_dir = Path(config_module.__file__).parent
    expected = package_dir.parent.parent / "exercises"
    assert EXERCISES_DIR == expected
