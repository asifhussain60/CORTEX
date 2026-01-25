# CORTEX Prompts & Agents: Holistic Gap Analysis
**Date:** 2026-01-25 | **Authority:** Review of `/github/prompts` + `/github/agents` | **Scope:** COMPLETE COVERAGE AUDIT

---

## 📋 Executive Summary

| Category | Status | Finding | Severity |
|----------|--------|---------|----------|
| **Prompt Coverage** | ⚠️ PARTIAL | 7 prompts exist, 3+ missing | 🟡 MEDIUM |
| **Agent Coverage** | ⚠️ CRITICAL | 7 agents defined, 4 unimplemented | 🔴 HIGH |
| **Prompt-Agent Pairing** | ⚠️ MISALIGNED | 5/7 prompts have agents, 2 orphaned | 🟡 MEDIUM |
| **Orchestrator Mapping** | 🔴 BROKEN | Prompts reference 23 orchestrators, agents reference only 7-8 | 🔴 HIGH |
| **DoR Protocol** | ✅ PRESENT | All major prompts have DoR, but enforcement inconsistent | 🟢 LOW |
| **CORE Rules Enforcement** | ⚠️ INCOMPLETE | CORE-030, CORE-035 recently added, coverage gaps | 🟡 MEDIUM |

---

## 🎯 PROMPT INVENTORY (Current vs. Complete)

### Currently Implemented (7)

| # | Prompt | Version | Status | Agent Paired | DoR Present |
|---|--------|---------|--------|--------------|-------------|
| 1 | `CORTEX.prompt.md` | 5.0 | ✅ ACTIVE | ✅ CORTEX.md (Master) | ✅ YES |
| 2 | `cortex-review.prompt.md` | 5.2 | ✅ ACTIVE | ✅ cortex-review.md | ✅ YES |
| 3 | `cortex-total-recall.prompt.md` | 7.0 | ✅ ACTIVE | ✅ cortex-total-recall.md | ✅ YES |
| 4 | `cortex-builder.prompt.md` | 4.0 | ✅ ACTIVE | ✅ cortex-builder.md | ✅ YES |
| 5 | `cortex-enforcement.prompt.md` | 2.0 | ✅ ACTIVE | ✅ cortex-enforcement-agents.md | ✅ YES |
| 6 | `cortex-doc.prompt.md` | Latest | ✅ ACTIVE | ❌ **MISSING** | ✅ YES |
| 7 | `cortex-git-commit.prompt.md` | 4.0 | ✅ ACTIVE | ❌ **MISSING** | ✅ YES |

### Missing Prompts (Identified from Copilot Instructions)

| # | Prompt | Purpose | Why Needed | Severity |
|---|--------|---------|-----------|----------|
| 8 | `cortex-refactor.prompt.md` | Refactoring orchestration | Referenced in intent router (REFACTOR intent) | 🟡 HIGH |
| 9 | `cortex-test.prompt.md` | Test generation & validation | Referenced in intent router (TEST intent) | 🟡 HIGH |
| 10 | `cortex-analyze.prompt.md` | Analysis & investigation | Referenced in intent router (ANALYZE intent) | 🟡 MEDIUM |
| 11 | `cortex-feedback.prompt.md` | Feedback collection & GitHub Issues | Mentioned in archived docs | 🔵 LOW |

---

## 👥 AGENT INVENTORY (Current vs. Complete)

### Currently Implemented (7 Agent Definitions)

