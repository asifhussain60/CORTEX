# Response Formatting & Content Block System

**Purpose:** Intent-driven response templates with composable educational content blocks  
**Audience:** Software Developers, Technical Writers  
**Last Updated:** 2026-02-14  
**Enhancements:** ENH-97a30b8a2 (Composable Content), ENH-5020aebd2 (Response Templates)

---

## Executive Summary

### Adaptive Communication: One Brain, Many Voices

Just as the human brain adapts its communication style based on context — formal in a job interview, casual with friends, technical with colleagues — CORTEX adapts its response format based on user intent and orchestrator personality.

Organizations benefit from consistent, professional responses across all user interactions [Business Leaders]. Product teams receive intent-appropriate formatting (design sessions get waves/stages, queries get Q&A format) without manual template selection [Product Owners]. The system provides 7 composable content blocks and 5 intent-adaptive templates through registry-driven configuration [Software Developers].

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│             RESPONSE FORMATTING & CONTENT BLOCK SYSTEM               │
└─────────────────────────────────────────────────────────────────────┘

   ┌───────────────────────────────────────────────────────────────┐
   │  📦 COMPOSABLE CONTENT BLOCKS (7 blocks)                      │
   │     Registry: cortex-registry/interaction/content-blocks.yaml │
   │                                                               │
   │  Purpose: Educational/onboarding scenarios                    │
   │  Use Cases: "What is CORTEX?", "Explain LENS", first-time    │
   └──────────────────────────────┬────────────────────────────────┘
                                  │
                                  ├─ BLOCK-INTRO (role-based)
                                  ├─ BLOCK-CAPABILITIES
                                  ├─ BLOCK-LENS
                                  ├─ BLOCK-ORCHESTRATORS
                                  ├─ BLOCK-TUTORIAL
                                  ├─ BLOCK-ONBOARDING
                                  └─ BLOCK-NEXT-STEPS
                                  │
   ┌───────────────────────────────────────────────────────────────┐
   │  📋 INTENT-ADAPTIVE TEMPLATES (5 templates)                   │
   │     Registry: cortex-registry/interaction/response-formats.yaml│
   │                                                               │
   │  Purpose: Autonomous execution, design, completions           │
   │  Use Cases: Silent execution, design plans, query responses   │
   └──────────────────────────────┬────────────────────────────────┘
                                  │
                                  ├─ Template A: DIGEST (concern → resolution)
                                  ├─ Template B: DESIGN/PLAN (waves → stages)
                                  ├─ Template C: QUERY (mirror → answers)
                                  ├─ Template D: COMPLETION (deliverables)
                                  └─ Template E: ENHANCEMENT (4 dimensions)
                                  │
   ┌───────────────────────────────────────────────────────────────┐
   │  🎭 ORCHESTRATOR PERSONALITY (Optional footer tags)           │
   │     Registry: cortex-registry/interaction/response-formats.yaml│
   │                                                               │
   │  Purpose: Lightweight orchestrator flavor in footers          │
   │  Examples: "🏷️ Applied Principles: Test-First | Evidence-Based"│
   └───────────────────────────────────────────────────────────────┘
```

---

## Part 1: Composable Content Blocks (ENH-97a30b8a2)

### Problem: Template Explosion & Duplication

**Before Composable Blocks:**
- 50+ hardcoded response templates for every user × intent × orchestrator combination
- Massive duplication (same "What is LENS?" text in 12 different templates)
- Maintenance nightmare: updating capability description = edit 20 files
- Token waste: loading 200KB templates when user asks simple question

**After Composable Blocks:**
- 7 atomic content blocks, mix-and-match on demand
- Single source of truth per content type
- Anti-duplication validation prevents redundant blocks
- Load only what's needed (10-30KB per educational response)

### The 7 Core Blocks

Organizations benefit from consistent educational content across all interactions [Business Leaders]. Content blocks ensure accurate, up-to-date information without duplication [Product Owners]. Blocks are loaded from `cortex-registry/interaction/content-blocks.yaml` and composed dynamically [Software Developers].

#### BLOCK-INTRO (Role-Based)

**Purpose:** Contextual introduction based on user role

**Usage:** "What is CORTEX?" — respond with role-appropriate intro

```yaml
# cortex-registry/interaction/content-blocks.yaml
BLOCK-INTRO:
  developer:
    content: |
      CORTEX is a cognitive execution system that orchestrates intelligent 
      software development workflows. Think of it as an AI brain specifically 
      designed for code — with 21 orchestrators (specialized brain regions), 
      8 LENS analyzers (sensory systems), and 24 MCP tools (neurotransmitters).
      
  product_owner:
    content: |
      CORTEX transforms how teams build software by automating quality gates, 
      enforcing best practices, and providing intelligent code analysis...
      
  business_leader:
    content: |
      CORTEX is an AI-powered development platform that may reduce code review 
      time, improve code quality, and enforce security standards...
