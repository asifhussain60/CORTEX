# STS Regeneration - Artifacts

**Plan:** STS-REGEN  
**Created:** December 28, 2025

---

## 🗂️ Supporting Artifacts

This directory contains code, data, and configuration files generated during plan execution.

### Artifact Categories

#### 1. Baseline Files
- `sts-baseline-2025-12-28.json` - Newly generated baseline
- `baseline-comparison.json` - Old vs new comparison
- `baseline-diff.patch` - Changes in git diff format

#### 2. Validation Results
- `validation-run-*.json` - Individual validation runs
- `capability-metrics-*.csv` - Metrics in tabular format
- `regression-analysis-*.json` - Regression detection results

#### 3. Test Outputs
- `pytest-report.html` - Template app test results
- `coverage-report.xml` - Code coverage data
- `test-failures.log` - Any test failures (for investigation)

#### 4. CI/CD Artifacts
- `sts-validation.yml` - GitHub Actions workflow
- `quick_sts_check.sh` - Quick validation script
- `workflow-test-output.log` - Local workflow test results

#### 5. Certification
- `cortex-4.0-sts-certification.pdf` - Final certification document
- `certification-data.json` - Structured certification data
- `capability-scores.csv` - Individual capability scores

---

## 📦 Artifact Naming Convention

```
{artifact-type}-{timestamp}.{extension}
```

Examples:
- `baseline-20251228-143022.json`
- `validation-run-20251228-150134.json`
- `pytest-report-20251228-152045.html`

---

## 🔒 Artifact Retention

**Temporary Artifacts:** (90 days)
- Individual validation runs
- Test outputs
- Workflow test logs

**Permanent Artifacts:** (version controlled)
- Final baseline
- Certification documents
- Updated scripts
- Workflow definitions

---

## 📊 Expected Artifacts by Phase

| Phase | Artifacts Generated |
|-------|---------------------|
| 1. Discovery | audit-report.md, gaps-identified.json |
| 2. Baseline Regen | baseline-2025-12-28.json, baseline-comparison.json |
| 3. Script Updates | Updated .py files, script-updates.md |
| 4. Template App | pytest-report.html, coverage-report.xml |
| 5. Documentation | Updated .md/.html files |
| 6. CI/CD Prep | .yml workflow, .sh script |
| 7. Final Validation | certification.pdf, validation-results.json |

---

**Note:** Large artifacts (>10MB) should be stored in `cortex-brain/artifacts/` with references here.
