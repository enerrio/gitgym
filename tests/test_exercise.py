import textwrap
from pathlib import Path
from unittest import mock

import pytest

from gitgym.exercise import Exercise, load_exercise, load_all_exercises


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


def _make_exercise_toml(directory: Path, name: str, topic: str, title: str) -> None:
    toml = directory / "exercise.toml"
    toml.write_text(
        textwrap.dedent(f"""\
            [exercise]
            name = "{name}"
            topic = "{topic}"
            title = "{title}"
            description = "Description for {name}."

            [goal]
            summary = "Goal for {name}."

            [[hints]]
            text = "Hint for {name}."
        """)
    )


def test_load_all_exercises_returns_sorted_list(tmp_path):
    # Create a fake exercises tree: two topics, two exercises each
    (tmp_path / "02_committing" / "01_amend").mkdir(parents=True)
    (tmp_path / "02_committing" / "02_multi_commit").mkdir(parents=True)
    (tmp_path / "01_basics" / "02_staging").mkdir(parents=True)
    (tmp_path / "01_basics" / "01_init").mkdir(parents=True)

    _make_exercise_toml(tmp_path / "01_basics" / "01_init", "init", "Basics", "Init")
    _make_exercise_toml(
        tmp_path / "01_basics" / "02_staging", "staging", "Basics", "Staging"
    )
    _make_exercise_toml(
        tmp_path / "02_committing" / "01_amend", "amend", "Committing", "Amend"
    )
    _make_exercise_toml(
        tmp_path / "02_committing" / "02_multi_commit",
        "multi_commit",
        "Committing",
        "Multi Commit",
    )

    with mock.patch("gitgym.exercise.EXERCISES_DIR", tmp_path):
        exercises = load_all_exercises()

    assert len(exercises) == 4
    assert [ex.name for ex in exercises] == ["init", "staging", "amend", "multi_commit"]


def test_load_all_exercises_returns_exercise_instances(tmp_path):
    (tmp_path / "01_basics" / "01_init").mkdir(parents=True)
    _make_exercise_toml(tmp_path / "01_basics" / "01_init", "init", "Basics", "Init")

    with mock.patch("gitgym.exercise.EXERCISES_DIR", tmp_path):
        exercises = load_all_exercises()

    assert len(exercises) == 1
    assert isinstance(exercises[0], Exercise)


def test_load_all_exercises_empty_dir(tmp_path):
    with mock.patch("gitgym.exercise.EXERCISES_DIR", tmp_path):
        exercises = load_all_exercises()

    assert exercises == []
