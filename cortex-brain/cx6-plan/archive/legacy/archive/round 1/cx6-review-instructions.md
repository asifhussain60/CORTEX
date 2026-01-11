# CORTEX 6.0 Design Review Instructions for GPT

**Purpose:** Prevent false positive findings and ensure accurate design critique  
**Version:** 1.0.0  
**Created:** 2026-01-10  
**Author:** Asif Hussain

---

## 🎯 Your Role as Reviewer

You are reviewing **DESIGN SPECIFICATIONS** for CORTEX 6.0, a production-grade AI orchestration system. Your goal is to identify **logical gaps, security risks, scalability concerns, and architectural inconsistencies** — NOT to flag features as "missing" when they are intentionally future work.

---

## ✅ What TO Review and Flag

### 1. Logical Inconsistencies
- **Data flows that don't connect:** Component A outputs X, Component B expects Y
- **Circular dependencies:** Feature A depends on B, B depends on A
- **Impossible sequences:** Step 3 requires data from Step 5

**Example valid finding:**
> "ActionPolicyEngine validates paths, but StateManager doesn't invoke it before file writes. Bypass possible."

---

### 2. Security Gaps
- **Missing trust boundaries:** Operations that should be sandboxed but aren't
- **Credential exposure risks:** Secrets could leak in logs, errors, or responses
- **Insufficient validation:** User input accepted without sanitization

**Example valid finding:**
> "Command execution allowlist includes `git` but doesn't restrict arguments. Injection possible via `--upload-pack='malicious command'`."

---

### 3. Scalability Concerns
- **Unspecified limits:** No guidance on "how much is too much"
- **Resource exhaustion:** Unbounded queues, memory leaks, disk space
- **Concurrency issues:** Race conditions, deadlocks, lack of locking

**Example valid finding:**
> "Audit logger uses SQLite with 1000-entry buffer, but no backpressure strategy if write speed < log rate. Buffer overflow risk."

---

### 4. Operational Risks
- **Unclear failure modes:** What happens when component X fails?
- **No rollback mechanism:** Destructive operation with no undo
- **Monitoring gaps:** Critical metrics not tracked

**Example valid finding:**
> "Staged rollout promotes to ACTIVE after 48h, but no specification for rollback if post-promotion issues discovered."

---

### 5. Ambiguity in Specifications
- **Underspecified behavior:** "System validates input" (how? what rules?)
- **Conflicting statements:** Document says A in one section, B in another
- **Missing edge cases:** What if file doesn't exist? What if API returns 429?

**Example valid finding:**
> "Routing semantics say 'longest prefix wins' but example shows priority override. Which takes precedence?"

---

## ❌ What NOT to Flag (Known Design Decisions)

### 1. Features Marked "DESIGNED" Without Implementation
**Status labels you'll see:**
- `status: "DESIGNED"` → Accepted requirement, not yet built
- `status: "IMPLEMENTED"` → Code exists
- `status: "PARTIAL"` → Partially built

