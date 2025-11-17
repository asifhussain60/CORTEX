# Phase 3 Behavioral Test Execution Guide

**Date:** 2025-11-08  
**Phase:** 3 - Modular Entry Point Validation  
**Purpose:** Step-by-step guide for executing behavioral validation tests  
**Status:** Ready for execution

---

## 🎯 Overview

This guide provides detailed instructions for executing the 10 behavioral validation test scenarios to confirm that the modular entry point approach achieves the measured 97.2% token reduction in practice with GitHub Copilot.

**Prerequisites:**
- ✅ Test structure created (`cortex-slim-test.md` + 3 excerpts)
- ✅ Token measurements complete (97.2% reduction confirmed)
- ✅ Test scenarios defined (10 scenarios in `test-scenarios.md`)
- ⏳ Ready for behavioral validation execution

---

## 📋 Quick Test Execution Checklist

### Before You Start
- [ ] Open GitHub Copilot Chat in VS Code
- [ ] Have this guide open in a separate window
- [ ] Prepare to take screenshots of each test
- [ ] Note the time for each test (subjective response time)
- [ ] Create a results document to record findings

### Test Execution Order
1. [ ] Test 4: Backward Compatibility (baseline measurement)
2. [ ] Test 1: Story Intent (modular approach)
3. [ ] Test 2: Setup Intent (modular approach)
4. [ ] Test 3: Technical Intent (modular approach)
5. [ ] Test 5: Direct Module (direct access)
6. [ ] Test 6: Multiple Modules (combined)
7. [ ] Test 7: No Intent (edge case)
8. [ ] Test 8: Invalid Module (error handling)
9. [ ] Test 9: Rapid Switching (context switching)
10. [ ] Test 10: Stress Test (all modules)

---

## 🧪 Test 1: Story Intent (Modular Approach)

### Objective
Verify that requesting the CORTEX story through the slim entry point loads only the story module, achieving ~97% token reduction.

### Steps

**1. Open a NEW GitHub Copilot Chat conversation**
   - Click "New Chat" or restart VS Code
   - Ensure clean state (no previous context)

**2. Enter the following command exactly:**
```markdown
#file:prompts/user/cortex-slim-test.md

Tell me the CORTEX story
```

**3. Observe and document:**
   - ✅ Does the story content appear?
   - ✅ Does it mention "The Intern with Amnesia"?
   - ✅ Is the response focused on the story (not other documentation)?
   - ✅ How long did it take to respond? (subjective)

**4. Take a screenshot:**
   - Capture the entire Copilot response
   - Save as `test1-story-intent-response.png`

**5. Estimate token count:**
   - If Copilot shows token usage → record it
   - If not visible → estimate based on response length
   - Expected: ~2,000-3,000 tokens (vs 74,000 baseline)

**6. Record results:**
```
Test 1: Story Intent
Date: _____
Result: ✅ Pass / ❌ Fail
Token Count (estimated): _____
Response Time: _____ seconds
Notes: _____
```

### Success Criteria
- ✅ Story content appears
- ✅ Mentions "The Intern with Amnesia"
- ✅ Focused response (not full documentation)
- ✅ Estimated tokens ≤5,000 (vs 74,000 baseline = 93% reduction)

---

## 🧪 Test 2: Setup Intent (Modular Approach)

### Objective
Verify that requesting setup instructions loads only the setup module.

### Steps

**1. Open a NEW GitHub Copilot Chat conversation**

**2. Enter the following command:**
```markdown
#file:prompts/user/cortex-slim-test.md

How do I set up CORTEX?
```

**3. Observe and document:**
   - ✅ Does setup/installation content appear?
   - ✅ Does it mention "Quick Start" or installation steps?
   - ✅ Is the response focused on setup (not story or API)?

**4. Take a screenshot:**
   - Save as `test2-setup-intent-response.png`

**5. Estimate token count:**
   - Expected: ~2,000-3,000 tokens

**6. Record results:**
```
Test 2: Setup Intent
Date: _____
Result: ✅ Pass / ❌ Fail
Token Count (estimated): _____
Response Time: _____ seconds
Notes: _____
```

### Success Criteria
- ✅ Setup instructions appear
- ✅ Mentions installation or configuration
- ✅ Focused response
- ✅ Estimated tokens ≤5,000 (93% reduction)

---

## 🧪 Test 3: Technical Intent (Modular Approach)

### Objective
Verify that requesting API documentation loads only the technical module.

