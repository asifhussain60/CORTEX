#!/bin/bash
# ============================================================================
# .temp/ Cleanup Script
# ============================================================================
# Authority: Phase 102 - Workflow Runtime Foundation
# Purpose: Auto-delete workflow instances older than 7 days
# Schedule: Run daily via cron or manually
# ============================================================================

TEMP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTANCES_DIR="$TEMP_DIR/instances"
MAX_AGE_DAYS=7

echo "=== Workflow Instance Cleanup ==="
echo "Directory: $INSTANCES_DIR"
echo "Max age: $MAX_AGE_DAYS days"
echo ""

# Find and delete instance files older than 7 days
find "$INSTANCES_DIR" -type f -name "*.yaml" -mtime +$MAX_AGE_DAYS -print -delete

echo ""
echo "Cleanup complete."
echo "Current instance count: $(find "$INSTANCES_DIR" -type f -name "*.yaml" | wc -l)"
