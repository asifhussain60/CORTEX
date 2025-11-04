# KDS BRAIN Architecture (v6.0)

**Active Location:** `KDS/kds-brain/`  
**Organization:** Flat files implementing 5-tier conceptual architecture  
**Status:** ✅ Production (All agents active)  
**Last Updated:** 2025-11-04

---

## Overview

The KDS BRAIN is a **Biologically-Inspired Reasoning and Adaptive Intelligence Network** that simulates human cognition to manage AI context efficiently across multiple timescales and abstraction levels.

**Key Philosophy:**
> "Application context is transient, KDS intelligence is permanent"

The BRAIN uses a **5-tier architecture** conceptually modeled after human brain function, but implemented as **flat files** for simplicity and performance.

---

## 5-Tier Conceptual Architecture

### Tier 0: Instinct (Permanent Knowledge)

| Property | Value |
|----------|-------|
| **Biological Analog** | Brainstem / Basal Ganglia |
| **Implementation** | Embedded in agent logic and governance rules |
| **Resettable** | ❌ NO (Permanent KDS intelligence) |
| **Update Method** | Explicit versioning only |

**Files:**
- `prompts/internal/*.md` - Agent behaviors and workflows
- `governance/rules.md` - 17 core governance rules
- `governance/rules/*.md` - Specialized rules

**Purpose:**
- Core rules that never change without explicit decision
- Architectural patterns (SOLID, TDD, Local-First)
- Protection thresholds and confidence scoring
- Routing logic and intent detection

**Examples:**
- "Always use element IDs for Playwright selectors"
- "Test-first workflow for UI changes"
- "SOLID architecture principles"
- "Local-first, zero external dependencies"

---

### Tier 1: Working Memory (Short-term Conversation)

| Property | Value |
|----------|-------|
| **Biological Analog** | Prefrontal Cortex |
| **Implementation** | `kds-brain/conversation-*.jsonl` |
| **Resettable** | 🔄 Auto (FIFO when 21st conversation starts) |
| **Capacity** | 20 conversations + active conversation buffer |

**Files:**
- `conversation-context.jsonl` - Last 10 messages buffer (rolling)
- `conversation-history.jsonl` - Last 20 complete conversations (FIFO)


**Purpose:**
- Maintain conversation continuity ("Make it purple" resolution)
- Cross-conversation reference ("In our last conversation...")
- Active conversation never deleted (even if oldest)

**Format (JSON Lines):**
```jsonl
{"id":"conv_001","start":"2025-11-04T10:00:00Z","messages":[...],"status":"complete"}
{"id":"conv_002","start":"2025-11-04T14:30:00Z","messages":[...],"status":"active"}
```

**FIFO Behavior:**
- When conversation #21 starts → conversation #1 deleted
- Patterns extracted to Tier 2 before deletion
- No time limits - conversations preserved until FIFO

---

### Tier 2: Long-term Knowledge (Consolidated Patterns)

| Property | Value |
|----------|-------|
| **Biological Analog** | Cortex / Hippocampus |
| **Implementation** | `kds-brain/knowledge-graph.yaml` |
| **Resettable** | ✅ YES (Application-specific data cleared by amnesia) |
| **Update Trigger** | brain-updater.md (50+ events OR 24 hours) |

**File:** `knowledge-graph.yaml`

**Structure:**
```yaml
intent_patterns:         # "add button" → PLAN
file_relationships:      # Co-modification patterns  
workflow_templates:      # Proven sequences
validation_insights:     # Common mistakes
correction_history:      # Error corrections
feature_components:      # UI patterns
test_patterns:           # Successful strategies
architectural_patterns:  # Design patterns
```

**Purpose:**
- Learn from deleted conversations (extract patterns before FIFO removal)
- Accumulate validated patterns over time
- Provide context for routing and planning
- Track file co-modification history
- Remember common mistakes and corrections

**Example Patterns:**
```yaml
file_relationships:
  host_control_panel:
    confidence: 0.95
    files:
      - Components/Host/HostControlPanelContent.razor
      - Components/Host/HostControlPanelSidebar.razor
      - Services/HostControlPanelService.cs
    patterns: [blazor, signalr, realtime]
    
workflow_templates:
  ui_feature_flow:
    confidence: 0.92
    steps:
      - plan_phases
      - write_tests_first
      - implement_component
      - verify_tests
      - commit
```

---

### Tier 3: Context Awareness (Development Intelligence)

| Property | Value |
|----------|-------|
| **Biological Analog** | Associative Cortex |
| **Implementation** | `kds-brain/development-context.yaml` |
| **Resettable** | ✅ YES (Project-specific metrics) |
| **Update Trigger** | development-context-collector.md (throttled: max 1x/hour) |

**File:** `development-context.yaml`

