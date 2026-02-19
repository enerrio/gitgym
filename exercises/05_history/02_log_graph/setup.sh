#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
mkdir -p "$EXERCISE_DIR"
cd "$EXERCISE_DIR"

# Idempotent: start fresh
if [ -d ".git" ]; then
	rm -rf .git
fi

git init
git config user.email "gitgym@example.com"
git config user.name "Git Gym"

# Commit 1: shared ancestor (on main)
echo "# Project" >README.md
git add README.md
git commit -m "Initial commit"

# Commit 2: second commit on main
echo "version: 1.0" >version.txt
git add version.txt
git commit -m "Add version file"

# Create feature branch from initial commit (diverge from main)
git switch -c feature HEAD~1

# Commit 3: first commit on feature
echo "new feature work" >feature.txt
git add feature.txt
git commit -m "Start feature development"

# Commit 4: second commit on feature
echo "feature complete" >>feature.txt
git add feature.txt
git commit -m "Complete feature implementation"

# Return to main (branches have diverged, not yet merged)
git switch main

# Remove any leftover answer file
rm -f answer.txt
