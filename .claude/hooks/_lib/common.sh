#!/bin/bash
# Common utilities for Claude Code hooks
# Source this file at the top of your hook: source "$(dirname "$0")/_lib/common.sh"

set -euo pipefail

# Resolve paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$CLAUDE_DIR/logs"

# ─── Logging ──────────────────────────────────────────────────────────────

ensure_log_dir() {
    mkdir -p "$LOG_DIR"
}

log_info() {
    ensure_log_dir
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" >> "$LOG_DIR/${2:-hook}.log"
}

log_warn() {
    ensure_log_dir
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $1" >> "$LOG_DIR/${2:-hook}.log"
}

log_error() {
    ensure_log_dir
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "$LOG_DIR/${2:-hook}.log"
}

# ─── JSON Helpers ─────────────────────────────────────────────────────────

# Read a JSON field from stdin
json_read() {
    local field="$1"
    cat | jq -r "$field // empty" 2>/dev/null || echo ""
}

# Check if stdin is valid JSON
json_valid() {
    cat >/dev/null | jq -e . >/dev/null 2>&1
}

# ─── Event Data Parsing ───────────────────────────────────────────────────

# Read event data from stdin and extract common fields
parse_event() {
    local event_data
    event_data=$(cat)
    echo "$event_data"
}

# Extract the command from a Bash tool event
extract_bash_command() {
    local event_data="$1"
    echo "$event_data" | jq -r '.tool_input.command // ""' 2>/dev/null || echo ""
}

# Extract file path from Edit/Write event
extract_file_path() {
    local event_data="$1"
    echo "$event_data" | jq -r '.parameters.file_path // empty' 2>/dev/null || echo ""
}

# ─── Git Helpers ──────────────────────────────────────────────────────────

get_current_branch() {
    git branch --show-current 2>/dev/null || echo ""
}

is_protected_branch() {
    local branch="$1"
    local protected=("main" "master" "develop" "release")
    for p in "${protected[@]}"; do
        [[ "$branch" == "$p" ]] && return 0
    done
    return 1
}

# ─── Output Formatting ────────────────────────────────────────────────────

print_box() {
    local title="$1"
    local width=50
    printf '\n'
    printf '━%.0s' $(seq 1 $width)
    printf '\n  %s\n' "$title"
    printf '━%.0s' $(seq 1 $width)
    printf '\n\n'
}

block_tool() {
    local reason="$1"
    cat <<EOF
{"decision": "block", "reason": "$reason"}
EOF
}

# ─── Skill Rules ──────────────────────────────────────────────────────────

load_skill_rules() {
    local rules_file="$CLAUDE_DIR/hooks/skill-rules.json"
    if [ -f "$rules_file" ]; then
        cat "$rules_file"
    else
        echo "{}"
    fi
}

# ─── Validation ───────────────────────────────────────────────────────────

require_jq() {
    if ! command -v jq &>/dev/null; then
        echo "Error: jq is required but not installed" >&2
        exit 1
    fi
}

# ─── Initialization ───────────────────────────────────────────────────────

# Auto-require jq for all hooks that source this library
require_jq
