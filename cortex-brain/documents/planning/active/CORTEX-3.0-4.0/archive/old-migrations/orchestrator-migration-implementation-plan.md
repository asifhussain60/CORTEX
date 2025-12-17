# Orchestrator Migration Implementation Plan

**Author:** Asif Hussain  
**Date:** December 2, 2025  
**Version:** 1.0  
**Status:** 🚀 READY TO EXECUTE

---

## Executive Summary

This plan converts 15 USER-facing orchestrators to fast CLI utilities following the proven pattern from `align_utility.py` and `healthcheck_utility.py`. Each migration includes:
1. Create lightweight utility in `src/operations/modules/admin/` (or appropriate category)
2. Create CLI wrapper in `src/operations/`
3. Delete old orchestrator (keep `.bak`)
4. Update routing in unified entry point
5. Add deploy gate validation
6. Test with align and deploy commands

**Total Effort:** ~40-50 hours (15 orchestrators × 2.5-3.5 hours each)  
**Timeline:** 3 sprints (6 weeks)  
**Priority Order:** TDD Mastery features first (commit, planning, tdd)

---

## Migration Pattern (Proven Template)

### Pattern Components

**1. Utility Module** (`src/operations/modules/[category]/[name]_utility.py`)
```python
"""
[Name] Utility - Fast & Reliable

Lightweight replacement for [Name]Orchestrator focusing on essential functionality.

Design Goals:
    - Execute in <5 seconds (or <3s for critical)
    - Clear pass/fail reporting
    - No complex dependencies
    - Actionable error messages

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: PRODUCTION
"""

import logging
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

from src.config import config

logger = logging.getLogger(__name__)

@dataclass
class [Name]Result:
    """Result of [name] operation."""
    success: bool
    message: str
    details: Dict[str, Any] = None

def run_[name]_utility(**kwargs) -> Dict[str, Any]:
    """
    Execute [name] operation.
    
    Args:
        **kwargs: Operation-specific parameters
    
    Returns:
        Dict with success, message, and result data
    """
    try:
        # Core logic here
        result = [Name]Result(
            success=True,
            message="Operation completed successfully",
            details={}
        )
        
        return {
            "success": result.success,
            "message": result.message,
            "data": result.details
        }
    
    except Exception as e:
        logger.error(f"[Name] utility failed: {e}")
        return {
            "success": False,
            "message": f"Operation failed: {e}",
            "data": None
        }

if __name__ == "__main__":
    result = run_[name]_utility()
    print(result["message"])
```

**2. CLI Wrapper** (`src/operations/[name].py`)
```python
"""
[Name] Entry Point

Simple CLI wrapper for fast [Name]Utility.
Follows standard CORTEX operations pattern.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.modules.[category].[name]_utility import run_[name]_utility


def run_[name](**kwargs):
    """
    Run [name] operation using fast utility.
    
    Returns:
        Dict with success, message, and operation results
    """
    result = run_[name]_utility(**kwargs)
    
    return {
        "success": result["success"],
        "message": result["message"],
        "data": result.get("data"),
    }


def main():
    """CLI entry point."""
    result = run_[name]()
    
    print(f"\n{'='*60}")
    print(f"[Name] Operation")
    print(f"{'='*60}\n")
    print(result["message"])
    
    if result.get("data"):
        print(f"\n[Name] Details:")
        for key, value in result["data"].items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
```

**3. Orchestrator Cleanup**
```bash
# Move old orchestrator to .bak
mv src/orchestrators/[name]_orchestrator.py src/orchestrators/[name]_orchestrator.py.bak
```

**4. Routing Update** (in unified_entry_point_orchestrator.py or appropriate router)
```python
# Replace orchestrator call with utility
from src.operations.[name] import run_[name]
result = run_[name](**params)
```

**5. Deploy Gate Validation** (in deploy_orchestrator.py)
```python
# Add to validation gates
{
    "gate": "gate_[number]",
    "name": "[Name] Utility Validation",
    "validator": "validate_[name]_utility",
    "blocking": True,
    "category": "operations"
}
```

---

## Sprint 1: TDD Mastery Core (Week 1-2)

**Priority:** 🔥 CRITICAL - These are the defining CORTEX features

### 1. commit_orchestrator → commit_utility

**Current:** 16KB (449 lines), git checkpoint creation  
**Target:** <3s execution  
**Complexity:** Medium (git operations, stash management)