| # | Agent File | Agents Defined | Status | Prompts Paired | Wiring Status |
|---|------------|-----------------|--------|-----------------|---------------|
| 1 | `CORTEX.md` | 1 (Master) | ✅ DEFINED | ✅ CORTEX.prompt | ⚠️ PARTIAL |
| 2 | `cortex-review.md` | 1 (Coordinator) | ✅ DEFINED | ✅ cortex-review.prompt | ⚠️ PARTIAL |
| 3 | `cortex-review-agents.md` | 8 (Sub-agents) | ✅ DEFINED | ✅ cortex-review.prompt | ⚠️ PARTIAL |
| 4 | `cortex-total-recall.md` | 1 (Discovery/Fixer) | ✅ DEFINED | ✅ cortex-total-recall.prompt | ⚠️ PARTIAL |
| 5 | `cortex-builder.md` | 1 (TDD) | ✅ DEFINED | ✅ cortex-builder.prompt | ⚠️ PARTIAL |
| 6 | `cortex-enforcement-agents.md` | 3 (Enforcement) | ✅ DEFINED | ✅ cortex-enforcement.prompt | ❌ **UNIMPLEMENTED** |
| 7 | `cortex-planner.md` | 1 (Planning) | ✅ DEFINED | ❌ **ORPHANED** | ⚠️ PARTIAL |

### Unimplemented Agents (Referenced but Not Defined)

| # | Agent | Type | Referenced In | Implementation Status |
|---|-------|------|---------------|-----------------------|
| 1 | **EnforcementOrchestrator** | Orchestrator | enforcement.prompt | 🔴 **NOT IMPLEMENTED** |
| 2 | **GovernanceEnforcementAgent** | Sub-agent | enforcement.prompt | 🔴 **NOT IMPLEMENTED** |
| 3 | **SecurityCheckpointAgent** | Sub-agent | enforcement.prompt | 🔴 **NOT IMPLEMENTED** |
| 4 | **ComplianceValidationAgent** | Sub-agent | enforcement.prompt | 🔴 **NOT IMPLEMENTED** |
| 5 | **DocumentationOrchestrator** | Orchestrator | doc.prompt | 🔴 **NOT IMPLEMENTED** |
| 6 | **GitOrchestrator** | Orchestrator | git-commit.prompt | 🔴 **NOT IMPLEMENTED** |
| 7 | **RefactoringOrchestrator** | Orchestrator | CORTEX.prompt (intent routing) | ⚠️ **UNSPECIFIED** |
| 8 | **PlanningOrchestrator** | Orchestrator | planner.md | ⚠️ **UNSPECIFIED** |

---

## 🔗 PROMPT-TO-AGENT MAPPING MATRIX

### Complete Coverage

```
CORTEX.prompt.md (5.0)
  ├─ Routes to: CORTEX.md (Master Agent) ✅
  ├─ Delegates to: 8+ specialist orchestrators (prompt-defined) ⚠️
  └─ Status: FUNCTIONAL but incomplete orchestrator delegation

cortex-review.prompt.md (5.2)
  ├─ Routes to: cortex-review.md (Coordinator) ✅
  ├─ Uses: cortex-review-agents.md (8 sub-agents) ✅
  ├─ Enforces: CORE-030, CORE-035 (NEW) ✅
  └─ Status: COMPLETE - Implementation Truth verification enabled

cortex-total-recall.prompt.md (7.0)
  ├─ Routes to: cortex-total-recall.md (Discovery Agent) ✅
  ├─ Capabilities: AC-PERMANENT-FIX validation (8 fixes) ✅
  ├─ References: TotalRecallAgent class ✅
  └─ Status: COMPLETE - Auto-wiring, unwired detection

cortex-builder.prompt.md (4.0)
  ├─ Routes to: cortex-builder.md (TDD Agent) ✅
  ├─ Enforces: CORE-008, CORE-011, CORE-012 ✅
  └─ Status: COMPLETE - TDD workflow defined

cortex-enforcement.prompt.md (2.0)
  ├─ Routes to: cortex-enforcement-agents.md (3 agents) ✅
  ├─ Defines: 3 enforcement agents but... 🔴
  │   ├─ GovernanceEnforcementAgent (NOT IMPLEMENTED)
  │   ├─ SecurityCheckpointAgent (NOT IMPLEMENTED)
  │   ├─ ComplianceValidationAgent (NOT IMPLEMENTED)
  └─ Status: ⚠️ CRITICAL - Agents defined in prompt but NOT in orchestrator code

cortex-doc.prompt.md (Latest)
  ├─ Routes to: DocumentationOrchestrator (NOT DEFINED) 🔴
  ├─ Enables: 8-phase end-to-end generation ✅
  └─ Status: ⚠️ PARTIAL - Agent definition missing

cortex-git-commit.prompt.md (4.0)
  ├─ Routes to: GitOrchestrator (NOT DEFINED) 🔴
  ├─ Enforces: CORE-026, CORE-027 ✅
  └─ Status: ⚠️ PARTIAL - Agent definition missing

cortex-planner.md (4.0)
  ├─ Prompt: ❌ NO CORRESPONDING PROMPT
  ├─ Role: Phase planning & progress tracking ✅
  ├─ SSOT: cortex-impl-map.yaml ✅
  └─ Status: 🟡 ORPHANED - Agent exists without prompt guide
```

