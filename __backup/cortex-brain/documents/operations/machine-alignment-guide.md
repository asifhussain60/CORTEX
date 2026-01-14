# Machine Alignment Guide - CORTEX 6.0 Enhanced Architecture

**Purpose:** Comprehensive instructions for pulling and aligning development machines with CORTEX 6.0's enhanced governance architecture  
**Target Audience:** Developers setting up new machines or syncing existing ones  
**Version:** 6.0.1  
**Last Updated:** 2026-01-12  
**Author:** Asif Hussain  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Overview

CORTEX 6.0 introduces a **4-tier governance architecture** with middle-layer enforcement components that ensure production-grade integrity. This guide ensures your machine properly implements:

1. **Governance Merger** (Tier 0-3 rule precedence)
2. **Governance Checkpoint Middleware** (Runtime enforcement)
3. **Governance-to-Todo Pipeline** (Task generation from rules)
4. **Audit Integration** (Tamper-proof compliance tracking)
5. **TDD-Master Enforcement** (Test-first development)

---

## 🔄 Quick Start (5 Minutes)

```bash
# 1. Pull latest CORTEX6 branch
cd /path/to/CORTEX
git fetch origin
git checkout CORTEX6
git pull origin CORTEX6

# 2. Verify 4-tier governance structure
ls -la cortex-brain/tier0/governance/core-rules.yaml
ls -la cortex-brain/tier1/tracking/progress-tracker.json
ls -la cortex-brain/tier2/
ls -la cortex-brain/tier3/

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run alignment verification
python3 scripts/verify_integrity.py --check-governance

# 5. Test governance enforcement
pytest tests/governance/ -v --tb=short

# 6. Validate audit trail
python3 scripts/verify_audit_trail.py --last-7-days
```

**Expected Output:**
```
✅ 4-tier governance structure: VALID
✅ 23 CORE rules loaded from tier0
✅ GovernanceMerger operational (merge time: 42ms)
✅ Audit trail integrity: 100% (hash chain valid)
✅ 48/48 governance tests passing
```

---

## 📁 Critical Directory Structure

### What Your Machine MUST Have

```
CORTEX/
├── cortex-brain/
│   ├── tier0/                          # ⭐ HIGHEST precedence
│   │   └── governance/
│   │       └── core-rules.yaml         # 23 SKULL rules (immutable)
│   ├── tier1/                          # ⭐ HIGH precedence
│   │   ├── tracking/
│   │   │   └── progress-tracker.json   # Active epic state
│   │   └── acceptance-criteria/
│   │       └── AC-INDEX.yaml           # AC registry with titles
│   ├── tier2/                          # ⭐ MEDIUM precedence
│   │   └── engineering-standards/      # Company practices
│   ├── tier3/                          # ⭐ LOW precedence
│   │   └── learned-patterns/           # Knowledge practices
│   └── database/
│       └── governance.db               # SQLite audit log (WAL mode)
├── src/
│   ├── orchestrators/
│   │   ├── core/
│   │   │   ├── governance_merger.py              # ⭐ 4-tier rule merging
│   │   │   ├── governance_to_todo_pipeline.py    # ⭐ Task generation
│   │   │   └── master_orchestrator.py            # Central controller
│   │   ├── middleware/
│   │   │   └── governance_checkpoint.py          # ⭐ Runtime enforcement
│   │   └── audit_logger.py                       # ⭐ Tamper-proof logging
│   ├── tier0/
│   │   └── governance_engine.py        # Rule validation logic
│   └── infrastructure/
│       └── enhanced_audit_logger.py    # Hash chain implementation
├── tests/
│   └── governance/
│       ├── test_governance_merger.py
│       ├── test_governance_checkpoint.py
│       └── test_governance_tools.py
└── scripts/
    ├── verify_integrity.py
    ├── verify_audit_trail.py
    └── audit_based_evidence_validator.py
```

---

## 🏗️ Enhanced Architecture Components

### 1. GovernanceMerger (Core Middle Component)

**File:** `src/orchestrators/core/governance_merger.py`

**Purpose:** Merges 4 tiers of governance rules with precedence-based conflict resolution.

