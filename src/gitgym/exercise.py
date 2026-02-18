import tomllib
from dataclasses import dataclass
from pathlib import Path

from gitgym.config import EXERCISES_DIR


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


def load_all_exercises() -> list[Exercise]:
    """Discover all NN_topic/NN_exercise/ directories under EXERCISES_DIR and return them sorted."""
    exercise_dirs = sorted(
        d
        for topic_dir in sorted(EXERCISES_DIR.iterdir())
        if topic_dir.is_dir()
        for d in sorted(topic_dir.iterdir())
        if d.is_dir()
    )
    return [load_exercise(d) for d in exercise_dirs]
