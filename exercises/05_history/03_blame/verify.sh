#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check poem.txt still exists (not accidentally deleted)
if [ ! -f "poem.txt" ]; then
	echo "poem.txt is missing. Reset the exercise with: gitgym reset"
	exit 1
fi

# Check answer.txt exists
if [ ! -f "answer.txt" ]; then
	echo "answer.txt not found."
	echo "Use 'git blame poem.txt' to find the author of line 3, then write their name to answer.txt."
	exit 1
fi

# Get the commit hash responsible for line 3
LINE3_HASH=$(git blame poem.txt | sed -n '3p' | awk '{print $1}')
if [ -z "$LINE3_HASH" ]; then
	echo "Could not determine the author of line 3. Was the repository reset properly?"
	echo "Try: gitgym reset"
	exit 1
fi

# Get the author name for that commit
EXPECTED_AUTHOR=$(git log -1 --format="%aN" "$LINE3_HASH")

# Read user's answer (strip leading/trailing whitespace)
ANSWER=$(sed 's/^[[:space:]]*//;s/[[:space:]]*$//' answer.txt | head -1)

if [ -z "$ANSWER" ]; then
	echo "answer.txt is empty."
	echo "Write the author's name to answer.txt."
	exit 1
fi

if [ "$ANSWER" != "$EXPECTED_AUTHOR" ]; then
	echo "The name '$ANSWER' is not the author of line 3."
	echo "Run 'git blame poem.txt' and look at line 3."
	exit 1
fi

echo "Correct! '$EXPECTED_AUTHOR' wrote line 3 of poem.txt."
echo "git blame is a powerful tool for understanding who made changes and why."
exit 0
