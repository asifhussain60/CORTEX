# CORTEX 6.0 - Hallucination Prevention: Integration Architecture

**Purpose:** Technical blueprint for implementing AC-VALIDATE-* and AC-METRICS-* ACs  
**Audience:** Development team (Python/architecture level)  
**Date:** 2026-01-13

---

## Architecture Overview

### Current Flow (Phase 2)
```
User Request
  ↓
[CORTEX.prompt.md Gateway]
  ↓
[MasterOrchestrator.evaluate_intent()]
  ├→ Load governance (4-tier merger)
  ├→ Generate required_actions
  ├→ Create TodoManager tasks
  └→ Execute in dependency order

[TodoManager.track_progress()]
  ├→ Persist to progress-tracker.json
  ├→ Log to audit trail
  └→ Generate evidence bundle
```

### Enhanced Flow (With Hallucination Prevention)
```
User Request
  ↓
[CORTEX.prompt.md Gateway]
  ↓
[INPUT VALIDATION LAYER] ← NEW AC-VALIDATE-001-010
  ├→ Canonicalize intent
  ├→ Validate AC-ID format
  ├→ Check prerequisites
  ├→ Detect contradictions
  └→ Block invalid requests (with guidance)
  ↓
[MasterOrchestrator.evaluate_intent()]
  ├→ Load governance (4-tier merger)
  ├→ Generate required_actions
  ├→ Create TodoManager tasks
  └→ Execute in dependency order
  ↓
[OUTPUT VALIDATION] ← NEW AC-VALIDATE-005
  ├→ Check semantic consistency
  └→ Validate evidence manifest
  ↓
[METRICS COLLECTION] ← NEW AC-METRICS-001-005
  ├→ Track test success rate
  ├→ Record execution latency
  ├→ Verify evidence completeness
  ├→ Log governance violations
  └→ Alert on anomalies
  ↓
[TodoManager.track_progress()]
  ├→ Persist to progress-tracker.json
  ├→ Log to audit trail
  └→ Generate evidence bundle
```

---

## Implementation Points

### 1. AC-VALIDATE-001: Intent Canonicalization

**Where:** Pre-routing in CORTEX.prompt.md or MasterOrchestrator.__init__

```python
# File: src/orchestrators/core/master_orchestrator.py

from src.orchestrators.validation.intent_canonicalizer import IntentCanonicalizer

class MasterOrchestrator:
    def __init__(self, user_intent: str):
        # AC-VALIDATE-001: Canonicalize intent
        self.canonicalizer = IntentCanonicalizer()
        self.canonical_intent = self.canonicalizer.canonicalize(user_intent)
        
        # Example: "  IMPLEMENT  ac-audit-001  " → "implement AC-AUDIT-001"
        
    def evaluate_intent(self) -> Dict[str, Any]:
        """
        Evaluate canonical intent against governance.
        
        AC-VALIDATE-001 ensures input is normalized:
        - Whitespace trimmed
        - Case standardized (AC-IDs to uppercase)
        - Unicode normalization (NFC)
        - Special characters handled consistently
        """
        # Continue with normalized intent
```

**New Module:** `src/orchestrators/validation/intent_canonicalizer.py`

```python
import unicodedata
from typing import Optional

class IntentCanonicalizer:
    """Normalize user intent for consistent processing."""
    
    def canonicalize(self, intent: str) -> str:
        """
        Canonicalize user intent.
        
        AC-VALIDATE-001 Implementation:
        1. Strip whitespace
        2. Unicode NFC normalization (ä → a + ¨)
        3. Uppercase AC-IDs
        4. Remove extra spaces
        5. Log original + canonical for audit
        
        Latency target: <10ms
        """
        # 1. Strip
        intent = intent.strip()
        
        # 2. Unicode normalize (NFC)
        intent = unicodedata.normalize('NFC', intent)
        
        # 3. Uppercase AC-IDs (AC-* pattern)
        import re
        intent = re.sub(
            r'\bac-([a-z]+)-(\d+)\b',
            lambda m: f'AC-{m.group(1).upper()}-{m.group(2)}',
            intent,
            flags=re.IGNORECASE
        )
        
        # 4. Normalize spacing
        intent = ' '.join(intent.split())
        
        # 5. Audit log
        self.audit_log(original=intent, canonical=intent)
        
        return intent
```

