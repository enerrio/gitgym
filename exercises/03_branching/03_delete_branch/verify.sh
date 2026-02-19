#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check that the current branch is still main
CURRENT=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ "$CURRENT" != "main" ]; then
	echo "You are on branch '$CURRENT'. Make sure you stay on 'main' while deleting the old-feature branch."
	exit 1
fi

# Check that old-feature branch no longer exists
if git branch --list "old-feature" | grep -q "old-feature"; then
	echo "The 'old-feature' branch still exists."
	echo "Delete it with: git branch -d old-feature"
	exit 1
fi

echo "Great job! You deleted the merged 'old-feature' branch."
exit 0
