#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check that it's a git repo
if [ ! -d ".git" ]; then
	echo "This directory is not a git repository yet."
	echo "Use 'git init' to initialize it."
	exit 1
fi

echo "Great job! You initialized a git repository."
exit 0
