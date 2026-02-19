#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check there is at least one commit
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo 0)
if [ "$COMMIT_COUNT" -eq 0 ]; then
	echo "No commits found yet."
	echo "Use 'git commit -m \"your message\"' to create your first commit."
	exit 1
fi

# Check the commit message is non-empty
COMMIT_MSG=$(git log -1 --format="%s")
if [ -z "$COMMIT_MSG" ]; then
	echo "Your commit has an empty message."
	echo "A good commit message describes what changed and why."
	exit 1
fi

echo "Great job! You made your first commit: \"$COMMIT_MSG\""
exit 0
