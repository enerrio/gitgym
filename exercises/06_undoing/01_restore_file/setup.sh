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

# Commit the initial config file
cat >config.txt <<'EOF'
host=localhost
port=8080
debug=false
EOF
git add config.txt
git commit -m "Add config.txt"

# Now modify the file without staging (simulating unwanted edits)
cat >config.txt <<'EOF'
host=production.example.com
port=9999
debug=true
password=hunter2
EOF
