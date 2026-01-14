# CORTEX Hallucination Fix - Quick Implementation Guide

**Priority:** CRITICAL  
**Status:** Ready to Implement  
**Estimated Fix Time:** 4 hours  
**Risk Level:** Low (fixes are additive safeguards)

---

## 🎯 The Problem in 30 Seconds

- User said "Proceed" (intended for Phase 3 only)
- Copilot hallucinated execution of Phases 3-11 in single response
- Generated 9,291 lines of fabricated terminal output
- Claimed 85/110 ACs done when actually 36/110
- **Root cause:** No phase boundary checks + no CORE-025 challenges

---

## ✅ Fix #1: Phase Boundary Check (30 min - DO THIS FIRST)

**File:** `src/orchestrators/core/master_orchestrator.py`

**Add this method:**
```python
def advance_to_next_phase(self):
    """
    CRITICAL: Enforce phase boundaries
    Returns False to BLOCK auto-advancement between phases
    """
    current_phase = self.get_current_phase()
    
    # Verify current phase is 100% complete
    current_completion = self.tracker['phases'][f'phase_{current_phase}']
    if current_completion['status'] != 'completed':
        return False
    
    # BLOCK: Force user confirmation for phase advancement
    # This breaks the hallucination loop
    return False  # ← Always return False (user must say "proceed" again)
```

**Where to call it:**
```python
# In execute() method, after AC implementation loop:
if all_acs_in_phase_complete():
    should_advance = self.advance_to_next_phase()
    if not should_advance:
        return {  # ← STOP HERE, wait for user
            'status': 'phase_complete',
            'next_action': 'User confirmation required for next phase'
        }
```

---

## ✅ Fix #2: Add CORE-025 Challenge (60 min)

**File:** `.github/prompts/CORTEX.prompt.md`

**Add before any phase boundary:**
```markdown
## PHASE COMPLETION CHALLENGE (CORE-025 Enforcement)

When any phase completes 100%, present this challenge:

---

✅ PHASE X COMPLETE

• {AC-ID-1}: {Title} ✅
• {AC-ID-2}: {Title} ✅
...

🎯 NEXT STEPS

Phase X+1 ({Name}) is ready to begin with {N} acceptance criteria.

**Ready to proceed to Phase X+1?**

Options:
1. `Yes` → Begin Phase X+1 implementation
2. `No` → Stop execution, review current state
3. `Review` → Show Phase X+1 requirements first

**Awaiting your decision...**

---

**Implementation:** Add to MasterOrchestrator output before returning:

```python
if phase_complete:
    return {
        'status': 'challenge',
        'message': f'Ready to proceed to Phase {next_phase}?',
        'options': ['Yes', 'No', 'Review'],
        'require_user_input': True  # ← BLOCK execution
    }
```
```

---

## ✅ Fix #3: SSOT Validation (120 min)

**File:** `src/orchestrators/core/master_orchestrator.py`

**Add validation before reporting completion:**
```python
def validate_before_reporting(self, ac_id, claimed_status):
    """
    BLOCK any completion claim not backed by SSOT evidence
    """
    # Reload tracker (source of truth)
    tracker = self.load_progress_tracker()
    
    # Check if AC actually implemented
    for implemented_ac in tracker.get('implemented_ac_ids', []):
        if ac_id == implemented_ac:
            return True
    
    # BLOCK: No evidence found
    logger.error(f'{ac_id} not in SSOT - blocking completion claim')
    return False
```

**Usage:**
```python
# Before reporting AC complete:
if not self.validate_before_reporting(ac_id, 'completed'):
    raise GoveranceException(f'Cannot claim {ac_id} complete - no SSOT evidence')
```

---

## ✅ Fix #4: Hallucination Detection (120 min)

**File:** `src/infrastructure/hallucination_detector.py` (NEW)

```python
class HallucinationDetector:
    """Real-time hallucination detection"""
    
    def check_metrics_drift(self):
        """Compare reported vs SSOT metrics"""
        reported = self.get_reported_metrics()
        actual = self.load_from_ssot()
        
        drift = abs(reported['completion'] - actual['completion'])
        if drift > 10:  # >10% difference = hallucination
            return {
                'detected': True,
                'confidence': 0.95,
                'action': 'BLOCK_OUTPUT'
            }
        return {'detected': False}
    
    def check_perfect_success_rate(self):
        """100% success is unrealistic"""
        success_rate = self.calculate_recent_success_rate()
        if success_rate > 0.98:  # >98% = suspicious
            return {
                'detected': True,
                'confidence': 0.80,
                'action': 'WARN_USER'
            }
        return {'detected': False}
    
    def check_identical_terminal_patterns(self):
        """Terminal output should vary"""
        patterns = self.analyze_terminal_outputs()
        if patterns['similarity'] > 0.95:  # >95% identical = fake
            return {
                'detected': True,
                'confidence': 0.90,
                'action': 'BLOCK_OUTPUT'
            }
        return {'detected': False}
```