**Implementation Steps:**
1. Create `src/operations/modules/git/commit_utility.py`
   - Pre-flight validation (dirty state, untracked files)
   - Stash management
   - Commit with metadata
   - Safety checkpoint creation
2. Create `src/operations/commit.py` CLI wrapper
3. Update routing in entry point
4. Test: `python -m src.operations.commit` 
5. Delete `src/orchestrators/commit_orchestrator.py` (keep .bak)
6. Add deploy gate validation

**DoD Checklist:**
- [ ] Utility executes in <3s
- [ ] CLI wrapper functional
- [ ] Old orchestrator deleted (`.bak` kept)
- [ ] Routing updated
- [ ] Deploy gate passes
- [ ] Align verification passes
- [ ] Manual test: create checkpoint, verify git log

### 2. git_checkpoint_orchestrator → git_checkpoint_utility

**Current:** Git checkpoint management  
**Target:** <2s execution  
**Complexity:** Medium (git operations, metadata)

**Implementation Steps:**
1. Create `src/operations/modules/git/git_checkpoint_utility.py`
   - Checkpoint creation with metadata
   - Checkpoint listing
   - 30-day retention
2. Create `src/operations/git_checkpoint.py` CLI wrapper
3. Update routing
4. Test execution
5. Delete old orchestrator
6. Add deploy gate

**DoD Checklist:**
- [ ] Utility executes in <2s
- [ ] CLI wrapper functional
- [ ] Old orchestrator deleted
- [ ] Routing updated
- [ ] Deploy gate passes
- [ ] Align verification passes
- [ ] Manual test: list checkpoints, verify timestamps

### 3. rollback_orchestrator → rollback_utility

**Current:** Rollback to checkpoints  
**Target:** <3s execution  
**Complexity:** Medium (git reset, confirmation)

**Implementation Steps:**
1. Create `src/operations/modules/git/rollback_utility.py`
   - Checkpoint validation
   - Git reset operations
   - Confirmation prompts
2. Create `src/operations/rollback.py` CLI wrapper
3. Update routing
4. Test execution
5. Delete old orchestrator
6. Add deploy gate

**DoD Checklist:**
- [ ] Utility executes in <3s
- [ ] CLI wrapper functional
- [ ] Old orchestrator deleted
- [ ] Routing updated
- [ ] Deploy gate passes
- [ ] Align verification passes
- [ ] Manual test: rollback and verify state

---

## Sprint 2: Planning & Code Quality (Week 3-4)

### 4. planning_orchestrator → planning_utility

**Current:** 112KB (LARGEST), DoR/DoD validation, Vision API  
**Target:** <5s (without Vision), <15s (with Vision)  
**Complexity:** HIGH (file operations, Vision API, ADO integration)

**⚠️ WARNING:** 112KB size suggests code duplication - investigate before migration

**Implementation Steps:**
1. **Profile first:** Identify slow operations
2. Create `src/operations/modules/planning/planning_utility.py`
   - DoR/DoD validation
   - File-based planning
   - Vision API integration (optional)
   - ADO client (lightweight)
3. Create `src/operations/planning.py` CLI wrapper
4. Update routing
5. Test with/without Vision API
6. Delete old orchestrator
7. Add deploy gate

**DoD Checklist:**
- [ ] Profiling complete, bottlenecks identified
- [ ] Code duplication removed
- [ ] Utility executes in <5s (fast path)
- [ ] Vision API path <15s
- [ ] CLI wrapper functional
- [ ] Old orchestrator deleted
- [ ] Routing updated
- [ ] Deploy gate passes
- [ ] Manual test: create plan, approve, resume

### 5. tdd_orchestrator → tdd_utility

**Current:** 23KB, RED→GREEN→REFACTOR state machine  
**Target:** <2s (state transitions)  
**Complexity:** HIGH (state machine, terminal integration, auto-debug)

**Implementation Steps:**
1. Create `src/operations/modules/tdd/tdd_utility.py`
   - State machine (IDLE→RED→GREEN→REFACTOR→COMPLETE)
   - Terminal integration
   - Auto-debug on RED failures
   - Performance-based refactoring
2. Create `src/operations/tdd.py` CLI wrapper
3. Update routing
4. Test state transitions
5. Delete old orchestrator
6. Add deploy gate

