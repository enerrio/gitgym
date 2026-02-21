#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
mkdir -p "$EXERCISE_DIR"
cd "$EXERCISE_DIR"

# Idempotent: start fresh
if [ -d ".git" ]; then
	rm -rf .git
fi

git init --initial-branch=main
git config user.email "gitgym@example.com"
git config user.name "Git Gym"

# Initial commit on main
echo "# My Project" >README.md
git add README.md
git commit -m "Initial commit"

# Create feature branch with two commits
git switch -c feature
echo "feature work" >feature.txt
git add feature.txt
git commit -m "Add feature.txt"

echo "more work" >>feature.txt
git add feature.txt
git commit -m "Update feature.txt"

# Return to main (which has NOT advanced — ready for fast-forward)
git switch main
