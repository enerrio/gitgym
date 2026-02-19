#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Bisect must not be in progress
if [ -f ".git/BISECT_HEAD" ] || [ -f ".git/BISECT_LOG" ]; then
	echo "git bisect is still in progress."
	echo "Run 'git bisect reset' to return to the latest commit before checking your answer."
	exit 1
fi

# found_commit.txt must exist
if [ ! -f "found_commit.txt" ]; then
	echo "found_commit.txt does not exist."
	echo "After running bisect, write the hash of the first bad commit to found_commit.txt"
	exit 1
fi

# Read the user's answer
ANSWER=$(cat found_commit.txt | tr -d '[:space:]')
if [ -z "$ANSWER" ]; then
	echo "found_commit.txt is empty."
	echo "Write the full commit hash of the first bad commit into found_commit.txt"
	exit 1
fi

# Resolve the user's answer to a full hash (handles both full and abbreviated hashes)
if ! git rev-parse "$ANSWER" >/dev/null 2>&1; then
	echo "'$ANSWER' is not a valid commit hash in this repository."
	exit 1
fi
ANSWER_FULL=$(git rev-parse "$ANSWER")

# Find the expected bad commit (the one that changed calc.sh to return 41)
EXPECTED_HASH=$(git log --format="%H" --grep="Optimize calculation algorithm" | head -1)

if [ "$ANSWER_FULL" != "$EXPECTED_HASH" ]; then
	EXPECTED_SHORT=$(git rev-parse --short "$EXPECTED_HASH")
	echo "That is not the first bad commit."
	echo "Hint: the first bad commit message is 'Optimize calculation algorithm' ($EXPECTED_SHORT)."
	exit 1
fi

echo "Correct! You found the first bad commit using git bisect."
echo "git bisect is a powerful tool for tracking down regressions in large histories."
exit 0