**DoD Checklist:**
- [ ] Utility state transitions <2s
- [ ] Auto-debug functional
- [ ] CLI wrapper functional
- [ ] Old orchestrator deleted
- [ ] Routing updated
- [ ] Deploy gate passes
- [ ] Manual test: full TDD cycle

### 6. code_review_orchestrator → code_review_utility

**Current:** Dependency-driven PR analysis  
**Target:** <10s (standard review)  
**Complexity:** HIGH (AST parsing, dependency crawling)

**Implementation Steps:**
1. Create `src/operations/modules/code_review/code_review_utility.py`
   - Dependency-driven crawling
   - Tiered analysis (Quick/Standard/Deep)
   - Report generation
2. Create `src/operations/code_review.py` CLI wrapper
3. Update routing
4. Test review tiers
5. Delete old orchestrator
6. Add deploy gate

**DoD Checklist:**
- [ ] Utility executes in <10s
- [ ] All 3 tiers functional
- [ ] CLI wrapper functional
- [ ] Old orchestrator deleted
- [ ] Routing updated
- [ ] Deploy gate passes
- [ ] Manual test: review sample PR

### 7. lint_validation_orchestrator → lint_utility

**Current:** Code quality validation  
**Target:** <5s  
**Complexity:** LOW (external tools)

**Implementation Steps:**
1. Create `src/operations/modules/validation/lint_utility.py`
   - Linter execution (pylint, eslint, etc.)
   - Result parsing
   - Report generation
2. Create `src/operations/lint.py` CLI wrapper
3. Update routing
4. Test with sample code
5. Delete old orchestrator
6. Add deploy gate

**DoD Checklist:**
- [ ] Utility executes in <5s
- [ ] CLI wrapper functional
- [ ] Old orchestrator deleted
- [ ] Routing updated
- [ ] Deploy gate passes
- [ ] Manual test: lint sample files

---

## Sprint 3: Integration & Enhancement (Week 5-6)

### 8. ado_work_item_orchestrator → ado_utility

**Current:** ADO API integration  
**Target:** <5s  
**Complexity:** MEDIUM (API calls)

**Implementation Steps:**
1. Create `src/operations/modules/ado/ado_utility.py`
   - Work item creation
   - Status updates
   - Query operations
2. Create `src/operations/ado.py` CLI wrapper
3. Update routing
4. Test with ADO instance
5. Delete old orchestrator
6. Add deploy gate

### 9. swagger_entry_point_orchestrator → swagger_utility

**Current:** OpenAPI/Swagger operations  
**Target:** <5s  
**Complexity:** MEDIUM (spec parsing)

**Implementation Steps:**
1. Create `src/operations/modules/api/swagger_utility.py`
   - Spec parsing
   - Validation
   - Entry point generation
2. Create `src/operations/swagger.py` CLI wrapper
3. Update routing
4. Test with sample specs
5. Delete old orchestrator
6. Add deploy gate

### 10. ux_enhancement_orchestrator → ux_utility

**Current:** UX improvement analysis  
**Target:** <10s  
**Complexity:** MEDIUM (UI analysis)

**Implementation Steps:**
1. Create `src/operations/modules/ux/ux_utility.py`
   - UI element discovery
   - Accessibility checks
   - UX pattern validation
2. Create `src/operations/ux.py` CLI wrapper
3. Update routing
4. Test with sample UI
5. Delete old orchestrator
6. Add deploy gate

### 11. realignment_orchestrator → realignment_utility

**Current:** System realignment  
**Target:** <5s  
**Complexity:** LOW (validation checks)

**Implementation Steps:**
1. Create `src/operations/modules/admin/realignment_utility.py`
   - Configuration sync
   - State validation
   - Alignment checks
2. Create `src/operations/realignment.py` CLI wrapper
3. Update routing
4. Test realignment
5. Delete old orchestrator
6. Add deploy gate

### 12. application_health_orchestrator → app_health_utility

**Current:** Application health dashboard  
**Target:** <10s  
**Complexity:** MEDIUM (metrics collection)

**Implementation Steps:**
1. Create `src/operations/modules/health/app_health_utility.py`
   - Metrics collection
   - Dashboard generation
   - Health scoring
2. Create `src/operations/app_health.py` CLI wrapper
3. Update routing
4. Test dashboard generation
5. Delete old orchestrator
6. Add deploy gate

### 13. rca_orchestrator → rca_utility

**Current:** Root cause analysis  
**Target:** <15s  
**Complexity:** HIGH (log analysis, pattern matching)

