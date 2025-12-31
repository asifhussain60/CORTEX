# 🔧 Decompose Maintenance Prompt into Modular Structure

**Priority:** MEDIUM (45) | **Estimated Effort:** 3-4 hrs | **Category:** Refactoring

---

## 🎯 Objective

Refactor `cortex-maintenance.prompt.md` from a single 1000+ line file into a modular folder structure with smaller, maintainable component files while preserving all functionality.

---

## 📋 Execution Steps

### Step 1: Analyze Current Maintenance Prompt Structure
```bash
# Get file size and line count
file="/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-maintenance.prompt.md"
lines=$(wc -l < "$file")
sizeKB=$(du -k "$file" | cut -f1)
echo "File: $lines lines, ${sizeKB}KB"

# Identify major sections
grep -n "^##" "$file" | head -30
```

**Expected Output:** List of all major sections (12 maintenance phases, rules, templates, etc.)

### Step 2: Design Folder Structure
Create the modular architecture:
```bash
baseDir="/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/maintenance"
folders=("phases" "rules" "templates" "workflows")

for folder in "${folders[@]}"; do
    mkdir -p "$baseDir/$folder"
    echo "✅ Created: $baseDir/$folder"
done
```

### Step 3: Extract Phase Definitions
Split each of the 12 phases into separate files. Create phase template files:
```bash
# Phase names to extract
phases=(
    "phase-01-cleanup-obsolete"
    "phase-02-consolidate-duplicates"
    "phase-03-refactor-bloat"
    "phase-04-documentation-audit"
    "phase-05-test-coverage"
    "phase-06-performance-optimization"
    "phase-07-security-review"
    "phase-08-dependency-updates"
    "phase-09-code-quality"
    "phase-10-technical-debt"
    "phase-11-integration-validation"
    "phase-12-final-verification"
)

baseDir="/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/maintenance/phases"

for i in {0..11}; do
    phaseNum=$((i + 1))
    phaseFile="$baseDir/${phases[$i]}.md"
    echo "📝 Template created for: $phaseFile (manual extraction needed)"
done
```

**Manual Action Required:** Extract actual phase content from original file into each phase file using the template structure below:
```markdown
# Phase {N}: {PHASE_NAME}

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
```

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
```

### Step 4: Create Main Orchestration File
Create file `/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/maintenance/maintenance-orchestrator.md` with this content:

```markdown
# 🔧 CORTEX Maintenance System Orchestrator

**Version:** 5.0.0 | **Author:** Asif Hussain  
**Architecture:** Modular (12-phase pipeline)

---

## 🎯 System Overview

Modular maintenance system with decomposed phases for maintainability and extensibility.

---

## 📂 Architecture

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
```

**Manual Action Required:** Create the orchestrator file with the above content.

### Step 5: Update Master Prompt Reference
```bash
# Check if CORTEX.prompt.md references the old maintenance file
cortexPrompt="/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md"

if grep -q "cortex-maintenance.prompt.md" "$cortexPrompt"; then
    echo "⚠️  Update required in CORTEX.prompt.md"
    echo "Change reference from:"
    echo "  .github/prompts/cortex-maintenance.prompt.md"
    echo "To:"
    echo "  .github/prompts/maintenance/maintenance-orchestrator.md"
else
    echo "✅ No update needed or already updated"
fi
```

**Manual Action Required:** Update the maintenance reference in `CORTEX.prompt.md`.

### Step 6: Create Backup and Archive Original
```bash
# Create backup before archiving
timestamp=$(date +%Y%m%d_%H%M%S)
backupDir="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/archives/prompts"
originalFile="/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-maintenance.prompt.md"

mkdir -p "$backupDir"
cp "$originalFile" "$backupDir/cortex-maintenance.prompt.ARCHIVED.$timestamp.md"

echo "✅ Archived original to: $backupDir/cortex-maintenance.prompt.ARCHIVED.$timestamp.md"
echo "⚠️  Manual verification required before deleting original"
```

### Step 7: Validation
```bash
# Verify all phase files exist
expectedPhases=12
baseDir="/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/maintenance/phases"
actualCount=$(ls -1 "$baseDir"/*.md 2>/dev/null | wc -l | tr -d ' ')

if [ "$actualCount" -eq "$expectedPhases" ]; then
    echo "✅ All $expectedPhases phase files present"
    ls -1 "$baseDir"/*.md | xargs -I {} basename {}
else
    echo "❌ Expected $expectedPhases phases, found $actualCount"
fi

# Verify orchestrator exists
if [ -f "/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/maintenance/maintenance-orchestrator.md" ]; then
    echo "✅ Main orchestrator file present"
else
    echo "❌ Main orchestrator file missing"
fi

# Check total line count comparison
originalLines=$(wc -l < "/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-maintenance.prompt.md" | tr -d ' ')
newLines=$(find "/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/maintenance" -name "*.md" -exec wc -l {} + | tail -1 | awk '{print $1}')

echo ""
echo "Line count comparison:"
echo "  Original: $originalLines lines (single file)"
echo "  New: $newLines lines (distributed across multiple files)"
```

**Expected Output:** 
- ✅ All 12 phase files present
- ✅ Main orchestrator file present
- Line counts showing modularization (no single file > 300 lines)

---

## ✅ Success Criteria
- [ ] Folder structure created: `maintenance/phases/`, `maintenance/rules/`, `maintenance/templates/`, `maintenance/workflows/`
  Verify: `test -d /Users/asifhussain/PROJECTS/CORTEX/.github/prompts/maintenance/phases && echo "✅ Exists"`
- [ ] 12 phase files created in `phases/` directory
  Verify: `ls -1 /Users/asifhussain/PROJECTS/CORTEX/.github/prompts/maintenance/phases/*.md | wc -l` returns `12`
- [ ] Main orchestrator file created
  Verify: `test -f /Users/asifhussain/PROJECTS/CORTEX/.github/prompts/maintenance/maintenance-orchestrator.md && echo "✅ Exists"`
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
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/45-decompose-maint.md
```