**DO NOT flag:**
- "ActionPolicyEngine is not implemented" (it's DESIGNED, intentionally future work)
- "DeterministicRoutingEngine is missing" (it's DESIGNED)

**DO flag:**
- "ActionPolicyEngine spec says it validates paths, but doesn't define validation rules" (gap in DESIGN)

---

### 2. SQLite for Audit/State Storage
**Intentional decision:**
- SQLite is the CHOSEN database for single-instance deployments
- WAL mode provides concurrency safety
- Specified scale limit: 10,000 operations/day
- Migration plan exists for >10k ops/day (PostgreSQL)

**DO NOT flag:**
- "SQLite can't handle high concurrency" (addressed via WAL + scale limits)
- "Should use PostgreSQL" (that's Phase 2, after hitting limits)

**DO flag:**
- "No specification for what happens at 10,001 operations/day" (valid operational concern)

---

### 3. Routing Table Duality (CORTEX.prompt.md vs copilot-instructions.md)
**Intentional architecture:**
- `CORTEX.prompt.md` = **SOURCE OF TRUTH** (runtime routing table)
- `.github/copilot-instructions.md` = **STABLE REFERENCE** (GitHub Copilot UI instructions)

**DO NOT flag:**
- "Two files contain routing information, which is authoritative?" (answered in SPEC-019)
- "Routing table should be in one place" (it is, with a documented secondary reference)

**DO flag:**
- "No sync mechanism documented between the two files" (valid if true)

---

### 4. Import-Time Registration (Transitioning to Manifest-Based)
**Known legacy pattern:**
- Current: `@orchestrator_registry` decorator (import-time)
- Target: Manifest-based discovery (AC-ROUTE-002)
- Transition: CORE-021 allows legacy until AC-MIGRATE-001

**DO NOT flag:**
- "Import-time registration is fragile" (known, being replaced)
- "Should use explicit manifest" (that's the target, in progress)

**DO flag:**
- "No migration timeline specified" (if true, that's a gap)

---

### 5. Async Logging with Overflow Handling
**Intentional design:**
- Audit logger uses async buffered writes (1000 entries)
- Overflow policy: Drop oldest DEBUG/TRACE, keep ERROR+
- Flush interval: 5 seconds

**DO NOT flag:**
- "Async logging could lose logs on crash" (addressed via flush interval + retention policy)

**DO flag:**
- "What happens if 1000 ERROR logs arrive before flush?" (valid edge case)

---

### 6. Phase-Based Implementation (Not Everything is Built Now)
**CORTEX 6.0 is 4 phases:**
1. **Phase 1 (Foundation):** Audit, Governance, State, Security — **IN PROGRESS**
2. **Phase 2 (Orchestration Core):** MasterOrchestrator, TDD-Master, Routing — **NOT STARTED**
3. **Phase 3 (Feature Orchestrators):** ADO, Vacuum, Investigation — **NOT STARTED**
4. **Phase 4 (Intelligence):** LLM Classifier, Knowledge Graph — **NOT STARTED**

**DO NOT flag:**
- "MasterOrchestrator is not implemented" (Phase 2, not started)
- "LLM Intent Classifier is missing" (Phase 4, not started)

**DO flag:**
- "Phase 1 depends on Phase 2 component (cycle)" (architectural problem)

---

## 📋 Review Checklist (Use This)

For each document, ask:

### Architecture
- [ ] Are data flows complete and consistent?
- [ ] Are dependencies acyclic (no circular deps)?
- [ ] Are integration points specified?

### Security
- [ ] Are trust boundaries clearly defined?
- [ ] Are attack surfaces identified and mitigated?
- [ ] Are secrets handled safely (no logs, use keyring)?

### Scalability
- [ ] Are scale limits specified (requests/day, file sizes, etc.)?
- [ ] Are concurrency hazards addressed (locks, atomic writes)?
- [ ] Are resource limits enforced (buffer sizes, retention)?

### Operations
- [ ] Are failure modes documented?
- [ ] Are rollback mechanisms specified?
- [ ] Are monitoring/alerting requirements defined?

### Clarity
- [ ] Are ambiguous terms defined?
- [ ] Are conflicting statements resolved?
- [ ] Are edge cases handled?

---

## 🚫 Anti-Patterns to Avoid in Your Review

### ❌ Bad Finding (False Positive)
> "The DeterministicRoutingEngine is not implemented. This is a critical gap."

**Why bad:** Document says `status: "DESIGNED"`. It's future work, not a gap.

### ✅ Good Finding (True Positive)
> "The DeterministicRoutingEngine spec says 'fail fast on ambiguity' but doesn't define what constitutes an ambiguity. Is it same match_type + priority? Same pattern text? Needs clarification."

**Why good:** Points to gap in DESIGN logic, not missing implementation.

---

### ❌ Bad Finding (Ignores Context)
> "SQLite is unsuitable for production. Should use PostgreSQL."

**Why bad:** Document explicitly states SQLite is intentional, with scale limits and migration plan.

### ✅ Good Finding (Highlights Risk)
> "Scale limits specify 10k ops/day, but no monitoring alert configured to warn when approaching limit. Risk of silent overload."

**Why good:** Identifies operational gap within the chosen architecture.

---

### ❌ Bad Finding (Misunderstands Workflow)
> "CORTEX.prompt.md and copilot-instructions.md both define routing. Duplicate data, risk of drift."

**Why bad:** Document explains they serve different purposes (runtime vs UI reference).

### ✅ Good Finding (Catches Drift Risk)
> "CORTEX.prompt.md is updated per orchestrator (frequent), copilot-instructions.md only on major changes. No validation that references in copilot-instructions.md remain accurate. Drift risk."

**Why good:** Identifies maintenance gap that could cause issues over time.

---

## 📊 Scoring Guidance

When you provide a **Design Quality Score**, consider:

### High Score (80-100): Well-Specified, Minimal Gaps
- All data flows complete
- Security boundaries clear
- Scalability limits defined
- Failure modes documented
- Testable and implementable

### Medium Score (60-79): Solid Core, Some Ambiguities
- Major flows specified, minor gaps
- Security addressed but some details missing
- Scale considerations present but incomplete
- Some edge cases undefined

### Low Score (40-59): Concerning Gaps
- Data flows incomplete or inconsistent
- Security boundaries unclear
- Scalability not addressed
- Operational risks unmitigated

### Failing Score (<40): Fundamental Issues
- Logical inconsistencies (circular deps, impossible sequences)
- Security gaps (no validation, secrets exposed)
- No failure mode handling
- Unimplementable as specified

---

## 🎯 Example: How to Review a Section

### Section from `cx6-security-layer.yaml`:
```yaml
action_types:
  DELETE:
    default_policy: "DENY (explicit approval required)"
    authorization_required: "ALL delete operations"
```

### ❌ Bad Review:
> "DELETE action policy is not implemented."

**Why bad:** This is a design spec, not implementation critique.

### ✅ Good Review:
> "DELETE requires approval, but no specification for approval mechanism. Is it interactive prompt? Pre-approved allowlist? Timeout if no response? Needs clarification."

**Why good:** Points to gap in design logic, not missing code.

---

## 📝 Your Deliverable Format

Provide findings in this structure:

```
Design Quality Score: X / 100

Summary: [2-3 sentence overview]

Findings (concrete issues only):

1) [Issue Title]
   Issue: [What's wrong]
   Impact: [Why it matters]
   Evidence: [Where you found it, quote document]
   Severity: [Critical/High/Medium/Low]

2) ...

Recommendations (Critical/High only):
A) [Fix title]
   Fix: [Specific action]
   Trade-offs: [What it costs]
   Redesign vs patch: [Is it architectural or tactical?]

Improvement Summary:
- Top 3 fixes with highest risk reduction
```

---

## ✅ Final Checklist Before Submitting Review

- [ ] I flagged DESIGN GAPS, not missing implementations
- [ ] I checked if "missing" features are marked DESIGNED (future work)
- [ ] I considered documented design decisions (SQLite, routing duality, etc.)
- [ ] I provided specific evidence (quotes, file names, section references)
- [ ] I suggested concrete fixes, not just "do better"
- [ ] I assigned severity based on production impact, not personal preference

---

## 🚀 Now Review These Documents

1. **cx6-architecture-detailed.yaml** — Full system architecture
2. **cx6-security-layer.yaml** — ActionPolicyEngine and trust boundaries
3. **cx6-routing-spec.yaml** — Deterministic routing semantics
4. **cx6-rollout-lifecycle.yaml** — Staged rollout and automated rollback
5. **cx6-implementation-status.yaml** — What's built vs designed

**Focus on:** Logical consistency, security, scalability, operations, clarity.

**Ignore:** Features marked DESIGNED, known decisions documented in review guidance above.

Good luck! 🎯
