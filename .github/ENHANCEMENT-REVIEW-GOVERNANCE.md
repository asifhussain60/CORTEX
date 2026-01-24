# CORTEX Governance Enhancement Review
**Version:** 1.0 | **Updated:** 2026-01-24 | **Authority:** Strategic Review | **Status:** ✅ RECOMMENDATIONS READY

---

## 📋 Executive Summary

This document reviews all existing CORTEX prompts and agents (`CORTEX.md`, `cortex-builder.md`, `cortex-review.md`, `cortex-review-agents.md`, `cortex-planner.md`, and all `.prompt.md` files) in light of the NEW **Enforcement Architecture** and provides enhancement recommendations.

**Key Finding:** Existing agent ecosystem is well-designed but needs enhancements to integrate with the new enforcement layer and improve cross-agent coordination.

---

## 🔍 Review Matrix

| Component | Current State | Enforcement Integration | Enhancement Recommendation | Priority |
|-----------|---------------|------------------------|------------------------------|----------|
| `CORTEX.prompt.md` | ✅ Updated | ✅ Integrated (Stage 3) | Add enforcement cmdlets | ✅ HIGH |
| `cortex-builder.prompt.md` | ✅ Ready | ⚠️ Reference needed | Link to enforcement stage | 🟡 MEDIUM |
| `cortex-review.prompt.md` | ✅ Ready | ⚠️ Reference needed | Post-execution validation | 🟡 MEDIUM |
| `cortex-enforcement.prompt.md` | ✅ NEW | ✅ Complete | Ready for deployment | ✅ HIGH |
| `cortex-enforcement-agents.md` | ✅ NEW | ✅ Complete | Ready for deployment | ✅ HIGH |
| `cortex-total-recall.prompt.md` | ✅ Ready | ⚠️ Needs enhancement | Add enforcement discovery | 🟠 LOW |
| `cortex-doc.prompt.md` | ✅ Ready | ⚠️ SSOT sync needed | Document enforcement rules | 🟠 LOW |
| `cortex-git-commit.prompt.md` | ✅ Ready | ✅ Related (CORE-026) | Strengthen checkpoint enforcement | 🟡 MEDIUM |
| `.github/agents/CORTEX.md` | ✅ Ready | ⚠️ Update routing table | Add enforcement routing | 🟡 MEDIUM |
| `.github/agents/cortex-builder.md` | ✅ Ready | ⚠️ Reference enforcement | Link approval → enforcement | 🟡 MEDIUM |
| `.github/agents/cortex-planner.md` | ✅ Ready | ⚠️ Add compliance checks | Integrate phase readiness | 🟡 MEDIUM |
| `.github/agents/cortex-review-agents.md` | ✅ Ready | ✅ Reference OK | No changes needed | 🔵 LOW |

---

## 📝 Detailed Enhancement Recommendations

### 1. `cortex-builder.prompt.md` - IMPLEMENT Protocol Enhancement

**Current State:**
- Implements TDD RED→GREEN→REFACTOR
- Displays DoR before implementation
- References CORE-008, CORE-011, CORE-012, CORE-026, CORE-027

**Enhancement:**
Add reference to Stage 3 enforcement after DoR approval:

**Add after DoR Display section:**
```markdown
### Stage 3: Governance Enforcement Check

After user approval (Stage 2), the following enforcement checks run automatically:

| Check | Rule | Blocks | Escalates |
|-------|------|--------|-----------|
| Test file exists | CORE-008 | ✅ | - |
| Type hints present | CORE-011 | ✅ | - |
| Docstrings complete | CORE-012 | ✅ | - |
| Git checkpoint ready | CORE-026 | ✅ | - |

If any TIER 0 check fails → Operation blocked (see `/enforce` for details)
If any TIER 1 check fails → Operation escalated (proceed with warning)

Reference: `cortex-enforcement.prompt.md`, `cortex-enforcement-agents.md`
```

**Action:** Link to enforcement agents in docstring

---

### 2. `cortex-review.prompt.md` - Post-Execution Validation Enhancement

**Current State:**
- Runs 8 specialized review agents
- Performs comprehensive code analysis
- Governance agent (GOV) checks CORE rules

**Enhancement:**
Position review agents as POST-ENFORCEMENT validators:

**Add new section:**
```markdown
## 🔄 Relationship to Enforcement Agents

### Enforcement vs. Review (Key Difference)

**Enforcement Agents (Stage 3 - Pre-Execution):**
- ✅ PREVENT violations before code runs
- ✅ Block TIER 0 violations (non-negotiable)
- ✅ Run once before operation starts
- ✅ Fast fail (token efficient)

**Review Agents (Post-Execution):**
- 🔍 ANALYZE code after implementation
- 🔍 Catch design issues, brittleness, technical debt
- 🔍 Comprehensive audit (8 agents, 60 minutes)
- 🔍 Recommend improvements

### Recommended Workflow

```
IMPLEMENT → Enforcement (blocks if violation) → Execute → Review (analyzes)
```

- Enforcement: "Do you have a test file?" (BLOCK if no)
- Review: "Is your code brittle? Does it handle edge cases?" (ANALYZE)
```

