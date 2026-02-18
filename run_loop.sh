#!/bin/bash
# run_loop.sh — Ralph Wiggum Loop with monitoring
# Usage: ./run_loop.sh [max_iterations]
# Set AGENT=codex or AGENT=claude (default) before running.
#
# Examples:
#   ./run_loop.sh                    # Claude Code, 10 iterations
#   AGENT=codex ./run_loop.sh 25     # Codex CLI, 25 iterations
#   AGENT=claude ./run_loop.sh 5     # Claude Code, 5 iterations

set -euo pipefail
# set -e  → exit immediately if any command fails
# set -u  → treat unset variables as errors (catches typos)
# set -o pipefail → if any command in a pipe fails, the whole pipe fails
#                    (without this, only the LAST command's exit code matters,
#                     so a failure in `claude` could be silently swallowed by `tee`)

# --- Configuration ---
AGENT="${AGENT:-claude}"           # "claude" or "codex"
MAX_ITERATIONS=${1:-10}
# First command-line argument, or default to 10.
# Usage: ./run_loop.sh 25  → sets max to 25

STUCK_THRESHOLD=3
# How many consecutive iterations with NO change to PLAN.md before we bail.
# This is the "circuit breaker" — if the agent keeps running but never
# checks off a task, something is wrong.

SLEEP_BETWEEN=5
# Seconds to pause between iterations. Gives you a window to Ctrl+C,
# and avoids hammering the API if something goes wrong.

PROMPT_FILE="prompt.md"
PLAN_FILE="specs/PLAN.md"

# --- Validate agent choice ---
if [[ "$AGENT" != "claude" && "$AGENT" != "codex" ]]; then
  echo "ERROR: AGENT must be 'claude' or 'codex'. Got: $AGENT"
  exit 1
fi

# --- Check dependencies ---
if ! command -v "$AGENT" &>/dev/null; then
  echo "ERROR: '$AGENT' CLI not found. Is it installed and on your PATH?"
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "ERROR: 'jq' not found. Install it (e.g. brew install jq) to enable simple log extraction."
  exit 1
fi

if [ ! -f "$PROMPT_FILE" ]; then
  echo "ERROR: $PROMPT_FILE not found."
  exit 1
fi

if [ ! -f "$PLAN_FILE" ]; then
  echo "ERROR: $PLAN_FILE not found. Run spec/plan generation first."
  exit 1
fi

# --- Logging setup ---
LOG_DIR="logs"
mkdir -p "$LOG_DIR"
RUN_ID=$(date +%Y%m%d_%H%M%S)
# RUN_ID is a timestamp like "20260217_143052" — unique per run.
# This means you can run the loop multiple times and logs don't collide.

LOG_FILE="$LOG_DIR/run_${RUN_ID}.log"
# Human-readable log: logs/run_20260217_143052.log

JSON_DIR="$LOG_DIR/run_${RUN_ID}_json"
mkdir -p "$JSON_DIR"
# Each iteration's raw JSON output gets its own file:
# logs/run_20260217_143052_json/iteration_1.json
# logs/run_20260217_143052_json/iteration_2.json
# This lets you parse cost, tokens, errors per-iteration after the fact.

SIMPLE_DIR="$LOG_DIR/run_${RUN_ID}_simple_json"
mkdir -p "$SIMPLE_DIR"
# Simplified per-iteration JSON containing only:
#   - assistant text messages
#   - tool calls that touched PLAN.md
# Much easier to read than the raw verbose output.
# logs/run_20260217_143052_simple_json/iteration_1.json

iteration=0
stuck_count=0
last_plan_hash=""
# State variables. last_plan_hash tracks the md5 of PLAN.md so we can
# detect when an iteration didn't actually change anything.

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
# Helper function. Prints to terminal AND appends to the log file.
# tee -a = append mode (doesn't overwrite).

