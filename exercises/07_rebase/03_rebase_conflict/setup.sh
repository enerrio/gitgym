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

# Initial commit on main (shared base)
echo "timeout=30" >config.txt
git add config.txt
git commit -m "Initial commit"

# feature branch changes the same line
git switch -c feature
echo "timeout=60" >config.txt
git add config.txt
git commit -m "Increase timeout on feature branch"

# main also changes the same line (causes rebase conflict)
git switch main
echo "timeout=45" >config.txt
git add config.txt
git commit -m "Set timeout to 45 on main"

# Leave user on feature branch, ready to rebase
git switch feature
