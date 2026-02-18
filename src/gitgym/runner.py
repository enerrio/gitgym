import os
import subprocess
from pathlib import Path

from gitgym.config import EXERCISES_DIR, WORKSPACE_DIR
from gitgym.exercise import Exercise


def _workspace_path(exercise: Exercise) -> Path:
    """Return the workspace directory for the given exercise."""
    relative = exercise.path.relative_to(EXERCISES_DIR)
    return WORKSPACE_DIR / relative


def run_setup(exercise: Exercise) -> bool:
    """Run setup.sh for the exercise, passing the workspace path as $1.

    Returns True on success, False on failure.
    Prints a clear error message if the script is missing, non-executable, or exits non-zero.
    """
    setup_script = exercise.path / "setup.sh"

    if not setup_script.exists():
        print(
            f"Error: setup.sh not found for exercise '{exercise.name}' at {setup_script}"
        )
        return False

    if not os.access(setup_script, os.X_OK):
        print(f"Error: setup.sh for exercise '{exercise.name}' is not executable.")
        print(f"Fix with: chmod +x {setup_script}")
        return False

    workspace_exercise_path = _workspace_path(exercise)
    workspace_exercise_path.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [str(setup_script), str(workspace_exercise_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(
            f"Error: setup.sh for exercise '{exercise.name}' failed (exit code {result.returncode})."
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return False

    return True
