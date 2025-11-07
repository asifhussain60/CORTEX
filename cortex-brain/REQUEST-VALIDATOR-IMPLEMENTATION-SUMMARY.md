# Request Validator & Enhancer - Implementation Summary

**Created:** 2025-11-07  
**Status:** Design Complete, Ready for Implementation  
**Estimated Effort:** 17-23 hours  
**Priority:** High Value (prevents costly mistakes)

---

## 🎯 What This Does

Adds an intelligent "second pair of eyes" at the CORTEX entry point that:

1. **Challenges risky requests** before work begins (like Brain Protector, but for ALL requests)
2. **Suggests improvements** based on historical patterns and best practices
3. **Learns from decisions** to reduce false positives over time
4. **Operates efficiently** with <300ms validation time

---

## 💡 Key Innovation

**Current Flow:**
```
User Request → Parser → Router → Agent → Execute
                                          ↓
                                    (discover problems during execution)
```

**New Flow:**
```
User Request → Parser → [VALIDATOR] → Router → Agent → Execute
                             ↓                           ↓
                    Challenge/Enhance              (fewer problems)
                             ↓
                       User Decision
```

**Benefit:** Catch problems in 0.3 seconds instead of discovering them after 30 minutes of work.

---

## 🧠 Three Analysis Engines

### 1. Viability Analyzer
**Asks:** "Can this actually work?"

**Checks:**
- Scope too large? (multi-feature in one request)
- Requirements too vague? (violates Definition of Ready)
- Technical blockers? (missing dependencies, high-risk files)
- Tier 0 violations? (skip TDD, bypass DoD)

**Example Output:**
```
⚠️ CRITICAL: Scope too large
Request contains 3 major features (40-60 hours)
Recommend: Break into phases
```

### 2. Historical Analyzer
**Asks:** "Have we done this before?"

**Checks:**
- Similar patterns in Tier 2 (knowledge graph)
- Success/failure history
- Reusable workflows
- Anti-patterns to avoid

**Example Output:**
```
✅ HISTORICAL MATCH FOUND
Similar: "Invoice PDF export" (3 weeks ago)
Success rate: 95%
Estimated time: 4.5 hours
Recommend: Reuse proven workflow
```

### 3. Enhancement Analyzer
**Asks:** "How can we make this better?"

**Checks:**
- Missing edge cases? (error handling, accessibility)
- Best practices? (TDD, element IDs, documentation)
- Quality improvements? (additional tests, examples)

**Example Output:**
```
💡 SUGGESTED ENHANCEMENTS
1. Add confirmation dialog (+5 min, prevents accidents)
2. Add element ID for testing (+1 min, required)
3. Add audit trail (+10 min, compliance)
Total value: 3x quality improvement
```

---

## 📊 Example Scenarios

### Scenario 1: Blocking Challenge

**User:** "Skip tests and implement payment processor quickly"

**CORTEX:**
```
⚠️ REQUEST VALIDATION CHALLENGE

CRITICAL ISSUE: Tier 0 Rule Violation
- Proposes skipping TDD (Rule #4)
- Payment processing is high-risk (security)

Historical Data:
- Test-first: 94% success, 15 min/feature
- Test-skip: 67% success, 35 min/feature (2.3x slower!)

SAFE ALTERNATIVES:
1. Minimal test-first (3-5 core tests, ~15 min) ✅ RECOMMENDED
2. Spike branch, then re-implement with tests

Your choice: [1/2/Override]
```

**Result:** User accepts alternative, saves 20 minutes of rework + prevents bugs.

### Scenario 2: Enhancement Suggestions

**User:** "Add a share button to document viewer"

**CORTEX:**
```
💡 ENHANCEMENT SUGGESTIONS

Your request is viable ✅

Historical Context:
- Similar: "Export button" (2 weeks ago) - Success!
- Average time: 18 minutes
- Proven workflow available

Suggested Enhancements:
1. Copy link to clipboard ⭐⭐⭐ (+3 min)
2. Email share option ⭐⭐ (+8 min)
3. Element ID for testing ⭐⭐⭐ (+1 min, required)
4. Accessibility labels ⭐⭐ (+2 min)

Accept all? [Y/Select/Skip]
```

