# Infrastructure Discovery: Ready-But-Inactive Components

**Author:** Asif Hussain  
**Date:** December 20, 2025  
**Status:** 🔍 DISCOVERY REPORT

---

## 🎯 Executive Summary

**Issue:** Production-ready infrastructure exists but is not wired into user-accessible operations.

**Root Cause:** 
1. Admin Governor focuses on plan↔implementation alignment, not feature activation
2. No systematic check for "infrastructure complete but not active"
3. Gap between "tests passing" and "user can invoke"

**Impact:** Wasted development effort building features users can't access.

---

## 🔍 Discovery Methodology

**Search Criteria:**
1. Complete Python modules with tests passing
2. NOT in `cortex-operations.yaml` as user operation
3. OR has `execution_method: internal` (no CLI wrapper/Copilot Chat)
4. OR no natural language triggers
5. OR orchestrator initialized but not routed

---

## 📦 CONFIRMED: Vision API Infrastructure

### Status: ✅ 100% Complete, ❌ 0% Activated

**Components:**
- `VisionAPI` (478 LOC)
- `VisionOrchestrator` (435 LOC)  
- `VisionContextMiddleware` (240 LOC)
- `ImageContextMiddleware`
- `VisionAPIModule` (253 LOC)

**Tests:** ✅ All passing
**Docs:** ✅ Complete
**Wiring:** ❌ Not in operations, no CLI wrapper, no routing

**Activation Plan:** Phase 6 Week 9 Days 3-5 (45 min effort)

---

## 🔍 POTENTIAL: Other Ready-But-Inactive Infrastructure

### Tier 1: High Confidence (Code + Tests Exist)

#### 1. **Image Detector** (`src/tier1/image_detector.py`)
- **Purpose:** Detect images in attachments
- **Status:** Production-ready
- **Used By:** VisionOrchestrator
- **Wiring:** Internal only (no direct user access)
- **Recommendation:** Keep internal (support module for Vision API)

#### 2. **Screenshot Analyzer** (`src/cortex_agents/screenshot_analyzer.py`)
- **Purpose:** Analyze screenshots for UI elements
- **Status:** Production-ready
- **Used By:** Vision system
- **Wiring:** Internal only
- **Recommendation:** Keep internal (part of Vision API)

#### 3. **Enhanced Feedback Module** (`enhanced_feedback_module`)
- **Purpose:** 8-category performance metrics
- **Status:** Operation exists (`feedback_report`)
- **Wiring:** ✅ Active in cortex-operations.yaml
- **Recommendation:** No action needed

#### 4. **Admin Feedback Review Module** (`admin_feedback_review_module`)
- **Purpose:** Aggregate feedback from multiple repos
- **Status:** Operation exists (`admin_feedback_review`)
- **Wiring:** ✅ Active (admin-only)
- **Recommendation:** No action needed

### Tier 2: Moderate Confidence (Infrastructure Modules)

These are **internal infrastructure** (correctly NOT user-facing):

1. **Conversation Memory** (`src/tier1/conversation_memory.py`)
   - **Status:** Core brain infrastructure
   - **Recommendation:** Keep internal

2. **Working Memory** (`src/tier1/working_memory.py`)
   - **Status:** Core brain infrastructure
   - **Recommendation:** Keep internal

3. **Temporal Correlator** (`src/tier1/temporal_correlator.py`)
   - **Status:** Brain feature
   - **Recommendation:** Keep internal

4. **Narrative Intelligence** (`src/tier1/narrative_intelligence.py`)
   - **Status:** Brain feature
   - **Recommendation:** Keep internal

5. **User Profile Manager** (`src/tier1/user_profile_manager.py`)
   - **Status:** Brain feature
   - **Recommendation:** Keep internal

6. **Work State Manager** (`src/tier1/work_state_manager.py`)
   - **Status:** Brain feature
   - **Recommendation:** Keep internal

7. **Response Context Integration** (`src/tier1/response_context_integration.py`)
   - **Status:** Template system
   - **Recommendation:** Keep internal

### Tier 3: Operations Registry Analysis

**From `cortex-operations.yaml`:**

#### Ready Operations (execution_method present):
```yaml
# 7 CLI wrappers (execution_method: cli_wrapper)
- system_integrity (✅ cli_script: system_integrity_wrapper.py)
- deploy_cortex_production (✅ cli_script: deploy_wrapper.py)
- regenerate_prompts (✅ cli_script: regenerate_prompts_wrapper.py)
- align (✅ cli_script: align_wrapper.py)
- cleanup (✅ cli_script: cleanup_wrapper.py)
- healthcheck (✅ cli_script: healthcheck_wrapper.py)
- optimize (✅ cli_script: optimize_wrapper.py)

# Many copilot_chat operations (execution_method: copilot_chat)
- sanitize
- ado
- tdd
- planning
- user_onboarding
- application_onboarding
- etc.
```