---

### 2. AC-VALIDATE-002: AC-ID Existence Check

**Where:** Post-canonicalization in MasterOrchestrator

```python
# File: src/orchestrators/core/master_orchestrator.py

from src.orchestrators.validation.ac_validator import ACValidator

class MasterOrchestrator:
    def __init__(self, user_intent: str):
        self.ac_validator = ACValidator(ac_index_path)
        
    def evaluate_intent(self) -> Dict[str, Any]:
        """
        AC-VALIDATE-002: Check AC-IDs exist
        
        Extract AC-IDs from canonical intent and verify they exist in AC-INDEX.
        """
        # Extract AC-IDs from intent
        ac_ids = self._extract_ac_ids(self.canonical_intent)
        
        # Validate each AC-ID exists
        invalid_ids = self.ac_validator.validate_exist(ac_ids)
        
        if invalid_ids:
            raise InvalidACIDError(
                f"AC-IDs not found: {invalid_ids}",
                suggestions=self.ac_validator.suggest_similar(invalid_ids),
                log_level=AuditLevel.WARNING
            )
        
        # Continue with validated AC-IDs
```

**New Module:** `src/orchestrators/validation/ac_validator.py`

```python
from typing import List, Set
import yaml

class ACValidator:
    """Validate AC-IDs against AC-INDEX."""
    
    def __init__(self, ac_index_path: str):
        self.ac_index = yaml.safe_load(open(ac_index_path))
        self.valid_ac_ids = set(self.ac_index['acceptance_criteria'].keys())
    
    def validate_exist(self, ac_ids: List[str]) -> List[str]:
        """
        AC-VALIDATE-002: Check AC-IDs exist.
        
        Return: List of invalid AC-IDs (empty if all valid)
        Latency: <5ms for 100 AC-IDs
        """
        invalid = []
        for ac_id in ac_ids:
            if ac_id not in self.valid_ac_ids:
                invalid.append(ac_id)
                self.audit_log(ac_id=ac_id, status="NOT_FOUND")
        return invalid
    
    def suggest_similar(self, invalid_ids: List[str]) -> List[str]:
        """Suggest correct AC-IDs using fuzzy matching."""
        # Use difflib to find similar AC-IDs
        from difflib import get_close_matches
        suggestions = []
        for invalid_id in invalid_ids:
            matches = get_close_matches(invalid_id, self.valid_ac_ids, n=3)
            suggestions.extend(matches)
        return suggestions
```

---

### 3. AC-VALIDATE-007: Phase Alignment Enforcement

**Where:** In ACValidator, after existence check

```python
# File: src/orchestrators/validation/ac_validator.py

class ACValidator:
    def validate_phase_alignment(self, ac_ids: List[str], current_phase: int) -> List[str]:
        """
        AC-VALIDATE-007: Ensure AC-IDs match current phase.
        
        CORTEX operates in phases. Can't implement Phase 4 AC while in Phase 2.
        
        Rule: ac_phase <= current_phase
        Action: WARN if out of order, ERROR if from future phases
        """
        out_of_order = []
        
        for ac_id in ac_ids:
            ac_info = self.ac_index['acceptance_criteria'][ac_id]
            ac_phase = ac_info.get('phase')
            
            if ac_phase > current_phase:
                out_of_order.append({
                    'ac_id': ac_id,
                    'ac_phase': ac_phase,
                    'current_phase': current_phase,
                    'message': f"{ac_id} is Phase {ac_phase}, can't implement in Phase {current_phase}"
                })
                self.audit_log(
                    ac_id=ac_id,
                    status="OUT_OF_ORDER",
                    severity="ERROR"
                )
            elif ac_phase < current_phase - 1:
                # Warning: AC is from 2+ phases ago (likely legacy)
                self.audit_log(
                    ac_id=ac_id,
                    status="OLD_PHASE",
                    severity="WARNING"
                )
        
        return out_of_order
```

---

### 4. AC-METRICS-001: Test Success Rate Tracking

