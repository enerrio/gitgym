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

# Commit 1: stable baseline
echo "# My App" >README.md
git add README.md
git commit -m "Initial commit"

# Commit 2: premature WIP commit (this is what the user must undo)
cat >feature.py <<'EOF'
def new_feature():
    pass  # TODO: implement
EOF
git add feature.py
git commit -m "WIP: half-done feature"
