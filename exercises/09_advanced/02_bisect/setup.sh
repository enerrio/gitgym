#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
mkdir -p "$EXERCISE_DIR"
cd "$EXERCISE_DIR"

# Idempotent: start fresh
if [ -d ".git" ]; then
	rm -rf .git
fi
rm -f test.sh found_commit.txt

git init
git config user.email "gitgym@example.com"
git config user.name "Git Gym"

# Commit 1 — good: calc.sh returns the correct answer (42)
cat >calc.sh <<'EOF'
#!/usr/bin/env bash
echo 42
EOF
chmod +x calc.sh
git add calc.sh
git commit -m "Add calculation script"

# Commit 2 — good: add logging helper
echo "# logging" >log_helper.sh
git add log_helper.sh
git commit -m "Add logging helper"

# Commit 3 — good: add README
echo "# Calculator Project" >README.txt
git add README.txt
git commit -m "Add README"

# Commit 4 — BAD: optimize calculation but introduce a bug (returns 41 instead of 42)
cat >calc.sh <<'EOF'
#!/usr/bin/env bash
# Optimized calculation
echo 41
EOF
git add calc.sh
git commit -m "Optimize calculation algorithm"

# Commit 5 — still bad (inherits the bug): add unit test file
echo "# tests" >tests.txt
git add tests.txt
git commit -m "Add unit test stubs"

# Commit 6 — still bad: add documentation
echo "Usage: ./calc.sh" >USAGE.txt
git add USAGE.txt
git commit -m "Add usage documentation"

# Commit 7 — still bad: update version
echo "1.1" >version.txt
git add version.txt
git commit -m "Bump version to 1.1"

# Write the test script that bisect will run
# It runs calc.sh and checks the output is 42
cat >test.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
RESULT=$(./calc.sh)
if [ "$RESULT" = "42" ]; then
    exit 0
else
    exit 1
fi
EOF
chmod +x test.sh
