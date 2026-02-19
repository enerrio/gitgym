#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Must be on main
CURRENT=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ "$CURRENT" != "main" ]; then
	echo "You are on branch '$CURRENT', not 'main'."
	echo "Switch to main first: git switch main"
	exit 1
fi

# feature branch must still exist
if ! git branch --list "feature" | grep -q "feature"; then
	echo "The 'feature' branch no longer exists. Did you delete it accidentally?"
	echo "Reset the exercise with: gitgym reset"
	exit 1
fi

# feature must be fully merged into main
if ! git branch --merged main | grep -q "feature"; then
	echo "The 'feature' branch has not been merged into 'main' yet."
	echo "Make sure you are on 'main' and run: git merge feature"
	exit 1
fi

# A merge commit must exist (HEAD should have two parents)
PARENT_COUNT=$(git cat-file -p HEAD | grep -c "^parent " || true)
if [ "$PARENT_COUNT" -lt 2 ]; then
	echo "No merge commit found on 'main'."
	echo "Make sure you perform a real merge (not a fast-forward)."
	exit 1
fi

echo "Excellent! You performed a three-way merge of 'feature' into 'main'."
echo "A merge commit was created to tie the two diverged histories together."
exit 0
