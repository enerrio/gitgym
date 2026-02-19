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

# No cherry-pick in progress
if [ -f ".git/CHERRY_PICK_HEAD" ]; then
	echo "A cherry-pick is still in progress."
	echo "Resolve any conflicts, stage the files, then run: git cherry-pick --continue"
	exit 1
fi

# login_fix.py must exist on main (brought in by cherry-pick)
if [ ! -f "login_fix.py" ]; then
	echo "login_fix.py is not present on the main branch."
	echo "Cherry-pick the login fix commit: git cherry-pick <hash>"
	echo "(The commit hash is in cherry_pick_this.txt)"
	exit 1
fi

# cleanup.txt must NOT be on main (should not have been cherry-picked)
if [ -f "cleanup.txt" ]; then
	echo "cleanup.txt is present on main — it looks like you cherry-picked more than one commit."
	echo "Reset and cherry-pick only the 'Fix critical login bug' commit."
	exit 1
fi

echo "Excellent! You cherry-picked exactly the commit you needed."
echo "The login fix is now on main without the unrelated cleanup commit."
exit 0
