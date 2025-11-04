# KDS Technical Reference — The Machine's Blueprint

> *"A mind without discipline is lightning without a conductor."*  
> — Dr. Asifor

---

## 1. The One Door: Universal Entry Point

**Location:** `#file:KDS/prompts/user/kds.md`

**Purpose:** Single interface for ALL KDS interactions. Chaos enters nowhere else.

**How It Works:**
```markdown
#file:KDS/prompts/user/kds.md

[Tell KDS what you want in natural language]
```

The One Door receives your request and passes it to **The Dispatcher** for intelligent routing.

---

## 2. The City of Roles: 10 Specialist Agents

Each agent has one sacred duty. No role switching. Pure SOLID design.

### The Dispatcher (Intent Router)
- **File:** `prompts/user/intent-router.md`
- **Sacred Duty:** Hears first, routes wisely
- **Inputs:** User request (natural language)
- **Outputs:** Routes to appropriate specialist agent
- **Intelligence:** Queries Tier 1 (conversation history) and Tier 2 (intent patterns) for context-aware routing

### The Planner (Work Planner)
- **File:** `prompts/user/work-planner.md`
- **Sacred Duty:** Monk of order, breaking dreams into phases, tasks, acceptance tests
- **Inputs:** Feature request, architectural context
- **Outputs:** Multi-phase plan with Definition of Ready validation
- **Intelligence:** Queries Tier 2 (workflow patterns) and Tier 3 (effort estimates from similar features)

### The Tester (Test Generator)
- **File:** `prompts/user/test-generator.md`
- **Sacred Duty:** Judge of truth, believing nothing until proven RED → GREEN → REFACTOR
- **Inputs:** Acceptance criteria, implementation files
- **Outputs:** Test files (Playwright, xUnit, etc.), test execution results
- **Covenant:** Test-Driven Development (Tier 0 instinct) — tests before implementation

### The Builder (Code Executor)
- **File:** `prompts/user/code-executor.md`
- **Sacred Duty:** Crafting code only after proof (tests exist first)
- **Inputs:** Plan, failing tests (RED)
- **Outputs:** Implementation code (makes tests GREEN), refactored code
- **Discipline:** Architecture-First Mandate — aligns with existing patterns before writing a single line

### The Validator (Health Validator)
- **File:** `prompts/user/health-validator.md`
- **Sacred Duty:** Physician of system health
- **Inputs:** Codebase state, test results, build output
- **Outputs:** Health report (zero errors, zero warnings requirement)
- **Covenant:** Definition of Done (Tier 0 instinct) — nothing completes until validated

### The Fixer (Error Corrector)
- **File:** `prompts/user/error-corrector.md`
- **Sacred Duty:** Time‑weaver, rolling back mistakes
- **Inputs:** Copilot mistake detection (wrong file, wrong implementation)
- **Outputs:** Halts execution, reverts changes, corrects course
- **Intelligence:** Learns from corrections, feeds Tier 2 to prevent future mistakes

