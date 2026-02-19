#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check that hello.txt is staged (present in the index)
if ! git diff --cached --name-only | grep -qx "hello.txt"; then
	echo "hello.txt is not staged yet."
	echo "Use 'git add hello.txt' to stage it."
	exit 1
fi

echo "Great job! hello.txt is staged and ready to commit."
exit 0
