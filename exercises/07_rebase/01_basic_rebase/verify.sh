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
	echo "Resolve any conflicts, stage the files, then run: git rebase --continue"
	exit 1
fi

# After a successful rebase, the merge-base of feature and main should equal
# main's HEAD (i.e., feature starts from where main currently is).
MERGE_BASE=$(git merge-base feature main)
MAIN_HEAD=$(git rev-parse main)

if [ "$MERGE_BASE" != "$MAIN_HEAD" ]; then
	echo "The 'feature' branch has not been rebased onto 'main' yet."
	echo "Run: git rebase main"
	exit 1
fi

# feature should have at least one commit beyond main
AHEAD=$(git log main..feature --oneline | wc -l | tr -d ' ')
if [ "$AHEAD" -lt 1 ]; then
	echo "The 'feature' branch has no commits beyond 'main'."
	echo "Something went wrong — try resetting with: gitgym reset"
	exit 1
fi

echo "Excellent! You successfully rebased the feature branch onto main."
echo "The history is now linear: feature's commits follow directly after main's latest commit."
exit 0
