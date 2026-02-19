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

# Create and commit an initial file so readme.txt has a committed version
echo "# My Project" >readme.txt
git add readme.txt
git commit -m "Initial commit"

# Modify the committed file (now it appears as "modified" in git status)
echo "# My Project (updated)" >readme.txt

# Add two new untracked files — user must stage only feature.txt
echo "New feature content" >feature.txt
echo "Private notes" >notes.txt
