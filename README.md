# gitgym

An interactive CLI platform for learning git, inspired by [Rustlings](https://github.com/rust-lang/rustlings). Work through progressively harder exercises in real git repositories inside a safe, sandboxed workspace.

## Installation

```bash
pip install gitgym
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install gitgym
```

**Requires:** Python 3.12+ and git installed on your system.

## Quick Start

```bash
# See all exercises
gitgym list

# Set up and start the next exercise
gitgym next

# cd into the printed exercise directory, then run git commands
cd ~/.gitgym/exercises/01_basics/01_init

# Check your work
gitgym verify

# Or watch for changes automatically
gitgym watch
```

## Typical Workflow

1. Run `gitgym next` (or `gitgym start <exercise>`) to set up the exercise repo.
2. `cd` into the directory that gitgym prints.
3. Read the description with `gitgym describe`.
4. Run git commands in that directory to reach the goal state.
5. Run `gitgym verify` to check your work, or use `gitgym watch` for live feedback.
6. Move on to the next exercise.

## Commands

| Command                   | Description                                                |
| ------------------------- | ---------------------------------------------------------- |
| `gitgym list`             | List all exercises grouped by topic with completion status |
| `gitgym start [exercise]` | Set up an exercise repo (defaults to next incomplete)      |
| `gitgym next`             | Alias for `gitgym start` with no argument                  |
| `gitgym describe`         | Print the current exercise's description and goal          |
| `gitgym verify`           | Check if the current exercise's goal state is met          |
| `gitgym watch`            | Watch mode: auto re-verify on repo changes                 |
| `gitgym hint`             | Show the next progressive hint                             |
| `gitgym reset [exercise]` | Reset an exercise to its initial state                     |
| `gitgym reset --all`      | Reset all exercises and clear progress                     |
| `gitgym progress`         | Show overall progress summary                              |

## Exercises

gitgym ships with 32 exercises across 9 topics:

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

## Progressive Hints

Each exercise includes progressive hints. Call `gitgym hint` repeatedly to reveal them one at a time:

```
$ gitgym hint
Hint 1/3: Look at the `git init` command.

$ gitgym hint
Hint 2/3: Run `git init` inside the exercise directory.

$ gitgym hint
Hint 3/3: Just run: git init
(No more hints available.)
```

## Watch Mode

`gitgym watch` polls the exercise directory every second. Whenever you save a file or run a git command, it automatically re-runs verification and prints the result — no need to switch terminals.

```
$ gitgym watch
Watching for changes... (Ctrl+C to stop)
[11:02:34] Running verify...
  Goal not yet met: nothing staged for commit.
[11:02:41] Running verify...
  Correct! You staged the file.
```

## Data & Privacy

All exercise repos are stored in `~/.gitgym/exercises/`. Progress is tracked locally in `~/.gitgym/progress.json`. No data is sent anywhere.

## License

MIT