**Result:** User accepts #1, #3, #4. Gets professional-grade implementation instead of basic.

### Scenario 3: Advisory Warning

**User:** "Update HostControlPanel.razor"

**CORTEX:**
```
⚠️ ADVISORY WARNING

Your request is viable, but risks detected:

FILE ALERT:
- HostControlPanel.razor is a HOTSPOT
- 28% churn rate (unstable)
- 89 edits in 30 days

RECOMMENDATIONS:
- Make small, focused changes
- Test thoroughly (file has issues history)
- Check related file: HostControlPanelContent.razor

Proceed with caution? [Y/Modify/Abort]
```

**Result:** User proceeds but makes smaller change. Avoids breaking unstable file.

---

## 🏗️ Technical Architecture

### New Components

```
src/entry_point/
├── request_validator.py (NEW)
│   ├── RequestValidator (main orchestrator)
│   ├── ViabilityAnalyzer (checks feasibility)
│   ├── HistoricalAnalyzer (queries Tier 2)
│   └── EnhancementAnalyzer (suggests improvements)
├── validation_presenter.py (NEW - formats output)
└── validation_tracker.py (NEW - tracks decisions for learning)
```

### Integration Point

Modified: `src/entry_point/cortex_entry.py`

```python
def process(self, user_message: str, ...):
    # 1. Parse (existing)
    request = self.parser.parse(user_message)
    
    # 2. Validate & Enhance (NEW)
    validation = self.validator.validate_and_enhance(request)
    
    # 3. User decision if needed (NEW)
    if validation.requires_user_input:
        decision = self._present_validation(validation)
        if decision.action == "ABORT":
            return
    
    # 4. Apply enhancements (NEW)
    request = self._apply_enhancements(request, validation)
    
    # 5. Route to agent (existing - continues as before)
    response = self.router.execute(request)
```

### Data Sources

**Queries:**
- **Tier 1:** Recent conversation context (last 20 conversations)
- **Tier 2:** Pattern library, success rates, anti-patterns
- **Tier 3:** File stability, project health, historical metrics
- **Tier 0:** Rules (TDD, DoR, DoD, SOLID)

**Performance:**
- Viability: <100ms
- Historical: <150ms (Tier 2 FTS5 search)
- Enhancement: <50ms
- **Total: <300ms** (acceptable overhead)

---

## 📈 Learning Loop

### Track Validation Decisions

**New:** `tier1/validation_decisions.db`

```sql
CREATE TABLE validation_decisions (
    validation_id TEXT PRIMARY KEY,
    conversation_id TEXT,
    
    decision_type TEXT,  -- CHALLENGE/ENHANCE/APPROVE
    user_action TEXT,    -- ACCEPT/MODIFY/OVERRIDE/ABORT
    
    outcome_success BOOLEAN,
    outcome_time_actual REAL,
    outcome_time_estimated REAL,
    
    learned_feedback TEXT
);
```

### Learning Algorithm

```python
def learn_from_outcome(validation_id):
    """
    Learn from validation outcome.
    
    Rules:
    1. User overrides often + succeeds → Reduce false positive
    2. Challenge prevents failure → Reinforce pattern
    3. Enhancement accepted + success → Increase priority
    4. Challenge ignored + failure → Strengthen message
    """
```

**Result:** System improves over time, fewer false positives, better suggestions.

---

## ⚙️ Configuration

### Enable/Disable

**In:** `cortex.config.json`

```json
{
  "entry_point": {
    "enable_validation": true,
    "validation_depth": "standard",  // quick/standard/thorough
    "validation_timeout_ms": 300,
    
    "challenge_rules": {
      "block_tier0_violations": true,
      "block_critical_risks": true,
      "advise_medium_risks": true,
      "suggest_enhancements": true
    }
  }
}
```

