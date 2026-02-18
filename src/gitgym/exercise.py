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
