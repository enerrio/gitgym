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

# Create feature branch and add a commit
git switch -c feature
echo "feature work" >feature.txt
git add feature.txt
git commit -m "Add feature.txt"

# Return to main and add a commit (branches now diverge)
git switch main
echo "main progress" >main.txt
git add main.txt
git commit -m "Add main.txt"

# User should now be on main, ready to merge feature
