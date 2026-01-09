# CORTEX-5.5 Migration Execution Guide

**Version:** 1.0.0  
**Created:** 2026-01-06  
**Purpose:** Step-by-step guide to execute CORTEX-5.5 clean branch migration

---

## 🎯 Overview

This guide walks you through creating the CORTEX-5.5 branch with:
- ✅ 85% file reduction (from ~1000 files to ~150 essential files)
- ✅ Phase 1 scaffolding ready for immediate execution
- ✅ Pull-on-demand system for CORTEX-5.0 dependencies
- ✅ Zero technical debt carried forward

**Estimated Time:** 15 minutes  
**Prerequisites:** Git, PowerShell 7+, clean working tree

---

## 📋 Pre-Migration Checklist

Before starting, verify:

```powershell
# 1. You're in CORTEX root
pwd  # Should show: D:\PROJECTS\CORTEX

# 2. Clean working tree
git status  # Should show "nothing to commit, working tree clean"

# 3. Latest CORTEX-5.0
git fetch origin
git checkout CORTEX-5.0
git pull origin CORTEX-5.0

# 4. Latest main
git checkout main
git pull origin main

# 5. PowerShell version (need 7+)
$PSVersionTable.PSVersion  # Should be 7.x or higher
```

---

## 🚀 Automated Migration (Recommended)

### Step 1: Run Migration Script

```powershell
# Execute automated migration
.\create-cortex-5.5-branch.ps1
```

**What it does:**
1. ✅ Validates environment (Git repo, clean tree)
2. ✅ Creates CORTEX-5.5 branch from main
3. ✅ Creates 19 essential directories
4. ✅ Copies ~50 essential files from CORTEX-5.0
5. ✅ Creates Phase 1 scaffolding (src/knowledge/, company_knowledge/)
6. ✅ Validates structure

**Expected Output:**
```
🚀 CORTEX-5.5 Clean Branch Migration
═══════════════════════════════════════════════════════

[1/8] Validating environment
✅ Git repository validated
✅ Working tree is clean

[2/8] Fetching latest from remote
✅ Fetched latest changes

[3/8] Creating branch from main
✅ Created branch CORTEX-5.5 from main

[4/8] Creating directory structure
✅ Created 19 directories

[5/8] Copying essential files from CORTEX-5.0
  ✓ .gitignore
  ✓ requirements.txt
  ✓ pytest.ini
  ... (50+ files)
✅ Copied 52 files, skipped 3

[6/8] Copying cortex5-enhancement-epic plan
✅ Copied cortex5-enhancement-epic plan

[7/8] Copying source code modules
✅ Copied source code modules

[8/8] Creating Phase 1 scaffolding
✅ Created Phase 1 scaffolding

═══════════════════════════════════════════════════════
🎉 CORTEX-5.5 Branch Created Successfully!
═══════════════════════════════════════════════════════
```

### Step 2: Review Changes

```powershell
# Check what was created
git status

# Should show ~150 files staged
git diff --cached --stat

# Review structure
tree -L 3
```

### Step 3: Validate Structure

```powershell
# Run structure validation (if available)
python -m pytest tests/ -v --tb=short

# Check essential files exist
Test-Path "src/knowledge/company_knowledge_provider.py"  # Should be True
Test-Path "cortex-brain/brain-protection-rules.yaml"    # Should be True
Test-Path ".github/prompts/CORTEX.prompt.md"            # Should be True
```

### Step 4: Commit and Push

```powershell
# Stage all changes
git add .

# Commit with epic reference
git commit -m "feat: Initialize CORTEX-5.5 clean branch with Phase 1 scaffolding

- Essential files only (85% reduction vs CORTEX-5.0)
- Pull from CORTEX-5.0 on demand via pull-from-cortex-5.0.ps1
- Phase 1: Knowledge Extension Layer ready for execution
- Zero technical debt carried forward
- See: cortex-brain/documents/planning/active/cortex5-enhancement-epic/CORTEX-5.5-MIGRATION-STRATEGY.md

Epic: cortex5-enhancement-epic-v2
Phase: 0 (Foundation)"

# Push to remote
git push -u origin CORTEX-5.5
```

---

## 🔧 Manual Migration (Alternative)

If automated script fails, follow these steps:

### Step 1: Create Branch

```powershell
git checkout main
git pull origin main
git checkout -b CORTEX-5.5
```

### Step 2: Create Directories

```powershell
$dirs = @(
    ".github/prompts/maintenance",
    "cortex-brain/tier0", "cortex-brain/tier1", "cortex-brain/tier2/company-knowledge",
    "cortex-brain/config", "cortex-brain/manifests/orchestrators",
    "cortex-brain/documents/planning/active",
    "src/orchestrators/planning", "src/orchestrators/ado", "src/orchestrators/investigation",
    "src/knowledge", "src/config", "src/database", "src/response_templates",
    "src/logging", "src/diagnostics", "src/utils",
    "tests/unit", "tests/integration"
)

$dirs | ForEach-Object { New-Item -ItemType Directory -Path $_ -Force }
```