# --- Simple log extractor ---
extract_simple_log() {
  local iter=$1
  local json_file="$JSON_DIR/iteration_${iter}.json"
  local simple_file="$SIMPLE_DIR/iteration_${iter}.json"

  if [ ! -f "$json_file" ]; then
    log "WARNING: No JSON file found for iteration $iter, skipping extraction."
    return
  fi

  # Claude Code --output-format=json --verbose produces a top-level JSON ARRAY
  # of event objects. Each event has a .type field. The main types are:
  #
  #   "system"    → init metadata (tools list, model, session_id, etc.)
  #   "assistant" → a message from the model; content lives at .message.content[]
  #   "user"      → a user turn (tool results, etc.)
  #   "result"    → final summary (cost, duration, etc.)
  #
  # Assistant content blocks each have a .type:
  #   "text"     → plain assistant text
  #   "tool_use" → a tool call; .name is the tool name, .input has arguments
  #
  # Tool names in Claude Code (capitalized, unlike the API):
  #   "Edit"   → targeted find-and-replace; input has .file_path, .old_string, .new_string
  #   "Write"  → full file write;            input has .file_path, .content
  #
  # To inspect the raw schema yourself:
  #   cat logs/run_<id>_json/iteration_1.json | jq '.[1]'   # first assistant event

  jq --arg iter "$iter" --arg plan "$PLAN_FILE" '{
    iteration: ($iter | tonumber),

    assistant_messages: [
      .[]
      | select(.type == "assistant")
      | .message.content[]?
      | select(.type == "text")
      | .text
    ],

    plan_edits: [
      .[]
      | select(.type == "assistant")
      | .message.content[]?
      | select(.type == "tool_use")
      | select(.name == "Edit" or .name == "Write")
      | select(
          # .input.file_path is the field Claude Code uses (not .input.path)
          (.input.file_path? // "") | test("PLAN\\.md$")
        )
      | {
          tool: .name,
          path: .input.file_path,
          # Edit uses old_string / new_string
          old_string: (.input.old_string // null),
          new_string: (.input.new_string // null),
          # Write uses content
          content:    (.input.content    // null)
        }
    ]
  }' "$json_file" > "$simple_file" 2>/dev/null \
    && log "Simple log written: $simple_file" \
    || log "WARNING: jq failed to parse $json_file — simple log skipped for iteration $iter."
}

# --- Agent runner function ---
run_agent() {
  local iter=$1
  local json_file="$JSON_DIR/iteration_${iter}.json"

  case "$AGENT" in
    claude)
      # cat prompt.md        → feeds the prompt file to stdin
      # claude --print       → run non-interactively, print output to stdout
      # --dangerously-skip-permissions → don't ask "is it ok to edit this file?"
      #                                  (required for unattended loops)
      # --output-format=json → structured output (cost, tokens, etc.)
      # --verbose            → include tool calls and reasoning in output
      # 2>&1                 → merge stderr into stdout (captures warnings too)
      # tee ...json          → write to the per-iteration JSON file AND...
      # >> "$LOG_FILE"       → also append to the main log
      cat "$PROMPT_FILE" | claude --print \
        --model sonnet \
        --dangerously-skip-permissions \
        --output-format=json \
        --verbose 2>&1 \
        | tee "$json_file" >> "$LOG_FILE"
      ;;
    codex)
      # Codex CLI doesn't support JSON output natively,
      # so we capture stdout and wrap it ourselves.
      local prompt_content
      prompt_content=$(cat "$PROMPT_FILE")

      codex exec --full-auto --json - < "$PROMPT_FILE" 2>&1 \
        | tee "$json_file" >> "$LOG_FILE"

      # Note: $json_file will contain plain text, not structured JSON.
      # If you need structured output from Codex, you'd need to parse
      # its stdout or use its API directly.
      ;;
  esac
}

# --- Main loop ---
log "Starting loop run $RUN_ID"
log "Agent: $AGENT | Max iterations: $MAX_ITERATIONS | Stuck threshold: $STUCK_THRESHOLD"

while true; do
  iteration=$((iteration + 1))
  # Bash arithmetic. Increments the counter.

  # --- Exit condition 1: All tasks done ---
  # Matches both "[ ]" and "[]"
  if ! grep -qE '\[[ ]?\]' "$PLAN_FILE"; then
    # grep -q = quiet mode (just check, don't print)
    # -E = use Extended Regular Expressions (ERE)
    #      allows regex operators like ?, +, |, () without backslashes
    # '\[[ ]?\]'  = regex pattern:
    #   \[        = literal "[" (escaped because [ starts a character class in regex)
    #   [ ]?      = a single space, OPTIONAL (the ? makes it 0 or 1 occurrences)
    #   \]        = literal "]"
    #
    # So this matches:
    #   "[]"      (no space)
    #   "[ ]"     (space inside — typical unchecked markdown checkbox)
    #
    # The leading "!" negates the exit code:
    #   grep returns 0 if it finds a match
    #   grep returns 1 if it does NOT find a match
    #   "!" flips that logic
    log "ALL TASKS COMPLETE after $((iteration - 1)) iterations"
    break
  fi

  # --- Exit condition 2: Runaway protection ---
  if [ "$iteration" -gt "$MAX_ITERATIONS" ]; then
    log "HIT MAX ITERATIONS ($MAX_ITERATIONS)"
    break
  fi

  # --- Stuck detection ---
  current_hash=$(md5sum "$PLAN_FILE" | cut -d' ' -f1)
  # md5sum outputs: "a1b2c3d4...  specs/PLAN.md"
  # cut -d' ' -f1 = split on space, take the first field (just the hash)

  if [ -n "$last_plan_hash" ] && [ "$current_hash" = "$last_plan_hash" ]; then
    # PLAN.md didn't change since last iteration → agent didn't complete a task
    stuck_count=$((stuck_count + 1))
    log "WARNING: No progress detected ($stuck_count/$STUCK_THRESHOLD)"
    if [ "$stuck_count" -ge "$STUCK_THRESHOLD" ]; then
      # Three iterations with no progress = something is broken.
      # Maybe the agent is failing tests, maybe the task is too ambiguous,
      # maybe it's editing the wrong files.
      log "STUCK — stopping loop. Investigate and restart."
      break
    fi
  else
    stuck_count=0  # Progress was made, reset the counter
  fi
  last_plan_hash="$current_hash"

  # --- Run iteration ---
  remaining=$(grep -c '\[ \]' "$PLAN_FILE" || true)
  # grep -c = count matching lines
  # || true = don't let set -e kill us if grep finds 0 matches (exit code 1)
  log "--- Iteration $iteration | Tasks remaining: $remaining ---"

  run_agent "$iteration"
  extract_simple_log "$iteration"
  # Runs immediately after the agent finishes so the JSON file is fresh.
  # Produces logs/run_<id>_simple_json/iteration_<n>.json with only the
  # assistant's text and any edits it made to PLAN.md.

  # --- Post-iteration audit ---
  if git rev-parse --is-inside-work-tree &>/dev/null; then
    latest_commit=$(git log --oneline -1 2>/dev/null || echo "(no commits)")
    # Log the most recent commit message so you can see what the agent did.
    # 2>/dev/null || true = suppress errors if no commits exist yet.
    log "Latest commit: $latest_commit"
  fi

  log "--- Iteration $iteration complete ---"
  sleep "$SLEEP_BETWEEN"
done

# --- Summary ---
completed=$(grep -c '\[x\]' "$PLAN_FILE" || true)
remaining=$(grep -c '\[ \]' "$PLAN_FILE" || true)
log "=========================================="
log "Run $RUN_ID finished"
log "Agent: $AGENT"
log "Iterations: $((iteration - 1))"
log "Tasks completed: $completed | Tasks remaining: $remaining"
log "Logs: $LOG_FILE"
log "JSON dir: $JSON_DIR"
log "Simple JSON dir: $SIMPLE_DIR"
log "=========================================="