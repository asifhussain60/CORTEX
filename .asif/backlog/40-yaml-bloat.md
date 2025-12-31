# 📦 YAML Files Refactoring & Modularization

**Priority:** MEDIUM (40) | **Estimated Effort:** 6-8 hrs | **Category:** Refactoring

---

## 🎯 Objective

Identify and refactor large YAML files (>5000 lines) into modular, maintainable structures while preserving functionality and enabling component reuse.

---

## 📋 Execution Steps

### Step 1: Identify Large YAML Files
```powershell
# Find all YAML files and sort by size
$yamlFiles = Get-ChildItem "d:\PROJECTS\CORTEX" -Recurse -Include "*.yaml","*.yml" -File

Write-Host "📊 YAML Files Analysis" -ForegroundColor Cyan
Write-Host "=" * 80

$largeFiles = $yamlFiles | ForEach-Object {
    $lines = (Get-Content $_.FullName).Count
    $sizeKB = [math]::Round($_.Length / 1KB, 2)
    
    [PSCustomObject]@{
        File = $_.FullName.Replace("d:\PROJECTS\CORTEX\", "")
        Lines = $lines
        SizeKB = $sizeKB
        Priority = if ($lines -gt 5000) { "🔴 CRITICAL" } 
                   elseif ($lines -gt 2000) { "🟠 HIGH" }
                   elseif ($lines -gt 1000) { "🟡 MEDIUM" }
                   else { "🟢 OK" }
    }
} | Sort-Object Lines -Descending

# Display results
$largeFiles | Format-Table -AutoSize

# Focus on files > 1000 lines
$refactorCandidates = $largeFiles | Where-Object { $_.Lines -gt 1000 }
Write-Host "`n🎯 Refactoring Candidates (>1000 lines): $($refactorCandidates.Count)" -ForegroundColor Yellow
```

**Expected Output:** Sorted list of all YAML files with line counts, identifying files needing refactoring.

### Step 2: Analyze Structure of Large Files
For each file >1000 lines, analyze structure:

```powershell
$targetFiles = @(
    "cortex-brain\response-templates-v4.yaml",
    "cortex-brain\operations-config.yaml",
    "cortex-brain\knowledge-graph.yaml"
    # Add others from Step 1 results
)

foreach ($file in $targetFiles) {
    $fullPath = "d:\PROJECTS\CORTEX\$file"
    
    Write-Host "`n📄 Analyzing: $file" -ForegroundColor Cyan
    Write-Host "=" * 80
    
    # Show top-level keys (main sections)
    python -c @"
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
"@
}
```

**Expected Output:** For each large file, list of top-level sections and their item counts.

### Step 3: Design Modular Structure
For each large file, create decomposition plan:

```powershell
# Example: response-templates-v4.yaml decomposition
$decompositionPlan = @{
    "response-templates-v4.yaml" = @{
        BaseDir = "cortex-brain\response-templates"
        Files = @(
            @{ Name = "core-templates.yaml"; Sections = @("cortex_header", "understanding", "approach") }
            @{ Name = "progress-templates.yaml"; Sections = @("progress_tracker_standard", "autonomous_execution_progress") }
            @{ Name = "orchestrator-templates.yaml"; Sections = @("planning", "tdd", "debug", "refinement") }
            @{ Name = "composable-blocks.yaml"; Sections = @("composable_blocks", "generic_blocks") }
            @{ Name = "response-formats.yaml"; Sections = @("instant", "quick", "standard", "comprehensive") }
        )
        MainFile = "templates-index.yaml"  # References all component files
    }
    "operations-config.yaml" = @{
        BaseDir = "cortex-brain\config\operations"
        Files = @(
            @{ Name = "cleanup-config.yaml"; Sections = @("cleanup_rules", "cleanup_targets") }
            @{ Name = "refactor-config.yaml"; Sections = @("refactoring_rules", "refactor_patterns") }
            @{ Name = "documentation-config.yaml"; Sections = @("doc_generation_rules", "doc_templates") }
            @{ Name = "validation-config.yaml"; Sections = @("validation_rules", "quality_gates") }
        )
        MainFile = "operations-index.yaml"
    }
}

# Display decomposition plan
$decompositionPlan.GetEnumerator() | ForEach-Object {
    Write-Host "`n📦 Decomposition Plan: $($_.Key)" -ForegroundColor Green
    Write-Host "  Base Directory: $($_.Value.BaseDir)"
    Write-Host "  Component Files:"
    $_.Value.Files | ForEach-Object {
        Write-Host "    - $($_.Name)"
        Write-Host "      Sections: $($_.Sections -join ', ')"
    }
    Write-Host "  Main Index: $($_.Value.MainFile)"
}
```

**Expected Output:** Detailed decomposition plans showing how large files will be split.

### Step 4: Create Directory Structure
```powershell
# Create directories for modular YAML files
$directories = @(
    "cortex-brain\response-templates",
    "cortex-brain\config\operations",
    "cortex-brain\knowledge\modules"
)

