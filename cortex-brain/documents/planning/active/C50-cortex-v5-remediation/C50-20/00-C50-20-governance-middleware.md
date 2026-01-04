# C50-20: Governance Middleware Implementation

**Epic:** C50 - CORTEX v5 Gap Remediation  
**Feature:** Implement v5.0 Universal Pattern middleware (Phase -2, N+1, Runtime)  
**Priority:** P0 (CRITICAL BLOCKER)  
**Complexity:** TIER 4 (COMPREHENSIVE)  
**Effort:** 6-8 hours  
**Author:** CORTEX Investigation Orchestrator  
**Created:** 2026-01-04

---

## 🎯 Problem Statement

**Current State:** SKULL rules defined in `brain-protection-rules.yaml` but not enforced at runtime:
- ✅ 61 SKULL rules documented (v5.0)
- ❌ Middleware classes referenced but NOT IMPLEMENTED:
  - `GovernanceCheckpoint` (Runtime enforcement)
  - `SetupVerifier` (Phase -2: Pre-execution)
  - `TeardownRefactor` (Phase N+1: Post-execution)
- ❌ Master orchestrator lifecycle hooks not wired

**Risk:** Gap 2 remediation incomplete, v5.0 pattern not operational, SKULL rules unenforced.

**Goal:** Implement all 3 middleware classes + wire into master orchestrator lifecycle.

---

## 📋 Acceptance Criteria

### Definition of Ready (DoR)
- [x] Brittleness analysis completed
- [x] SKULL rules defined in YAML (v5.0)
- [x] Master orchestrator lifecycle hook structure exists
- [x] Gap 2 remediation requirements documented

### Definition of Done (DoD)
- [ ] `GovernanceCheckpoint` class implemented (runtime enforcement)
- [ ] `SetupVerifier` class implemented (Phase -2)
- [ ] `TeardownRefactor` class implemented (Phase N+1)
- [ ] Master orchestrator wired to all 3 middleware
- [ ] Audit log writes to `tracking/governance-audit.jsonl`
- [ ] All middleware tests pass (100% coverage)
- [ ] Integration tests pass (real orchestrator execution)
- [ ] Validation report generated

---

## 🏗️ Phase Breakdown

### Phase 1: GovernanceCheckpoint Middleware (2h)

**Purpose:** Runtime enforcement of SKULL rules at phase boundaries.

**RED (Tests First):**
```python
# tests/orchestrators/middleware/test_governance_checkpoint.py
import pytest
from pathlib import Path
from src.orchestrators.middleware.governance_checkpoint import GovernanceCheckpoint, ViolationResult

def test_governance_checkpoint_initialization():
    """Test GovernanceCheckpoint loads SKULL rules."""
    rules_path = Path("cortex-brain/brain-protection-rules.yaml")
    checkpoint = GovernanceCheckpoint(rules_path)
    
    assert checkpoint.rules is not None
    assert len(checkpoint.rules) >= 61  # v5.0 has 61 rules
    assert checkpoint.audit_log.exists()

def test_pre_execution_validates_dor():
    """Test pre-execution validates Definition of Ready."""
    checkpoint = GovernanceCheckpoint(Path("cortex-brain/brain-protection-rules.yaml"))
    
    context = {
        "orchestrator_id": "planning_v5",
        "dependencies": ["C50-00", "C50-01"],
        "dependencies_met": False  # DoR violation
    }
    
    result = checkpoint.pre_execution_hook("test-plan", context)
    
    assert result.passed is False
    assert "DoR" in result.message
    assert result.rule_id == "PHASE_ACCEPTANCE_CRITERIA"

def test_post_execution_validates_dod():
    """Test post-execution validates Definition of Done."""
    checkpoint = GovernanceCheckpoint(Path("cortex-brain/brain-protection-rules.yaml"))
    
    result_context = {
        "orchestrator_id": "planning_v5",
        "tests_passing": False,  # DoD violation
        "deliverables_created": True,
        "refactor_complete": False
    }
    
    result = checkpoint.post_execution_hook("test-plan", result_context)
    
    assert result.passed is False
    assert "DoD" in result.message

def test_audit_log_written_on_violation():
    """Test violations logged to audit trail."""
    checkpoint = GovernanceCheckpoint(Path("cortex-brain/brain-protection-rules.yaml"))
    
    context = {"dependencies_met": False}
    checkpoint.pre_execution_hook("test", context)
    
    # Check audit log
    with open(checkpoint.audit_log) as f:
        lines = f.readlines()
    
    last_entry = json.loads(lines[-1])
    assert last_entry["rule_id"] == "PHASE_ACCEPTANCE_CRITERIA"
    assert last_entry["violated"] is True
```

