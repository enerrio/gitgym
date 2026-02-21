# Contributing to gitgym

Thanks for your interest in contributing! Whether it's a new exercise, a bug fix, or an improvement to the CLI, contributions are welcome.

## Adding a New Exercise

Each exercise is a self-contained directory with three files. This is the core pattern:

```
exercises/<NN_topic>/<NN_name>/
├── exercise.toml   # metadata, description, goal, and hints
├── setup.sh        # creates the initial repo state
└── verify.sh       # checks if the learner solved it (exit 0 = pass)
```

### Step 1: Choose a Location

Exercises are grouped by topic. Each topic is a numbered directory (e.g., `01_basics`, `03_branching`). Within a topic, exercises are also numbered to control order.

- To add an exercise to an existing topic, create the next numbered directory inside it.
- To add a new topic, create a new numbered topic directory.

### Step 2: Create `exercise.toml`

This file defines all the metadata. Here's a template:

```toml
[exercise]
name = "your_exercise_name"
topic = "Topic Name"
title = "A Short Title"
description = """
A paragraph explaining the context and what the learner should do. \
Use backslash line continuations to keep the TOML readable.
"""

[goal]
summary = "One sentence describing the target state."

[[hints]]
text = "A gentle nudge in the right direction."

[[hints]]
text = "A more specific hint."

[[hints]]
text = "The exact command or steps needed."
```

Guidelines:

- `name` must be unique across all exercises and match the directory name.
- Provide 2-4 hints, progressing from vague to specific.
- Keep the description focused on one concept.

### Step 3: Create `setup.sh`

This script receives a single argument: the path to the exercise working directory. It should create the initial repo state the learner will work with.

```bash
#!/usr/bin/env bash
set -euo pipefail

WORKDIR="$1"
cd "$WORKDIR"

git init
# ... create files, make commits, set up branches, etc.
```

Guidelines:

- Always start with `set -euo pipefail`.
- Use `$1` for the working directory — never hardcode paths.
- Keep setup minimal — only create what's needed for the exercise.
- Use deterministic values (fixed dates, author names) when possible so verify scripts can rely on them.

### Step 4: Create `verify.sh`

This script also receives the exercise working directory as `$1`. It should exit `0` if the learner solved the exercise, or exit non-zero with an error message if not.

```bash
#!/usr/bin/env bash
set -euo pipefail

WORKDIR="$1"
cd "$WORKDIR"

# Example: check that a branch named "feature" exists
if ! git branch --list | grep -q "feature"; then
    echo "Expected a branch named 'feature'."
    exit 1
fi
```

Guidelines:

- Print a helpful message on failure so the learner knows what's wrong.
- Check the _result_, not the _method_ — don't verify which commands were run, verify the end state.
- Make sure `verify.sh` is executable (`chmod +x verify.sh`).

### Step 5: Test It

```bash
# Run setup and verify manually
tmpdir=$(mktemp -d)
bash exercises/<topic>/<exercise>/setup.sh "$tmpdir"
cd "$tmpdir"
# ... solve the exercise manually ...
bash /path/to/exercises/<topic>/<exercise>/verify.sh "$tmpdir"

# Run the full test suite
uv run pytest -v
```

Also confirm that `gitgym list` shows your new exercise and that `gitgym start <name>` + `gitgym verify` works end to end.

## Reporting Bugs

Open an issue using the **Bug Report** template. Include:

- Your OS and Python version
- The exercise you were working on (if applicable)
- Steps to reproduce the problem
- What you expected vs. what happened

## Suggesting Exercises

Open an issue using the **Exercise Request** template. Describe:

- The git concept you want covered
- Why it would be a good addition
- Where it fits in the current exercise progression

## Development Setup

```bash
git clone https://github.com/enerrio/git-gym.git
cd git-gym
uv sync --dev
uv run pytest -v          # run tests
uv run ruff check .       # lint
uv run ruff format .      # format
```

## Code Style

- This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.
- Run `uv run ruff check . && uv run ruff format --check .` before submitting a PR.
- CI will enforce this automatically.
