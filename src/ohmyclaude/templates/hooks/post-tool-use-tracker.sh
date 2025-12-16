#!/bin/bash
set -e

# Post-tool-use hook that tracks edited files and their repos
# This runs after Edit, MultiEdit, or Write tools complete successfully

# Set restrictive umask for created files
umask 077

CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$HOME/project}"

# Read tool information from stdin
tool_info=$(cat)

# Extract relevant data
tool_name=$(echo "$tool_info" | jq -r '.tool_name // empty')
session_id=$(echo "$tool_info" | jq -r '.session_id // "default"')

# Sanitize session_id to prevent path traversal / filesystem injection
session_id=$(echo "$session_id" | tr -cd 'A-Za-z0-9._-')
session_id=${session_id:0:64}
if [[ -z "$session_id" ]]; then
    session_id="default"
fi

# Skip if not an edit tool
if [[ ! "$tool_name" =~ ^(Edit|MultiEdit|Write)$ ]]; then
    exit 0
fi

# Collect file paths (support MultiEdit with multiple files)
mapfile -t file_paths < <(
    if [[ "$tool_name" == "MultiEdit" ]]; then
        echo "$tool_info" | jq -r '.tool_input.edits[].file_path // empty'
    else
        echo "$tool_info" | jq -r '.tool_input.file_path // empty'
    fi
)

# Skip if no file paths
if [[ ${#file_paths[@]} -eq 0 ]]; then
    exit 0
fi

# Create cache directory in project
cache_dir="$CLAUDE_PROJECT_DIR/.claude/tsc-cache/$session_id"
mkdir -p "$cache_dir"

# Function to detect repo from file path
detect_repo() {
    local file="$1"
    local project_root="$CLAUDE_PROJECT_DIR"

    # Remove project root from path
    local relative_path="${file#$project_root/}"

    # Extract first directory component
    local repo=$(echo "$relative_path" | cut -d'/' -f1)

    # Common project directory patterns
    case "$repo" in
        # Frontend variations
        frontend|client|web|app|ui)
            echo "$repo"
            ;;
        # Backend variations
        backend|server|api|src|services)
            echo "$repo"
            ;;
        # Database
        database|prisma|migrations)
            echo "$repo"
            ;;
        # Package/monorepo structure
        packages)
            # For monorepos, get the package name
            local package=$(echo "$relative_path" | cut -d'/' -f2)
            if [[ -n "$package" ]]; then
                echo "packages/$package"
            else
                echo "$repo"
            fi
            ;;
        # Examples directory
        examples)
            local example=$(echo "$relative_path" | cut -d'/' -f2)
            if [[ -n "$example" ]]; then
                echo "examples/$example"
            else
                echo "$repo"
            fi
            ;;
        *)
            # Check if it's a source file in root
            if [[ ! "$relative_path" =~ / ]]; then
                echo "root"
            else
                echo "unknown"
            fi
            ;;
    esac
}

# Function to get build command for repo
get_build_command() {
    local repo="$1"
    local project_root="$CLAUDE_PROJECT_DIR"
    local repo_path="$project_root/$repo"

    # Check if package.json exists and has a build script
    if [[ -f "$repo_path/package.json" ]]; then
        if grep -q '"build"' "$repo_path/package.json" 2>/dev/null; then
            # Detect package manager (prefer pnpm, then npm, then yarn)
            if [[ -f "$repo_path/pnpm-lock.yaml" ]]; then
                echo "cd $repo_path && pnpm build"
            elif [[ -f "$repo_path/package-lock.json" ]]; then
                echo "cd $repo_path && npm run build"
            elif [[ -f "$repo_path/yarn.lock" ]]; then
                echo "cd $repo_path && yarn build"
            else
                echo "cd $repo_path && npm run build"
            fi
            return
        fi
    fi

    # Special case for database with Prisma
    if [[ "$repo" == "database" ]] || [[ "$repo" =~ prisma ]]; then
        if [[ -f "$repo_path/schema.prisma" ]] || [[ -f "$repo_path/prisma/schema.prisma" ]]; then
            echo "cd $repo_path && npx prisma generate"
            return
        fi
    fi

    # No build command found
    echo ""
}

# Function to get TSC command for repo
get_tsc_command() {
    local repo="$1"
    local project_root="$CLAUDE_PROJECT_DIR"
    local repo_path="$project_root/$repo"

    # Check if tsconfig.json exists
    if [[ -f "$repo_path/tsconfig.json" ]]; then
        # Check for Vite/React-specific tsconfig
        if [[ -f "$repo_path/tsconfig.app.json" ]]; then
            echo "cd $repo_path && npx tsc --project tsconfig.app.json --noEmit"
        else
            echo "cd $repo_path && npx tsc --noEmit"
        fi
        return
    fi

    # No TypeScript config found
    echo ""
}

# Process each file path
for file_path in "${file_paths[@]}"; do
    # Skip empty paths
    [[ -z "$file_path" ]] && continue

    # Skip markdown files
    [[ "$file_path" =~ \.(md|markdown)$ ]] && continue

    # Detect repo
    repo=$(detect_repo "$file_path")

    # Skip if unknown repo
    [[ -z "$repo" || "$repo" == "unknown" ]] && continue

    # Log edited file: timestamp, tool, path (tab-delimited for TS reminder)
    printf "%s\t%s\t%s\n" "$(date +%s)" "$tool_name" "$file_path" >> "$cache_dir/edited-files.log"

    # Update affected repos list
    if ! grep -q "^$repo$" "$cache_dir/affected-repos.txt" 2>/dev/null; then
        echo "$repo" >> "$cache_dir/affected-repos.txt"
    fi

    # Store build/tsc commands once per repo
    build_cmd=$(get_build_command "$repo")
    tsc_cmd=$(get_tsc_command "$repo")

    [[ -n "$build_cmd" ]] && echo "$repo:build:$build_cmd" >> "$cache_dir/commands.txt.tmp"
    [[ -n "$tsc_cmd" ]] && echo "$repo:tsc:$tsc_cmd" >> "$cache_dir/commands.txt.tmp"
done

# Remove duplicates from commands
if [[ -f "$cache_dir/commands.txt.tmp" ]]; then
    sort -u "$cache_dir/commands.txt.tmp" > "$cache_dir/commands.txt"
    rm -f "$cache_dir/commands.txt.tmp"
fi

# Exit cleanly
exit 0