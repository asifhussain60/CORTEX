# CORTEX Phase 3 - Test Scenarios & Validation Suite

**Purpose:** Comprehensive test scenarios for modular entry point validation  
**Phase:** 3 - Modular Entry Point Validation  
**Timeline:** Week 11-12 (Days 3-5)  
**Status:** Test specification ready for execution

---

## 🎯 Test Objectives

1. **Verify single entry point maintained** - User only interacts with slim file
2. **Measure token reduction** - Compare baseline vs modular approach
3. **Validate backward compatibility** - Existing commands still work
4. **Document Copilot behavior** - What files actually get loaded?
5. **Assess user experience impact** - Any workflow changes?

---

## 📋 Test Scenario 1: Story Intent

### Test Setup
- **Entry point:** `#file:prompts/user/cortex-slim-test.md`
- **User request:** "Tell me the CORTEX story"
- **Expected module:** `story-excerpt.md`
- **Expected token count:** ~1,600 tokens (slim 800 + story 800)

### Execution Steps
1. Open GitHub Copilot Chat
2. Enter command:
   ```markdown
   #file:prompts/user/cortex-slim-test.md
   
   Tell me the CORTEX story
   ```
3. Observe response
4. Measure token count (if possible via API)
5. Document which files were loaded

### Success Criteria
- ✅ Story content appears in response
- ✅ Response mentions "The Intern with Amnesia"
- ✅ Single entry point used (no manual module reference)
- ✅ Token count ≤2,000 tokens (~93% reduction vs baseline)

### Data to Collect
- [ ] Response content (screenshot)
- [ ] Token count (manual or API)
- [ ] Files loaded by Copilot (observable?)
- [ ] Response time (subjective)
- [ ] User experience notes

---

## 📋 Test Scenario 2: Setup Intent

### Test Setup
- **Entry point:** `#file:prompts/user/cortex-slim-test.md`
- **User request:** "How do I set up CORTEX?"
- **Expected module:** `setup-excerpt.md`
- **Expected token count:** ~1,600 tokens (slim 800 + setup 800)

### Execution Steps
1. Open GitHub Copilot Chat (new conversation)
2. Enter command:
   ```markdown
   #file:prompts/user/cortex-slim-test.md
   
   How do I set up CORTEX?
   ```
3. Observe response
4. Measure token count
5. Document files loaded

### Success Criteria
- ✅ Setup instructions appear in response
- ✅ Response mentions "Quick Start" or "Installation"
- ✅ Single entry point used
- ✅ Token count ≤2,000 tokens (~93% reduction)

### Data to Collect
- [ ] Response content (screenshot)
- [ ] Token count (manual or API)
- [ ] Files loaded by Copilot
- [ ] Response time
- [ ] User experience notes

---

## 📋 Test Scenario 3: Technical Intent

### Test Setup
- **Entry point:** `#file:prompts/user/cortex-slim-test.md`
- **User request:** "Show me the Tier 1 API reference"
- **Expected module:** `technical-excerpt.md`
- **Expected token count:** ~1,600 tokens (slim 800 + technical 800)

### Execution Steps
1. Open GitHub Copilot Chat (new conversation)
2. Enter command:
   ```markdown
   #file:prompts/user/cortex-slim-test.md
   
   Show me the Tier 1 API reference
   ```
3. Observe response
4. Measure token count
5. Document files loaded

### Success Criteria
- ✅ API documentation appears in response
- ✅ Response mentions "WorkingMemory" or "KnowledgeGraph" classes
- ✅ Single entry point used
- ✅ Token count ≤2,000 tokens (~93% reduction)

### Data to Collect
- [ ] Response content (screenshot)
- [ ] Token count (manual or API)
- [ ] Files loaded by Copilot
- [ ] Response time
- [ ] User experience notes

---

## 📋 Test Scenario 4: Backward Compatibility (Baseline)

### Test Setup
- **Entry point:** `#file:prompts/user/cortex.md` (full file)
- **User request:** "Add a purple button"
- **Expected behavior:** Works exactly as before
- **Expected token count:** ~28,000 tokens (7,026 lines)

### Execution Steps
1. Open GitHub Copilot Chat (new conversation)
2. Enter command:
   ```markdown
   #file:prompts/user/cortex.md
   
   Add a purple button to the HostControlPanel
   ```
3. Observe response
4. Measure token count
5. Compare with historical baseline

### Success Criteria
- ✅ Response is identical to pre-modular behavior
- ✅ No breaking changes
- ✅ All documentation still accessible
- ✅ Token count ~28,000 tokens (baseline)

### Data to Collect
- [ ] Response content (screenshot)
- [ ] Token count (baseline measurement)
- [ ] Files loaded
- [ ] Response time
- [ ] Any differences from expected behavior

---

## 📋 Test Scenario 5: Direct Module Reference

