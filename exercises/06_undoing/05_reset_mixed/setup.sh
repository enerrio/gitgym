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

# Commit 1: stable baseline
echo "# Project" >README.md
git add README.md
git commit -m "Initial commit"

# Commit 2: a large, messy commit with unrelated changes (to undo)
echo "Fix typo in README" >>README.md
cat >utils.py <<'EOF'
def helper():
    pass
EOF
cat >styles.css <<'EOF'
body { margin: 0; }
EOF
git add README.md utils.py styles.css
git commit -m "Add everything at once"
