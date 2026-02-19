#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check that the current branch is "bugfix"
CURRENT=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ "$CURRENT" != "bugfix" ]; then
	echo "You are currently on branch '$CURRENT', not 'bugfix'."
	echo "Switch to it with: git switch bugfix"
	exit 1
fi

echo "Well done! You switched to the 'bugfix' branch."
exit 0
