import json
from datetime import datetime, timezone

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


def mark_in_progress(exercise_key: str) -> None:
    """Set an exercise status to 'in_progress' with a started_at timestamp."""
    data = load_progress()
    existing = data["exercises"].get(exercise_key, {})
    data["exercises"][exercise_key] = {
        **existing,
        "status": "in_progress",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    save_progress(data)


def mark_completed(exercise_key: str) -> None:
    """Set an exercise status to 'completed' with a completed_at timestamp."""
    data = load_progress()
    existing = data["exercises"].get(exercise_key, {})
    data["exercises"][exercise_key] = {
        **existing,
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    save_progress(data)


def increment_hints_used(exercise_key: str) -> None:
    """Increment the hints_used counter for an exercise."""
    data = load_progress()
    existing = data["exercises"].get(exercise_key, {})
    current_hints = existing.get("hints_used", 0)
    data["exercises"][exercise_key] = {
        **existing,
        "hints_used": current_hints + 1,
    }
    save_progress(data)


def reset_exercise_progress(exercise_key: str) -> None:
    """Remove the exercise entry from progress (sets it back to not_started)."""
    data = load_progress()
    data["exercises"].pop(exercise_key, None)
    save_progress(data)