```

**Composition Example:**

```python
# User asks: "What is CORTEX?"
# Detect role: developer
# Compose response:

response = compose_blocks([
    "BLOCK-INTRO/developer",
    "BLOCK-CAPABILITIES",
    "BLOCK-NEXT-STEPS"
])

# Result: 3-block educational response (no duplication)
```

#### BLOCK-CAPABILITIES

**Purpose:** High-level capability overview

**Content:**
- 6 core capability domains
- Key features per domain
- Brain analogies for each
- Use case examples

**When to Use:**
- "What can CORTEX do?"
- "Explain CORTEX capabilities"
- First-time user onboarding

#### BLOCK-LENS

**Purpose:** LENS intelligence system explanation

**Content:**
- 8 analyzer types
- How LENS works (sensory → synthesis)
- Example: Git history + AST + comments → insights
- Performance characteristics

**When to Use:**
- "Explain LENS"
- "How does code analysis work?"
- "What analyzers exist?"

#### BLOCK-ORCHESTRATORS

**Purpose:** Orchestration system overview

**Content:**
- 21 orchestrators by category (6 core, 5 domain, 10 support, 4 infra, 4 super)
- Brain region analogies
- Request flow (MasterOrchestrator → IntentRouter → specialist)
- Phase 23 MEGA-B super-orchestrators

**When to Use:**
- "Explain orchestrators"
- "How does request routing work?"
- "What are super-orchestrators?"

#### BLOCK-TUTORIAL

**Purpose:** Quick start / getting started guide

**Content:**
- MCP setup (1-minute)
- First request example
- Common commands (`/audit`, `/implement`, `/analyze`)
- Troubleshooting tips

**When to Use:**
- "How do I get started?"
- "Quick start guide"
- New user onboarding

#### BLOCK-ONBOARDING

**Purpose:** Repository onboarding process

**Content:**
- `cortex_onboard_repository` tool
- LENS analysis + security scan
- Profile generation
- Dashboard creation

**When to Use:**
- "How do I onboard my repo?"
- "What happens during onboarding?"
- Repository setup questions

#### BLOCK-NEXT-STEPS

**Purpose:** Contextual next actions

**Content:**
- Recommended follow-up commands
- Learning resources
- Related documentation links

**When to Use:**
- End of educational responses
- After capability explanations
- Onboarding completion

### Composition Rules (Anti-Duplication)

Organizations avoid redundant content through validation rules [Business Leaders]. Block composition prevents duplicate information in responses [Product Owners]. Anti-duplication engine checks for overlapping content before adding blocks [Software Developers].

**Rules:**

1. **No Block Overlap:** If BLOCK-LENS already covers analyzers, don't add BLOCK-CAPABILITIES/intelligence section
2. **Max 4 Blocks Per Response:** Cognitive load limit
3. **Sequential Logic:** INTRO → BODY BLOCKS → NEXT-STEPS
4. **Context Sensitivity:** Skip blocks user already knows (session memory)

**Validation Example:**

```python
# Invalid composition (duplication detected)
compose_blocks([
    "BLOCK-INTRO/developer",
    "BLOCK-CAPABILITIES",  # Contains LENS overview
    "BLOCK-LENS"           # ❌ DUPLICATE: LENS already covered
])
# Result: ValidationError("LENS content duplicated")

