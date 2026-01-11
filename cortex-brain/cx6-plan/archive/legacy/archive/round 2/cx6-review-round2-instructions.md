# GPT-4 Holistic Design Review - Round 2 Instructions

**Review Date:** 2026-01-10  
**CORTEX Version:** 6.0.0  
**Review Type:** Holistic Design Quality Assessment  
**Target Score:** 95+ / 100  

---

## 📋 CRITICAL: Read This First

**You are reviewing DESIGN SPECIFICATIONS, not implementation.**

**Before starting, READ:**
1. `cx6-reviewer-guidance.md` (THIS FILE PREVENTS INVALID RECOMMENDATIONS)
2. `cx6-architecture-detailed.yaml` (System overview)
3. `AC-INDEX.yaml` (Acceptance criteria registry)

**DO NOT:**
- Flag "missing implementation" (AC-IDs are not started by design)
- Demand exhaustive upfront specifications (we use incremental AC building)
- Assume no existing infrastructure (check git recovery notes)
- Overcomplicate simple problems (e.g., "dir requires shell=True")

**DO:**
- Identify logical contradictions in design
- Find security escape hatches (symlinks, injections, approvals)
- Assess operational feasibility (rollback triggers, minimum samples)
- Challenge underspecified critical controls (approval timeouts, path canonicalization)

---

## 🎯 Review Objective

**Current Design Score:** 83/100  
**Target Design Score:** 95+/100  

**5 Critical Improvements Already Accepted:**
1. ✅ **AC-SECURITY-005:** Approval State Machine (+10 points)
2. ✅ **AC-SECURITY-006:** Canonical Path Resolution (+7 points)
3. ✅ **AC-ROUTE-004:** Unicode-Safe Intent Normalization (+5 points)
4. ✅ **AC-ROUTE-005:** Complete PREFIX Tie-Breaking (+1 point)
5. ✅ **AC-ROLLOUT-004:** Statistical Trigger Guards (+2 points)

**Your task:** Validate these improvements address the gaps, identify any remaining issues.

---

## 📁 Files to Review

### Primary Design Specs (MUST READ)

1. **cx6-security-layer.yaml** (717 lines)
   - Focus: Threat model, ActionPolicyEngine, path sandboxing, command allowlists
   - New AC-IDs: AC-SECURITY-005 (Approval), AC-SECURITY-006 (Paths), AC-SECURITY-008 (Commands)

2. **cx6-routing-spec.yaml**
   - Focus: Pattern matching, conflict detection, normalization
   - New AC-IDs: AC-ROUTE-004 (Unicode), AC-ROUTE-005 (Tie-breaking)

3. **cx6-rollout-lifecycle.yaml**
   - Focus: SHADOW → CANARY → ACTIVE progression, rollback triggers
   - New AC-ID: AC-ROLLOUT-004 (Statistical guards)

4. **cx6-architecture-detailed.yaml**
   - Focus: 4-tier governance, orchestration pipeline, audit integration

### Supporting Context

5. **AC-INDEX.yaml** (2700+ lines)
   - All acceptance criteria with dependencies, tests, implementation notes
   - Design score tracking: current 83 → target 95+

6. **core-rules.yaml** (1175 lines)
   - 21 SKULL rules (Tier 0 governance)
   - Enforcement hooks, validation logic

7. **cx6-reviewer-guidance.md**
   - **READ THIS FIRST** - Prevents invalid recommendations
   - Common pitfalls, scoring calibration, review process

---

## 🔍 Review Focus Areas

### 1. Approval Protocol (AC-SECURITY-005)

**Acceptance Criteria:**
```yaml
States: REQUESTED → APPROVED/DENIED/EXPIRED
Timeout: 5 minutes default, configurable
Non-interactive: DENY by default (fail-closed)
Audit: correlation_id, timestamp, actor, decision, justification
Replay protection: approval tokens expire after single use
```

**Review Questions:**
- Is the state machine complete? (What about REQUESTED → CANCELLED?)
- How does timeout interact with long-running operations? (e.g., vacuum takes 15 minutes)
- What if approval arrives AFTER timeout? (Race condition?)
- How is "actor" authenticated in non-interactive mode?
- Is replay protection sufficient? (Can tokens be reused across sessions?)

**Previous Gap (Round 1):**
> "Approval-required actions have no defined approval mechanism. Either (a) approvals become bypassable, or (b) system deadlocks, or (c) operators auto-approve and normalize unsafe behavior."

**Design Response:**
- AC-SECURITY-005 defines explicit state machine with EXPIRED state
- Fail-closed by default (DENY when non-interactive)
- Audit trail captures all approval attempts

**Validation:** Does this fully address the gap?

---

### 2. Path Sandboxing (AC-SECURITY-006)

**Acceptance Criteria:**
```yaml
Use os.path.realpath() for all paths before sandbox check
Deny operations on symlinks/junctions outside WORKSPACE_ROOT
Normalize deny patterns: all absolute paths after realpath
Platform-specific: Windows junctions, Unix symlinks
```