### Steps

**1. Open a NEW GitHub Copilot Chat conversation**

**2. Enter the following command:**
```markdown
#file:prompts/user/cortex-slim-test.md

Show me the Tier 1 API reference
```

**3. Observe and document:**
   - ✅ Does API documentation appear?
   - ✅ Does it mention "WorkingMemory" or "KnowledgeGraph"?
   - ✅ Is the response focused on technical details?

**4. Take a screenshot:**
   - Save as `test3-technical-intent-response.png`

**5. Estimate token count:**
   - Expected: ~2,500-4,000 tokens (technical module is larger)

**6. Record results:**
```
Test 3: Technical Intent
Date: _____
Result: ✅ Pass / ❌ Fail
Token Count (estimated): _____
Response Time: _____ seconds
Notes: _____
```

### Success Criteria
- ✅ API documentation appears
- ✅ Mentions API classes or methods
- ✅ Focused response
- ✅ Estimated tokens ≤5,000 (93% reduction)

---

## 🧪 Test 4: Backward Compatibility (Baseline)

### Objective
Confirm that the full `cortex.md` file still works, establishing baseline token count.

### Steps

**1. Open a NEW GitHub Copilot Chat conversation**

**2. Enter the following command:**
```markdown
#file:prompts/user/cortex.md

Add a purple button to the HostControlPanel
```

**3. Observe and document:**
   - ✅ Does Copilot respond normally (as it did before modularization)?
   - ✅ Does it provide implementation steps or code?
   - ✅ Is there any difference from previous behavior?

**4. Take a screenshot:**
   - Save as `test4-backward-compat-response.png`

**5. Estimate token count:**
   - Expected: ~74,000 tokens (full file)
   - This is the baseline we're comparing against

**6. Record results:**
```
Test 4: Backward Compatibility
Date: _____
Result: ✅ Pass / ❌ Fail
Token Count (estimated): ~74,000 (baseline)
Response Time: _____ seconds
Notes: _____
```

### Success Criteria
- ✅ Response identical to pre-modular behavior
- ✅ No errors or confusion
- ✅ All documentation accessible
- ✅ Baseline token count confirmed (~74,000)

---

## 🧪 Test 5: Direct Module Reference

### Objective
Test direct module access (no slim entry point) to verify 97.2% reduction.

### Steps

**1. Open a NEW GitHub Copilot Chat conversation**

**2. Enter the following command (direct module reference):**
```markdown
#file:prompts/shared/test/story-excerpt.md

Summarize the CORTEX story
```

**3. Observe and document:**
   - ✅ Does story content appear?
   - ✅ Is this simpler than using slim entry point?
   - ✅ Is token count even lower than Test 1?

**4. Take a screenshot:**
   - Save as `test5-direct-module-response.png`

**5. Estimate token count:**
   - Expected: ~2,000 tokens (just module, no slim entry)
   - Should be lower than Test 1

**6. Record results:**
```
Test 5: Direct Module
Date: _____
Result: ✅ Pass / ❌ Fail
Token Count (estimated): _____
Response Time: _____ seconds
Comparison with Test 1: _____ (better/same/worse)
Notes: _____
```

### Success Criteria
- ✅ Story content appears
- ✅ Token count ≤2,500 (even better than modular)
- ✅ Simpler user experience (direct reference)

**Important:** This test validates the recommendation to prioritize direct module access over slim entry point routing.

---

## 🧪 Test 6: Multiple Modules

### Objective
Test how Copilot handles requests requiring multiple modules.

### Steps

**1. Open a NEW GitHub Copilot Chat conversation**

**2. Enter the following command:**
```markdown
#file:prompts/user/cortex-slim-test.md

Show me the setup guide and API reference
```

**3. Observe and document:**
   - ✅ Does Copilot provide both setup and technical content?
   - ✅ Does it load both modules?
   - ✅ How does it handle the multiple intent?

**4. Take a screenshot:**
   - Save as `test6-multiple-modules-response.png`

**5. Estimate token count:**
   - Expected: ~3,500-5,000 tokens (slim + 2 modules)
   - Still significantly less than baseline (93% reduction)

**6. Record results:**
```
Test 6: Multiple Modules
Date: _____
Result: ✅ Pass / ❌ Fail
Token Count (estimated): _____
Response Time: _____ seconds
Notes: _____
```

### Success Criteria
- ✅ Both modules' content appears (or reference provided)
- ✅ Token count ≤6,000
- ✅ Still 90%+ reduction vs baseline