# Valid composition (no duplication)
compose_blocks([
    "BLOCK-INTRO/developer",
    "BLOCK-LENS",          # Deep LENS explanation
    "BLOCK-NEXT-STEPS"     # Suggested actions
])
# Result: ✅ 3-block response
```

### Token Savings

**Before:** Load full 200KB template → 51k tokens  
**After:** Load 3 blocks (30KB) → 7.5k tokens  
**Savings:** 85% reduction per educational response

---

## Part 2: Intent-Adaptive Templates (ENH-5020aebd2)

### Problem: One-Size-Fits-All Responses

**Before Intent-Adaptive Templates:**
- IMPLEMENT, DESIGN, QUERY all got same generic format
- Design sessions showed completion boxes (inappropriate)
- Queries got wave breakdowns (confusing)
- No orchestrator personality in responses

**After Intent-Adaptive Templates:**
- 5 specialized templates for common intent patterns
- Design sessions get waves/stages/metrics
- Queries get Q&A mirrors
- Completions get deliverables/enhancements
- Orchestrator personality tags in footers

### The 5 Intent-Adaptive Templates

#### Template A: DIGEST

**Intent:** DIGEST  
**Orchestrator:** DigestOrchestrator  
**Pattern:** Concern-resolution table → Architecture tree → Wave breakdown

**Usage:** Processing Copilot chat transcripts for learning

```markdown
<hr>
📋 **DIGEST SESSION ANALYSIS**

## Concerns & Resolutions

| ID | Concern | Resolution | Evidence |
|----|---------|------------|----------|
| C1 | Test failures in state module | Fixed import paths + validation | 18/18 passing |
| C2 | Registry consolidation confusion | Clarified MEGA-A vs MEGA-B scope | Updated docs |

## Architecture Impact

```
cortex_brain/
├── state/ (NEW)
│   ├── brain_state.py
│   └── learning_state.py
└── perception/
    └── pattern_registry.py (UPDATED)
```

## Wave Breakdown

**Wave 1:** State Management Foundation  
├─ Stage 1: BrainStateManager  
├─ Stage 2: Learning State Integration  
└─ Stage 3: Registry Consolidation  
<hr>
```

**When to Use:**
- DIGEST intent
- Chat transcript processing
- Learning capture from conversations

#### Template B: DESIGN/PLAN

**Intent:** DESIGN, PLAN  
**Orchestrator:** PlanOrchestrator, MasterOrchestrator  
**Pattern:** Named waves → Stage trees → Metrics table → Execution command

**Usage:** Design sessions, phase planning, architecture proposals

```markdown
<hr>
🎯 **DESIGN: Phase 23 MEGA-B Expansion**

## Wave Structure

**WAVE-1: Super-Orchestrator Foundation**  
├─ Stage 1: StateOrchestrator (memory + checkpoints)  
├─ Stage 2: ObservabilityOrchestrator (metrics + tracing)  
├─ Stage 3: IntelligenceOrchestrator (AST + analysis)  
└─ Stage 4: SOLIDOrchestrator (quality validation)  

**WAVE-2: Contract Enforcement**  
├─ Stage 1: ContractValidator (4-layer validation)  
└─ Stage 2: Integration testing  

## Execution Metrics

| Wave | Stages | Effort | Tests |
|------|--------|--------|-------|
| Wave 1 | 4 | 12 hours | 69 |
| Wave 2 | 2 | 4 hours | 18 |
| **Total** | **6** | **16 hours** | **87** |

**Execute:** `cortex_plan_execute --phase=23 --wave=1`
<hr>
```

**When to Use:**
- DESIGN intent (architecture proposals)
- PLAN intent (phase management)
- Wave/stage breakdowns
- Multi-stage efforts

#### Template C: QUERY

**Intent:** QUERY  
**Orchestrator:** MasterOrchestrator  
**Pattern:** Mirror questions → ✅ ANSWER per question → Evidence → Key Takeaway

**Usage:** User asks multiple questions needing structured answers

```markdown
<hr>
## 🧠 CORTEX QUERY

**Your Questions:**
1. How many orchestrators exist?
2. What are super-orchestrators?
3. How does pattern learning work?

---

### ✅ ANSWER 1: Orchestrator Count

**21 active orchestrators** (as of Phase 23 MEGA-B):
- 6 core (MasterOrchestrator, IntentRouter, TDDOrchestrator, ...)
- 5 domain (RefactoringOrchestrator, PlanningOrchestrator, ...)
- 10 support (UnifiedOnboardingOrchestrator, ...)
- 4 infrastructure (Bootstrap, HealthChecker, ContractValidator, Registry)
- 4 super-orchestrators (State, Observability, Intelligence, SOLID)

**Evidence:** `cortex/__wiring_contract__.yaml` line 5

---