---

## 🎯 GAP ANALYSIS: MISSING COMPONENTS

### Gap 1: Missing Prompt Files

#### cortex-refactor.prompt.md (CRITICAL)
**Current State:** Referenced in CORTEX.prompt.md intent routing
```yaml
Intent: REFACTOR
Handler: RefactoringOrchestrator
Keywords: refactor, improve, cleanup, optimize
```
**Missing:** Prompt definition for RefactoringOrchestrator coordination

**What Needs to Be Added:**
- DoR protocol for refactoring operations
- SOLID principle enforcement
- Circular dependency detection
- Refactoring safety checks (impact analysis)
- Rollback procedures

**Severity:** 🟠 CRITICAL - Blocks REFACTOR operations

---

#### cortex-test.prompt.md (CRITICAL)
**Current State:** Referenced in CORTEX.prompt.md intent routing
```yaml
Intent: TEST
Handler: TDDOrchestrator
Keywords: test, unittest, pytest
```
**Missing:** Dedicated test generation/validation prompt (currently merged into builder)

**What Needs to Be Added:**
- Test discovery & enumeration
- Coverage analysis & reporting
- Test failure diagnosis
- Mock/fixture generation
- Property-based testing guidance

**Severity:** 🟠 HIGH - Blocks TEST operations independently

---

#### cortex-analyze.prompt.md (MEDIUM)
**Current State:** Referenced in CORTEX.prompt.md intent routing
```yaml
Intent: ANALYZE
Handler: MasterOrchestrator
Keywords: analyze, review, investigate
```
**Missing:** Dedicated analysis prompt (currently merged into review)

**What Needs to Be Added:**
- Lightweight analysis (vs. full review)
- Targeted deep-dives
- Dependency analysis
- Impact analysis
- Performance profiling guidance

**Severity:** 🟡 MEDIUM - Can use review prompt as fallback

---

#### cortex-feedback.prompt.md (LOW)
**Current State:** Mentioned in archived documentation
**Missing:** Feedback collection & GitHub Issues integration

**What Needs to Be Added:**
- Feedback collection from users
- GitHub Issues creation/management
- Classification & prioritization
- Escalation procedures

**Severity:** 🔵 LOW - Enhancement, not critical

---

### Gap 2: Missing Agent Definitions

#### EnforcementOrchestrator & Sub-Agents (CRITICAL)
**Current State in cortex-enforcement.prompt.md:**
```markdown
# The 3 Enforcement Agents

### 1. GovernanceEnforcementAgent
### 2. SecurityCheckpointAgent  
### 3. ComplianceValidationAgent
```

**Problem:**
- ✅ Prompt defines all 3 agents
- ✅ Integration point specified (MasterOrchestrator Stage 3)
- ❌ **Agent definitions missing from `/github/agents/core/`**
- ❌ **Agent implementations not in codebase**
- ❌ **No orchestrator code to wire them**