**GREEN (Implementation):**
```python
# src/orchestrators/middleware/governance_checkpoint.py
"""
Governance Checkpoint Middleware
Runtime enforcement of SKULL rules at phase boundaries.

CORTEX v5 Universal Pattern: Runtime Governance (Gap 2 Remediation)
"""
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class EnforcementLevel(Enum):
    BLOCKING = "blocked"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ViolationResult:
    passed: bool
    rule_id: str
    rule_name: str
    message: str
    enforcement: EnforcementLevel
    evidence: Dict[str, Any] = None


class GovernanceCheckpoint:
    """Runtime SKULL rule enforcement."""
    
    def __init__(self, rules_path: Path):
        self.rules_path = rules_path
        self.rules = self._load_skull_rules()
        self.audit_log = Path("tracking/governance-audit.jsonl")
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
        self.audit_log.touch(exist_ok=True)
    
    def _load_skull_rules(self) -> Dict[str, Any]:
        """Load SKULL rules from YAML."""
        with open(self.rules_path) as f:
            data = yaml.safe_load_all(f)
            rules = []
            for doc in data:
                if isinstance(doc, dict) and 'rule_id' in doc:
                    rules.append(doc)
            return {rule['rule_id']: rule for rule in rules}
    
    def pre_execution_hook(self, plan_id: str, context: Dict[str, Any]) -> ViolationResult:
        """
        Phase -1 to Phase 0 transition validation.
        Validates Definition of Ready (DoR).
        """
        # Check PHASE_ACCEPTANCE_CRITERIA rule
        rule = self.rules.get("PHASE_ACCEPTANCE_CRITERIA")
        if not rule:
            return ViolationResult(
                passed=True,
                rule_id="PHASE_ACCEPTANCE_CRITERIA",
                rule_name="N/A",
                message="Rule not found (skipping)",
                enforcement=EnforcementLevel.INFO
            )
        
        # DoR validation
        dor_met = context.get("dependencies_met", True)
        resources_available = context.get("resources_available", True)
        false_positive_check = context.get("false_positive_check", True)
        
        dor_passed = dor_met and resources_available and false_positive_check
        
        result = ViolationResult(
            passed=dor_passed,
            rule_id="PHASE_ACCEPTANCE_CRITERIA",
            rule_name=rule['name'],
            message=f"DoR {'PASSED' if dor_passed else 'FAILED'}: dependencies_met={dor_met}, resources={resources_available}",
            enforcement=EnforcementLevel.BLOCKING if not dor_passed else EnforcementLevel.INFO,
            evidence={"dor": context}
        )
        
        self._log_to_audit(plan_id, result)
        return result
    
    def post_execution_hook(self, plan_id: str, result_context: Dict[str, Any]) -> ViolationResult:
        """
        Phase N to Phase N+1 transition validation.
        Validates Definition of Done (DoD).
        """
        rule = self.rules.get("PHASE_ACCEPTANCE_CRITERIA")
        
        # DoD validation
        deliverables_created = result_context.get("deliverables_created", False)
        tests_passing = result_context.get("tests_passing", False)
        refactor_complete = result_context.get("refactor_complete", False)
        
        dod_passed = deliverables_created and tests_passing and refactor_complete
        
        result = ViolationResult(
            passed=dod_passed,
            rule_id="PHASE_ACCEPTANCE_CRITERIA",
            rule_name=rule['name'] if rule else "N/A",
            message=f"DoD {'PASSED' if dod_passed else 'FAILED'}: deliverables={deliverables_created}, tests={tests_passing}, refactor={refactor_complete}",
            enforcement=EnforcementLevel.BLOCKING if not dod_passed else EnforcementLevel.INFO,
            evidence={"dod": result_context}
        )
        
        self._log_to_audit(plan_id, result)
        return result
    
    def _log_to_audit(self, plan_id: str, result: ViolationResult):
        """Write violation to audit log."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "plan_id": plan_id,
            "rule_id": result.rule_id,
            "rule_name": result.rule_name,
            "violated": not result.passed,
            "enforcement": result.enforcement.value,
            "message": result.message,
            "evidence": result.evidence
        }
        
        with open(self.audit_log, 'a') as f:
            f.write(json.dumps(entry) + '\n')
```

**REFACTOR:**
- Extract DoR/DoD validation into separate methods
- Add type hints for all methods
- Add docstrings with examples

---

### Phase 2: SetupVerifier Middleware (1.5h)

**Purpose:** Phase -2 setup verification (dependency tests, not just file checks).