---

## 🧪 Test 7: No Intent Specified

### Objective
Test how Copilot handles ambiguous requests (edge case).

### Steps

**1. Open a NEW GitHub Copilot Chat conversation**

**2. Enter the following command:**
```markdown
#file:prompts/user/cortex-slim-test.md

Help me
```

**3. Observe and document:**
   - ✅ Does Copilot ask for clarification?
   - ✅ Does it provide general guidance?
   - ✅ Does it gracefully handle the ambiguity?

**4. Take a screenshot:**
   - Save as `test7-no-intent-response.png`

**5. Estimate token count:**
   - Expected: ~1,500-2,000 tokens (just slim entry, maybe)

**6. Record results:**
```
Test 7: No Intent
Date: _____
Result: ✅ Pass / ❌ Fail
Token Count (estimated): _____
Response Time: _____ seconds
Notes: _____
```

### Success Criteria
- ✅ Graceful handling (no errors)
- ✅ Provides guidance or asks for clarification
- ✅ Token count minimal

---

## 🧪 Test 8: Invalid Module Request

### Objective
Test error handling for non-existent module requests.

### Steps

**1. Open a NEW GitHub Copilot Chat conversation**

**2. Enter the following command:**
```markdown
#file:prompts/user/cortex-slim-test.md

Show me the deployment guide
```

**3. Observe and document:**
   - ✅ Does Copilot handle gracefully?
   - ✅ Does it explain that deployment guide doesn't exist?
   - ✅ Does it suggest alternatives?

**4. Take a screenshot:**
   - Save as `test8-invalid-module-response.png`

**5. Estimate token count:**
   - Expected: ~1,500-2,000 tokens

**6. Record results:**
```
Test 8: Invalid Module
Date: _____
Result: ✅ Pass / ❌ Fail
Token Count (estimated): _____
Response Time: _____ seconds
Notes: _____
```

### Success Criteria
- ✅ Graceful error handling
- ✅ No system crash or confusion
- ✅ Reasonable token count

---

## 🧪 Test 9: Rapid Module Switching

### Objective
Test context switching between modules in a single conversation.

### Steps

**1. Open a NEW GitHub Copilot Chat conversation**

**2. Request story:**
```markdown
#file:prompts/user/cortex-slim-test.md

Tell me the story
```

**3. Wait for response, then request setup:**
```markdown
#file:prompts/user/cortex-slim-test.md

How do I install?
```

**4. Wait for response, then request technical:**
```markdown
#file:prompts/user/cortex-slim-test.md

Show me the API
```

**5. Observe and document:**
   - ✅ Does context switch smoothly?
   - ✅ Does Copilot remember previous requests?
   - ✅ Is cumulative token count reasonable?

**6. Take screenshots:**
   - Save as `test9-rapid-switching-1.png`, `test9-rapid-switching-2.png`, `test9-rapid-switching-3.png`

**7. Estimate cumulative token count:**
   - Expected: ~6,000-8,000 tokens (3 requests)
   - Still 89-91% reduction vs baseline (3 × 74,000 = 222,000)

**8. Record results:**
```
Test 9: Rapid Switching
Date: _____
Result: ✅ Pass / ❌ Fail
Cumulative Token Count: _____
Response Time (total): _____ seconds
Notes: _____
```

### Success Criteria
- ✅ All requests handled correctly
- ✅ Context switches smoothly
- ✅ Cumulative tokens ≤10,000 (vs 222,000 = 95% reduction)
- ✅ No confusion or context loss

---

## 🧪 Test 10: Stress Test (All Modules)

### Objective
Test requesting all documentation at once.

### Steps

**1. Open a NEW GitHub Copilot Chat conversation**

**2. Enter the following command:**
```markdown
#file:prompts/user/cortex-slim-test.md

Show me everything: story, setup, and technical documentation
```

**3. Observe and document:**
   - ✅ Does Copilot provide all content?
   - ✅ Is response coherent despite large request?
   - ✅ Is token count still significantly less than baseline?

**4. Take a screenshot:**
   - Save as `test10-stress-test-response.png`

**5. Estimate token count:**
   - Expected: ~5,000-7,000 tokens (slim + all 3 modules)
   - Still 91-93% reduction vs baseline

**6. Record results:**
```
Test 10: Stress Test
Date: _____
Result: ✅ Pass / ❌ Fail
Token Count (estimated): _____
Response Time: _____ seconds
Notes: _____
```

