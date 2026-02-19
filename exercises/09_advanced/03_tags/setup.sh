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

# Build up a small history representing a completed release
echo "1.0.0" >version.txt
git add version.txt
git commit -m "Set version to 1.0.0"

echo "# Changelog" >CHANGELOG.txt
echo "- Initial release" >>CHANGELOG.txt
git add CHANGELOG.txt
git commit -m "Add changelog"

echo "# MyProject" >README.txt
echo "Version 1.0 is ready!" >>README.txt
git add README.txt
git commit -m "Finalize README for v1.0 release"
