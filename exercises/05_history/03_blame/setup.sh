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

# Commit 1: Alice adds line 1
echo "Roses are red," >poem.txt
git add poem.txt
GIT_AUTHOR_NAME="Alice" GIT_AUTHOR_EMAIL="alice@example.com" \
	GIT_COMMITTER_NAME="Alice" GIT_COMMITTER_EMAIL="alice@example.com" \
	git commit -m "Add first line of poem"

# Commit 2: Bob adds line 2
echo "Violets are blue," >>poem.txt
git add poem.txt
GIT_AUTHOR_NAME="Bob" GIT_AUTHOR_EMAIL="bob@example.com" \
	GIT_COMMITTER_NAME="Bob" GIT_COMMITTER_EMAIL="bob@example.com" \
	git commit -m "Add second line of poem"

# Commit 3: Charlie adds line 3
echo "Git blame is useful," >>poem.txt
git add poem.txt
GIT_AUTHOR_NAME="Charlie" GIT_AUTHOR_EMAIL="charlie@example.com" \
	GIT_COMMITTER_NAME="Charlie" GIT_COMMITTER_EMAIL="charlie@example.com" \
	git commit -m "Add third line of poem"

# Commit 4: Diana adds line 4
echo "And so are you!" >>poem.txt
git add poem.txt
GIT_AUTHOR_NAME="Diana" GIT_AUTHOR_EMAIL="diana@example.com" \
	GIT_COMMITTER_NAME="Diana" GIT_COMMITTER_EMAIL="diana@example.com" \
	git commit -m "Add fourth line of poem"

# Remove any leftover answer file
rm -f answer.txt