**Implementation Steps:**
1. Create `src/operations/modules/analysis/rca_utility.py`
   - Log parsing
   - Pattern matching
   - Root cause identification
2. Create `src/operations/rca.py` CLI wrapper
3. Update routing
4. Test with sample logs
5. Delete old orchestrator
6. Add deploy gate

### 14. upgrade_orchestrator → upgrade_utility

**Current:** CORTEX upgrade workflow  
**Target:** <15s (check), <30s (upgrade)  
**Complexity:** MEDIUM (git operations, backup)

**Implementation Steps:**
1. Create `src/operations/modules/admin/upgrade_utility.py`
   - Version check
   - Backup creation
   - Upgrade execution
   - Rollback capability
2. Create `src/operations/upgrade.py` CLI wrapper
3. Update routing
4. Test upgrade (dry-run)
5. Delete old orchestrator
6. Add deploy gate

### 15. API Enhancement (NEW) → api_enhancement_utility

**Current:** NONE (new feature from Option C)  
**Target:** <10s  
**Complexity:** MEDIUM-HIGH (spec generation, validation)

**Implementation Steps:**
1. Create `src/operations/modules/api/api_enhancement_utility.py`
   - API planning template integration
   - Route discovery (Express, FastAPI, ASP.NET, Spring)
   - OpenAPI scaffolding generation
   - Contract validation
2. Create `src/operations/api_enhance.py` CLI wrapper
3. Add routing in entry point
4. Test with sample API codebase
5. Add deploy gate

**DoD Checklist:**
- [ ] Utility executes in <10s
- [ ] Multi-framework support (4 frameworks)
- [ ] OpenAPI scaffold generation works
- [ ] CLI wrapper functional
- [ ] Routing added
- [ ] Deploy gate passes
- [ ] Manual test: generate spec from code

---

## Deploy Gate Integration

### Gate Configuration (deploy_orchestrator.py)

```python
USER_OPERATION_GATES = [
    # Sprint 1: TDD Mastery
    {
        "gate": "gate_15",
        "name": "Commit Utility Validation",
        "validator": "validate_commit_utility",
        "blocking": True,
        "category": "git"
    },
    {
        "gate": "gate_16",
        "name": "Git Checkpoint Utility Validation",
        "validator": "validate_git_checkpoint_utility",
        "blocking": True,
        "category": "git"
    },
    {
        "gate": "gate_17",
        "name": "Rollback Utility Validation",
        "validator": "validate_rollback_utility",
        "blocking": True,
        "category": "git"
    },
    
    # Sprint 2: Planning & Code Quality
    {
        "gate": "gate_18",
        "name": "Planning Utility Validation",
        "validator": "validate_planning_utility",
        "blocking": True,
        "category": "planning"
    },
    {
        "gate": "gate_19",
        "name": "TDD Utility Validation",
        "validator": "validate_tdd_utility",
        "blocking": True,
        "category": "tdd"
    },
    {
        "gate": "gate_20",
        "name": "Code Review Utility Validation",
        "validator": "validate_code_review_utility",
        "blocking": True,
        "category": "code_quality"
    },
    {
        "gate": "gate_21",
        "name": "Lint Utility Validation",
        "validator": "validate_lint_utility",
        "blocking": True,
        "category": "code_quality"
    },
    
    # Sprint 3: Integration & Enhancement
    {
        "gate": "gate_22",
        "name": "ADO Utility Validation",
        "validator": "validate_ado_utility",
        "blocking": True,
        "category": "integration"
    },
    {
        "gate": "gate_23",
        "name": "Swagger Utility Validation",
        "validator": "validate_swagger_utility",
        "blocking": True,
        "category": "api"
    },
    {
        "gate": "gate_24",
        "name": "UX Utility Validation",
        "validator": "validate_ux_utility",
        "blocking": True,
        "category": "enhancement"
    },
    {
        "gate": "gate_25",
        "name": "Realignment Utility Validation",
        "validator": "validate_realignment_utility",
        "blocking": True,
        "category": "admin"
    },
    {
        "gate": "gate_26",
        "name": "App Health Utility Validation",
        "validator": "validate_app_health_utility",
        "blocking": True,
        "category": "health"
    },
    {
        "gate": "gate_27",
        "name": "RCA Utility Validation",
        "validator": "validate_rca_utility",
        "blocking": True,
        "category": "analysis"
    },
    {
        "gate": "gate_28",
        "name": "Upgrade Utility Validation",
        "validator": "validate_upgrade_utility",
        "blocking": True,
        "category": "admin"
    },
    {
        "gate": "gate_29",
        "name": "API Enhancement Utility Validation",
        "validator": "validate_api_enhancement_utility",
        "blocking": True,
        "category": "api"
    },
]
```