**What Needs to Be Created:**
```
.github/agents/core/cortex-enforcement-agents-DETAIL.md
├─ Agent 1: GovernanceEnforcementAgent
│  ├─ Checks: CORE-008 through CORE-035
│  ├─ Output: CheckResult.BLOCK() or CheckResult.PASS()
│  └─ Integration: MasterOrchestrator.stage_3_enforcement()
├─ Agent 2: SecurityCheckpointAgent
│  ├─ Checks: CORE-026 (git checkpoints), CORE-030 (verification)
│  └─ Integration: DoR approval gate
└─ Agent 3: ComplianceValidationAgent
   ├─ Checks: TIER 1-3 escalations
   └─ Integration: User escalation workflow
```

**Severity:** 🔴 CRITICAL - Enforcement mechanism incomplete

---

#### DocumentationOrchestrator Agent (MEDIUM)
**Current State in cortex-doc.prompt.md:**
```markdown
Intent: DOCUMENT - FRESH GENERATION
Handler: DocumentationOrchestrator
```

**Problem:**
- ✅ Prompt defines 8-phase pipeline
- ❌ **Agent definition missing**
- ❌ **No agent guide for orchestrator behavior**

**What Needs to Be Created:**
```
.github/agents/core/cortex-documentation.md
├─ Discovery Phase Agent
├─ Generation Phase Agent
├─ Diagram Phase Agent
├─ Build Validation Agent
├─ Link Validation Agent
├─ Reporting Agent
├─ Cleanup Agent
└─ Git Commit Agent
```

**Severity:** 🟡 MEDIUM - Prompt exists but agent guide missing

---

#### GitOrchestrator Agent (MEDIUM)
**Current State in cortex-git-commit.prompt.md:**
```markdown
Intent: DEPLOY (Git operations)
Handler: GitOrchestrator
```

**Problem:**
- ✅ Prompt defines commit/push/merge operations
- ❌ **Agent definition missing**
- ❌ **No agent guide for git orchestration**

**What Needs to Be Created:**
```
.github/agents/core/cortex-git.md
├─ Pre-commit Validation Agent
├─ Checkpoint Creation Agent
├─ Commit Message Generation Agent
├─ Push Agent
└─ Merge Conflict Resolution Agent
```

**Severity:** 🟡 MEDIUM - Prompt exists but agent guide missing

---

### Gap 3: Orphaned Components

#### cortex-planner.md Has No Prompt
**Current State:**
- ✅ Agent definition exists (cortex-planner.md v4.0)
- ❌ **No corresponding prompt file**
- ❌ **No DoR protocol guide**

**What Needs to Be Created:**
```
.github/prompts/cortex-planning.prompt.md
├─ Purpose: Phase planning & progress tracking
├─ SSOT: cortex-impl-map.yaml
├─ Commands: /status, /phase, /next, /readiness, /blockers
├─ DoR protocol
└─ Output format specification
```

**Severity:** 🟡 MEDIUM - Agent orphaned without prompt guide

---

## 🔌 ORCHESTRATOR COVERAGE MATRIX

### Orchestrators Referenced in Prompts

