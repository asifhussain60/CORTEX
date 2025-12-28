---
mode: agent
description: "CORTEX System Maintenance - Health checks, intent router validation, and prompt regeneration"
---

# 🩺 CORTEX System Maintenance

**Purpose:** Keep CORTEX 4.0 at peak performance through health checks, intent router validation, and automated prompt regeneration.

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 6-Phase Maintenance Pipeline

| Phase | Action | Success Criteria |
|-------|--------|------------------|
| **1** | Quick Health Check | Health score ≥90 |
| **2** | Full Diagnostic | All components wired |
| **3** | Wiring Integrity | 100% wiring coverage |
| **4** | Review Reports | Reports generated |
| **5** | Intent Router Validation | All manifests synced |
| **6** | Regenerate Lean Prompts | <200 lines each |

---

## Phase 1-4: Health & Diagnostics

```bash
# Phase 1: Quick check
python3 scripts/cortex_system_doctor.py --quick

# Phase 2: Full diagnostic
python3 scripts/cortex_system_doctor.py --phase diagnose --phase scan

# Phase 3: Wiring integrity
python3 scripts/check_wiring_integrity.py

# Phase 4: Reports in cortex-brain/health-reports/
```

---

## Phase 5: Intent Router Validation ⚠️ CRITICAL

### 5a. Manifest Path Verification

**Source of Truth:** `cortex-brain/manifests/orchestrators/`

Scan all orchestrator manifests and verify CORTEX.prompt.md references them correctly:

| Manifest File | Orchestrator | Must Have Triggers |
|---------------|--------------|-------------------|
| `planning-system-4.0-manifest.yaml` | Planning System | `plan [x]`, `create a plan`, `make a plan` |
| `tdd-orchestrator-v4-manifest.yaml` | TDD Mastery | `start tdd`, `run tests`, `tdd [x]` |
| `ado-planning-manifest.yaml` | ADO Operations | `plan ado`, `ado story`, `ado feature` |
| `code-sanitization-manifest.yaml` | Sanitization | `sanitize`, `make generic`, `anonymize` |
| `refinement-orchestrator-manifest.yaml` | Refinement | `refine`, `improve cortex` |

### 5b. Output Structure Validation

Planning System MUST specify folder structure from manifest:
```yaml
output_location: cortex-brain/documents/planning/active/{PLAN_NAME}/
required_subfolders: [context/, reports/, artifacts/, tracking/]
required_files: [00-master-plan.md]
```

### 5c. Validation Commands

```bash
# Check for broken/old paths
grep -r "orchestrator-manifests" .github/prompts/  # Should return NOTHING

# Verify all manifest references exist
for f in $(grep -oh "cortex-brain/manifests/orchestrators/[^\"']*" .github/prompts/*.md); do
  [ -f "$f" ] || echo "MISSING: $f"
done
```

---

## Phase 6: Regenerate Lean Prompts

**Goal:** Create minimal, clean prompt files with proper intent routing.

### 6a. CORTEX.prompt.md Structure (Target: <200 lines)

```markdown
# 🎯 CORTEX Universal Entry Point
Version | Author | Status

## Intent Router
[Table: Command → Orchestrator → Manifest Path → Output Spec]

## Response Format (v4.0)
[4 tiers: INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE]

## Brain Protection (SKULL)
[4 rules: TDD, Discovery, Cleanup, Git Isolation]

## Quick Reference
[Command table with descriptions]
```

### 6b. copilot-instructions.md Structure (Target: <150 lines)

```markdown
# GitHub Copilot Instructions for CORTEX
## Entry Point
→ Load CORTEX.prompt.md

## Response Format
→ Defer to CORTEX.prompt.md

## Key Workflows
[Brief list with manifest references]

## Document Organization
[Category list]
```

### 6c. Wiring Rules

1. **Single Source of Truth:** `CORTEX.prompt.md` is the intent router
2. **copilot-instructions.md:** Points TO CORTEX.prompt.md, doesn't duplicate
3. **Manifests:** All orchestrators reference their manifest file
4. **Output Specs:** Planning operations include folder structure requirement

---

## ✅ Success Criteria

| Check | Pass Condition |
|-------|----------------|
| Health Score | ≥ 90/100 |
| Wiring Coverage | 100% |
| Manifest Paths | All resolve to existing files |
| Intent Triggers | Each orchestrator has ≥3 triggers |
| CORTEX.prompt.md | <200 lines, all manifests wired |
| copilot-instructions.md | <150 lines, defers to CORTEX.prompt.md |
| Output Structures | Planning System has folder spec |

---

## 📋 Validation Checklist

Run during every maintenance cycle:

- [ ] Health score ≥90
- [ ] All manifest paths resolve to existing files
- [ ] No references to deprecated `orchestrator-manifests/` path
- [ ] Each orchestrator has ≥3 trigger phrases
- [ ] Planning System has output folder structure specified
- [ ] CORTEX.prompt.md is <200 lines
- [ ] copilot-instructions.md is <150 lines
- [ ] copilot-instructions.md defers to CORTEX.prompt.md (no duplication)
- [ ] Reports folder cleaned (see Phase 7)

---

## Phase 7: Report Management 🗑️

**Goal:** Prevent report bloat - user won't read them, CORTEX doesn't need most of them.

### 7a. Report Policy

| Report Type | Policy | Reason |
|-------------|--------|--------|
| **Timestamped operational logs** (cleanup-*, brain-tuning-*, architectural-review-*) | DELETE | Ephemeral, no reference value |
| **Benchmark/test results** (benchmark_*, DOC_QUALITY_REPORT_*) | DELETE | Temporary test data |
| **Task completion summaries** (story-*, planning-*, feature-*) | DELETE | User won't read, redundant |
| **Duplicate analyses** (unwired-components-TIMESTAMP-*) | DELETE | Keep only latest if needed |
| **Major architecture decisions** (SYSTEM-INTEGRITY-*, MOCK-STUB-AUDIT) | KEEP | Reference for future decisions |
| **Migration/refactor summaries** (ORCHESTRATOR-*, CORTEX-CLEANUP-*) | KEEP | Historical context |

### 7b. Cleanup Commands

```bash
cd cortex-brain/documents/reports/

# Delete timestamped operational JSONs
rm -f cleanup-*.json architectural-review-*.json brain-tuning-*.json

# Delete benchmark/test JSONs
rm -f benchmark_*.json DOC_QUALITY_REPORT_*.json summary_*.json

# Delete task completion summaries
rm -f story-*.md planning-*.md feature-*.md *-complete.md

# Delete duplicate analyses (keep only one if needed)
rm -f unwired-components-2025*.json unwired-components-2025*.md

# Delete operational JSONs
rm -f git-sync-*.json validation_report.json system-alignment-report-*.json

# Verify cleanup
echo "Remaining reports: $(ls -1 | wc -l)"
du -sh .
```

### 7c. Prevention Rules

**STOP creating reports for:**
- ❌ Task completion summaries
- ❌ Incremental progress updates  
- ❌ Operational logs with timestamps
- ❌ Benchmark results (use metrics database instead)

**ONLY create reports for:**
- ✅ Major architectural decisions
- ✅ System-wide migrations/refactors
- ✅ Compliance audits (when required)
- ✅ Reference documentation (non-temporal)

### 7d. Alternative: Use Metrics Database

For tracking operational data, use `cortex-brain/analytics/metrics.db` instead of JSON reports.

---