**Key Features:**
- **4-tier loading:** CORTEX Core (Tier 0) → Business (Tier 1) → Company (Tier 2) → Knowledge (Tier 3)
- **Conflict resolution:** Higher tier wins (Tier 0 beats all)
- **Performance:** <50ms merge time with caching
- **Unified output:** Single instruction set for orchestrators

**Verification:**
```bash
# Test merger directly
python3 -c "
from src.orchestrators.core.governance_merger import GovernanceMerger
merger = GovernanceMerger()
result = merger.merge_all_tiers()
print(f'Rules merged: {len(result.unified_rules)}')
print(f'Conflicts: {len(result.conflicts)}')
print(f'Merge time: {result.merge_time_ms}ms')
"
```

**Expected:**
```
Rules merged: 23+ (depending on Tier 1-3 additions)
Conflicts: 0-2 (auto-resolved)
Merge time: <50ms
```

**Integration Points:**
- **MasterOrchestrator** calls `merge_all_tiers()` on startup
- **TodoManager** uses merged rules to generate tasks
- **TDD-Master** validates against merged CORE-019 rule

---

### 2. GovernanceCheckpointMiddleware (Runtime Enforcer)

**File:** `src/orchestrators/middleware/governance_checkpoint.py`

**Purpose:** Runtime enforcement of SKULL rules during orchestrator execution.

**Key Features:**
- **Pre-execution checks:** Validates state before operations
- **BLOCKING enforcement:** Stops violating operations (CORE-008, CORE-017, CORE-019)
- **WARNING alerts:** Logs risky patterns (CORE-001 >500 lines)
- **Audit integration:** Every check logged with correlation ID

**Verification:**
```bash
# Test checkpoint enforcement
python3 -c "
from src.orchestrators.middleware.governance_checkpoint import GovernanceCheckpointMiddleware
middleware = GovernanceCheckpointMiddleware()
result = middleware.check_tdd_enforcement({'operation': 'implement', 'tests_exist': False})
print(f'TDD Check: {result.passed}')
print(f'Level: {result.level}')
print(f'Message: {result.message}')
"
```

**Expected (when tests missing):**
```
TDD Check: False
Level: BLOCKING
Message: CORE-008 violation: TDD enforcement requires tests before implementation
```

**Integration Points:**
- **MasterOrchestrator** wraps all operations with middleware
- **TDD-Master** pre-checks via `check_tdd_enforcement()`
- **Planning v5** validates via `check_planning_standards()`

---

### 3. Governance-to-Todo Pipeline (Task Generator)

**File:** `src/orchestrators/core/governance_to_todo_pipeline.py`

**Purpose:** Converts governance rules into actionable TODO items for TodoManager.

**Key Features:**
- **Rule parsing:** Extracts required actions from governance rules
- **Task creation:** Generates tasks with dependencies and priorities
- **Progress tracking:** Updates `progress-tracker.json`
- **AC-ID linking:** Associates tasks with acceptance criteria

**Verification:**
```bash
# Test pipeline directly
python3 -c "
from src.orchestrators.core.governance_to_todo_pipeline import GovernanceToTodoPipeline
pipeline = GovernanceToTodoPipeline()
tasks = pipeline.extract_required_actions({'rule_id': 'CORE-008', 'name': 'TDD Enforcement'})
print(f'Tasks generated: {len(tasks)}')
for task in tasks:
    print(f'  - {task.title} (priority: {task.priority})')
"
```

**Expected:**
```
Tasks generated: 3
  - Write failing test (RED phase) (priority: HIGH)
  - Implement minimal code (GREEN phase) (priority: HIGH)
  - Refactor and improve (REFACTOR phase) (priority: MEDIUM)
```

**Integration Points:**
- **MasterOrchestrator** calls `extract_required_actions()` on new requests
- **TodoManager** persists tasks to `progress-tracker.json`
- **AC-INDEX** registers AC-IDs for tracking

---

### 4. Enhanced Audit Logger (Tamper-Proof Trail)

**File:** `src/infrastructure/enhanced_audit_logger.py`

**Purpose:** Immutable audit trail with hash chain integrity.

**Key Features:**
- **Hash chaining:** Each log entry hashes previous entry
- **SQLite WAL mode:** Atomic writes, no partial corruption
- **Correlation tracking:** Links related operations
- **Retention policies:** Auto-cleanup by severity (7-90 days)
- **Query API:** Temporal and categorical filtering