**Where:** Post-execution in TodoManager

```python
# File: src/orchestrators/core/todo_manager.py

from src.infrastructure.metrics_tracker import MetricsTracker

class TodoManager:
    def __init__(self):
        self.metrics = MetricsTracker()
    
    def track_task_completion(self, task_id: str, test_results: Dict) -> None:
        """
        Track metrics for anomaly detection.
        
        AC-METRICS-001: Test success rate baseline + deviation
        """
        # Extract test metrics
        total_tests = test_results['total']
        passed_tests = test_results['passed']
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        # Get historical baseline
        baseline = self.metrics.get_baseline(
            orchestrator_id=task_id,
            metric='test_success_rate'
        )
        
        # Check for deviation
        if baseline is not None:
            deviation = abs(success_rate - baseline) / baseline
            
            if deviation > 0.20:  # 20% drop triggers alert
                self.metrics.alert(
                    level="HIGH",
                    message=f"Test success rate drop: {baseline:.1%} → {success_rate:.1%}",
                    action="QUARANTINE_ORCHESTRATOR",
                    threshold=deviation
                )
                self.audit_log(
                    status="ANOMALY_DETECTED",
                    metric="test_success_rate",
                    deviation=deviation
                )
        
        # Store for baseline
        self.metrics.record(
            orchestrator_id=task_id,
            metric='test_success_rate',
            value=success_rate,
            timestamp=datetime.now()
        )
```

**New Module:** `src/infrastructure/metrics_tracker.py`

```python
from typing import Optional, Dict
import sqlite3
from datetime import datetime, timedelta

class MetricsTracker:
    """Track orchestrator health metrics for anomaly detection."""
    
    def __init__(self, db_path: str = "cortex-brain/database/metrics.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create metrics schema if not exists."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orchestrator_metrics (
                id INTEGER PRIMARY KEY,
                orchestrator_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(orchestrator_id, metric_name, timestamp)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metric_baselines (
                orchestrator_id TEXT PRIMARY KEY,
                metric_name TEXT,
                baseline_value REAL,
                sample_count INTEGER,
                last_updated DATETIME
            )
        """)
        conn.commit()
        conn.close()
    
    def get_baseline(self, orchestrator_id: str, metric: str) -> Optional[float]:
        """Get historical baseline for orchestrator metric."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT baseline_value FROM metric_baselines WHERE orchestrator_id = ? AND metric_name = ?",
            (orchestrator_id, metric)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def record(self, orchestrator_id: str, metric: str, value: float, timestamp: datetime):
        """Record metric value."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO orchestrator_metrics (orchestrator_id, metric_name, metric_value, timestamp) VALUES (?, ?, ?, ?)",
            (orchestrator_id, metric, value, timestamp)
        )
        
        # Update baseline (running average)
        self._update_baseline(conn, orchestrator_id, metric, value)
        
        conn.commit()
        conn.close()
    
    def _update_baseline(self, conn: sqlite3.Connection, orchestrator_id: str, metric: str, new_value: float):
        """Update running average baseline."""
        # Fetch last 10 values
        cursor = conn.execute(
            """SELECT metric_value FROM orchestrator_metrics 
               WHERE orchestrator_id = ? AND metric_name = ? 
               ORDER BY timestamp DESC LIMIT 10""",
            (orchestrator_id, metric)
        )
        values = [row[0] for row in cursor.fetchall()]
        values.append(new_value)
        
        # Calculate new baseline
        new_baseline = sum(values) / len(values)
        
        # Update or insert
        conn.execute(
            """INSERT OR REPLACE INTO metric_baselines 
               (orchestrator_id, metric_name, baseline_value, sample_count, last_updated)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (orchestrator_id, metric, new_baseline, len(values))
        )
    
    def alert(self, level: str, message: str, action: str, threshold: float):
        """Log anomaly alert to audit trail."""
        from src.infrastructure.enhanced_audit_logger import LOGGER
        
        LOGGER.log(
            level=AuditLevel.WARNING if level == "HIGH" else AuditLevel.INFO,
            category=AuditCategory.INFRASTRUCTURE,
            component="MetricsTracker",
            operation="anomaly_detected",
            message=message,
            metadata={
                'action': action,
                'threshold': threshold
            }
        )
```