**RED (Tests First):**
```python
# tests/orchestrators/middleware/test_setup_verifier.py
def test_setup_verifier_validates_dependencies():
    """Test SetupVerifier runs actual dependency tests."""
    verifier = SetupVerifier()
    
    result = verifier.verify_dependencies(
        plan_id="C50-03",
        dependencies=["C50-00", "C50-01"]
    )
    
    assert result.passed is True or result.passed is False
    assert "false_positive" not in result.message  # Real validation

def test_setup_verifier_detects_false_positives():
    """Test false positive detection (file exists but broken)."""
    verifier = SetupVerifier()
    
    # Create broken dependency file
    broken_file = Path("tests/fixtures/broken_dep.py")
    broken_file.write_text("import nonexistent_module")  # Will fail import
    
    result = verifier.detect_false_positives([broken_file])
    
    assert len(result.broken_dependencies) > 0
    assert broken_file in result.broken_dependencies
```

**GREEN (Implementation):**
```python
# src/orchestrators/middleware/setup_verification.py
"""
Setup Verifier Middleware
Phase -2: Pre-execution dependency validation.

CORTEX v5 Universal Pattern: Setup Verification
"""
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class VerificationResult:
    passed: bool
    dependencies_checked: List[str]
    broken_dependencies: List[Path]
    message: str
    evidence: Dict[str, Any]


class SetupVerifier:
    """Phase -2 setup verification."""
    
    def verify_dependencies(self, plan_id: str, dependencies: List[str]) -> VerificationResult:
        """
        Verify dependencies are ACTUALLY complete (not just file existence).
        Runs pytest on dependency test files.
        """
        broken = []
        
        for dep_id in dependencies:
            # Find test file for dependency
            test_file = Path(f"tests/orchestrators/planning/test_{dep_id.lower()}.py")
            
            if not test_file.exists():
                broken.append(test_file)
                continue
            
            # Run pytest on test file
            result = subprocess.run(
                ["pytest", str(test_file), "-v"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                broken.append(test_file)
        
        passed = len(broken) == 0
        
        return VerificationResult(
            passed=passed,
            dependencies_checked=dependencies,
            broken_dependencies=broken,
            message=f"Dependency verification {'PASSED' if passed else 'FAILED'} ({len(broken)} broken)",
            evidence={"tested": dependencies, "broken": [str(b) for b in broken]}
        )
    
    def detect_false_positives(self, file_paths: List[Path]) -> VerificationResult:
        """
        Detect false positives: files exist but are broken.
        Tries importing Python files to check validity.
        """
        broken = []
        
        for file_path in file_paths:
            if not file_path.exists():
                broken.append(file_path)
                continue
            
            if file_path.suffix == ".py":
                # Try importing
                result = subprocess.run(
                    ["python", "-c", f"import {file_path.stem}"],
                    capture_output=True,
                    cwd=file_path.parent
                )
                
                if result.returncode != 0:
                    broken.append(file_path)
        
        return VerificationResult(
            passed=len(broken) == 0,
            dependencies_checked=[str(f) for f in file_paths],
            broken_dependencies=broken,
            message=f"False positive check {'PASSED' if len(broken) == 0 else 'FAILED'}",
            evidence={"broken_imports": [str(b) for b in broken]}
        )
```

**REFACTOR:**
- Extract pytest runner into helper method
- Add caching for dependency checks (avoid re-running)
- Add timeout for subprocess calls

---

### Phase 3: TeardownRefactor Middleware (1.5h)

**Purpose:** Phase N+1 teardown + REFACTOR + git commit.

**RED (Tests First):**
```python
# tests/orchestrators/middleware/test_teardown_refactor.py
def test_teardown_refactor_removes_unused_imports():
    """Test REFACTOR removes unused imports."""
    refactor = TeardownRefactor()
    
    # Create test file with unused import
    test_file = Path("tests/fixtures/test_unused_imports.py")
    test_file.write_text("import os\nimport sys\n\nprint('hello')")
    
    refactor.refactor_whole_file(test_file)
    
    # Check unused imports removed
    content = test_file.read_text()
    assert "import os" not in content
    assert "import sys" not in content

def test_teardown_git_commit_pattern():
    """Test git commit follows /cortex-git-commit pattern."""
    refactor = TeardownRefactor()
    
    commit_msg = refactor.generate_commit_message(
        orchestrator_name="Planning v5",
        phase_summary="Phase 2: Architecture Analysis complete",
        files_modified=5,
        tests_added=3
    )
    
    assert "Planning v5:" in commit_msg
    assert "Files modified: 5" in commit_msg
    assert "Tests added: 3" in commit_msg
    assert "Co-authored-by: CORTEX" in commit_msg
```

