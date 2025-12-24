# Dashboard Reconciliation Engine - Quick Reference

**Version:** 1.0.0 | **Author:** Asif Hussain | **Status:** ✅ Production Ready

---

## Overview

The Dashboard Reconciliation Engine validates and adjusts dashboard metrics using industry standards (CVSS v3.1/v4.0, OWASP Top 10 2025, ISO 27001, SOC 2) to ensure accuracy and consistency.

## Automatic Integration

Reconciliation runs **automatically** during dashboard generation. No manual intervention required.

```bash
# Dashboard generation now includes reconciliation
python -m src.orchestrators.dashboard_collector --path /path/to/repo
```

**Output:**
- Dashboard data: `cortex-brain/dashboards/{repo}/`
- Reconciliation report: `cortex-brain/dashboards/{repo}/reconciliation.json`

---

## What Gets Reconciled

### Core Metrics
- **Security Score** (35% weight)
- **Quality Score** (25% weight)
- **Maintainability Score** (15% weight)
- **Architecture Score** (15% weight)
- **Test Coverage** (10% weight)

### Validation Rules (15 total)

**Constraint Validators (R1-R7, R13-R14):**
- R1: Critical vulnerabilities cap security at 30
- R2: 5+ high vulns cap at 50, 3-4 cap at 60
- R3: Security <30 floors overall at 10, <50 floors at 30
- R4: OWASP violations reduce security by 10 per violation
- R5: 100+ code smells floor quality at 30
- R6: Complexity >20 caps maintainability at 40
- R7: Coverage <30% floors quality at 20, <50% at 40
- R13: Debug mode in prod = critical violation
- R14: Hardcoded secrets reduce security by 25 per secret

**Cross-Tab Validators (R8-R10):**
- R8: Security <50 AND Quality <50 cap overall at 50
- R9: Architecture >80 with Security <40 = anomaly (confidence ≥0.8)
- R10: Complexity >15 with Maintainability >80 caps at 70

---

## Reading Reconciliation Reports

### Report Structure

```json
{
  "reconciliation_timestamp": "2025-12-07T11:30:00",
  "reconciliation_version": "1.0.0",
  "repository": "my-project",
  "execution_time_ms": 8.5,
  
  "reconciled_data": {
    "security_score": 65,
    "quality_score": 72,
    "overall_score": 68.5,
    ...
  },
  
  "violations": [
    {
      "rule_id": "R2",
      "severity": "high",
      "message": "5+ high vulnerabilities found (8 total)",
      "original_score": 75,
      "adjusted_score": 50,
      "adjustment": -25,
      "rationale": "High vulnerability count requires security score cap"
    }
  ],
  
  "anomalies": [
    {
      "type": "score_inconsistency",
      "confidence": 0.92,
      "category": "architecture_security",
      "message": "High architecture (85) with low security (38)",
      "recommendation": "Review security architecture patterns"
    }
  ],
  
  "audit_trail": {
    "changes": [...],
    "rules_triggered": 3,
    "anomalies_detected": 1
  },
  
  "metrics": {
    "total_adjustments": 5,
    "total_score_delta": -12.5,
    "violations_count": 3,
    "anomalies_count": 1,
    "confidence_average": 0.87
  }
}
```

### Interpreting Results

**Violations (🚨 Action Required):**
- **Critical:** Immediate fix required (hardcoded secrets, debug mode in prod)
- **High:** Fix ASAP (critical/high vulns, low security/coverage)
- **Medium:** Address soon (complexity issues, quality problems)
- **Low:** Plan to fix (minor inconsistencies)

**Anomalies (🔍 Investigate):**
- **Confidence ≥0.9:** Very likely real issue - investigate immediately
- **Confidence 0.7-0.9:** Probable issue - review when convenient
- **Confidence <0.7:** Possible false positive - lower priority

**Audit Trail:**
- Shows every score change with justification
- Track which rules fired and why
- Understand reconciliation decisions

---

## Configuration

**File:** `cortex-brain/reconciliation-config.yaml`

### Common Adjustments

**Change Scoring Weights:**
```yaml
scoring_weights:
  security: 0.40      # Increase security importance
  quality: 0.20
  maintainability: 0.15
  architecture: 0.15
  test_coverage: 0.10
```

**Adjust Thresholds:**
```yaml
thresholds:
  quality_floor:
    min_quality_score: 40  # Raise minimum quality
    code_smell_threshold: 50  # Lower tolerance
```

**Disable Rules:**
```yaml
thresholds:
  complexity_penalty:
    enabled: false  # Temporarily disable R6
```

