#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

STAGED=$(git diff --cached --name-only)
PASS=1

# feature.txt must be staged
if ! echo "$STAGED" | grep -qx "feature.txt"; then
	echo "feature.txt is not staged yet."
	echo "Use 'git add feature.txt' to stage it."
	PASS=0
fi

# readme.txt (modified) must be staged
if ! echo "$STAGED" | grep -qx "readme.txt"; then
	echo "readme.txt is not staged yet."
	echo "Use 'git add readme.txt' to stage the modified version."
	PASS=0
fi

# notes.txt must NOT be staged
if echo "$STAGED" | grep -qx "notes.txt"; then
	echo "notes.txt should not be staged — leave it untracked."
	PASS=0
fi

if [ "$PASS" -eq 0 ]; then
	exit 1
fi

echo "Great job! You staged the right files and left notes.txt untracked."
exit 0