**Integration:**
```python
# Before returning orchestrator result:
detector = HallucinationDetector()
if detector.check_metrics_drift()['detected']:
    raise HallucinationException('Metrics drift detected - not backed by SSOT')
```

---

## ✅ Fix #5: Operations Per Response Guard (60 min)

**File:** `.github/prompts/CORTEX.prompt.md`

**Update:**
```markdown
## INCREMENTAL EXECUTION (CORE-001 Enforcement)

**STRICT LIMIT: 1 AC-ID per orchestrator invocation**

After implementing 1 AC:
1. Report: "AC-{ID}: {Title} implemented (1/1 this response)"
2. Print: "Type 'continue' to implement next AC"
3. STOP - Wait for user input

**This ensures:**
- <500 lines per response (CORE-001)
- User stays in control (no runaway loops)
- Hallucination impossible (only 1 action per turn)

**Implementation:**

```python
if operations_count >= 1:
    print(f"✅ AC-{ac_id} complete (1/1 this response)")
    print("→ Type 'continue' to implement next AC or 'status' to review")
    return  # ← STOP immediately
```
```

---

## 📋 Implementation Checklist

- [ ] Fix #1: Phase boundary check (30 min)
  - [ ] Add `advance_to_next_phase()` method
  - [ ] Wire into execute() loop
  - [ ] Test: Verify Phase 3 doesn't auto-advance to Phase 4

- [ ] Fix #2: CORE-025 challenges (60 min)
  - [ ] Add challenge template to CORTEX.prompt.md
  - [ ] Add return statement with `require_user_input: True`
  - [ ] Test: Verify challenge appears after phase complete

- [ ] Fix #3: SSOT validation (120 min)
  - [ ] Add `validate_before_reporting()` method
  - [ ] Add error throwing for missing evidence
  - [ ] Test: Try to claim non-existent AC complete → Error

- [ ] Fix #4: Hallucination detection (120 min)
  - [ ] Create `hallucination_detector.py`
  - [ ] Implement 3 detection methods
  - [ ] Wire into MasterOrchestrator pre-return
  - [ ] Test: Inject fake metrics → Detection triggers

- [ ] Fix #5: Limit operations (60 min)
  - [ ] Add max-1-AC-per-response check
  - [ ] Update CORTEX.prompt.md
  - [ ] Test: Generate 500+ lines → Operation stops

**Total Implementation Time: ~4 hours**

---

## 🧪 Testing Protocol

After implementing all fixes, run these tests:

```bash
# Test 1: Single phase execution
python3 -m src.main "implement phase 3"
# Expected: Only Phase 3 executes, stops with challenge

# Test 2: Challenge appears
# User sees: "Ready to proceed to Phase 4? (Yes/No/Review)"
# Verify: Challenge requires user input

# Test 3: SSOT validation
# Try: Manually claim fake AC complete
# Expected: validation_before_reporting() blocks it

# Test 4: Hallucination detection
# Inject: Fake metrics (85/110 instead of 36/110)
# Expected: detector.check_metrics_drift() triggers

# Test 5: Response length
# Generate: Full phase execution
# Expected: ~300-400 lines (not 9,291)
```

---

## 🎯 Success Criteria

✅ **Fix Successful if:**
- [ ] No auto-advancement between phases
- [ ] Phase boundary challenge appears every time
- [ ] All metrics match SSOT (progress-tracker.json)
- [ ] Response length <500 lines per AC (CORE-001)
- [ ] 0 hallucinated ACs or fabricated metrics in 10 test runs

❌ **Fix Failed if:**
- [ ] Any phase auto-advances without user confirmation
- [ ] Metrics drift >5% from SSOT files
- [ ] Response >500 lines
- [ ] Hallucination detector doesn't fire on known hallucinations

---

## 📞 Contact & Questions

**Primary Author:** Architecture Analysis  
**File Location:** `cortex-brain/analysis/HALLUCINATION-ROOT-CAUSE-ANALYSIS.md` (full details)  
**This Guide:** `cortex-brain/analysis/HALLUCINATION-FIX-QUICK-GUIDE.md`

---

**Status: Ready to Implement** ✅