**Action:** Add relationship diagram showing enforcement → implementation → review flow

---

### 3. `cortex-total-recall.prompt.md` - Enforcement Discovery Enhancement

**Current State:**
- Discovers all production-ready components
- Maps entry points for orchestrators
- Validates production readiness

**Enhancement:**
Add enforcement agent discovery:

**Add new command:**
```markdown
| `/recall-enforcement` | List enforcement agents | 3 agents with rules |
| `/recall-enforcement-rules` | Show all enforced rules | TIER 0 + TIER 1 |
| `/recall-governance-status` | Governance compliance | Violations and statistics |
```

**Add new section:**
```markdown
## 🛡️ Enforcement Components

### Enforcement Orchestrator
- **Location:** `cortex/orchestrators/core/enforcement_orchestrator.py` (to be created)
- **Authority:** `cortex_brain/tier0/governance/`, `cortex_brain/tier1/acceptance/`
- **Stage:** 3 (between DoR approval and domain orchestrator delegation)

### Enforcement Agents (3 Total)

| Agent | Rules | Authority |
|-------|-------|-----------|
| GovernanceEnforcementAgent | CORE-008, 011, 012, 013, 029 | tier0/governance/ |
| SecurityCheckpointAgent | CORE-026, 025, 027 | tier0/governance/ |
| ComplianceValidationAgent | TIER-1-001 through 004 | tier1/acceptance/ |

### Discovery Command
```python
# Find enforcement components
agent = TotalRecallAgent()
enforcement = agent.recall_enforcement()
# Returns: agents, rules, authority documents, integration points
```

**Action:** Add enforcement discovery commands and section

---

### 4. `cortex-doc.prompt.md` - SSOT Governance Documentation Sync

**Current State:**
- Auto-discovers components
- Generates documentation
- Validates mkdocs site

**Enhancement:**
Ensure enforcement rules are documented:

**Add validation check:**
```markdown
### Governance Rule Documentation (NEW)

All TIER 0 and TIER 1 enforcement rules MUST be:
1. Documented in `docs/governance/`
2. Linked from enforcement prompt
3. Referenced in phase readiness checklist
4. Included in DoR displays

Validation:
- [ ] `/doc-governance` generates CORE-001 through CORE-029 reference
- [ ] `/doc-enforcement` generates enforcement agent guide
- [ ] Links validated (no 404s)
```

**Action:** Add governance documentation validation section

---

### 5. `cortex-git-commit.prompt.md` - Checkpoint Enforcement Enhancement

**Current State:**
- Pre-commit validation (SSOT, file placement)
- Checkpoint creation (CORE-026)
- Audit trail logging (CORE-027)

**Enhancement:**
Strengthen checkpoint enforcement integration:

**Add section:**
```markdown
## 🔐 Integration with Enforcement Layer

### Checkpoint as Enforcement Prerequisite

CORE-026 (Git Checkpoint) is enforced by **SecurityCheckpointAgent** before:
- IMPLEMENT operations (TDDOrchestrator)
- FIX operations (FixHandler)
- REFACTOR operations (RefactoringOrchestrator)
- DEPLOY operations (GitOrchestrator)

### Workflow

```
1. User issues: /implement {feature}
2. CORTEX: DisplayDoR → Get approval
3. CORTEX: SecurityCheckpointAgent runs
   - Checks: Is git clean? Can checkpoint be created?
   - If YES: Creates checkpoint automatically
   - If NO: BLOCKS with "create checkpoint first"
4. If checkpoint passes: Route to TDDOrchestrator
```

### Manual Checkpoint (When Needed)

```bash
# If enforcement blocks due to uncommitted changes
git commit -m "checkpoint: before AC-IMPL-001"
```
```

**Action:** Add checkpoint enforcement workflow and auto-checkpoint on first pass

---

### 6. `.github/agents/CORTEX.md` - Master Agent Routing Enhancement

**Current State:**
- Intent routing table (8 intents → 8 orchestrators)
- DoR display format
- LENS protocol

**Enhancement:**
Add enforcement orchestrator to routing table:

**Update Intent Routing Table:**
```markdown
| Intent | Orchestrator | Pre-Execution Stage |
|--------|--------------|-------------------|
| (Any) | EnforcementOrchestrator | ✅ Stage 3 (before domain orchestrator) |
| IMPLEMENT | TDDOrchestrator | After enforcement pass |
| FIX | IntentRouter → FixHandler | After enforcement pass |
| ... | ... | ... |
```

**Add new section:**
```markdown
## 🛡️ Stage 3: Rule Enforcement (NEW)

