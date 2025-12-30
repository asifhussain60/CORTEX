# 🔧 Toolkit Consolidation & Cleanup

**Priority:** MEDIUM | **Estimated Effort:** 30 min | **Category:** Maintenance

---

## 🎯 Objective

Review, deduplicate, and consolidate cortex-toolkit scripts. Remove obsolete tools.

---

## 📋 Execution Steps

### Step 1: Audit Current Toolkit
```
Read files:
- cortex-toolkit/TOOLS-INVENTORY.md
- cortex-toolkit/toolkit-manifest.yaml
- cortex-toolkit/STATUS-REPORT.md
```

### Step 2: Inventory All Scripts
List all Python scripts in toolkit:
```bash
find cortex-toolkit -name "*.py" -type f | sort
```

### Step 3: Identify Duplicates & Obsolete Scripts
Check for:
- Scripts with similar functionality (e.g., multiple cleanup scripts)
- Scripts not listed in toolkit-manifest.yaml
- Scripts with no callers (grep for import/usage)
- Scripts marked as deprecated

### Step 4: Consolidation Analysis
Create consolidation plan:

| Current Scripts | Consolidate To | Action |
|-----------------|----------------|--------|
| Multiple health scripts | `core/brain/healthcheck.py` | MERGE |
| Duplicate wrappers | Single wrapper per tool | MERGE |
| Unused scripts | - | DELETE |

### Step 5: Execute Consolidation
For each consolidation:
1. Identify unique functionality in each script
2. Merge into primary script
3. Update imports and references
4. Delete redundant scripts

### Step 6: Update Manifest
Update `toolkit-manifest.yaml`:
- Remove deleted tool entries
- Update script paths for consolidated tools
- Verify all listed tools exist

### Step 7: Update TOOLS-INVENTORY.md
Regenerate inventory:
```bash
python3 cortex-toolkit/core/documentation/generate_inventory.py
```
Or manually update tool counts and paths.

### Step 8: Validation
```bash
# Verify all manifest scripts exist
python3 -c "
import yaml
import os
m = yaml.safe_load(open('cortex-toolkit/toolkit-manifest.yaml'))
for cat in m.get('categories', {}).values():
    for tool in cat.get('tools', []):
        path = 'cortex-toolkit/' + tool['script']
        if not os.path.exists(path):
            print(f'MISSING: {path}')
"
```

---

## ✅ Success Criteria
- [ ] No duplicate scripts remain
- [ ] All manifest entries have existing scripts
- [ ] TOOLS-INVENTORY.md reflects actual state
- [ ] Consolidated tool count documented
- [ ] All wrappers functional

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/03-cortex-toolkit.md
```
