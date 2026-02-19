#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check answer.txt exists
if [ ! -f "answer.txt" ]; then
	echo "answer.txt not found."
	echo "Use 'git log --oneline --graph --all' to visualize history, then write the commit count to answer.txt."
	exit 1
fi

# Get the actual total unique commit count
EXPECTED_COUNT=$(git rev-list --all --count)

# Read user's answer (strip whitespace)
ANSWER=$(tr -d '[:space:]' <answer.txt)

if [ -z "$ANSWER" ]; then
	echo "answer.txt is empty."
	echo "Write the total number of commits to answer.txt."
	exit 1
fi

if [ "$ANSWER" != "$EXPECTED_COUNT" ]; then
	echo "The number in answer.txt ($ANSWER) is not correct."
	echo "Expected: $EXPECTED_COUNT unique commits across all branches."
	echo "Run 'git log --oneline --graph --all' and count the '*' symbols, or use 'git rev-list --all --count'."
	exit 1
fi

echo "Correct! There are $EXPECTED_COUNT unique commits across all branches."
echo "The graph view makes diverging branches and their histories easy to see at a glance."
exit 0
