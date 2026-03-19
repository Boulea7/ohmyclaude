#!/bin/bash
set -e

# Run relative to the hook bundle itself so the script also works
# when copied into plugin or extension bundles.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

cat | npx tsx skill-activation-prompt.ts
