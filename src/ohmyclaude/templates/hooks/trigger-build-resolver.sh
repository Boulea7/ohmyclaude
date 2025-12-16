#!/bin/bash
set -e

# Set restrictive umask for created files (always, not just in DEBUG mode)
umask 077

CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$HOME/project}"
DEBUG="${OHMYCLAUDE_HOOK_DEBUG:-0}"
hook_input=$(cat || true)

log_file=""
if [[ "$DEBUG" == "1" ]]; then
    log_dir="$CLAUDE_PROJECT_DIR/.claude"
    mkdir -p "$log_dir"
    log_file="$log_dir/hook-debug.log"
    {
        echo "Hook triggered at $(date)"
        echo "Args: $*"
        echo "Stdin:"
        echo "$hook_input"
        echo "=== DEBUG SECTION ==="
        echo "CLAUDE_PROJECT_DIR: $CLAUDE_PROJECT_DIR"
        echo "Current working directory: $(pwd)"
    } >> "$log_file"
fi

# Define the service directories to check
services_dirs=("email" "exports" "form" "frontend" "projects" "uploads" "users" "utilities" "events" "database")
services_with_changes=()

# Check each service directory for git changes
for service in "${services_dirs[@]}"; do
    service_path="$CLAUDE_PROJECT_DIR/$service"
    if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
        echo "Checking service: $service at $service_path" >> "$log_file"
    fi

    # Check if directory exists and is a git repo
    if [ -d "$service_path" ] && [ -d "$service_path/.git" ]; then
        if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
            echo "  -> Is a git repository" >> "$log_file"
        fi

        # Check for changes in this specific repo
        cd "$service_path"
        git_status=$(git status --porcelain 2>/dev/null)

        if [ -n "$git_status" ]; then
            if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
                echo "  -> Has changes:" >> "$log_file"
                echo "$git_status" | sed 's/^/    /' >> "$log_file"
            fi
            services_with_changes+=("$service")
        else
            if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
                echo "  -> No changes" >> "$log_file"
            fi
        fi
    else
        if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
            echo "  -> Not a git repository or doesn't exist" >> "$log_file"
        fi
    fi
done

# Return to original directory
cd "$CLAUDE_PROJECT_DIR"

if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
    echo "Services with changes: ${services_with_changes[@]}" >> "$log_file"
fi

if [[ ${#services_with_changes[@]} -gt 0 ]]; then
    services_list=$(IFS=', '; echo "${services_with_changes[*]}")
    if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
        echo "Changes detected in: $services_list — triggering build-error-resolver..." >> "$log_file"
    fi
    echo "Changes detected in: $services_list — triggering build-error-resolver..." >&2

    if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
        echo "Attempting to run claude with sub-agent..." >> "$log_file"
    fi

    # Try different possible syntaxes for sub-agents
    if command -v claude >/dev/null 2>&1; then
        # Option 1: Try direct agent invocation
        if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
            claude --agent build-error-resolver <<EOF 2>> "$log_file"
Build and fix errors in these specific services only: ${services_list}

Focus on these services in the monorepo structure. Each service has its own build process.
EOF
        else
            claude --agent build-error-resolver <<EOF >/dev/null 2>&1 || true
Build and fix errors in these specific services only: ${services_list}
EOF
        fi

        # If that fails, try alternative syntax
        if [ $? -ne 0 ]; then
            if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
                echo "First attempt failed, trying alternative syntax..." >> "$log_file"
                claude chat "Use the build-error-resolver agent to build and fix errors in: ${services_list}" 2>> "$log_file"
            else
                claude chat "Use the build-error-resolver agent to build and fix errors in: ${services_list}" >/dev/null 2>&1 || true
            fi
        fi
    else
        if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
            echo "Claude CLI not found in PATH" >> "$log_file"
        fi
    fi

    if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
        echo "Claude command completed with exit code: $?" >> "$log_file"
    fi
else
    if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
        echo "No services with changes detected — skipping build-error-resolver." >> "$log_file"
    fi
    echo "No services with changes detected — skipping build-error-resolver." >&2
fi

if [[ "$DEBUG" == "1" && -n "$log_file" ]]; then
    echo "=== END DEBUG SECTION ===" >> "$log_file"
fi
exit 0