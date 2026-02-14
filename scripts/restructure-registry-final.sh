#!/bin/bash
# Final registry restructure - numbered phase folders at top level

set -e

REGISTRY_ROOT="cortex-registry/_cortex-master"
BACKUP_DIR="_workspaces/_backup-registry-final-$(date +%Y%m%d-%H%M%S)"

echo "🔧 Registry Restructure: Numbered Phases at Top Level"
echo ""

# Create backup
echo "📦 Creating backup: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -R "$REGISTRY_ROOT" "$BACKUP_DIR/"

cd "$REGISTRY_ROOT"

# Step 1: Convert phase YAML files to numbered folders
echo ""
echo "📂 Creating numbered phase folders from YAML files..."
for phase_file in work/phases/active/phase-*.yaml work/phases/active/phase-*.md; do
    if [ -f "$phase_file" ]; then
        filename=$(basename "$phase_file")
        
        # Extract phase number and name
        if [[ $filename =~ ^phase-([0-9]+)-(.+)\.(yaml|md)$ ]]; then
            phase_num="${BASH_REMATCH[1]}"
            phase_name="${BASH_REMATCH[2]}"
            
            # Create folder with number-name format
            folder_name="${phase_num}-${phase_name}"
            
            echo "  Creating: $folder_name/"
            mkdir -p "$folder_name"
            
            # Move file into folder and rename to spec.yaml or spec.md
            ext="${BASH_REMATCH[3]}"
            mv "$phase_file" "$folder_name/spec.$ext"
            
            # Create README.md for quick reference
            cat > "$folder_name/README.md" <<EOF
# Phase ${phase_num}: $(echo $phase_name | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2));}1')

**Status:** Active
**Location:** \`spec.$ext\`

---

See \`spec.$ext\` for full phase specification.
EOF
        fi
    fi
done

# Step 2: Create knowledge/ folder structure
echo ""
echo "📚 Organizing knowledge base..."
mkdir -p knowledge

# Move reference material
if [ -d "work/specifications" ]; then
    echo "  Moving: specifications → knowledge/specifications"
    mv work/specifications knowledge/ 2>/dev/null || true
fi

if [ -d "work/governance" ]; then
    echo "  Moving: governance → knowledge/governance"
    mv work/governance knowledge/ 2>/dev/null || true
fi

if [ -d "work/guides" ]; then
    echo "  Moving: guides → knowledge/guides"
    mv work/guides knowledge/ 2>/dev/null || true
fi

if [ -d "work/config" ]; then
    echo "  Moving: config → knowledge/config"
    mv work/config knowledge/ 2>/dev/null || true
fi

# Step 3: Keep archive/ as-is (already organized)
echo ""
echo "📦 Archive folder preserved"

# Step 4: Clean up old structure
echo ""
echo "🗑️  Removing old work/ and history/ folders..."
rm -rf work/
rm -rf history/

echo ""
echo "✅ Restructure complete!"
echo ""
echo "📊 New structure:"
echo ""
ls -1 | grep -E "^[0-9]" | head -20
echo ""
echo "📁 Knowledge folders:"
ls -1 knowledge/ 2>/dev/null || echo "  (none)"
echo ""
echo "✅ Done! Backup: $BACKUP_DIR"
