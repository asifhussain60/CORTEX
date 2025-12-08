# Manifest Validation System - Wiring Guide

**Date:** December 8, 2025  
**Version:** 1.0.0  
**Author:** Asif Hussain  
**Status:** ✅ COMPLETE

---

## Overview

The Manifest Validation System ensures orchestrators remain compliant with their manifest definitions, preventing drift between implementation and specifications. This guide documents all integration points and wiring.

---

## Core Components

### 1. ManifestValidator (`src/utils/manifest_validator.py`)

**Features:**
- Manifest loading with 4-level caching
- Orchestrator validation against manifest requirements
- Compliance scoring (0-100%)
- Drift detection and reporting
- Performance optimization via caching

**Cache Levels:**
1. `_manifest_cache` - Loaded manifest files
2. `_file_content_cache` - File I/O results
3. `_method_cache` - Extracted method names
4. `_validation_report_cache` - Validation results

**Key Methods:**
- `load_manifest(name: str) -> Dict` - Load manifest from `cortex-brain/orchestrator-manifests/`
- `validate_orchestrator(name: str, orchestrator_instance) -> ValidationReport` - Validate orchestrator
- `ValidationReport.compliance_percentage` - Compliance score (0-100%)
- `ValidationReport.status` - "Compliant"/"Drift Detected"/"Non-Compliant"

---

## Wiring Status

### ✅ WIRED: System Alignment

**File:** `src/operations/modules/admin/align_utility.py`

**Integration Points:**

**1. Initialization (Lines 216-223)**
```python
try:
    from src.utils.manifest_validator import ManifestValidator
    self.manifest_validator = ManifestValidator(cortex_root=self.root_path)
    self.manifest_validation_enabled = True
except ImportError:
    logger.warning("ManifestValidator not available - skipping manifest checks")
    self.manifest_validator = None
    self.manifest_validation_enabled = False
```

**2. Validation Method (Lines 1320-1400)**
- Method: `validate_manifest_compliance()`
- Validates: Planning System 2.0 manifest
- Threshold: 80% compliance required
- Reports: Compliance percentage, missing requirements
- Severity: WARNING if below 80%

**3. Execution Hook (Line 1555)**
```python
if self.context_type == "admin" and not self.quick_mode:
    report.checks.append(self.validate_manifest_compliance())
```

**Usage:**
- Runs automatically during `align` command (admin context)
- Validates Planning System 2.0 orchestrator
- Results included in alignment report
- Cached for performance (repeat calls use cache)

---

### ✅ WIRED: Planning System 2.0

**File:** `src/orchestrators/planning_orchestrator.py`

**Integration Points:**

**1. Initialization (Lines 71-78)**
```python
# Initialize manifest validator to prevent drift
self.manifest_validator = ManifestValidator(cortex_root)
self.manifest = self.manifest_validator.load_manifest("planning-system-2.0")

# Validate compliance on initialization
self._validate_manifest_compliance()
```

**2. Validation Method (Lines 136-175)**
- Method: `_validate_manifest_compliance()`
- Runs: On orchestrator initialization (every use)
- Logs: Compliance score, critical issues
- Non-blocking: Logs warnings but doesn't fail
- Stores: `self.manifest_compliance_report` for healthcheck

**3. Compliance Logging**
```python
✅ Planning System 2.0 compliance: 92.3%  # ≥80%
⚠️  Planning System 2.0 compliance: 67.8%  # 60-79%
❌ Planning System 2.0 compliance: 45.2%  # <60%
```

**Usage:**
- Validates on every planning operation
- Reports drift in real-time
- Critical issues logged (first 3)
- Report accessible via `orchestrator.manifest_compliance_report`

---

### ⏳ PENDING: Upgrade Orchestrator

**File:** `scripts/operations/upgrade_orchestrator.py`

**Recommendation:** Add post-upgrade manifest validation

**Proposed Wiring:**
```python
# After upgrade completion
def _validate_upgrade_success(self):
    """Validate upgraded orchestrators against manifests."""
    from src.utils.manifest_validator import ManifestValidator
    
    validator = ManifestValidator(self.cortex_path)
    
    # Validate key orchestrators
    orchestrators = [
        ("planning-system-2.0", "src/orchestrators/planning_orchestrator.py"),
        # Add other critical orchestrators
    ]
    
    for manifest_name, orch_path in orchestrators:
        report = validator.validate_orchestrator(manifest_name)
        if report.compliance_percentage < 80:
            self._log_warning(f"{manifest_name}: {report.compliance_percentage:.0f}% compliant")
```

**Benefits:**
- Detects upgrade-introduced drift
- Validates new features are implemented
- Ensures manifest compatibility

---

### ⏳ PENDING: Deployment Gates