**Review Questions:**
- Does `realpath()` resolve ALL link types? (hardlinks, junction points, reparse points?)
- What about NTFS alternate data streams (Windows)?
- Can deny patterns be bypassed via 8.3 short names (Windows)?
- What if `WORKSPACE_ROOT` itself is a symlink?
- How are relative vs absolute deny patterns normalized?

**Previous Gap (Round 1):**
> "Path sandboxing can be escaped via symlinks/junctions + pattern mismatch risk. A 'within workspace' path can resolve outside the boundary."

**Design Response:**
- Canonical path resolution with `realpath()` before sandbox check
- Explicit symlink/junction denial for out-of-workspace targets
- Deny patterns converted to absolute after canonicalization

**Validation:** Does this fully address symlink escape vectors?

---

### 3. Unicode Normalization (AC-ROUTE-004)

**Acceptance Criteria:**
```yaml
Apply Unicode NFKC normalization to all user intents
Strip zero-width characters (U+200B, U+FEFF, etc.)
Collapse whitespace: multiple spaces → single space
Normalize quotes/dashes: smart quotes → ASCII
Deterministic: same visual intent → same routing outcome
```

**Review Questions:**
- Does NFKC handle all Unicode confusables? (e.g., Cyrillic 'а' vs Latin 'a')
- What about emoji in intents? (Normalize or strip?)
- Are there locale-specific normalization issues?
- How does this interact with regex patterns in routing table?
- Can attackers use homoglyphs to bypass routing? (e.g., "рlan" with Cyrillic 'р')

**Previous Gap (Round 1):**
> "Threat model explicitly includes 'Hidden Unicode characters change intent,' but routing normalization only says lowercase + strip whitespace. No Unicode normalization (NFKC), no zero-width removal."

**Design Response:**
- Explicit NFKC normalization step
- Zero-width character stripping
- Whitespace collapse + quote/dash normalization

**Validation:** Does this fully address Unicode attack vectors?

---

### 4. PREFIX Tie-Breaking (AC-ROUTE-005)

**Acceptance Criteria:**
```yaml
If PREFIX lengths equal → use explicit priority field
If priority equal → fail at startup with conflict error
Extend conflict detection to cover PREFIX tie scenarios
Runtime never raises ambiguity (startup guarantees uniqueness)
```

**Review Questions:**
- What if two patterns have same prefix length AND same priority? (edge case)
- How are prefix lengths calculated? (byte length, codepoint length, grapheme length?)
- Does this handle multi-word prefixes correctly?
- What about case sensitivity in prefix matching?
- Can startup conflict detection be bypassed by dynamic pattern registration?

**Previous Gap (Round 1):**
> "PREFIX conflict handling incomplete. Spec picks max(..., key=len) and returns immediately, without tie-break path. Hidden non-determinism or 'first in list wins' behavior."

**Design Response:**
- Explicit priority fallback for equal-length prefixes
- Fail-fast at startup if priority also equal
- Runtime ambiguity impossible (startup validation guarantees uniqueness)

**Validation:** Does this eliminate all non-determinism?

---

### 5. Statistical Trigger Guards (AC-ROLLOUT-004)

**Acceptance Criteria:**
```yaml
Minimum sample size: 100 requests before triggers arm
Cold-start baseline: synthetic baseline for new orchestrators
Low-traffic handling: disable triggers if <10 requests/hour
Flapping detection: 3 consecutive breaches before rollback
```

**Review Questions:**
- Is 100 requests enough for statistical significance? (depends on error rate)
- What is the "synthetic baseline" for cold starts? (how is it calculated?)
- How does low-traffic threshold (10 req/hour) interact with canary 5% traffic?
- Can flapping detection be gamed? (e.g., 2 breaches, pause, 2 more breaches)
- What if baseline itself is unstable? (high variance scenarios)

**Previous Gap (Round 1):**
> "Rollout triggers lack minimum sample sizing + 'new orchestrator baseline' handling. No spec for minimum requests/events before triggers arm, nor baseline for brand-new orchestrators with no history."

**Design Response:**
- Explicit minimum sample size (100 requests)
- Synthetic baseline for cold-start orchestrators
- Low-traffic disabling to prevent false positives
- Flapping protection (3 consecutive breaches)

**Validation:** Does this prevent false-positive rollbacks?

---

## 🚨 Known Invalid Recommendations (DO NOT REPEAT)

### ❌ Invalid #1: "dir command requires shell=True"

**Why Invalid:**
- CORTEX uses `python -m src.tools.safe_file_lister` or `pwsh -Command Get-ChildItem`
- No shell=True needed; cross-platform alternatives exist

**Corrected Design:**
- AC-SECURITY-008 replaces 'dir' with python/pwsh wrappers

---

### ❌ Invalid #2: "Shadow mode side-effect control underspecified"

