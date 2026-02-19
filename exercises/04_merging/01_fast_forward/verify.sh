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

# feature branch must exist
if ! git branch --list "feature" | grep -q "feature"; then
	echo "The 'feature' branch no longer exists. Did you delete it accidentally?"
	echo "Reset the exercise with: gitgym reset"
	exit 1
fi

# main and feature must point to the same commit (fast-forward complete)
MAIN_SHA=$(git rev-parse main)
FEATURE_SHA=$(git rev-parse feature)

if [ "$MAIN_SHA" != "$FEATURE_SHA" ]; then
	echo "The 'feature' branch has not been merged into 'main' yet."
	echo "Make sure you are on 'main' and run: git merge feature"
	exit 1
fi

# Ensure no merge commit was created (fast-forward: no extra parent)
PARENT_COUNT=$(git cat-file -p HEAD | grep -c "^parent " || true)
if [ "$PARENT_COUNT" -gt 1 ]; then
	echo "Looks like a merge commit was created instead of a fast-forward merge."
	echo "Reset and try again without the --no-ff flag: gitgym reset"
	exit 1
fi

echo "Well done! You performed a fast-forward merge of 'feature' into 'main'."
echo "Notice that no merge commit was created — git simply moved the pointer forward."
exit 0
