# CORTEX Setup Enhanced Flow Guide

**Purpose:** Documentation for the Enhanced Setup Flow with post-setup onboarding prompt  
**Version:** 1.0  
**Status:** ✅ IMPLEMENTED  
**Author:** Asif Hussain

---

## 🎯 Overview

The Enhanced Flow separates application onboarding from the initial setup workflow, giving users more control over when to run the potentially time-consuming analysis.

### Why Enhanced Flow?

**Previous Flow (Integrated):**
- User consented to ALL steps upfront (including onboarding)
- Onboarding ran automatically during Phase 4
- No flexibility to defer analysis
- ~10 minute setup time (fixed)

**Enhanced Flow (Separate):**
- User consents to setup steps only (dependencies, gitignore, EPM)
- Onboarding offered as optional post-setup question
- Users can defer with `onboard application` command
- ~5-7 minute setup + optional 3-5 minute onboarding

---

## 🔄 Workflow Comparison

### Previous Flow (v3.1)
```
Phase 1: Detection
   ↓
Phase 2: User Consent (all steps including onboarding)
   ↓
Phase 3: Dependencies
   ↓
Phase 4: Onboarding (automatic if approved)
   ↓
Phase 5: GitIgnore
   ↓
Phase 6: Copilot Instructions
   ↓
Phase 7: Completion Report
   ↓
Done
```

### Enhanced Flow (v3.2)
```
Phase 1: Detection
   ↓
Phase 2: User Consent (setup steps only)
   ↓
Phase 3: Dependencies
   ↓
Phase 3.5: Policy Validation
   ↓
Phase 3.6: Realignment
   ↓
Phase 4: Onboarding - DEFERRED
   ↓
Phase 5: GitIgnore
   ↓
Phase 6: Copilot Instructions
   ↓
Phase 7: Completion Report
   ↓
Phase 8: Post-Setup Onboarding Prompt ⭐ NEW
   ├─ User says 'y' → Run OnboardingOrchestrator
   └─ User says 'n' → Skip (can run later)
   ↓
Done
```

---

## 💬 User Experience

### Phase 8 Prompt

```
================================================================================
✅ CORTEX Setup Complete! (7.2s)
================================================================================

================================================================================
📊 Application Onboarding (Optional)
================================================================================

Onboarding analyzes your application and provides:
  • Code quality score and improvement recommendations
  • Security vulnerability scan (OWASP)
  • Performance metrics and bottleneck detection
  • Interactive dashboard with visualizations

Estimated time: 3-5 minutes

Note: You can run onboarding later with 'onboard application' command

Would you like to onboard your application now? (y/n): _
```

### User Says 'y' (Onboard Now)

```
Phase 8: Onboarding application...
================================================================================

📊 Gathering project metadata...
✅ Project: MyApp
✅ Type: Python application
✅ Files: 142 Python files, 87 test files

🔍 Running code quality analysis...
✅ Issues found: 8 (2 critical, 3 warning, 3 info)
✅ Quality score: 82.3%

🔒 Running security scan...
✅ Vulnerabilities: 0 critical, 1 medium, 3 low

⚡ Collecting performance metrics...
✅ Average complexity: 5.8
✅ Largest file: 847 lines
✅ Test coverage: 72%

📈 Generating dashboard data...
✅ Dashboard: cortex-brain/dashboard/index.html

✅ Onboarding complete!
   Quality Score: 82.3%
   Security Issues: 4 (0 critical)
   Dashboard: cortex-brain/dashboard/index.html
```

### User Says 'n' (Defer Onboarding)

```
⏸️  Onboarding skipped
   Run later with: onboard application

================================================================================
🎉 Setup Complete - CORTEX is ready!
================================================================================
```

---

## 🔧 Technical Implementation

### Changes Made

**1. Phase 2 Consent Update**
```python
# Phase 2: User Consent (excluding onboarding - will ask separately)
consent = consent_mgr.request_onboarding_consent(detected)
phase_results['consent'] = {
    'action': consent.action.value,
    'approved_steps': consent.approved_steps,
    'skipped_steps': consent.skipped_steps,
    'onboarding_deferred': True  # ⭐ NEW: Onboarding will be asked separately
}
```

**2. Phase 4 Deferred**
```python
# Phase 4: Onboard Application - DEFERRED
logger.info("\nPhase 4: Onboarding deferred to post-setup")
phase_results['onboarding'] = {
    'deferred': True,
    'message': 'Will be offered after setup completes'
}
```

**3. Phase 8 Added (Post-Setup Prompt)**
```python
# Phase 8: Post-Setup Onboarding Prompt (Enhanced Flow)
logger.info("📊 Application Onboarding (Optional)")

if self.interactive:
    onboard_now = input("Would you like to onboard your application now? (y/n): ")
    
    if onboard_now == 'y':
        # Run OnboardingOrchestrator
        onboarding = OnboardingOrchestrator(self.cortex_root)
        onboard_result = onboarding.onboard_application(...)
        # Store results in phase_results['post_setup_onboarding']
    else:
        # User deferred, can run manually later
        phase_results['post_setup_onboarding'] = {'skipped': True, 'user_choice': 'deferred'}
```

