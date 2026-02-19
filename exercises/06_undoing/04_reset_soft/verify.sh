#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check the WIP commit no longer exists as the latest commit
LAST_MSG=$(git log -1 --format="%s")
if echo "$LAST_MSG" | grep -q "WIP: half-done feature"; then
	echo "The 'WIP: half-done feature' commit is still the latest commit."
	echo "Use 'git reset --soft HEAD~1' to undo it."
	exit 1
fi

# Check feature.py is staged (exists in the index and differs from parent)
if git diff --cached --quiet -- feature.py; then
	echo "feature.py is not staged."
	echo "With --soft, the changes should remain in the staging area after the reset."
	echo "Make sure you used 'git reset --soft' (not --hard or --mixed)."
	exit 1
fi

# Check feature.py content is still present
STAGED_CONTENT=$(git show :feature.py 2>/dev/null || echo "")
if [ -z "$STAGED_CONTENT" ]; then
	echo "feature.py is missing from the staging area."
	echo "Reset the exercise with: gitgym reset"
	exit 1
fi

echo "Perfect! The 'WIP' commit is gone and feature.py is still staged."
echo "'git reset --soft' lets you undo a commit without losing any of your work."
exit 0
