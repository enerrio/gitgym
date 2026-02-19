#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check notes.txt exists
if [ ! -f "notes.txt" ]; then
	echo "notes.txt is missing."
	echo "Reset the exercise with: gitgym reset"
	exit 1
fi

# Check the stash list is empty (user popped the stash)
STASH_COUNT=$(git stash list | wc -l | tr -d ' ')
if [ "$STASH_COUNT" -ne 0 ]; then
	echo "The stash still has $STASH_COUNT entry/entries."
	echo "Use 'git stash pop' to apply the stash and remove it from the list."
	exit 1
fi

# Check that notes.txt has the stashed content (not just the committed version)
if ! grep -q "Action items" notes.txt; then
	echo "notes.txt does not contain the stashed content."
	echo "Use 'git stash pop' to recover your work from the stash."
	exit 1
fi

echo "Great work! You successfully recovered your uncommitted changes from the stash."
echo "'git stash pop' is the most common way to re-apply stashed changes."
exit 0
