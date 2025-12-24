# Documentation Alignment Requirements - Phase 11: Multi-Repo Architecture

**Version:** 1.0 | **Author:** Asif Hussain | **Created:** December 20, 2025

**Status:** 📋 PLANNED | **Target Phase:** Phase 11 (Post-Core)

---

## 🎯 Overview

This document tracks all documentation updates required for Phase 11 (Multi-Repo Architecture Enhancement) to ensure consistency across CORTEX documentation after workspace-aware operations are implemented.

---

## 📚 Documents Requiring Updates

### Category 1: Core Prompt Files (CRITICAL)

**1. `.github/prompts/CORTEX.prompt.md`**
- **Current State:** Documents GIT_ISOLATION_ENFORCEMENT, single-repo assumption
- **Required Changes:**
  - Remove GIT_ISOLATION_ENFORCEMENT warnings
  - Add workspace-aware operation examples
  - Update architecture diagrams (add workspace registry)
  - Add upgrade command documentation
  - Add workspace detection section
  - Update "Common Pitfalls" section (remove #4 about mixing CORTEX/user code)
- **Priority:** P0 (BLOCKING)
- **Estimated Effort:** 2 hours

**2. `.github/copilot-instructions.md`**
- **Current State:** Mirrors CORTEX.prompt.md but shorter
- **Required Changes:**
  - Remove GIT_ISOLATION warning
  - Add workspace detection brief
  - Add upgrade command
  - Update quick command reference
- **Priority:** P0 (BLOCKING)
- **Estimated Effort:** 1 hour

### Category 2: Architecture Documentation

**3. `cortex-brain/core/brain-protection-rules.yaml`**
- **Current State:** Contains GIT_ISOLATION_ENFORCEMENT rule
- **Required Changes:**
  - Archive GIT_ISOLATION_ENFORCEMENT with deprecation note
  - Add WORKSPACE_AWARE_OPERATIONS rule definition
  - Document workspace validation requirements
  - Add examples of valid/invalid workspace operations
- **Priority:** P0 (BLOCKING)
- **Estimated Effort:** 3 hours

**4. `README.md` (Root)**
- **Current State:** Single-repo setup instructions
- **Required Changes:**
  - Add multi-repo setup section
  - Update quick start for workspace initialization
  - Add "One CORTEX → N Repos" diagram
  - Document `cortex init workspace` command
  - Add upgrade instructions
- **Priority:** P1 (High)
- **Estimated Effort:** 2 hours

**5. `docs/architecture/brain-architecture.md`** (If exists)
- **Current State:** Documents single Brain structure
- **Required Changes:**
  - Update Tier 3 structure (segmentation by workspace)
  - Document workspace registry
  - Add cross-repo pattern learning flow
- **Priority:** P1 (High)
- **Estimated Effort:** 3 hours

### Category 3: User Guides (NEW)

**6. `cortex-brain/documents/implementation-guides/multi-repo-setup-guide.md`**
- **Current State:** Does not exist
- **Required Content:**
  - How to initialize workspace (`cortex init workspace`)
  - How workspace detection works (VSCode API → Copilot → CWD)
  - How to switch between workspaces
  - Troubleshooting workspace detection failures
  - FAQ: "Does CORTEX work without workspace initialization?" (Yes, falls back to default)
- **Priority:** P1 (High)
- **Estimated Effort:** 4 hours

**7. `cortex-brain/documents/architecture/workspace-architecture.md`**
- **Current State:** Does not exist
- **Required Content:**
  - Workspace registry design rationale
  - Brain Tier 3 segmentation architecture
  - Cross-repo pattern learning mechanism
  - Workspace operation validation flow
  - Upgrade mechanism architecture
- **Priority:** P2 (Medium)
- **Estimated Effort:** 5 hours

### Category 4: Orchestrator Documentation

**8. `src/orchestrators/base_orchestrator.py` (Docstring)**
- **Current State:** No workspace awareness mentioned
- **Required Changes:**
  - Add workspace detection to class docstring
  - Document `self.workspace_info` attribute
  - Document `self.target_directory` usage
  - Add example: "Write to active workspace, not CORTEX directory"
- **Priority:** P1 (High)
- **Estimated Effort:** 1 hour

**9. Orchestrator Module Guides (All 4 completed orchestrators)**
- **Files:**
  - `modules/execution-orchestrator-guide.md`
  - `modules/documentation-orchestrator-guide.md`
  - `modules/tdd-mastery-guide.md`
  - `modules/planning-orchestrator-guide.md`
- **Required Changes:**
  - Add workspace-aware operation examples
  - Document how orchestrator detects active workspace
  - Show output directory selection logic
  - Add troubleshooting: "Files created in wrong directory"
- **Priority:** P2 (Medium)
- **Estimated Effort:** 2 hours each (8 hours total)

### Category 5: Configuration Examples

**10. `cortex.config.template.json`**
- **Current State:** Single-repo paths
- **Required Changes:**
  - Add workspace registry path
  - Add example multi-repo configuration
  - Document workspace detection settings
  - Add upgrade settings (auto-check, channel)
- **Priority:** P1 (High)
- **Estimated Effort:** 1 hour

**11. `.cortex/config.json` (Template - NEW)**
- **Current State:** Does not exist
- **Required Content:**
  - Template for user repos
  - Points to central CORTEX installation
  - Contains workspace UUID
  - Optional: Workspace-specific overrides (test framework, conventions)
- **Priority:** P0 (BLOCKING)
- **Estimated Effort:** 1 hour

### Category 6: Migration Guides

**12. `cortex-brain/documents/migration/v3.9-to-v4.0-migration-guide.md`**
- **Current State:** May not exist yet
- **Required Content:**
  - How to migrate from single-repo to multi-repo setup
  - Brain Tier 3 migration steps
  - GIT_ISOLATION removal implications
  - Backward compatibility notes
  - Rollback procedure
- **Priority:** P1 (High)
- **Estimated Effort:** 4 hours

### Category 7: Testing Documentation

**13. Test Plan for Phase 11**
- **Current State:** Does not exist
- **Required Content:**
  - Test scenarios: 1 CORTEX + 3 user repos
  - Workspace detection accuracy tests (VSCode + Visual Studio)
  - Brain context isolation validation
  - Upgrade mechanism testing
  - Cross-workspace operation prevention tests
  - **NEW:** VSCode API integration tests
  - **NEW:** Visual Studio 2019+ API integration tests
  - **NEW:** Cross-IDE workspace switching tests
- **Priority:** P1 (High)
- **Estimated Effort:** 4 hours (updated from 3 hours)

### Category 8: Cross-IDE Support (NEW)

**14. `cortex-brain/documents/implementation-guides/vscode-workspace-detection.md`**
- **Current State:** Does not exist
- **Required Content:**
  - VSCode API integration guide
  - Environment variable configuration
  - Extension development notes (future)
  - Debugging workspace detection in VSCode
  - Known limitations and workarounds
- **Priority:** P1 (High)
- **Estimated Effort:** 2 hours

**15. `cortex-brain/documents/implementation-guides/visual-studio-workspace-detection.md`**
- **Current State:** Does not exist
- **Required Content:**
  - Visual Studio 2019+ DTE2 API integration
  - Solution file parsing
  - Environment variable configuration
  - Extension development notes (future)
  - Debugging workspace detection in VS
  - Known limitations and workarounds
- **Priority:** P1 (High)
- **Estimated Effort:** 2 hours

---

## 📊 Summary Metrics (Updated)

| Category | Documents | Total Effort |
|----------|-----------|--------------|
| Core Prompts | 2 | 3 hours |
| Architecture | 3 | 8 hours |
| User Guides | 2 | 9 hours |
| Orchestrators | 5 | 9 hours |
| Configuration | 2 | 2 hours |
| Migration | 1 | 4 hours |
| Testing | 1 | 4 hours |
| **Cross-IDE Support** | **2 docs** | **4 hours** |
| **TOTAL** | **18 documents** | **43 hours** |

**Breakdown:**
- P0 (BLOCKING): 4 documents, 7 hours
- P1 (High): 11 documents, 28 hours (includes cross-IDE)
- P2 (Medium): 3 documents, 8 hours

---

## 🎯 Implementation Strategy

### Phase 11 Package Integration

**Package 1-2 (Workspace Registry + Brain Segmentation):**
- Create #11 (workspace-architecture.md) - 5 hours
- Create #13 (test plan) - 3 hours

**Package 3 (Remove GIT_ISOLATION):**
- Update #3 (brain-protection-rules.yaml) - 3 hours
- Update #1 (CORTEX.prompt.md) - 2 hours
- Update #2 (copilot-instructions.md) - 1 hour

**Package 4 (Orchestrator Integration):**
- Update #8 (base_orchestrator docstring) - 1 hour
- Update #9 (4 orchestrator guides) - 8 hours

**Package 5 (Upgrade Mechanism):**
- Create #6 (multi-repo-setup-guide.md) - 4 hours
- Create #12 (migration guide) - 4 hours
- Update #4 (README.md) - 2 hours
- Create #11 (.cortex/config.json template) - 1 hour
- Update #10 (cortex.config.template.json) - 1 hour

### Parallel Documentation Work

**During Implementation (Developers):**
- Update docstrings in code (Package 1-4)
- Create .cortex/config.json template (Package 5)

**After Implementation (Documentation Sprint):**
- Create all new guides (#6, #7, #12, #13) - 16 hours
- Update all orchestrator guides (#9) - 8 hours
- Update README and templates (#4, #10) - 3 hours
- Final review and consistency check - 2 hours

---

## 🚨 Critical Dependencies

**Documentation BLOCKS Phase 11 Completion:**
- ❌ Cannot merge to main without updated CORTEX.prompt.md
- ❌ Cannot release v4.0 without multi-repo-setup-guide.md
- ❌ Cannot deprecate GIT_ISOLATION without migration guide

**Documentation REQUIRED for User Adoption:**
- Users cannot use multi-repo without setup guide
- Developers cannot troubleshoot without architecture docs
- Future maintainers cannot understand without migration guide

---

## ✅ Acceptance Criteria

**Documentation Quality:**
1. ✅ All P0 documents updated before code merge
2. ✅ All P1 documents complete before v4.0 GA
3. ✅ Code examples tested and validated
4. ✅ Diagrams accurately reflect implementation
5. ✅ No broken links in documentation
6. ✅ Consistent terminology across all docs

**User Experience:**
1. ✅ New user can setup multi-repo in <10 minutes
2. ✅ Existing user can migrate in <30 minutes
3. ✅ Troubleshooting guide resolves 80%+ common issues

---

## 📞 Owner & Timeline

**Documentation Owner:** Asif Hussain  
**Implementation Phase:** Phase 11 (Post-Core)  
**Estimated Completion:** End of Phase 11 implementation (1 week)  
**Review Cycle:** 2 days after implementation complete

---

## 🔄 Maintenance Plan

**Post-Phase 11:**
- All new orchestrators MUST document workspace-aware behavior
- Any Brain changes MUST update workspace architecture doc
- Quarterly review of multi-repo setup guide (user feedback)

**Version Control:**
- Documentation version synced with CORTEX version
- Breaking changes MUST update migration guide
- Deprecations MUST have 1-version notice period
