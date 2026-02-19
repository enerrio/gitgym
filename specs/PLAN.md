# gitgym - Implementation Plan

Each task is small and independently testable. Complete them in order; check off each box when done.

---

## Phase 1: Project Scaffolding

- [x] Initialize a `uv` project: run `uv init`, set up `pyproject.toml` with project metadata, Python >=3.12, `click` dependency, `[project.scripts] gitgym = "gitgym.cli:main"`, and hatchling build backend
- [x] Create the source package directory `src/gitgym/` with `__init__.py` (version string) and `__main__.py` (`from gitgym.cli import main; main()`)
- [x] Create `src/gitgym/config.py` with path constants: `WORKSPACE_DIR = ~/.gitgym/exercises/`, `PROGRESS_FILE = ~/.gitgym/progress.json`, `EXERCISES_DIR` (package-relative `exercises/` directory)
- [x] Create the empty `exercises/` directory at project root (will hold exercise definitions, shipped with the package)
- [x] Configure `pyproject.toml` so that `exercises/` is included in the built package (hatchling `[tool.hatch.build]` settings)
- [x] Run `uv sync` and verify `uv run gitgym --help` prints output without error

## Phase 2: Exercise Loading

- [x] Create `src/gitgym/exercise.py` with an `Exercise` dataclass: `name`, `topic`, `title`, `description`, `goal_summary`, `hints` (list of strings), `path` (path to exercise directory on disk)
- [x] Implement `load_exercise(exercise_dir: Path) -> Exercise` that reads `exercise.toml` from a directory and returns an `Exercise` instance
- [x] Implement `load_all_exercises() -> list[Exercise]` that discovers all `NN_topic/NN_exercise/` directories under `EXERCISES_DIR`, loads each, and returns them sorted by directory name
- [x] Write tests: create a temp directory with a sample `exercise.toml`, verify `load_exercise` parses all fields correctly
- [x] Write tests: create a temp tree with multiple topics/exercises, verify `load_all_exercises` returns them in order

## Phase 3: Progress Tracking

- [x] Create `src/gitgym/progress.py` with functions: `load_progress() -> dict`, `save_progress(data: dict)`, reading/writing `~/.gitgym/progress.json`
- [x] Implement `get_exercise_status(exercise_key: str) -> str` returning `"not_started"`, `"in_progress"`, or `"completed"`
- [x] Implement `mark_in_progress(exercise_key: str)` — sets status to `"in_progress"` with `started_at` timestamp
- [x] Implement `mark_completed(exercise_key: str)` — sets status to `"completed"` with `completed_at` timestamp
- [x] Implement `increment_hints_used(exercise_key: str)` — bumps the `hints_used` counter
- [x] Implement `reset_exercise_progress(exercise_key: str)` — removes the exercise entry from progress
- [x] Implement `reset_all_progress()` — deletes the progress file
- [x] Implement `get_current_exercise() -> str | None` — returns the key of the exercise currently `in_progress` (or `None`)
- [x] Write tests for each function using a temp file for progress.json

## Phase 4: Exercise Runner (setup & verify)

- [x] Create `src/gitgym/runner.py` with `run_setup(exercise: Exercise) -> bool` that runs `setup.sh` via `subprocess`, passing the workspace exercise path as `$1`; returns True on success
- [x] Implement `run_verify(exercise: Exercise) -> tuple[bool, str]` that runs `verify.sh`, captures stdout/stderr, returns `(success, output)`
- [x] Ensure both functions handle missing scripts, non-executable scripts, and non-zero exit codes gracefully with clear error messages
- [x] Write tests: create a trivial setup.sh and verify.sh in a temp dir, confirm `run_setup` creates expected files and `run_verify` returns correct pass/fail

## Phase 5: Display Helpers

- [x] Create `src/gitgym/display.py` with helper functions for formatted terminal output: `print_success(msg)`, `print_error(msg)`, `print_info(msg)`, `print_exercise_header(exercise)` using click styling
- [x] Implement `print_exercise_list(exercises, progress)` — formats the grouped exercise list with completion indicators
- [x] Implement `print_progress_summary(exercises, progress)` — prints overall stats (completed / total, per-topic breakdown)

## Phase 6: CLI Commands (Core)

