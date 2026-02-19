#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check alias.st is set to "status"
ST_ALIAS=$(git config alias.st 2>/dev/null || echo "")
if [ "$ST_ALIAS" != "status" ]; then
	echo "The alias 'st' is not configured as 'status'."
	echo "Set it with: git config alias.st status"
	exit 1
fi

# Check alias.co is set to "checkout"
CO_ALIAS=$(git config alias.co 2>/dev/null || echo "")
if [ "$CO_ALIAS" != "checkout" ]; then
	echo "The alias 'co' is not configured as 'checkout'."
	echo "Set it with: git config alias.co checkout"
	exit 1
fi

echo "Great work! Both aliases are configured."
echo "  git st  →  git status"
echo "  git co  →  git checkout"
echo "You can now use 'git st' and 'git co' as shortcuts in this repository."
exit 0
