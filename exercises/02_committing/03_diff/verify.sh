#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check there are at least 2 commits (original + new)
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo 0)
if [ "$COMMIT_COUNT" -lt 2 ]; then
	echo "Expected at least 2 commits but found $COMMIT_COUNT."
	echo "Stage and commit the changes to app.py."
	exit 1
fi

# Check app.py has no unstaged changes
if ! git diff --quiet app.py 2>/dev/null; then
	echo "app.py still has unstaged changes."
	echo "Stage them with 'git add app.py' then commit."
	exit 1
fi

# Check app.py has no staged-but-uncommitted changes
if ! git diff --staged --quiet app.py 2>/dev/null; then
	echo "app.py is staged but not yet committed."
	echo "Run 'git commit -m \"your message\"' to commit."
	exit 1
fi

# Check the committed app.py contains the updated f-string greeting
CONTENT=$(git show HEAD:app.py 2>/dev/null || echo "")
if ! echo "$CONTENT" | grep -q '{name}'; then
	echo "The committed app.py doesn't contain the updated greeting."
	echo "Make sure you committed the modified version of app.py."
	exit 1
fi

echo "Great work! You inspected the diff and committed the changes to app.py."
exit 0