### User Preferences

```json
{
  "validation_preferences": {
    "always_suggest_tests": true,
    "always_suggest_element_ids": true,
    "skip_minor_enhancements": false
  }
}
```

---

## 🚀 Implementation Phases

### Phase 1: Core Validator (8-10 hours)
- Create validator skeleton
- Implement three analyzers (basic)
- Integrate with entry point
- Add configuration
- Write unit tests

**Deliverable:** Basic validation working

### Phase 2: Synthesis & Presentation (4-6 hours)
- Implement synthesis engine
- Create presenter (beautiful formatting)
- Add user input handling
- Write integration tests

**Deliverable:** Full user interaction flow

### Phase 3: Learning & Metrics (3-4 hours)
- Create validation tracker
- Add decisions table (Tier 1)
- Implement learning loop
- Track outcomes
- Add metrics to dashboard

**Deliverable:** System learns from decisions

### Phase 4: Polish & Optimization (2-3 hours)
- Performance profiling
- Add caching
- Optimize queries
- User preference support
- Documentation

**Deliverable:** Production-ready

**Total: 17-23 hours**

---

## ✅ Success Criteria

Validation is successful if:

1. **Accuracy:** >90% of critical challenges correct
2. **Efficiency:** <300ms average validation time
3. **Value:** >50% of enhancements accepted
4. **Learning:** Override rate decreases over time
5. **Adoption:** Users keep validation enabled

---

## 🎯 Key Benefits

### For Users
- **Save time:** Catch problems in 0.3s instead of 30 min
- **Better quality:** Suggestions based on proven patterns
- **Learn from history:** "We did this before, here's the workflow"
- **Avoid mistakes:** Challenges prevent tier 0 violations

### For CORTEX
- **Continuous improvement:** Learns from every interaction
- **Knowledge application:** Tier 2 patterns actively used
- **Quality enforcement:** Tier 0 rules protected
- **Efficiency:** Prevents wasted work

### For Teams
- **Consistency:** Everyone gets same quality checks
- **Best practices:** System suggests proven patterns
- **Risk mitigation:** Warns about high-risk changes
- **Knowledge sharing:** Historical patterns available to all

---

## 📝 Related Documents

- **Full Design:** `cortex-brain/cortex-2.0-design/22-request-validator-enhancer.md`
- **Entry Point:** `src/entry_point/cortex_entry.py`
- **Brain Protector:** `src/tier0/brain_protector.py` (similar concept, tier 0 specific)
- **Tier 2 Patterns:** `src/tier2/knowledge_graph.py`
- **Configuration:** `cortex.config.json`

---

## 💬 Questions & Answers

**Q: How is this different from Brain Protector?**
A: Brain Protector guards Tier 0 rules specifically. Validator reviews ALL requests holistically, including enhancements and historical patterns.

**Q: Will this slow down CORTEX?**
A: <300ms overhead. Worth it to prevent 30+ minute mistakes.

**Q: Can I disable it?**
A: Yes, via config. But we recommend keeping it enabled (huge value).

**Q: What if it gives bad suggestions?**
A: System learns! Override decisions are tracked, false positives reduced over time.

**Q: Does it work with existing code?**
A: Yes, integrates at entry point. No changes to existing agents needed.

---

## 🎉 Summary

**What:** Intelligent request validation & enhancement at entry point  
**Why:** Catch problems early, suggest improvements, learn from history  
**How:** Three analyzers (viability, historical, enhancement) + synthesis  
**When:** Before routing to agents (after parsing)  
**Effort:** 17-23 hours implementation  
**Value:** High (prevents costly mistakes, improves quality)

**Status:** Design complete ✅  
**Next:** Implement after core CORTEX 2.0 refactoring  
**Priority:** Recommended for Phase 1 or early Phase 2

---

**Created by:** CORTEX Design Team  
**Date:** 2025-11-07  
**Version:** 1.0