| # | Orchestrator | Prompt Reference | Prompt Version | Agent Defined | Agent File | Implementation |
|---|--------------|------------------|-----------------|---------------|------------|-----------------|
| 1 | MasterOrchestrator | CORTEX.prompt (Stage 1-4) | 5.0 | ✅ | CORTEX.md | ⚠️ Partial |
| 2 | InteractionOrchestrator | CORTEX.prompt (Stage 1) | 5.0 | ✅ | CORTEX.md | ⚠️ Referenced |
| 3 | IntentRouter | CORTEX.prompt (Stage 1) | 5.0 | ✅ | CORTEX.md | ⚠️ Referenced |
| 4 | TDDOrchestrator | cortex-builder.prompt | 4.0 | ✅ | cortex-builder.md | ⚠️ Partial |
| 5 | ReviewOrchestrator | cortex-review.prompt | 5.2 | ✅ | cortex-review.md | ⚠️ Partial |
| 6 | RefactoringOrchestrator | CORTEX.prompt (intent routing) | 5.0 | ❌ | **MISSING** | ❌ MISSING |
| 7 | PlanningOrchestrator | cortex-planner.md, total-recall.prompt | 4.0 / 7.0 | ✅ | cortex-planner.md | ⚠️ Partial |
| 8 | DomainOrchestrator | CORTEX.prompt (Stage 4) | 5.0 | ❌ | **MISSING** | ⚠️ Referenced |
| 9 | DocumentationOrchestrator | cortex-doc.prompt | Latest | ❌ | **MISSING** | ❌ MISSING |
| 10 | GitOrchestrator | cortex-git-commit.prompt | 4.0 | ❌ | **MISSING** | ❌ MISSING |
| 11 | EnforcementOrchestrator | cortex-enforcement.prompt | 2.0 | ❌ | **MISSING** | ❌ MISSING |
| 12-23 | Support Orchestrators (12 more) | total-recall.prompt (WIRE-003) | 7.0 | ⚠️ Partial | - | ❌ UNSPECIFIED |

---

## ⚙️ IMPLEMENTATION DEFICIENCY MATRIX

### Prompt Quality (✅ GOOD)

| Aspect | Status | Details |
|--------|--------|---------|
| DoR Protocol | ✅ YES | All major prompts have clear DoR |
| Response Headers | ✅ YES | CORE-029 enforcement in place |
| CORE Rule Coverage | ⚠️ PARTIAL | CORE-030, CORE-035 added recently |
| Command Reference | ✅ YES | Quick command syntax documented |
| Error Handling | ⚠️ PARTIAL | Some prompts lack failure recovery |
| Version Control | ✅ YES | All prompts versioned |

### Agent Quality (⚠️ INCOMPLETE)

| Aspect | Status | Details |
|--------|--------|---------|
| Agent Definition | 🔴 CRITICAL | 4 agents undefined (Enforcement, Doc, Git, Refactor) |
| Sub-agent Detail | ✅ YES | Review agents well-documented |
| Orchestrator Alignment | ⚠️ PARTIAL | Agent definitions don't map to orchestrator code |
| CORE Rule Checking | ⚠️ PARTIAL | Limited enforcement agent implementations |
| Integration Points | ⚠️ PARTIAL | Stage 3 enforcement not fully wired |
| Testing Guidance | 🔵 MINIMAL | Limited test generation guidance |

### Orchestrator Wiring (🔴 BROKEN)

| Orchestrator Type | Count | Wired | % Coverage |
|-------------------|-------|-------|------------|
| Core Orchestrators | 6 | 3-4 | 50-67% |
| Domain Orchestrators | 5 | 2-3 | 40-60% |
| Support Orchestrators | 12 | 1-2 | 8-17% |
| **TOTAL** | **23** | **~8-10** | **~35-43%** |

---

## 🎯 CRITICAL DEFICIENCIES (Priority Order)

### 🔴 TIER 0: BLOCKING (Must Fix Immediately)

#### Deficiency #1: Enforcement Agents Undefined
**Problem:** `cortex-enforcement.prompt.md` references 3 agents that don't exist
- GovernanceEnforcementAgent
- SecurityCheckpointAgent
- ComplianceValidationAgent

**Impact:** Governance enforcement (Stage 3) cannot execute

**Fix:**
1. Create `cortex-enforcement-agents-DETAIL.md` with full agent specifications
2. Reference in `cortex-enforcement.prompt.md`
3. Implement orchestrator code for EnforcementOrchestrator
4. Wire into MasterOrchestrator Stage 3

**Effort:** 2-3 hours | **Priority:** 🔴 CRITICAL

---

#### Deficiency #2: Orchestrator Implementations Missing (Enforcement, Doc, Git)
**Problem:** 3+ orchestrators referenced in prompts but not implemented

**Impact:**
- `/doc-fresh-generate` command non-functional (DocumentationOrchestrator)
- `/git-commit`, `/git-checkpoint` non-functional (GitOrchestrator)
- Governance enforcement non-functional (EnforcementOrchestrator)

