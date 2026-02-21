#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
mkdir -p "$EXERCISE_DIR"
cd "$EXERCISE_DIR"

# Start fresh (idempotent)
if [ -d ".git" ]; then
	rm -rf .git
fi

git init --initial-branch=main
git config user.email "gitgym@example.com"
git config user.name "Git Gym"

# Create an initial commit on main
echo "# My Project" >README.md
git add README.md
git commit -m "Initial commit"

# Create the bugfix branch (without switching to it)
git branch bugfix