### Test Setup
- **Entry point:** `#file:prompts/shared/test/story-excerpt.md` (direct)
- **User request:** None (just load the module)
- **Expected token count:** ~800 tokens (story only, no slim file)

### Execution Steps
1. Open GitHub Copilot Chat (new conversation)
2. Enter command:
   ```markdown
   #file:prompts/shared/test/story-excerpt.md
   
   Summarize the CORTEX story
   ```
3. Observe response
4. Measure token count
5. Compare with Test Scenario 1

### Success Criteria
- ✅ Story content appears
- ✅ Token count ≤1,000 tokens (just module, no slim entry)
- ✅ Even better reduction than combined approach

### Data to Collect
- [ ] Response content
- [ ] Token count (module only)
- [ ] Comparison with Scenario 1
- [ ] User experience (is this simpler?)

---

## 📋 Test Scenario 6: Multiple Module References

### Test Setup
- **User request:** "Show me setup and technical docs"
- **Expected modules:** Multiple (setup-excerpt.md + technical-excerpt.md)
- **Expected token count:** ~2,400 tokens (slim 800 + setup 800 + technical 800)

### Execution Steps
1. Open GitHub Copilot Chat (new conversation)
2. Enter command:
   ```markdown
   #file:prompts/user/cortex-slim-test.md
   
   Show me the setup guide and API reference
   ```
3. Observe how Copilot handles multiple intents
4. Measure token count
5. Document behavior

### Success Criteria
- ✅ Both modules' content appears (or reference provided)
- ✅ Token count ≤3,000 tokens
- ✅ Still significantly less than baseline (90% reduction)

### Data to Collect
- [ ] Response content
- [ ] Token count (combined modules)
- [ ] How Copilot handled multiple intents
- [ ] User experience notes

---

## 📋 Test Scenario 7: No Intent Specified

### Test Setup
- **Entry point:** `#file:prompts/user/cortex-slim-test.md`
- **User request:** Generic request with no clear intent
- **Expected behavior:** Copilot requests clarification or loads nothing

### Execution Steps
1. Open GitHub Copilot Chat (new conversation)
2. Enter command:
   ```markdown
   #file:prompts/user/cortex-slim-test.md
   
   Help me
   ```
3. Observe response
4. Measure token count
5. Document Copilot's behavior

### Success Criteria
- ✅ Copilot provides guidance or asks for clarification
- ✅ Token count minimal (just slim entry, no modules)
- ✅ No errors or confusion

### Data to Collect
- [ ] Response content
- [ ] Token count (minimal expected)
- [ ] How Copilot handled ambiguity
- [ ] User experience

---

## 📋 Test Scenario 8: Invalid Module Request

### Test Setup
- **Entry point:** `#file:prompts/user/cortex-slim-test.md`
- **User request:** Request for non-existent module
- **Expected behavior:** Graceful error or fallback

### Execution Steps
1. Open GitHub Copilot Chat (new conversation)
2. Enter command:
   ```markdown
   #file:prompts/user/cortex-slim-test.md
   
   Show me the deployment guide
   ```