#### Infrastructure Modules (execution_method: internal) - CORRECTLY Internal:
```yaml
# 302 operations total
# Many have execution_method: internal (infrastructure only)
# Examples:
- vision_api (module only, no user operation)
- platform_detection
- git_sync
- virtual_environment
- python_dependencies
- etc.
```

---

## 🚨 CRITICAL FINDING: vision_api Module

**Current State:**
```yaml
modules:
  vision_api:
    name: Vision API
    description: Vision API Setup Module
    phase: FEATURES
    execution_method: internal
    priority: 10
    class: VisionAPIModule
    file: vision_api_module.py
    # ...
```

**Issue:** Module exists but no user-facing operation!

**Missing:**
```yaml
operations:
  analyze_image:  # ❌ DOES NOT EXIST
    name: Analyze Image
    execution_method: copilot_chat
    natural_language:
      - analyze this image
      - what's in this screenshot
    modules:
      - vision_orchestrator
```

---

## 🔬 Search Pattern Results

### Pattern 1: "TODO wire" or "FIXME integrate"
**Result:** No matches in src/**/*.py

### Pattern 2: "infrastructure ready" or "production ready"
**Result:** No explicit markers in code

### Pattern 3: Operations with `execution_method: internal`
**Result:** 200+ operations (mostly EPM modules, correctly internal)

### Pattern 4: Classes with tests but no CLI wrapper
**Result:** Vision API system (confirmed)

---

## ✅ Recommendations

### Immediate Action (Phase 6 Week 9 Days 3-5)

1. **Activate Vision API**
   - Add `analyze_image` operation
   - Wire IntentRouter
   - 45 minutes effort
   - High user value

### Future Prevention (Phase 7: Infrastructure Activation Review)

Add new phase to systematically discover and activate ready infrastructure:

1. **Scan for:**
   - Complete modules with passing tests
   - Missing operations in cortex-operations.yaml
   - Orchestrators initialized but not routed
   - CLI wrappers missing for ready features

2. **Validation Checklist:**
   - ✅ Tests passing
   - ✅ Documentation complete
   - ✅ Operation in registry
   - ✅ Natural language triggers
   - ✅ Routing logic active
   - ✅ User can invoke

3. **Quarterly Review:**
   - Run infrastructure scan
   - Identify gaps
   - Prioritize activation
   - Update documentation

---

## 📊 Summary Statistics

| Category | Count | Status |
|----------|-------|--------|
| **Total Operations** | 302 | Mixed |
| **CLI Wrappers** | 7 | ✅ Active |
| **Copilot Chat Operations** | 50+ | ✅ Active |
| **Internal Modules** | 200+ | ✅ Correctly Internal |
| **Ready But Inactive** | 1 | ❌ Vision API |
| **Investigation Needed** | 0 | None found |

---

## 🎓 Lessons Learned

### Why Admin Governor Didn't Catch This

**Admin Governor Focus:**
```yaml
1. Plan ↔ Implementation Sanity Enforcement
   - Compare plan vs repo
   - Missing implementations
   - Extra/unplanned artifacts

2. Wiring & Activation Verification
   - Registered in cortex-operations.yaml ✅ (vision_api module IS registered)
   - Execution method classification ✅ (execution_method: internal)
   - CLI wrappers exist ✅ (not required for internal modules)
   - Imports discoverable ✅ (all imports work)
   - Orchestrator manifests exist ✅ (docs exist)
```

**Gap:** Admin Governor validates wiring for **infrastructure modules**, not **user-facing operations**.

Vision API is correctly wired as an **internal module**. The missing piece is the **user-facing operation** to invoke it.

### Solution: Extend Admin Governor

Add new responsibility:

```yaml
2.5 User Operation Completeness Verification
- For each orchestrator with production-ready infrastructure:
  - Check if user-facing operation exists
  - Verify natural language triggers
  - Validate routing logic active
  - Test end-to-end invocation path
- Report ready-but-inaccessible features
- Generate activation checklists
```

---

## 🔗 Related Documents

- **Vision API Activation Guide:** `cortex-brain/documents/implementation-guides/vision-api-activation-guide.md`
- **Admin Governor Prompt:** `.github/prompts/CORTEX_ADMIN_GOVERNOR.prompt.md`
- **Operations Registry:** `cortex-operations.yaml`
- **Phase 6 Plan:** `cortex-brain/documents/planning/orchestrators/cortex-4.0-orchestrator-consolidation-plan.md`

---

## ✅ Action Items

1. ✅ **Create Vision API Activation Guide** (This document + vision-api-activation-guide.md)
2. ⏳ **Update Phase 6 Plan** (Add Week 9 Days 3-5: Vision API Activation)
3. ⏳ **Add Phase 7: Infrastructure Activation Review**
4. ⏳ **Extend Admin Governor** (Add user operation completeness checks)
5. ⏳ **Execute Vision API Activation** (Week 9 Days 3-5)
