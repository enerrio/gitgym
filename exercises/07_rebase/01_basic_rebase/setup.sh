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
echo "Version 1.0" >version.txt
git add version.txt
git commit -m "Initial commit"

# Create feature branch from here
git switch -c feature

# Add two commits on feature
echo "Feature work A" >feature_a.txt
git add feature_a.txt
git commit -m "Add feature A"

echo "Feature work B" >feature_b.txt
git add feature_b.txt
git commit -m "Add feature B"

# Switch back to main and advance it
git switch main
echo "Hotfix applied" >hotfix.txt
git add hotfix.txt
git commit -m "Apply hotfix on main"

# Leave user on feature branch (target branch for the rebase)
git switch feature