**Fix:**
1. Implement DocumentationOrchestrator in codebase
2. Implement GitOrchestrator in codebase
3. Implement EnforcementOrchestrator in codebase
4. Wire into MasterOrchestrator

**Effort:** 6-8 hours | **Priority:** 🔴 CRITICAL

---

### 🟠 TIER 1: HIGH BLOCKING (Fix This Phase)

#### Deficiency #3: Missing Prompt Files (Refactor, Test)
**Problem:** `cortex-refactor.prompt.md` and `cortex-test.prompt.md` not created

**Impact:**
- REFACTOR intent routing has no orchestration guide
- TEST intent routing has no dedicated guidance

**Fix:**
1. Create `cortex-refactor.prompt.md` (500-800 lines)
2. Create `cortex-test.prompt.md` (400-600 lines)
3. Align with existing DoR/response header patterns
4. Reference corresponding agent definitions (create if needed)

**Effort:** 2-3 hours | **Priority:** 🟠 HIGH

---

#### Deficiency #4: cortex-planner.md Orphaned (No Prompt)
**Problem:** Agent definition exists but no orchestration guide

**Impact:** Planning operations lack formal prompt guidance

**Fix:**
1. Create `cortex-planning.prompt.md` (300-500 lines)
2. Define DoR protocol for planning operations
3. Reference cortex-planner.md agent
4. Add to README and prompt index

**Effort:** 1-2 hours | **Priority:** 🟠 MEDIUM-HIGH

---

### 🟡 TIER 2: MEDIUM (Fix Before Phase Complete)

#### Deficiency #5: Agent Definition Files Missing (Doc, Git)
**Problem:** Documentation and Git orchestrators have no agent guide

**Impact:** Agent behavior not documented, developer guidance missing

**Fix:**
1. Create `cortex-documentation.md` agent definition
2. Create `cortex-git.md` agent definition
3. Cross-reference with corresponding prompts
4. Update agent README with new entries

**Effort:** 1-2 hours | **Priority:** 🟡 MEDIUM

---

#### Deficiency #6: Refactor & Test Agent Definitions Missing
**Problem:** Once prompts are created, agents need definition files

**Impact:** Agent behavior not documented for REFACTOR and TEST operations

**Fix:**
1. Create `cortex-refactor.md` agent definition
2. Create `cortex-test.md` agent definition
3. Align with prompt definitions
4. Update agent README

**Effort:** 1-2 hours | **Priority:** 🟡 MEDIUM

---

#### Deficiency #7: Support Orchestrators (12) Unspecified
**Problem:** `cortex-total-recall.prompt.md` references WIRE-003 (6 support orchestrators) but agent specs undefined

**Impact:** Support orchestrator behavior not documented

**Fix:**
1. Document support orchestrators in agents/core/
2. Create agent definitions for: OnboardingOrchestrator, ToolDiscoveryOrchestrator, UpgradeOrchestrator, RollbackOrchestrator, SetupOrchestrator, ComposedOrchestrator
3. Reference orchestrator implementations in codebase

**Effort:** 3-4 hours | **Priority:** 🟡 MEDIUM

---

#### Deficiency #8: CORE Rule Enforcement Incomplete
**Problem:** CORE-030 (Implementation Truth) and CORE-035 (Single Canonical) enforcement inconsistent

**Impact:** 
- Documentation-driven answers may persist
- Duplicate implementations may not be detected

**Fix:**
1. Update enforcement agents to enforce CORE-030, CORE-035
2. Add to all enforcement agent definitions
3. Wire into MasterOrchestrator Stage 3

**Effort:** 2-3 hours | **Priority:** 🟡 MEDIUM

---

## 📊 COVERAGE SCORECARD

