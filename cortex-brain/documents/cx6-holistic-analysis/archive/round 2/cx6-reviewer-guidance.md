# CORTEX 6.0 Design Review - Reviewer Guidance

**Document Purpose:** Guide external reviewers away from invalid recommendations  
**Target Audience:** GPT-4, Claude, or human reviewers evaluating CORTEX 6 design  
**Version:** 1.0.0  
**Created:** 2026-01-10  
**Author:** Asif Hussain  

---

## 📋 Review Scope & Expectations

### What You're Reviewing

You are reviewing **DESIGN SPECIFICATIONS** for CORTEX 6.0, a production-grade AI orchestration system with:
- 4-tier governance architecture (Tier 0-3)
- Audit infrastructure with SQLite + JSONL storage
- Action security layer for file/command operations
- Deterministic routing engine
- Staged rollout system (REGISTERED → SHADOW → CANARY → ACTIVE)

### What This Is NOT

This is **NOT** a code review. You are evaluating:
- ✅ **Design completeness** - Are there logical gaps?
- ✅ **Security coverage** - Are attack surfaces addressed?
- ✅ **Operational feasibility** - Can this be built and operated?

You are **NOT** evaluating:
- ❌ Implementation status (AC-IDs are intentionally not started)
- ❌ Code quality (no code exists yet)
- ❌ Test coverage (tests will be written during TDD)

---

## 🚨 Common Pitfalls to AVOID

### Pitfall #1: Flagging "Missing Implementation"

**WRONG:**
> "AC-SECURITY-001 has no implementation. This is a critical gap."

**CORRECT:**
> "AC-SECURITY-001's design lacks specificity around approval timeout behavior in distributed scenarios."

**Why:** All AC-IDs are `status: not_started`. That's by design. We follow **incremental AC building** - requirements emerge during implementation, not upfront.

---

### Pitfall #2: Demanding Exhaustive Upfront Specification

**WRONG:**
> "Argument validation is underspecified. You must define validation rules for ALL placeholders before implementation."

**CORRECT:**
> "Consider documenting a few high-risk placeholder patterns (e.g., git refs) as examples. Full validation rules can emerge incrementally."

**Why:** CORTEX philosophy is **YAGNI + TDD**. We solve problems when they're actually problems, not preemptively. Premature specification leads to over-engineering.

---

### Pitfall #3: Assuming No Existing Infrastructure

**WRONG:**
> "Shadow mode has no side-effect controls. This is a critical gap."

**CORRECT:**
> "Clarify whether ActionPolicyEngine's existing DRY_RUN mode applies to SHADOW, or if a new mechanism is needed."

**Why:** CORTEX 6.0 builds on existing components from CORTEX 4.0/5.0. Check git history and recovery notes before assuming something doesn't exist.

---

### Pitfall #4: Overcomplicating Simple Problems

**WRONG:**
> "The 'dir' command requires shell=True. You must redesign command execution to support shell builtins."

**CORRECT:**
> "Consider removing 'dir' from the allowlist and using cross-platform alternatives like 'python -m src.tools.safe_file_lister' or 'pwsh -Command Get-ChildItem'."

**Why:** Simple problems have simple solutions. Don't force architectural changes when a workaround exists.

---

## 🎯 What to Focus On

### HIGH-VALUE Review Areas

1. **Logical Contradictions**
   - Example: "Threat model mentions Unicode attacks, but normalization doesn't handle Unicode."
   - **This is valid!** Design says one thing, implementation plan says another.

2. **Security Escape Hatches**
   - Example: "Path sandboxing checks `abspath` but doesn't resolve symlinks."
   - **This is valid!** Symlink traversal is a real attack vector.

3. **Operational Feasibility**
   - Example: "Rollback triggers use 5-minute windows without minimum sample sizing. This will false-positive in low-traffic scenarios."
   - **This is valid!** Design doesn't account for edge cases.

4. **Missing Approval Mechanisms**
   - Example: "WRITE requires 'interactive approval' but no timeout, authentication, or non-interactive behavior defined."
   - **This is valid!** Critical control is underspecified.

