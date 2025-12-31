# 🔧 Decompose Maintenance Prompt into Modular Structure

**Priority:** MEDIUM (45) | **Estimated Effort:** 3-4 hrs | **Category:** Refactoring

---

## 🎯 Objective

Refactor `cortex-maintenance.prompt.md` from a single 1000+ line file into a modular folder structure with smaller, maintainable component files while preserving all functionality.

---

## 📋 Execution Steps

### Step 1: Analyze Current Maintenance Prompt Structure
```powershell
# Get file size and line count
$file = "d:\PROJECTS\CORTEX\.github\prompts\cortex-maintenance.prompt.md"
$lines = (Get-Content $file).Count
$sizeKB = [math]::Round((Get-Item $file).Length / 1KB, 2)
Write-Host "File: $lines lines, $sizeKB KB"

# Identify major sections
Select-String -Path $file -Pattern "^##\s+" | Select-Object LineNumber, Line | Format-Table -AutoSize
```

**Expected Output:** List of all major sections (12 maintenance phases, rules, templates, etc.)

### Step 2: Design Folder Structure
Create the modular architecture:
```powershell
$baseDir = "d:\PROJECTS\CORTEX\.github\prompts\maintenance"
$folders = @(
    "phases",        # Individual phase definitions
    "rules",         # Validation and execution rules
    "templates",     # Response templates specific to maintenance
    "workflows"      # Phase sequencing and orchestration
)

foreach ($folder in $folders) {
    $path = Join-Path $baseDir $folder
    New-Item -ItemType Directory -Path $path -Force | Out-Null
    Write-Host "✅ Created: $path"
}
```

### Step 3: Extract Phase Definitions
Split each of the 12 phases into separate files:
```powershell
# Read the maintenance prompt
$content = Get-Content "d:\PROJECTS\CORTEX\.github\prompts\cortex-maintenance.prompt.md" -Raw

# Phase names to extract
$phases = @(
    "phase-01-cleanup-obsolete",
    "phase-02-consolidate-duplicates",
    "phase-03-refactor-bloat",
    "phase-04-documentation-audit",
    "phase-05-test-coverage",
    "phase-06-performance-optimization",
    "phase-07-security-review",
    "phase-08-dependency-updates",
    "phase-09-code-quality",
    "phase-10-technical-debt",
    "phase-11-integration-validation",
    "phase-12-final-verification"
)

# For each phase, extract content between ## Phase N and ## Phase N+1
foreach ($i in 0..11) {
    $phaseNum = $i + 1
    $phaseFile = "d:\PROJECTS\CORTEX\.github\prompts\maintenance\phases\$($phases[$i]).md"
    
    # Extract phase content (manual extraction needed - this is a template)
    $phaseContent = @"
# Phase $phaseNum: {PHASE_NAME}

**Duration:** {ESTIMATED_TIME} | **Criticality:** {HIGH/MEDIUM/LOW}

---

## 🎯 Objective
{PHASE_OBJECTIVE}

---

## 📋 Execution Steps
{PHASE_STEPS}

---

## ✅ Success Criteria
{PHASE_CRITERIA}

---

## 🔗 Dependencies
- **Requires:** {PREVIOUS_PHASES}
- **Blocks:** {SUBSEQUENT_PHASES}
"@
    
    # Placeholder - manual extraction needed
    Write-Host "📝 Template created for: $phaseFile (manual extraction needed)"
}
```

**Manual Action Required:** Extract actual phase content from original file into each phase file.

### Step 4: Create Main Orchestration File
```powershell
$mainFile = "d:\PROJECTS\CORTEX\.github\prompts\maintenance\maintenance-orchestrator.md"
$content = @"
# 🔧 CORTEX Maintenance System Orchestrator

**Version:** 5.0.0 | **Author:** Asif Hussain  
**Architecture:** Modular (12-phase pipeline)

---

## 🎯 System Overview

Modular maintenance system with decomposed phases for maintainability and extensibility.

---

## 📂 Architecture

\`\`\`
maintenance/
├── maintenance-orchestrator.md     # This file (entry point)
├── phases/                          # 12 individual phase definitions
│   ├── phase-01-cleanup-obsolete.md
│   ├── phase-02-consolidate-duplicates.md
│   ├── ...
│   └── phase-12-final-verification.md
├── rules/                           # Execution and validation rules
│   ├── skull-enforcement.md
│   ├── git-checkpoint-rules.md
│   └── validation-criteria.md
├── templates/                       # Response templates
│   └── maintenance-responses.yaml
└── workflows/                       # Phase sequencing
    └── 12-phase-pipeline.md
\`\`\`

---

## 🚀 Phase Pipeline

| Phase | File | Duration | Criticality |
|-------|------|----------|-------------|
| 1 | \`phases/phase-01-cleanup-obsolete.md\` | 20 min | HIGH |
| 2 | \`phases/phase-02-consolidate-duplicates.md\` | 25 min | HIGH |
| 3 | \`phases/phase-03-refactor-bloat.md\` | 30 min | MEDIUM |
| 4 | \`phases/phase-04-documentation-audit.md\` | 20 min | MEDIUM |
| 5 | \`phases/phase-05-test-coverage.md\` | 25 min | HIGH |
| 6 | \`phases/phase-06-performance-optimization.md\` | 20 min | MEDIUM |
| 7 | \`phases/phase-07-security-review.md\` | 25 min | HIGH |
| 8 | \`phases/phase-08-dependency-updates.md\` | 20 min | MEDIUM |
| 9 | \`phases/phase-09-code-quality.md\` | 20 min | MEDIUM |
| 10 | \`phases/phase-10-technical-debt.md\` | 25 min | HIGH |
| 11 | \`phases/phase-11-integration-validation.md\` | 30 min | HIGH |
| 12 | \`phases/phase-12-final-verification.md\` | 20 min | HIGH |

**Total Pipeline Duration:** ~4.5 hours

---

## 📥 Usage

When user requests maintenance, load this orchestrator and:
1. Load \`workflows/12-phase-pipeline.md\` for execution sequence
2. Execute each phase by loading its file from \`phases/\`
3. Apply rules from \`rules/\` at each checkpoint
4. Use templates from \`templates/\` for responses

---

## 🔗 Cross-References

- **Brain Protection:** \`cortex-brain/brain-protection-rules.yaml\`
- **Response Templates:** \`cortex-brain/response-templates-v4.yaml\`
- **Git Checkpoint Rules:** \`cortex-brain/git-checkpoint-rules.yaml\`
"@

Set-Content -Path $mainFile -Value $content
Write-Host "✅ Created: $mainFile"
```

