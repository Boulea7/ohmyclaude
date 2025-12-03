#!/bin/bash
# OhMyClaude Post-Tool-Use Tracker
#
# This hook runs after Edit/Write tools to track edited files.
# Useful for build systems and change tracking.
#
# Based on: claude-code-infrastructure-showcase
# Adapted for: OhMyClaude with simplified logic

set -euo pipefail

# Read tool information from stdin
tool_info=$(cat)

# Extract relevant data using jq
tool_name=$(echo "$tool_info" | jq -r '.tool_name // empty')
file_path=$(echo "$tool_info" | jq -r '.tool_input.file_path // empty')
session_id=$(echo "$tool_info" | jq -r '.session_id // empty')

# Skip if not an edit tool or no file path
if [[ ! "$tool_name" =~ ^(Edit|MultiEdit|Write)$ ]] || [[ -z "$file_path" ]]; then
    exit 0
fi

# Sanitize inputs to prevent path traversal
file_path=$(realpath -m "$file_path" 2>/dev/null || echo "$file_path")
session_id=$(echo "$session_id" | tr -cd '[:alnum:]-_')

# Skip markdown and documentation files
if [[ "$file_path" =~ \.(md|markdown|txt|rst)$ ]]; then
    exit 0
fi

# Create cache directory
cache_dir="${CLAUDE_PROJECT_DIR:-.}/.claude/edit-cache/${session_id:-default}"
mkdir -p "$cache_dir"

# Log edited file with timestamp
echo "$(date +%s):$file_path" >> "$cache_dir/edited-files.log"

# Track file extensions for potential build triggers
ext="${file_path##*.}"
case "$ext" in
    py)
        echo "python" >> "$cache_dir/affected-types.txt"
        ;;
    ts|tsx|js|jsx)
        echo "typescript" >> "$cache_dir/affected-types.txt"
        ;;
    json)
        echo "config" >> "$cache_dir/affected-types.txt"
        ;;
    yaml|yml)
        echo "config" >> "$cache_dir/affected-types.txt"
        ;;
esac

# Remove duplicates
if [[ -f "$cache_dir/affected-types.txt" ]]; then
    sort -u "$cache_dir/affected-types.txt" -o "$cache_dir/affected-types.txt"
fi

exit 0