foreach ($dir in $directories) {
    $fullPath = "d:\PROJECTS\CORTEX\$dir"
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "✅ Created: $dir"
    } else {
        Write-Host "✓ Exists: $dir"
    }
}
```

### Step 5: Extract and Modularize Components
For each large file, extract sections into component files:

```powershell
# Example: Extract response-templates-v4.yaml sections
$sourceFile = "d:\PROJECTS\CORTEX\cortex-brain\response-templates-v4.yaml"
$targetDir = "d:\PROJECTS\CORTEX\cortex-brain\response-templates"

python -c @"
import yaml
from pathlib import Path

# Load source file
with open('$sourceFile', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# Define extraction plan (from Step 3)
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
    target_path = Path('$targetDir') / filename
    with open(target_path, 'w', encoding='utf-8') as f:
        yaml.dump(extracted, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f'✅ Created: {filename} ({len(extracted)} sections)')

# Create index file referencing all components
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

with open(Path('$targetDir') / 'templates-index.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(index, f, default_flow_style=False)

print(f'✅ Created: templates-index.yaml')
"@
```

**Expected Output:** Component YAML files created in target directory with extracted sections.

### Step 6: Create Loading Mechanism
Create utility to load modular YAML files:

```powershell
$loaderScript = "d:\PROJECTS\CORTEX\src\cortex_brain\yaml_loader.py"

$loaderContent = @'
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
'@

Set-Content -Path $loaderScript -Value $loaderContent
Write-Host "✅ Created: $loaderScript"
```

### Step 7: Update References
Update code that loads the original large YAML files:

```powershell
# Find all Python files that import the large YAML files
$importPatterns = @(
    "response-templates-v4.yaml",
    "operations-config.yaml"
)

foreach ($pattern in $importPatterns) {
    Write-Host "`n🔍 Finding references to: $pattern" -ForegroundColor Cyan
    
    $matches = Get-ChildItem "d:\PROJECTS\CORTEX\src" -Recurse -Filter "*.py" | 
        Select-String -Pattern $pattern -List
    
    if ($matches) {
        Write-Host "Files to update:" -ForegroundColor Yellow
        $matches | ForEach-Object {
            Write-Host "  - $($_.Path.Replace('d:\PROJECTS\CORTEX\', '')): Line $($_.LineNumber)"
        }
        Write-Host "`n⚠️  Manual update required to use ModularYamlLoader"
    } else {
        Write-Host "✅ No direct references found (or already updated)"
    }
}
```

**Manual Action Required:** Update identified files to use `ModularYamlLoader` instead of direct YAML loading.

### Step 8: Archive Original Files
```powershell
# Create backups before archiving
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archiveDir = "d:\PROJECTS\CORTEX\cortex-brain\archives\yaml-refactor-$timestamp"
New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null

$filesToArchive = @(
    "cortex-brain\response-templates-v4.yaml",
    "cortex-brain\operations-config.yaml"
)

foreach ($file in $filesToArchive) {
    $sourcePath = "d:\PROJECTS\CORTEX\$file"
    $fileName = Split-Path $file -Leaf
    $archivePath = Join-Path $archiveDir $fileName
    
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $archivePath -Force
        Write-Host "✅ Archived: $file"
    }
}

Write-Host "`n📦 Original files archived to: $archiveDir"
Write-Host "⚠️  Manual verification required before deleting originals"
```

### Step 9: Validation
```powershell
# Validate modular YAML structure
python -c @"
from pathlib import Path
from src.cortex_brain.yaml_loader import ModularYamlLoader

# Test response-templates loading
loader = ModularYamlLoader(Path('cortex-brain/response-templates'))
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

# Compare with original file
import yaml
with open('cortex-brain/archives/yaml-refactor-*/response-templates-v4.yaml', 'r') as f:
    original = yaml.safe_load(f)

if len(templates) == len(original):
    print(f'✅ Template count matches original ({len(templates)})')
else:
    print(f'⚠️  Count mismatch: Original={len(original)}, Modular={len(templates)}')
"@

# Check file sizes
Write-Host "`n📊 File Size Comparison:" -ForegroundColor Cyan
$original = Get-Item "d:\PROJECTS\CORTEX\cortex-brain\archives\yaml-refactor-*\response-templates-v4.yaml" | Select-Object -First 1
$modular = Get-ChildItem "d:\PROJECTS\CORTEX\cortex-brain\response-templates\*.yaml"

Write-Host "  Original: $([math]::Round($original.Length / 1KB, 2)) KB (single file)"
Write-Host "  Modular: $([math]::Round(($modular | Measure-Object -Property Length -Sum).Sum / 1KB, 2)) KB ($($ modular.Count) files)"
Write-Host "  Largest modular file: $([math]::Round(($modular | Sort-Object Length -Descending | Select-Object -First 1).Length / 1KB, 2)) KB"
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
  Verify: Directories exist: `response-templates/`, `config/operations/`, `knowledge/modules/`
- [ ] Component YAML files extracted and created
  Verify: Each large file split into 3-7 component files
- [ ] No single component file exceeds 1000 lines
  Verify: `Get-ChildItem cortex-brain\response-templates\*.yaml | ForEach-Object { (Get-Content $_.FullName).Count }` all <1000
- [ ] `ModularYamlLoader` utility created and tested
  Verify: Script exists at `src/cortex_brain/yaml_loader.py` and loads files correctly
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
```powershell
Remove-Item "d:\PROJECTS\CORTEX\.asif\backlog\40-yaml-bloat.md" -Force
```
