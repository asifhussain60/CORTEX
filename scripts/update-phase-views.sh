#!/bin/bash
# Update _views/ symlinks based on status fields in phases/*.yaml

cd "$(dirname "$0")/../cortex-registry/_cortex-master" || exit 1

echo "🔄 Updating phase views..."

# Remove old symlinks
rm -f _views/active/*.yaml _views/completed/*.yaml _views/deferred/*.yaml

# Regenerate symlinks
for phase_file in phases/*.yaml; do
    if [ -f "$phase_file" ]; then
        filename=$(basename "$phase_file")
        status=$(grep "^status:" "$phase_file" | head -1 | awk '{print $2}' | tr -d '\r')
        
        case "$status" in
            active) ln -sf "../../phases/$filename" "_views/active/$filename" ;;
            completed) ln -sf "../../phases/$filename" "_views/completed/$filename" ;;
            deferred) ln -sf "../../phases/$filename" "_views/deferred/$filename" ;;
        esac
    fi
done

# Update master index
total=$(ls -1 phases/*.yaml 2>/dev/null | wc -l | tr -d ' ')
active=$(ls -1 _views/active/*.yaml 2>/dev/null | wc -l | tr -d ' ')
completed=$(ls -1 _views/completed/*.yaml 2>/dev/null | wc -l | tr -d ' ')
deferred=$(ls -1 _views/deferred/*.yaml 2>/dev/null | wc -l | tr -d ' ')

cat > master-index.yaml <<YAML
# CORTEX Master Registry Index
# Auto-generated: $(date +%Y-%m-%d)

metadata:
  total_phases: ${total}
  active: ${active}
  completed: ${completed}
  deferred: ${deferred}
  
# Quick Navigation:
# - Active work: _views/active/
# - Done: _views/completed/
# - Backlog: _views/deferred/
# - All phases: phases/
YAML

echo "✅ Updated! ${total} phases | ${active} active | ${completed} completed | ${deferred} deferred"