---

### 5. AC-METRICS-004: Governance Violation Alerting

**Where:** In GovernanceMerger, post-rule evaluation

```python
# File: src/orchestrators/core/governance_merger.py

from src.infrastructure.metrics_tracker import MetricsTracker

class GovernanceMerger:
    def __init__(self):
        self.metrics = MetricsTracker()
    
    def merge_governance(self) -> Dict:
        """
        Merge 4 tiers of governance rules.
        
        AC-METRICS-004: Track governance violations
        """
        merged = self._merge_tiers()
        violations = self._check_violations(merged)
        
        # Log violations
        for violation in violations:
            self.metrics.record(
                orchestrator_id='system',
                metric='governance_violations',
                value=1,  # Count
                timestamp=datetime.now()
            )
            
            self.audit_log(
                status="VIOLATION",
                rule_id=violation['rule_id'],
                severity=violation['severity'],
                message=violation['message']
            )
            
            # Alert on high-severity
            if violation['severity'] == 'HIGH':
                self.metrics.alert(
                    level="HIGH",
                    message=f"Governance violation: {violation['rule_id']}",
                    action="BLOCK_OPERATION",
                    threshold=0
                )
        
        return merged
```

---

### 6. AC-VALIDATE-005: Semantic Output Validation

**Where:** Post-evidence generation in TodoManager

```python
# File: src/orchestrators/core/todo_manager.py

from src.orchestrators.validation.semantic_validator import SemanticValidator

class TodoManager:
    def __init__(self):
        self.semantic_validator = SemanticValidator()
    
    def generate_evidence_bundle(self, task_id: str) -> Dict:
        """
        Generate evidence bundle.
        
        AC-VALIDATE-005: Check output makes semantic sense
        """
        bundle = self._collect_evidence(task_id)
        
        # AC-VALIDATE-005: Semantic validation
        validation_result = self.semantic_validator.validate(
            bundle=bundle,
            ac_id=task_id,
            context={
                'orchestrator_id': self.orchestrator_id,
                'phase': self.current_phase,
                'previous_implementations': self._get_implemented_acs()
            }
        )
        
        if not validation_result.is_valid:
            self.audit_log(
                status="VALIDATION_FAILED",
                errors=validation_result.errors,
                warnings=validation_result.warnings
            )
            
            if validation_result.is_critical:
                raise SemanticValidationError(
                    f"Output validation failed: {validation_result.errors}",
                    suggestions=validation_result.suggestions
                )
        
        return bundle
```

**New Module:** `src/orchestrators/validation/semantic_validator.py`

```python
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    is_critical: bool = False

class SemanticValidator:
    """Validate orchestrator output for semantic consistency."""
    
    def validate(self, bundle: Dict, ac_id: str, context: Dict) -> ValidationResult:
        """
        AC-VALIDATE-005: Check semantic consistency.
        
        Checks:
        1. Test results exist and are valid JSON
        2. Manifest covers all implementation claims
        3. Audit trace complete (start + end timestamps)
        4. No contradictions with previous implementations
        5. Evidence completeness (manifest + tests + audit all present)
        """
        errors = []
        warnings = []
        suggestions = []
        
        # Check 1: Test results valid
        if not self._validate_test_results(bundle.get('test_results')):
            errors.append("test_results.json missing or invalid")
            suggestions.append("Ensure pytest was executed and results saved")
        
        # Check 2: Manifest valid
        manifest = bundle.get('manifest')
        if not manifest or not self._validate_manifest(manifest):
            errors.append("manifest.yaml missing or incomplete")
        
        # Check 3: Audit trace complete
        audit_trace = bundle.get('audit_trace')
        if not audit_trace or not self._validate_audit_trace(audit_trace):
            errors.append("audit_trace.jsonl incomplete")
        
        # Check 4: No contradictions
        contradictions = self._check_contradictions(ac_id, context)
        if contradictions:
            warnings.extend(contradictions)
        
        # Check 5: All files present
        missing_files = self._check_completeness(bundle)
        if missing_files:
            errors.extend([f"Missing: {f}" for f in missing_files])
        
        is_critical = len(errors) > 0
        is_valid = not is_critical
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            is_critical=is_critical
        )
    
    def _check_contradictions(self, ac_id: str, context: Dict) -> List[str]:
        """Check for contradictions with previous implementations."""
        # TODO: Implement AC-COHERENCE-001 style checking
        # For now, just placeholder
        return []
```

