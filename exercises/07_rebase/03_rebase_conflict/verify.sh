#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Must be on feature branch
CURRENT=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ "$CURRENT" != "feature" ]; then
	echo "You are on branch '$CURRENT', not 'feature'."
	echo "Switch to the feature branch first: git switch feature"
	exit 1
fi

# No ongoing rebase
if [ -d ".git/rebase-merge" ] || [ -d ".git/rebase-apply" ]; then
	echo "A rebase is still in progress."
	echo "Resolve the conflict in config.txt, stage it, then run: git rebase --continue"
	exit 1
fi

# After a successful rebase, feature should start from main's HEAD
MERGE_BASE=$(git merge-base feature main)
MAIN_HEAD=$(git rev-parse main)

if [ "$MERGE_BASE" != "$MAIN_HEAD" ]; then
	echo "The 'feature' branch has not been rebased onto 'main' yet."
	echo "Run: git rebase main"
	exit 1
fi

# No conflict markers should remain in config.txt
if grep -q "^<<<<<<\|^=======\|^>>>>>>>" config.txt 2>/dev/null; then
	echo "config.txt still contains conflict markers."
	echo "Edit config.txt to remove all <<<<<<, =======, and >>>>>>> lines, stage it, then run: git rebase --continue"
	exit 1
fi

echo "Great work! You resolved the rebase conflict and completed the rebase."
echo "Handling conflicts during a rebase is the same as during a merge — edit, stage, continue."
exit 0
