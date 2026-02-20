# gitgym

[![PyPI version](https://img.shields.io/pypi/v/gitgym)](https://pypi.org/project/gitgym/)
[![Python](https://img.shields.io/pypi/pyversions/gitgym)](https://pypi.org/project/gitgym/)
[![CI](https://github.com/enerrio/gitgym/actions/workflows/ci.yml/badge.svg)](https://github.com/enerrio/gitgym/actions/workflows/ci.yml)

An interactive CLI for learning git through hands-on exercises, inspired by [Rustlings](https://github.com/rust-lang/rustlings). No quizzes — you practice real git commands in real repositories inside a safe, sandboxed workspace.

## Installation

```bash
pip install gitgym
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install gitgym
```

**Requirements:** Python 3.12+ and git. macOS and Linux only (Windows is not currently supported).

## Quick Start

```bash
gitgym list              # see all 32 exercises
gitgym next              # set up the next exercise
cd ~/.gitgym/exercises/01_basics/01_init   # cd into the printed path
# ... run git commands to solve the exercise ...
gitgym verify            # check your work
```

## Recommended Setup

Open **two terminal windows** (or tabs) side by side:

| Terminal 1 (work)                       | Terminal 2 (control)              |
| --------------------------------------- | --------------------------------- |
| `cd` into the exercise directory        | `gitgym describe` — read the goal |
| Run git commands to solve the exercise  | `gitgym hint` — get a hint        |
| Edit files, stage, commit, branch, etc. | `gitgym verify` — check your work |
|                                         | `gitgym watch` — live feedback    |

This keeps your git work separate from the gitgym CLI, just like a real workflow.

## Commands

| Command                   | Description                                                |
| ------------------------- | ---------------------------------------------------------- |
| `gitgym list`             | List all exercises grouped by topic with completion status |
| `gitgym start [exercise]` | Set up an exercise (defaults to next incomplete)           |
| `gitgym next`             | Alias for `gitgym start` with no argument                  |
| `gitgym describe`         | Print the current exercise's description and goal          |
| `gitgym verify`           | Check if the current exercise's goal state is met          |
| `gitgym watch`            | Auto re-verify on changes (Ctrl+C to stop)                 |
| `gitgym hint`             | Show the next progressive hint                             |
| `gitgym reset [exercise]` | Reset an exercise to its initial state                     |
| `gitgym reset --all`      | Reset all exercises and clear progress                     |
| `gitgym progress`         | Show overall progress summary                              |
| `gitgym clean`            | Remove all gitgym data from your system                    |

Exercise names are shown in `gitgym list` (e.g. `init`, `staging`, `amend`). Use these names with `gitgym start` and `gitgym reset`.

## Exercises

32 exercises across 9 topics, from beginner to advanced:

| Topic               | Exercises                                              |
| ------------------- | ------------------------------------------------------ |
| **Basics**          | init, staging, status, first_commit, gitignore         |
| **Committing**      | amend, multi_commit, diff                              |
| **Branching**       | create_branch, switch_branches, delete_branch          |
| **Merging**         | fast_forward, three_way_merge, merge_conflict          |
| **History**         | log_basics, log_graph, blame, show                     |
| **Undoing Changes** | restore_file, unstage, revert, reset_soft, reset_mixed |
| **Rebase**          | basic_rebase, interactive_rebase, rebase_conflict      |
| **Stashing**        | stash_basics, stash_pop_apply                          |
| **Advanced**        | cherry_pick, bisect, tags, aliases                     |

## Features

**Progressive hints** — Each exercise has multiple hints revealed one at a time:

```
$ gitgym hint
Hint 1/3: Look at the `git init` command.

$ gitgym hint
Hint 2/3: Run `git init` inside the exercise directory.
```

**Watch mode** — `gitgym watch` polls the exercise directory and re-verifies automatically whenever you make changes. No need to switch terminals to run verify.

**Progress tracking** — Your progress is saved locally in `~/.gitgym/progress.json`. Close your terminal and pick up where you left off. Run `gitgym progress` to see a per-topic breakdown.

**Cleanup** — When you're done, run `gitgym clean` to remove all exercise data from your system.

## Platform Support

gitgym works on **macOS** and **Linux**. Windows is not currently supported because exercises use bash shell scripts. Windows users can use [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) as a workaround.

## Contributing

Exercises follow a simple structure — each one is a directory with three files:

- `exercise.toml` — metadata, description, goal, and hints
- `setup.sh` — creates the initial repo state
- `verify.sh` — checks if the goal is met (exit 0 = pass)

See the `exercises/` directory for examples.
