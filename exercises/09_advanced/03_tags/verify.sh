#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

HEAD_HASH=$(git rev-parse HEAD)

# Check lightweight tag v1.0 exists
if ! git rev-parse "v1.0" >/dev/null 2>&1; then
	echo "Tag 'v1.0' does not exist."
	echo "Create it with: git tag v1.0"
	exit 1
fi

# Check v1.0 points to HEAD
V1_HASH=$(git rev-parse "v1.0")
if [ "$V1_HASH" != "$HEAD_HASH" ]; then
	echo "Tag 'v1.0' does not point to the current HEAD commit."
	echo "Delete it and recreate: git tag -d v1.0 && git tag v1.0"
	exit 1
fi

# Check that v1.0 is a lightweight tag (not annotated)
# Annotated tags have their own object type; lightweight tags resolve directly to commits
TAG_TYPE=$(git cat-file -t "v1.0")
if [ "$TAG_TYPE" != "commit" ]; then
	echo "'v1.0' appears to be an annotated tag, not a lightweight tag."
	echo "Delete it and recreate without -a: git tag -d v1.0 && git tag v1.0"
	exit 1
fi

# Check annotated tag v1.0-release exists
if ! git rev-parse "v1.0-release" >/dev/null 2>&1; then
	echo "Tag 'v1.0-release' does not exist."
	echo "Create it with: git tag -a v1.0-release -m 'Release version 1.0'"
	exit 1
fi

# Check v1.0-release is an annotated tag
RELEASE_TYPE=$(git cat-file -t "v1.0-release")
if [ "$RELEASE_TYPE" != "tag" ]; then
	echo "'v1.0-release' is a lightweight tag, but it should be annotated."
	echo "Delete it and recreate with -a: git tag -d v1.0-release && git tag -a v1.0-release -m 'Release version 1.0'"
	exit 1
fi

# Check v1.0-release points to HEAD
RELEASE_COMMIT=$(git rev-parse "v1.0-release^{commit}")
if [ "$RELEASE_COMMIT" != "$HEAD_HASH" ]; then
	echo "Tag 'v1.0-release' does not point to the current HEAD commit."
	exit 1
fi

# Check v1.0-release has the correct message
TAG_MSG=$(git tag -l --format="%(contents)" "v1.0-release" | head -1)
if ! echo "$TAG_MSG" | grep -qi "release version 1.0"; then
	echo "The tag message for 'v1.0-release' should be 'Release version 1.0'."
	echo "Delete it and recreate: git tag -d v1.0-release && git tag -a v1.0-release -m 'Release version 1.0'"
	exit 1
fi

echo "Well done! You created both a lightweight tag (v1.0) and an annotated tag (v1.0-release)."
echo "Annotated tags are the recommended way to mark releases because they carry metadata."
exit 0
