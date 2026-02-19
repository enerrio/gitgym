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

# Initial commit on main with a shared file
echo "Project version: 1.0" >README.md
git add README.md
git commit -m "Initial commit"

# feature branch changes the same line
git switch -c feature
echo "Project version: 2.0-feature" >README.md
git add README.md
git commit -m "Bump version on feature branch"

# main also changes the same line (creates conflict)
git switch main
echo "Project version: 1.1-main" >README.md
git add README.md
git commit -m "Bump version on main"

# User is now on main and should run: git merge feature (which will conflict)
