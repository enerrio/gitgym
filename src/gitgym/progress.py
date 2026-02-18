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