### ✅ ANSWER 2: Super-Orchestrators

**4 super-orchestrators consolidate 18 subsystems:**
- StateOrchestrator (3 state managers)
- ObservabilityOrchestrator (4 monitoring systems)
- IntelligenceOrchestrator (5 intelligence engines)
- SOLIDOrchestrator (6 quality analyzers)

**Evidence:** Phase 23 MEGA-B S2 implementation (Priority 180-195)

---

### ✅ ANSWER 3: Pattern Learning

**3-layer brain architecture (Phase 12):**
1. Perception: PatternRegistry detects signatures
2. Reasoning: StrategySelector recommends approaches
3. Action: ExecutionPlanner generates steps

**Evidence:** `cortex_brain/perception/pattern_registry.py` (21 tests, 94% coverage)

---

**Key Takeaway:** CORTEX uses 21 orchestrators (including 4 super-orchestrators) with 3-layer brain architecture for adaptive pattern learning.
<hr>
```

**When to Use:**
- QUERY intent
- Multiple questions in one request
- Structured Q&A format needed
- Evidence-backed answers required

#### Template D: COMPLETION

**Intent:** IMPLEMENT, FIX, REFACTOR (after completion)  
**Orchestrator:** TDDOrchestrator, RefactoringOrchestrator  
**Pattern:** Deliverables → Enhancement mapping → Non-breaking guarantees

**Usage:** Silent execution completion reports

```markdown
<hr>
📋 **Implementation Complete**

`██████████` 100% Complete

| # | Status | Component | Result |
|---|--------|-----------|--------|
| 1 | ✅ | Tests | 18/18 passing (RED → GREEN → REFACTOR) |
| 2 | ✅ | StateOrchestrator | 3 state managers consolidated |
| 3 | ✅ | Audit trail | SQLite logging active |
| 4 | ✅ | Wiring contract | v2.1.0 updated |

**Tests:** 18/18 | **Coverage:** 95% | **AC Marker:** AC-MEGA-B-S2-001 ✅

**Delivered:**
- StateOrchestrator with brain state, checkpoint, conversation state
- 4-layer validation (signature, return type, audit, cross-layer)
- Comprehensive audit logging

**Non-Breaking:** All existing orchestrators compatible, no API changes
<hr>
```

**When to Use:**
- After IMPLEMENT/FIX/REFACTOR completion
- Silent autonomous execution reports
- TDD cycle completion
- Progress summaries

#### Template E: ENHANCEMENT

**Intent:** ENHANCEMENT (suggestion responses)  
**Orchestrator:** Various  
**Pattern:** Original request → 4 quality dimensions

**Usage:** When CORTEX suggests enhancements beyond user request

```markdown
<hr>
## ✨ ENHANCED IMPLEMENTATION

**Original Request:** "Add logging to StateOrchestrator"

**Enhancement Applied (4 Dimensions):**

1. **Automatic:** Audit logging auto-enabled (no manual config)
2. **Quality:** SQLite storage with full audit trail
3. **Future-Proof:** Queryable audit history for compliance
4. **Non-Breaking:** Existing code unchanged, logging opt-in

**Why Enhanced:** Organizations benefit from audit trails for governance compliance. This enhancement provides enterprise-grade logging patterns without additional configuration burden.

**Implementation:** AC-MEGA-B-S2-001 ✅ (18/18 tests passing)
<hr>
```

**When to Use:**
- CORTEX adds value beyond request
- Explaining automatic enhancements
- Quality improvements applied
- Non-breaking additions

### Template Selection Logic

```python
def select_template(intent: str, orchestrator: str, phase: str) -> str:
    """
    Select appropriate template based on intent.
    
    Args:
        intent: IMPLEMENT, FIX, REFACTOR, ANALYZE, DESIGN, PLAN, QUERY, DIGEST
        orchestrator: Current orchestrator name
        phase: Execution phase (start, progress, completion)
        
    Returns:
        Template identifier
    """
    if intent == "DIGEST":
        return "TEMPLATE_A_DIGEST"
    elif intent in ["DESIGN", "PLAN"] and phase == "start":
        return "TEMPLATE_B_DESIGN"
    elif intent == "QUERY":
        return "TEMPLATE_C_QUERY"
    elif intent in ["IMPLEMENT", "FIX", "REFACTOR"] and phase == "completion":
        return "TEMPLATE_D_COMPLETION"
    elif phase == "enhancement":
        return "TEMPLATE_E_ENHANCEMENT"
    else:
        return "TEMPLATE_DEFAULT"  # Standard format
