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

# Commit initial file
echo "# placeholder" >feature.txt
git add feature.txt
git commit -m "Add feature placeholder"

# Modify the file to create work-in-progress changes, then stash them
cat >feature.txt <<'EOF'
def new_feature():
    return "Hello from the new feature!"
EOF

git stash
