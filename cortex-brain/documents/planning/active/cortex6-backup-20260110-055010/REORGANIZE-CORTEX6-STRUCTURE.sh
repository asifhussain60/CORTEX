#!/bin/bash
# CORTEX 6 Folder Reorganization Script
# Purpose: Consolidate 7 folders into clean intuitive structure
# Date: 2026-01-11
# Author: Asif Hussain

set -e  # Exit on error

CORTEX6_DIR="cortex-brain/documents/planning/active/cortex6"
cd "$CORTEX6_DIR" || exit 1

echo "🔄 CORTEX 6 Folder Reorganization"
echo "=================================="
echo ""

# Backup first
echo "📦 Creating backup..."
BACKUP_DIR="../cortex6-backup-$(date +%Y%m%d-%H%M%S)"
cp -r . "$BACKUP_DIR"
echo "   ✅ Backup created: $BACKUP_DIR"
echo ""

# Step 1: Create new structure
echo "📁 Creating new folder structure..."
mkdir -p requirements
mkdir -p execution/{phases,tracking,dashboard/static}
mkdir -p analysis
mkdir -p artifacts/completion-reports
mkdir -p summaries/stage-summaries
echo "   ✅ New folders created"
echo ""

# Step 2: Move canonical sources
echo "📋 Moving canonical sources to requirements/..."
if [ -f "acceptance-criteria/CX6-requirements.yaml" ]; then
    mv acceptance-criteria/CX6-requirements.yaml requirements/
    echo "   ✅ Moved CX6-requirements.yaml"
fi
if [ -f "acceptance-criteria/requirements/CX6-requirements.yaml" ]; then
    mv acceptance-criteria/requirements/CX6-requirements.yaml requirements/
    echo "   ✅ Moved CX6-requirements.yaml (from requirements/)"
fi
if [ -f "acceptance-criteria/CX6-acceptance-criteria.yaml" ]; then
    mv acceptance-criteria/CX6-acceptance-criteria.yaml requirements/
    echo "   ✅ Moved CX6-acceptance-criteria.yaml"
fi
echo ""

# Step 3: Move execution files
echo "🚀 Moving execution files..."
if [ -f "plan/config.yaml" ]; then
    mv plan/config.yaml execution/
    echo "   ✅ Moved config.yaml"
fi
if [ -d "plan/phases" ]; then
    mv plan/phases/* execution/phases/ 2>/dev/null || true
    echo "   ✅ Moved phase definitions"
fi
if [ -d "cortex6-planner/tracking" ]; then
    mv cortex6-planner/tracking/* execution/tracking/ 2>/dev/null || true
    echo "   ✅ Moved tracking files"
elif [ -d "tracking" ]; then
    mv tracking/* execution/tracking/ 2>/dev/null || true
    echo "   ✅ Moved tracking files (from root)"
fi
if [ -d "dashboard" ]; then
    mv dashboard/* execution/dashboard/ 2>/dev/null || true
    echo "   ✅ Moved dashboard files"
fi
echo ""

# Step 4: Move analysis files
echo "📊 Moving analysis files..."
if [ -d "acceptance-criteria/analysis" ]; then
    mv acceptance-criteria/analysis/* analysis/ 2>/dev/null || true
    echo "   ✅ Moved analysis from acceptance-criteria/"
fi
if [ -d "acceptance-criteria/strategies" ]; then
    mv acceptance-criteria/strategies/* analysis/ 2>/dev/null || true
    echo "   ✅ Moved strategies"
fi
if [ -d "cortex6-planner/analysis" ]; then
    mv cortex6-planner/analysis/* analysis/ 2>/dev/null || true
    echo "   ✅ Moved analysis from cortex6-planner/"
fi
if [ -d "analysis" ] && [ "$(ls -A old-analysis 2>/dev/null)" ]; then
    # If there's already an analysis folder, merge it
    cp -r old-analysis/* analysis/ 2>/dev/null || true
fi
echo ""

# Step 5: Move artifacts
echo "📦 Moving artifacts..."
if [ -d "artifacts" ]; then
    # Move YAML plans
    mv artifacts/*.yaml artifacts/ 2>/dev/null || true
    echo "   ✅ Moved YAML artifacts"
fi
if [ -d "cortex6-planner/artifacts" ]; then
    mv cortex6-planner/artifacts/* artifacts/ 2>/dev/null || true
    echo "   ✅ Moved artifacts from cortex6-planner/"
fi
echo ""

# Step 6: Move summaries
echo "📝 Moving summaries..."
if [ -d "acceptance-criteria/summaries" ]; then
    mv acceptance-criteria/summaries/* summaries/ 2>/dev/null || true
    echo "   ✅ Moved summaries from acceptance-criteria/"
fi
if [ -d "cortex6-planner/summaries" ]; then
    mv cortex6-planner/summaries/* summaries/ 2>/dev/null || true
    echo "   ✅ Moved summaries from cortex6-planner/"
fi
if [ -d "summaries" ] && [ "$(ls -A old-summaries 2>/dev/null)" ]; then
    cp -r old-summaries/* summaries/ 2>/dev/null || true
fi
if [ -f "acceptance-criteria/GAP-FIX-IMPROVEMENT-SUMMARY.md" ]; then
    mv acceptance-criteria/GAP-FIX-IMPROVEMENT-SUMMARY.md summaries/
    echo "   ✅ Moved GAP-FIX-IMPROVEMENT-SUMMARY.md"
fi
echo ""

# Step 7: Archive old structure
echo "🗄️ Archiving old folders..."
mkdir -p archive/old-structure-$(date +%Y%m%d)
[ -d "acceptance-criteria" ] && mv acceptance-criteria archive/old-structure-$(date +%Y%m%d)/ || true
[ -d "cortex6-planner" ] && mv cortex6-planner archive/old-structure-$(date +%Y%m%d)/ || true
[ -d "plan" ] && mv plan archive/old-structure-$(date +%Y%m%d)/ || true
[ -d "dashboard" ] && mv dashboard archive/old-structure-$(date +%Y%m%d)/ || true
[ -d "implementation-guides" ] && mv implementation-guides archive/old-structure-$(date +%Y%m%d)/ || true
echo "   ✅ Old folders archived"
echo ""

# Step 8: Clean up empty directories
echo "🧹 Cleaning up empty directories..."
find . -type d -empty -delete 2>/dev/null || true
echo "   ✅ Empty directories removed"
echo ""

echo "✅ REORGANIZATION COMPLETE"
echo ""
echo "📁 New structure:"
echo "   requirements/        - Canonical sources (2 files)"
echo "   execution/           - Active plan execution"
echo "   analysis/            - Planning artifacts"
echo "   artifacts/           - Generated deliverables"
echo "   summaries/           - Documentation"
echo "   archive/             - Historical artifacts"
echo ""
echo "💾 Backup location: $BACKUP_DIR"
echo ""
echo "⚠️  NEXT STEPS:"
echo "   1. Verify new structure: ls -la"
echo "   2. Update references in Gap-Fix prompt"
echo "   3. Update references in SOURCE-OF-TRUTH-README.md"
echo "   4. Test plan execution with new paths"
echo ""