### Step 3: Copy Essential Files

```powershell
# Root configuration
git checkout CORTEX-5.0 -- .gitignore requirements.txt pytest.ini mypy.ini README.md LICENSE

# GitHub Prompts
git checkout CORTEX-5.0 -- .github/copilot-instructions.md
git checkout CORTEX-5.0 -- .github/prompts/CORTEX.prompt.md

# Brain tier files
git checkout CORTEX-5.0 -- cortex-brain/brain-protection-rules.yaml
git checkout CORTEX-5.0 -- cortex-brain/response-templates-v4.yaml
git checkout CORTEX-5.0 -- cortex-brain/capabilities.yaml
git checkout CORTEX-5.0 -- cortex-brain/tier2/schema.sql

# Configuration
git checkout CORTEX-5.0 -- cortex-brain/config/master-orchestrator.yaml
git checkout CORTEX-5.0 -- cortex-brain/config/planning-v5-default.yaml

# Source code
git checkout CORTEX-5.0 -- src/main.py
git checkout CORTEX-5.0 -- src/orchestrators/master_orchestrator.py
git checkout CORTEX-5.0 -- src/orchestrators/planning/
git checkout CORTEX-5.0 -- src/config/
git checkout CORTEX-5.0 -- src/database/

# (See CORTEX-5.5-MIGRATION-STRATEGY.md for complete list)
```

### Step 4: Create Phase 1 Scaffolding

```powershell
# Create knowledge module
New-Item -ItemType File -Path "src/knowledge/__init__.py" -Force
New-Item -ItemType File -Path "src/knowledge/company_knowledge_provider.py" -Force
New-Item -ItemType File -Path "src/knowledge/knowledge_merger.py" -Force

# Create sample company structure
New-Item -ItemType Directory -Path "cortex-brain/tier2/company-knowledge/sample_company" -Force
New-Item -ItemType File -Path "cortex-brain/tier2/company-knowledge/sample_company/architecture.md" -Force
New-Item -ItemType File -Path "cortex-brain/tier2/company-knowledge/sample_company/tech-stack.yaml" -Force

# (See create-cortex-5.5-branch.ps1 for file content templates)
```

---

## ✅ Post-Migration Validation

### Validation Checklist

Run each command and verify output:

```powershell
# 1. Git status
git status
# Expected: All changes staged, branch CORTEX-5.5

# 2. File count
(git ls-files | Measure-Object).Count
# Expected: ~150-180 files (vs ~1000 in CORTEX-5.0)

# 3. Essential files exist
Test-Path "src/main.py"                                    # True
Test-Path "cortex-brain/brain-protection-rules.yaml"       # True
Test-Path "src/knowledge/company_knowledge_provider.py"    # True
Test-Path ".github/prompts/CORTEX.prompt.md"               # True

# 4. Epic plan exists
Test-Path "cortex-brain/documents/planning/active/cortex5-enhancement-epic/00-cortex5-epic.md"  # True

# 5. Python syntax check
Get-ChildItem -Path "src" -Filter "*.py" -Recurse | ForEach-Object {
    python -m py_compile $_.FullName
}
# Expected: No syntax errors

# 6. Structure validation
tree cortex-brain -L 2
tree src -L 2
```

### Success Criteria

✅ **Branch Created:** `CORTEX-5.5` exists and is checked out  
✅ **File Reduction:** ~150 files (85% reduction from CORTEX-5.0)  
✅ **Phase 1 Ready:** `src/knowledge/` scaffolding exists  
✅ **Epic Available:** cortex5-enhancement-epic plan accessible  
✅ **No Syntax Errors:** All Python files compile  
✅ **Pull System Ready:** `pull-from-cortex-5.0.ps1` script exists  

---

## 🔄 Using the Pull System

### When to Pull from CORTEX-5.0

**Pull when:**
- ✅ Phase implementation explicitly requires a file
- ✅ File is actively used (not obsolete)
- ✅ AST analysis shows current dependencies
- ✅ File modified within last 90 days

**Don't pull when:**
- ❌ File is obsolete (>90 days old)
- ❌ File has >5 dependencies (rewrite instead)
- ❌ File is in excluded categories (samples, backups, archives)
- ❌ Alternative exists (simpler rewrite)

### Pull Command

```powershell
# Example: Phase 3 needs LLM utilities
.\pull-from-cortex-5.0.ps1 `
    -Phase 3 `
    -Files @("src/llm/llm_provider.py", "src/llm/prompt_builder.py") `
    -Justification "LLM-based goal detection requires prompt building utilities" `
    -AlternativesConsidered @("Rewrite with OpenAI SDK", "Use Anthropic Claude API") `
    -DecisionRationale "Existing LLM provider supports multiple models, rewrite not justified" `
    -Category "llm_utilities"
```

**What it does:**
1. ✅ Validates files exist in CORTEX-5.0
2. ✅ Checks file age (<90 days preferred)
3. ✅ Validates pull budget (max 20 pulls)
4. ✅ Pulls files from CORTEX-5.0
5. ✅ Updates tracking JSON (`pulls-from-cortex-5.0.json`)
6. ✅ Records justification and alternatives