---

### LOW-VALUE Review Areas (Skip These)

1. **Missing Tests**
   - We're in **design phase**. Tests come during TDD (Phase 1-2).

2. **Implementation Gaps**
   - AC-IDs are placeholders. Implementation happens incrementally.

3. **Over-Specifying Edge Cases**
   - Don't demand validation rules for every possible input. We use TDD to discover edge cases.

4. **Tool/Library Choices**
   - Don't prescribe specific libraries unless there's a design-level reason (e.g., security).

---

## 🧠 CORTEX Philosophy Reminders

### Incremental AC Building

**Design Approach:**
- **NOT:** Write 100-page specification upfront
- **YES:** Define acceptance criteria, implement via TDD, refine as needed

**Why:** Requirements drift. We build what's needed, when it's needed.

---

### YAGNI (You Ain't Gonna Need It)

**Design Approach:**
- **NOT:** "What if we need to support 10 languages? Design for that now."
- **YES:** "We support Python + JavaScript today. Add others when teams ask."

**Why:** Premature optimization wastes time. Solve actual problems.

---

### Fail-Closed Security

**Design Approach:**
- **NOT:** "Default to allow, add denylists later."
- **YES:** "Default to deny, add allowlists explicitly."

**Why:** Security failures should block operations, not permit them.

---

## 📐 Scoring Calibration

### Current Score: 83/100

**Where Points Were Lost:**
- **Approval Protocol Gap (-10):** No mechanism for "interactive approval REQUIRED"
- **Path Sandboxing Holes (-7):** Symlink traversal not addressed
- **Routing Non-Determinism (-5):** Unicode normalization missing
- **Command Execution Flaw (-3):** 'dir' allowlist without shell strategy
- **Shadow Side-Effects (-2):** Documentation gap (DRY_RUN exists but not documented)

---

### Target Score: 95+

**How to Get There:**
1. **Fix approval protocol** (+10 points) → AC-SECURITY-005
2. **Fix path sandboxing** (+7 points) → AC-SECURITY-006
3. **Fix routing normalization** (+5 points) → AC-ROUTE-004
4. **Fix PREFIX tie-breaking** (+1 point) → AC-ROUTE-005
5. **Fix rollout triggers** (+2 points) → AC-ROLLOUT-004
6. **Fix command execution** (+3 points) → AC-SECURITY-008

**Total:** 83 + 28 = 111 → Capped at 100, realistically 95-97

---

## 🚀 Recommended Review Process

### Step 1: Read Threat Model (5 min)

**Files:**
- `cx6-security-layer.yaml` (lines 1-150)
- Focus on: attack_surfaces, trust_boundaries

**Question:** Are all attack surfaces addressed by AC-IDs?

---

### Step 2: Check Design Contradictions (10 min)

**Files:**
- `cx6-routing-spec.yaml`
- `cx6-rollout-lifecycle.yaml`

**Question:** Does the spec say one thing but design another?

**Example:**
- Threat model: "Hidden Unicode characters change intent"
- Routing algorithm: `lower().strip()` (no Unicode normalization)
- **Contradiction detected!**

---

### Step 3: Validate Security Controls (15 min)

**Files:**
- `cx6-security-layer.yaml` (full read)

**Question:** Can an attacker bypass these controls?

**Test Cases:**
- Symlink escape: `ln -s /etc/passwd cortex-brain/data.txt` → blocked?
- Command injection: `git branch --format="%(refname); rm -rf /"` → blocked?
- Approval bypass: Non-interactive mode defaults to ALLOW? → FAIL-CLOSED?

---

### Step 4: Assess Operational Feasibility (10 min)

**Files:**
- `cx6-rollout-lifecycle.yaml`

**Question:** Will this work in production?

**Scenarios:**
- New orchestrator (no 7-day baseline): How do triggers work?
- Low-traffic intent (<10 requests/day): Do triggers false-positive?
- Rollback flapping: Can orchestrator flip-flop between ACTIVE/CANARY?

---

## 📝 Review Output Format

### Accepted Format