**Verification:**
```bash
# Verify audit trail integrity
python3 scripts/verify_audit_trail.py --check-integrity

# Query recent governance events
python3 -m src.main "audit query --category GOVERNANCE --last 1h"
```

**Expected:**
```
✅ Hash chain integrity: VALID (1,247 entries checked)
✅ No broken links detected
✅ Tamper-proof guarantee: MAINTAINED

Recent governance events:
2026-01-12 14:32:01 | GOVERNANCE | INFO | CORE-008 validated: TDD phase RED
2026-01-12 14:32:15 | GOVERNANCE | INFO | CORE-008 validated: TDD phase GREEN
```

**Integration Points:**
- **All orchestrators** log via `EnterpriseAuditLogger.log()`
- **GovernanceCheckpointMiddleware** audits all checks
- **Evidence bundles** reference audit entries for proof

---

## ⚙️ Detailed Setup Instructions

### Step 1: Pre-Flight Checks (2 minutes)

```bash
# Verify Python version (3.9+ required)
python3 --version  # Should show 3.9.0 or higher

# Verify Git version
git --version  # Should show 2.30.0 or higher

# Check disk space (minimum 2GB free)
df -h .

# Verify write permissions
touch cortex-brain/.write-test && rm cortex-brain/.write-test
```

---

### Step 2: Fresh Clone or Pull (3 minutes)

#### Option A: Fresh Clone (New Machine)

```bash
# Clone CORTEX repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Checkout CORTEX6 branch
git checkout CORTEX6

# Verify branch
git branch --show-current  # Should show: CORTEX6
```

#### Option B: Existing Repository (Update)

```bash
# Navigate to CORTEX
cd /path/to/CORTEX

# Stash local changes if any
git stash save "Pre-sync backup $(date +%Y%m%d-%H%M%S)"

# Fetch latest
git fetch origin

# Checkout CORTEX6
git checkout CORTEX6

# Pull latest changes
git pull origin CORTEX6 --rebase

# Restore stash if needed
git stash list
# git stash pop  # If you had local changes
```

---

### Step 3: Install Dependencies (5 minutes)

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Verify critical packages
python3 -c "
import yaml
import pytest
import sqlite3
print('✅ All dependencies installed')
"
```

---

### Step 4: Initialize Governance System (3 minutes)

```bash
# 1. Load core rules (Tier 0)
python3 -c "
from src.tier0.governance_engine import GovernanceEngine
engine = GovernanceEngine()
rules = engine.get_all_rules()
print(f'✅ {len(rules)} CORE rules loaded')
"

# 2. Initialize audit database
python3 -c "
from src.infrastructure.enhanced_audit_logger import EnterpriseAuditLogger
logger = EnterpriseAuditLogger()
logger.info('INFRASTRUCTURE', 'Setup', 'initialize', 'Machine alignment started')
print('✅ Audit logger initialized')
"

# 3. Verify GovernanceMerger
python3 -c "
from src.orchestrators.core.governance_merger import GovernanceMerger
merger = GovernanceMerger()
result = merger.merge_all_tiers()
print(f'✅ GovernanceMerger: {len(result.unified_rules)} rules merged in {result.merge_time_ms}ms')
"

# 4. Test middleware
python3 -c "
from src.orchestrators.middleware.governance_checkpoint import GovernanceCheckpointMiddleware
middleware = GovernanceCheckpointMiddleware()
print('✅ GovernanceCheckpointMiddleware: operational')
"
```

**Expected Output:**
```
✅ 23 CORE rules loaded
✅ Audit logger initialized
✅ GovernanceMerger: 23 rules merged in 37ms
✅ GovernanceCheckpointMiddleware: operational
```

---

### Step 5: Run Validation Suite (5 minutes)

```bash
# 1. Governance tests (CRITICAL)
pytest tests/governance/ -v --tb=short

# Expected: 48/48 tests passing
# - test_governance_merger.py: 16 passing
# - test_governance_checkpoint.py: 12 passing
# - test_governance_tools.py: 20 passing

# 2. Integration tests
pytest tests/integration/test_governance_todo_integration.py -v

