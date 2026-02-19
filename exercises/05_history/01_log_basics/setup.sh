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
echo "# My Project" >README.md
git add README.md
git commit -m "Initial commit"

# Commit 2: add main source file
cat >main.py <<'EOF'
def greet(name):
    print(f"Hello, {name}!")

greet("world")
EOF
git add main.py
git commit -m "Add main.py with greeting function"

# Commit 3: bug fix (this is the target commit)
cat >main.py <<'EOF'
def greet(name):
    if not name:
        raise ValueError("name cannot be empty")
    print(f"Hello, {name}!")

greet("world")
EOF
git add main.py
git commit -m "Fix: squash bug #42 (empty name crash)"

# Commit 4: add tests
cat >test_main.py <<'EOF'
# Tests for main.py
def test_greet_normal():
    pass  # placeholder
EOF
git add test_main.py
git commit -m "Add test_main.py"

# Commit 5: update docs
echo "See README for usage." >>README.md
git add README.md
git commit -m "Update README with usage note"

# Remove any leftover answer file
rm -f answer.txt
