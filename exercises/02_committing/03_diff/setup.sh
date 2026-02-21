#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
mkdir -p "$EXERCISE_DIR"
cd "$EXERCISE_DIR"

# Start fresh (idempotent)
if [ -d ".git" ]; then
	rm -rf .git
fi

git init --initial-branch=main
git config user.email "gitgym@example.com"
git config user.name "Git Gym"

# Commit original version of app.py
cat >app.py <<'EOF'
def greet(name):
    return "Hello, " + name
EOF
git add app.py
git commit -m "Add app.py"

# Modify app.py — the user must inspect, stage, and commit this change
cat >app.py <<'EOF'
def greet(name):
    return f"Hello, {name}!"
EOF
