#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

PASS=1

# .gitignore must exist
if [ ! -f ".gitignore" ]; then
	echo ".gitignore does not exist yet."
	echo "Create a .gitignore file in the exercise directory."
	exit 1
fi

# build.log must be ignored
if ! git check-ignore -q build.log 2>/dev/null; then
	echo "build.log is not being ignored by git."
	echo "Add 'build.log' to your .gitignore."
	PASS=0
fi

# secret.key must be ignored
if ! git check-ignore -q secret.key 2>/dev/null; then
	echo "secret.key is not being ignored by git."
	echo "Add 'secret.key' to your .gitignore."
	PASS=0
fi

if [ "$PASS" -eq 0 ]; then
	exit 1
fi

echo "Great job! Your .gitignore correctly excludes build.log and secret.key."
exit 0
