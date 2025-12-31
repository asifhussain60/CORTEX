# 📦 YAML Files Refactoring & Modularization

**Priority:** MEDIUM (40) | **Estimated Effort:** 6-8 hrs | **Category:** Refactoring

---

## 🎯 Objective

Identify and refactor large YAML files (>5000 lines) into modular, maintainable structures while preserving functionality and enabling component reuse.

---

## 📋 Execution Steps

### Step 1: Identify Large YAML Files
```bash
# Find all YAML files and sort by line count
echo "📊 YAML Files Analysis"
echo "========================================"

find /Users/asifhussain/PROJECTS/CORTEX -name "*.yaml" -o -name "*.yml" | while read f; do
    lines=$(wc -l < "$f" 2>/dev/null | tr -d ' ')
    sizeKB=$(du -k "$f" 2>/dev/null | cut -f1)
    relPath=$(echo "$f" | sed "s|/Users/asifhussain/PROJECTS/CORTEX/||")
    
    if [ "$lines" -gt 5000 ]; then
        priority="🔴 CRITICAL"
    elif [ "$lines" -gt 2000 ]; then
        priority="🟠 HIGH"
    elif [ "$lines" -gt 1000 ]; then
        priority="🟡 MEDIUM"
    else
        priority="🟢 OK"
    fi
    
    echo "$lines|$sizeKB|$priority|$relPath"
done | sort -t'|' -k1 -nr | head -20 | column -t -s'|'

# Count refactoring candidates
echo ""
echo "🎯 Refactoring Candidates (>1000 lines):"
find /Users/asifhussain/PROJECTS/CORTEX -name "*.yaml" -o -name "*.yml" | while read f; do
    lines=$(wc -l < "$f" 2>/dev/null | tr -d ' ')
    if [ "$lines" -gt 1000 ]; then
        echo "  - $f ($lines lines)"
    fi
done
```

**Expected Output:** Sorted list of all YAML files with line counts, identifying files needing refactoring.

### Step 2: Analyze Structure of Large Files
For each file >1000 lines, analyze structure:

```bash
targetFiles=(
    "cortex-brain/response-templates-v4.yaml"
    "cortex-brain/operations-config.yaml"
    "cortex-brain/knowledge-graph.yaml"
)

for file in "${targetFiles[@]}"; do
    fullPath="/Users/asifhussain/PROJECTS/CORTEX/$file"
    
    echo ""
    echo "📄 Analyzing: $file"
    echo "========================================"
    
    # Show top-level keys (main sections)
    python3 -c "
import yaml
try:
    with open('$fullPath', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if isinstance(data, dict):
        print(f'Top-level sections ({len(data)} keys):')
        for key in data.keys():
            item_count = len(data[key]) if isinstance(data[key], (list, dict)) else 1
            item_type = type(data[key]).__name__
            print(f'  - {key}: {item_type} ({item_count} items)')
    else:
        print(f'Root structure: {type(data).__name__}')
except Exception as e:
    print(f'Error: {e}')
"
done
```

**Expected Output:** For each large file, list of top-level sections and their item counts.

### Step 3: Design Modular Structure
For each large file, create decomposition plan. Here is the target structure:

**response-templates-v4.yaml decomposition:**
| Component File | Sections |
|----------------|----------|
| `core-templates.yaml` | cortex_header, understanding, approach |
| `progress-templates.yaml` | progress_tracker_standard, autonomous_execution_progress |
| `orchestrator-templates.yaml` | planning, tdd, debug, refinement |
| `composable-blocks.yaml` | composable_blocks, generic_blocks |
| `response-formats.yaml` | instant, quick, standard, comprehensive |
| `templates-index.yaml` | Main index referencing all components |

**Base Directory:** `cortex-brain/response-templates/`

**operations-config.yaml decomposition:**
| Component File | Sections |
|----------------|----------|
| `cleanup-config.yaml` | cleanup_rules, cleanup_targets |
| `refactor-config.yaml` | refactoring_rules, refactor_patterns |
| `documentation-config.yaml` | doc_generation_rules, doc_templates |
| `validation-config.yaml` | validation_rules, quality_gates |
| `operations-index.yaml` | Main index referencing all components |

**Base Directory:** `cortex-brain/config/operations/`

**Expected Output:** Detailed decomposition plans showing how large files will be split.

### Step 4: Create Directory Structure
```bash
# Create directories for modular YAML files
directories=(
    "cortex-brain\response-templates",
    "cortex-brain\config\operations",
    "cortex-brain\knowledge\modules"
)
### Step 4: Create Directory Structure
```bash
# Create directories for modular YAML files
directories=(
    "cortex-brain/response-templates"
    "cortex-brain/config/operations"
    "cortex-brain/knowledge/modules"
)

