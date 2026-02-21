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

# Commit the initial version of the notes file
echo "Meeting notes from Monday" >notes.txt
git add notes.txt
git commit -m "Add initial notes"

# Simulate work in progress: add more content to notes.txt
cat >notes.txt <<'EOF'
Meeting notes from Monday

Action items:
- Fix login bug
- Update documentation
- Deploy to staging
EOF

# Stash the work-in-progress changes so the user must pop them to recover
git stash
