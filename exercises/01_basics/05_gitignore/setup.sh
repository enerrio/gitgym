#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
mkdir -p "$EXERCISE_DIR"
cd "$EXERCISE_DIR"

# Start fresh (idempotent)
if [ -d ".git" ]; then
	rm -rf .git
fi
rm -f .gitignore

git init --initial-branch=main
git config user.email "gitgym@example.com"
git config user.name "Git Gym"

# Commit a normal source file to give the repo some history
echo "print('hello')" >main.py
git add main.py
git commit -m "Initial commit"

# Create files that the user should ignore (do NOT stage or commit them)
echo "build output log" >build.log
echo "super-secret-value" >secret.key
