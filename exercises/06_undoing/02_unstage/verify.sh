#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check notes.txt still exists
if [ ! -f "notes.txt" ]; then
	echo "notes.txt is missing."
	echo "Reset the exercise with: gitgym reset"
	exit 1
fi

# Check notes.txt is NOT staged (no diff between index and HEAD for this file)
if ! git diff --cached --quiet -- notes.txt; then
	echo "notes.txt is still staged."
	echo "Use 'git restore --staged notes.txt' to unstage it."
	exit 1
fi

# Check the working directory changes are still present (file differs from HEAD)
if git diff --quiet -- notes.txt; then
	echo "The changes to notes.txt are gone from the working directory too."
	echo "The goal is to unstage without losing changes. Reset with: gitgym reset"
	exit 1
fi

echo "Correct! notes.txt is unstaged but your working directory changes are preserved."
echo "'git restore --staged' gives you a chance to review changes before committing."
exit 0
