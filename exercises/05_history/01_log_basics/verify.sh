#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check answer.txt exists
if [ ! -f "answer.txt" ]; then
	echo "answer.txt not found."
	echo "Use 'git log --oneline' to find the commit hash and write it to answer.txt."
	exit 1
fi

# Get the abbreviated hash of the bug-fix commit
EXPECTED_HASH=$(git log --format="%h %s" | grep "bug #42" | awk '{print $1}')
if [ -z "$EXPECTED_HASH" ]; then
	echo "Could not find the bug-fix commit in the log. Was the repository reset properly?"
	echo "Try: gitgym reset"
	exit 1
fi

# Read user's answer (strip whitespace)
ANSWER=$(tr -d '[:space:]' <answer.txt)

if [ -z "$ANSWER" ]; then
	echo "answer.txt is empty."
	echo "Write the abbreviated commit hash to answer.txt."
	exit 1
fi

# Resolve the user's answer to a short hash (supports both short and full hash)
RESOLVED=$(git rev-parse --short "$ANSWER" 2>/dev/null || echo "")
if [ -z "$RESOLVED" ]; then
	echo "'$ANSWER' is not a valid commit hash in this repository."
	echo "Use 'git log --oneline' to find the correct hash."
	exit 1
fi

if [ "$RESOLVED" != "$EXPECTED_HASH" ]; then
	echo "The hash '$ANSWER' does not point to the bug-fix commit."
	echo "Look for the commit that mentions 'bug #42' in its message."
	exit 1
fi

echo "Correct! '$ANSWER' is the commit that fixed bug #42."
echo "You used 'git log' to navigate project history — a skill you'll use constantly."
exit 0
