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

# Initial commit on main
echo "# My Project" >README.md
git add README.md
git commit -m "Initial commit"

# Create feature branch with three messy WIP commits
git switch -c feature

echo "step 1" >feature.txt
git add feature.txt
git commit -m "WIP: start feature"

echo "step 2" >>feature.txt
git add feature.txt
git commit -m "WIP: make progress"

echo "step 3" >>feature.txt
git add feature.txt
git commit -m "WIP: finish feature"

# User is on feature branch, ready to run: git rebase -i main
