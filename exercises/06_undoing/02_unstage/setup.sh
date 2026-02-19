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

# Create and commit an initial file so HEAD exists
echo "# Meeting Notes" >notes.txt
git add notes.txt
git commit -m "Add notes.txt"

# Modify the file and stage the change (this is what the user must undo)
cat >>notes.txt <<'EOF'

TODO: this section is not ready yet — do not commit!
EOF
git add notes.txt