### Validator Template

```python
def validate_[name]_utility(self) -> Dict[str, Any]:
    """
    Validate [name] utility exists and is functional.
    
    Checks:
        1. Utility module exists
        2. CLI wrapper exists
        3. Entry point function present
        4. Can import without errors
        5. Old orchestrator removed (only .bak exists)
    
    Returns:
        Dict with success, message, and validation details
    """
    try:
        # Check utility exists
        utility_path = self.cortex_root / "src/operations/modules/[category]/[name]_utility.py"
        if not utility_path.exists():
            return {
                "success": False,
                "message": f"[Name] utility not found: {utility_path}",
                "gate": "gate_[number]"
            }
        
        # Check CLI wrapper exists
        cli_path = self.cortex_root / "src/operations/[name].py"
        if not cli_path.exists():
            return {
                "success": False,
                "message": f"[Name] CLI wrapper not found: {cli_path}",
                "gate": "gate_[number]"
            }
        
        # Check old orchestrator removed
        old_orch = self.cortex_root / "src/orchestrators/[name]_orchestrator.py"
        if old_orch.exists():
            return {
                "success": False,
                "message": f"Old orchestrator still exists: {old_orch}",
                "gate": "gate_[number]"
            }
        
        # Test import
        try:
            from src.operations.[name] import run_[name]
        except ImportError as e:
            return {
                "success": False,
                "message": f"Cannot import [name] CLI: {e}",
                "gate": "gate_[number]"
            }
        
        return {
            "success": True,
            "message": "[Name] utility validated successfully",
            "gate": "gate_[number]"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"[Name] validation failed: {e}",
            "gate": "gate_[number]"
        }
```

---

## Align Verification

### Post-Migration Checklist

After each utility migration, run:

```bash
# Windows
python -m src.operations.align

# Mac/Linux
python3 -m src.operations.align
```

**Expected Output:**
```
✅ [OK] Brain tier structure: All 4 tiers present
✅ [OK] Protection rules: brain-protection-rules.yaml valid
✅ [OK] Response templates: 62 templates loaded
✅ [OK] Working memory: Database operational
✅ [OK] Knowledge graph: Database operational
✅ [OK] Development context: Database operational
✅ [OK] Core modules: All orchestrators/agents present
✅ [OK] Configuration: cortex.config.json valid
✅ [OK] [Name] utility: Operational

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ System Alignment: HEALTHY (9/9 checks passed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Testing Strategy

### Unit Tests (Per Utility)

Create `tests/operations/test_[name]_utility.py`:

```python
"""
Unit tests for [name] utility.

Tests core functionality, error handling, and performance targets.

Author: Asif Hussain
"""

import pytest
from pathlib import Path
from src.operations.modules.[category].[name]_utility import run_[name]_utility

class Test[Name]Utility:
    """Test suite for [name] utility."""
    
    def test_basic_execution(self):
        """Test basic utility execution."""
        result = run_[name]_utility()
        assert result["success"] is True
        assert "message" in result
        assert "data" in result
    
    def test_performance_target(self):
        """Test utility meets performance target (<Xs)."""
        import time
        start = time.time()
        result = run_[name]_utility()
        duration = time.time() - start
        assert duration < [target_seconds], f"Execution took {duration:.2f}s (target: <{target_seconds}s)"
    
    def test_error_handling(self):
        """Test error handling with invalid input."""
        result = run_[name]_utility(invalid_param="test")
        assert result["success"] is False
        assert "error" in result["message"].lower()
    
    def test_cli_wrapper_import(self):
        """Test CLI wrapper can be imported."""
        from src.operations.[name] import run_[name]
        assert callable(run_[name])
```

### Integration Tests

```bash
# Test full workflow
pytest tests/integration/test_[name]_workflow.py -v

# Test deploy gate
pytest tests/integration/test_deploy_gates.py::test_gate_[number] -v
```

### Manual Smoke Tests

```bash
# Direct utility test
python -m src.operations.modules.[category].[name]_utility

# CLI wrapper test
python -m src.operations.[name]

