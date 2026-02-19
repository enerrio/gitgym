#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check the messy commit is no longer the latest commit
LAST_MSG=$(git log -1 --format="%s")
if echo "$LAST_MSG" | grep -q "Add everything at once"; then
	echo "The 'Add everything at once' commit is still the latest commit."
	echo "Use 'git reset HEAD~1' to undo it."
	exit 1
fi

# Check nothing is staged (index matches HEAD)
if ! git diff --cached --quiet; then
	echo "There are still staged changes."
	echo "With --mixed (the default), the changes should be unstaged after the reset."
	echo "Make sure you used 'git reset HEAD~1' without --soft."
	exit 1
fi

# Check working directory still has the changes (files exist)
if [ ! -f "utils.py" ] || [ ! -f "styles.css" ]; then
	echo "utils.py or styles.css is missing from the working directory."
	echo "With --mixed, the files should still be present. Did you use --hard by mistake?"
	echo "Reset with: gitgym reset"
	exit 1
fi

echo "Great work! The commit is undone, nothing is staged, and your files are intact."
echo "'git reset' (--mixed) is perfect for breaking up a large commit into smaller ones."
exit 0
