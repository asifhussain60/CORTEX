# Composable Block Analysis Report

**Generated:** 2025-12-31
**Total Orchestrators:** 8
**Total Unique Blocks:** 32

## 📊 Shared Blocks (Cross-Orchestrator)

Blocks used by multiple orchestrators:

| Block | Orchestrators | Usage Count |
|-------|--------------|-------------|
| `next_action` | 8 (ado-planning, code-sanitization, cortex-lens-v3, debug-orchestrator, planning-system-4.0, refinement-orchestrator, tdd-orchestrator-v4, technical-documentation-orchestrator) | 17 |
| `cortex_header` | 7 (code-sanitization, cortex-lens-v3, debug-orchestrator, planning-system-4.0, refinement-orchestrator, tdd-orchestrator-v4, technical-documentation-orchestrator) | 15 |
| `changes` | 6 (code-sanitization, debug-orchestrator, planning-system-4.0, refinement-orchestrator, tdd-orchestrator-v4, technical-documentation-orchestrator) | 9 |
| `achievements` | 4 (ado-planning, code-sanitization, planning-system-4.0, refinement-orchestrator) | 4 |
| `understanding` | 3 (debug-orchestrator, planning-system-4.0, refinement-orchestrator) | 3 |
| `approach` | 3 (debug-orchestrator, planning-system-4.0, refinement-orchestrator) | 3 |
| `test_results_summary` | 3 (debug-orchestrator, refinement-orchestrator, tdd-orchestrator-v4) | 8 |
| `cautions` | 3 (code-sanitization, cortex-lens-v3, technical-documentation-orchestrator) | 3 |
| `plan_file_link` | 2 (ado-planning, planning-system-4.0) | 5 |
| `cortex_header_shield` | 2 (ado-planning, planning-system-4.0) | 4 |
| `progress_tracker_standard` | 2 (ado-planning, planning-system-4.0) | 4 |
| `validation_status_dor_dod` | 2 (ado-planning, planning-system-4.0) | 3 |

## 🎯 Orchestrator-Specific Blocks

Blocks used by only one orchestrator:

### ado-planning
- `ado_auth_status`
- `ado_links`
- `work_item_summary`

### code-sanitization
- `sanitization_findings`

### cortex-lens-v3
- `analytics_summary`
- `health_metrics`
- `system_recommendations`

### debug-orchestrator
- `bug_hypothesis`
- `fix_verification`
- `root_cause_analysis`

### planning-system-4.0
- `deliverables_matrix`
- `plan_structure_tree`
- `plan_summary_table`
- `threat_analysis`

### refinement-orchestrator
- `code_quality_delta`
- `improvement_areas`

### tdd-orchestrator-v4
- `coverage_metrics`
- `tdd_cycle_status`

### technical-documentation-orchestrator
- `coverage_report`
- `doc_summary`

## 📈 Orchestrator Coverage

| Orchestrator | Operations | Unique Blocks | Mandatory | Conditional | Orchestrator-Specific |
|--------------|-----------|---------------|-----------|-------------|----------------------|
| ado-planning | 2 | 9 | ✅ | ✅ | ✅ |
| code-sanitization | 2 | 6 | ✅ | ✅ | ✅ |
| cortex-lens-v3 | 2 | 6 | ✅ | ✅ | ✅ |
| debug-orchestrator | 3 | 9 | ✅ | ✅ | ✅ |
| planning-system-4.0 | 3 | 14 | ✅ | ✅ | ✅ |
| refinement-orchestrator | 2 | 9 | ✅ | ✅ | ✅ |
| tdd-orchestrator-v4 | 3 | 6 | ✅ | ✅ | ✅ |
| technical-documentation-orchestrator | 2 | 6 | ✅ | ✅ | ✅ |

## 💡 Optimization Recommendations

1. **Most Reused Block:** `next_action` (used by 8 orchestrators)
   - Consider this as core template component

2. **Leanest Orchestrators:** tdd-orchestrator-v4, cortex-lens-v3, code-sanitization, technical-documentation-orchestrator (6 unique blocks)
   - Good templates for simple operations

3. **Single-Use Blocks:** 2 blocks used only once
   - Consider if these need to be standalone blocks
