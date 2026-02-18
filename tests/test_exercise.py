import textwrap
from pathlib import Path

import pytest

from gitgym.exercise import Exercise, load_exercise


@pytest.fixture
def exercise_dir(tmp_path):
    toml = tmp_path / "exercise.toml"
    toml.write_text(
        textwrap.dedent("""\
            [exercise]
            name = "init"
            topic = "Basics"
            title = "Initialize a Repository"
            description = "Every git journey starts with `git init`."

            [goal]
            summary = "The directory should be a valid git repository."

            [[hints]]
            text = "Look at the `git init` command."

            [[hints]]
            text = "Run `git init` inside the exercise directory."
        """)
    )
    return tmp_path


def test_exercise_dataclass_fields():
    ex = Exercise(
        name="init",
        topic="Basics",
        title="Initialize a Repository",
        description="Every git journey starts with `git init`.",
        goal_summary="The directory should be a valid git repository.",
        hints=["Look at `git init`.", "Run `git init` inside the directory."],
        path=Path("/tmp/exercises/01_basics/01_init"),
    )
    assert ex.name == "init"
    assert ex.topic == "Basics"
    assert ex.title == "Initialize a Repository"
    assert ex.description == "Every git journey starts with `git init`."
    assert ex.goal_summary == "The directory should be a valid git repository."
    assert ex.hints == ["Look at `git init`.", "Run `git init` inside the directory."]
    assert ex.path == Path("/tmp/exercises/01_basics/01_init")


def test_exercise_hints_is_list():
    ex = Exercise(
        name="staging",
        topic="Basics",
        title="Stage Files",
        description="Stage files with git add.",
        goal_summary="All files should be staged.",
        hints=[],
        path=Path("/tmp/exercises/01_basics/02_staging"),
    )
    assert isinstance(ex.hints, list)
    assert ex.hints == []


def test_exercise_path_is_path():
    ex = Exercise(
        name="init",
        topic="Basics",
        title="Initialize a Repository",
        description="desc",
        goal_summary="goal",
        hints=["hint"],
        path=Path("/some/path"),
    )
    assert isinstance(ex.path, Path)


def test_load_exercise_parses_all_fields(exercise_dir):
    ex = load_exercise(exercise_dir)
    assert ex.name == "init"
    assert ex.topic == "Basics"
    assert ex.title == "Initialize a Repository"
    assert ex.description == "Every git journey starts with `git init`."
    assert ex.goal_summary == "The directory should be a valid git repository."
    assert ex.hints == [
        "Look at the `git init` command.",
        "Run `git init` inside the exercise directory.",
    ]
    assert ex.path == exercise_dir


def test_load_exercise_path_is_path_object(exercise_dir):
    ex = load_exercise(exercise_dir)
    assert isinstance(ex.path, Path)


def test_load_exercise_hints_order_preserved(exercise_dir):
    ex = load_exercise(exercise_dir)
    assert ex.hints[0] == "Look at the `git init` command."
    assert ex.hints[1] == "Run `git init` inside the exercise directory."


def test_load_exercise_no_hints(tmp_path):
    toml = tmp_path / "exercise.toml"
    toml.write_text(
        textwrap.dedent("""\
            [exercise]
            name = "staging"
            topic = "Basics"
            title = "Stage Files"
            description = "Stage files with git add."

            [goal]
            summary = "All files should be staged."
        """)
    )
    ex = load_exercise(tmp_path)
    assert ex.hints == []


def test_load_exercise_missing_toml_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_exercise(tmp_path)