```yaml
findings:
  - issue: "Approval timeout not defined for non-interactive runs"
    severity: CRITICAL
    impact: "Deadlock or bypass depending on implementation choice"
    evidence: "cx6-security-layer.yaml:234 says 'approval REQUIRED' but no timeout"
    recommendation: "Define timeout (e.g., 5 min) and default behavior (fail-closed)"

  - issue: "PREFIX tie-breaking incomplete"
    severity: HIGH
    impact: "Non-deterministic routing for same-length patterns"
    evidence: "cx6-routing-spec.yaml:123 uses max(..., key=len) without priority fallback"
    recommendation: "Add explicit priority tie-break, fail at startup if still ambiguous"
```

---

### Rejected Format

```yaml
findings:
  - issue: "AC-SECURITY-001 not implemented"
    severity: CRITICAL
    recommendation: "Implement ActionPolicyEngine before Phase 1 ends"
```

**Why Rejected:** This is a project management issue, not a design gap.

---

## 🎓 Example: Good vs Bad Feedback

### ❌ BAD Feedback

> "The system lacks a comprehensive error handling strategy. You should define exception hierarchies, retry logic, circuit breakers, and fallback mechanisms before implementation."

**Why Bad:**
- Too broad (no specific gap identified)
- Premature optimization (demands full strategy upfront)
- Ignores existing work (custom exceptions already defined in SPEC-011)

---

### ✅ GOOD Feedback

> "AC-SECURITY-001 states 'Policy evaluation <10ms' but doesn't specify behavior when evaluation exceeds this threshold. Options: fail-open (risky), fail-closed (safe but may block legit ops), or queue for async approval. Consider documenting the chosen strategy."

**Why Good:**
- Specific gap (timeout behavior)
- Security-relevant (fail-open vs fail-closed)
- Actionable (choose one of three options)
- Acknowledges tradeoffs

---

## 🔍 Red Flags in Your Own Review

If you find yourself writing these, **STOP** and reconsider:

1. **"This should use [specific library/framework]"**
   - Unless security-critical, implementation choices are not design gaps.

2. **"You need to specify [exhaustive list] before proceeding"**
   - CORTEX uses incremental refinement. Don't demand waterfall.

3. **"This is missing implementation"**
   - It's a design review. Implementation is not the goal.

4. **"Consider adding [complex feature]"**
   - YAGNI. Don't over-engineer. Solve actual problems.

---

## 📊 Self-Check: Are You Adding Value?

Ask yourself after each finding:

1. **Is this a design gap?** (Not implementation status)
2. **Is this a security risk?** (Not a code quality issue)
3. **Is this operationally feasible?** (Not a theoretical edge case)
4. **Is this contradictory?** (Not just "could be better")

If you answered **NO** to all four, your feedback is likely low-value.

---

## 🎯 Final Reminder: CORTEX Is Production-Focused

**CORTEX 6.0 is not:**
- An academic research project
- A proof-of-concept
- A startup MVP

**CORTEX 6.0 is:**
- A production-grade AI orchestration system
- Used by teams to build software
- Required to fail safely, not fail fast

**Your review should reflect this context.**

---

## 📞 Questions?

If you're unsure whether a finding is valid, ask yourself:

1. **Would this cause a production incident?** → Valid
2. **Would this confuse a team member?** → Valid
3. **Would this violate a security boundary?** → Valid
4. **Is this a "nice to have"?** → Low priority

**When in doubt, frame it as a question rather than a demand:**
- ❌ "You must define X before Y"
- ✅ "Consider whether X needs clarification for Y scenarios"

---

**Review with this guidance, and your feedback will be 10x more valuable.**

---

## 🔗 Cross-References

- **Design Specs:** `cx6-architecture-detailed.yaml`, `cx6-security-layer.yaml`, `cx6-routing-spec.yaml`, `cx6-rollout-lifecycle.yaml`
- **AC Registry:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
- **Core Rules:** `cortex-brain/tier0/governance/core-rules.yaml`
- **Progress Tracker:** `cortex-brain/tier1/tracking/progress-tracker.json`

---

**End of Reviewer Guidance**