**Before delegating to domain orchestrator, ALWAYS run:**

```python
enforcement_result = self._enforcement_orchestrator.execute(
    intent_type=intent.type,
    context=request_context
)

if enforcement_result.blocked:
    return self._report_violation(enforcement_result)
```

**Enforcement agents check:**
- TIER 0: Blocking rules (TDD, type hints, docstrings, checkpoints)
- TIER 1: Escalation rules (phase readiness, test coverage, dependencies)

**Reference:** `cortex-enforcement.prompt.md`, `cortex-enforcement-agents.md`
```

**Action:** Add enforcement stage to CORTEX.md routing table and protocol

---

### 7. `.github/agents/cortex-builder.md` - Builder Agent Enhancement

**Current State:**
- Response header format
- DoR display
- TDD cycle explanation

**Enhancement:**
Link enforcement stage to builder workflow:

**Add section after DoR Display:**
```markdown
## ⚠️ Stage 3: Governance Enforcement (Automatic)

Before implementation starts, the **EnforcementOrchestrator** runs automatically:

1. **GovernanceEnforcementAgent** checks:
   - ✅ Test file exists (CORE-008)
   - ✅ Type hints will be required (CORE-011)
   - ✅ Docstrings will be required (CORE-012)

2. **SecurityCheckpointAgent** checks:
   - ✅ Git checkpoint ready (CORE-026)

3. **ComplianceValidationAgent** checks:
   - ⚠️ Phase dependencies met
   - ⚠️ Test coverage adequate

If any TIER 0 check fails → **OPERATION BLOCKED** (fix and retry)
If any TIER 1 check fails → **WARNING ESCALATED** (proceed with caution)

See: `cortex-enforcement.prompt.md` for enforcement details
```

**Action:** Add enforcement stage reference to TDD workflow

---

### 8. `.github/agents/cortex-planner.md` - Phase Readiness Enhancement

**Current State:**
- Shows phase status
- Checks phase readiness
- Tracks progress

**Enhancement:**
Integrate enforcement compliance into readiness checks:

**Add to Readiness Checklist:**
```markdown
| Check | Requirement | Enforcer |
|-------|-------------|----------|
| Dependencies | All required phases COMPLETED | ComplianceValidationAgent |
| Prerequisites | Required components exist | ComplianceValidationAgent |
| Audit Trail | Previous phase verified | SecurityCheckpointAgent |
| Governance | CORE rules loaded | GovernanceEnforcementAgent |
| Workspace | Git clean | SecurityCheckpointAgent |
| Enforcement | All Tier 0 checks pass | EnforcementOrchestrator |
```

**Add new command:**
```markdown
| `/phase-readiness-enforce {phase}` | Check enforcement compliance | Enforcement agents |
```

**Action:** Integrate enforcement compliance into phase readiness checks

---

### 9. `.github/agents/cortex-review-agents.md` - Review Agent Enhancement

**Current State:**
- 8 specialized review agents (BRIT, HALL, GOV, etc.)
- Governance agent checks CORE rules

**Enhancement:**
Clarify relationship between Review Agents and Enforcement:

**Add new section:**
```markdown
## 🔄 Relationship to Enforcement Agents (NEW)

### Key Difference

| Aspect | Review Agents | Enforcement Agents |
|--------|---------------|-------------------|
| **When** | After implementation | Before execution |
| **Function** | Analyze code quality | Prevent violations |
| **Blocking** | Recommendations only | TIER 0 violations block |
| **Speed** | Comprehensive (60 min) | Fast (< 5 sec) |
| **Scope** | Design, brittleness, debt | CORE rules only |

### Workflow

```
Code → Enforcement (blocks violations) → Review (analyzes quality)
```

### Agent 3: Governance (GOV) - UPDATED

Now works **WITH** enforcement agents:

**Pre-execution (Enforcement):**
- GovernanceEnforcementAgent checks CORE-008, 011, 012, 013

**Post-execution (Review):**
- GOV agent audits full code for:
  - Overall governance compliance
  - Complex governance scenarios
  - Pattern violations
  - Best practices alignment