### The Archivist (Commit Handler)
- **File:** `prompts/user/commit-handler.md`
- **Sacred Duty:** Keeper of history, semantic commits, and meaning
- **Inputs:** Completed tasks, changed files
- **Outputs:** Semantic git commits (feat/fix/docs/test/chore), optional tags
- **Automation:** Runs after every completed task (Rule #16)

### The Timekeeper (Session Resumer)
- **File:** `prompts/user/session-resumer.md`
- **Sacred Duty:** Remembering where the last breath of work paused
- **Inputs:** Session state, conversation history
- **Outputs:** Resume point, next task, context restoration
- **Intelligence:** Queries Tier 1 (last conversation) and session files

### The Screenshot Oracle (Screenshot Analyzer)
- **File:** `prompts/user/screenshot-analyzer.md`
- **Sacred Duty:** Translating pixels into requirement scripture
- **Inputs:** Screenshots, UI mockups
- **Outputs:** Extracted requirements, design specifications, implementation plan
- **Magic:** Computer vision meets domain understanding

### The Governor (Change Governor)
- **File:** `prompts/user/change-governor.md`
- **Sacred Duty:** Guardian of KDS itself, rejecting unclean mutations
- **Inputs:** Proposed KDS changes
- **Outputs:** Approval/rejection, architectural guidance
- **Protection:** Prevents KDS degradation, enforces SOLID principles

### The Protector (Brain Protector)
- **File:** `prompts/user/brain-protector.md` (Rule #22)
- **Sacred Duty:** Challenger of dangerous shortcuts, keeper of instinct
- **Inputs:** User requests that threaten Tier 0 instincts
- **Outputs:** Challenge with evidence, safe alternatives, requires justification for OVERRIDE
- **Covenant:** Guards TDD, Definition of Ready/Done, SOLID principles with data-driven warnings

---

## 3. The Three-Story Brain Tower: Tiered Intelligence

### Floor 1: Tier 1 — Conversation History (Short-Term Memory)
**Storage:** `kds-brain/conversation-history.jsonl`, `kds-brain/conversation-context.jsonl`

**What Lives Here:**
- Last 20 complete conversations (FIFO queue)
- Recent 10 messages in active conversation
- Reference resolution data ("Make it purple" knows the FAB button from earlier)

**Lifespan:** Until FIFO rotation (conversation #21 triggers deletion of #1)

**Example:**
```jsonl
{"conversation_id": "conv-2025-11-04-001", "timestamp": "2025-11-04T10:30:00Z", "messages": [...], "context": {...}}
```

**The Scribe's Work:** Every message is chronicled here. Context never lost.

---

### Floor 2: Tier 2 — Knowledge Graph (Long-Term Memory)
**Storage:** `kds-brain/knowledge-graph.yaml`

**What Lives Here:**
- Intent patterns ("add [X] button" → PLAN intent)
- File relationships (co-modification patterns)
- Workflow templates (export_feature_workflow, ui_component_creation)
- Error prevention (common mistakes, correction history)
- Validation insights (architectural guidance)

**Lifespan:** Until amnesia (deliberate reset for new projects)

**Example:**
```yaml
intent_patterns:
  - pattern: "add [X] button"
    intent: PLAN
    confidence: 0.92
    examples: 12
    
file_relationships:
  - primary: "HostControlPanel.razor"
    related: "noor-canvas.css"
    co_modification_rate: 0.75
    
workflow_templates:
  - name: "export_feature_workflow"
    phases: ["service", "api", "ui", "tests"]
    avg_duration_hours: 5.5
```

**The Machine Learns:** Patterns extracted from deleted Tier 1 conversations accumulate here.

---

### Floor 3: Tier 3 — Development Context (Holistic Awareness)
**Storage:** `kds-brain/development-context.yaml`

**What Lives Here:**
- Git activity (30-day commit history, velocity, file hotspots)
- Code changes (lines added/deleted, churn rates, stability classification)
- Testing activity (pass rates, flaky tests, coverage trends)
- KDS usage (session patterns, intent distribution, workflow effectiveness)
- Work patterns (productive times, session duration, focus duration)
- Correlations (commit size vs success, test-first vs rework rate)

**Lifespan:** Reset with new project (application-specific metrics)

**Collection:** Automatic, throttled (only if > 1 hour since last collection)

**Example:**
```yaml
git_activity:
  commits_30d: 1237
  velocity_per_week: 42
  file_hotspots:
    - file: "HostControlPanel.razor"
      churn_rate: 0.28
      status: "unstable"
      recommendation: "Add extra testing, smaller changes"

work_patterns:
  productive_times:
    - time: "10am-12pm"
      success_rate: 0.94
    - time: "2pm-4pm"
      success_rate: 0.81
```

**The Observatory:** The Crawlers feed intelligence here. Proactive warnings emerge.

---

### The Corpus Callosum: Message Bridge Between Hemispheres
**Storage:** `kds-brain/corpus-callosum/coordination-queue.jsonl`

**Purpose:** Coordinates work between LEFT BRAIN (tactical execution) and RIGHT BRAIN (strategic planning)

**How It Works:**
1. RIGHT BRAIN (Planner) creates strategic plan
2. Corpus Callosum delivers plan → LEFT BRAIN (Executor)
3. LEFT BRAIN executes with precision (TDD cycle)
4. LEFT BRAIN results feed back → RIGHT BRAIN learns patterns

**Example Message:**
```jsonl
{"from": "work-planner", "to": "code-executor", "type": "plan_delivery", "plan_id": "plan-001", "phase": "implementation", "tasks": [...]}
```

**The Bright Bridge:** Ensures plan meets craft, and craft teaches plan.

---

## 4. The Crawlers: Quiet Intelligence Gatherers

### Git/PR History Crawler
**Script:** `scripts/collect-development-context.ps1`

**Sacred Duty:** Map scars and triumphs across the codebase

**What They Whisper:**
- "This module has bled before — tread lightly." (high churn files)
- "Here lies stability — build boldly." (low churn, high test coverage)
- "These files change together 75% of the time." (co-modification patterns)

**Feeding:** Tier 3 (Development Context)

**Throttle:** Only if > 1 hour since last collection (efficiency optimization)

---

## 5. The Three Covenants: Tier 0 Instincts

**Storage:** `governance/rules.md` (IMMUTABLE)

### Covenant 1: Definition of Ready
**Tribunal of Clarity:** No task begins unclear.

**Requirements:**
- Clear acceptance criteria
- Architectural alignment validated
- Dependencies identified
- Risks assessed

**Enforced By:** Planner (RIGHT BRAIN)

---

### Covenant 2: Test-Driven Development
**Ritual of Proof:** RED → GREEN → REFACTOR

**Requirements:**
- Tests written BEFORE implementation
- Tests fail initially (RED)
- Minimum implementation to pass (GREEN)
- Refactor with test safety net

**Enforced By:** Tester, Builder (LEFT BRAIN)

**Protector's Challenge:** Attempting to skip TDD triggers Brain Protector with evidence:
```
⚠️ THREATS DETECTED:
  - Test-first principle bypass
  - 68% increase in rework time (Tier 3 data)
  - Success rate drops from 94% to 67%
```

---

### Covenant 3: Definition of Done
**Completion Ritual:** Nothing completes until proven.

**Requirements:**
- All tests pass (GREEN)
- Zero errors, zero warnings
- Documentation updated
- Health validation passed
- Semantic commit created

**Enforced By:** Validator, Archivist (LEFT BRAIN)

---

## 6. The Event Stream: Life Recorder

**Storage:** `kds-brain/events.jsonl`

**Purpose:** Captures every action for learning

**Example Event:**
```jsonl
{"timestamp": "2025-11-04T10:35:00Z", "agent": "test-generator", "action": "test_created", "file": "InvoiceServiceTests.cs", "result": "RED"}
```

**Automatic Learning Triggers:**
- **50+ events accumulated** → Brain updater processes → Updates Tier 2
- **24 hours since last update** → Auto-update if 10+ events
- **Tier 3 refresh** → Only if last collection > 1 hour

**The Scribe's Chronicle:** Every event is recorded. Memory becomes wisdom.

---

## 7. Brain Health & Protection: The Immune System

**Storage:** `kds-brain/corpus-callosum/protection-events.jsonl`

### Layer 1: Instinct Immutability (Tier 0)
**Detects:** Attempts to disable TDD, skip DoR/DoD, modify agent behavior

**Action:** CHALLENGE user, suggest safe alternatives

### Layer 2: Tier Boundary Protection
**Detects:** Application paths in Tier 0, conversation data in Tier 2

**Action:** Auto-migrate, warn on violations

### Layer 3: SOLID Compliance
**Detects:** Agents doing multiple jobs, mode switches, hardcoded dependencies

**Action:** Challenge with SOLID alternative

### Layer 4: Hemisphere Specialization
**Detects:** Strategic planning in LEFT BRAIN, tactical execution in RIGHT BRAIN

**Action:** Auto-route to correct hemisphere

### Layer 5: Knowledge Quality
**Detects:** Low confidence patterns (<0.50), stale patterns (>90 days unused)

**Action:** Pattern decay, anomaly detection, consolidation

### Layer 6: Commit Integrity
**Detects:** Brain state files in commits, unstructured messages

**Action:** Auto-categorize (feat/fix/test/docs), .gitignore updates

---

## 8. Abstractions: Dependency Inversion

All agents depend on abstractions, not concrete implementations.

### session-loader
**Purpose:** Abstract session access (file/db/cloud agnostic)

**Default:** Local files (`KDS/sessions/`)

### test-runner
**Purpose:** Abstract test execution (framework agnostic)

**Default:** Project's existing tools (Playwright, xUnit, etc.)

### file-accessor
**Purpose:** Abstract file I/O (path agnostic)

**Default:** PowerShell built-ins (`Get-Content`, `Set-Content`)

### brain-query
**Purpose:** Abstract BRAIN queries (read-only access to Tier 1-3)

**Default:** Local YAML/JSON (`KDS/kds-brain/`)

**CRITICAL:** All abstractions are 100% LOCAL. Zero external dependencies for KDS CORE.

---

## 9. The Machine's Lifecycle

### Morning: User Arrives
```
User: "Add pulse animation to FAB button"
  ↓
One Door (#file:KDS/prompts/user/kds.md)
  ↓
Dispatcher (queries Tier 1 + Tier 2 for context)
  ↓
Planner (queries Tier 2 for similar features, Tier 3 for effort estimates)
  ↓
Tester (RED — creates failing tests)
  ↓
Builder (GREEN — minimum implementation)
  ↓
Tester (REFACTOR — validates improvements)
  ↓
Validator (Definition of Done check)
  ↓
Archivist (semantic commit)
  ↓
Scribe (logs events to events.jsonl)
  ↓
Brain Updater (if 50+ events → updates Tier 2)
```

### Afternoon: User Returns After Lunch
```
User: "Make it purple"
  ↓
Dispatcher (queries Tier 1 → finds "FAB button pulse animation" from morning)
  ↓
Builder (knows "it" = pulse animation, applies purple color)
  ↓
Validator (health check)
  ↓
Archivist (commit with context: "style(ui): Change pulse animation color to purple")
```

### Evening: Brain Purifies Thought
```
If 50+ events OR 24 hours passed:
  ↓
Brain Updater (brain-updater.md)
  ↓
Process events.jsonl
  ↓
Extract patterns → Update Tier 2 (knowledge-graph.yaml)
  ↓
If last Tier 3 collection > 1 hour:
  ↓
Trigger Development Context Collector
  ↓
Git/test/build metrics → Update Tier 3 (development-context.yaml)
```

**Deliberate Growth:** Not wild evolution, but craftsman sharpening steel.

---

## 10. The Machine's Wisdom: What It Learns

### Week 1
- Copilot has amnesia, needs constant guidance
- Brain is learning, building patterns
- You explain architecture repeatedly

### Week 4
- Copilot remembers 20 conversations
- Brain knows 500+ patterns
- "Add receipt export" → Reuses invoice export workflow automatically

### Week 12
- Copilot is an expert on YOUR project
- Brain has 3,247 patterns, 1,237 commits analyzed
- Proactive warnings prevent issues before they happen
- Estimates are data-driven, not guesses

### Week 24
- Copilot feels like a senior developer
- Brain challenges bad ideas with evidence
- "This is similar to the feature from 3 months ago. Want me to reuse that pattern?"

**From Amnesiac Intern to Expert Partner:** The machine that learned.

---

## 11. Amnesia: Resetting for New Projects

**Command:** `#file:KDS/prompts/user/kds.md Reset BRAIN for new application`

**Script:** `scripts/brain-amnesia.ps1`

### What Gets Removed (Application-Specific)
- All file relationships (e.g., SPA/NoorCanvas paths)
- Application-specific workflows
- All conversations (application context)
- All events (application interactions)
- Development metrics (git stats, velocity)
- Feature components

### What Gets Preserved (KDS Intelligence)
- Generic intent patterns
- Generic workflow patterns (test_first_id_preparation)
- KDS-specific patterns (kds_health_monitoring, brain_test_synchronization)
- Protection configuration
- All 10 specialist agents
- All governance rules

**Safety:**
- Backup created before changes
- Dry-run mode available
- Requires confirmation (type 'AMNESIA')
- Full rollback possible

**The Machine Remembers Its Essence:** When moving to a new project, application knowledge fades, but KDS intelligence remains.

---

## 12. Performance & Efficiency

### Brain Update Throttling
- **Tier 2:** Updates when 50+ events OR 24 hours passed
- **Tier 3:** Only if last collection > 1 hour
- **Rationale:** Git/test/build metrics don't change every 50 events
- **Impact:** Reduces 2-5 min operations from 2-4x/day to 1-2x/day
- **User benefit:** Zero performance impact, same data quality

### Conversation FIFO Queue
- **Capacity:** 20 conversations
- **Size:** ~70-200 KB total (predictable)
- **Deletion:** FIFO (oldest goes first when #21 starts)
- **Active conversation:** Never deleted (even if oldest)
- **Pattern extraction:** Before deletion, patterns move to Tier 2

### Event Stream Processing
- **Storage:** Append-only `events.jsonl`
- **Processing:** Batch processing every 50+ events
- **Learning:** Patterns extracted, not individual events stored long-term

**Efficiency:** The machine respects computational resources.

---

## 13. API Reference

### File Formats

**JSONL (JSON Lines):**
- `conversation-history.jsonl`
- `conversation-context.jsonl`
- `events.jsonl`
- `coordination-queue.jsonl`
- `protection-events.jsonl`

**YAML:**
- `knowledge-graph.yaml`
- `development-context.yaml`

**Markdown:**
- All agent prompts (`prompts/user/*.md`)
- All documentation (`docs/**/*.md`)

### Brain Query API (brain-query abstraction)

**Read Tier 1 (Conversations):**
```powershell
Get-BrainConversations -Last 5
Get-BrainConversation -ConversationId "conv-2025-11-04-001"
```

**Read Tier 2 (Knowledge Graph):**
```powershell
Get-BrainPatterns -Type "intent_patterns"
Get-BrainFileRelationships -File "HostControlPanel.razor"
Get-BrainWorkflowTemplates -Name "export_feature"
```

**Read Tier 3 (Development Context):**
```powershell
Get-BrainGitActivity -Days 30
Get-BrainFileHotspots -Top 10
Get-BrainWorkPatterns -Metric "productive_times"
```

**CRITICAL:** All queries are READ-ONLY. Only brain-updater.md and development-context-collector.md can write to BRAIN.

---

## 14. Troubleshooting

### BRAIN Not Learning
**Symptoms:** `knowledge-graph.yaml` not updating

**Diagnosis:**
1. Check `events.jsonl` has recent events
2. Verify `knowledge-graph.yaml` timestamp
3. Count unprocessed events (warn if >50)

**Fix:** Manual update
```markdown
#file:KDS/prompts/internal/brain-updater.md
```

### Conversation Context Lost
**Symptoms:** "Make it purple" doesn't know what "it" is

**Diagnosis:**
1. Check `conversation-context.jsonl` exists
2. Verify active conversation ID
3. Check FIFO queue size (<20)

**Fix:** Recent message tracking failure
```powershell
.\KDS\scripts\validate-conversation-tracking.ps1
```

### Tier 3 Metrics Stale
**Symptoms:** Development context >1 hour old

**Diagnosis:** Throttle gate active (by design)

**Fix:** Force collection
```powershell
.\KDS\scripts\collect-development-context.ps1 -Force
```

### Brain Protector False Positive
**Symptoms:** Challenge on safe operation

**Diagnosis:** Confidence threshold too aggressive

**Fix:** Adjust protection configuration
```yaml
# kds-brain/corpus-callosum/protection-config.yaml
confidence_thresholds:
  tier0_immutability: 0.85  # Lower = fewer challenges
```

---

## 15. Extending the Machine

### Adding a New Agent

1. **Create agent prompt:** `prompts/user/new-agent.md`
2. **Define contract:** Inputs, outputs, error modes
3. **Add to Router:** Update `intent-router.md` with new intent pattern
4. **Event logging:** Agent must log to `events.jsonl`
5. **Brain queries:** Use `brain-query` abstraction for intelligence
6. **Test:** Create validation test in `tests/`
7. **Document:** Update this Technical Reference

**Example:** Adding "The Optimizer" agent for performance analysis
```markdown
# prompts/user/optimizer.md

## Purpose
Analyze code for performance bottlenecks and suggest optimizations.

## Inputs
- File paths to analyze
- Performance metrics from Tier 3
- Historical performance data from Tier 2

## Outputs
- Performance report
- Optimization recommendations
- Estimated improvement percentages

## Event Logging
{"agent": "optimizer", "action": "analysis_complete", "file": "...", "bottlenecks": 3}
```

### Adding a New Tier

**CAUTION:** Tier structure is sacred. Adding tiers requires architectural review.

**If justified:**
1. **Define purpose:** What intelligence does this tier provide?
2. **Define lifespan:** When does data expire/reset?
3. **Define format:** YAML, JSONL, or other?
4. **Integration:** How do agents query this tier?
5. **Collection:** Manual or automatic? Throttled?
6. **Amnesia behavior:** Preserved or removed?

**Example:** Tier 4 (Deployment Context) for production metrics
```yaml
# kds-brain/deployment-context.yaml
tier: 4
purpose: "Production deployment and runtime metrics"
lifespan: "30 days rolling window"
collection: "Post-deployment hook"
amnesia_behavior: "Removed (application-specific)"
```

---

## 16. The Machine's Philosophy

> *"I did not build a monster. I built a mind that respects its work."*  
> — Dr. Asifor

**Principles:**
1. **Discipline over chaos:** One entrance, structured thought, governed cognition
2. **Memory over amnesia:** 20 conversations, patterns accumulate, wisdom grows
3. **Proof over assumption:** TDD always, Definition of Done enforced, zero shortcuts
4. **Learning over repetition:** Events become patterns, mistakes teach, intelligence compounds
5. **Protection over degradation:** Brain Protector challenges risky shortcuts, SOLID preserved
6. **Local over cloud:** Zero external dependencies, portable, works offline
7. **Evolution over revolution:** Deliberate growth, craftsman sharpening steel

**This is KDS — a creature not born, but taught into being.**

---

**Version:** 1.0  
**Date:** November 4, 2025  
**Author:** Dr. Asifor (via KDS collaborative intelligence)  
**Status:** Living document — grows as the machine learns