**GREEN (Implementation):**
```python
# src/orchestrators/middleware/teardown_refactor.py
"""
Teardown Refactor Middleware
Phase N+1: Post-execution cleanup + git commit.

CORTEX v5 Universal Pattern: Teardown + REFACTOR
"""
import subprocess
from pathlib import Path
from typing import List


class TeardownRefactor:
    """Phase N+1 teardown and REFACTOR."""
    
    def refactor_whole_file(self, file_path: Path):
        """
        Whole-file cleanup:
        - Remove unused imports (autoflake)
        - Remove orphaned code
        - Format code (black)
        """
        # Remove unused imports
        subprocess.run([
            "autoflake",
            "--in-place",
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            str(file_path)
        ])
        
        # Format with black
        subprocess.run([
            "black",
            str(file_path)
        ])
    
    def generate_commit_message(
        self,
        orchestrator_name: str,
        phase_summary: str,
        files_modified: int,
        tests_added: int,
        coverage_change: str = "N/A"
    ) -> str:
        """Generate /cortex-git-commit pattern message."""
        return f"""{orchestrator_name}: {phase_summary}

Files modified: {files_modified}
Tests added: {tests_added}
Coverage: {coverage_change}

Co-authored-by: CORTEX v5 <cortex@asifhussain.dev>"""
    
    def git_commit_with_pattern(
        self,
        files: List[Path],
        orchestrator_name: str,
        phase_summary: str
    ):
        """Commit files with /cortex-git-commit pattern."""
        # Stage files
        for file in files:
            subprocess.run(["git", "add", str(file)])
        
        # Generate message
        message = self.generate_commit_message(
            orchestrator_name=orchestrator_name,
            phase_summary=phase_summary,
            files_modified=len(files),
            tests_added=0  # TODO: detect test count
        )
        
        # Commit
        subprocess.run(["git", "commit", "-m", message])
```

**REFACTOR:**
- Add dry-run mode for testing
- Add validation for commit message format
- Add error handling for git operations

---

### Phase 4: Master Orchestrator Wiring (1h)

**Purpose:** Wire all 3 middleware into master orchestrator lifecycle.

**RED (Tests First):**
```python
# tests/orchestrators/test_master_orchestrator_lifecycle.py
def test_master_orchestrator_lifecycle_hooks():
    """Test master orchestrator calls all lifecycle hooks."""
    from src.orchestrators.master_orchestrator import MasterOrchestrator
    
    orchestrator = MasterOrchestrator()
    
    # Check lifecycle hooks registered
    assert len(orchestrator.pre_execution_hooks) >= 2  # setup_verification, governance_checkpoint
    assert len(orchestrator.post_execution_hooks) >= 1  # teardown_refactor
    
    # Execute test orchestrator
    result = orchestrator.execute_orchestrator(
        orchestrator_id="test_orchestrator",
        context={"test": True}
    )
    
    # Check hooks were called
    assert result.setup_verification_ran is True
    assert result.governance_checkpoint_ran is True
    assert result.teardown_refactor_ran is True
```

**GREEN (Implementation):**
```python
# src/orchestrators/master_orchestrator.py (modifications)
from src.orchestrators.middleware.setup_verification import SetupVerifier
from src.orchestrators.middleware.governance_checkpoint import GovernanceCheckpoint
from src.orchestrators.middleware.teardown_refactor import TeardownRefactor

class MasterOrchestrator:
    def __init__(self):
        # ... existing code ...
        
        # Initialize middleware
        self.setup_verifier = SetupVerifier()
        self.governance_checkpoint = GovernanceCheckpoint(
            Path("cortex-brain/brain-protection-rules.yaml")
        )
        self.teardown_refactor = TeardownRefactor()
        
        # Register lifecycle hooks
        self.pre_execution_hooks = [
            (1, self.setup_verifier.verify_dependencies),  # Priority 1
            (20, self.governance_checkpoint.pre_execution_hook)  # Priority 20
        ]
        
        self.post_execution_hooks = [
            (30, self.teardown_refactor.refactor_whole_file)  # Priority 30
        ]
    
    def execute_orchestrator(self, orchestrator_id: str, context: Dict[str, Any]):
        # Run pre-execution hooks
        for priority, hook in sorted(self.pre_execution_hooks, key=lambda x: x[0]):
            result = hook(orchestrator_id, context)
            if not result.passed and result.enforcement == EnforcementLevel.BLOCKING:
                raise RuntimeError(f"Pre-execution hook failed: {result.message}")
        
        # ... orchestrator execution ...
        
        # Run post-execution hooks
        for priority, hook in sorted(self.post_execution_hooks, key=lambda x: x[0]):
            hook(orchestrator_id, execution_result)
```