**Change CVSS Ranges:**
```yaml
cvss:
  version: "4.0"  # Use CVSS v4.0 instead of v3.1
  ranges:
    critical:
      min: 9.5  # Stricter critical threshold
      max: 10.0
```

---

## Troubleshooting

### Reconciliation Skipped

**Symptoms:** Log shows "Reconciliation skipped" or missing reconciliation.json

**Causes:**
1. Import error (reconciliation package not found)
2. Data format mismatch (missing required fields)
3. Engine crash (exception during reconciliation)

**Solutions:**
```bash
# Check imports
python -c "from src.dashboard.reconciliation import ReconciliationEngine; print('✓ OK')"

# Check test suite
pytest tests/dashboard/reconciliation/ -v

# Enable debug logging
export LOG_LEVEL=DEBUG
python -m src.orchestrators.dashboard_collector --path /path/to/repo
```

### Unexpected Score Adjustments

**Symptom:** Scores lower than expected

**Investigation:**
1. Check `violations` array in reconciliation.json
2. Review `audit_trail.changes` for specific adjustments
3. Verify raw scores in main dashboard data files

**Example:**
```json
// In reconciliation.json
"audit_trail": {
  "changes": [
    {
      "category": "security",
      "field": "score",
      "before": 85,
      "after": 50,
      "reason": "R2: Capped due to 5+ high vulnerabilities"
    }
  ]
}
```

**Resolution:** Fix underlying issue (e.g., reduce high vulnerabilities) or adjust R2 threshold in config.

### False Positive Anomalies

**Symptom:** Anomalies with low confidence (<0.7)

**Solution:** Adjust confidence thresholds in config:
```yaml
anomaly_detection:
  min_confidence: 0.8  # Raise from 0.7 to reduce false positives
```

---

## Performance

**Typical Execution Times:**
- Small repos (<1K files): ~5-10ms
- Medium repos (1K-10K files): ~10-20ms
- Large repos (>10K files): ~20-50ms

**Overhead:** <0.5% of total dashboard generation time

**Optimization Tips:**
1. Enable caching in config (default: ON)
2. Reduce `max_workers` if CPU-constrained
3. Disable unused validation rules
4. Use `parallel_validation: true` (default)

---

## Integration Examples

### Programmatic Use

```python
from src.dashboard.reconciliation import ReconciliationEngine

# Initialize engine
engine = ReconciliationEngine()

# Prepare data (flat structure)
data = {
    'security_score': 75,
    'quality_score': 82,
    'maintainability_score': 70,
    'architecture_score': 85,
    'test_coverage': 65,
    'critical_vulnerabilities': 0,
    'high_vulnerabilities': 3,
    'code_smells': 45,
    'cyclomatic_complexity': 12,
    'security_hotspots': 8
}

# Run reconciliation
result = engine.reconcile(data, repository="my-project")

# Access results
print(f"Overall Score: {result.reconciled_data['overall_score']}")
print(f"Violations: {len(result.violations)}")
print(f"Anomalies: {len(result.anomalies)}")

# Serialize to JSON
import json
with open('reconciliation-report.json', 'w') as f:
    json.dump(result.to_dict(), f, indent=2)
```

### CI/CD Integration

```bash
#!/bin/bash
# run-reconciliation.sh

# Generate dashboard with reconciliation
python -m src.orchestrators.dashboard_collector --path . --output ci-build

# Check for critical violations
CRITICAL_COUNT=$(jq '.violations | map(select(.severity=="critical")) | length' \
  cortex-brain/dashboards/ci-build/reconciliation.json)

if [ "$CRITICAL_COUNT" -gt 0 ]; then
  echo "❌ FAILED: $CRITICAL_COUNT critical violations found"
  exit 1
fi

echo "✅ PASSED: No critical violations"
exit 0
```

---

## Support & Resources

**Documentation:**
- Full implementation plan: `cortex-brain/documents/planning/dashboard-reconciliation-engine-plan.md`
- Test suite: `tests/dashboard/reconciliation/`
- Source code: `src/dashboard/reconciliation/`

**Configuration:**
- Main config: `cortex-brain/reconciliation-config.yaml`
- SKULL rules: `cortex-brain/brain-protection-rules.yaml`

**Validation:**
```bash
# Run full test suite (73 tests)
pytest tests/dashboard/reconciliation/ -v

# Run specific test categories
pytest tests/dashboard/reconciliation/normalizers/ -v
pytest tests/dashboard/reconciliation/validators/ -v
pytest tests/dashboard/reconciliation/test_reconciliation_engine.py -v
```

---

**Version:** 1.0.0 | **Last Updated:** December 7, 2025 | **Status:** Production Ready