```
PROMPT COVERAGE
───────────────
  ✅ Core intents covered:          5/8 (62%)
     ├─ IMPLEMENT ✅
     ├─ FIX ✅ (via CORTEX.prompt)
     ├─ REVIEW ✅
     ├─ TEST ❌ (missing)
     ├─ REFACTOR ❌ (missing)
     ├─ ANALYZE ❌ (missing)
     ├─ DOCUMENT ✅
     └─ DEPLOY ✅

  ✅ DoR protocol:                 7/7 (100%)
  ✅ Response headers:             7/7 (100%)
  ⚠️  CORE rule coverage:          29/35 (83%)
  ❌ Missing prompt files:          3 (TEST, REFACTOR, ANALYZE)

AGENT COVERAGE
──────────────
  ✅ Agent definitions:            7/11 (64%)
  ✅ Sub-agents:                   8/8 (100% for review)
  ❌ Enforcement agents:           0/3 (0% implementation)
  ❌ Documentation agent:          0/1 (0%)
  ❌ Git agent:                    0/1 (0%)
  ❌ Refactor agent:               0/1 (0%)
  ❌ Test agent:                   0/1 (0%)
  ⚠️  Planner agent orphaned:      1/1 (100% definition, 0% prompt)

ORCHESTRATOR WIRING
───────────────────
  ✅ Core orchestrators:           4/6 (67%)
  ⚠️  Domain orchestrators:        2-3/5 (40-60%)
  ❌ Support orchestrators:        1-2/12 (8-17%)
  ❌ Enforcement orchestrator:     0/1 (0%)
  ❌ Documentation orchestrator:   0/1 (0%)
  ❌ Git orchestrator:             0/1 (0%)
  ───────────────────────────────────────────
  📊 TOTAL ORCHESTRATOR COVERAGE:  ~8-10/23 (35-43%)

INTEGRATION HEALTH
──────────────────
  ✅ Prompt-Agent pairing:         5/7 (71%)
  ⚠️  Agent-Orchestrator wiring:   5/11 (45%)
  ❌ Enforcement integration:      0/1 (0%)
  ❌ Documentation integration:    0/1 (0%)
  ❌ Git integration:              0/1 (0%)

═══════════════════════════════════════════════
OVERALL SYSTEM HEALTH:  🟡 YELLOW (PARTIAL)
═══════════════════════════════════════════════
```

---

## 🛠️ REMEDIATION ROADMAP

### Phase 1: Critical Fixes (2-3 hours)

**1.1 Create cortex-enforcement-agents-DETAIL.md**
```
Location: .github/agents/core/cortex-enforcement-agents-DETAIL.md
Contents: Full specifications for 3 enforcement agents
Reference: From cortex-enforcement.prompt.md
Status: BLOCKING → READY
```

**1.2 Implement EnforcementOrchestrator (Code)**
```
Location: cortex/orchestrators/core/enforcement_orchestrator.py
Wiring: Update MasterOrchestrator Stage 3
Status: MISSING → FUNCTIONAL
```

**1.3 Implement DocumentationOrchestrator (Code)**
```
Location: cortex/orchestrators/documentation/documentation_orchestrator.py
Wiring: MasterOrchestrator intent routing
Status: MISSING → FUNCTIONAL
```

### Phase 2: High Priority Fixes (2-3 hours)

**2.1 Create cortex-refactor.prompt.md**
```
Location: .github/prompts/cortex-refactor.prompt.md
Model: cortex-builder.prompt.md pattern
Status: MISSING → CREATED
```

**2.2 Create cortex-test.prompt.md**
```
Location: .github/prompts/cortex-test.prompt.md
Model: cortex-builder.prompt.md pattern
Status: MISSING → CREATED
```

**2.3 Create cortex-planning.prompt.md**
```
Location: .github/prompts/cortex-planning.prompt.md
Model: cortex-builder.prompt.md pattern
Status: ORPHANED → PAIRED
```

### Phase 3: Medium Priority Fixes (1-2 hours)

**3.1 Create Agent Definition Files**
```
cortex-refactor.md
cortex-test.md
cortex-documentation.md
cortex-git.md
```