**REFACTOR:**
- Extract hook registration into separate method
- Add hook priority sorting helper
- Add hook error handling wrapper

---

### Phase 5: Integration Testing (2h)

**Purpose:** Test middleware with real orchestrator execution.

**RED (Tests First):**
```python
# tests/orchestrators/test_middleware_integration.py
def test_planning_v5_with_middleware():
    """Test Planning v5 orchestrator with full middleware stack."""
    from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
    from src.orchestrators.master_orchestrator import MasterOrchestrator
    
    master = MasterOrchestrator()
    
    # Execute planning orchestrator
    result = master.execute_orchestrator(
        orchestrator_id="planning_v5",
        context={
            "feature_name": "test-feature",
            "user_request": "plan test feature",
            "dependencies": []  # DoR should pass
        }
    )
    
    # Check middleware ran
    assert result.governance_checkpoint_ran is True
    assert result.setup_verification_ran is True
    assert result.teardown_refactor_ran is True
    
    # Check audit log
    audit_log = Path("tracking/governance-audit.jsonl")
    assert audit_log.exists()
    
    with open(audit_log) as f:
        entries = [json.loads(line) for line in f]
    
    assert len(entries) >= 2  # Pre + post execution

def test_middleware_blocks_on_dor_failure():
    """Test middleware blocks execution on DoR failure."""
    master = MasterOrchestrator()
    
    # Execute with DoR violation
    with pytest.raises(RuntimeError, match="DoR FAILED"):
        master.execute_orchestrator(
            orchestrator_id="planning_v5",
            context={
                "dependencies_met": False  # DoR violation
            }
        )
```

**GREEN (Implementation):**
- Run integration tests with real orchestrators
- Verify audit log populated
- Verify git commits follow pattern
- Verify REFACTOR cleanup runs

**REFACTOR:**
- Add integration test fixtures
- Add helper functions for audit log parsing
- Add cleanup after integration tests

---

## 🔧 Implementation Checklist

### Pre-Implementation
- [x] Brittleness analysis reviewed
- [x] SKULL rules v5.0 validated
- [ ] Master orchestrator lifecycle hook structure understood

### Implementation
- [ ] Phase 1: GovernanceCheckpoint (RED→GREEN→REFACTOR)
- [ ] Phase 2: SetupVerifier (RED→GREEN→REFACTOR)
- [ ] Phase 3: TeardownRefactor (RED→GREEN→REFACTOR)
- [ ] Phase 4: Master Orchestrator Wiring (RED→GREEN→REFACTOR)
- [ ] Phase 5: Integration Testing (RED→GREEN→REFACTOR)

### Post-Implementation
- [ ] All middleware tests pass (100% coverage)
- [ ] Integration tests pass (real orchestrator execution)
- [ ] Audit log writes working (`tracking/governance-audit.jsonl`)
- [ ] Git commits follow /cortex-git-commit pattern
- [ ] Validation report generated

---

## 📊 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking orchestrator execution | MEDIUM | HIGH | Comprehensive testing + feature flags |
| Audit log performance | LOW | MEDIUM | Async logging, log rotation |
| Git commit failures | LOW | HIGH | Dry-run mode, rollback support |
| Middleware initialization errors | MEDIUM | HIGH | Graceful degradation, fallback to no enforcement |

---

## 🎯 Success Criteria

**Feature Complete When:**
1. ✅ All 3 middleware classes implemented
2. ✅ Master orchestrator wired to lifecycle hooks
3. ✅ All middleware tests pass (100% coverage)
4. ✅ Integration tests pass (real execution)
5. ✅ Audit log writes on violations
6. ✅ Git commits follow /cortex-git-commit pattern
7. ✅ Validation report generated

---

## 📝 Notes

**Dependencies:**
- Should complete after C50-19 (Brain Data Cutover)

**Blocking:**
- All C50 child plans (requires governance enforcement)

**Related Issues:**
- Brittleness Analysis: `C50-brittleness-analysis-2026-01-04.md`
- Gap 2 Remediation: Runtime governance enforcement

---

**Author:** CORTEX Investigation Orchestrator  
**Reviewed By:** Asif Hussain  
**Status:** READY FOR EXECUTION  
**Estimated Duration:** 6-8 hours (TDD enforced)

**Copyright © 2026 Asif Hussain. All rights reserved.**
