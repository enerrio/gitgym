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

# Commit 1: initial app
cat >app.py <<'EOF'
def main():
    print("Hello, world!")

main()
EOF
git add app.py
git commit -m "Initial commit"

# Commit 2: add debug output (the "bad" commit to revert)
cat >app.py <<'EOF'
def main():
    print("DEBUG: entering main()")
    print("Hello, world!")

main()
EOF
git add app.py
git commit -m "Add debug output"

# Commit 3: add an unrelated feature (to show history is preserved)
echo "# App" >README.md
git add README.md
git commit -m "Add README"
