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
	echo "Resolve any issues, then run: git rebase --continue"
	exit 1
fi

# feature should have exactly 1 commit beyond main
AHEAD=$(git log main..feature --oneline | wc -l | tr -d ' ')
if [ "$AHEAD" -ne 1 ]; then
	echo "Expected exactly 1 commit on 'feature' beyond 'main', but found $AHEAD."
	echo "Use 'git rebase -i main' and squash all three WIP commits into one."
	exit 1
fi

# The single commit message must not contain "WIP"
COMMIT_MSG=$(git log main..feature --format="%s" | head -1)
if echo "$COMMIT_MSG" | grep -qi "WIP"; then
	echo "The commit message still contains 'WIP': \"$COMMIT_MSG\""
	echo "Re-run 'git rebase -i main' and write a clean commit message."
	exit 1
fi

echo "Well done! You squashed three WIP commits into one clean commit."
echo "Interactive rebase is a powerful tool for keeping history readable."
exit 0
