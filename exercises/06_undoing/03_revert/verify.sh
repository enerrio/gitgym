#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check app.py exists
if [ ! -f "app.py" ]; then
	echo "app.py is missing."
	echo "Reset the exercise with: gitgym reset"
	exit 1
fi

# Check the original "Add debug output" commit is still in history (history not rewritten)
DEBUG_COMMIT=$(git log --format="%h %s" | grep "Add debug output" | awk '{print $1}')
if [ -z "$DEBUG_COMMIT" ]; then
	echo "The 'Add debug output' commit is no longer in the history."
	echo "Use 'git revert' — it creates a new commit rather than removing the old one."
	echo "Reset with: gitgym reset"
	exit 1
fi

# Check there is a revert commit in the log
REVERT_COMMIT=$(git log --format="%s" | grep -i "^[Rr]evert" | head -1 || true)
if [ -z "$REVERT_COMMIT" ]; then
	echo "No revert commit found in the history."
	echo "Use 'git revert <hash>' to create a revert commit."
	exit 1
fi

# Check app.py no longer contains the debug line
if grep -q "DEBUG:" app.py; then
	echo "app.py still contains the debug output line."
	echo "Make sure you reverted the correct commit."
	exit 1
fi

echo "Excellent! You reverted the 'Add debug output' commit."
echo "The original commit is still in the history, and a new revert commit was added on top."
echo "'git revert' is the safe way to undo changes on shared branches."
exit 0
