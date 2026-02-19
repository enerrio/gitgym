#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
mkdir -p "$EXERCISE_DIR"
cd "$EXERCISE_DIR"

# Start fresh (idempotent)
if [ -d ".git" ]; then
	rm -rf .git
fi

git init
git config user.email "gitgym@example.com"
git config user.name "Git Gym"

# Create an initial commit on main
echo "# My Project" >README.md
git add README.md
git commit -m "Initial commit"

# Create and switch to old-feature branch, add a commit
git switch -c old-feature
echo "feature work" >feature.txt
git add feature.txt
git commit -m "Add feature"

# Merge old-feature into main and return to main
git switch main
git merge old-feature --no-ff -m "Merge old-feature into main"