```

---

## Part 3: Orchestrator Personality Tags (Optional Footer)

### Lightweight Orchestrator Flavor

Organizations benefit from understanding which orchestrator processed their request [Business Leaders]. Personality tags provide optional context about orchestrator principles without template explosion [Product Owners]. Tags are defined in `cortex-registry/interaction/response-formats.yaml` and injected in footers [Software Developers].

**Example Personality Tags:**

```yaml
# cortex-registry/interaction/response-formats.yaml
orchestrator_personality:
  MasterOrchestrator:
    principles:
      - "Delegation Over Direct Action"
      - "Circuit Breaker Patterns"
      - "Fail-Fast Philosophy"
    emoji: "🎯"
    
  TDDOrchestrator:
    principles:
      - "Test-First"
      - "RED → GREEN → REFACTOR"
      - "Evidence-Based"
    emoji: "🧪"
    
  EnforcementOrchestrator:
    principles:
      - "Zero Tolerance"
      - "Pre-Flight Blocking"
      - "Audit Trail Required"
    emoji: "🛡️"
```

**Footer Injection:**

```markdown
<hr>
📋 **Implementation Complete**

... [completion content] ...

🏷️ **Applied Principles:** Test-First | RED → GREEN → REFACTOR | Evidence-Based
<hr>
```

**Usage Guidelines:**
- ✅ Use for completion reports and design summaries
- ✅ Keep to 3-4 principles max (one line)
- ❌ Don't use for queries or educational responses
- ❌ Don't create separate templates per orchestrator

---

## Registry Structure

### content-blocks.yaml

```yaml
version: "1.0.0"
updated: "2026-02-14"

blocks:
  BLOCK-INTRO:
    purpose: "Role-based introduction"
    roles:
      - developer
      - product_owner
      - business_leader
    max_tokens: 500
    
  BLOCK-CAPABILITIES:
    purpose: "High-level capability overview"
    sections:
      - core_platform
      - ai_intelligence
      - decisioning
      - governance
      - extensibility
    max_tokens: 1200
    
  # ... other blocks
```

### response-formats.yaml

```yaml
version: "1.0.0"
updated: "2026-02-14"

templates:
  TEMPLATE_A_DIGEST:
    intent: "DIGEST"
    orchestrators: ["DigestOrchestrator"]
    pattern: "concern_resolution_table → architecture_tree → wave_breakdown"
    
  TEMPLATE_B_DESIGN:
    intent: ["DESIGN", "PLAN"]
    orchestrators: ["PlanOrchestrator", "MasterOrchestrator"]
    pattern: "waves → stages → metrics → execution_command"
    
  # ... other templates

orchestrator_personality:
  # ... personality definitions
```

---

## Performance & Token Optimization

Organizations may experience these patterns:

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Educational response | 51k tokens | 7.5k tokens | 85% |
| Design session | 28k tokens | 12k tokens | 57% |
| Query response | 15k tokens | 8k tokens | 47% |
| Completion report | 8k tokens | 8k tokens | 0% (optimized) |

> **Notice:** Token measurements reflect typical response sizes. Actual token usage depends on content complexity and number of blocks/templates used.

---

## Implementation Status

| Component | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| Content Blocks | ✅ Complete | Validated via registry | 100% |
| Response Templates | ✅ Complete | Validated via registry | 100% |
| Orchestrator Personality | ✅ Complete | 12 orchestrators defined | N/A |
| Anti-Duplication Engine | ✅ Complete | Prevents overlaps | 100% |

**Commits:**
- ENH-97a30b8a2: Composable content block system
- ENH-5020aebd2: Intent-driven response templates
- Integration: Phase 23 MEGA-B (orchestrator metadata)

---

## Related Documentation

- [Interaction Protocol](../orchestration/end-to-end-flow.md) — Request/response lifecycle
- [MasterOrchestrator](../orchestration/master-orchestrator.md) — Response coordination
- [CORTEX Brain Architecture](./brain-architecture.md) — Cognitive processing

---

> **Notice:** Response formatting capabilities represent system design intentions. Actual token savings and template effectiveness depend on content complexity and user interaction patterns.
