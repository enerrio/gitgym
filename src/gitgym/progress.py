import json

from gitgym.config import PROGRESS_FILE


def load_progress() -> dict:
    """Load progress from ~/.gitgym/progress.json. Returns empty progress dict if file doesn't exist."""
    if not PROGRESS_FILE.exists():
        return {"version": 1, "exercises": {}}
    with open(PROGRESS_FILE) as f:
        return json.load(f)


def save_progress(data: dict) -> None:
    """Save progress dict to ~/.gitgym/progress.json."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_exercise_status(exercise_key: str) -> str:
    """Return the status of an exercise: 'not_started', 'in_progress', or 'completed'."""
    data = load_progress()
    exercise = data.get("exercises", {}).get(exercise_key)
    if exercise is None:
        return "not_started"
    return exercise.get("status", "not_started")