**Structure:**
```yaml
git_activity:            # Commit history (30 days)
code_changes:            # Velocity, churn rates
kds_usage:               # Session patterns
testing_activity:        # Test creation, pass rates
project_health:          # Build status
work_patterns:           # Productivity times
correlations:            # Data-driven insights
```

**Purpose:**
- Proactive warnings ("This file is unstable, 28% churn")
- Data-driven recommendations ("Test-first = 94% success rate")
- Velocity tracking and trending
- Identify file hotspots
- Detect productivity patterns

**Example Data:**
```yaml
code_changes:
  velocity:
    week_1: 1247
    week_2: 1583
    week_3: 1124
    trend: stable
    
file_hotspots:
  - file: Components/Host/HostControlPanelContent.razor
    churn_rate: 0.28
    status: unstable
    recommendation: "Add extra testing"
    
work_patterns:
  productive_hours:
    - "10:00-12:00": 0.94  # 94% success rate
    - "14:00-16:00": 0.87
  session_duration:
    optimal: "45-60min"
    actual_avg: "52min"
```

---

### Tier 4: Event Stream (Activity Log)

| Property | Value |
|----------|-------|
| **Biological Analog** | Sensory Input Stream |
| **Implementation** | `kds-brain/events.jsonl` |
| **Resettable** | ✅ YES (Application-specific events) |
| **Retention** | Until processed by brain-updater |

**File:** `events.jsonl`

**Format (JSON Lines):**
```jsonl
{"timestamp":"2025-11-04T10:23:45Z","type":"task_complete","agent":"code-executor","task":"Add FAB pulse","files":["FAB.razor"]}
{"timestamp":"2025-11-04T10:25:12Z","type":"test_pass","test":"fab-button.spec.ts","duration":"2.3s"}
```

**Purpose:**
- Feed Tier 2 updates (brain-updater processes events)
- Audit trail of all KDS activity
- Support learning and pattern detection
- Enable retrospective analysis

**Event Types:**
- `task_start`, `task_complete`
- `test_pass`, `test_fail`
- `file_create`, `file_modify`
- `routing_decision`
- `error_correction`

---

### Tier 5: Health & Diagnostics

| Property | Value |
|----------|-------|
| **Biological Analog** | Homeostatic Systems |
| **Implementation** | Various monitoring files |
| **Resettable** | Partial (anomalies reset, reports archived) |
| **Purpose** | System health and integrity monitoring |

**Files:**
- `kds-brain/anomalies.yaml` - Protection system violations
- `reports/monitoring/` - Periodic health reports
- `reports/self-review/` - Self-review results

**Purpose:**
- Track BRAIN integrity
- Detect anomalies and violations
- Monitor system health
- Alert on issues

**Example:**
```yaml
anomalies:
  - timestamp: "2025-11-04T10:30:00Z"
    type: confidence_low
    intent: EXECUTE
    confidence: 0.65
    threshold: 0.70
    action: asked_user
    
  - timestamp: "2025-11-04T11:15:00Z"
    type: file_mismatch
    expected: HostControlPanel.razor
    actual: HostControlPanelContent.razor
    corrected: true
```

---

## How Tiers Work Together

```
USER REQUEST
    ↓
Tier 0 (Instinct) → Apply core rules, route intent
    ↓
Tier 1 (Working Memory) → Resolve "it" references from recent messages
    ↓
Tier 2 (Long-term) → Provide patterns for planning/execution
    ↓
Tier 3 (Context) → Warn about hotspots, suggest best practices
    ↓
EXECUTE TASK
    ↓
Tier 4 (Event Stream) → Log event for learning
    ↓
(Later: brain-updater.md)
    ↓
Tier 4 → Tier 2 → Update patterns from events
Tier 1 (old convo deleted) → Tier 2 → Extract patterns before deletion
```

---

## File Organization (Current Active Structure)

```
kds-brain/                           # Active brain (flat structure)
├── conversation-context.jsonl      # Tier 1: Last 10 messages
├── conversation-history.jsonl      # Tier 1: Last 20 conversations
├── knowledge-graph.yaml            # Tier 2: Consolidated patterns
├── development-context.yaml        # Tier 3: Project metrics
├── events.jsonl                    # Tier 4: Event stream
├── anomalies.yaml                  # Tier 5: Health monitoring
├── .gitignore                      # Ignore auto-generated files
└── schemas/                        # Validation schemas
    └── pr-intelligence-schema.yaml

_archive/
└── brain-hierarchical-prototype/   # v6.0 hierarchical prototype (not used)
    └── brain/
        └── ARCHIVE-README.md       # Explanation of archived structure
```

---

## Memory Update Triggers