- [x] Create `src/gitgym/cli.py` with a `click.Group` named `main` and a git-installed check that runs before any command
- [x] Implement `gitgym list` — calls `load_all_exercises()`, loads progress, delegates to `print_exercise_list`
- [x] Implement `gitgym start [exercise]` — if name given, set up that exercise; if not, find next incomplete exercise; run `setup.sh`, mark `in_progress`, print the exercise path and description
- [x] Implement `gitgym next` — alias for `gitgym start` with no argument
- [x] Implement `gitgym describe` — find the current in-progress exercise, print its description and goal
- [x] Implement `gitgym verify` — find the current exercise, run `verify.sh`, print result, mark completed on success
- [x] Implement `gitgym hint` — find the current exercise, read `hints_used` from progress, show the next hint, increment counter
- [x] Implement `gitgym reset` / `gitgym reset <exercise>` — re-run `setup.sh`, reset progress entry
- [x] Implement `gitgym reset --all` — delete workspace and progress, print confirmation
- [x] Implement `gitgym progress` — load exercises and progress, delegate to `print_progress_summary`
- [x] Write CLI integration tests: invoke each command via `click.testing.CliRunner` with a temp workspace

## Phase 7: Watch Mode

- [x] Create `src/gitgym/watcher.py` with a polling-based `watch(exercise)` loop that checks mtime of files in the exercise directory every 1 second
- [x] On detected change, run `verify.sh` and display the result; on success, mark completed and stop
- [x] Implement `gitgym watch` CLI command that starts watch mode for the current exercise
- [x] Add optional `watchdog`-based implementation behind a try/except import, falling back to polling
- [x] Write tests: modify a file in a temp exercise dir, verify the watcher detects the change

## Phase 8: Error Handling & Edge Cases

- [x] Add startup check for `git` binary availability; print install instructions if missing
- [x] Handle "no exercise in progress" for `describe`, `verify`, `hint`, `watch` with a helpful message
- [x] Handle corrupted/missing exercise repo (suggest `gitgym reset`)
- [x] Handle setup.sh failure (print stderr, suggest filing a bug)
- [x] Handle verify.sh unexpected crash vs. normal failure (distinguish script error from goal-not-met)

## Phase 9: First Exercise Set (01_basics)

- [x] Create `exercises/01_basics/01_init/` with `exercise.toml`, `setup.sh` (creates dir with a file, no git repo), `verify.sh` (checks `.git/` exists)
- [x] Create `exercises/01_basics/02_staging/` — setup creates a repo with an untracked file; verify checks the file is staged
- [x] Create `exercises/01_basics/03_status/` — setup creates a repo with mixed tracked/untracked/modified files; verify checks specific files are staged
- [x] Create `exercises/01_basics/04_first_commit/` — setup creates a repo with staged files; verify checks for at least one commit with a non-empty message
- [x] Create `exercises/01_basics/05_gitignore/` — setup creates a repo with files that should be ignored; verify checks `.gitignore` exists and specified files are excluded
- [x] Test each exercise end-to-end: run setup.sh, perform the expected git actions, run verify.sh, confirm exit 0

## Phase 10: Remaining Exercises (02–09)

- [x] Create `exercises/02_committing/` exercises (amend, multi_commit, diff) with setup/verify scripts
- [x] Create `exercises/03_branching/` exercises (create_branch, switch_branches, delete_branch)
- [x] Create `exercises/04_merging/` exercises (fast_forward, three_way_merge, merge_conflict)
- [x] Create `exercises/05_history/` exercises (log_basics, log_graph, blame, show)
- [x] Create `exercises/06_undoing/` exercises (restore_file, unstage, revert, reset_soft, reset_mixed)
- [x] Create `exercises/07_rebase/` exercises (basic_rebase, interactive_rebase, rebase_conflict)
- [x] Create `exercises/08_stashing/` exercises (stash_basics, stash_pop_apply)
- [ ] Create `exercises/09_advanced/` exercises (cherry_pick, bisect, tags, aliases)
- [ ] Test every exercise end-to-end: setup → solve → verify

## Phase 11: Packaging & Distribution

- [ ] Verify `uv build` produces a working wheel/sdist that includes `exercises/`
- [ ] Test install from wheel in a clean venv: `pip install dist/*.whl && gitgym list`
- [ ] Add a `README.md` for PyPI with usage instructions
- [ ] Ensure `gitgym --version` prints the version from `pyproject.toml`