# 3. Performance regression test
pytest tests/integration/test_state_governance_performance_regression.py -v

# 4. Audit integrity
python3 scripts/verify_audit_trail.py --full-check

# 5. Evidence validation
python3 scripts/audit_based_evidence_validator.py
```

**Success Criteria:**
- ✅ 48/48 governance tests passing
- ✅ Merge time <50ms
- ✅ Audit hash chain valid
- ✅ Evidence verification ≥80%

---

### Step 6: Configure IDE Integration (Optional, 10 minutes)

#### VS Code Setup

Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.pylintArgs": [
    "--load-plugins=pylint_governance"
  ],
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests/"
  ],
  "files.watcherExclude": {
    "**/cortex-brain/database/**": true,
    "**/cortex-brain/audit-logs/**": true
  },
  "cortex.governance.autoCheck": true,
  "cortex.tdd.enforceRedPhase": true
}
```

#### Pre-commit Hook

Install pre-commit hook for automatic governance checks:

```bash
# Copy hook
cp scripts/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Test hook
git add .vscode/settings.json
git commit -m "test: verify pre-commit hook"

# Should see:
# 🔍 Running governance checks...
# ✅ CORE-008: TDD enforcement validated
# ✅ CORE-017: Governance bypass check passed
# ✅ CORE-019: TDD-Master route validated
```

---

## 🔍 Troubleshooting

### Issue 1: GovernanceMerger Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'src.orchestrators.core.governance_merger'
```

**Solution:**
```bash
# Verify file exists
ls -la src/orchestrators/core/governance_merger.py

# If missing, pull latest
git pull origin CORTEX6

# Verify PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

### Issue 2: Tier 0 Rules Not Loading

**Symptoms:**
```
FileNotFoundError: cortex-brain/tier0/governance/core-rules.yaml not found
```

**Solution:**
```bash
# Check tier0 structure
ls -la cortex-brain/tier0/governance/

# If missing, recreate from backup
git checkout origin/CORTEX6 -- cortex-brain/tier0/

# Verify YAML syntax
python3 -c "
import yaml
with open('cortex-brain/tier0/governance/core-rules.yaml') as f:
    rules = yaml.safe_load(f)
    print(f'✅ {len(rules.get(\"rules\", []))} rules loaded')
"
```

---

### Issue 3: Audit Database Locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Check for stale locks
lsof cortex-brain/database/governance.db

# Kill stale processes
kill -9 <PID>

# Enable WAL mode (prevents locks)
python3 -c "
import sqlite3
conn = sqlite3.connect('cortex-brain/database/governance.db')
conn.execute('PRAGMA journal_mode=WAL')
conn.close()
print('✅ WAL mode enabled')
"
```

---

### Issue 4: Tests Failing After Pull

**Symptoms:**
```
FAILED tests/governance/test_governance_merger.py::test_merge_performance
```

**Solution:**
```bash
# Clear pytest cache
rm -rf .pytest_cache

# Reinstall test dependencies
pip install --upgrade pytest pytest-cov pytest-asyncio

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# Re-run tests
pytest tests/governance/ -v --cache-clear
```

---

## 📊 Validation Checklist

Use this checklist after setup:

```markdown
## Machine Alignment Validation

- [ ] **Git Status**
  - [ ] On CORTEX6 branch
  - [ ] No uncommitted changes in src/orchestrators/core/
  - [ ] Latest commit matches origin/CORTEX6

- [ ] **Governance Architecture**
  - [ ] tier0/governance/core-rules.yaml exists (23 rules)
  - [ ] GovernanceMerger imports successfully
  - [ ] GovernanceCheckpointMiddleware operational
  - [ ] Governance-to-Todo pipeline functional

- [ ] **Tests Passing**
  - [ ] 48/48 governance tests passing
  - [ ] Integration tests passing
  - [ ] Performance <50ms merge time

- [ ] **Audit System**
  - [ ] governance.db exists
  - [ ] WAL mode enabled
  - [ ] Hash chain integrity valid
  - [ ] Can query last 24h of logs

- [ ] **IDE Integration**
  - [ ] Pre-commit hook installed
  - [ ] VS Code settings configured
  - [ ] Python path includes project root

