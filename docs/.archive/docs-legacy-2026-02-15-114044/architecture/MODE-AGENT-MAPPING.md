# Mode-Agent-MCP Tool Mapping Architecture
**Version:** 1.0  
**Phase:** 81 Stage 4  
**Status:** 🟢 Complete  
**Date:** 2026-02-11

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [8-Mode Routing System](#8-mode-routing-system)
3. [Mode→Agent→MCP Tool Mappings](#modeagentmcp-tool-mappings)
4. [Agent Capability Matrix](#agent-capability-matrix)
5. [Collaboration Patterns by Mode](#collaboration-patterns-by-mode)
6. [Integration Flows](#integration-flows)
7. [Mode Detection Logic](#mode-detection-logic)
8. [Token Optimization](#token-optimization)
9. [Visual Architecture](#visual-architecture)
10. [Implementation Examples](#implementation-examples)

---

## Executive Summary

CORTEX operates across **8 distinct modes** (HEPTA-MODE+), each with dedicated agent teams and MCP tool chains. This document maps:

- **MODE** → How user input/context triggers operational mode
- **AGENTS** → Which agents execute within that mode
- **MCP TOOLS** → Which MCP tools the agents invoke
- **FLOW** → The execution sequence and gates
- **INTEGRATION** → How modes work together

### Key Insight: Capability-Based Agent Clustering

Rather than 1-agent-per-mode, CORTEX uses **shared capability clustering**:
- Single agent serves 2-4 modes (based on capabilities)
- MCP tools deduplicated across agents
- Token efficiency through LENS cache reuse (60% savings)
- Intelligent fallback chains for resilience

---

## 8-Mode Routing System

### Mode Overview Table

| Mode | Priority | Trigger | Agent | Purpose | Token Cost |
|------|----------|---------|-------|---------|-----------|
| **PRE-FLIGHT** | 0 (ALWAYS FIRST) | Automatic | cortex-environment-setup | Environment validation | 50-100 |
| **AUDIT** | 1 | No request / /audit | cortex-auditor | Codebase health scan | 150-250 |
| **META-AUDIT** | 4 | /meta-audit | cortex-architect | Self-improvement analysis | 200-300 |
| **DIGEST** | 2 | Chat markers ≥5 | cortex-digest | Session learning extraction | 100-150 |
| **QUERY** | 3 | Questions/how/why | cortex-ask-coordinator | Knowledge retrieval | 120-180 |
| **PLAN** | 2 | /plan or phase files | cortex-phase-resolver | ROI-based phase prioritization | 180-250 |
| **DESIGN** | 2 | User request | cortex-designer | Implementation with TDD | 200-350 |
| **INTERACTIVE** | 3 | Recommendations/guidance | cortex-interactive | Exploratory conversation | 150-250 |

### Mode Selection Hierarchy

```
User Input
    ↓
┌─────────────────────────────────────────┐
│ 1. PRE-FLIGHT (always first)            │ Priority 0
└─────────┬───────────────────────────────┘
          │ Auto-runs, no user control
          ↓
┌─────────────────────────────────────────┐
│ 2. DIGEST Detection (chat markers ≥5)   │ Priority 2
│    If triggered → DIGEST Mode           │
└─────────┬───────────────────────────────┘
          │
          ├─ Yes → Run DIGEST → Learn
          │
          ↓
┌─────────────────────────────────────────┐
│ 3. Explicit Command Check               │ Priorities 1-4
│    /audit → AUDIT                       │
│    /meta-audit → META-AUDIT             │
│    /plan → PLAN                         │
│    /list → LIST                         │
│    ? or /ask → QUERY                    │
└─────────┬───────────────────────────────┘
          │
          ├─ Matched → Run matching mode
          │
          ↓
┌─────────────────────────────────────────┐
│ 4. Request Type Detection               │ Priorities 2-3
│    Implementation request → DESIGN      │
│    Question → QUERY                     │
│    Recommendation → INTERACTIVE         │
│    No request → AUDIT                   │
└─────────────────────────────────────────┘
```

---

## Mode→Agent→MCP Tool Mappings

### 1. PRE-FLIGHT Mode

**Purpose:** Automatic environment validation (runs BEFORE every operation)

| Component | Value |
|-----------|-------|
| **Agent** | cortex-environment-setup |
| **Trigger** | ALWAYS (automatic, no user control) |
| **Priority** | 0 (highest - always first) |
| **Header** | 🧠 CORTEX Architect | Mode: Pre-Flight |

**MCP Tools:**
```
cortex_validate_environment()
├─ Check Python version (≥3.9)
├─ Validate core dependencies
├─ Check wiring.yaml integrity
└─ Verify git state
```

**Agent Capabilities:**
- env_validation
- dependency_checking
- git_state_verification
- wiring_integrity_validation

**Collaboration:**
- Single agent (no collaborators)
- Sequential execution
- Failure: HALT with error message

**Success Criteria:**
- ✅ Python ≥3.9
- ✅ All core dependencies installed
- ✅ No wiring conflicts

---

### 2. AUDIT Mode

**Purpose:** Context-blind codebase health scan with evidence-based findings

| Component | Value |
|-----------|-------|
| **Primary Agent** | cortex-auditor |
| **Secondary Agent** | cortex-meta-auditor (if recursive validation needed) |
| **Trigger** | No request OR /audit command |
| **Priority** | 1 |
| **Header** | 🧠 CORTEX Architect | Mode: Audit |

**MCP Tool Chain:**
```
cortex_audit()
├─ P0 Checks (Security & Critical)
│   └─ cortex_validate_compliance()
│   └─ cortex_detect_duplicates()
├─ P1 Checks (Infrastructure & Governance)
│   └─ cortex_lens_analyze() [MANDATORY]
│   └─ cortex_meta_audit() [if governance issues]
├─ P2 Checks (Quality)
│   └─ cortex_lens_analyze() [code quality]
│   └─ cortex_git_history() [24h context]
└─ P3 Checks (Cleanup)
    └─ cortex_detect_duplicates() [CORE-035]
```

**Agent Capabilities:**
- code_analysis
- governance_check
- security_scanning
- quality_assessment
- recursive_validation (meta-auditor only)

**Collaboration Pattern:** Sequential
```
cortex-auditor (PRIMARY)
    ├─ P0 Checks
    ├─ P1 Checks
    ├─ P2 Checks
    └─ P3 Checks
    
cortex-meta-auditor (if P1 issues found)
    └─ Governance recursion
```

**Output:** Inline-only (NO markdown files per CORE-002)
- Executive summaries
- Priority-based findings
- Evidence for all findings

---

### 3. META-AUDIT Mode

**Purpose:** Prompt/agent self-enhancement analysis (after primary audit)

| Component | Value |
|-----------|-------|
| **Agent** | cortex-architect |
| **Trigger** | /meta-audit command (after primary audit) |
| **Priority** | 4 |
| **Header** | 🧠 CORTEX Architect | Mode: Meta-Audit |

**MCP Tool Chain:**
```
cortex_meta_audit()
├─ Analyze prompt effectiveness
├─ Check agent coherence
├─ Review recommendation quality
└─ Generate meta-intelligence report
```

**Agent Capabilities:**
- prompt_analysis
- agent_coherence_check
- recommendation_quality_assessment
- meta_intelligence

**Recursion Guard:** max_depth=1 (cannot trigger another meta-audit)

**Collaboration:** Single agent with optional cortex-auditor for validation

---

### 4. DIGEST Mode

**Purpose:** Auto-detect Copilot chat → extract learnings → enhance CORTEX

| Component | Value |
|-----------|-------|
| **Agent** | cortex-digest |
| **Trigger** | File with ≥5 Copilot chat markers OR /digest command |
| **Priority** | 2 |
| **Header** | 🧠 CORTEX Architect | Mode: Digest |

**Detection Algorithm:**
```python
markers = {
    "Read [](file://": 2 points,
    "#file:": 2 points,
    "Summarizing conversation": 3 points,
    "GitHub Copilot:": 1 point,
    "asifhussain60:": 1 point
}
score = sum(markers.values())
if score >= 5:  # Threshold
    trigger_digest_mode()
```

**MCP Tool Chain:**
```
cortex_digest_session()
├─ cortex_git_history() [24h context]
├─ cortex_lens_analyze() [pattern detection]
└─ No output files (CORE-002 compliance)
```

**Agent Capabilities:**
- session_learning_extraction
- pattern_identification
- violation_detection
- enhancement_proposal_generation

**Output:** Inline-only (NO markdown file generation)
- Structured learnings (tables)
- Enhancement proposals
- Pattern identification

---

### 5. QUERY Mode (Educational)

**Purpose:** Knowledge retrieval with educational responses

| Component | Value |
|-----------|-------|
| **Agent** | cortex-ask-coordinator |
| **Trigger** | Questions (how/why/what), /ask command |
| **Priority** | 3 |
| **Header** | 🧠 CORTEX Architect | Mode: Query |

**MCP Tool Chain:**
```
cortex_total_recall()
├─ cortex_git_history() [context]
└─ cortex_lens_analyze() [verification]
```

**Agent Capabilities:**
- knowledge_retrieval
- concept_explanation
- example_generation
- verification_against_implementation

**Characteristics:**
- No TDD enforcement
- No DoR approval gate
- No code generation
- Educational focus

---

### 6. PLAN Mode

**Purpose:** ROI-based phase prioritization with progress tracking

| Component | Value |
|-----------|-------|
| **Primary Agent** | cortex-phase-resolver |
| **Secondary Agent** | cortex-master-plan-auditor |
| **Trigger** | /plan command OR cortex-registry/_cortex-master/ files |
| **Priority** | 2 |
| **Header** | 🧠 CORTEX Architect | Mode: Plan |

**MCP Tool Chain:**
```
cortex_plan_setup()
├─ Load phase registry
├─ Calculate ROI scores
└─ Display priority ranking

cortex_plan_resolve()
├─ Intelligent phase selection
└─ Execute selected phase

cortex_plan_sync_status()
├─ Update phase progress
└─ Sync with dashboard

cortex_master_plan_auditor()
└─ Validate phase coherence
```

**Agent Capabilities:**
- phase_management
- roi_calculation
- phase_synchronization
- plan_validation
- progress_tracking

**Collaboration Pattern:** Hierarchical
```
User /plan command
    ↓
cortex-phase-resolver (PRIMARY)
    ├─ Load phases
    ├─ Calculate ROI
    └─ Display ranking
    ↓
User selects phase
    ↓
cortex-master-plan-auditor (VALIDATOR)
    ├─ Validate phase dependencies
    ├─ Check pre-conditions
    └─ Approve execution
    ↓
Phase executor
    └─ Execute with progress tracking
```

**Progress Format:**
```
[✓] Phase 2 | [→] Phase 3 | [ ] Phase 4
```
- Max 3 phases shown (rolling window)
- Single line preferred
- No screaming blocks (█▓░ forbidden)
- No emoji (🟢🔴🟡 forbidden)

---

### 7. DESIGN Mode

**Purpose:** Enhanced request + challenge + incremental TDD implementation

| Component | Value |
|-----------|-------|
| **Primary Agent** | cortex-designer |
| **Validator** | cortex-holistic-validator |
| **Trigger** | User implementation request (implement/fix/refactor) |
| **Priority** | 2 |
| **Header** | 🧠 CORTEX Architect | Mode: Design |

**MCP Tool Chain (Full TDD Workflow):**
```
cortex_process_request()
├─ Request Enhancement
│   ├─ Security analysis
│   ├─ Edge case identification
│   └─ MCP exposure check
│
├─ Challenge Generation (cortex_challenge)
│   ├─ Disagreement detection (3-5 questions)
│   ├─ Assumption validation
│   └─ Alternative approaches
│
├─ DoR Gate
│   ├─ Await "proceed" approval
│   └─ Risk assessment
│
├─ RED Phase (cortex_lens_analyze + cortex_validate_compliance)
│   ├─ Write failing tests
│   ├─ Validate test structure
│   └─ Governance pre-check
│
├─ GREEN Phase (cortex_process_request)
│   ├─ Implement code (incremental <500 LOC)
│   ├─ Run tests → verify passing
│   └─ Compliance validation
│
├─ REFACTOR Phase (cortex_refactor)
│   ├─ Code quality improvements
│   ├─ Test coverage validation
│   └─ Final compliance check
│
└─ Completion Report (inline)
    └─ Evidence of all tests passing
```

**Agent Capabilities:**
- code_generation
- request_enhancement
- challenge_generation
- tdd_enforcement
- incremental_delivery
- test_writing
- code_refactoring

**Collaboration Pattern:** Hierarchical Resolver→Auditor→Executor
```
cortex-designer (RESOLVER)
    ├─ Enhance request
    ├─ Generate challenges
    └─ Validate DoR

cortex-holistic-validator (AUDITOR)
    ├─ Pre-check TDD structure
    ├─ Governance validation
    └─ Risk assessment

cortex-executor (EXECUTOR)
    ├─ Write tests (RED)
    ├─ Implement code (GREEN)
    └─ Refactor (REFACTOR)
```

**Mandatory Gates:**
1. Challenge generation (cannot skip)
2. DoR approval (must wait for "proceed" / "yes" / "approve")
3. TDD enforcement (tests before code)
4. Incremental delivery (<500 LOC per increment)

**Output Format:**
- Enhanced request analysis
- Challenge questions (3-5)
- DoR table (Decision of Ready)
- Implementation steps
- Completion report with test evidence

---

### 8. INTERACTIVE Mode

**Purpose:** Exploratory conversation without TDD or DoR gates

| Component | Value |
|-----------|-------|
| **Agent** | cortex-interactive |
| **Trigger** | Recommendation/guidance requests |
| **Priority** | 3 |
| **Header** | 🧠 CORTEX Architect | Mode: Interactive |

**MCP Tool Chain:**
```
cortex_challenge()  [Optional - if generating design scenarios]
├─ Generate alternatives
├─ Compare tradeoffs
└─ Provide guidance

cortex_lens_analyze() [Context gathering]
└─ Code context for examples

cortex_total_recall() [Knowledge retrieval]
└─ Examples and patterns
```

**Agent Capabilities:**
- recommendation_generation
- tradeoff_analysis
- architecture_guidance
- pattern_explanation
- example_generation

**Characteristics:**
- ❌ No TDD enforcement
- ❌ No DoR approval gate
- ❌ No code generation
- ✅ Educational focus
- ✅ Exploratory tone
- ✅ Guidance and examples

**Output Format:**
- Conversational tone
- Examples and analogies
- Architecture diagrams (ASCII)
- Tradeoff analysis
- Best practices references

---

## Agent Capability Matrix

### Core Agents & Modes They Serve

| Agent | Modes Served | Primary Capability | Secondary Capabilities |
|-------|--------------|-------------------|------------------------|
| **cortex-environment-setup** | PRE-FLIGHT | env_validation | dependency_checking |
| **cortex-auditor** | AUDIT, META-AUDIT | code_analysis | governance_check |
| **cortex-meta-auditor** | META-AUDIT | recursive_validation | governance_check |
| **cortex-digest** | DIGEST | session_learning | pattern_identification |
| **cortex-ask-coordinator** | QUERY | knowledge_retrieval | concept_explanation |
| **cortex-phase-resolver** | PLAN | phase_management | roi_calculation |
| **cortex-master-plan-auditor** | PLAN | plan_validation | phase_coherence_check |
| **cortex-designer** | DESIGN | request_enhancement | challenge_generation |
| **cortex-holistic-validator** | DESIGN | tdd_enforcement | governance_validation |
| **cortex-interactive** | INTERACTIVE | recommendation_generation | tradeoff_analysis |
| **cortex-executor** | DESIGN | code_generation | test_writing |

### Capability-to-Mode Mapping

| Capability | Modes | Agents |
|-----------|-------|---------|
| **code_analysis** | AUDIT, META-AUDIT | cortex-auditor, cortex-lens |
| **security_scanning** | AUDIT, DESIGN | cortex-auditor, cortex-validator |
| **tdd_enforcement** | DESIGN | cortex-designer, cortex-validator |
| **code_generation** | DESIGN | cortex-executor |
| **phase_management** | PLAN | cortex-phase-resolver |
| **roi_calculation** | PLAN | cortex-phase-resolver |
| **session_learning** | DIGEST | cortex-digest |
| **knowledge_retrieval** | QUERY | cortex-ask-coordinator |
| **recommendation_generation** | INTERACTIVE, DESIGN | cortex-interactive, cortex-designer |
| **governance_check** | AUDIT, META-AUDIT, DESIGN | cortex-auditor, cortex-validator |

---

## Collaboration Patterns by Mode

### Pattern 1: PRE-FLIGHT (Solo)
```
cortex-environment-setup
└─ Single agent, no collaborators
```

### Pattern 2: AUDIT (Sequential with Optional Recursion)
```
User: /audit
    ↓
cortex-auditor (PRIMARY)
├─ P0 Checks
├─ P1 Checks  ← Issues found?
│   ├─ Yes → Invoke cortex-meta-auditor
│   │   └─ Recursive governance validation
│   └─ No → Continue
├─ P2 Checks
└─ P3 Checks
```

### Pattern 3: DIGEST (Solo)
```
cortex-digest
└─ Single agent
    ├─ Scan markers
    ├─ Extract learnings
    └─ Generate inline recommendations
```

### Pattern 4: QUERY (Solo or with Context)
```
cortex-ask-coordinator
├─ Use cortex_total_recall() for knowledge
├─ Optionally use cortex_lens_analyze() for examples
└─ Return educational response
```

### Pattern 5: PLAN (Hierarchical Resolver→Auditor)
```
cortex-phase-resolver (RESOLVER)
    ├─ Load phases
    ├─ Calculate ROI
    ├─ Display priority ranking
    └─ Wait for user selection
        ↓
cortex-master-plan-auditor (AUDITOR)
    ├─ Validate phase dependencies
    ├─ Check pre-conditions
    └─ Approve execution
        ↓
Phase selected → Execute
```

### Pattern 6: DESIGN (Hierarchical Resolver→Auditor→Executor)
```
cortex-designer (RESOLVER)
    ├─ Enhance request
    ├─ Generate challenges (3-5 questions)
    └─ Build DoR table
        ↓
User reviews → /proceed
        ↓
cortex-holistic-validator (AUDITOR)
    ├─ Pre-check TDD structure
    ├─ Validate governance requirements
    └─ Risk assessment
        ↓
cortex-executor (EXECUTOR)
    ├─ RED phase: Write failing tests
    ├─ GREEN phase: Implement code
    ├─ REFACTOR phase: Code quality
    └─ Completion report
```

### Pattern 7: INTERACTIVE (Solo with Optional Context)
```
cortex-interactive
├─ Parse question/recommendation
├─ Gather context (optional cortex_lens_analyze)
├─ Generate educational response
└─ Provide examples and guidance
```

---

## Integration Flows

### Flow 1: Simple Audit (No Implementation)
```
User: /audit
    ↓ (or: no request)
┌─────────────────┐
│ PRE-FLIGHT ✅   │ Validates environment
└────────┬────────┘
         ↓
┌─────────────────┐
│ AUDIT ✅        │ P0→P1→P2→P3 checks
│                 │ inline findings
└─────────────────┘
```

### Flow 2: Implementation Request (Full TDD)
```
User: "implement authentication feature"
    ↓
┌─────────────────┐
│ PRE-FLIGHT ✅   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ DESIGN ✅       │
├─────────────────┤
│ 1. Enhance req  │ Consider security, edge cases
├─────────────────┤
│ 2. Challenge    │ 3-5 questions for validation
├─────────────────┤
│ 3. DoR Gate     │ User must /proceed
├─────────────────┤
│ 4. RED phase    │ Write tests
├─────────────────┤
│ 5. GREEN phase  │ Implement (<500 LOC)
├─────────────────┤
│ 6. REFACTOR     │ Code quality
├─────────────────┤
│ 7. Report       │ All tests passing ✅
└─────────────────┘
```

### Flow 3: Chat Session Learning Extraction
```
User: /digest path/to/chat-session.md
    ↓
┌─────────────────┐
│ PRE-FLIGHT ✅   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ DIGEST ✅       │
├─────────────────┤
│ 1. Scan markers │
├─────────────────┤
│ 2. Extract      │
│    learnings    │
├─────────────────┤
│ 3. Validate     │
│    against DB   │
└─────────────────┘
```

### Flow 4: Phase Planning (Multi-Phase)
```
User: /plan
    ↓
┌──────────────────────┐
│ PRE-FLIGHT ✅        │
└─────────┬────────────┘
          ↓
┌──────────────────────┐
│ PLAN ✅              │
├──────────────────────┤
│ 1. Load phases       │
├──────────────────────┤
│ 2. Calculate ROI     │
├──────────────────────┤
│ 3. Display ranking   │
│    [✓] Phase 2       │
│    [→] Phase 3       │
│    [ ] Phase 4       │
└──────────────────────┘
    User selects Phase 3
        ↓
┌──────────────────────┐
│ Validate & Execute   │
├──────────────────────┤
│ cortex-master-plan   │
│ -auditor validates   │
│                      │
│ Then: Execute phase  │
│ with progress bar    │
└──────────────────────┘
```

---

## Mode Detection Logic

### Decision Tree Algorithm

```python
def detect_mode(request_context) -> Mode:
    """Determine CORTEX operating mode from request context."""
    
    # Step 1: PRE-FLIGHT (always first)
    # No decision needed - runs automatically
    mode = PRE-FLIGHT
    if not validate_environment():
        return HALT_WITH_ERROR
    
    # Step 2: Check for DIGEST (chat markers)
    if request_context.has_file:
        marker_score = count_copilot_markers(request_context.file)
        if marker_score >= 5:
            return DIGEST
    
    # Step 3: Check for explicit commands
    if request_context.command == "/audit":
        return AUDIT
    elif request_context.command == "/meta-audit":
        return META_AUDIT
    elif request_context.command == "/plan":
        return PLAN
    elif request_context.command == "/list":
        return LIST
    elif request_context.command.startswith("/ask"):
        return QUERY
    
    # Step 4: Analyze request type
    if not request_context.request:
        # No request provided
        return AUDIT
    
    request_text = request_context.request.lower()
    
    # Check for questions
    if any(kw in request_text for kw in ["how", "why", "what", "explain", "verify"]):
        return QUERY
    
    # Check for recommendations
    if any(kw in request_text for kw in ["recommend", "suggest", "tradeoff", "alternative"]):
        return INTERACTIVE
    
    # Check for implementation requests
    if any(kw in request_text for kw in ["implement", "fix", "refactor", "add", "create", "build"]):
        return DESIGN
    
    # Default: AUDIT if unclear
    return AUDIT
```

### Explicit Command Precedence

| Command | Mode | Note |
|---------|------|------|
| (none) | AUDIT | Default behavior |
| `/audit` | AUDIT | Explicit audit |
| `/meta-audit` | META-AUDIT | Self-analysis after audit |
| `/plan` | PLAN | Phase prioritization |
| `/digest` | DIGEST | Chat learning extraction |
| `/list {query}` | LIST | Tabular results |
| `/ask {topic}` | QUERY | Educational |
| `/implement {feature}` | DESIGN | TDD implementation |
| `/fix {issue}` | DESIGN | TDD bug fix |
| `/refactor {target}` | DESIGN | TDD refactoring |

---

## Token Optimization

### LENS Cache Reuse Strategy (60% Efficiency Gain)

**Problem:** Multiple agents analyzing same code file duplicates analysis

```
Without cache (inefficient):
Agent-1 analyzes file.py → 3000 tokens
Agent-2 analyzes file.py → 3000 tokens (DUPLICATE!)
Agent-3 analyzes file.py → 3000 tokens (DUPLICATE!)
Total: 9000 tokens
```

**Solution:** Shared LENS cache

```
With cache (optimized):
LENS pre-warmed: file.py analyzed once → 3000 tokens
Agent-1 uses cache → 100 tokens (cache hit)
Agent-2 uses cache → 100 tokens (cache hit)
Agent-3 uses cache → 100 tokens (cache hit)
Total: 3300 tokens (63% reduction)
```

### Context Optimization per Mode

| Mode | Context Optimization | Token Savings |
|------|----------------------|---------------|
| PRE-FLIGHT | Minimal (env only) | N/A |
| AUDIT | LENS cache for all P0-P3 checks | 40-50% |
| META-AUDIT | AUDIT findings reused | 30-40% |
| DIGEST | Previous AUDIT context | 20-30% |
| QUERY | Knowledge graph cached | 35-45% |
| PLAN | Phase metadata cached | 25-35% |
| DESIGN | LENS + git history cached | 50-60% |
| INTERACTIVE | Minimal (conversational) | 10-20% |

---

## Visual Architecture

### Complete Mode→Agent→MCP Tool Mapping Diagram

```
----------------------------------------
│                            USER REQUEST                                     │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ↓
        ┌──────────────────────────────────────────────┐
        │        PRE-FLIGHT Mode (Priority 0)          │
        │                                              │
        │  Agent: cortex-environment-setup             │
        │  Tools: cortex_validate_environment          │
        │  Status: ✅ (All environment checks pass)    │
        └────────┬─────────────────────────────────────┘
                 │
        ✅ Continue? Yes
                 │
                 ↓
----------------------------------------
│                      MODE DETECTION ROUTING                                │
----------------------------------------
│                                                                            │
│  ┌─ DIGEST? (chat markers ≥5)                                             │
│  │                                                                        │
│  ├─ /audit command?                                                       │
│  │                                                                        │
│  ├─ /meta-audit command?                                                  │
│  │                                                                        │
│  ├─ /plan command?                                                        │
│  │                                                                        │
│  ├─ /list command?                                                        │
│  │                                                                        │
│  ├─ Question detected (how/why/what)?                                     │
│  │                                                                        │
│  ├─ Recommendation request?                                               │
│  │                                                                        │
│  ├─ Implementation request (implement/fix/refactor)?                       │
│  │                                                                        │
│  └─ No request? → Default AUDIT                                           │
│                                                                            │
----------------------------------------
         │         │         │        │       │        │         │
         ↓         ↓         ↓        ↓       ↓        ↓         ↓
    DIGEST    AUDIT   META-AUDIT  PLAN   QUERY   INTERACTIVE  DESIGN
     Mode      Mode     Mode      Mode   Mode      Mode         Mode
     (P2)      (P1)     (P4)      (P2)   (P3)      (P3)         (P2)
        │         │        │        │      │         │           │
        ↓         ↓        ↓        ↓      ↓         ↓           ↓
    ┌────────────────────────────────────────────────────────────────────┐
    │  AGENT EXECUTION LAYER                                             │
    ├────────────────────────────────────────────────────────────────────┤
    │                                                                    │
    │  DIGEST:          AUDIT:           META-AUDIT:                    │
    │  cortex-digest    cortex-auditor   cortex-architect               │
    │                   + optional       + recursive                    │
    │                   cortex-meta-     validation                     │
    │                   auditor                                         │
    │                                                                    │
    │  PLAN:            QUERY:           INTERACTIVE:    DESIGN:        │
    │  cortex-phase-    cortex-ask-      cortex-         cortex-        │
    │  resolver +       coordinator      interactive     designer +     │
    │  cortex-master-                                    cortex-        │
    │  plan-auditor                                      holistic-      │
    │                                                    validator +    │
    │                                                    cortex-        │
    │                                                    executor       │
    │                                                                    │
    └──────────────────────────┬──────────────────────────────────────┘
                               │
                               ↓
    ┌────────────────────────────────────────────────────────────────────┐
    │  MCP TOOL EXECUTION LAYER                                          │
    ├────────────────────────────────────────────────────────────────────┤
    │                                                                    │
    │  All agent operations → MCP Tool Chain                             │
    │                                                                    │
    │  Key Tools:                                                        │
    │  • cortex_audit()                  - AUDIT P0-P3 checks            │
    │  • cortex_lens_analyze()           - Code intelligence             │
    │  • cortex_challenge()              - Design challenges             │
    │  • cortex_process_request()        - TDD implementation            │
    │  • cortex_plan_resolve()           - Phase prioritization          │
    │  • cortex_digest_session()         - Session learning              │
    │  • cortex_total_recall()           - Knowledge retrieval           │
    │  • cortex_validate_compliance()    - Governance checks             │
    │  • cortex_detect_duplicates()      - CORE-035 validation           │
    │  • cortex_refactor()               - Code quality                  │
    │  • cortex_git_history()            - 24h context                   │
    │                                                                    │
    └────────────────────────────────────────────────────────────────────┘
```

### Simplified Mode→Agent→Tools Flow

```
REQUEST TYPE        AGENT(S)                   PRIMARY MCP TOOLS
────────────────────────────────────────────────────────────────────
No request       → cortex-auditor          → cortex_audit +
/audit                                         cortex_lens_analyze

/meta-audit      → cortex-architect        → cortex_meta_audit +
                   + cortex-auditor           cortex_audit

File with        → cortex-digest           → cortex_digest_session +
chat markers                                  cortex_lens_analyze

Question         → cortex-ask-coordinator  → cortex_total_recall +
/ask                                          cortex_lens_analyze

/plan            → cortex-phase-resolver   → cortex_plan_resolve +
                   + cortex-master-plan-      cortex_plan_sync_status
                   auditor

Recommendation   → cortex-interactive      → cortex_challenge +
/recommend                                   cortex_lens_analyze

implement/fix/   → cortex-designer         → cortex_process_request
refactor           + cortex-holistic-         [TDD workflow:
/implement         validator +                RED→GREEN→REFACTOR]
                   cortex-executor            + cortex_challenge
                                              + cortex_refactor
```

---

## Implementation Examples

### Example 1: Simple Audit Flow

**User Input:**
```
/audit
```

**Execution:**
```python
# Step 1: PRE-FLIGHT (automatic)
pre_flight = cortex_validate_environment()
assert pre_flight.success

# Step 2: Route to AUDIT mode
mode = detect_mode(request="/audit")
# Result: AUDIT

# Step 3: Execute AUDIT workflow
auditor = get_agent("cortex-auditor")
result = auditor.run(
    mode="AUDIT",
    mcp_tools=[
        cortex_audit,
        cortex_lens_analyze,
        cortex_detect_duplicates,
    ]
)

# Step 4: Output (inline only)
print(result.findings)  # P0, P1, P2, P3 findings
print(result.recommendations)  # Actionable suggestions
```

**Output Example:**
```
## 🧠 CORTEX Architect
**Author:** Asif Hussain | **Mode:** Audit ✅

### P0 Findings (Critical)
- ❌ Missing type hints in 3 core modules
  Evidence: cortex/lens/analyzer.py (line 45-67)
  Fix: Add @override decorator and type hints

### P1 Findings (Infrastructure)
- ⚠️ Governance violation: CORE-008 (TDD)
  Evidence: 5 new functions without tests
  Fix: Add test files before implementation

### P2 Findings (Quality)
- 📊 Code duplication: 127 duplicated lines
  Evidence: mcp_executor.py ↔ router_v2.py
  Fix: Extract shared utility

### P3 Findings (Cleanup)
- 📝 Documentation: 2 undocumented functions
```

---

### Example 2: Implementation Flow with Challenge Gate

**User Input:**
```
/implement user authentication system
```

**Execution:**
```python
# Step 1: PRE-FLIGHT
pre_flight_ok = validate_environment()

# Step 2: Route to DESIGN
mode = detect_mode(request="/implement user authentication system")
# Result: DESIGN

# Step 3: DESIGN workflow - RESOLVER phase
designer = get_agent("cortex-designer")

# 3a. Enhanced Request
enhanced = designer.enhance_request(
    original="user authentication system",
    considerations={
        "security": ["password hashing", "session management"],
        "edge_cases": ["lockout attempts", "password reset"],
        "mcp_exposure": ["cortex_validate_compliance"],
    }
)

# 3b. Generate Challenge (3-5 questions)
challenges = designer.generate_challenge(
    request=enhanced,
    questions=[
        "Q1: What's your authentication flow? (JWT/Sessions/OAuth?)",
        "Q2: How do you handle rate limiting to prevent brute force?",
        "Q3: Should this support multi-factor authentication?",
        "Q4: How are passwords securely stored (bcrypt/scrypt)?",
        "Q5: What's your session timeout strategy?"
    ]
)

# 3c. Display DoR (Decision of Ready)
dor_table = designer.build_dor_table(
    requirements=enhanced.requirements,
    challenges=challenges,
    approval_needed=True
)
print(dor_table)

# 3d. Wait for approval
approval = await_user_response("proceed", "yes", "approve")
if not approval:
    return "Cancelled - user declined implementation"

# Step 4: DESIGN workflow - AUDITOR phase
validator = get_agent("cortex-holistic-validator")
pre_check = validator.pre_check(
    request=enhanced,
    validation_scope=["tdd_structure", "governance", "risk"]
)

# Step 5: DESIGN workflow - EXECUTOR phase
executor = get_agent("cortex-executor")

# 5a. RED Phase (write tests)
tests = executor.write_tests(
    module="cortex/auth/authenticator.py",
    test_framework="pytest",
    target_coverage=95
)
# Result: tests/unit/auth/test_authenticator.py (125 lines, 8 tests)

# 5b. Run tests (should fail initially)
result = run_tests("tests/unit/auth/test_authenticator.py")
assert result.failures == 8, "Tests should fail initially (RED phase)"

# 5c. GREEN Phase (implement code)
implementation = executor.implement_code(
    tests=tests,
    max_lines=450,  # <500 LOC limit
)
# Result: cortex/auth/authenticator.py (387 lines)

# 5d. Run tests (should pass)
result = run_tests("tests/unit/auth/test_authenticator.py")
assert result.passed == 8, "All tests should pass (GREEN phase)"
assert result.coverage >= 95, "Coverage should meet target"

# 5e. REFACTOR Phase (code quality)
refactored = executor.refactor_code(
    module="cortex/auth/authenticator.py",
    targets=["extract_methods", "type_hints", "docstrings"]
)

# 5f. Final validation
final_check = validator.post_check(
    code=refactored,
    tests=tests,
    validation_scope=["compliance", "governance", "performance"]
)

# 5g. Completion report
report = executor.completion_report()
print(report)
```

**DoR Table Output:**
```
┌──────────────────────────────────────┐
│        DECISION OF READY (DoR)       │
├──────────────────────────────────────┤
│ Requirement             │ Status     │
├────────────────────────┼────────────┤
│ Authentication flows   │ ✅ Defined │
│ Security requirements  │ ✅ Listed  │
│ Edge cases handled     │ ✅ Mapped  │
│ Test strategy          │ ✅ Ready   │
│ Governance compliant   │ ✅ Checked │
├──────────────────────────────────────┤
│ Challenges Addressed?   │ ✅ Yes    │
│ Risk Level             │ 🟡 Medium │
│ Proceed with impl?     │ ⏳ Awaiting approval
│                        │   /proceed, /yes, /approve
└──────────────────────────────────────┘
```

**Completion Report Output:**
```
## 🧠 CORTEX Architect
**Author:** Asif Hussain | **Mode:** Design | **Scope:** User Authentication System ✅

### ✅ Implementation Complete

#### Test Results
- RED Phase: 8 tests written, initially failing ✅
- GREEN Phase: 8 tests passing after implementation ✅
- REFACTOR Phase: Code quality improved, tests still passing ✅
- Coverage: 96% (target: 95%) ✅

#### Code Metrics
- Lines of code: 387 (target: <500) ✅
- Type hints: 100% coverage ✅
- Docstrings: 95% (7/7 public methods) ✅
- Complexity: 2.1 avg (target: <3) ✅

#### Governance Compliance
- CORE-008 (TDD): ✅ Passing (tests before code)
- CORE-011 (Type hints): ✅ 100% compliance
- CORE-012 (Docstrings): ✅ Google style
- CORE-027 (Audit trail): ✅ AC_START → AC_COMPLETE

#### Git History
- Commit: eea6ba24 (main)
- Branch: CORTEX
- Files changed: 3
- Lines added: 387
- Tests added: 8

Ready for code review! 🚀
```

---

### Example 3: PLAN Mode Phase Prioritization

**User Input:**
```
/plan
```

**Execution:**
```python
# Step 1: PRE-FLIGHT
validate_environment()

# Step 2: Route to PLAN
mode = detect_mode(request="/plan")  # Result: PLAN

# Step 3: RESOLVER Phase
resolver = get_agent("cortex-phase-resolver")

# 3a. Load phase registry
phases = resolver.load_phases(
    registry_path="cortex-registry/_cortex-master/phases/active"
)

# 3b. Calculate ROI scores
roi_scores = {}
for phase in phases:
    roi = (phase.value * phase.success_probability * phase.urgency) / phase.effort_hours
    roi_scores[phase.id] = {
        "roi": roi,
        "value": phase.value,
        "effort": phase.effort_hours,
        "probability": phase.success_probability,
    }

# 3c. Sort and display
ranked = sorted(roi_scores.items(), key=lambda x: x[1]["roi"], reverse=True)

print("Phase Priority List (ROI-ranked):")
for i, (phase_id, metrics) in enumerate(ranked[:10], 1):
    print(f"{i:2}. {phase_id:15} ROI: {metrics['roi']:.2f} | "
          f"Value: {metrics['value']:3} | "
          f"Effort: {metrics['effort']:3}h")

# 3d. Display with ASCII progress
print("""
Current Status:
[✓] Phase 80 (Agent Metadata Standardization) - 100%
[→] Phase 81 (IntentRouter Capability Routing) - 90%
[ ] Phase 82 (TBD)

Recommended Next:
[→] Phase 81 S4: Mode-Agent Mapping Documentation (ROI: 8.2)
[ ] Phase 81 S5: Advanced Integration Tests (ROI: 7.1)
[ ] Phase 82: New Project (ROI: 6.5)
""")

# Step 4: User selection
user_choice = input("Select phase: ")  # User enters "Phase 81 S4"

# Step 5: AUDITOR Phase
auditor = get_agent("cortex-master-plan-auditor")
validation = auditor.validate_phase(
    phase_id="Phase 81 S4",
    checks=["dependencies", "pre_conditions", "resource_availability"]
)

# Step 6: Execute selected phase
executor = get_phase_executor("Phase 81 S4")
executor.run_with_progress()
```

---

## Summary: Mode-Agent-MCP Integration

| Mode | Primary Agent | MCP Tool Chain | Collaboration | Output | Status |
|------|---------------|----------------|---------------|--------|--------|
| **PRE-FLIGHT** | env-setup | cortex_validate_environment | Solo | Pass/Fail | 🟢 Auto |
| **AUDIT** | auditor | cortex_audit + lens | Optional recursion | Inline findings | 🟢 Ready |
| **META-AUDIT** | architect | cortex_meta_audit | Recursive validation | Inline report | 🟢 Ready |
| **DIGEST** | digest | cortex_digest_session | Solo | Inline learnings | 🟢 Ready |
| **QUERY** | ask-coordinator | cortex_total_recall | Solo/context | Educational | 🟢 Ready |
| **PLAN** | phase-resolver | cortex_plan_* | Hierarchical auditor | Phase ranking | 🟢 Ready |
| **DESIGN** | designer | cortex_process_request | Hierarchical auditor+executor | Full TDD | 🟢 Ready |
| **INTERACTIVE** | interactive | cortex_challenge | Solo/context | Guidance | 🟢 Ready |

---

**Document Status:** ✅ Phase 81 Stage 4 Complete  
**Integration:** All 8 modes documented with agent teams and MCP tool chains  
**Ready for:** Production deployment and team reference

