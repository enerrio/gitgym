#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check feature.txt exists
if [ ! -f "feature.txt" ]; then
	echo "feature.txt is missing."
	echo "Reset the exercise with: gitgym reset"
	exit 1
fi

# Check that the stashed changes are applied (feature.txt has the new content)
if ! grep -q "new_feature" feature.txt; then
	echo "The stashed changes have not been applied to feature.txt."
	echo "Use 'git stash apply' to apply the stash while keeping it in the list."
	exit 1
fi

# Check stash list is NOT empty (user used apply, not pop)
STASH_COUNT=$(git stash list | wc -l | tr -d ' ')
if [ "$STASH_COUNT" -eq 0 ]; then
	echo "The stash list is empty — it looks like you used 'git stash pop'."
	echo "For this exercise, use 'git stash apply' instead."
	echo "'apply' keeps the stash entry so you can re-use it on other branches."
	exit 1
fi

echo "Excellent! You applied the stash without removing it from the stash list."
echo "'git stash apply' is useful when you want to apply changes to multiple branches"
echo "or keep the stash as a backup while reviewing the result."
exit 0
