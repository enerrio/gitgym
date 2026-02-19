#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check answer.txt exists
if [ ! -f "answer.txt" ]; then
	echo "answer.txt not found."
	echo "Use 'git log --oneline' to find the 'Add launch code' commit, then"
	echo "run 'git show <hash>:launch.txt | head -1 > answer.txt'."
	exit 1
fi

# Find the commit that added launch.txt
COMMIT_HASH=$(git log --format="%h %s" | grep "Add launch code" | awk '{print $1}')
if [ -z "$COMMIT_HASH" ]; then
	echo "Could not find the 'Add launch code' commit. Was the repository reset properly?"
	echo "Try: gitgym reset"
	exit 1
fi

# Get the expected first line from that commit
EXPECTED_LINE=$(git show "${COMMIT_HASH}:launch.txt" | head -1)

# Read user's answer (strip leading/trailing whitespace)
ANSWER=$(sed 's/^[[:space:]]*//;s/[[:space:]]*$//' answer.txt | head -1)

if [ -z "$ANSWER" ]; then
	echo "answer.txt is empty."
	echo "Write the first line of launch.txt from the 'Add launch code' commit to answer.txt."
	exit 1
fi

if [ "$ANSWER" != "$EXPECTED_LINE" ]; then
	echo "The content in answer.txt does not match the first line of launch.txt in the 'Add launch code' commit."
	echo "Use: git show <hash>:launch.txt | head -1"
	exit 1
fi

echo "Correct! You recovered the launch code using 'git show'."
echo "git show lets you inspect any file at any point in history — even deleted files."
exit 0
