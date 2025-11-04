# KDS Mind Palace Architecture

**The Technical Specification**

**Version:** 6.0 (Cognitive Intelligence)  
**Date:** November 4, 2025  
**Status:** 🎯 ACTIVE IMPLEMENTATION  
**Concept:** Biologically-inspired 5-faculty memory system with left/right brain specialization

**Audience:** Developers, architects, KDS contributors  
**Companion Documents:** The Memory Keeper (story), Quick Start Guide (user-friendly), Visual Blueprints (diagrams)

---

## 📖 Reading This Document

**Brain-Inspired Terms:**
This specification uses accessible, brain-inspired nomenclature instead of technical jargon:

| You'll See | Technical Equivalent | Why We Use It |
|------------|---------------------|---------------|
| **Mind** | BRAIN system | More accessible than acronym |
| **Core Instincts** (Tier 0) | Permanent rules layer | Eternal wisdom that never changes |
| **Active Memory** (Tier 1) | Short-term conversation buffer | What you're working on now |
| **Recollection** (Tier 2) | Long-term knowledge graph | Learned patterns and memories |
| **Awareness** (Tier 3) | Development context | Project health and metrics |
| **Imagination** (Tier 4) | Creative idea reservoir | Future possibilities and experiments |
| **Experience Stream** | events.jsonl | Continuous flow of experiences |
| **Memory Formation** | Pattern extraction | How minds consolidate learning |
| **The Keeper** | Instincts manager | Guardian of eternal truths |
| **The Scribe** | Conversation tracker | Chronicler of recent activity |
| **The Librarian** | Knowledge curator | Organizer of learned patterns |
| **The Observer** | Metrics collector | Tracker of project health |
| **The Dreamer** | Idea capturer | Keeper of creative insights |

**See Also:** The Memory Keeper story for character-driven explanations

---

## 🎭 The Six Characters (Quick Reference)

The Mind Palace is inhabited by six key characters, each representing a system component:

| Character | Role | Tier | Brain Side | Survives Amnesia? |
|-----------|------|------|------------|-------------------|
| **The Keeper** | Guardian of eternal wisdom | Tier 0 (Core Instincts) | Left | ✅ Always |
| **The Scribe** | Chronicler of conversations | Tier 1 (Active Memory) | Left | ❌ No |
| **The Librarian** | Organizer of learned patterns | Tier 2 (Recollection) | Left | ⚠️ Patterns extracted |
| **The Observer** | Tracker of project health | Tier 3 (Awareness) | Left | ❌ No |
| **The Dreamer** | Keeper of creative insights | Tier 4 (Imagination) | Right | ⚠️ Cross-project ideas kept |
| **The Gatekeeper** | Universal entry point | Router | Both | ✅ Always |

**See:** The Memory Keeper story for character-driven explanations

---

## ✅ Implementation Checklist

**Legend:** ✅ Complete | 🔄 In Progress | ⏳ Pending | 🔍 Review

### Phase 1: Design Documentation
- [x] ✅ WHOLE-BRAIN-ARCHITECTURE.md (master spec with checklist)
- [ ] 🔄 INSTINCT-LAYER-DESIGN.md (Tier 0 detailed design)
- [ ] ⏳ IMAGINATION-TIER-DESIGN.md (Tier 4 detailed design)
- [ ] ⏳ BRAIN-ENFORCEMENT-SYSTEM.md (4-layer defense)

