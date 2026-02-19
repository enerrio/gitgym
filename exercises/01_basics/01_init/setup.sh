#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
mkdir -p "$EXERCISE_DIR"
cd "$EXERCISE_DIR"

# Remove any existing git repo so the exercise is in the expected initial state
# (idempotent: running setup.sh a second time resets back to pre-init state)
if [ -d ".git" ]; then
	rm -rf .git
fi

# Create a file for the user to work with
echo "Hello, git!" >hello.txt
