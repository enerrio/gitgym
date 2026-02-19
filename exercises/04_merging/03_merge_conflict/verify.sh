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

# Check there is no ongoing merge (MERGE_HEAD would exist during an unfinished merge)
if [ -f ".git/MERGE_HEAD" ]; then
	echo "There is an unfinished merge in progress."
	echo "Resolve all conflicts, stage the files, then run: git commit"
	exit 1
fi

# feature must be fully merged into main
if ! git branch --merged main | grep -q "feature"; then
	echo "The 'feature' branch has not been merged into 'main' yet."
	echo "Run: git merge feature, resolve the conflict, then commit."
	exit 1
fi

# No conflict markers should remain in README.md
if grep -q "^<<<<<<\|^=======\|^>>>>>>>" README.md 2>/dev/null; then
	echo "README.md still contains conflict markers."
	echo "Edit README.md to remove all <<<<<<, =======, and >>>>>>> lines, then stage and commit."
	exit 1
fi

# A merge commit must exist (HEAD should have two parents)
PARENT_COUNT=$(git cat-file -p HEAD | grep -c "^parent " || true)
if [ "$PARENT_COUNT" -lt 2 ]; then
	echo "No merge commit found on 'main'."
	echo "Make sure to complete the merge with: git commit"
	exit 1
fi

echo "Great work! You resolved the merge conflict and completed the merge."
echo "Handling conflicts is a key skill for collaborative git workflows."
exit 0
