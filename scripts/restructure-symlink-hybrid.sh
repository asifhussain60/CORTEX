#!/bin/bash
# Registry restructure: Symlink hybrid with phases/ + _views/ + master-index.yaml

set -e

REGISTRY_ROOT="cortex-registry/_cortex-master"
BACKUP_DIR="_workspaces/_backup-registry-symlink-$(date +%Y%m%d-%H%M%S)"

echo "🔧 Registry Restructure: Symlink Hybrid (Option A)"
echo ""

# Create backup
echo "📦 Creating backup: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -R "$REGISTRY_ROOT" "$BACKUP_DIR/"

cd "$REGISTRY_ROOT"

# Step 1: Create phases/ directory and convert folders to YAMLs
echo ""
echo "📂 Step 1: Converting phase folders to YAML files in phases/..."
mkdir -p phases

phase_counter=1
for phase_dir in [0-9]*-*/; do
    if [ -d "$phase_dir" ]; then
        # Extract original phase number from folder name
        folder_name=$(basename "$phase_dir")
        if [[ $folder_name =~ ^([0-9]+)- ]]; then
            original_num="${BASH_REMATCH[1]}"
            phase_name=$(echo "$folder_name" | sed "s/^${original_num}-//" | sed 's/-$//')
            
            # Use sequential numbering for new structure
            new_num=$(printf "%02d" $phase_counter)
            
            # Determine status based on original phase number
            if [ "$original_num" -le "48" ]; then
                status="completed"
            elif [ "$original_num" -ge "81" ]; then
                status="active"
            else
                status="deferred"
            fi
            
            echo "  Converting: $folder_name → phases/${new_num}-${phase_name}.yaml (status: $status)"
            
            # Check if spec.yaml or spec.md exists
            if [ -f "${phase_dir}/spec.yaml" ]; then
                cp "${phase_dir}/spec.yaml" "phases/${new_num}-${phase_name}.yaml"
            elif [ -f "${phase_dir}/spec.md" ]; then
                # Convert MD to YAML metadata + content
                cat > "phases/${new_num}-${phase_name}.yaml" <<EOF
phase: ${new_num}
name: $(echo $phase_name | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2));}1')
status: ${status}
original_phase_id: ${original_num}
created: 2026-02-14
priority: medium

# Converted from spec.md
# See archive for original markdown content
EOF
            fi
            
            # Add status metadata if not present
            if ! grep -q "^status:" "phases/${new_num}-${phase_name}.yaml" 2>/dev/null; then
                # Prepend status to YAML
                temp_file=$(mktemp)
                echo "status: ${status}" > "$temp_file"
                echo "original_phase_id: ${original_num}" >> "$temp_file"
                cat "phases/${new_num}-${phase_name}.yaml" >> "$temp_file"
                mv "$temp_file" "phases/${new_num}-${phase_name}.yaml"
            fi
            
            phase_counter=$((phase_counter + 1))
        fi
    fi
done

# Step 2: Create _views/ directory structure
echo ""
echo "📂 Step 2: Creating _views/ symlink structure..."
mkdir -p _views/{active,completed,deferred}

# Step 3: Generate symlinks based on status field
echo ""
echo "🔗 Step 3: Generating symlinks based on status fields..."
for phase_file in phases/*.yaml; do
    if [ -f "$phase_file" ]; then
        filename=$(basename "$phase_file")
        status=$(grep "^status:" "$phase_file" | awk '{print $2}' | tr -d '\r')
        
        if [ -n "$status" ]; then
            case "$status" in
                active)
                    echo "  Linking: $filename → _views/active/"
                    ln -sf "../../phases/$filename" "_views/active/$filename"
                    ;;
                completed)
                    echo "  Linking: $filename → _views/completed/"
                    ln -sf "../../phases/$filename" "_views/completed/$filename"
                    ;;
                deferred)
                    echo "  Linking: $filename → _views/deferred/"
                    ln -sf "../../phases/$filename" "_views/deferred/$filename"
                    ;;
            esac
        fi
    fi
done

# Step 4: Generate master-index.yaml
echo ""
echo "📊 Step 4: Generating master-index.yaml..."
cat > master-index.yaml <<'EOF'
# CORTEX Master Registry Index
# Auto-generated from phases/*.yaml
# Last updated: 2026-02-14T11:30:00Z

metadata:
  version: 1.0
  structure: symlink-hybrid
  source_directory: phases/
  view_directories: _views/{active,completed,deferred}/
  
status_summary:
EOF

active_count=$(ls -1 _views/active/*.yaml 2>/dev/null | wc -l | tr -d ' ')
completed_count=$(ls -1 _views/completed/*.yaml 2>/dev/null | wc -l | tr -d ' ')
deferred_count=$(ls -1 _views/deferred/*.yaml 2>/dev/null | wc -l | tr -d ' ')
total_count=$(ls -1 phases/*.yaml 2>/dev/null | wc -l | tr -d ' ')

cat >> master-index.yaml <<EOF
  total_phases: ${total_count}
  active: ${active_count}
  completed: ${completed_count}
  deferred: ${deferred_count}

phases:
EOF

# Add phase entries
for phase_file in phases/*.yaml; do
    if [ -f "$phase_file" ]; then
        filename=$(basename "$phase_file" .yaml)
        phase_num=$(echo "$filename" | grep -oE '^[0-9]+')
        phase_name=$(echo "$filename" | sed 's/^[0-9]*-//' | sed 's/-/ /g')
        status=$(grep "^status:" "$phase_file" | awk '{print $2}' | tr -d '\r')
        
        cat >> master-index.yaml <<EOF
  - id: ${phase_num}
    name: ${phase_name}
    status: ${status}
    file: phases/${filename}.yaml
EOF
    fi
done

cat >> master-index.yaml <<'EOF'

# Quick Navigation:
# - Browse by status: _views/{active,completed,deferred}/
# - All phases: phases/
# - Regenerate views: scripts/update-phase-views.sh
EOF

echo ""
echo "✅ Step 5: Cleaning up old structure..."
for phase_dir in [0-9]*-*/; do
    if [ -d "$phase_dir" ]; then
        rm -rf "$phase_dir"
    fi
done

echo ""
echo "✅ Restructure complete!"
echo ""
echo "📊 Final Statistics:"
echo "  Total phases: ${total_count}"
echo "  Active: ${active_count}"
echo "  Completed: ${completed_count}"
echo "  Deferred: ${deferred_count}"
echo ""
echo "📁 Structure:"
echo "  phases/          → ${total_count} YAML files (source of truth)"
echo "  _views/active/   → ${active_count} symlinks"
echo "  _views/completed/→ ${completed_count} symlinks"
echo "  _views/deferred/ → ${deferred_count} symlinks"
echo "  master-index.yaml → Auto-generated index"
echo ""
echo "✅ Done! Backup: $BACKUP_DIR"
