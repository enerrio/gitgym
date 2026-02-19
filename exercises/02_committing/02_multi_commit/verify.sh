#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check there are at least 3 commits
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo 0)
if [ "$COMMIT_COUNT" -lt 3 ]; then
	echo "Found $COMMIT_COUNT commit(s), but at least 3 are required."
	echo "Stage and commit each file (README.md, main.py, utils.py) separately."
	exit 1
fi

# Check all commit messages are non-empty
EMPTY_MSG_COUNT=$(git log --format="%s" | grep -c "^$" || true)
if [ "$EMPTY_MSG_COUNT" -gt 0 ]; then
	echo "One or more commits have an empty message."
	echo "Use 'git commit -m \"your message\"' to add a meaningful message."
	exit 1
fi

echo "Well done! You created $COMMIT_COUNT commits with meaningful messages."
exit 0
