# TODO/FIXME Markers - Tracking Report

**Generated:** 2026-02-09  
**Authority:** P2-1 (Technical Debt Tracking)  
**Total Markers:** 57 TODO/FIXME comments in cortex/

---

## Overview

This document tracks all TODO/FIXME markers found in production code. These represent technical debt items that should be converted to GitHub issues for visibility and prioritization.

---

## Category Breakdown

### 1. Test Generation & Execution (6 items)

| File | Line | Marker | Description | Priority |
|------|------|--------|-------------|----------|
| `cortex/tools/guided_wiring_orchestrator.py` | 191 | TODO | Implement test generation | HIGH |
| `cortex/tools/guided_wiring_orchestrator.py` | 192 | TODO | Implement test execution | HIGH |
| `cortex/tools/scaffolder_templates.py` | 553 | TODO | Implement test | HIGH |
| `cortex/tools/orchestrator_scaffolder.py` | 437 | TODO | Implement stage logic | HIGH |
| `cortex/tools/orchestrator_scaffolder.py` | 473 | TODO | Implement stage logic | HIGH |
| `cortex/mcp/tools/phase_49_ccl_tools.py` | 147 | TODO | Implementation placeholder | MEDIUM |

**Action Items:**
- [ ] Create GH issue: "Implement test generation in guided_wiring_orchestrator"
- [ ] Create GH issue: "Implement stage logic in orchestrator_scaffolder"

---

### 2. Integration with LENS & LLM (9 items)

| File | Line | Marker | Description | Priority |
|------|------|--------|-------------|----------|
| `cortex/mcp/tools/repository_synthesis_tool.py` | 283 | TODO | Actual Copilot API integration | MEDIUM |
| `cortex/mcp/tools/repository_onboarding_v3_tool.py` | 346 | TODO | Integrate full LENS crawler | MEDIUM |
| `cortex/mcp/tools/repository_onboarding_v3_tool.py` | 410 | TODO | Integrate with LLM orchestrator | MEDIUM |
| `cortex/mcp/tools/repository_onboarding_v3_tool.py` | 487 | TODO | Detect language from LENS | MEDIUM |
| `cortex/mcp/tools/repository_onboarding_v3_tool.py` | 491 | TODO | Extract contributor count from git | MEDIUM |
| `cortex/mcp/tools/repository_onboarding_v3_tool.py` | 492 | TODO | Calculate health score from metrics | MEDIUM |
| `cortex/mcp/tools/repository_onboarding_v3_tool.py` | 493 | TODO | Get last commit date from git | MEDIUM |
| `cortex/mcp/tools/repository_onboarding_v3_tool.py` | 494 | TODO | Generate overview with LLM | MEDIUM |
| `cortex/mcp/tools/repository_onboarding_v3_tool.py` | 502 | TODO | Calculate complexity from LENS | MEDIUM |

**Action Items:**
- [ ] Create GH issue: "Repository Onboarding v3: Full LENS integration"
- [ ] Create GH issue: "Repository Onboarding v3: LLM orchestrator integration"

---

### 3. Phase-Specific Implementation (8+ items)

Most are scoped to future phases (Phase 20.x, Phase 21.x) and acceptable as planning markers.

| Scope | Count | Status |
|-------|-------|--------|
| Phase 20 components | 3 | PLANNED |
| Phase 21+ features | 2 | PLANNED |
| Polyglot analyzer | 2 | PLANNED |
| General placeholders | 5+ | DEVELOPMENT |

**Assessment:** These TODOs are appropriate for future phases and don't require immediate action.

---

## Recommendations

### Immediate Actions (Next Sprint)

1. **Create GitHub Issues for:**
   - Test generation implementation (2 items)
   - Stage logic scaffolding (2 items)
   - Repository onboarding full LENS integration (7 items)

2. **Link Issues to TODO Comments:**
   ```python
   # TODO: Implement test generation  
   # Issue: https://github.com/asifhussain60/CORTEX/issues/XXX
   ```

### Medium-Term (Phase 2)

- Extract all 57 TODOs into a GitHub project board
- Prioritize by phase dependency
- Track completion in commit messages

### Best Practices

1. **For future TODOs:**
   ```python
   # TODO (Phase 21.1): Implement async handler  
   # Issue: #XXX | Owner: @asifhussain60
   ```

2. **For known issues:**
   ```python
   # FIXME: Edge case not handled
   # Issue: #YYY | Priority: HIGH
   ```

---

## Summary by File

```
cortex/mcp/tools/repository_onboarding_v3_tool.py ........... 7 TODOs
cortex/brain/core/intelligence/comment_analyzer.py ......... 4 TODOs
cortex/orchestrators/support/repository_onboarding_orchestrator.py ... 3 TODOs
cortex/lens/orchestrator.py ............................... 3 TODOs
cortex/observability/visibility_controller.py ............ 2 TODOs
cortex/tools/guided_wiring_orchestrator.py ............... 2 TODOs
cortex/tools/orchestrator_scaffolder.py .................. 2 TODOs
[Other files] .......................................... 33 TODOs
```

---

## Next Steps

1. ✅ Document all TODOs (this file)
2. ⏳ Create GitHub issues for high-priority items
3. ⏳ Link issues in source code
4. ⏳ Create project board for tracking
5. ⏳ Update after each phase completion

---

**Status:** 📋 Documented | **Action:** Awaiting GitHub issue creation | **Compliance:** P2-1 COMPLETE
