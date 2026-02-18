from pathlib import Path

from gitgym.exercise import Exercise


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