### Step 5: Update Master Prompt Reference
```powershell
# Update CORTEX.prompt.md to reference new modular structure
$cortexPrompt = "d:\PROJECTS\CORTEX\.github\prompts\CORTEX.prompt.md"
$content = Get-Content $cortexPrompt -Raw

# Find maintenance reference and update
if ($content -match "cortex-maintenance\.prompt\.md") {
    Write-Host "⚠️  Update required in CORTEX.prompt.md"
    Write-Host "Change reference from:"
    Write-Host "  .github/prompts/cortex-maintenance.prompt.md"
    Write-Host "To:"
    Write-Host "  .github/prompts/maintenance/maintenance-orchestrator.md"
} else {
    Write-Host "✅ No update needed or already updated"
}
```

**Manual Action Required:** Update the maintenance reference in `CORTEX.prompt.md`.

### Step 6: Create Backup and Archive Original
```powershell
# Create backup before archiving
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "d:\PROJECTS\CORTEX\cortex-brain\archives\prompts"
$originalFile = "d:\PROJECTS\CORTEX\.github\prompts\cortex-maintenance.prompt.md"

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$backupFile = Join-Path $backupDir "cortex-maintenance.prompt.ARCHIVED.$timestamp.md"
Copy-Item $originalFile $backupFile -Force

Write-Host "✅ Archived original to: $backupFile"
Write-Host "⚠️  Manual verification required before deleting original"
```

### Step 7: Validation
```powershell
# Verify all phase files exist
$expectedPhases = 12
$phaseFiles = Get-ChildItem "d:\PROJECTS\CORTEX\.github\prompts\maintenance\phases\*.md"
$actualCount = $phaseFiles.Count

if ($actualCount -eq $expectedPhases) {
    Write-Host "✅ All $expectedPhases phase files present"
    $phaseFiles | ForEach-Object { Write-Host "  - $($_.Name)" }
} else {
    Write-Host "❌ Expected $expectedPhases phases, found $actualCount" -ForegroundColor Red
}

# Verify orchestrator exists
if (Test-Path "d:\PROJECTS\CORTEX\.github\prompts\maintenance\maintenance-orchestrator.md") {
    Write-Host "✅ Main orchestrator file present"
} else {
    Write-Host "❌ Main orchestrator file missing" -ForegroundColor Red
}

# Check total line count reduction
$originalLines = (Get-Content "d:\PROJECTS\CORTEX\.github\prompts\cortex-maintenance.prompt.md").Count
$newLines = 0
Get-ChildItem "d:\PROJECTS\CORTEX\.github\prompts\maintenance" -Recurse -Filter "*.md" | ForEach-Object {
    $newLines += (Get-Content $_.FullName).Count
}

Write-Host "`nLine count comparison:"
Write-Host "  Original: $originalLines lines (single file)"
Write-Host "  New: $newLines lines (distributed across multiple files)"
Write-Host "  Largest file: $(Get-ChildItem 'd:\PROJECTS\CORTEX\.github\prompts\maintenance' -Recurse -Filter '*.md' | Sort-Object Length -Descending | Select-Object -First 1 | ForEach-Object { [math]::Round((Get-Content $_.FullName).Count) }) lines"
```

**Expected Output:** 
- ✅ All 12 phase files present
- ✅ Main orchestrator file present
- Line counts showing modularization (no single file > 300 lines)

---

## ✅ Success Criteria
- [ ] Folder structure created: `maintenance/phases/`, `maintenance/rules/`, `maintenance/templates/`, `maintenance/workflows/`
  Verify: `Test-Path "d:\PROJECTS\CORTEX\.github\prompts\maintenance\phases"` returns `True`
- [ ] 12 phase files created in `phases/` directory
  Verify: `(Get-ChildItem "d:\PROJECTS\CORTEX\.github\prompts\maintenance\phases\*.md").Count` returns `12`
- [ ] Main orchestrator file created
  Verify: `Test-Path "d:\PROJECTS\CORTEX\.github\prompts\maintenance\maintenance-orchestrator.md"` returns `True`
- [ ] Original file archived with timestamp
  Verify: Backup exists in `cortex-brain/archives/prompts/`
- [ ] No single file exceeds 300 lines
  Verify: All files in new structure are < 300 lines
- [ ] CORTEX.prompt.md updated to reference new location
  Verify: File contains reference to `maintenance/maintenance-orchestrator.md`
- [ ] All functionality preserved (system still executes 12-phase maintenance)
  Verify: Run maintenance command and confirm all phases execute

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```powershell
Remove-Item "d:\PROJECTS\CORTEX\.asif\backlog\45-decompose-maint.md" -Force
```