- [ ] **Evidence System**
  - [ ] Evidence validator runs without errors
  - [ ] Verification rate ≥80%
  - [ ] AC-INDEX.yaml accessible
```

---

## 🎓 Understanding the Architecture

### Governance Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                              │
│              "implement authentication"                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  MasterOrchestrator   │
         │   (Central Control)   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  GovernanceMerger     │◄───── Tier 0: SKULL (23 rules)
         │  (4-Tier Loader)      │◄───── Tier 1: Business
         └───────────┬───────────┘◄───── Tier 2: Company
                     │            ◄───── Tier 3: Knowledge
                     │
                     ▼
         ┌───────────────────────┐
         │ Unified Rule Set      │
         │ (Conflicts Resolved)  │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ Governance-to-Todo    │
         │ Pipeline              │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ TodoManager           │
         │ (Task Tracking)       │
         └───────────┬───────────┘
                     │
                     ▼
    ┌────────────────┴────────────────┐
    │                                  │
    ▼                                  ▼
┌───────────────┐          ┌──────────────────┐
│ TDD-Master    │          │ Other Operations │
│ (Implements)  │          │ (ADO, Planning)  │
└───────┬───────┘          └────────┬─────────┘
        │                           │
        ▼                           ▼
┌────────────────────────────────────────────┐
│   GovernanceCheckpointMiddleware           │
│   (Runtime Enforcement)                    │
│   - BLOCKS violating operations            │
│   - WARNS on risky patterns                │
│   - AUDITS all checks                      │
└────────────────┬───────────────────────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │ EnterpriseAuditLogger │
     │ (Hash Chain)          │
     └───────────┬───────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │  governance.db        │
     │  (Tamper-Proof)       │
     └───────────────────────┘
```

### Rule Precedence Example

**Scenario:** CORE-008 (TDD Enforcement) vs. Company Rule "Quick Fixes Allowed"

1. **GovernanceMerger** loads both rules
2. **Conflict detected:** CORE-008 (Tier 0) vs. Company (Tier 2)
3. **Resolution:** Tier 0 wins (HIGHEST precedence)
4. **Result:** TDD enforcement BLOCKS quick fix without tests
5. **Audit:** Decision logged with correlation ID

```yaml
# Unified Rule After Merge
rule_id: CORE-008
governance_tier: 0
precedence: HIGHEST
severity: blocked
overridden_rules:
  - company_quick_fix (Tier 2, MEDIUM precedence)
```

---

## 🚀 Next Steps

After successful alignment:

1. **Try a test operation:**
   ```bash
   python3 -m src.main "implement hello world feature" --format markdown
   ```

2. **Monitor governance logs:**
   ```bash
   python3 -m src.main "audit query --category GOVERNANCE --last 1h"
   ```

3. **Review active epic:**
   ```bash
   cat cortex-brain/tier1/tracking/progress-tracker.json | jq '.active_epic'
   ```

4. **Check phase progress:**
   ```bash
   python3 scripts/update_plan_viewer_progress.py
   open cortex-brain/dashboards/plan-viewer.html
   ```

---

## 📚 Additional Resources

- **Architecture Docs:** `docs/architecture/governance-merger-architecture.md`
- **API Reference:** `src/orchestrators/core/README.md`
- **Audit Guide:** `cortex-brain/documents/operations/audit-trail-guide.md`
- **TDD-Master Docs:** `cortex-brain/documents/implementation-guides/tdd-master-guide.md`

---

## 🆘 Support

If issues persist after following this guide:

1. **Check GitHub Issues:** [CORTEX/issues](https://github.com/asifhussain60/CORTEX/issues)
2. **Review Recent Changes:** `git log --oneline --graph --all -20`
3. **Capture Diagnostic:**
   ```bash
   python3 scripts/verify_integrity.py --full-report > diagnostic.txt
   ```
4. **Contact:** File issue with diagnostic.txt attached

---

**Remember:** CORTEX 6.0's governance architecture is **non-negotiable**. The 4-tier system ensures production-grade integrity. If a component fails validation, fix it before proceeding—no workarounds allowed (CORE-017).

---

**Document Version:** 6.0.1  
**Last Updated:** 2026-01-12  
**Reviewed By:** Asif Hussain  
**Next Review:** 2026-02-01
