# CORTEX Migration Strategy

**Date:** 2025-11-05  
**From:** KDS v8  
**To:** CORTEX v1.0  
**Approach:** Clean slate redesign on new branch

---

## Git Workflow

### Step 1: Commit Current State

**Purpose:** Preserve complete KDS history before redesign

```bash
# Ensure all work is committed
git status

# Stage all files
git add .

# Comprehensive commit message
git commit -m "feat(kds): Complete KDS v8 before CORTEX redesign

KDS v8 Implementation Summary:
- Phase 0: Enforcement layer (pre-commit validation)
- Phase 1: Live data dashboard (real-time events)
- Phase 2: Features tab (scanner + test runner) - PARTIAL
- Phase 3.5: Git commit tracking
- 6-tier BRAIN architecture
- 10 specialist agents
- Conversation memory (Tier 1)
- Knowledge graph (Tier 2)
- Development context (Tier 3)
- Event stream (Tier 4)

Known Issues:
- Runtime errors (JSON parsing, storyboard)
- Some features documented but not implemented
- BRAIN restoration needed (see BRAIN-RESTORATION-PLAN.md)

This commit preserves KDS before clean-slate CORTEX redesign.
See cortex-design/ for redesign plan.

Stats:
- 4,340 lines kds.md
- 1,249 commits analyzed
- 14 conversations logged
- 3,247 patterns in knowledge graph"

# Push to remote (CRITICAL - preserves history)
git push origin main
```

**Validation:**
```bash
# Verify commit succeeded
git log -1 --oneline

# Verify push succeeded
git ls-remote origin main
```

---

### Step 2: Create Redesign Branch

**Purpose:** Isolate CORTEX development, enable safe experimentation

```bash
# Create and switch to redesign branch
git checkout -b cortex-redesign

# Verify branch created
git branch --show-current
# Expected output: cortex-redesign
```

**Branch Strategy:**
```
main (KDS v8 - preserved)
  └── cortex-redesign (clean slate)
       ├── phase0-instinct
       ├── phase1-working-memory
       ├── phase2-long-term-knowledge
       ├── phase3-context-intelligence
       ├── phase4-agents
       ├── phase5-entry-point
       └── phase6-migration-validation
            └── (merge back to main after validation)
```

---

### Step 3: Extract Feature Inventory

**Purpose:** Document every KDS capability before deletion

**Process:**
```bash
# Create comprehensive feature inventory
# (Done in feature-inventory/ folder)

# Files to create:
# - tier0-instinct.md (governance rules)
# - tier1-working-memory.md (conversation features)
# - tier2-knowledge-graph.md (learning patterns)
# - tier3-context.md (git/test metrics)
# - agents-list.md (10 specialist agents)
# - scripts-inventory.md (PowerShell automation)
# - workflows-catalog.md (TDD, commit, BRAIN update)
# - dashboard-features.md (WPF dashboard V8)
```

**Validation Checklist:**
- [ ] All tiers documented
- [ ] All agents cataloged
- [ ] All scripts inventoried
- [ ] All workflows captured
- [ ] All dashboard features listed
- [ ] All tests documented
- [ ] All governance rules extracted

---

### Step 4: Clean Slate (Delete KDS Folders)

**Purpose:** Start fresh with optimal structure

**⚠️ CRITICAL:** Only proceed after:
- ✅ Step 1 complete (committed and pushed)
- ✅ Step 2 complete (on cortex-redesign branch)
- ✅ Step 3 complete (feature inventory done)

```bash
# Verify you're on cortex-redesign branch
git branch --show-current
# MUST output: cortex-redesign

# Delete legacy folders (keep cortex-design/)
Remove-Item -Path "kds-brain" -Recurse -Force
Remove-Item -Path "scripts" -Recurse -Force
Remove-Item -Path "prompts" -Recurse -Force
Remove-Item -Path "governance" -Recurse -Force
Remove-Item -Path "sessions" -Recurse -Force
Remove-Item -Path "dashboard-wpf" -Recurse -Force
Remove-Item -Path "docs" -Recurse -Force -Exclude "cortex-design"
Remove-Item -Path "tests" -Recurse -Force
Remove-Item -Path "tooling" -Recurse -Force
Remove-Item -Path "_archive" -Recurse -Force
Remove-Item -Path "backups" -Recurse -Force
Remove-Item -Path "hooks" -Recurse -Force
Remove-Item -Path "knowledge" -Recurse -Force
Remove-Item -Path "reports" -Recurse -Force
Remove-Item -Path "templates" -Recurse -Force

# Keep only:
# - cortex-design/ (our redesign specs)
# - .git/ (repository history)
# - .gitignore
# - README.md (will be updated)
```

