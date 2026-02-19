#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
mkdir -p "$EXERCISE_DIR"
cd "$EXERCISE_DIR"

# Idempotent: start fresh
if [ -d ".git" ]; then
	rm -rf .git
fi
rm -f cherry_pick_this.txt

git init
git config user.email "gitgym@example.com"
git config user.name "Git Gym"

# Initial commits on main
echo "# Main application" >main.py
git add main.py
git commit -m "Initial commit"

echo "# v2 feature added" >>main.py
git add main.py
git commit -m "Add v2 feature"

# Create hotfix branch with two commits
git switch -c hotfix

echo "# login fix: validate token before auth" >login_fix.py
git add login_fix.py
git commit -m "Fix critical login bug"

echo "# remove unused imports" >cleanup.txt
git add cleanup.txt
git commit -m "Clean up old code"

# Return to main — leave the hotfix branch alone
git switch main

# Write the hash of the login fix commit for the user's convenience
CHERRY_HASH=$(git log hotfix --format="%H" --grep="Fix critical login bug" | head -1)
echo "$CHERRY_HASH" >cherry_pick_this.txt
