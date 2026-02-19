#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check there is at least one commit
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo 0)
if [ "$COMMIT_COUNT" -eq 0 ]; then
	echo "No commits found."
	exit 1
fi

# Check the commit message no longer has the typo
COMMIT_MSG=$(git log -1 --format="%s")
if echo "$COMMIT_MSG" | grep -q "worlt"; then
	echo "The commit message still contains the typo 'worlt': \"$COMMIT_MSG\""
	echo "Use 'git commit --amend -m \"Add hello world\"' to fix it."
	exit 1
fi

if [ -z "$COMMIT_MSG" ]; then
	echo "The commit message is empty. Add a meaningful message."
	exit 1
fi

echo "Excellent! You amended the commit message to: \"$COMMIT_MSG\""
exit 0