**Validation:**
```bash
# Verify clean state
Get-ChildItem -Directory

# Expected output:
# - cortex-design/
# - .git/
```

---

### Step 5: Create CORTEX Folder Structure

**Purpose:** Implement optimal organization from day 1

```bash
# Create root folders
New-Item -ItemType Directory -Path "cortex-brain"
New-Item -ItemType Directory -Path "cortex-agents"
New-Item -ItemType Directory -Path "cortex-scripts"
New-Item -ItemType Directory -Path "cortex-tests"
New-Item -ItemType Directory -Path "cortex-docs"
New-Item -ItemType Directory -Path "cortex-governance"

# Create tier-specific folders
New-Item -ItemType Directory -Path "cortex-brain/tier0-instinct"
New-Item -ItemType Directory -Path "cortex-brain/tier1-working-memory"
New-Item -ItemType Directory -Path "cortex-brain/tier2-long-term-knowledge"
New-Item -ItemType Directory -Path "cortex-brain/tier3-context-intelligence"

# Create agent folders
New-Item -ItemType Directory -Path "cortex-agents/internal"
New-Item -ItemType Directory -Path "cortex-agents/user"
New-Item -ItemType Directory -Path "cortex-agents/abstractions"

# Create test folders
New-Item -ItemType Directory -Path "cortex-tests/unit"
New-Item -ItemType Directory -Path "cortex-tests/integration"
New-Item -ItemType Directory -Path "cortex-tests/regression"
New-Item -ItemType Directory -Path "cortex-tests/performance"

# Create script folders
New-Item -ItemType Directory -Path "cortex-scripts/brain"
New-Item -ItemType Directory -Path "cortex-scripts/git"
New-Item -ItemType Directory -Path "cortex-scripts/monitoring"
New-Item -ItemType Directory -Path "cortex-scripts/setup"
```

**Complete Structure:**
```
CORTEX/
├── cortex-design/              # Redesign specs (temporary)
│   ├── feature-inventory/
│   ├── architecture/
│   ├── phase-plans/
│   └── test-specifications/
│
├── cortex-brain/               # BRAIN storage (4 tiers)
│   ├── tier0-instinct/         # Governance rules (IMMUTABLE)
│   ├── tier1-working-memory/   # Last 20 conversations (SQLite)
│   ├── tier2-long-term-knowledge/  # Patterns (SQLite + FTS5)
│   └── tier3-context-intelligence/ # Git/test metrics (JSON cache)
│
├── cortex-agents/              # Specialist agents
│   ├── internal/               # Internal agents (executor, tester, etc.)
│   ├── user/                   # User-facing (cortex.md entry point)
│   └── abstractions/           # Shared interfaces (DIP)
│
├── cortex-scripts/             # Automation scripts
│   ├── brain/                  # BRAIN management
│   ├── git/                    # Git automation
│   ├── monitoring/             # Health checks
│   └── setup/                  # Installation
│
├── cortex-tests/               # Comprehensive test suite
│   ├── unit/                   # Unit tests per tier/agent
│   ├── integration/            # Cross-tier integration tests
│   ├── regression/             # Cumulative regression suite
│   └── performance/            # Benchmarks and performance tests
│
├── cortex-docs/                # Documentation
│   ├── architecture/           # System design docs
│   ├── guides/                 # User guides
│   └── api/                    # API references
│
├── cortex-governance/          # Immutable rules (Tier 0)
│   ├── core-principles.md      # SOLID, TDD, DoR/DoD
│   ├── tier-boundaries.md      # Data separation rules
│   └── protection-rules.md     # Brain protection contracts
│
├── .git/                       # Git repository
├── .gitignore                  # Git ignore rules
└── README.md                   # Project overview
```

---

### Step 6: Phase-by-Phase Development

**Each phase commits separately:**