| Event | Tier | Action |
|-------|------|--------|
| User sends message | 1 | Append to conversation-context.jsonl |
| Conversation ends | 1 | Move to conversation-history.jsonl |
| 21st conversation starts | 1 → 2 | Delete oldest, extract patterns to Tier 2 |
| Task completed | 4 | Log event to events.jsonl |
| 50+ events accumulated | 4 → 2 | brain-updater.md processes to Tier 2 |
| 24 hours passed | 4 → 2 | brain-updater.md (if 10+ events) |
| brain-updater runs | 2 → 3 | development-context-collector.md (if >1hr) |
| Anomaly detected | 5 | Log to anomalies.yaml |
| Application reset | 1,2,3,4 | Amnesia (preserve Tier 0 + generic patterns) |

---

## Amnesia (Application Reset)

**What Gets Removed (Resettable Tiers):**
- ✅ Tier 1: All conversations
- ✅ Tier 2: Application-specific patterns
- ✅ Tier 3: All development metrics
- ✅ Tier 4: All events
- ✅ Tier 5: Anomalies (reports archived)

**What Gets Preserved (Instinct Tier):**
- ❌ Tier 0: Core rules, generic patterns, governance
- ❌ Tier 2: Generic/reusable patterns (e.g., test_first_id_preparation)

**Tool:** `scripts/brain-amnesia.ps1` or `prompts/internal/brain-amnesia.md`

**Use Cases:**
- Moving KDS to a new project
- Starting fresh after experimentation
- Distributing KDS to team/new project
- Clearing old application context

**See:** `BRAIN-AMNESIA-IMPLEMENTATION.md` for complete details

---

## Required Behaviors

1. ✅ **Never modify Tier 0 instincts** without explicit versioning
2. ✅ **Learn only validated patterns** (confidence thresholds)
3. ✅ **Forget aggressively** when application resets (amnesia)
4. ✅ **Prioritize recent knowledge** over stale memory (FIFO)
5. ✅ **Ask user if confidence < threshold** (protection)
6. ✅ **Always maintain working memory context** (conversation tracking)
7. ✅ **Extract patterns before deletion** (FIFO queue management)
8. ✅ **Throttle expensive operations** (Tier 3 collection: 1x/hour max)

---

## Commands

### Query BRAIN
```markdown
#file:KDS/prompts/internal/brain-query.md

Query for: file relationships for HostControlPanel
```

### Update BRAIN
```markdown
#file:KDS/prompts/internal/brain-updater.md

Process events and update knowledge graph
```

### Reset Knowledge Layer (Amnesia)
```markdown
#file:KDS/prompts/user/kds.md

Reset BRAIN for new application
```

Or directly:
```powershell
.\KDS\scripts\brain-amnesia.ps1
```

### Collect Development Context
```powershell
.\KDS\scripts\collect-development-context.ps1
```

### View BRAIN Health
```markdown
#file:KDS/prompts/user/kds.md

launch dashboard
```

Or:
```powershell
.\KDS\scripts\launch-dashboard.ps1
```

---

## Summary

| Tier | Location | Purpose | Resettable |
|------|----------|---------|------------|
| **0: Instinct** | Agent logic + governance/ | Core rules | ❌ NO |
| **1: Working Memory** | conversation-*.jsonl | Recent conversations | 🔄 Auto-FIFO |
| **2: Long-term** | knowledge-graph.yaml | Learned patterns | ✅ YES (partial) |
| **3: Context** | development-context.yaml | Project metrics | ✅ YES |
| **4: Event Stream** | events.jsonl | Activity log | ✅ YES |
| **5: Health** | anomalies.yaml + reports/ | Diagnostics | Partial |

**Active Structure:** Flat files in `kds-brain/`  
**Conceptual Model:** 5-tier architecture with dual hemispheres (inspired by human brain)  
**Status:** ✅ Production ready (v5.x), 🎯 Hemispheres planned (v6.0)  
**All Agents:** Reference `kds-brain/` (not archived `brain/`)

---

## 🧠 v6.0 Enhancement: Dual-Hemisphere Architecture

**Planned for v6.0:** Left-Right brain specialization for optimal processing

### LEFT HEMISPHERE (Tactical Execution)
- **Focus:** TDD, code implementation, validation, error correction
- **Agents:** code-executor, test-generator, error-corrector, health-validator
- **Storage:** `kds-brain/left-hemisphere/execution-state.jsonl`

### RIGHT HEMISPHERE (Strategic Planning)
- **Focus:** Planning, pattern matching, architecture, risk assessment
- **Agents:** intent-router, work-planner, brain-query, change-governor
- **Storage:** `kds-brain/right-hemisphere/active-plan.yaml`

### CORPUS CALLOSUM (Coordination)
- **Focus:** Inter-hemisphere communication, validation loops, learning pipeline
- **Storage:** `kds-brain/corpus-callosum/coordination-queue.jsonl`

**See:** `KDS-V6-BRAIN-HEMISPHERES-DESIGN.md` for complete architecture  
**See:** `KDS-V6-PROGRESSIVE-INTELLIGENCE-PLAN.md` for implementation plan

---

**BRAIN = Stable instincts + adaptive learning + short-term focus + contextual awareness + health monitoring + specialized hemispheres**
