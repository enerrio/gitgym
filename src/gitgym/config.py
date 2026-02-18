from pathlib import Path

# User's home directory for workspace and progress file
GITGYM_HOME = Path.home() / ".gitgym"
WORKSPACE_DIR = GITGYM_HOME / "exercises"
PROGRESS_FILE = GITGYM_HOME / "progress.json"

# Package-relative exercises directory (shipped with the package)
EXERCISES_DIR = Path(__file__).parent / "exercises"
