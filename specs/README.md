# gitgym - Specification Document

An interactive CLI platform for learning git, inspired by [Rustlings](https://github.com/rust-lang/rustlings). Users work through progressively harder exercises that set up real git repositories in a safe, sandboxed workspace and verify that the user has achieved a goal state.

## Overview

| Attribute      | Value                                                             |
| -------------- | ----------------------------------------------------------------- |
| CLI command    | `gitgym`                                                          |
| Python package | `gitgym`                                                          |
| Python version | 3.12+                                                             |
| Distribution   | PyPI (`pip install gitgym` or `uv pip install gitgym`)            |
| Tooling        | `uv` for project management, dependency resolution, and packaging |
| License        | MIT                                                               |

## Core Concepts

### Exercises

Each exercise presents the user with a pre-built git repository in a specific state (commits, branches, staged files, conflicts, etc.) and a clearly defined **goal**. The user must run real git commands in their own terminal to transform the repo from the initial state to the goal state. There are no quizzes — the exercises themselves test knowledge.

### Sandbox / Workspace

All exercise repos live in a **persistent dedicated workspace** at `~/.gitgym/exercises/`. This allows users to close their terminal and pick up where they left off. Repos are never created inside the user's own projects.

### Interaction Model

The user interacts with exercise repos **directly in their terminal**. The typical workflow is:

1. Run `gitgym start` or `gitgym next` to set up the current exercise.
2. `cd` into the exercise directory printed by gitgym.
3. Read the exercise description (also available via `gitgym describe`).
4. Run git commands directly in the exercise repo.
5. Run `gitgym verify` to check if the goal state is met, or use `gitgym watch` for automatic re-verification.

## CLI Commands

| Command                   | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| `gitgym list`             | List all exercises grouped by topic, showing completion status            |
| `gitgym start [exercise]` | Set up an exercise repo. If no name given, starts the next incomplete one |
| `gitgym next`             | Alias for `gitgym start` with no argument (next incomplete exercise)      |
| `gitgym describe`         | Print the current exercise's description and goal                         |
| `gitgym verify`           | Check if the current exercise's goal state is met                         |
| `gitgym watch`            | Watch mode: automatically re-verify on repo changes                       |
| `gitgym hint`             | Show the next progressive hint (repeat for more specific hints)           |
| `gitgym reset`            | Reset the current exercise to its initial state                           |
| `gitgym reset <exercise>` | Reset a specific exercise by name                                         |
| `gitgym reset --all`      | Reset all exercises and clear progress                                    |
| `gitgym progress`         | Show overall progress summary                                             |

## Exercise Structure

### On Disk

Each exercise is a folder under `exercises/` in the gitgym package:

```
exercises/
  01_basics/
    01_init/
      exercise.toml
      setup.sh
      verify.sh
    02_staging/
      exercise.toml
      setup.sh
      verify.sh
  02_committing/
    01_first_commit/
      exercise.toml
      setup.sh
      verify.sh
    ...
  03_branching/
    ...
```

The directory naming convention `NN_topic/NN_exercise` determines both the **topic grouping** and the **recommended order**.

### exercise.toml

```toml
[exercise]
name = "init"
topic = "Basics"
title = "Initialize a Repository"
description = """
Every git journey starts with `git init`. In this exercise, you'll \
initialize a new git repository in the provided directory.
"""

[goal]
summary = "The directory should be a valid git repository."

[[hints]]
text = "Look at the `git init` command."

[[hints]]
text = "Run `git init` inside the exercise directory."

[[hints]]
text = "Just run: git init"
```

**Fields:**

| Field                  | Required | Description                                          |
| ---------------------- | -------- | ---------------------------------------------------- |
| `exercise.name`        | yes      | Unique identifier (matches folder name)              |
| `exercise.topic`       | yes      | Topic group for display purposes                     |
| `exercise.title`       | yes      | Human-readable title                                 |
| `exercise.description` | yes      | Full description shown to user (supports multi-line) |
| `goal.summary`         | yes      | Short description of the goal state                  |
| `hints`                | yes      | Array of progressive hints (shown one at a time)     |

### setup.sh

A bash script that **creates** the exercise repo's initial state. It receives one argument: the path to the exercise working directory.

```bash
#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
mkdir -p "$EXERCISE_DIR"
cd "$EXERCISE_DIR"

# Example: create a directory with a file but no git repo
echo "Hello, git!" > hello.txt
```

Requirements:

- Must be idempotent (running it twice produces the same state).
- Must only modify files under the provided `$EXERCISE_DIR`.
- Should not require network access.
- Must set `set -euo pipefail` at the top.

### verify.sh

A bash script that **checks** whether the exercise goal is met. It receives one argument: the path to the exercise working directory. Exit code 0 means success; non-zero means failure. Stdout/stderr is captured and shown to the user on failure.

```bash
#!/usr/bin/env bash
set -euo pipefail

EXERCISE_DIR="$1"
cd "$EXERCISE_DIR"

# Check that it's a git repo
if [ ! -d ".git" ]; then
    echo "This directory is not a git repository yet."
    echo "Use 'git init' to initialize it."
    exit 1
fi

echo "Great job! You initialized a git repository."
exit 0
```

Requirements:

- Exit 0 on success, non-zero on failure.
- Print a helpful message on failure (shown to the user).
- Print a congratulatory/informative message on success.
- Must only read from the provided `$EXERCISE_DIR`.

## Topics and Exercise Curriculum

### 01 - Basics

| #   | Exercise     | Goal                                                 |
| --- | ------------ | ---------------------------------------------------- |
| 01  | init         | Initialize a git repository                          |
| 02  | staging      | Stage files with `git add`                           |
| 03  | status       | Interpret `git status` and stage specific files      |
| 04  | first_commit | Create a commit with a message                       |
| 05  | gitignore    | Create a `.gitignore` to exclude files from tracking |

### 02 - Committing

| #   | Exercise     | Goal                                                   |
| --- | ------------ | ------------------------------------------------------ |
| 01  | amend        | Amend the most recent commit message                   |
| 02  | multi_commit | Create a series of meaningful commits                  |
| 03  | diff         | Use `git diff` to understand changes before committing |

### 03 - Branching

| #   | Exercise        | Goal                              |
| --- | --------------- | --------------------------------- |
| 01  | create_branch   | Create and switch to a new branch |
| 02  | switch_branches | Switch between existing branches  |
| 03  | delete_branch   | Delete a merged branch            |

### 04 - Merging

| #   | Exercise        | Goal                         |
| --- | --------------- | ---------------------------- |
| 01  | fast_forward    | Perform a fast-forward merge |
| 02  | three_way_merge | Perform a three-way merge    |
| 03  | merge_conflict  | Resolve a merge conflict     |

### 05 - History

| #   | Exercise   | Goal                                                       |
| --- | ---------- | ---------------------------------------------------------- |
| 01  | log_basics | Use `git log` to find information about past commits       |
| 02  | log_graph  | Use `git log --oneline --graph --all` to visualize history |
| 03  | blame      | Use `git blame` to find who changed a line                 |
| 04  | show       | Use `git show` to inspect a specific commit                |

### 06 - Undoing Changes

| #   | Exercise     | Goal                                                       |
| --- | ------------ | ---------------------------------------------------------- |
| 01  | restore_file | Restore a file to its last committed state                 |
| 02  | unstage      | Unstage a file without losing changes                      |
| 03  | revert       | Revert a commit without rewriting history                  |
| 04  | reset_soft   | Use `git reset --soft` to uncommit but keep changes staged |
| 05  | reset_mixed  | Use `git reset` to uncommit and unstage changes            |

### 07 - Rebase

| #   | Exercise           | Goal                                    |
| --- | ------------------ | --------------------------------------- |
| 01  | basic_rebase       | Rebase a feature branch onto main       |
| 02  | interactive_rebase | Squash commits using interactive rebase |
| 03  | rebase_conflict    | Resolve conflicts during a rebase       |

### 08 - Stashing

| #   | Exercise        | Goal                                                      |
| --- | --------------- | --------------------------------------------------------- |
| 01  | stash_basics    | Stash uncommitted changes and reapply them                |
| 02  | stash_pop_apply | Understand the difference between `stash pop` and `apply` |

### 09 - Advanced

| #   | Exercise    | Goal                                     |
| --- | ----------- | ---------------------------------------- |
| 01  | cherry_pick | Cherry-pick a commit from another branch |
| 02  | bisect      | Use `git bisect` to find a buggy commit  |
| 03  | tags        | Create and manage tags                   |
| 04  | aliases     | Configure git aliases                    |

## Progress Tracking

Progress is stored in `~/.gitgym/progress.json`:

```json
{
  "version": 1,
  "exercises": {
    "01_basics/01_init": {
      "status": "completed",
      "completed_at": "2026-02-16T10:30:00Z",
      "hints_used": 0
    },
    "01_basics/02_staging": {
      "status": "in_progress",
      "started_at": "2026-02-16T10:35:00Z",
      "hints_used": 1
    }
  }
}
```

**Statuses:** `not_started` (default / absent), `in_progress`, `completed`.

The `reset` command updates progress accordingly:

- `reset <exercise>` sets that exercise back to `not_started` and re-runs `setup.sh`.
- `reset --all` deletes progress.json and re-creates the entire workspace.

## Watch Mode

`gitgym watch` uses filesystem polling (via `watchdog` or simple polling loop) to detect changes in the current exercise directory. When changes are detected, it automatically runs `verify.sh` and displays the result. This provides a Rustlings-like experience where the user works in one terminal and sees verification results update in another.

Polling interval: 1 second (configurable).

## Progressive Hints

Hints are defined in `exercise.toml` as an ordered array. Each call to `gitgym hint` reveals the next hint in the sequence. The number of hints used is tracked in `progress.json`.

Example output:

```
$ gitgym hint
Hint 1/3: Look at the `git init` command.

$ gitgym hint
Hint 2/3: Run `git init` inside the exercise directory.

$ gitgym hint
Hint 3/3: Just run: git init
(No more hints available.)
```

## Project Structure (Python Package)

```
gitgym/
  pyproject.toml            # uv-managed project config (PEP 621)
  uv.lock                   # uv lockfile (committed to repo)
  LICENSE
  README.md
  src/
    gitgym/
      __init__.py
      __main__.py            # python -m gitgym support
      cli.py                 # CLI entry point (click)
      config.py              # Paths, constants
      exercise.py            # Exercise loading/parsing
      runner.py              # Setup and verify execution
      progress.py            # Progress tracking
      watcher.py             # Watch mode implementation
      display.py             # Terminal output formatting
  exercises/                 # Exercise definitions (shipped with package)
    01_basics/
      01_init/
        exercise.toml
        setup.sh
        verify.sh
      ...
  tests/
    ...
```

## Dependencies and Tooling

The project uses **uv** for all Python project management: dependency resolution, virtual environments, locking, and packaging.

### Runtime Dependencies

| Dependency | Purpose                     | Required                       |
| ---------- | --------------------------- | ------------------------------ |
| `click`    | CLI framework               | yes                            |
| `tomllib`  | TOML parsing (stdlib 3.11+) | stdlib                         |
| `watchdog` | Filesystem watching         | optional (fallback to polling) |

### Development Workflow

```bash
# Clone and set up
git clone <repo-url> && cd gitgym
uv sync                    # Create venv, install deps from lockfile

# Run during development
uv run gitgym              # Run the CLI via uv

# Add a dependency
uv add <package>           # Adds to pyproject.toml and updates uv.lock

# Add a dev dependency
uv add --dev <package>

# Run tests
uv run pytest

# Build for distribution
uv build                   # Creates sdist and wheel in dist/

# Publish to PyPI
uv publish
```

### pyproject.toml (key sections)

```toml
[project]
name = "gitgym"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "click",
]

[project.optional-dependencies]
watch = ["watchdog"]

[project.scripts]
gitgym = "gitgym.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Error Handling

- **Git not installed:** Detect at startup, print clear error with install instructions.
- **Exercise repo corrupted:** Suggest `gitgym reset` to re-create the exercise.
- **Setup script failure:** Print the script's stderr and suggest filing a bug.
- **Verify script failure (non-goal):** Print error and suggest `gitgym reset`.
- **No exercise in progress:** Print helpful message pointing to `gitgym start` or `gitgym list`.

## Open Source Considerations

- MIT License.
- Contributing guide explaining how to add new exercises (TOML + setup.sh + verify.sh).
- CI pipeline running exercise setup + verify scripts to ensure they work.
- All exercise content should be beginner-friendly with clear, jargon-free descriptions.

## Non-Goals (Explicitly Out of Scope)

- **Remote operations:** No exercises involving `push`, `pull`, `fetch`, or remote repos.
- **Web UI:** CLI only.
- **Quizzes:** Exercises serve as the knowledge test.
- **Multi-language support:** English only (initially).
- **GUI:** No graphical interface.