---

## 📊 Benefits

**User Control:**
- ✅ Faster initial setup (~5-7 min instead of ~10 min)
- ✅ Can defer analysis to later when convenient
- ✅ Clear separation of setup vs analysis phases

**Flexibility:**
- ✅ Run onboarding immediately after setup
- ✅ Defer with `onboard application` command
- ✅ Skip entirely if not needed

**Transparency:**
- ✅ Clear explanation of what onboarding does
- ✅ Time estimate provided upfront
- ✅ User knows they can run it later

**Developer Experience:**
- ✅ Non-interactive mode automatically skips Phase 8
- ✅ CI/CD pipelines don't get blocked by prompts
- ✅ Manual onboarding command always available

---

## 🎯 User Scenarios

### Scenario 1: Developer Wants Full Setup

**Flow:**
1. Runs `setup cortex`
2. Approves all setup steps in Phase 2
3. Waits 7 minutes for setup to complete
4. Phase 8 prompt appears
5. Says 'y' to onboard immediately
6. Waits 3-5 minutes for onboarding
7. Reviews dashboard and quality report
8. **Total time:** ~12 minutes

**Result:** Same as previous integrated flow, but with clearer separation

---

### Scenario 2: Developer in a Hurry

**Flow:**
1. Runs `setup cortex`
2. Approves setup steps in Phase 2
3. Waits 7 minutes for setup to complete
4. Phase 8 prompt appears
5. Says 'n' to defer onboarding
6. CORTEX ready to use immediately
7. **Later:** Runs `onboard application` when convenient

**Result:** Faster initial setup, analysis deferred

---

### Scenario 3: CI/CD Pipeline

**Flow:**
1. Runs `setup cortex --non-interactive`
2. Setup completes in ~7 minutes
3. Phase 8 automatically skipped (non-interactive mode)
4. Pipeline continues with next steps

**Result:** No blocking prompts, predictable execution time

---

### Scenario 4: Developer Never Needs Onboarding

**Flow:**
1. Runs `setup cortex`
2. Approves setup steps in Phase 2
3. Phase 8 prompt appears
4. Says 'n' to skip onboarding
5. Never runs `onboard application`

**Result:** CORTEX works fine without onboarding (it's truly optional)

---

## 🔍 Manual Onboarding Command

**Users can run onboarding anytime after setup:**

```bash
# Natural language
onboard application
analyze application
analyze my project
run onboarding

# All trigger OnboardingOrchestrator
```

**What happens:**
1. Detects project structure
2. Runs quality analysis
3. Performs security scan
4. Collects performance metrics
5. Generates dashboard
6. Saves report to `cortex-brain/documents/analysis/`

---

## 📝 Phase Results Structure

**After Enhanced Flow completes:**

```python
phase_results = {
    'detection': {...},
    'consent': {
        'action': 'proceed',
        'approved_steps': ['dependencies', 'gitignore', 'copilot_instructions'],
        'onboarding_deferred': True  # ⭐ NEW
    },
    'dependencies': {...},
    'policy_validation': {...},
    'realignment': {...},
    'onboarding': {
        'deferred': True,  # ⭐ NEW
        'message': 'Will be offered after setup completes'
    },
    'gitignore': {...},
    'copilot_instructions': {...},
    'completion_report': {...},
    'post_setup_onboarding': {  # ⭐ NEW
        # If user said 'y':
        'success': True,
        'quality_score': 82.3,
        'security_issues': 4,
        'dashboard_url': '...'
        
        # OR if user said 'n':
        'skipped': True,
        'user_choice': 'deferred'
        
        # OR if non-interactive:
        'skipped': True,
        'reason': 'non-interactive mode'
    }
}
```

---

## 🔄 Backward Compatibility

**Existing Systems:**
- No breaking changes to Phase 1-7
- Phase 4 now shows "deferred" instead of running analysis
- Phase 8 is additive (new phase)

**User Impact:**
- Previous behavior: Onboarding automatic if approved
- New behavior: Onboarding requires explicit Phase 8 consent
- **Migration:** Documented in setup-enhanced-flow-guide.md

---

## 📚 Related Documentation

- **Master Setup Orchestrator:** `src/orchestrators/master_setup_orchestrator.py`
- **Onboarding Orchestrator:** `src/operations/onboarding_orchestrator.py`
- **User Consent Manager:** `src/operations/user_consent_manager.py`
- **Setup EPM Guide:** `.github/prompts/modules/setup-epm-guide.md`

---

**Last Updated:** November 27, 2025  
**Version:** 1.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
