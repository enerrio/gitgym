import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Exercise:
    name: str
    topic: str
    title: str
    description: str
    goal_summary: str
    hints: list[str]
    path: Path


def load_exercise(exercise_dir: Path) -> "Exercise":
    toml_path = exercise_dir / "exercise.toml"
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
    ex = data["exercise"]
    hints = [h["text"] for h in data.get("hints", [])]
    return Exercise(
        name=ex["name"],
        topic=ex["topic"],
        title=ex["title"],
        description=ex["description"],
        goal_summary=data["goal"]["summary"],
        hints=hints,
        path=exercise_dir,
    )
