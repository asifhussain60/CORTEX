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
        folder_name=$(basename "$phase_dir")
        if [[ $folder_name =~ ^([0-9]+)- ]]; then
            original_num="${BASH_REMATCH[1]}"
            phase_name=$(echo "$folder_name" | sed "s/^${original_num}-//" | sed 's/-$//')
            
            new_num=$(printf "%02d" $phase_counter)
            
            # Determine status
            if [ "$original_num" -le "48" ]; then
                status="completed"
            elif [ "$original_num" -ge "81" ]; then
                status="active"
            else
                status="deferred"
            fi
            
            echo "  Converting: $folder_name → phases/${new_num}-${phase_name}.yaml (status: $status)"
            
            if [ -f "${phase_dir}/spec.yaml" ]; then
                cp "${phase_dir}/spec.yaml" "phases/${new_num}-${phase_name}.yaml"
                # Add status if missing
                if ! grep -q "^status:" "phases/${new_num}-${phase_name}.yaml" 2>/dev/null; then
                    temp_file=$(mktemp)
                    echo "status: ${status}" > "$temp_file"
                    echo "original_phase_id: ${original_num}" >> "$temp_file"
                    cat "phases/${new_num}-${phase_name}.yaml" >> "$temp_file"
                    mv "$temp_file" "phases/${new_num}-${phase_name}.yaml"
                fi
            fi
            
            phase_counter=$((phase_counter + 1))
        fi
    fi
done

# Step 2: Create _views/ directory
echo ""
echo "📂 Step 2: Creating _views/ symlink structure..."
mkdir -p _views/{active,completed,deferred}

# Step 3: Generate symlinks
echo ""
echo "🔗 Step 3: Generating symlinks..."
for phase_file in phases/*.yaml; do
    if [ -f "$phase_file" ]; then
        filename=$(basename "$phase_file")
        status=$(grep "^status:" "$phase_file" | head -1 | awk '{print $2}' | tr -d '\r')
        
        case "$status" in
            active)
                ln -sf "../../phases/$filename" "_views/active/$filename"
                ;;
            completed)
                ln -sf "../../phases/$filename" "_views/completed/$filename"
                ;;
            deferred)
                ln -sf "../../phases/$filename" "_views/deferred/$filename"
                ;;
        esac
    fi
done

# Step 4: Generate master index
echo ""
echo "📊 Step 4: Generating master-index.yaml..."
active_count=$(ls -1 _views/active/*.yaml 2>/dev/null | wc -l | tr -d ' ')
completed_count=$(ls -1 _views/completed/*.yaml 2>/dev/null | wc -l | tr -d ' ')
deferred_count=$(ls -1 _views/deferred/*.yaml 2>/dev/null | wc -l | tr -d ' ')
total_count=$(ls -1 phases/*.yaml 2>/dev/null | wc -l | tr -d ' ')

cat > master-index.yaml <<EOF
# CORTEX Master Registry Index
# Auto-generated: 2026-02-14

metadata:
  total_phases: ${total_count}
  active: ${active_count}
  completed: ${completed_count}
  deferred: ${deferred_count}
  
# Regenerate: scripts/update-phase-views.sh
EOF

# Step 5: Clean up
echo ""
echo "🗑️ Cleaning up old folders..."
for phase_dir in [0-9]*-*/; do
    [ -d "$phase_dir" ] && rm -rf "$phase_dir"
done

echo ""
echo "✅ Complete! Stats: ${total_count} total | ${active_count} active | ${completed_count} completed | ${deferred_count} deferred"