### Success Criteria
- ✅ All content accessible
- ✅ Token count ≤8,000 (89% reduction)
- ✅ Response remains coherent
- ✅ No performance issues

---

## 📊 Results Compilation

### After completing all 10 tests, compile results:

**Token Reduction Summary:**

| Test | Measured Tokens | Baseline Tokens | Reduction % |
|------|----------------|-----------------|-------------|
| 1. Story Intent | _____ | 74,000 | _____ % |
| 2. Setup Intent | _____ | 74,000 | _____ % |
| 3. Technical Intent | _____ | 74,000 | _____ % |
| 4. Backward Compat | ~74,000 | 74,000 | 0% (baseline) |
| 5. Direct Module | _____ | 74,000 | _____ % |
| 6. Multiple Modules | _____ | 74,000 | _____ % |
| 7. No Intent | _____ | 74,000 | _____ % |
| 8. Invalid Module | _____ | 74,000 | _____ % |
| 9. Rapid Switching | _____ | 222,000 | _____ % |
| 10. Stress Test | _____ | 74,000 | _____ % |

**Average Reduction:** _____ %  
**Expected:** 93-97%  
**Status:** ✅ Pass / ❌ Fail

### Qualitative Assessment:

**User Experience:**
- [ ] No degradation
- [ ] Smooth context switching
- [ ] Graceful error handling
- [ ] Intuitive interface

**Technical Performance:**
- [ ] Fast response times
- [ ] No system errors
- [ ] Token reduction confirmed
- [ ] Backward compatibility maintained

---

## 🎯 Decision Matrix Update

After completing all tests, update the decision matrix:

### Scoring

| Criterion | Weight | Score (1-5) | Weighted | Evidence |
|-----------|--------|-------------|----------|----------|
| **Token Reduction** | 40% | _____ | _____ | Test results |
| **Single Entry Point** | 30% | _____ | _____ | Tests 1-3, 6-10 |
| **Backward Compat** | 20% | _____ | _____ | Test 4 |
| **Implementation Effort** | 10% | 4.0 | 0.4 | Known (12-16 hrs) |
| **TOTAL** | 100% | - | _____ | **GO/NO-GO** |

**GO/NO-GO Threshold:** ≥3.5/5 = GO

### Expected Scores:

- **Token Reduction:** 5.0 (if ≥90% achieved)
- **Single Entry Point:** 4.5-5.0 (if behavior confirms)
- **Backward Compat:** 5.0 (if Test 4 passes)
- **Implementation Effort:** 4.0 (known)

**Expected Total:** 4.65-4.75 / 5 = **STRONG GO**

---

## 📋 Final Deliverables

After test execution, update these documents:

1. **`PHASE-3-VALIDATION-REPORT.md`**
   - Add test results to Section 2
   - Update decision matrix in Section 3
   - Add final recommendation in Section 5

2. **`status-data.yaml`**
   - Update `phase_3.tasks` with completion status
   - Update `phase_3.progress` to 1.0 (100%)
   - Add test metrics

3. **`STATUS.md`**
   - Update Phase 3 progress to 100%
   - Add completion summary
   - Update next actions for Phase 4

4. **`HOLISTIC-REVIEW-2025-11-08-FINAL.md`**
   - Add Phase 3 completion details
   - Update recommendations section

---

## 🚀 Expected Outcome

**Based on token measurements (97.2% reduction), we expect:**

- ✅ **STRONG GO decision** (4.65-4.75 / 5 score)
- ✅ **Proceed to Phase 3.7:** Full modular split (15-21 hours)
- ✅ **Priority:** Direct module access (97.2% reduction)
- ✅ **Secondary:** Slim entry point for flexibility (95.1% reduction)

**If unexpected issues arise:**
- Fallback to Phase 3.6: Python injection approach
- Re-evaluate decision matrix
- Consult with stakeholders

---

## 📞 Support

**Questions during test execution?**
- Review `test-scenarios.md` for detailed test specifications
- Check `PHASE-3-VALIDATION-REPORT.md` for context
- Consult `24-holistic-review-and-adjustments.md` for strategic guidance

**Contact:** CORTEX Development Team  
**Phase:** 3 - Modular Entry Point Validation  
**Status:** Ready for execution

---

**Document Version:** 1.0  
**Created:** 2025-11-08  
**Purpose:** Step-by-step guide for Phase 3 behavioral validation  
**Next:** Execute tests → Compile results → Make final decision
