#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check config.txt exists
if [ ! -f "config.txt" ]; then
	echo "config.txt is missing."
	echo "Reset the exercise with: gitgym reset"
	exit 1
fi

# Check there are no unstaged changes to config.txt
if ! git diff --quiet -- config.txt; then
	echo "config.txt still has uncommitted modifications."
	echo "Use 'git restore config.txt' to discard working directory changes."
	exit 1
fi

# Check the file content matches the committed version
COMMITTED=$(git show HEAD:config.txt)
CURRENT=$(cat config.txt)

if [ "$COMMITTED" != "$CURRENT" ]; then
	echo "config.txt does not match the last committed version."
	echo "Use 'git restore config.txt' to restore it."
	exit 1
fi

echo "Well done! You restored config.txt to its last committed state."
echo "'git restore' is a safe way to discard accidental changes before they are staged."
exit 0
