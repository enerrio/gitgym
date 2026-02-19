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

# Commit 1: initial project
echo "# Mission Control" >README.md
git add README.md
git commit -m "Initial commit"

# Commit 2: add the secret launch code file
cat >launch.txt <<'EOF'
LAUNCH_CODE=XK-47
Authorized personnel only. Do not share this code.
EOF
git add launch.txt
git commit -m "Add launch code"

# Commit 3: remove the sensitive file
git rm launch.txt
git commit -m "Remove launch code (moved to secure storage)"

# Remove any leftover answer file
rm -f answer.txt