### Pull Budget Tracking

```powershell
# Check pull budget status
$tracking = Get-Content "cortex-brain/documents/planning/active/cortex5-enhancement-epic/tracking/pulls-from-cortex-5.0.json" | ConvertFrom-Json

Write-Host "Pull Budget: $($tracking.pull_budget.current_pull_count)/$($tracking.pull_budget.max_pulls_allowed)"
Write-Host "Remaining: $($tracking.pull_budget.remaining_pulls)"

# View pull history
$tracking.pulls | Format-Table phase, pull_date, file_count, justification
```

---

## 🏁 Ready for Phase 1 Execution

Once migration is complete:

```powershell
# 1. Open epic master plan
code "cortex-brain/documents/planning/active/cortex5-enhancement-epic/00-cortex5-epic.md"

# 2. Open Phase 1 implementation guide
code "cortex-brain/documents/planning/active/cortex5-enhancement-epic/phases/phase-01-knowledge-extension.md"

# 3. Start implementation
# Follow Phase 1 step-by-step implementation guide
# Use TDD: Write tests first, then implement
```

### Phase 1 Quick Start

**Goal:** Implement `CompanyKnowledgeProvider` with merge logic

**Steps:**
1. Write failing tests for `CompanyKnowledgeProvider.query_architecture()`
2. Implement minimal code to pass tests
3. Refactor while keeping tests green
4. Repeat for other query methods
5. Implement `KnowledgeMerger.merge_with_cortex_knowledge()`
6. Integration test: Query company knowledge → Verify override works

**Expected Duration:** 2 weeks (Phase 1 timeline)

---

## 🆘 Troubleshooting

### Issue: Script fails with "Not a Git repository"

**Solution:**
```powershell
# Ensure you're in CORTEX root
cd D:\PROJECTS\CORTEX
pwd  # Should show CORTEX directory
```

### Issue: "Branch already exists"

**Solution:**
```powershell
# Delete and recreate
git branch -D CORTEX-5.5
.\create-cortex-5.5-branch.ps1
```

### Issue: "File not found in CORTEX-5.0"

**Cause:** File may have been moved or deleted in CORTEX-5.0  
**Solution:**
```powershell
# Check if file exists in CORTEX-5.0
git checkout CORTEX-5.0
git ls-files | Select-String "filename"

# If not found, skip or find alternative in CORTEX-5.0
```

### Issue: Pull budget exceeded

**Cause:** More than 20 files pulled from CORTEX-5.0  
**Solution:**
```powershell
# Review pulls to ensure necessity
$tracking = Get-Content "tracking/pulls-from-cortex-5.0.json" | ConvertFrom-Json
$tracking.pulls | Format-Table

# Consider if rewrite would be better than pull
# Request budget increase (update max_pulls_allowed in tracking JSON)
```

### Issue: Python syntax errors after migration

**Cause:** Missing dependencies or incomplete module  
**Solution:**
```powershell
# Install dependencies
pip install -r requirements.txt

# Check specific file
python -m py_compile src/path/to/file.py

# If still fails, may need to pull additional dependencies
```

---

## 📊 Migration Success Metrics

After migration, verify these metrics:

| Metric | Target | Command |
|--------|--------|---------|
| **File Count** | ~150 files | `(git ls-files | Measure-Object).Count` |
| **File Reduction** | 85% | `(1000 - 150) / 1000 * 100` |
| **Branch Exists** | CORTEX-5.5 | `git branch --list CORTEX-5.5` |
| **Phase 1 Ready** | Scaffolding exists | `Test-Path "src/knowledge/*.py"` |
| **Epic Accessible** | Plan exists | `Test-Path "cortex-brain/documents/planning/active/cortex5-enhancement-epic"` |
| **Pull System Ready** | Script exists | `Test-Path "pull-from-cortex-5.0.ps1"` |
| **No Syntax Errors** | 0 errors | `pytest tests/ -v` |

---

## 📚 Related Documents

- **Migration Strategy:** `CORTEX-5.5-MIGRATION-STRATEGY.md` (full technical details)
- **Epic Master Plan:** `00-cortex5-epic.md` (11 phases, 9 weeks)
- **Phase 1 Guide:** `phases/phase-01-knowledge-extension.md` (first implementation)
- **Pull Tracking:** `tracking/pulls-from-cortex-5.0.json` (live pull log)

---

## 🎉 Congratulations!

You've successfully created the CORTEX-5.5 clean branch! 🚀

**Next Steps:**
1. ✅ Commit and push the new branch
2. ✅ Open Phase 1 implementation guide
3. ✅ Start TDD cycle: RED→GREEN→REFACTOR
4. ✅ Track progress in `tracking/progress-tracker.json`

**Questions?** See `README.md` in cortex5-enhancement-epic folder.

---

**Last Updated:** 2026-01-06  
**Maintained By:** CORTEX Planning System v5  
**Script Version:** create-cortex-5.5-branch.ps1 v1.0.0
