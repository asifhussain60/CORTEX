#!/bin/bash
# ============================================================================
# CORTEX YAML Reader Launcher
# ============================================================================
# Quick launcher script for the YAML Reader SPA
# Usage: ./launch-yaml-reader.sh
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
YAML_READER_PATH="$SCRIPT_DIR/.yaml-reader/index.html"

if [ ! -f "$YAML_READER_PATH" ]; then
    echo "❌ Error: YAML Reader not found at $YAML_READER_PATH"
    exit 1
fi

echo "🚀 Launching CORTEX YAML Reader..."
echo "📂 Location: $YAML_READER_PATH"
echo ""

# Open in default browser
open "$YAML_READER_PATH"

echo "✅ YAML Reader opened in browser"
echo ""
echo "💡 Tip: Drag & drop YAML files from cortex-registry/ to load them"
echo "   - Press '/' to search"
echo "   - Press 'Esc' to clear search"
echo "   - Try different views: Tree, Cards, Graph, Raw"