**Why Invalid:**
- ActionPolicyEngine already has DRY_RUN mode (not fully documented)
- This is a documentation gap, not a design gap

**Corrected Design:**
- Document DRY_RUN behavior in rollout spec (no new AC-ID needed)

---

### ❌ Invalid #3: "Argument validation underspecified"

**Why Invalid:**
- CORTEX uses incremental AC building via TDD
- Validation rules emerge during RED phase, not upfront

**Corrected Design:**
- AC-SECURITY-007 creates incremental validation registry (Phase 2)

---

## 📊 Scoring Guidance

### Point Allocation

| Category | Points | Current | Target | AC-IDs |
|----------|--------|---------|--------|--------|
| Approval Protocol | 10 | 0 | 10 | AC-SECURITY-005 |
| Path Sandboxing | 10 | 3 | 10 | AC-SECURITY-006 |
| Routing Determinism | 10 | 5 | 10 | AC-ROUTE-004, AC-ROUTE-005 |
| Command Execution | 10 | 7 | 10 | AC-SECURITY-008 |
| Rollout Triggers | 10 | 8 | 10 | AC-ROLLOUT-004 |
| Shadow Side-Effects | 5 | 3 | 5 | (Documentation) |
| **TOTAL** | **55** | **26** | **55** | **~83 → ~95+** |

### Score Calculation

```
Current Score = 83/100
Maximum Gain = +28 points (from 5 ACs + documentation)
Realistic Target = 95-97/100 (some edge cases may remain)
```

---

## 📝 Expected Output Format

```yaml
design_quality_score: XX / 100

summary: |
  Brief paragraph on overall design quality, focusing on security,
  determinism, and operational feasibility.

critical_issues:
  - issue: "Specific design gap"
    severity: CRITICAL | HIGH | MEDIUM | LOW
    impact: "What happens if this isn't fixed"
    evidence: "File:line reference or quote"
    recommendation: "Concrete fix (ideally points to existing or new AC-ID)"

high_issues:
  - issue: "..."
    # same format

medium_issues:
  - issue: "..."
    # same format

accepted_improvements:
  - ac_id: "AC-SECURITY-005"
    assessment: "Does this fully address the approval gap?"
    remaining_risks: ["List any remaining concerns"]

  - ac_id: "AC-SECURITY-006"
    assessment: "Does this fully address path traversal?"
    remaining_risks: ["List any remaining concerns"]

  # ... for all 5 new AC-IDs

recommendations:
  critical:
    - "Top 3 fixes with highest risk reduction"
  
  high:
    - "Important but not blocking"
  
  medium:
    - "Nice to have, not urgent"

things_not_to_change:
  - "One design decision that is correct and should NOT be altered"

long_term_direction:
  - "Strategic recommendation for future phases"
```

---

## 🎯 Success Criteria

Your review is successful if:

1. **Design score >= 95/100** (or clear path to get there)
2. **No critical security gaps** (approval, paths, commands, routing)
3. **Operational feasibility validated** (rollback triggers, minimum samples)
4. **No invalid recommendations** (see "Known Invalid Recommendations" section)
5. **Actionable feedback** (points to specific AC-IDs or new requirements)

---

## 🔄 Iteration Process

**If score < 95:**
1. Identify remaining gaps (critical/high severity only)
2. Propose new AC-IDs or refinements to existing ones
3. Estimate point gain per fix
4. Prioritize by risk reduction (highest first)

**If score >= 95:**
1. Validate all critical/high issues addressed
2. Document any remaining medium/low issues for Phase 2+
3. Confirm operational feasibility
4. Approve design for implementation

---

## 📞 Questions to Ask Yourself

Before submitting findings:

1. **Is this a design gap or implementation gap?** (Only design gaps matter)
2. **Would this cause a production incident?** (If no, probably low priority)
3. **Is there an existing AC-ID that addresses this?** (Check AC-INDEX.yaml first)
4. **Am I over-engineering?** (YAGNI principle applies)
5. **Is this contradicting the design or just "could be better"?** (Contradictions are critical)

---

## 🚀 Start Here

1. **Read `cx6-reviewer-guidance.md`** (10 minutes)
2. **Scan `AC-INDEX.yaml` lines 1-150** (context on new AC-IDs)
3. **Review `cx6-security-layer.yaml`** (focus on AC-SECURITY-005, AC-SECURITY-006)
4. **Review `cx6-routing-spec.yaml`** (focus on AC-ROUTE-004, AC-ROUTE-005)
5. **Review `cx6-rollout-lifecycle.yaml`** (focus on AC-ROLLOUT-004)
6. **Scan `cx6-architecture-detailed.yaml`** (system overview)
7. **Write findings** (use format above)

---

**Total Review Time Estimate:** 90-120 minutes  
**Output:** YAML file with findings + score + recommendations  

---

**Ready? Begin your review. Focus on security gaps, logical contradictions, and operational feasibility.**