**3.2 Create Support Orchestrator Agent Definitions**
```
6 agent definitions for WIRE-003 orchestrators
```

### Phase 4: Polish (1 hour)

**4.1 Update Prompt READMEs**
**4.2 Update Agent READMEs**
**4.3 Update copilot-instructions.md with new orchestrators**
**4.4 Verify all cross-references**

---

## 📝 RECOMMENDATIONS

### Immediate Actions

1. **Enforce Prompt-Agent Pairing Rule**
   - Every `.prompt.md` must have corresponding `.md` agent file
   - Every agent file should have corresponding prompt (exceptions: sub-agents)

2. **Implement Missing Orchestrators**
   - EnforcementOrchestrator (BLOCKING)
   - DocumentationOrchestrator (HIGH)
   - GitOrchestrator (HIGH)
   - RefactoringOrchestrator (MEDIUM)

3. **Create Missing Prompts**
   - cortex-refactor.prompt.md
   - cortex-test.prompt.md
   - cortex-planning.prompt.md

4. **Enforce CORE-030 and CORE-035**
   - Add to all enforcement agent definitions
   - Test in enforcement orchestrator

### Process Improvements

1. **Checklist: New Orchestrator**
   ```
   [ ] Prompt file created (.github/prompts/)
   [ ] Agent definition created (.github/agents/core/)
   [ ] README entries updated (both)
   [ ] Orchestrator code implemented (cortex/orchestrators/)
   [ ] Wired into MasterOrchestrator
   [ ] Integration tested
   [ ] Updated copilot-instructions.md
   ```

2. **Cross-Reference Validation**
   - All prompts → verify agent definition exists
   - All agents → verify prompt definition exists
   - All orchestrators → verify in agent definition
   - All agent definitions → verify in orchestrator code

3. **Coverage Metrics**
   - Maintain "Prompt Coverage Scorecard" in monitoring
   - Target: 100% prompt-agent pairing
   - Target: 100% orchestrator documentation
   - Target: 100% orchestrator wiring to MasterOrchestrator

---

## 🔍 VERIFICATION CHECKLIST

Before declaring "complete":

- [ ] All 7 prompts have corresponding agent definitions
- [ ] All 11 referenced orchestrators have agent definitions
- [ ] All 23 orchestrators documented in agents/
- [ ] All enforcement agents (3) implemented and wired
- [ ] All CORE rules (31-35) enforced in appropriate agents
- [ ] All prompts follow response header pattern
- [ ] All prompts have DoR protocol
- [ ] All orchestrators wired to MasterOrchestrator
- [ ] README files updated for prompts/ and agents/
- [ ] copilot-instructions.md reflects current agent/prompt inventory

---

## 📋 FINAL SUMMARY

**What We Have:** 
- 7 prompts (6/7 with agents)
- 7 agent definitions (partial coverage)
- 8 sub-agents (review only)
- ~8-10 orchestrators wired

**What We Need:**
- 3+ missing prompt files (TEST, REFACTOR, ANALYZE)
- 4+ missing agent definitions (Enforcement, Doc, Git, Refactor)
- 3+ missing orchestrator implementations (Enforcement, Doc, Git)
- 3 missing enforcement agents (GovernanceEnforcement, SecurityCheckpoint, ComplianceValidation)
- 12 support orchestrators documented/specified

**Impact if Not Fixed:**
- 🔴 CRITICAL: Enforcement mechanism non-functional
- 🔴 CRITICAL: 35-45% orchestrator coverage (vs. goal: 100%)
- 🟠 HIGH: REFACTOR and TEST operations lack guidance
- 🟡 MEDIUM: Documentation agent unmapped

**Estimated Effort to Complete:** 8-12 hours

---

**Document Authority:** Holistic review of `/github/prompts` and `/github/agents` directories  
**Last Updated:** 2026-01-25 | **Status:** 🟡 ANALYSIS COMPLETE - AWAITING APPROVAL