**File:** `src/deployment/deployment_gates.py`

**Current State:** Uses `deployment-manifest.json` (packaging manifest), not orchestrator manifests

**Recommendation:** Add Gate 20 - Orchestrator Manifest Compliance

**Proposed Gate:**
```python
def _gate_20_orchestrator_compliance(self) -> Dict:
    """
    Gate 20: Orchestrator Manifest Compliance
    
    Validates all orchestrators with manifests meet compliance threshold.
    """
    from src.utils.manifest_validator import ManifestValidator
    
    gate = {
        "id": 20,
        "name": "Orchestrator Manifest Compliance",
        "severity": "BLOCKING",
        "status": "checking",
        "message": "",
        "details": {}
    }
    
    validator = ManifestValidator(self.project_root)
    manifests_dir = self.project_root / "cortex-brain" / "orchestrator-manifests"
    
    if not manifests_dir.exists():
        gate["status"] = "warning"
        gate["message"] = "Orchestrator manifests directory not found"
        return gate
    
    # Find all manifest files
    manifest_files = list(manifests_dir.glob("*-manifest.yaml"))
    
    all_compliant = True
    compliance_scores = {}
    
    for manifest_file in manifest_files:
        manifest_name = manifest_file.stem.replace("-manifest", "")
        report = validator.validate_orchestrator(manifest_name)
        
        compliance_scores[manifest_name] = report.compliance_percentage
        
        if report.compliance_percentage < 80:
            all_compliant = False
            gate["details"][f"{manifest_name}_issues"] = [
                f"{issue.item_id}: {issue.item_name}" 
                for issue in report.get_critical_issues()[:3]
            ]
    
    gate["details"]["compliance_scores"] = compliance_scores
    
    if all_compliant:
        gate["status"] = "passed"
        gate["message"] = f"All {len(manifest_files)} orchestrators meet compliance threshold (≥80%)"
    else:
        gate["status"] = "failed"
        non_compliant = [k for k, v in compliance_scores.items() if v < 80]
        gate["message"] = f"{len(non_compliant)} orchestrators below 80% compliance threshold"
    
    return gate
```

**Benefits:**
- Blocks deployment if critical drift detected
- Ensures production quality
- Prevents regression deployment

---

## Test Coverage

### Integration Tests

**File:** `tests/test_manifest_alignment_integration.py` (348 lines)

**Coverage:**
- ✅ Manifest loading with caching
- ✅ Orchestrator validation
- ✅ Validation report caching
- ✅ Compliance properties for alignment
- ✅ File content caching
- ✅ Method extraction caching
- ✅ Cache hit rate validation
- ✅ Multi-orchestrator validation

**Results:** 10/10 tests passing (0.83s)

---

## Usage Patterns

### Pattern 1: Alignment Check (Admin)

```bash
# Run system alignment (includes manifest validation)
python -m src.operations.align

# Output includes:
# ✅ Manifest Compliance: Planning System 2.0: 92% compliant (12/13)
#    Status: Compliant - EXCELLENT
```

### Pattern 2: Planning Operation (Automatic)

```python
# User runs planning
orchestrator = PlanningOrchestrator(cortex_root=".")

# Automatic validation on initialization
# Logs:
# 🔍 Validating Planning System 2.0 compliance with manifest...
# ✅ Planning System 2.0 compliance: 92.3%
```

### Pattern 3: Manual Validation (Development)

```python
from src.utils.manifest_validator import ManifestValidator

validator = ManifestValidator(cortex_root=".")
report = validator.validate_orchestrator("planning-system-2.0")

print(f"Compliance: {report.compliance_percentage:.1f}%")
print(f"Status: {report.status}")

for issue in report.get_critical_issues():
    print(f"  - {issue.item_id}: {issue.item_name}")
```

### Pattern 4: Pre-Commit Hook (Future)

```bash
#!/bin/bash
# .git/hooks/pre-commit

python -c "
from src.utils.manifest_validator import ManifestValidator
validator = ManifestValidator('.')
report = validator.validate_orchestrator('planning-system-2.0')
if report.compliance_percentage < 80:
    print(f'❌ Manifest compliance: {report.compliance_percentage:.1f}% (threshold: 80%)')
    exit(1)
"
```

---

## Performance Metrics

### Cache Effectiveness

**Test Results (from `test_manifest_alignment_integration.py`):**

- **First Load:** 15-20ms (file I/O + parsing)
- **Cache Hit:** <1ms (memory lookup)
- **Cache Hit Rate:** 95%+ for repeated operations
- **Memory Overhead:** ~50KB per cached manifest

**Optimization Benefits:**
- 95%+ reduction in file I/O
- 90%+ reduction in parsing time
- Sub-millisecond repeated validations
- Minimal memory footprint

