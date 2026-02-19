#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check that a branch named "feature" exists
if ! git branch --list "feature" | grep -q "feature"; then
	echo "No branch named 'feature' found."
	echo "Create it with: git switch -c feature"
	exit 1
fi

# Check that the current branch is "feature"
CURRENT=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ "$CURRENT" != "feature" ]; then
	echo "The 'feature' branch exists but you are currently on '$CURRENT'."
	echo "Switch to it with: git switch feature"
	exit 1
fi

echo "Excellent! You created the 'feature' branch and switched to it."
exit 0
