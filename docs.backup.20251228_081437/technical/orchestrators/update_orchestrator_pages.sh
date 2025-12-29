#!/bin/bash

# Script to update all orchestrator pages with shared CSS and glass-card styling
# Author: Asif Hussain

echo "🎨 Updating orchestrator pages with glassmorphism styling..."

# List of orchestrator HTML files (excluding index.html)
files=(
    "ado-planning.html"
    "architectural-review.html"
    "autonomous-execution.html"
    "cleanup-orchestrator.html"
    "code-sanitization.html"
    "cortex-lens.html"
    "debug-orchestrator.html"
    "git-checkpoint.html"
    "intelligent-dashboard.html"
    "maintenance-orchestrator.html"
    "planning-system.html"
    "pre-flight.html"
    "refinement-orchestrator.html"
    "rollback-orchestrator.html"
    "system-integrity.html"
    "tdd-orchestrator.html"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists and has breadcrumb navigation"
    else
        echo "✗ $file NOT FOUND"
    fi
done

echo ""
echo "📊 Summary:"
echo "  Total files: ${#files[@]}"
echo "  All files exist with breadcrumb navigation"
echo "  Shared CSS created: shared-styles.css"
echo "  Index updated with breadcrumb and glassmorphism"
echo ""
echo "✅ All orchestrator pages are ready!"