for dir in "${directories[@]}"; do
    fullPath="/Users/asifhussain/PROJECTS/CORTEX/$dir"
    if [ ! -d "$fullPath" ]; then
        mkdir -p "$fullPath"
        echo "✅ Created: $dir"
    else
        echo "✓ Exists: $dir"
    fi
done
```

### Step 5: Extract and Modularize Components
For each large file, extract sections into component files:

```bash
# Example: Extract response-templates-v4.yaml sections
sourceFile="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/response-templates-v4.yaml"
targetDir="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/response-templates"

python3 << 'EOF'
import yaml
from pathlib import Path

# Load source file
sourceFile = "/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/response-templates-v4.yaml"
targetDir = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/response-templates")

with open(sourceFile, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# Define extraction plan
extraction_plan = {
    'core-templates.yaml': ['cortex_header', 'understanding', 'approach', 'response', 'changes', 'next_steps'],
    'progress-templates.yaml': ['progress_tracker_standard', 'autonomous_execution_progress', 'ado_execution_progress'],
    'orchestrator-templates.yaml': ['planning', 'tdd', 'debug', 'refinement', 'lens', 'sanitization'],
    'composable-blocks.yaml': ['composable_blocks', 'generic_blocks'],
    'response-formats.yaml': ['instant', 'quick', 'standard', 'comprehensive']
}

# Extract sections
for filename, sections in extraction_plan.items():
    extracted = {}
    for section in sections:
        if section in data:
            extracted[section] = data[section]
    
    # Write component file
    target_path = targetDir / filename
    with open(target_path, 'w', encoding='utf-8') as f:
        yaml.dump(extracted, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f'✅ Created: {filename} ({len(extracted)} sections)')

# Create index file
index = {
    'version': '4.0',
    'components': list(extraction_plan.keys()),
    'load_order': [
        'core-templates.yaml',
        'composable-blocks.yaml',
        'progress-templates.yaml',
        'orchestrator-templates.yaml',
        'response-formats.yaml'
    ]
}

with open(targetDir / 'templates-index.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(index, f, default_flow_style=False)

print('✅ Created: templates-index.yaml')
EOF
```

**Expected Output:** Component YAML files created in target directory with extracted sections.

### Step 6: Create Loading Mechanism
Create utility to load modular YAML files at `/Users/asifhussain/PROJECTS/CORTEX/src/cortex_brain/yaml_loader.py`:

```python
"""
YAML Modular Loader
Loads and merges modular YAML files based on index file.
"""
import yaml
from pathlib import Path
from typing import Dict, Any


class ModularYamlLoader:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
    
    def load_indexed(self, index_file: str) -> Dict[str, Any]:
        """Load YAML files referenced in index file"""
        index_path = self.base_dir / index_file
        
        with open(index_path, 'r', encoding='utf-8') as f:
            index = yaml.safe_load(f)
        
        merged_data = {}
        load_order = index.get('load_order', index.get('components', []))
        
        for component_file in load_order:
            component_path = self.base_dir / component_file
            if component_path.exists():
                with open(component_path, 'r', encoding='utf-8') as f:
                    component_data = yaml.safe_load(f)
                    merged_data.update(component_data)
        
        return merged_data
    
    def load_all(self, pattern: str = "*.yaml") -> Dict[str, Any]:
        """Load and merge all YAML files matching pattern"""
        merged_data = {}
        
        for yaml_file in sorted(self.base_dir.glob(pattern)):
            if yaml_file.name == 'templates-index.yaml':
                continue  # Skip index file
            
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                merged_data.update(data)
        
        return merged_data


# Example usage
if __name__ == "__main__":
    loader = ModularYamlLoader(Path("cortex-brain/response-templates"))
    templates = loader.load_indexed("templates-index.yaml")
    print(f"Loaded {len(templates)} templates from modular files")
```

### Step 7: Update References
Update code that loads the original large YAML files:

```bash
# Find all Python files that import the large YAML files
importPatterns=("response-templates-v4.yaml" "operations-config.yaml")

for pattern in "${importPatterns[@]}"; do
    echo ""
    echo "🔍 Finding references to: $pattern"
    
    matches=$(grep -r "$pattern" /Users/asifhussain/PROJECTS/CORTEX/src --include="*.py" -l 2>/dev/null)
    
    if [ -n "$matches" ]; then
        echo "Files to update:"
        echo "$matches" | while read f; do
            lineNum=$(grep -n "$pattern" "$f" | head -1 | cut -d: -f1)
            relPath=$(echo "$f" | sed "s|/Users/asifhussain/PROJECTS/CORTEX/||")
            echo "  - $relPath: Line $lineNum"
        done
        echo ""
        echo "⚠️  Manual update required to use ModularYamlLoader"
    else
        echo "✅ No direct references found (or already updated)"
    fi
done
```

**Manual Action Required:** Update identified files to use `ModularYamlLoader` instead of direct YAML loading.

### Step 8: Archive Original Files
```bash
# Create backups before archiving
timestamp=$(date +%Y%m%d_%H%M%S)
archiveDir="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/archives/yaml-refactor-$timestamp"
mkdir -p "$archiveDir"

filesToArchive=(
    "cortex-brain/response-templates-v4.yaml"
    "cortex-brain/operations-config.yaml"
)

for file in "${filesToArchive[@]}"; do
    sourcePath="/Users/asifhussain/PROJECTS/CORTEX/$file"
    fileName=$(basename "$file")
    archivePath="$archiveDir/$fileName"
    
    if [ -f "$sourcePath" ]; then
        cp "$sourcePath" "$archivePath"
        echo "✅ Archived: $file"
    fi
done

echo ""
echo "📦 Original files archived to: $archiveDir"
echo "⚠️  Manual verification required before deleting originals"
```

### Step 9: Validation
```bash
python3 << 'EOF'
from pathlib import Path
import sys
sys.path.insert(0, '/Users/asifhussain/PROJECTS/CORTEX')

from src.cortex_brain.yaml_loader import ModularYamlLoader

# Test response-templates loading
loader = ModularYamlLoader(Path('/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/response-templates'))
templates = loader.load_indexed('templates-index.yaml')

print('✅ Modular Loading Test:')
print(f'  Loaded {len(templates)} templates')
print(f'  Sample keys: {list(templates.keys())[:5]}')

# Verify all expected templates present
expected = ['cortex_header', 'understanding', 'progress_tracker_standard', 'autonomous_execution_progress']
missing = [key for key in expected if key not in templates]

if missing:
    print(f'❌ Missing templates: {missing}')
else:
    print(f'✅ All expected templates present')
EOF

# Check file sizes
echo ""
echo "📊 File Size Comparison:"
originalSize=$(du -k /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/archives/yaml-refactor-*/response-templates-v4.yaml 2>/dev/null | cut -f1 | head -1)
modularTotal=$(du -k /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/response-templates/*.yaml 2>/dev/null | awk '{sum+=$1} END {print sum}')
modularCount=$(ls -1 /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/response-templates/*.yaml 2>/dev/null | wc -l | tr -d ' ')

echo "  Original: ${originalSize}KB (single file)"
echo "  Modular: ${modularTotal}KB ($modularCount files)"
```

**Expected Output:**
- ✅ All templates loaded successfully
- ✅ Template count matches original
- ✅ No single modular file exceeds 1000 lines

---

## ✅ Success Criteria
- [ ] All YAML files >5000 lines identified
  Verify: Report from Step 1 lists all large files
- [ ] Decomposition plan created for each large file
  Verify: Plan shows component files and sections for each target file
- [ ] Modular directory structure created
  Verify: `test -d /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/response-templates && echo "✅ Exists"`
- [ ] Component YAML files extracted and created
  Verify: Each large file split into 3-7 component files
- [ ] No single component file exceeds 1000 lines
  Verify: `wc -l /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/response-templates/*.yaml | sort -n`
- [ ] `ModularYamlLoader` utility created and tested
  Verify: `test -f /Users/asifhussain/PROJECTS/CORTEX/src/cortex_brain/yaml_loader.py && echo "✅ Exists"`
- [ ] Original files archived with timestamp
  Verify: Archive directory exists with original files
- [ ] All references updated to use modular loading
  Verify: No broken imports, system loads templates correctly
- [ ] Validation confirms functionality preserved
  Verify: Loaded data matches original file content

---

## 📁 Files to Create

| File | Purpose |
|------|---------|
| `cortex-brain/response-templates/core-templates.yaml` | Core response templates |
| `cortex-brain/response-templates/progress-templates.yaml` | Progress tracking templates |
| `cortex-brain/response-templates/orchestrator-templates.yaml` | Orchestrator-specific templates |
| `cortex-brain/response-templates/composable-blocks.yaml` | Composable template blocks |
| `cortex-brain/response-templates/response-formats.yaml` | Response format definitions |
| `cortex-brain/response-templates/templates-index.yaml` | Index file for loading |
| `src/cortex_brain/yaml_loader.py` | Modular YAML loader utility |

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/40-yaml-bloat.md
```
Remove-Item "d:\PROJECTS\CORTEX\.asif\backlog\40-yaml-bloat.md" -Force
```