# Routing test (from main entry point)
python -m src.main [name]
```

---

## Mac Continuation Instructions

### Setup on Mac

```bash
# 1. Pull latest changes
cd ~/PROJECTS/CORTEX
git pull origin CORTEX-3.0

# 2. Verify Python environment
python3 --version  # Should be 3.8+
which python3

# 3. Install dependencies (if needed)
pip3 install -r requirements.txt

# 4. Verify CORTEX config
python3 -c "from src.config import config; print(config.brain_path)"

# 5. Run align to verify system
python3 -m src.operations.align
```

### Continue Work on Mac

**Check current progress:**
```bash
# View implementation plan
cat cortex-brain/documents/implementation-guides/orchestrator-migration-implementation-plan.md

# Check completed utilities
ls -la src/operations/modules/*/
ls -la src/operations/*.py

# Check remaining orchestrators
ls -la src/orchestrators/*_orchestrator.py | grep -v ".bak"
```

**Continue Sprint 1 (if not complete):**
```bash
# Create commit utility
touch src/operations/modules/git/commit_utility.py
code src/operations/modules/git/commit_utility.py

# Follow pattern from align_utility.py
cat src/operations/modules/admin/align_utility.py

# Test after creation
python3 -m src.operations.commit
```

**Run validation:**
```bash
# After each utility
python3 -m src.operations.align

# Before commit
python3 -m src.operations.healthcheck

# Deploy dry-run
python3 -m src.orchestrators.deploy_orchestrator --dry-run
```

### Mac-Specific Notes

**Path Differences:**
- Windows: `d:\PROJECTS\CORTEX\`
- Mac: `~/PROJECTS/CORTEX/`

**Python Command:**
- Windows: `python`
- Mac: `python3`

**Terminal:**
- Windows: PowerShell (`pwsh`)
- Mac: Bash/Zsh

**Config Update (if needed):**
```bash
# Edit cortex.config.json for Mac hostname
hostname  # Get your Mac's hostname
code cortex.config.json

# Add Mac machine config
{
  "machines": {
    "YOUR-MAC-HOSTNAME": {
      "rootPath": "/Users/yourusername/PROJECTS/CORTEX",
      "brainPath": "/Users/yourusername/PROJECTS/CORTEX/cortex-brain"
    }
  }
}
```

---

## Success Metrics

### Per-Utility Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| **Execution Time** | <3s (critical), <5s (standard), <10s (complex) | `time python3 -m src.operations.[name]` |
| **Code Size** | <500 lines (simple), <1000 lines (complex) | `wc -l src/operations/modules/[category]/[name]_utility.py` |
| **Test Coverage** | >80% | `pytest --cov=src.operations.modules.[category].[name]_utility` |
| **Deploy Gate** | PASS | `python3 -m src.orchestrators.deploy_orchestrator --dry-run` |
| **Align Check** | PASS | `python3 -m src.operations.align` |

### Overall Project Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Utilities Migrated** | 15 | 2 (align, healthcheck) | 🟡 13% |
| **Old Orchestrators Removed** | 15 | 2 | 🟡 13% |
| **Deploy Gates Added** | 15 | 0 | 🔴 0% |
| **Average Execution Time** | <5s | TBD | ⚪ Pending |
| **Code Reduction** | 30-50% | TBD | ⚪ Pending |

---

## Risk Mitigation

### High-Risk Migrations

**planning_orchestrator (112KB)**
- **Risk:** Code duplication, performance bottlenecks
- **Mitigation:** Profile first, refactor before migration
- **Contingency:** Split into planning_core + planning_vision utilities

**tdd_orchestrator (State Machine)**
- **Risk:** Complex state management, terminal integration
- **Mitigation:** Preserve state machine logic exactly, extensive testing
- **Contingency:** Keep orchestrator for complex workflows, utility for simple cases

**code_review_orchestrator (AST Parsing)**
- **Risk:** Heavy dependency crawling, token budget
- **Mitigation:** Cache parsed files, incremental analysis
- **Contingency:** Tiered execution (fast path for small PRs)

### Rollback Strategy

**Per-Utility Rollback:**
```bash
# Restore old orchestrator
cp src/orchestrators/[name]_orchestrator.py.bak src/orchestrators/[name]_orchestrator.py

# Remove utility
rm src/operations/modules/[category]/[name]_utility.py
rm src/operations/[name].py

# Revert routing changes
git checkout src/orchestrators/unified_entry_point_orchestrator.py

# Remove deploy gate
# Edit deploy_orchestrator.py manually
```

**Full Sprint Rollback:**
```bash
# Create rollback branch
git checkout -b rollback-sprint-[number]

# Revert sprint commits
git revert [commit-range]

# Test system alignment
python3 -m src.operations.align

# If successful, merge to CORTEX-3.0
git checkout CORTEX-3.0
git merge rollback-sprint-[number]
```

---

## Commit Strategy

### Per-Utility Commits

```bash
# After each utility completion
git add src/operations/modules/[category]/[name]_utility.py
git add src/operations/[name].py
git add src/orchestrators/[name]_orchestrator.py.bak
git add src/orchestrators/unified_entry_point_orchestrator.py  # If routing changed
git add src/orchestrators/deploy_orchestrator.py  # If gate added
git commit -m "feat: migrate [name] orchestrator to utility

- Create [name]_utility.py with <Xs execution
- Add CLI wrapper in src/operations/[name].py
- Remove old [name]_orchestrator.py (keep .bak)
- Update routing in unified entry point
- Add deploy gate validation (gate_[number])
- Tests: [test results]

DoD: ✅ Utility functional, ✅ Gate passes, ✅ Align verified"
```

### Sprint Commits

```bash
# After each sprint
git add cortex-brain/documents/implementation-guides/
git commit -m "docs: complete sprint [number] orchestrator migrations

Migrated:
- [name1] orchestrator → utility
- [name2] orchestrator → utility
- [name3] orchestrator → utility

Metrics:
- Average execution: [time]
- Code reduction: [percentage]
- All gates passing

Status: Sprint [number] of 3 complete"
```

### Push to Remote

```bash
# After each sprint or significant milestone
git push origin CORTEX-3.0

# Or if working on feature branch
git push origin feature/orchestrator-migration
```

---

## Next Steps (Immediate)

### Windows (Current Session)

1. ✅ Create implementation plan (this document)
2. ⏳ Commit and push to remote
3. ⏳ Verify Mac can pull changes

```bash
# Commit this plan
git add cortex-brain/documents/implementation-guides/orchestrator-migration-implementation-plan.md
git add cortex-brain/documents/reports/ORCHESTRATOR-MIGRATION-COMPLETE-ANALYSIS.md
git commit -m "docs: create comprehensive orchestrator migration plan

- 15 utilities to migrate (align and healthcheck complete)
- 3-sprint timeline (6 weeks)
- API enhancement utility added as #15
- Deploy gate integration (gates 15-29)
- Mac continuation instructions included
- DoD: Utility + CLI + Gate + Align + Delete orchestrator

Ready to execute Sprint 1 (commit, git_checkpoint, rollback)"

git push origin CORTEX-3.0
```

### Mac (Next Session)

1. Pull latest changes
2. Verify environment setup
3. Begin Sprint 1: commit_utility migration
4. Test and validate
5. Commit and push
6. Continue with git_checkpoint_utility

---

## Appendix A: File Structure After Migration

```
CORTEX/
├── src/
│   ├── operations/
│   │   ├── modules/
│   │   │   ├── admin/
│   │   │   │   ├── align_utility.py ✅
│   │   │   │   ├── healthcheck_utility.py ✅
│   │   │   │   ├── realignment_utility.py ⏳
│   │   │   │   └── upgrade_utility.py ⏳
│   │   │   ├── git/
│   │   │   │   ├── commit_utility.py ⏳
│   │   │   │   ├── git_checkpoint_utility.py ⏳
│   │   │   │   └── rollback_utility.py ⏳
│   │   │   ├── planning/
│   │   │   │   └── planning_utility.py ⏳
│   │   │   ├── tdd/
│   │   │   │   └── tdd_utility.py ⏳
│   │   │   ├── code_review/
│   │   │   │   └── code_review_utility.py ⏳
│   │   │   ├── validation/
│   │   │   │   └── lint_utility.py ⏳
│   │   │   ├── ado/
│   │   │   │   └── ado_utility.py ⏳
│   │   │   ├── api/
│   │   │   │   ├── swagger_utility.py ⏳
│   │   │   │   └── api_enhancement_utility.py ⏳ NEW
│   │   │   ├── ux/
│   │   │   │   └── ux_utility.py ⏳
│   │   │   ├── health/
│   │   │   │   └── app_health_utility.py ⏳
│   │   │   └── analysis/
│   │   │       └── rca_utility.py ⏳
│   │   ├── align.py ✅
│   │   ├── healthcheck.py ✅
│   │   ├── commit.py ⏳
│   │   ├── git_checkpoint.py ⏳
│   │   ├── rollback.py ⏳
│   │   ├── planning.py ⏳
│   │   ├── tdd.py ⏳
│   │   ├── code_review.py ⏳
│   │   ├── lint.py ⏳
│   │   ├── ado.py ⏳
│   │   ├── swagger.py ⏳
│   │   ├── api_enhance.py ⏳ NEW
│   │   ├── ux.py ⏳
│   │   ├── app_health.py ⏳
│   │   ├── rca.py ⏳
│   │   ├── realignment.py ⏳
│   │   └── upgrade.py ⏳
│   └── orchestrators/
│       ├── system_alignment_orchestrator.py.bak ✅
│       ├── healthcheck_orchestrator.py.bak ✅
│       ├── commit_orchestrator.py.bak ⏳
│       ├── git_checkpoint_orchestrator.py.bak ⏳
│       ├── rollback_orchestrator.py.bak ⏳
│       ├── planning_orchestrator.py.bak ⏳
│       ├── tdd_orchestrator.py.bak ⏳
│       ├── code_review_orchestrator.py.bak ⏳
│       ├── lint_validation_orchestrator.py.bak ⏳
│       ├── ado_work_item_orchestrator.py.bak ⏳
│       ├── swagger_entry_point_orchestrator.py.bak ⏳
│       ├── ux_enhancement_orchestrator.py.bak ⏳
│       ├── application_health_orchestrator.py.bak ⏳
│       ├── rca_orchestrator.py.bak ⏳
│       ├── realignment_orchestrator.py.bak ⏳
│       └── upgrade_orchestrator.py.bak ⏳
└── tests/
    └── operations/
        ├── test_align_utility.py ✅
        ├── test_healthcheck_utility.py ✅
        ├── test_commit_utility.py ⏳
        ├── test_git_checkpoint_utility.py ⏳
        ├── test_rollback_utility.py ⏳
        ├── test_planning_utility.py ⏳
        ├── test_tdd_utility.py ⏳
        ├── test_code_review_utility.py ⏳
        ├── test_lint_utility.py ⏳
        ├── test_ado_utility.py ⏳
        ├── test_swagger_utility.py ⏳
        ├── test_api_enhancement_utility.py ⏳ NEW
        ├── test_ux_utility.py ⏳
        ├── test_app_health_utility.py ⏳
        ├── test_rca_utility.py ⏳
        ├── test_realignment_utility.py ⏳
        └── test_upgrade_utility.py ⏳

Legend:
✅ Complete
⏳ Pending
NEW - New feature (API Enhancement from Option C)
```

---

## Appendix B: Quick Reference

### Commands Summary

```bash
# Development (Windows)
python -m src.operations.[name]              # Test utility directly
python -m src.operations.align               # Verify system
python -m src.orchestrators.deploy_orchestrator --dry-run  # Test deploy

# Development (Mac)
python3 -m src.operations.[name]
python3 -m src.operations.align
python3 -m src.orchestrators.deploy_orchestrator --dry-run

# Testing
pytest tests/operations/test_[name]_utility.py -v
pytest tests/integration/ -v
pytest --cov=src.operations.modules.[category].[name]_utility

# Git
git add [files]
git commit -m "feat: migrate [name] orchestrator to utility..."
git push origin CORTEX-3.0
```

### Performance Targets

| Utility | Target | Priority |
|---------|--------|----------|
| commit | <3s | 🔥 Critical |
| git_checkpoint | <2s | 🔥 Critical |
| rollback | <3s | 🔥 Critical |
| planning | <5s (fast), <15s (vision) | 🔥 Critical |
| tdd | <2s | 🔥 Critical |
| code_review | <10s | High |
| lint | <5s | High |
| ado | <5s | Medium |
| swagger | <5s | Medium |
| api_enhance | <10s | Medium |
| ux | <10s | Medium |
| realignment | <5s | Medium |
| app_health | <10s | Medium |
| rca | <15s | Medium |
| upgrade | <15s (check), <30s (upgrade) | Medium |

---

**Status:** 🚀 READY TO EXECUTE  
**Next Action:** Commit this plan and push to remote for Mac continuation  
**Sprint 1 Start:** Ready to begin commit_utility migration