---

## Testing Strategy for AC-VALIDATE-* and AC-METRICS-*

### Test Structure

```
tests/
  unit/
    test_intent_canonicalizer.py         # AC-VALIDATE-001
    test_ac_validator.py                 # AC-VALIDATE-002, 007
    test_semantic_validator.py           # AC-VALIDATE-005
    test_metrics_tracker.py              # AC-METRICS-001-005
  
  integration/
    test_validation_flow.py              # End-to-end AC-VALIDATE
    test_metrics_anomaly_detection.py    # Anomaly alerts
  
  golden_corpus/
    validation_intents.yaml              # 100 intents for golden corpus
```

### Example Test Suite (AC-VALIDATE-002)

```python
# tests/unit/test_ac_validator.py

import pytest
from src.orchestrators.validation.ac_validator import ACValidator

class TestACValidator:
    """Test AC-VALIDATE-002: AC-ID existence check"""
    
    @pytest.fixture
    def validator(self):
        return ACValidator("cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml")
    
    def test_valid_ac_id(self, validator):
        """Test valid AC-ID passes"""
        result = validator.validate_exist(["AC-AUDIT-001"])
        assert result == []  # No errors
    
    def test_invalid_ac_id(self, validator):
        """Test invalid AC-ID caught"""
        result = validator.validate_exist(["AC-FAKE-999"])
        assert "AC-FAKE-999" in result
    
    def test_multiple_mixed(self, validator):
        """Test mix of valid and invalid"""
        result = validator.validate_exist([
            "AC-AUDIT-001",  # Valid
            "AC-FAKE-999",   # Invalid
            "AC-GOV-001",    # Valid
        ])
        assert result == ["AC-FAKE-999"]
    
    def test_latency_under_5ms(self, validator):
        """Test AC-VALIDATE-002 latency target <5ms"""
        import time
        start = time.perf_counter()
        validator.validate_exist(["AC-AUDIT-001"] * 100)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.005  # 5ms
```

---

## Deployment Plan

### Phase 2 Integration Timeline

```
Week 1 (Days 1-5): Foundation
  ☐ Create src/orchestrators/validation/ module
  ☐ Implement AC-VALIDATE-001 (intent canonicalizer)
  ☐ Implement AC-VALIDATE-002 (AC-ID validator)
  ☐ Write unit tests for both
  ☐ Update AC-INDEX.yaml with new AC-IDs
  Effort: ~20 person-hours

Week 1.5 (Days 6-8): Integration + Metrics
  ☐ Integrate AC-VALIDATE into MasterOrchestrator
  ☐ Create src/infrastructure/metrics_tracker.py
  ☐ Implement AC-METRICS-001-005
  ☐ Integrate metrics into TodoManager + GovernanceMerger
  ☐ Create metrics.db schema
  Effort: ~20 person-hours

Week 2 (Days 9-10): Validation + Testing
  ☐ Implement AC-VALIDATE-003-010 (remaining validators)
  ☐ Write integration tests (end-to-end flow)
  ☐ Test golden corpus (100 intents)
  ☐ Measure false positive rate <1%
  ☐ Performance testing (latency targets)
  Effort: ~15 person-hours

Total: ~55 person-hours (1 person-week + 2 days)
```

---

## Migration Notes

### Backwards Compatibility

```
Current orchestrators (Phase 1) work WITHOUT validation:
  ✓ AC-VALIDATE-* checks are optional (warn, don't block)
  ✓ AC-METRICS-* tracking added, no functional change
  
New orchestrators (Phase 2+) MUST pass validation:
  ✓ AC-VALIDATE-002-010 enforced (block on failure)
  ✓ AC-METRICS data required for gate validation
```

---

**End of Integration Architecture Document**