```bash
# Phase 0: Instinct Layer
# (build tier 0 + tests)
git add cortex-governance/ cortex-tests/unit/tier0-tests.ps1
git commit -m "feat(cortex): Phase 0 - Instinct Layer complete

- Implemented Tier 0 governance rules
- Created core-principles.md (TDD, SOLID, DoR/DoD)
- Created tier-boundaries.md (data separation)
- Created protection-rules.md (BRAIN protection)
- Unit tests: 15/15 passing
- Performance: Rule lookup <1ms

Tests: ✅ All passing
Benchmarks: ✅ All targets met"

# Phase 1: Working Memory
# (build tier 1 + tests)
git add cortex-brain/tier1-working-memory/ cortex-tests/unit/tier1-tests.ps1
git commit -m "feat(cortex): Phase 1 - Working Memory (STM) complete

- Implemented Tier 1 SQLite storage
- FIFO queue (last 20 conversations)
- Entity extraction and indexing
- Conversation boundary detection
- Unit tests: 42/42 passing
- Integration tests: 8/8 passing
- Performance: Queries <50ms

Tests: ✅ All passing
Benchmarks: ✅ All targets met"

# Repeat for each phase...
```

---

### Step 7: Migration Validation

**Before merging to main:**

```bash
# Run complete test suite
.\cortex-tests\regression\run-all-tests.ps1

# Expected output:
# Phase 0: ✅ 15/15 tests passing
# Phase 1: ✅ 50/50 tests passing
# Phase 2: ✅ 67/67 tests passing
# Phase 3: ✅ 38/38 tests passing
# Phase 4: ✅ 125/125 tests passing
# Phase 5: ✅ 45/45 tests passing
# Phase 6: ✅ 30/30 tests passing (feature parity)
# TOTAL: ✅ 370/370 tests passing

# Run performance benchmarks
.\cortex-tests\performance\run-benchmarks.ps1

# Expected output:
# Query latency: ✅ 87ms (target <100ms)
# Storage size: ✅ 273KB (target <300KB)
# Learning cycle: ✅ 1.8min (target <2min)
# Context refresh: ✅ 8.2sec (target <10sec)
```

---

### Step 8: Repository Rename

**After validation complete:**

```bash
# Commit final validation
git add .
git commit -m "feat(cortex): Migration validation complete

- All 370 tests passing
- All performance benchmarks met
- 100% KDS feature parity verified
- Ready for repository rename and merge

Next: Rename KDS → CORTEX repository"

# Merge to main
git checkout main
git merge cortex-redesign --no-ff -m "feat: Merge CORTEX redesign (clean slate)

Complete redesign of KDS → CORTEX with:
- Efficient 4-tier BRAIN architecture
- SQLite storage (10-100x faster queries)
- 370-test comprehensive test suite
- 100% feature parity with KDS v8
- Performance targets exceeded

See cortex-design/ for redesign documentation.

Stats:
- Storage: 273KB (target <300KB) ✅
- Query latency: 87ms (target <100ms) ✅
- Learning cycle: 1.8min (target <2min) ✅
- Test coverage: 95%+ ✅"

# Push to remote
git push origin main
```

**GitHub Repository Rename:**
1. Go to repository Settings
2. Rename `KDS` → `CORTEX`
3. Update description: "CORTEX - Cerebral Orchestration and Runtime Task EXecution"
4. Update topics: `ai-assistant`, `brain-architecture`, `cognitive-system`, `tdd`, `solid-principles`

**Local Repository Update:**
```bash
# Update remote URL (after GitHub rename)
git remote set-url origin https://github.com/asifhussain60/CORTEX.git

# Verify
git remote -v
```

---

## Rollback Plan

**If migration fails at any phase:**

```bash
# Abandon cortex-redesign branch
git checkout main

# Delete redesign branch
git branch -D cortex-redesign

# Restart from clean state
git checkout -b cortex-redesign
```

**If migration succeeds but issues found after merge:**

```bash
# Revert merge commit
git revert -m 1 <merge-commit-hash>

# Or reset to pre-merge state
git reset --hard <commit-before-merge>

# Force push (if necessary)
git push origin main --force
```

---

## Success Criteria

**Migration complete when:**
- ✅ All phases committed
- ✅ All tests passing (370/370)
- ✅ All benchmarks met
- ✅ KDS feature parity verified
- ✅ cortex-redesign merged to main
- ✅ Repository renamed to CORTEX
- ✅ Documentation updated
- ✅ Team notified of rename

---

**Status:** Migration strategy defined  
**Next:** Begin feature inventory extraction
