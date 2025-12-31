# 📝 Final Report Template

**Generated ONLY after Phase 11 completion**

---

```markdown
# 🩺 CORTEX Maintenance Report

**Date:** {date}
**Duration:** {total_duration}
**Status:** ✅ ALL PHASES COMPLETE

---

## Visual Progress Tracker

### 🚑 SYSTEM MAINTENANCE COMPLETE

**Overall Progress:** `████████████████████` **100%** ✅ HEALTHY

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 0 - Cleanup | `██████████` | 100% ✅ |
| Phase 1 - Discovery | `██████████` | 100% ✅ |
| Phase 2 - Template Validation | `██████████` | 100% ✅ |
| Phase 3 - Preservation | `██████████` | 100% ✅ |
| Phase 4 - Scaffolding | `██████████` | 100% ✅ |
| Phase 5 - Wiring | `██████████` | 100% ✅ |
| Phase 6 - Testing | `██████████` | 100% ✅ |
| Phase 7 - Knowledge | `██████████` | 100% ✅ |
| Phase 8 - Organization | `██████████` | 100% ✅ |
| Phase 9 - Routing | `██████████` | 100% ✅ |
| Phase 10 - Prompts | `██████████` | 100% ✅ |
| Phase 11 - Verification | `██████████` | 100% ✅ |

📊 **Issues Found:** {count} | **Auto-Fixed:** {fixed} | **Health:** {score}%

---

## Phase Summaries

### Phase 0: Cleanup Orchestrator
- **Duration:** {duration}
- **Actions:** {actions_taken}
- **Space Freed:** {space_mb} MB
- **Backups Deleted:** {backup_count}

### Phase 1: Discovery
- **Duration:** {duration}
- **Unwired Components:** {unwired_count}
- **Duplicate Reports:** {duplicate_count}
- **Bloated Prompts:** {bloat_count}
- **Action Items:** {action_count}

### Phase 2: Template Validation
- **Duration:** {duration}
- **Templates Validated:** {template_count}
- **Broken References Fixed:** {fixed_count}
- **Duplicates Removed:** {duplicate_count}

### Phase 3: Preservation
- **Duration:** {duration}
- **Protected Paths Verified:** {verified_count}
- **Critical Data Intact:** ✅

### Phase 4: Scaffolding
- **Duration:** {duration}
- **Generators Verified:** {generator_count}
- **Missing Generators Created:** {created_count}

### Phase 5: Wiring
- **Duration:** {duration}
- **Components Wired:** {wired_count}
- **Wiring Coverage:** 100% ✅

### Phase 6: Testing
- **Duration:** {duration}
- **Tests Run:** {total_tests}
- **Tests Passing:** {passing_tests}
- **Obsolete Tests Deleted:** {deleted_tests}
- **Pass Rate:** 100% ✅

### Phase 7: Knowledge
- **Duration:** {duration}
- **Knowledge Files Synced:** {synced_count}
- **Broken References Fixed:** {fixed_count}
- **Plans Validated:** {plan_count}

### Phase 8: Organization
- **Duration:** {duration}
- **Reports Organized:** {organized_count}
- **Old Reports Archived:** {archived_count}

### Phase 9: Routing
- **Duration:** {duration}
- **Routes Validated:** {route_count}
- **Broken Paths Fixed:** {fixed_count}

### Phase 10: Prompts
- **Duration:** {duration}
- **Prompts Optimized:** {optimized_count}
- **Avg Size Reduction:** {reduction_pct}%

### Phase 11: Verification
- **Duration:** {duration}
- **Health Score:** {score}% ✅
- **Critical Issues:** 0
- **Warnings:** {warning_count}

---

## Changes Made

{git_diff_summary}

---

## Next Maintenance

**Recommended:** {next_date} (30 days from now)

**Frequency:** Run maintenance every 30 days or after major system changes.

---

**Report Generated:** {timestamp}
**Report Location:** `cortex-brain/health-reports/maintenance-report-{date}.md`
```

---

## Report Generation Rules

**Timing:**
- Generate ONLY after Phase 11 completes
- Do NOT generate partial reports mid-execution

**Location:**
- Save to: `cortex-brain/health-reports/maintenance-report-{yyyyMMdd}.md`
- Keep last 10 reports, archive older ones

**Contents:**
- Visual progress tracker (100% complete)
- Phase-by-phase summaries with metrics
- Git diff summary of changes made
- Next maintenance recommendation

**Commit:**
- Auto-commit report with message: `chore: maintenance report {date}`