3. Observe response (deployment guide doesn't exist as module)
4. Measure token count
5. Document error handling

### Success Criteria
- ✅ Graceful handling (error message or suggestion)
- ✅ No system crash or confusion
- ✅ Token count reasonable

### Data to Collect
- [ ] Response content
- [ ] Token count
- [ ] Error handling quality
- [ ] User experience

---

## 📋 Test Scenario 9: Rapid Module Switching

### Test Setup
- **Multiple requests in same conversation**
- **Expected behavior:** Context switching between modules

### Execution Steps
1. Open GitHub Copilot Chat
2. Request story:
   ```markdown
   #file:prompts/user/cortex-slim-test.md
   
   Tell me the story
   ```
3. Then request setup:
   ```markdown
   #file:prompts/user/cortex-slim-test.md
   
   How do I install?
   ```
4. Then request technical:
   ```markdown
   #file:prompts/user/cortex-slim-test.md
   
   Show me the API
   ```
5. Observe how Copilot handles context switching
6. Measure cumulative token count

### Success Criteria
- ✅ All requests handled correctly
- ✅ Context switches smoothly
- ✅ Cumulative token count ≤5,000 tokens (vs 28,000 for baseline)
- ✅ No confusion or context loss

### Data to Collect
- [ ] All response contents
- [ ] Cumulative token count
- [ ] Context switching behavior
- [ ] User experience (does it feel natural?)

---

## 📋 Test Scenario 10: Stress Test (All Modules)

### Test Setup
- **Request all documentation at once**
- **Expected token count:** ~3,200 tokens (slim + all 3 modules)

### Execution Steps
1. Open GitHub Copilot Chat (new conversation)
2. Enter command:
   ```markdown
   #file:prompts/user/cortex-slim-test.md
   
   Show me everything: story, setup, and technical documentation
   ```
3. Observe response
4. Measure token count
5. Compare with baseline

### Success Criteria
- ✅ All content accessible
- ✅ Token count ≤4,000 tokens (~86% reduction vs baseline)
- ✅ No performance degradation
- ✅ Response remains coherent

### Data to Collect
- [ ] Response content
- [ ] Token count (all modules)
- [ ] Performance observations
- [ ] User experience

---

## 📊 Data Collection Summary

### Required Measurements

| Test Scenario | Expected Tokens | Baseline Tokens | Reduction % |
|---------------|----------------|-----------------|-------------|
| 1. Story Intent | ~1,600 | 28,000 | 94.3% |
| 2. Setup Intent | ~1,600 | 28,000 | 94.3% |
| 3. Technical Intent | ~1,600 | 28,000 | 94.3% |
| 4. Backward Compat | ~28,000 | 28,000 | 0% (baseline) |
| 5. Direct Module | ~800 | 28,000 | 97.1% |
| 6. Multiple Modules | ~2,400 | 28,000 | 91.4% |
| 7. No Intent | ~800 | 28,000 | 97.1% |
| 8. Invalid Module | ~800 | 28,000 | 97.1% |
| 9. Rapid Switching | ~5,000 | 84,000 | 94.0% |
| 10. All Modules | ~3,200 | 28,000 | 88.6% |

**Average Expected Reduction:** ~93.5%

### Evidence to Collect

For each test scenario, collect:
1. ✅ Screenshot of Copilot response
2. ✅ Token count (manual or API measurement)
3. ✅ Files loaded observation (if detectable)
4. ✅ Response time (subjective or measured)
5. ✅ User experience notes
6. ✅ Any unexpected behavior

---

## 🎯 Success Criteria (Overall)

### Quantitative Criteria

| Criterion | Target | Weight |
|-----------|--------|--------|
| Token Reduction | ≥90% | 40% |
| Backward Compatibility | 100% (zero breaking changes) | 20% |
| Single Entry Point | Maintained (user doesn't reference modules directly) | 30% |
| Implementation Effort | ≤15-21 hours | 10% |

**GO/NO-GO Threshold:** ≥3.5/5 weighted score

### Qualitative Criteria

- ✅ User experience not degraded
- ✅ Documentation still fully accessible
- ✅ No confusion or cognitive load increase
- ✅ Graceful error handling
- ✅ Context switching works smoothly

---

## 📝 Test Execution Log

### Test 1: Story Intent
- **Date:** _____
- **Tester:** _____
- **Result:** ✅ Pass / ❌ Fail
- **Token Count:** _____
- **Notes:** _____

### Test 2: Setup Intent
- **Date:** _____
- **Tester:** _____
- **Result:** ✅ Pass / ❌ Fail
- **Token Count:** _____
- **Notes:** _____

### Test 3: Technical Intent
- **Date:** _____
- **Tester:** _____
- **Result:** ✅ Pass / ❌ Fail
- **Token Count:** _____
- **Notes:** _____

### Test 4: Backward Compatibility
- **Date:** _____
- **Tester:** _____
- **Result:** ✅ Pass / ❌ Fail
- **Token Count:** _____
- **Notes:** _____

### Test 5: Direct Module Reference
- **Date:** _____
- **Tester:** _____
- **Result:** ✅ Pass / ❌ Fail
- **Token Count:** _____
- **Notes:** _____

### Test 6: Multiple Module References
- **Date:** _____
- **Tester:** _____
- **Result:** ✅ Pass / ❌ Fail
- **Token Count:** _____
- **Notes:** _____

### Test 7: No Intent Specified
- **Date:** _____
- **Tester:** _____
- **Result:** ✅ Pass / ❌ Fail
- **Token Count:** _____
- **Notes:** _____

### Test 8: Invalid Module Request
- **Date:** _____
- **Tester:** _____
- **Result:** ✅ Pass / ❌ Fail
- **Token Count:** _____
- **Notes:** _____

### Test 9: Rapid Module Switching
- **Date:** _____
- **Tester:** _____
- **Result:** ✅ Pass / ❌ Fail
- **Token Count:** _____
- **Notes:** _____

### Test 10: Stress Test (All Modules)
- **Date:** _____
- **Tester:** _____
- **Result:** ✅ Pass / ❌ Fail
- **Token Count:** _____
- **Notes:** _____

---

## 🚀 Next Steps After Testing

1. **Compile results** into validation report
2. **Calculate decision matrix score** (weighted criteria)
3. **Make GO/NO-GO decision** (threshold: ≥3.5/5)
4. **Document recommendation** for Phase 4 approach
5. **Update status tracking documents**

---

**Document Version:** 1.0  
**Created:** 2025-11-08  
**Phase:** 3 - Modular Entry Point Validation  
**Deliverable:** Test scenarios and validation suite
