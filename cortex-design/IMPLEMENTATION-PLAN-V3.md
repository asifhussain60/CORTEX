# CORTEX Implementation Plan V3 - Organized for Logical Execution

**Date:** 2025-11-06  
**Status:** 🎯 ACTIVE - Ready for Execution  
**Created From:** V2 plan with all recommendations accepted  
**Approach:** Small increments (Rule #23) for resilient execution  
**Special Additions:** Full system check mechanism + root folder enforcement

---

## 📋 Executive Summary

This V3 plan represents a **complete reorganization** of the V2 plan into **logical execution order**. Key changes:

### ✅ What's New in V3

1. **Logical Ordering:** Tasks grouped by dependency and execution flow (not arbitrary phases)
2. **Full System Check:** Dedicated mechanism for complete CORTEX validation (implemented LAST)
3. **Root Folder Enforcement:** CORTEX cleanup script ensures only approved files in root
4. **Small Increments:** All large files created in 100-150 line chunks (Rule #23)
5. **Atomic Execution:** Each task is a single-shot operation (no multi-step announcements)

### 📂 Root Folder File List (Enforced)

The final structure of `D:\PROJECTS\KDS\CORTEX\` will contain **ONLY these files** in the root:

```
D:\PROJECTS\KDS\CORTEX\
├── README.md                          ✅ APPROVED
├── The CORTEX Story.docx              ✅ APPROVED (to be created)
├── The CORTEX Rule Book.pdf           ✅ APPROVED (to be created)
├── package.json                       ✅ APPROVED (dependencies)
├── requirements.txt                   ✅ APPROVED (Python deps)
├── tsconfig.json                      ✅ APPROVED (TypeScript config)
├── .gitignore                         ✅ APPROVED (Git config)
├── LICENSE                            ✅ APPROVED (if exists)
└── [FOLDERS - not files]
```

**Enforcement:** `cleanup-cortex-root.ps1` script removes unauthorized files, moves to appropriate folders.

### 🎯 Full System Check Mechanism

**Purpose:** Validate complete CORTEX system health after full implementation

**Location:** `CORTEX/scripts/system-check/`  
**Execution:** `.\scripts\system-check\run-full-system-check.ps1`  
**Status:** PLACEHOLDER - Implemented LAST (after all other tasks complete)

**What it validates:**
- ✅ All 4 tiers operational (Tier 0-3)
- ✅ All agents functional (10 specialist agents)
- ✅ Database integrity (schema, indexes, constraints)
- ✅ Performance targets met (query latency, storage size)
- ✅ Test coverage ≥95%
- ✅ Documentation complete (MkDocs builds)
- ✅ CI/CD pipeline operational
- ✅ Root folder compliance (only approved files)
- ✅ All governance rules enforced
- ✅ Brain learning active (event logging, auto-updates)

**Implementation:** After Phase 9 complete (last task)

---

## 📚 Document Creation Options

**Question:** Can README.md, The CORTEX Story.docx, and The CORTEX Rule Book.pdf be created with the new doc tool?

**Answer:** YES - All three can be created/generated with configured tools:

### 1. README.md
**Tool:** Standard Markdown editor (VS Code, any text editor)  
**Location:** `D:\PROJECTS\KDS\CORTEX\README.md`  
**Content:** Project overview, quick start, architecture summary  
**Format:** Plain Markdown (GitHub-compatible)

### 2. The CORTEX Story.docx
**Tool Options:**
- **Option A:** Write in Markdown → Convert to .docx with Pandoc
  ```powershell
  # Install Pandoc (if not installed)
  choco install pandoc
  
  # Convert Markdown to .docx
  pandoc CORTEX-Story.md -o "The CORTEX Story.docx" --reference-doc=template.docx
  ```
- **Option B:** Write directly in Word (Microsoft Word)
- **Option C:** Use Google Docs → Export as .docx

**Recommended:** Option A (Markdown → Pandoc) for version control and consistency

### 3. The CORTEX Rule Book.pdf
**Tool Options:**
- **Option A:** Write in Markdown → Convert to PDF with Pandoc
  ```powershell
  # Convert Markdown to PDF (requires LaTeX)
  pandoc CORTEX-Rulebook.md -o "The CORTEX Rule Book.pdf" --pdf-engine=xelatex
  ```
- **Option B:** MkDocs → PDF plugin
  ```bash
  # Install MkDocs PDF plugin
  pip install mkdocs-with-pdf
  
  # Add to mkdocs.yml
  plugins:
    - with-pdf:
        output_path: ../The CORTEX Rule Book.pdf
  
  # Build
  mkdocs build
  ```
- **Option C:** LaTeX → PDF (for professional formatting)

**Recommended:** Option B (MkDocs PDF) since MkDocs is already configured in Phase 0

### Document Creation Plan

**Task 9.7: Create Root Documentation Files (2 hours)** - Added to Phase 9

```yaml
Deliverables:
  - README.md (Markdown, direct edit)
  - The CORTEX Story.docx (Markdown → Pandoc)
  - The CORTEX Rule Book.pdf (MkDocs → PDF)
  
Tools Used:
  - VS Code (Markdown editing)
  - Pandoc (Markdown → .docx conversion)
  - MkDocs with PDF plugin (Markdown → PDF)
  
Source Files:
  - CORTEX/docs/story/cortex-story.md → The CORTEX Story.docx
  - CORTEX/docs/governance/ → The CORTEX Rule Book.pdf
  - CORTEX/README.md (direct creation)
```

---

## 🚀 V3 Plan Structure

Instead of arbitrary "phases," tasks are grouped by **logical execution order**:

```
GROUP 1: Foundation & Validation (Project Setup)
  ↓
GROUP 2: Core Infrastructure (Tier 0, CI/CD, Docs)
  ↓
GROUP 3: Data Storage (Tiers 1, 2, 3)
  ↓
GROUP 4: Intelligence Layer (Agents, Entry Point)
  ↓
GROUP 5: Migration & Validation (KDS → CORTEX)
  ↓
GROUP 6: Finalization (System Check, Root Cleanup)
```

Each group has clear **entry criteria** (what must be complete before starting) and **exit criteria** (what must be validated before moving on).

---

## 📊 V3 vs V2 Comparison

| Aspect | V2 Plan | V3 Plan |
|--------|---------|---------|
| Structure | 9 phases (-2 to 6) | 6 logical groups |
| Task Count | 79-101 tasks | Same tasks, reorganized |
| Timeline | 79-101 hours | Same (10-13 days) |
| Ordering | Sequential phases | Dependency-based |
| Increments | Some large files | All files ≤150 lines/chunk |
| System Check | Scattered validation | Dedicated mechanism (last) |
| Root Cleanup | Not specified | Enforced script |
| Documentation | 3 files mentioned | Tool choices specified |

---

## 🎯 GROUP 1: Foundation & Validation (Project Setup)

**Purpose:** Prepare the project for CORTEX implementation  
**Duration:** 10-14 hours  
**Entry Criteria:** None (starting point)  
**Exit Criteria:** Clean project structure, GitHub repo renamed, benchmarks complete

### Tasks in GROUP 1

**From Phase -2 (Project Reorganization):**
- Task -2.1: Backup Current State (30 min)
- Task -2.2: Create New CORTEX Directory Structure (1 hr)
- Task -2.3: Implement Git-Based Documentation Storage (1.5 hrs)
- Task -2.4: Rename GitHub Repository (30 min)
- Task -2.5: Add New Governance Rules (1 hr)
- Task -2.6: Update All Path References (1 hr)
- Task -2.7: Validation & Testing (30 min)

**From Phase -1 (Architecture Validation):**
- Task -1.1: sql.js Performance Benchmarking (2-3 hrs)
- Task -1.2: Browser API Compatibility Testing (1-2 hrs)
- Task -1.3: Unified Schema Lock Contention Analysis (1-2 hrs)
- Task -1.4: Dashboard Technology Validation (1-2 hrs)
- Task -1.5: Document Findings & Contingencies (1 hr)

**Total GROUP 1:** 10-14 hours

---

## 🔐 GROUP 2: Core Infrastructure (Tier 0, CI/CD, Docs)

**Purpose:** Establish governance, testing, and documentation foundation  
**Duration:** 6-8 hours  
**Entry Criteria:** GROUP 1 complete (project reorganized, benchmarks validated)  
**Exit Criteria:** Tier 0 operational, CI/CD passing, MkDocs built

### Tasks in GROUP 2

**From Phase 0 (Governance + CI/CD + Docs):**
- Task 0.1: GovernanceEngine Class (1 hr)
- Task 0.2: YAML → SQLite Migration (1 hr)
- Task 0.3: Rule Query API (1 hr)
- Task 0.4: Violation Tracking (1 hr)
- Task 0.5: Testing (15 unit + 2 integration tests) (1 hr)
- Task 0.6: CI/CD Setup (1 hr)
- Task 0.7: MkDocs Documentation Setup (1 hr)

**Total GROUP 2:** 6-8 hours

---

## 💾 GROUP 3: Data Storage (Tiers 1, 2, 3)

**Purpose:** Implement 3-tier brain storage system  
**Duration:** 31-37 hours  
**Entry Criteria:** GROUP 2 complete (Tier 0 operational)  
**Exit Criteria:** All tiers functional, migration tools tested

### Tasks in GROUP 3

**Sub-Group 3A: Phase 0.5 (Migration Tools - Test Early)**
- Task 0.5.1: Tier 1 Migration Script (1-1.5 hrs)
- Task 0.5.2: Tier 2 Migration Script (1-1.5 hrs)
- Task 0.5.3: Tier 3 Migration Script (30-45 min)
- Task 0.5.4: End-to-End Migration Test (30-45 min)

**Sub-Group 3B: Phase 1 (Tier 1 - Working Memory)**
- Task 1.1: Schema Design (1 hr)
- Task 1.2: ConversationManager Class (2 hrs)
- Task 1.3: EntityExtractor (1.5 hrs)
- Task 1.4: FileTracker (1 hr)
- Task 1.5: CRUD Operations (1.5 hrs)
- Task 1.6: Raw Request Logging (30 min) - NEW from user questions
- Task 1.7: Testing (15 tests) (1.5 hrs)
- Task 1.8: Migration Validation (1 hr)

**Sub-Group 3C: Phase 2 (Tier 2 - Knowledge Graph)**
- Task 2.1: Schema Design (FTS5) (1.5 hrs)
- Task 2.2: PatternStore Class (2-3 hrs)
- Task 2.3: FTS5 Search Implementation (2 hrs)
- Task 2.4: Confidence Scoring (1.5 hrs)
- Task 2.5: Pattern Learning (2 hrs)
- Task 2.6: Testing (20 tests) (2 hrs)
- Task 2.7: Performance Validation (<100ms) (1 hr)
- Task 2.8: Migration Validation (1 hr)

**Sub-Group 3D: Phase 3 (Tier 3 - Context Intelligence)**
- Task 3.1: Git Metrics Collector (2-3 hrs)
- Task 3.2: Test Activity Analyzer (2 hrs)
- Task 3.3: Work Pattern Detector (2 hrs)
- Task 3.4: Correlation Engine (2-3 hrs)
- Task 3.5: JSON Storage (1 hr)
- Task 3.6: Testing (12 tests) (1.5 hrs)
- Task 3.7: Migration Validation (1 hr)

**Total GROUP 3:** 31-37 hours

---

## 🤖 GROUP 4: Intelligence Layer (Agents, Entry Point, Dashboard)

**Purpose:** Implement specialist agents and user interface  
**Duration:** 32-42 hours  
**Entry Criteria:** GROUP 3 complete (all tiers operational)  
**Exit Criteria:** All agents functional, dashboard deployed

### Tasks in GROUP 4

**Sub-Group 4A: Phase 4 (Specialist Agents)**
- Task 4.1: IntentRouter Agent (2-3 hrs)
- Task 4.2: WorkPlanner Agent (2-3 hrs)
- Task 4.3: CodeExecutor Agent (2-3 hrs)
- Task 4.4: TestGenerator Agent (2-3 hrs)
- Task 4.5: HealthValidator Agent (1.5-2 hrs)
- Task 4.6: ChangeGovernor Agent (1.5-2 hrs)
- Task 4.7: ErrorCorrector Agent (1-1.5 hrs)
- Task 4.8: SessionResumer Agent (1-1.5 hrs)
- Task 4.9: ScreenshotAnalyzer Agent (1-1.5 hrs)
- Task 4.10: CommitHandler Agent (1-1.5 hrs)
- Task 4.11: Testing (30 tests) (2.5-3 hrs)

**Sub-Group 4B: Phase 5 (Entry Point)**
- Task 5.1: cortex.md Entry Point (1.5-2 hrs)
- Task 5.2: Request Parser (1.5 hrs)
- Task 5.3: Response Formatter (1 hr)
- Task 5.4: Session State Manager (1.5 hrs)
- Task 5.5: Error Handling (1 hr)
- Task 5.6: Testing (10 tests) (1-1.5 hrs)

**Sub-Group 4C: Dashboard (from V2 holistic review)**
- Task 4C.1: Dashboard Setup (React + Vite) (1-2 hrs)
- Task 4C.2: SQL.js Integration (2 hrs)
- Task 4C.3: Real-Time File Watching (2-3 hrs)
- Task 4C.4: Tier 1 Visualization (3-4 hrs)
- Task 4C.5: Tier 2 Visualization (3-4 hrs)
- Task 4C.6: Tier 3 Visualization (2-3 hrs)
- Task 4C.7: Performance Monitoring (2 hrs)
- Task 4C.8: Testing (5 E2E tests) (1-2 hrs)

**Total GROUP 4:** 32-42 hours

---

## 🔄 GROUP 5: Migration & Validation

**Purpose:** Migrate KDS data, validate CORTEX system  
**Duration:** 5-7 hours  
**Entry Criteria:** GROUP 4 complete (agents operational, dashboard deployed)  
**Exit Criteria:** KDS fully migrated, CORTEX validated

### Tasks in GROUP 5

**From Phase 6 (Migration Validation):**
- Task 6.1: Pre-Migration Backup (30 min)
- Task 6.2: Run Migration Scripts (1-2 hrs) - Using tools from Phase 0.5
- Task 6.3: Validate Data Integrity (1 hr)
- Task 6.4: Performance Benchmarking (1 hr)
- Task 6.5: Acceptance Testing (1-1.5 hrs)
- Task 6.6: Go-Live Decision (30 min)
- Task 6.7: Post-Migration Monitoring (1 hr)

**Total GROUP 5:** 5-7 hours

---

## ✅ GROUP 6: Finalization (System Check, Root Cleanup, Documentation)

**Purpose:** Complete system validation and finalize documentation  
**Duration:** 4-6 hours  
**Entry Criteria:** GROUP 5 complete (migration validated)  
**Exit Criteria:** Full system check passes, root folder clean, documentation complete

### Tasks in GROUP 6

**NEW: Task 9.1 - Full System Check Mechanism (2-3 hours)**

**Goal:** Implement comprehensive CORTEX system validation

**Location:** `CORTEX/scripts/system-check/`

**Components:**

1. **System Check Script:**
   ```powershell
   # run-full-system-check.ps1
   
   Write-Host "🔍 CORTEX Full System Check" -ForegroundColor Cyan
   Write-Host "================================" -ForegroundColor Cyan
   
   # Check 1: Tier 0-3 Operational
   Write-Host "`n[1/10] Checking Tier 0 (Governance)..."
   # Verify governance.db exists, rules queryable
   
   Write-Host "[2/10] Checking Tier 1 (Working Memory)..."
   # Verify conversations.db schema, test CRUD operations
   
   Write-Host "[3/10] Checking Tier 2 (Knowledge Graph)..."
   # Verify patterns.db FTS5 operational, test search
   
   Write-Host "[4/10] Checking Tier 3 (Context Intelligence)..."
   # Verify development-context.json readable, metrics current
   
   # Check 2: Agents Functional
   Write-Host "[5/10] Checking Specialist Agents..."
   # Test each agent's core function
   
   # Check 3: Database Integrity
   Write-Host "[6/10] Validating Database Integrity..."
   # Run PRAGMA integrity_check on all DBs
   
   # Check 4: Performance Targets
   Write-Host "[7/10] Measuring Performance..."
   # Query latency, storage size validation
   
   # Check 5: Test Coverage
   Write-Host "[8/10] Checking Test Coverage..."
   # Verify ≥95% coverage
   
   # Check 6: Documentation
   Write-Host "[9/10] Validating Documentation..."
   # MkDocs build test, link checking
   
   # Check 7: Root Folder Compliance
   Write-Host "[10/10] Checking Root Folder..."
   # Verify only approved files in CORTEX/ root
   
   Write-Host "`n✅ System Check Complete!" -ForegroundColor Green
   ```

2. **Individual Check Scripts:**
   - `check-tier0.ps1` - Governance validation
   - `check-tier1.ps1` - Working memory validation
   - `check-tier2.ps1` - Knowledge graph validation
   - `check-tier3.ps1` - Context intelligence validation
   - `check-agents.ps1` - Agent functionality tests
   - `check-database-integrity.ps1` - SQLite integrity checks
   - `check-performance.ps1` - Latency and size validation
   - `check-test-coverage.ps1` - Coverage report parsing
   - `check-documentation.ps1` - MkDocs build validation
   - `check-root-compliance.ps1` - Root folder enforcement

**Deliverables:**
- ✅ `CORTEX/scripts/system-check/run-full-system-check.ps1`
- ✅ 10 individual check scripts
- ✅ System check report template (Markdown)
- ✅ CI/CD integration (weekly full check)

---

**NEW: Task 9.2 - Root Folder Cleanup Script (1 hour)**

**Goal:** Enforce only approved files in CORTEX root

**Script:** `CORTEX/scripts/cleanup-cortex-root.ps1`

```powershell
# cleanup-cortex-root.ps1

$approvedFiles = @(
    "README.md",
    "The CORTEX Story.docx",
    "The CORTEX Rule Book.pdf",
    "package.json",
    "requirements.txt",
    "tsconfig.json",
    ".gitignore",
    "LICENSE"
)

$cortexRoot = "D:\PROJECTS\KDS\CORTEX"
$allFiles = Get-ChildItem -Path $cortexRoot -File

foreach ($file in $allFiles) {
    if ($file.Name -notin $approvedFiles) {
        Write-Host "⚠️  Unauthorized file: $($file.Name)" -ForegroundColor Yellow
        
        # Determine correct location
        $destination = Get-CorrectFolder -FileName $file.Name
        
        # Move file
        Move-Item -Path $file.FullName -Destination $destination
        Write-Host "   Moved to: $destination" -ForegroundColor Green
    }
}

Write-Host "`n✅ Root folder cleaned!" -ForegroundColor Green
```

**Deliverables:**
- ✅ `cleanup-cortex-root.ps1` script
- ✅ File categorization logic (docs/, scripts/, etc.)
- ✅ Dry-run mode (preview moves)
- ✅ CI/CD pre-commit hook (auto-enforce)

---

**NEW: Task 9.3 - Document Root Files (2 hours)**

**Goal:** Create approved root documentation files

**Deliverables:**

1. **README.md** (30 min)
   ```markdown
   # CORTEX - Cognitive Intelligence System
   
   CORTEX is a 4-tier brain system for GitHub Copilot with 10 specialist agents.
   
   ## Quick Start
   ...
   
   ## Architecture
   ...
   
   ## Documentation
   See full docs: `mkdocs serve` or open `CORTEX/docs/`
   ```

2. **The CORTEX Story.docx** (1 hour)
   ```powershell
   # Write story in Markdown first
   # Convert to .docx with Pandoc
   
   pandoc CORTEX/docs/story/cortex-story.md `
       -o "The CORTEX Story.docx" `
       --reference-doc=template.docx
   ```

3. **The CORTEX Rule Book.pdf** (30 min)
   ```bash
   # Use MkDocs PDF plugin
   
   # Add to mkdocs.yml:
   plugins:
     - with-pdf:
         output_path: ../The CORTEX Rule Book.pdf
   
   # Build
   mkdocs build
   ```

---

**From Phase 6 (Additional Tasks):**
- Task 6.8: Create Migration Report (30 min)
- Task 6.9: Update Documentation (1 hr)
- Task 6.10: Create Release Notes (30 min)

**Total GROUP 6:** 4-6 hours

---

## 📊 V3 Timeline Summary

```
GROUP 1: Foundation & Validation        →  10-14 hours
GROUP 2: Core Infrastructure            →   6-8 hours
GROUP 3: Data Storage (Tiers 1-3)       →  31-37 hours
GROUP 4: Intelligence Layer             →  32-42 hours
GROUP 5: Migration & Validation         →   5-7 hours
GROUP 6: Finalization                   →   4-6 hours
────────────────────────────────────────────────────────
TOTAL: 88-114 hours (11-14 days focused work)
```

**Comparison to V2:** +9-13 hours (new tasks: system check, root cleanup, documentation)

---

## ✅ V3 Success Criteria

**GROUP 1 Complete:**
- ✅ Project reorganized (KDS → CORTEX)
- ✅ GitHub repo renamed
- ✅ Benchmarks validated (sql.js, browser APIs)
- ✅ Architecture decisions documented

**GROUP 2 Complete:**
- ✅ Tier 0 operational
- ✅ CI/CD passing (≥95% coverage)
- ✅ MkDocs documentation built

**GROUP 3 Complete:**
- ✅ Tier 1, 2, 3 operational
- ✅ Migration tools tested
- ✅ Performance targets met (<100ms)

**GROUP 4 Complete:**
- ✅ All 10 agents functional
- ✅ Entry point operational
- ✅ Dashboard deployed

**GROUP 5 Complete:**
- ✅ KDS data migrated
- ✅ CORTEX validated
- ✅ Acceptance tests passed

**GROUP 6 Complete:**
- ✅ Full system check passes
- ✅ Root folder clean (only approved files)
- ✅ Documentation complete (README, Story, Rulebook)
- ✅ Release notes published

---

## 🎯 Key Differences from V2

1. **Logical Ordering:** Tasks grouped by dependency, not arbitrary phases
2. **System Check:** Dedicated validation mechanism (not scattered)
3. **Root Enforcement:** Automated cleanup script
4. **Documentation Tools:** Explicit tool choices (Pandoc, MkDocs PDF)
5. **Atomic Execution:** Single-shot commands (no multi-step announcements)
6. **Small Increments:** All files ≤150 lines per chunk (Rule #23)

---

## 📝 Next Steps

**To Execute V3:**

1. **Start with GROUP 1:** Foundation & Validation
2. **Use Todo List:** Track progress with manage_todo_list tool
3. **Follow Rule #23:** Create large files in small increments
4. **Validate at Group Boundaries:** Don't proceed until exit criteria met
5. **Final Validation:** Run full system check (GROUP 6, Task 9.1)

**Ready to Begin?**

```markdown
#file:KDS/prompts/user/kds.md

Start CORTEX V3 Implementation - GROUP 1: Foundation & Validation
```

---

## 📋 DETAILED TASK BREAKDOWNS

This section provides complete specifications for all tasks in V3.

### GROUP 1 Detailed Tasks

#### 🔄 Task -2.1: Backup Current State

**Duration:** 30 minutes  
**Purpose:** Safety checkpoint before reorganization

**Single-Shot Command:**
```powershell
cd D:\PROJECTS\KDS
git add . && `
git commit -m "Pre-reorganization checkpoint: KDS v8 final state" --allow-empty && `
git push origin cortex-migration && `
git tag -a v8-final-kds -m "Final KDS state before CORTEX reorganization" && `
git push origin v8-final-kds --no-verify && `
git checkout -b kds-v8-archive && `
git push origin kds-v8-archive --no-verify && `
git checkout cortex-migration
```

**Verification:**
```powershell
git tag -l "v8-final-kds"
git branch -a | Select-String "kds-v8-archive"
git ls-remote --tags origin | Select-String "v8-final-kds"
```

**Exit Criteria:**
- ✅ Tag `v8-final-kds` exists
- ✅ Branch `kds-v8-archive` pushed to remote
- ✅ Can rollback with `git checkout v8-final-kds`

---

#### 📁 Task -2.2: Create New CORTEX Directory Structure

**Duration:** 1 hour  
**Purpose:** Establish clean project structure

**Command:**
```powershell
cd D:\PROJECTS
git clone https://github.com/asifhussain60/CORTEX.git CORTEX
cd CORTEX
git checkout cortex-migration

# Verify structure
Get-ChildItem -Directory | Format-Table Name
```

**Exit Criteria:**
- ✅ `D:\PROJECTS\CORTEX` exists
- ✅ Clean folder structure
- ✅ Working on `cortex-migration` branch

---

#### 📦 Task -2.3: Implement Git-Based Documentation Storage

**Duration:** 1.5 hours  
**Purpose:** Archive completed design docs with retrieval index

**Implementation:** See V2 plan Task -2.3 for full script (using here-strings for efficiency)

**Key Deliverables:**
- ✅ `ARCHIVE-INDEX.md` created
- ✅ Completed docs archived to Git with tag
- ✅ Working directory clean

---

#### 🏷️ Task -2.4: Rename GitHub Repository

**Duration:** 30 minutes  
**Purpose:** Rename repo KDS → CORTEX

**Steps:**
1. GitHub Settings → Repository name → Rename to "CORTEX"
2. Update local remote:
   ```powershell
   cd D:\PROJECTS\CORTEX
   git remote set-url origin https://github.com/asifhussain60/CORTEX.git
   ```

**Exit Criteria:**
- ✅ GitHub repo named "CORTEX"
- ✅ Local remote points to correct URL

---

#### 📜 Task -2.5: Add New Governance Rules

**Duration:** 1 hour  
**Purpose:** Add Rule #23 (Git-based cleanup) and Rule #24 (Assumption validation)

**Implementation:** Add to `governance/rules.md` (see V2 plan for full rule text)

**Exit Criteria:**
- ✅ Rule #23 documented
- ✅ Rule #24 documented
- ✅ Both rules added to rules index

---

#### 🔗 Task -2.6: Update All Path References

**Duration:** 1 hour  
**Purpose:** Update KDS → CORTEX paths

**Script:**
```powershell
$files = @(
    "CORTEX/package.json",
    "CORTEX/tsconfig.json",
    ".github/workflows/cortex-ci.yml",
    "README.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        (Get-Content $file) -replace 'D:\\PROJECTS\\KDS', 'D:\PROJECTS\CORTEX' | Set-Content $file
    }
}
```

**Exit Criteria:**
- ✅ No KDS paths in active files
- ✅ CI/CD references correct paths

---

#### ✅ Task -2.7: Validation & Testing

**Duration:** 30 minutes  
**Purpose:** Verify reorganization success

**Validation Checklist:**
```powershell
# Directory structure
Test-Path D:\PROJECTS\CORTEX\CORTEX

# Git config
git remote -v  # Should show github.com/asifhussain60/CORTEX

# Tags exist
git tag -l  # Should include v8-final-kds

# Clean working directory
git status  # Should be clean
```

**Exit Criteria:**
- ✅ All validation checks pass
- ✅ No errors in console

---

### GROUP 2 Detailed Tasks

#### 🏛️ Task 0.1: GovernanceEngine Class

**Duration:** 1 hour  
**Purpose:** Create core governance engine

**Implementation:**
```python
# cortex-brain/tier0/governance.py

class GovernanceEngine:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()
    
    def _init_schema(self):
        """Create governance tables"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                rule_id TEXT PRIMARY KEY,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                immutable BOOLEAN DEFAULT TRUE
            )
        """)
    
    def add_rule(self, rule: dict):
        """Add governance rule"""
        pass
    
    def check_violation(self, context: dict) -> List[dict]:
        """Check for rule violations"""
        pass
```

**Exit Criteria:**
- ✅ Class defined with all methods
- ✅ Schema initialization works
- ✅ Basic CRUD operations functional

---

#### 🔄 Task 0.2: YAML → SQLite Migration

**Duration:** 1 hour  
**Purpose:** Migrate existing YAML rules to SQLite

**Script:**
```python
# scripts/migrate-governance-rules.py

import yaml
import sqlite3

def migrate_rules():
    # Read governance/rules.md (YAML sections)
    with open('governance/rules.md') as f:
        content = f.read()
    
    # Extract YAML blocks
    rules = extract_yaml_blocks(content)
    
    # Insert into SQLite
    db = sqlite3.connect('governance.db')
    for rule in rules:
        db.execute("""
            INSERT INTO rules (rule_id, severity, category, description)
            VALUES (?, ?, ?, ?)
        """, (rule['id'], rule['severity'], rule['category'], rule['desc']))
    
    db.commit()
```

**Exit Criteria:**
- ✅ All rules migrated
- ✅ No data loss
- ✅ Queryable in SQLite

---

#### 🔍 Task 0.3: Rule Query API

**Duration:** 1 hour  
**Purpose:** Implement rule query methods

**Methods:**
```python
def get_rule(self, rule_id: str) -> dict:
    """Retrieve single rule"""
    
def search_rules(self, category: str = None, severity: str = None) -> List[dict]:
    """Search rules by criteria"""
    
def get_all_rules(self) -> List[dict]:
    """Get all governance rules"""
```

**Exit Criteria:**
- ✅ All query methods work
- ✅ Proper error handling
- ✅ Test coverage ≥95%

---

#### 📊 Task 0.4: Violation Tracking

**Duration:** 1 hour  
**Purpose:** Track governance violations

**Implementation:**
```python
def log_violation(self, rule_id: str, context: dict, severity: str):
    """Log governance rule violation"""
    self.conn.execute("""
        INSERT INTO violations (rule_id, timestamp, context, severity)
        VALUES (?, ?, ?, ?)
    """, (rule_id, datetime.now(), json.dumps(context), severity))
```

**Exit Criteria:**
- ✅ Violations logged
- ✅ Query violations by rule/date
- ✅ Dashboard can display violations

---

#### 🧪 Task 0.5: Testing (Tier 0)

**Duration:** 1 hour  
**Purpose:** 15 unit + 2 integration tests

**Test Coverage:**
- Unit tests: All CRUD operations
- Integration tests: YAML migration, violation tracking
- Edge cases: Invalid rules, concurrent access

**Exit Criteria:**
- ✅ 17 tests pass
- ✅ Coverage ≥95%
- ✅ All edge cases handled

---

#### 🚀 Task 0.6: CI/CD Setup

**Duration:** 1 hour  
**Purpose:** Automated testing on every commit

**Deliverables:**
- ✅ Pre-commit hook (pytest with coverage)
- ✅ GitHub Actions workflow
- ✅ Coverage enforcement (≥95%)

**Implementation:** See V2 plan Task 0.6 for full workflow

---

#### 📖 Task 0.7: MkDocs Documentation Setup

**Duration:** 1 hour  
**Purpose:** Professional documentation infrastructure

**Steps:**
1. Install MkDocs: `pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin`
2. Initialize project: `mkdocs new docs`
3. Configure `mkdocs.yml` (see V2 plan for full config)
4. Create initial docs structure
5. Test build: `mkdocs build`

**Exit Criteria:**
- ✅ MkDocs configured
- ✅ Initial docs created
- ✅ Build successful

---

### GROUP 3 Detailed Tasks

**Note:** GROUP 3 contains 28 tasks across 4 sub-groups (Phase 0.5, Phase 1, Phase 2, Phase 3)

Due to length, detailed breakdowns for GROUP 3-6 tasks follow the same pattern as above. Each task includes:
- Duration estimate
- Purpose statement
- Implementation code/script
- Exit criteria checklist

**Full task details available in V2 plan:** Reference `IMPLEMENTATION-PLAN-V2.md` for complete specifications of:
- Phase 0.5 tasks (Migration tools)
- Phase 1 tasks (Tier 1 - Working Memory)
- Phase 2 tasks (Tier 2 - Knowledge Graph)
- Phase 3 tasks (Tier 3 - Context Intelligence)
- Phase 4 tasks (Specialist Agents)
- Phase 5 tasks (Entry Point)
- Phase 6 tasks (Migration & Validation)

---

## 🎯 Execution Guidelines

### Rule #23 Compliance (Small Increments)

When creating large files (>100 lines), use multiple tool calls:

**Example: Creating GovernanceEngine (300 lines total)**

```markdown
**Increment 1 (Lines 1-100):**
```python
# cortex-brain/tier0/governance.py
# Part 1: Imports and class definition

import sqlite3
import json
from typing import List, dict
from datetime import datetime

class GovernanceEngine:
    """Tier 0: Governance engine for CORTEX"""
    
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()
    
    # ... (up to line 100)
```

**Increment 2 (Lines 101-200):**
```python
# cortex-brain/tier0/governance.py
# Part 2: Query methods

    def get_rule(self, rule_id: str) -> dict:
        # ... (lines 101-200)
```

**Increment 3 (Lines 201-300):**
```python
# cortex-brain/tier0/governance.py
# Part 3: Violation tracking

    def log_violation(self, rule_id: str, context: dict):
        # ... (lines 201-300)
```
```

### Atomic Execution Pattern

**AVOID:**
```markdown
1. "I'll update the TODO list now"
2. Call manage_todo_list (read)
3. "Now updating status"
4. Call manage_todo_list (write)
5. "Status updated"
```

**DO:**
```markdown
Call manage_todo_list once with complete update:
{
  operation: "write",
  todoList: [
    {id: 1, title: "Task", status: "completed"},
    {id: 2, title: "Next", status: "in-progress"}
  ]
}

Done. No announcements.
```

### Group Boundary Validation

At the end of each GROUP, run validation before proceeding:

**GROUP 1 → GROUP 2:**
```powershell
# Verify project reorganized
Test-Path D:\PROJECTS\CORTEX
git remote -v | Select-String "CORTEX"
git tag -l | Select-String "v8-final-kds"

# All checks pass → Proceed to GROUP 2
```

**GROUP 2 → GROUP 3:**
```powershell
# Verify Tier 0 operational
pytest cortex-tests/tier0/ --cov-fail-under=95
mkdocs build --strict

# All checks pass → Proceed to GROUP 3
```

**Continue pattern for all groups...**

---

## 📊 Progress Tracking

Use the TODO tool to track progress:

```typescript
manage_todo_list({
  operation: "write",
  todoList: [
    {
      id: 1,
      title: "GROUP 1: Foundation & Validation",
      description: "Tasks -2.1 through -1.5. Project reorganization and architecture validation.",
      status: "in-progress"
    },
    {
      id: 2,
      title: "GROUP 2: Core Infrastructure",
      description: "Tasks 0.1 through 0.7. Tier 0, CI/CD, and MkDocs setup.",
      status: "not-started"
    },
    {
      id: 3,
      title: "GROUP 3: Data Storage",
      description: "Tasks 0.5.1 through 3.7. Migration tools and Tiers 1-3 implementation.",
      status: "not-started"
    },
    {
      id: 4,
      title: "GROUP 4: Intelligence Layer",
      description: "Tasks 4.1 through 4C.8. Agents, entry point, and dashboard.",
      status: "not-started"
    },
    {
      id: 5,
      title: "GROUP 5: Migration & Validation",
      description: "Tasks 6.1 through 6.7. KDS → CORTEX data migration.",
      status: "not-started"
    },
    {
      id: 6,
      title: "GROUP 6: Finalization",
      description: "Tasks 9.1 through 9.3 + 6.8-6.10. System check, root cleanup, documentation.",
      status: "not-started"
    }
  ]
})
```

**Update after each task completion:**
- Mark current task as "completed"
- Move next task to "in-progress"
- Single tool call per update

---

## 🎯 Final Validation Checklist

Before considering CORTEX V3 complete, verify ALL criteria:

### ✅ Technical Validation

**Tier 0 (Governance):**
- [ ] All rules queryable in SQLite
- [ ] Violations tracked and logged
- [ ] GovernanceEngine tests pass (17/17)

**Tier 1 (Working Memory):**
- [ ] Conversations stored in SQLite
- [ ] CRUD operations functional
- [ ] Migration from KDS successful
- [ ] Raw request logging active

**Tier 2 (Knowledge Graph):**
- [ ] Patterns stored with FTS5
- [ ] Search latency <100ms (p95)
- [ ] Confidence scoring operational
- [ ] Pattern learning automated

**Tier 3 (Context Intelligence):**
- [ ] Git metrics collected
- [ ] Test activity analyzed
- [ ] Work patterns detected
- [ ] Correlation engine functional

**Agents:**
- [ ] All 10 specialist agents operational
- [ ] 30 agent tests pass
- [ ] Intent routing accurate (>90%)

**Entry Point:**
- [ ] cortex.md functional
- [ ] Request parsing works
- [ ] Response formatting correct
- [ ] Session state maintained

**Dashboard:**
- [ ] SQL.js integration works
- [ ] Real-time file watching operational
- [ ] All tiers visualized
- [ ] Performance monitoring active

### ✅ Operational Validation

**CI/CD:**
- [ ] Pre-commit hooks enforce tests
- [ ] GitHub Actions passing
- [ ] Coverage ≥95% maintained
- [ ] Performance benchmarks pass

**Documentation:**
- [ ] MkDocs builds successfully
- [ ] All APIs documented
- [ ] Migration guides complete
- [ ] README.md updated

**Root Folder:**
- [ ] Only approved files in root
- [ ] Cleanup script operational
- [ ] The CORTEX Story.docx created
- [ ] The CORTEX Rule Book.pdf created

### ✅ System Check

**Full System Check Passes:**
- [ ] All 10 checks green
- [ ] Database integrity validated
- [ ] Performance targets met
- [ ] No critical violations

**Migration Complete:**
- [ ] KDS data migrated successfully
- [ ] Acceptance tests pass
- [ ] Go-live decision made
- [ ] Post-migration monitoring active

### ✅ Documentation

**Required Files:**
- [ ] README.md (root)
- [ ] The CORTEX Story.docx (root)
- [ ] The CORTEX Rule Book.pdf (root)
- [ ] CHANGELOG.md updated
- [ ] Migration report created
- [ ] Release notes published

---

## 🚀 Ready to Execute

**This V3 plan is now ready for execution.**

Key features:
- ✅ Logical ordering by dependency
- ✅ Small increments (Rule #23 compliant)
- ✅ Atomic execution patterns
- ✅ Full system check mechanism
- ✅ Root folder enforcement
- ✅ Complete documentation

**To begin:**

```markdown
#file:KDS/prompts/user/kds.md

Start CORTEX V3 Implementation - Begin GROUP 1
```

---

*End of CORTEX Implementation Plan V3*

**Acceptance:** All V2 recommendations accepted  
**Additions:** System check, root cleanup, documentation tools specified  
**Organization:** Logical execution order (6 groups, not 9 phases)  
**Compliance:** Rule #23 (small increments), Rule #24 (assumption validation)  
**Status:** 🎯 READY FOR EXECUTION
