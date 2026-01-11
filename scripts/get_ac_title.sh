#!/bin/bash
# Quick AC-ID title lookup helper
# Usage: ./scripts/get_ac_title.sh AC-AUDIT-001

if [ -z "$1" ]; then
    echo "Usage: $0 AC-ID"
    echo "Example: $0 AC-AUDIT-001"
    exit 1
fi

AC_ID="$1"
AC_INDEX="cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"

if [ ! -f "$AC_INDEX" ]; then
    echo "Error: AC-INDEX.yaml not found at $AC_INDEX"
    exit 1
fi

# Extract title for the given AC-ID
title=$(grep -A 1 "id: ${AC_ID}" "$AC_INDEX" | grep "name:" | sed 's/.*name: //' | head -1)

if [ -z "$title" ]; then
    echo "AC-ID not found: $AC_ID"
    exit 1
fi

echo "$title"