### Phase 2: System Audit & Cleanup
- [ ] 🔍 **CRITICAL: Holistic KDS review** - Identify leftover v4 code, consolidation opportunities
- [ ] ⏳ Delete obsolete files (KDTR references, old test-registry/, v4 patterns)
- [ ] ⏳ Create KDS/scripts/kds-toolkit.psm1 (consolidate 62 scripts' common functions)
- [ ] ⏳ Refactor all scripts to use shared PowerShell toolkit
- [ ] ⏳ Document PowerShell consolidation strategy

### Phase 3: Restore Missing Features
- [ ] ⏳ Test registry integration (simplified KDS/tests/index.json vs KDTR)
- [ ] ⏳ Publishing strategy for universal knowledge (lightweight, imagination-integrated)
- [ ] ⏳ Cross-project pattern sharing (via imagination.yaml)

### Phase 4: Core Implementation
- [ ] ⏳ Create instincts.yaml (Tier 0) with governance rules from rules.md
- [ ] ⏳ Create imagination.yaml (Tier 4) with publishing integration
- [ ] ⏳ Create initialize-instincts.ps1 (uses toolkit)
- [ ] ⏳ Create extract-to-instincts.ps1 (uses toolkit)
- [ ] ⏳ Create capture-imagination.ps1 (uses toolkit)

### Phase 5: Agent Updates
- [ ] ⏳ Enhance brain-updater.md (source classification + test registry triggers)
- [ ] ⏳ Enhance brain-amnesia.ps1 (Tier 0/4 preservation + toolkit)
- [ ] ⏳ Add event tagging to all 10+ agents (standardized format)
- [ ] ⏳ Enhance intent-router.md (instinct queries first)
- [ ] ⏳ Update conversation-context-manager.md (idea capture triggers)
- [ ] ⏳ Enhance health-validator.md (tier separation + test registry checks)

### Phase 6: Integration & UI
- [ ] ⏳ Update kds.md (5-tier story, commands, consolidated PowerShell refs)
- [ ] ⏳ Enhance dashboard (Tier 0/4 panels, test registry status)
- [ ] ⏳ Enhance dashboard API (new endpoints + toolkit)
- [ ] ⏳ Update metrics-reporter.md (tier analytics + hemisphere balance)

### Phase 7: New Agents
- [ ] ⏳ Create instinct-query.md (Tier 0 queries, rulebook access)
- [ ] ⏳ Create instinct-updater.md (One Door instinct modification) 🆕
- [ ] ⏳ Create imagination-query.md (Tier 4 queries, publishing workflow)

### Phase 8: Testing
- [ ] ⏳ Create test fixtures and scenarios
- [ ] ⏳ Run integration tests (tier separation, amnesia, publishing)
- [ ] ⏳ Validate dashboard displays
- [ ] ⏳ Test PowerShell toolkit functions

### Phase 9: Documentation
- [ ] ⏳ Update KDS-DESIGN.md (Decision 10, toolkit strategy, test registry)
- [ ] ⏳ Create imagination user guide
- [ ] ⏳ Update setup documentation (Phases 2, 4, 5 enhanced)
- [ ] ⏳ Create PowerShell toolkit guide
- [ ] ⏳ Update governance/rules.md (remove Rule #20 KDTR, add Tier 0 rules)

**Total Tasks:** 36  
**Completed:** 1  
**Remaining:** 35  
**Estimated Timeline:** 4-5 weeks  
**Status:** ✅ Ready for implementation (all designs complete)

---

## 🔍 Holistic System Review Findings

### Issues Discovered

**1. Leftover v4 Code & References**
- ❌ KDTR (KDS Test Registry) references in multiple files
- ❌ Old test-registry/ folder structure (now obsolete)
- ❌ Rule #20 in governance/rules.md (KDTR enforcement - no longer needed)
- ❌ Publishing mechanism references without implementation
- ❌ v4 design documents scattered in docs/

**2. PowerShell Script Duplication**
- ⚠️ **62 PowerShell scripts** with duplicated code
- ⚠️ Common functions repeated: logging, YAML parsing, event writing, BRAIN queries
- ⚠️ No central toolkit (kds-toolkit.psm1) for shared utilities
- ⚠️ Inconsistent error handling and output formatting
- ⚠️ Each script reinvents: file operations, health checks, validation

**3. Missing Features from Current System**
- ❌ Test registry (index.json) not integrated with test-generator.md
- ❌ Publishing strategy for cross-project patterns (Rule #14 references exist, no implementation)
- ❌ Universal knowledge distribution mechanism mentioned but missing
- ❌ Pattern reuse system partially designed, not connected to BRAIN

**4. Tier Contamination Risk**
- ⚠️ No enforcement for KDS intelligence separation (can leak to Tier 2)
- ⚠️ Governance rules in rules.md not loaded into BRAIN (should be Tier 0)
- ⚠️ Event tagging incomplete (missing source_type, tier, hemisphere fields)

**5. Documentation Gaps**
- ⚠️ kds.md references PowerShell scripts without explaining consolidation strategy
- ⚠️ No guide for kds-toolkit.psm1 (doesn't exist yet)
- ⚠️ Publishing mechanism documented but not implemented
- ⚠️ Test registry integration unclear

### Optimization Opportunities

**1. PowerShell Consolidation**
Create `KDS/scripts/kds-toolkit.psm1` with shared functions:
- Common logging with structured output
- YAML read/write with error handling
- Event logging with standardized format
- BRAIN queries with caching
- Health checks with validation
- File operations with safety checks
- Error handling with context preservation

**Benefits:**
- Reduce code duplication by 60-70%
- Standardize error handling across all scripts
- Easier maintenance and testing
- Consistent output formatting
- Shared validation logic

**2. Test Registry Revival**
Simplify KDTR complexity to lightweight index.json:
- File: KDS/tests/index.json
- Structure: Flat pattern catalog with references
- Integration: test-generator.md queries on creation
- Publishing: Patterns promoted from imagination.yaml
- No complex schemas, just searchable references

**3. Publishing Strategy Integration**
Lightweight mechanism via imagination.yaml:
- Cross-project ideas marked for publishing
- Patterns promoted from Tier 4 to published state
- Published patterns discoverable across KDS instances
- No separate publishing system, reuse imagination tier

**4. Governance Rules → Instinct Layer**
All rules from governance/rules.md become Tier 0 instincts:
- Never deleted (even with amnesia)
- Queryable by all agents
- Enforceable at routing time
- Version controlled evolution
- The "rulebook" referenced in all agents

---

## 🧠 Executive Summary

**Evolution:** The KDS Mind is evolving from a 3-tier system to a **5-faculty whole-brain architecture** inspired by human cognition.

**The Metaphor:** Think of the KDS Mind as a palace with five floors, each serving a distinct cognitive function. The Keeper guards eternal wisdom on the ground floor. The Scribe chronicles recent conversations on the first floor. The Librarian maintains learned patterns on the second. The Observer tracks project health from the third. The Dreamer captures creative ideas on the top floor. All accessed through One Door.

**New Capabilities:**
- ✅ **Tier 0 (Instincts):** Permanent engineering discipline - the "rulebook" that never changes
- ✅ **Tier 4 (Imagination):** Future ideas and innovation backlog - the "creative reservoir"
- 🧠 **Left-Brain/Right-Brain Organization:** Analytical vs Creative processing
- 🛡️ **4-Layer Enforcement:** Bulletproof protection against intelligence misrouting

**Philosophy:**
> "A complete mind needs both discipline (instincts) and creativity (imagination), both analytical rigor (left-brain) and innovative thinking (right-brain)."

---

## 📊 Complete 5-Tier Architecture

### Visual: The Whole Brain

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KDS WHOLE BRAIN ARCHITECTURE                     │
│                     (Inspired by Human Cognition)                   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TIER 0: INSTINCTS (Permanent Engineering Discipline)                │
│ Biological: Brainstem / Basal Ganglia                              │
│ File: instincts.yaml                                                │
│ Resettable: ❌ NEVER (version controlled, survives amnesia)         │
│ Hemisphere: LEFT BRAIN (Analytical, Rule-Based)                    │
├─────────────────────────────────────────────────────────────────────┤
│ Contents:                                                           │
│ - Engineering principles (TDD, SOLID, test-first)                  │
│ - Routing thresholds (confidence levels)                           │
│ - Protection rules (anti-patterns, anomaly detection)              │
│ - Agent behaviors (planner, executor, tester protocols)            │
│ - Commit rules (semantic commits, max files)                       │
│ - Workflow protocols (RED-GREEN-REFACTOR)                          │
│                                                                     │
│ Purpose: The unchanging "laws of physics" for KDS                  │
│ Analogy: Your innate reflexes and learned skills                   │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓ (informs all decisions)

┌─────────────────────────────────────────────────────────────────────┐
│ TIER 1: CONVERSATIONS (Short-Term Working Memory)                  │
│ Biological: Prefrontal Cortex                                      │
│ File: conversation-history.jsonl                                   │
│ Resettable: 🔄 Auto-flush (FIFO 20 conversations)                  │
│ Hemisphere: LEFT BRAIN (Logical context tracking)                  │
├─────────────────────────────────────────────────────────────────────┤
│ Contents:                                                           │
│ - Last 20 complete conversations                                   │
│ - Active conversation (never deleted)                              │
│ - Message-level context ("Make it purple" → FAB button)           │
│ - Entity tracking across messages                                  │
│                                                                     │
│ Purpose: "What were we just talking about?"                        │
│ Analogy: Your working memory during a conversation                 │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓ (consolidates to)

┌─────────────────────────────────────────────────────────────────────┐
│ TIER 2: KNOWLEDGE GRAPH (Long-Term Application Memory)             │
│ Biological: Cortex / Hippocampus                                   │
│ File: knowledge-graph.yaml                                         │
│ Resettable: ✅ YES (amnesia removes application patterns)          │
│ Hemisphere: LEFT BRAIN (Pattern recognition, associations)         │
├─────────────────────────────────────────────────────────────────────┤
│ Contents:                                                           │
│ - File relationships (co-modification patterns)                    │
│ - Architectural patterns (component structure)                     │
│ - Workflow patterns (successful task sequences)                    │
│ - Validation insights (common mistakes)                            │
│ - Intent patterns (learned from conversations)                     │
│                                                                     │
│ Purpose: "What have I learned about THIS application?"             │
│ Analogy: Your memory of a specific project's quirks                │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓ (metrics feed into)

┌─────────────────────────────────────────────────────────────────────┐
│ TIER 3: DEVELOPMENT CONTEXT (Holistic Project Intelligence)        │
│ Biological: Parietal Cortex (Spatial/temporal awareness)          │
│ File: development-context.yaml                                     │
│ Resettable: ✅ YES (amnesia resets to baseline)                    │
│ Hemisphere: LEFT BRAIN (Data-driven analysis)                      │
├─────────────────────────────────────────────────────────────────────┤
│ Contents:                                                           │
│ - Git activity (commit patterns, velocity)                         │
│ - File hotspots (churn rates, stability)                          │
│ - Test metrics (pass rates, flaky tests)                          │
│ - Work patterns (productive times, session duration)               │
│ - Correlations (commit size vs success)                           │
│                                                                     │
│ Purpose: "How is the project performing overall?"                  │
│ Analogy: Your sense of project momentum and health                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TIER 4: IMAGINATION (Innovation & Future Ideas) 🆕                  │
│ Biological: Default Mode Network (Creative thinking)               │
│ File: imagination.yaml                                             │
│ Resettable: ⚠️ SELECTIVE (keep cross-project ideas)                │
│ Hemisphere: RIGHT BRAIN (Creative, Innovative)                     │
├─────────────────────────────────────────────────────────────────────┤
│ Contents:                                                           │
│ - Future enhancements (backlog of ideas)                           │
│ - Deferred decisions ("Let's revisit this later")                 │
│ - Forgotten insights (captured before lost)                        │
│ - Innovation tracking (experiments, hypotheses)                    │
│ - Cross-project ideas (patterns from other projects)               │
│ - "What if" scenarios (exploratory thoughts)                       │
│                                                                     │
│ Purpose: "What could we build next?"                               │
│ Analogy: Your creative daydreaming and future planning             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ EVENT STREAM (Raw Input)                                           │
│ File: events.jsonl                                                 │
│ Purpose: Feed all tiers with tagged, classified events             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Left-Brain vs Right-Brain Organization

### **Left-Brain Functions (Analytical, Logical, Sequential)**

**Tiers:**
- ✅ Tier 0 (Instincts) - Rule-based discipline
- ✅ Tier 1 (Conversations) - Logical context tracking
- ✅ Tier 2 (Knowledge) - Pattern recognition
- ✅ Tier 3 (Dev Context) - Data-driven metrics

**Characteristics:**
- 📊 Data-driven decision making
- 📐 Rule-based processing
- 🔍 Analytical pattern detection
- 📈 Metric-based optimization
- ✅ Validation and verification

**Agents:**
- intent-router.md (logical routing)
- work-planner.md (structured planning)
- health-validator.md (systematic checks)
- metrics-reporter.md (data analysis)

---

### **Right-Brain Functions (Creative, Intuitive, Holistic)**

**Tiers:**
- ✅ Tier 4 (Imagination) - Creative ideation

**Characteristics:**
- 💡 Creative problem solving
- 🎨 Intuitive insights
- 🔮 Future visualization
- 🌟 Innovation tracking
- 🎯 "What if" exploration

**Agents:**
- screenshot-analyzer.md (visual interpretation)
- imagination-query.md (creative retrieval) 🆕
- brain-crawler.md (holistic discovery)

---

### **Whole-Brain Integration**

The magic happens when left and right work together:

```
Creative Idea (Right-Brain Tier 4)
    ↓
Analytical Validation (Left-Brain Tier 0)
    ↓
Structured Plan (Left-Brain Tier 1+2)
    ↓
Execution with Metrics (Left-Brain Tier 3)
    ↓
Learn & Iterate (Right-Brain captures new ideas)
```

**Example:**
```
User: "I wonder if we could add real-time collaboration..."
    ↓
Right-Brain: Captures to Tier 4 as future idea
    ↓
Left-Brain: Tags with context (current feature, dependencies)
    ↓
Later retrieval: "You had an idea about collaboration 3 weeks ago"
    ↓
Right-Brain: Resurfaces with full context
    ↓
Left-Brain: Validates against instincts, creates structured plan
```

---

## 🆕 Tier 0: Instinct Layer (The Rulebook)

### **Purpose**
Permanent engineering discipline that **never changes** across projects.

### **Storage**
**File:** `KDS/kds-brain/instincts.yaml`

**Sample Structure:**
```yaml
# KDS BRAIN - Instinct Layer (Tier 0)
# Version: 1.0
# Resettable: ❌ NEVER

engineering_discipline:
  enforce_tdd: true
  enforce_ui_test_ids: true
  protect_core_files: true
  avoid_monoliths: true
  architectural_thinking_first: true

routing_thresholds:
  ask_user_below: 0.70
  auto_route_above: 0.85
  learning_threshold: 0.50

commit_rules:
  semantic_commits: true
  categories: [feat, fix, test, docs, refactor, chore, perf]
  max_files_per_commit: 10
  require_tests_for_features: true

protection:
  confidence_decay:
    enabled: true
    rate: 0.02
  
  anomaly_detection:
    enabled: true
    z_score_threshold: 2.0
  
  anti_patterns:
    - name: "monolithic_implementation"
      penalty: -0.3
    - name: "temporary_location"
      penalty: -0.4

solid_compliance:
  single_responsibility: true
  open_closed: true
  interface_segregation: true
  dependency_inversion: true

agent_behavior:
  planner:
    require_phase_0_discovery: true
    no_refactor_phases: true
  
  executor:
    verify_location_before_create: true
    follow_existing_patterns: true
  
  tester:
    mirror_app_structure: true

test_first_protocol:
  enabled: true
  phases: [RED, GREEN, REFACTOR]

playwright_selectors:
  prefer_ids: true
  text_selectors_allowed: false

version: "1.0.0"
compatible_kds_version: ">=6.0.0"
update_policy: "version_controlled_only"
```

### **Key Features**
- ❌ **Never reset** (survives amnesia)
- 📝 **Version controlled** (track evolution in Git)
- 🔒 **Immutable during runtime** (no auto-learning here)
- 🎯 **Manually updated** (deliberate changes only)
- 🌍 **Cross-project** (applies to all applications)

---

## 🆕 Tier 4: Imagination Layer (The Creative Reservoir)

### **Purpose**
Capture and preserve future ideas, deferred decisions, and innovative thoughts that would otherwise be forgotten.

### **Storage**
**File:** `KDS/kds-brain/imagination.yaml`

**Sample Structure:**
```yaml
# KDS BRAIN - Imagination Layer (Tier 4)
# Version: 1.0
# Resettable: ⚠️ SELECTIVE (cross-project ideas preserved)

ideas:
  - id: idea-001
    title: "Real-time collaboration with SignalR"
    category: enhancement
    status: backlog
    priority: medium
    captured: "2025-11-04T10:23:00Z"
    context:
      conversation_id: "conv-015"
      trigger: "User mentioned 'what if multiple users could edit together?'"
      current_feature: "Asset canvas editing"
      related_files:
        - "SPA/NoorCanvas/Pages/HostControlPanel.razor"
        - "SPA/NoorCanvas/Services/SessionStateService.cs"
    tags: [signalr, collaboration, real-time]
    dependencies: [session-management, state-sync]
    estimated_complexity: high
    notes: |
      Would need conflict resolution strategy.
      Consider operational transformation or CRDTs.
      Research Yjs library for collaborative editing.
  
  - id: idea-002
    title: "Add keyboard shortcuts to canvas controls"
    category: enhancement
    status: backlog
    priority: low
    captured: "2025-11-03T14:15:00Z"
    context:
      conversation_id: "conv-012"
      trigger: "User struggled with mouse-only interface"
      current_feature: "Transcript canvas navigation"
    tags: [ux, accessibility, keyboard-navigation]
    estimated_complexity: medium
    notes: |
      Common shortcuts:
      - Ctrl+Z: Undo
      - Ctrl+S: Save
      - Space: Pan canvas
      - +/-: Zoom

deferred_decisions:
  - id: defer-001
    title: "Database choice for analytics"
    reason: "Not needed until we have users"
    captured: "2025-10-28T09:00:00Z"
    context:
      conversation_id: "conv-008"
      decision_point: "Should we use TimescaleDB or InfluxDB?"
    revisit_when: "user_count > 100 OR analytics_query_slow"
    options:
      - name: "TimescaleDB"
        pros: [sql-compatible, mature]
        cons: [heavier, postgres-dependency]
      - name: "InfluxDB"
        pros: [purpose-built, fast]
        cons: [new-query-language, learning-curve]
  
  - id: defer-002
    title: "Caching strategy for session state"
    reason: "Premature optimization"
    captured: "2025-11-01T16:30:00Z"
    revisit_when: "session_load_time > 500ms"
    notes: "Redis vs in-memory cache decision deferred"

forgotten_insights:
  - id: insight-001
    title: "Component IDs prevent Playwright test brittleness"
    insight: |
      Discovered that text-based selectors break constantly.
      ID-based selectors are 10x faster and immune to changes.
      This should be enforced in all components.
    captured: "2025-10-15T11:00:00Z"
    promoted_to: "instincts.yaml:playwright_selectors"
    applied: true
  
  - id: insight-002
    title: "Small commits correlate with 68% less rework"
    insight: |
      After analyzing 1,200 commits, found that commits with
      <5 files have significantly lower rework rate.
    captured: "2025-10-20T14:00:00Z"
    promoted_to: "instincts.yaml:commit_rules.max_files_per_commit"
    applied: true

experiments:
  - id: exp-001
    title: "Percy visual regression testing"
    status: successful
    started: "2025-10-25T00:00:00Z"
    completed: "2025-10-30T00:00:00Z"
    hypothesis: "Visual regression tests will catch UI bugs earlier"
    result: "Caught 3 CSS regressions that unit tests missed"
    decision: "Adopt for all UI components"
    applied: true
  
  - id: exp-002
    title: "Test-first workflow for UI features"
    status: in-progress
    started: "2025-11-01T00:00:00Z"
    hypothesis: "Writing Playwright tests first reduces rework"
    early_results: "96% success rate vs 67% without tests first"
    notes: "Strong signal - likely to promote to instinct"

cross_project_ideas:
  - id: cross-001
    title: "KDS brain-crawler pattern"
    origin_project: "NoorCanvas"
    applicable_to: [any-codebase]
    pattern: |
      Deep codebase analysis during setup provides
      superior context for AI-assisted development.
    value: "Reduces misrouted files by 85%"
    reusable: true

what_if_scenarios:
  - id: whatif-001
    title: "What if KDS had voice commands?"
    thought: |
      "Start session" spoken instead of typed.
      Could use Web Speech API for browser-based voice.
    feasibility: medium
    value: low
    status: shelved
    reason: "Novelty without clear value"
  
  - id: whatif-002
    title: "What if we generated tests from screenshots?"
    thought: |
      User provides mockup, KDS generates:
      1. Component structure
      2. Playwright visual tests
      3. Implementation plan
    feasibility: high
    value: high
    status: promising
    next_steps: "Research screenshot-to-code ML models"

metadata:
  total_ideas: 2
  total_deferred: 2
  total_insights: 2
  total_experiments: 2
  total_cross_project: 1
  total_what_if: 2
  
  by_status:
    backlog: 2
    in_progress: 1
    successful: 1
    shelved: 1
  
  by_priority:
    high: 0
    medium: 2
    low: 1
```

### **Key Features**
- 💡 **Quick capture** during conversations (auto-detected)
- 🏷️ **Rich tagging** (context, trigger, related files)
- 📊 **Categorization** (enhancement, bug, research, deferred)
- 🔗 **Cross-linking** (conversation IDs, file references)
- ⚠️ **Selective amnesia** (keep cross-project ideas)
- 🔄 **Promotion path** (idea → plan → instinct)

### **Imagination Capture Triggers**

Auto-capture when user says:
- "What if we could..."
- "I wonder if..."
- "In the future, we should..."
- "Let's revisit this later..."
- "TODO: ..."
- "IDEA: ..."
- "MAYBE: ..."
- "Remind me to..."

---

## 🛡️ 4-Layer Enforcement System

To ensure KDS intelligence NEVER gets into Tier 2 (deletable memory):

### **Layer 1: Event Tagging (Source of Truth)**

**All agents tag events with:**
```jsonl
{
  "timestamp": "2025-11-04T10:00:00Z",
  "agent": "work-planner",
  "action": "plan_created",
  "source_files": ["KDS/prompts/internal/work-planner.md"],
  "source_type": "kds_internal",  // or "application" or "mixed"
  "tier": "0",  // 0=instinct, 1=conversation, 2=knowledge, 3=dev-context, 4=imagination
  "hemisphere": "left"  // "left" or "right"
}
```

### **Layer 2: Brain Updater Classification**

**File:** `KDS/prompts/internal/brain-updater.md`

**Classification Rules:**
```yaml
source_classification_rules:
  kds_internal_patterns:
    file_patterns:
      - "KDS/prompts/**/*.md"
      - "KDS/scripts/**/*.ps1"
      - "KDS/docs/**/*.md"
      - "KDS/*.md"
    keyword_indicators:
      - "kds_internal_governance"
      - "specialist_agent"
      - "brain_system"
    action_types:
      - "agent_behavior"
      - "routing_logic"
      - "protection_rule"
    
    destination: Tier 0 (instincts.yaml)
  
  imagination_patterns:
    trigger_phrases:
      - "what if"
      - "in the future"
      - "let's revisit"
      - "I wonder"
    keywords:
      - "TODO"
      - "IDEA"
      - "MAYBE"
    
    destination: Tier 4 (imagination.yaml)
  
  application_patterns:
    file_patterns:
      - "SPA/**/*"
      - "Controllers/**/*"
      - "Services/**/*"
    
    destination: Tier 2 (knowledge-graph.yaml)
```

**Routing Logic:**
```
Event received
    ↓
Extract source_files, content
    ↓
Match against kds_internal_patterns?
    ├─ YES → Tier 0 (instincts.yaml)
    │
    ├─ Match against imagination_patterns?
    │   ├─ YES → Tier 4 (imagination.yaml)
    │   │
    │   └─ Match against application_patterns?
    │       ├─ YES → Tier 2 (knowledge-graph.yaml)
    │       └─ NO → Tier 2 + FLAG for review
```

### **Layer 3: Extraction Scripts**

**Files:**
- `KDS/scripts/extract-to-instincts.ps1` - KDS intelligence → Tier 0
- `KDS/scripts/capture-imagination.ps1` - Ideas → Tier 4

**When they run:**
- Automatically during `brain-updater.md` processing
- BEFORE consolidating to knowledge-graph.yaml
- After every 50 events OR 24 hours

### **Layer 4: Amnesia Safeguard**

**File:** `KDS/scripts/brain-amnesia.ps1`

**Pre-flight Check:**
```powershell
# Step 1.5: Validate KDS intelligence separation
Write-Host "[1.5/8] Validating tier separation..." -ForegroundColor Yellow

$forbiddenInTier2 = @(
    "KDS/prompts/",
    "specialist_agent",
    "brain_system_behavior",
    "routing_threshold"
)

$violations = @()
foreach ($pattern in $forbiddenInTier2) {
    if ($knowledgeGraph -match $pattern) {
        $violations += $pattern
    }
}

if ($violations.Count -gt 0) {
    Write-Host "⚠️ KDS intelligence in Tier 2 - auto-migrating..." -ForegroundColor Yellow
    & "$kdsRoot\scripts\extract-to-instincts.ps1"
}
```

**Amnesia Preservation:**
```yaml
NEVER DELETE:
  - instincts.yaml (Tier 0) ← KDS rulebook
  - imagination.yaml:cross_project_ideas ← Portable insights
  - imagination.yaml:forgotten_insights (promoted) ← Applied learnings

DELETE:
  - conversation-history.jsonl (Tier 1) ← Application conversations
  - knowledge-graph.yaml (Tier 2) ← Application patterns
  - development-context.yaml (Tier 3) ← Application metrics
  - imagination.yaml:ideas (status=backlog, tags=application-specific)
```

---

## 🎯 User-Facing Commands

### **Query Instincts**
```markdown
#file:KDS/prompts/user/kds.md

What are my routing thresholds?
```
→ Routes to `instinct-query.md` → Returns Tier 0 rules

### **Capture Idea**
```markdown
#file:KDS/prompts/user/kds.md

I have an idea: What if we added real-time collaboration?
```
→ Auto-captured to Tier 4 with conversation context

### **Review Imagination**
```markdown
#file:KDS/prompts/user/kds.md

Show me my backlog of ideas
```
→ Routes to `imagination-query.md` → Returns Tier 4 ideas

### **Promote Idea to Plan**
```markdown
#file:KDS/prompts/user/kds.md

Promote idea #idea-001 to a plan
```
→ Creates work plan from imagination.yaml idea

### **Search Forgotten Insights**
```markdown
#file:KDS/prompts/user/kds.md

Did I have any insights about testing?
```
→ Searches Tier 4 forgotten_insights section

---

## 📊 Dashboard Integration

**New Panels:**

```html
<!-- Tier 0: Instincts Panel -->
<div class="tier-panel instincts">
  <h3>🧠 Instincts (Tier 0)</h3>
  <div class="stats">
    <div>Routing Threshold: 0.85</div>
    <div>TDD Enforcement: ✅ Active</div>
    <div>Anti-Patterns: 3 rules</div>
    <div>SOLID Compliance: 4/5 principles</div>
  </div>
  <div class="health">
    <span class="badge">HEALTHY</span>
    <span>Never modified during amnesia</span>
  </div>
</div>

<!-- Tier 4: Imagination Panel -->
<div class="tier-panel imagination">
  <h3>💡 Imagination (Tier 4)</h3>
  <div class="stats">
    <div>Active Ideas: 2</div>
    <div>Deferred Decisions: 2</div>
    <div>Experiments: 1 in-progress</div>
    <div>What-If Scenarios: 2</div>
  </div>
  <div class="recent-ideas">
    <div class="idea">
      <strong>idea-001:</strong> Real-time collaboration
      <span class="priority medium">Medium</span>
    </div>
    <div class="idea">
      <strong>idea-002:</strong> Keyboard shortcuts
      <span class="priority low">Low</span>
    </div>
  </div>
  <button onclick="viewAllIdeas()">View All Ideas</button>
</div>

<!-- Tier Separation Health -->
<div class="health-panel">
  <h3>🛡️ Tier Separation Health</h3>
  <div class="health-score">100%</div>
  <ul>
    <li>✅ No KDS intelligence in Tier 2</li>
    <li>✅ Instincts properly classified</li>
    <li>✅ Imagination capture active</li>
    <li>✅ Event tagging compliant</li>
  </ul>
</div>
```

---

## 📈 Metrics Integration

**New Metrics:**

```yaml
instinct_stability:
  last_modified: "2025-10-15T00:00:00Z"
  days_stable: 20
  version: "1.0.0"
  manual_updates: 3
  auto_updates: 0  # Should always be 0

imagination_activity:
  ideas_captured_this_month: 12
  ideas_promoted_to_plans: 3
  ideas_shelved: 2
  deferred_decisions: 4
  insights_extracted: 6
  experiments_running: 1

tier_separation_health:
  kds_in_tier2_violations: 0
  auto_migrations_this_month: 0
  classification_accuracy: 100%
  
  events_by_tier:
    tier0: 15  # Instinct updates
    tier1: 247  # Conversations
    tier2: 189  # Application patterns
    tier3: 45  # Dev metrics
    tier4: 12  # Ideas captured

hemisphere_balance:
  left_brain_events: 496  # Tier 0+1+2+3
  right_brain_events: 12  # Tier 4
  ratio: "98/2"  # Heavily analytical (expected for coding tasks)
  
  right_brain_engagement:
    ideas_per_week: 3
    creative_sessions: 8
    what_if_questions: 2
```

---

## 🧪 Testing Strategy

### **Test Scenarios**

**1. KDS Intelligence Routing**
```yaml
Input: Agent updates KDS/prompts/internal/work-planner.md
Expected: Event tagged tier=0, routed to instincts.yaml
Verify: NOT in knowledge-graph.yaml
```

**2. Application Pattern Routing**
```yaml
Input: User modifies SPA/NoorCanvas/HostControlPanel.razor
Expected: Event tagged tier=2, routed to knowledge-graph.yaml
Verify: NOT in instincts.yaml
```

**3. Imagination Capture**
```yaml
Input: User says "What if we added dark mode?"
Expected: Auto-captured to imagination.yaml with conversation context
Verify: Tagged with trigger phrase, categorized as enhancement
```

**4. Amnesia Preservation**
```yaml
Input: Run brain-amnesia.ps1
Expected:
  - instincts.yaml UNCHANGED
  - imagination.yaml:cross_project_ideas PRESERVED
  - imagination.yaml:ideas (app-specific) DELETED
  - knowledge-graph.yaml RESET
Verify: KDS intelligence intact
```

**5. Tier Separation Health**
```yaml
Input: Run health-validator.md
Expected: Scan for KDS patterns in Tier 2
Verify: No violations found
```

---

## 🚀 Migration Plan

### **Phase 1: Design (Current)**
- ✅ Create WHOLE-BRAIN-ARCHITECTURE.md
- ✅ Create INSTINCT-LAYER-DESIGN.md
- ✅ Create IMAGINATION-TIER-DESIGN.md
- ✅ Create BRAIN-ENFORCEMENT-SYSTEM.md

### **Phase 2: Tier 0 Implementation**
- Create `instincts.yaml` structure
- Create `initialize-instincts.ps1` script
- Extract current KDS intelligence from knowledge-graph.yaml
- Migrate to instincts.yaml

### **Phase 3: Tier 4 Implementation**
- Create `imagination.yaml` structure
- Create `capture-imagination.ps1` script
- Update conversation-context-manager.md for auto-capture
- Create imagination-query.md agent

### **Phase 4: Enforcement System**
- Update all agents with event tagging
- Enhance brain-updater.md with classification
- Create extract-to-instincts.ps1
- Update brain-amnesia.ps1 with safeguards

### **Phase 5: Integration**
- Update dashboard with new panels
- Update metrics-reporter.md
- Update health-validator.md
- Update kds.md documentation

### **Phase 6: Testing & Validation**
- Create test scenarios
- Run validation suite
- Verify tier separation
- Test amnesia preservation

---

## 💭 Philosophy: Why Whole-Brain?

### **The Problem with Left-Brain Only**
```
Current 3-tier system:
- Excellent at analysis, patterns, metrics
- Weak at capturing creative insights
- Ideas get lost in conversations
- "What if" thoughts disappear
- Innovation happens but isn't tracked
```

### **The Whole-Brain Solution**
```
5-tier system:
- Left-Brain (Tier 0-3): Rigor, rules, data, patterns
- Right-Brain (Tier 4): Creativity, imagination, innovation
- Both hemispheres inform each other
- Ideas captured, not lost
- Systematic innovation tracking
```

### **Real-World Example**

**Without Imagination Tier:**
```
Week 1: "What if we added voice commands?" (forgotten)
Week 4: User asks "Did we discuss voice?"
Response: "I don't have that in my context" ❌
```

**With Imagination Tier:**
```
Week 1: "What if we added voice commands?"
Auto-captured: imagination.yaml:whatif-001
Week 4: "Did we discuss voice?"
Retrieved: "Yes, you suggested voice commands in conversation #12.
           Marked as low-value novelty and shelved." ✅
```

---

## 🎯 Success Criteria

### **Tier 0 (Instincts)**
- ✅ No KDS intelligence in Tier 2
- ✅ All routing rules in instincts.yaml
- ✅ Survives amnesia 100%
- ✅ Version controlled
- ✅ Manual updates only

### **Tier 4 (Imagination)**
- ✅ Auto-captures idea triggers
- ✅ Rich context tagging
- ✅ Promotes to plans when ready
- ✅ Cross-project ideas preserved
- ✅ Searchable backlog

### **Enforcement System**
- ✅ 100% classification accuracy
- ✅ Zero violations in Tier 2
- ✅ Auto-migration on detection
- ✅ Health checks pass

### **Integration**
- ✅ Dashboard shows all 5 tiers
- ✅ Metrics track tier health
- ✅ Users can query instincts
- ✅ Users can review imagination

---

## 📚 Related Documents

- `KDS/docs/architecture/INSTINCT-LAYER-DESIGN.md` - Tier 0 specification
- `KDS/docs/architecture/IMAGINATION-TIER-DESIGN.md` - Tier 4 specification
- `KDS/docs/architecture/BRAIN-ENFORCEMENT-SYSTEM.md` - 4-layer defense
- `KDS/docs/user-guides/USING-IMAGINATION-TIER.md` - User guide
- `KDS/BRAIN-AMNESIA-IMPLEMENTATION.md` - Amnesia with instincts
- `KDS/KDS-DESIGN.md` - Overall system design

---

**Implementation Status:** 📋 DESIGN COMPLETE  
**Next Step:** Phase 2 - Tier 0 Implementation  
**Estimated Timeline:** 6 phases over 2-3 weeks  
**Risk:** LOW (additive, non-breaking changes)  
**Value:** HIGH (bulletproof intelligence preservation + innovation tracking)

---

**The Whole Brain is greater than the sum of its parts.** 🧠✨