Reference: `cortex-enforcement-agents.md`
```

**Action:** Add relationship diagram and clarification section

---

## 🎯 Implementation Priority

### Phase 1 (IMMEDIATE - Ready Now)
- ✅ Deploy `cortex-enforcement.prompt.md` (READY)
- ✅ Deploy `cortex-enforcement-agents.md` (READY)
- ✅ Update `CORTEX.prompt.md` (DONE)

### Phase 2 (SHORT-TERM - This Week)
- 🔄 Update `.github/agents/CORTEX.md` (Add enforcement routing)
- 🔄 Update `cortex-builder.prompt.md` (Link enforcement stage)
- 🔄 Update `cortex-builder.md` (Link enforcement stage)
- 🔄 Update `cortex-git-commit.prompt.md` (Checkpoint enforcement)

### Phase 3 (MID-TERM - Next Week)
- 🔄 Update `cortex-review.prompt.md` (Post-execution positioning)
- 🔄 Update `cortex-review-agents.md` (Relationship clarification)
- 🔄 Update `.github/agents/cortex-planner.md` (Phase readiness integration)
- 🔄 Update `cortex-total-recall.prompt.md` (Enforcement discovery)

### Phase 4 (OPTIONAL - Nice-to-Have)
- 📝 Create `cortex-governance-guide.md` (Complete governance reference)
- 📝 Update `cortex-doc.prompt.md` (Governance documentation)
- 📝 Create `cortex-enforcement-troubleshooting.md` (Help guide)

---

## ✅ Quality Checklist

All enhanced prompts and agents should:

- [ ] Include response header enforcement (CORE-029)
- [ ] Reference enforcement layer where applicable
- [ ] Maintain backward compatibility
- [ ] Include AC-ID for audit trail
- [ ] Link to enforcement documentation
- [ ] Explain relationship to enforcement agents
- [ ] Provide clear examples
- [ ] No markdown files outside `docs/` (CORE-002)

---

## 📊 Enforcement Integration Status

| File | Updates | Status | Link Count |
|------|---------|--------|-----------|
| CORTEX.prompt.md | Stage 3 added | ✅ COMPLETE | 8 references |
| cortex-enforcement.prompt.md | NEW | ✅ READY | - |
| cortex-enforcement-agents.md | NEW | ✅ READY | - |
| cortex-builder.prompt.md | Pending | ⏳ PHASE-2 | +1 link |
| cortex-git-commit.prompt.md | Pending | ⏳ PHASE-2 | +2 links |
| CORTEX.md | Pending | ⏳ PHASE-2 | +3 links |
| cortex-builder.md | Pending | ⏳ PHASE-2 | +2 links |
| cortex-review.prompt.md | Pending | ⏳ PHASE-3 | +2 links |
| cortex-review-agents.md | Pending | ⏳ PHASE-3 | +3 links |
| cortex-planner.md | Pending | ⏳ PHASE-3 | +2 links |
| cortex-total-recall.prompt.md | Pending | ⏳ PHASE-3 | +3 links |
| cortex-doc.prompt.md | Pending | ⏳ PHASE-4 | +1 link |

---

## 🎁 Bonus: Cross-Reference Map

```
CORTEX.prompt.md (Master)
├── Enforcement Layer
│   ├─ cortex-enforcement.prompt.md (Agent prompt)
│   └─ cortex-enforcement-agents.md (Technical specs)
├── Implementation Path
│   ├─ cortex-builder.prompt.md (with enforcement link)
│   └─ cortex-builder.md (agent spec)
├── Validation Path
│   ├─ cortex-review.prompt.md (post-enforcement)
│   └─ cortex-review-agents.md (8 review agents)
├── Git Operations
│   ├─ cortex-git-commit.prompt.md (checkpoint enforcement)
│   └─ CORE-026 reference
├── Discovery
│   └─ cortex-total-recall.prompt.md (with enforcement discovery)
├── Planning
│   └─ cortex-planner.md (with compliance checks)
└── Documentation
    └─ cortex-doc.prompt.md (with governance docs)
```

---

## 📚 Related Documents

| Document | Purpose |
|----------|---------|
| `.github/prompts/cortex-enforcement.prompt.md` | Enforcement agent usage |
| `.github/agents/cortex-enforcement-agents.md` | Technical specifications |
| `cortex_brain/tier0/governance/core-rules.yaml` | Tier 0 rules authority |
| `cortex_brain/tier1/acceptance/` | Tier 1 rules authority |
| `CORTEX.prompt.md` | Master orchestrator (updated) |

---

## ✨ Summary

**CORTEX's governance architecture is STRONG**, but the new **Enforcement Layer makes it AIRTIGHT**:

1. **Before:** Rules existed but weren't enforced → could be bypassed
2. **After:** Rules are actively prevented at pre-execution stage → cannot be bypassed

**The 9 enhancement recommendations** weave enforcement seamlessly into the existing agent ecosystem, so developers naturally encounter governance checks at each stage without being surprised.

**All 2 new files (enforcement prompt + agents guide) are ready for production deployment TODAY.**

---

**Status:** ✅ READY FOR IMPLEMENTATION  
**Authority:** CORTEX Governance Review  
**Author:** Asif Hussain  
**Date:** 2026-01-24