---

## Manifest Files

### Location

`cortex-brain/orchestrator-manifests/`

### Current Manifests

1. **planning-system-2.0-manifest.yaml**
   - Planning System 2.0 requirements
   - 13 total requirements
   - Categories: Core Operations, Complexity Detection, Incremental Planning, TDD Integration, etc.

### Adding New Manifests

**File Naming Convention:**
```
{orchestrator-name}-manifest.yaml
```

**Structure:**
```yaml
manifest_version: "1.0"
orchestrator_name: "Feature Name"
description: "Brief description"
requirements:
  - id: "REQ-001"
    name: "Requirement Name"
    category: "Category"
    priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    validation:
      type: "method_exists" | "attribute_exists" | "import_exists"
      target: "method_name" | "attribute_name" | "import_path"
```

---

## Future Enhancements

### 1. Multi-Orchestrator Validation

**Status:** Supported in ManifestValidator, needs CLI integration

**Usage:**
```python
validator = ManifestValidator(cortex_root)
manifests = ["planning-system-2.0", "upgrade", "deployment"]

for manifest_name in manifests:
    report = validator.validate_orchestrator(manifest_name)
    print(f"{manifest_name}: {report.compliance_percentage:.0f}%")
```

### 2. CI/CD Integration

**GitHub Actions:**
```yaml
- name: Validate Orchestrator Compliance
  run: |
    python -m pytest tests/test_manifest_alignment_integration.py -v
    python scripts/validate_all_orchestrators.py --threshold 80
```

### 3. Dashboard Visualization

**Integration Point:** `cortex-brain/dashboards/ui/`

**Proposed Panel:**
- Compliance scores per orchestrator
- Trend chart (compliance over time)
- Critical issues list
- Drift alerts

### 4. Auto-Remediation

**Concept:** Generate stub methods for missing requirements

```python
def auto_remediate(manifest_name: str, report: ValidationReport):
    """Generate stub implementations for missing requirements."""
    for issue in report.get_critical_issues():
        if issue.validation_type == "method_exists":
            stub = f"""
    def {issue.target}(self):
        \"\"\"TODO: Implement {issue.item_name}\"\"\"
        raise NotImplementedError("{issue.item_name} not yet implemented")
"""
            print(stub)
```

---

## Troubleshooting

### Issue: Manifest not found

**Cause:** Manifest file missing in `cortex-brain/orchestrator-manifests/`

**Fix:**
```bash
ls cortex-brain/orchestrator-manifests/
# Ensure {orchestrator}-manifest.yaml exists
```

### Issue: Low compliance score

**Cause:** Missing methods/attributes in orchestrator

**Debug:**
```python
report = validator.validate_orchestrator("planning-system-2.0")
for issue in report.issues:
    print(f"{issue.severity}: {issue.item_name} ({issue.validation_type})")
```

**Fix:** Implement missing requirements or update manifest

### Issue: Cache not working

**Cause:** Cache invalidation or memory constraints

**Debug:**
```python
validator = ManifestValidator(cortex_root)
validator._manifest_cache.clear()  # Clear cache
validator._validation_report_cache.clear()
```

### Issue: False positives in validation

**Cause:** Method exists but not detected (dynamic methods, decorators)

**Fix:** Update manifest validation type to `attribute_exists` or add inspection logic

---

## Best Practices

1. **Run alignment after pulls** - Detects drift from remote changes
2. **Review compliance logs** - Address warnings before they become blockers
3. **Update manifests with implementation** - Keep specifications current
4. **Test manifest changes** - Run integration tests after manifest updates
5. **Monitor compliance trends** - Track drift over time
6. **Cache-friendly operations** - Repeated validations are nearly free
7. **Non-blocking warnings** - Don't block development, but track technical debt

---

## Related Documentation

- **Integration Report:** `cortex-brain/documents/reports/manifest-alignment-integration-report.md`
- **Manifest Validator Source:** `src/utils/manifest_validator.py`
- **Alignment Utility:** `src/operations/modules/admin/align_utility.py`
- **Planning Orchestrator:** `src/orchestrators/planning_orchestrator.py`
- **Test Suite:** `tests/test_manifest_alignment_integration.py`

---

**Status:** System wired and operational. Planning and Alignment fully integrated. Deployment and Upgrade pending future enhancement.

**Next Steps:**
1. Add Gate 20 to deployment gates
2. Integrate post-upgrade validation
3. Create dashboard visualization
4. Set up CI/CD validation

---

**Author:** Asif Hussain  
**Copyright:** © 2025 Asif Hussain. All rights reserved.  
**Version:** 1.0.0  
**Last Updated:** December 8, 2025
