# CORTEX System Diagrams - Technical Visualization Prompts
**Purpose:** Generate professional system diagrams that visually reveal CORTEX architecture and design

**Target:** Google Gemini Image Generation  
**Format:** Technical diagrams only - flowcharts, sequence diagrams, architecture diagrams, UML  
**Style:** Professional engineering documentation, not cartoons

---

## 🎯 Prompt Design Guidelines

**For Technical Diagrams:**
- Use clear, professional language
- Specify diagram type explicitly (flowchart, sequence diagram, architecture diagram, UML)
- Include precise labels, annotations, and technical terminology
- Request "technical diagram style" or "software architecture diagram"
- Avoid narrative/story elements

**Bad Example (Cartoon):**
```
Create a cute robot with a brain showing...
```

**Good Example (System Diagram):**
```
Create a technical architecture diagram showing CORTEX dual-hemisphere system.
Use boxes for components, arrows for data flow, labels for each module.
Style: AWS architecture diagram, clean lines, professional color coding.
```

---

## 📐 Core Architecture Diagrams

### Diagram 1: CORTEX Complete System Architecture
```
Create a technical system architecture diagram showing CORTEX 2.0 components and data flow.

DIAGRAM TYPE: Layered architecture diagram (top-down)

LAYER 1 - Entry Point (Top):
- Box labeled "Universal Entry Point (cortex.md)"
- Single door icon
- Color: Gray

LAYER 2 - Right Brain (Strategic Planner):
- Container box labeled "RIGHT BRAIN - Strategic Planning"
- Child boxes: Intent Router, Work Planner, Brain Protector, Change Governor, Screenshot Analyzer
- Color: Orange (#FF6B35)
- Style: Hexagonal nodes, interconnected

LAYER 3 - Corpus Callosum (Bridge):
- Horizontal bar labeled "Corpus Callosum - Coordination Queue"
- Bidirectional arrows connecting Layer 2 and Layer 4
- Color: Purple (#7B1FA2)

LAYER 4 - Left Brain (Tactical Executor):
- Container box labeled "LEFT BRAIN - Tactical Execution"
- Child boxes: Code Executor, Test Generator, Error Corrector, Health Validator, Commit Handler
- Color: Blue (#0066CC)
- Style: Rectangular nodes, grid layout

LAYER 5 - Memory Tiers (Foundation):
- 5 horizontal bands stacked bottom-up:
  - Tier 0: Instinct (dark gray, lock icon)
  - Tier 1: Working Memory (light blue, SQLite icon)
  - Tier 2: Knowledge Graph (purple, network icon)
  - Tier 3: Dev Context (orange, chart icon)
  - Tier 4: Event Stream (green, log icon)

PERIPHERY - Plugin System:
- Circular nodes around edges: Cleanup, Documentation, Self-Review, Maintenance
- Dashed lines connecting to hook points

DATA FLOW:
- Arrows showing: User → Entry → Right Brain → Corpus Callosum → Left Brain → Memory Tiers
- Feedback arrows: Memory Tiers → Right Brain (learning loop)

STYLE: Modern software architecture diagram, AWS-style, clean lines, professional color palette, 
clear labels, isometric 3D perspective. Suitable for technical documentation.
```

---

### Diagram 2: Dual-Hemisphere Brain Architecture
---

### Diagram 2: Dual-Hemisphere Brain Architecture
```
Create a split-screen comparison diagram showing RIGHT BRAIN vs LEFT BRAIN architecture.

DIAGRAM TYPE: Side-by-side comparison with center bridge

LEFT PANEL - Right Brain (Strategic):
- Title: "RIGHT BRAIN - Strategic Planning"
- Component boxes arranged organically:
  * Intent Router (entry point)
  * Work Planner (strategic planning)
  * Brain Protector (rule enforcement)
  * Change Governor (architecture guardian)
  * Screenshot Analyzer (visual analysis)
- Connection style: Curved, flowing lines
- Color scheme: Orange gradient (#FF6B35 to #FF8C42)
- Icons: Lightbulb (ideas), chess piece (strategy), shield (protection)
- Labels: "Plans", "Analyzes", "Protects", "Routes"

CENTER - Corpus Callosum:
- Vertical bridge connecting both sides
- Label: "Corpus Callosum - Message Coordination"
- Arrows showing bidirectional data flow:
  * Right to Left: "Strategic Plan", "Context", "Patterns"
  * Left to Right: "Execution Results", "Test Status", "Health Metrics"
- Color: Purple gradient (#7B1FA2)
- Icon: Network/connection symbol

RIGHT PANEL - Left Brain (Tactical):
- Title: "LEFT BRAIN - Tactical Execution"
- Component boxes arranged in grid:
  * Test Generator (RED phase)
  * Code Executor (GREEN phase)
  * Error Corrector (error handling)
  * Health Validator (REFACTOR phase)
  * Commit Handler (version control)
- Connection style: Straight, precise lines
- Color scheme: Blue gradient (#0066CC to #4A90E2)
- Icons: Gear (execution), checkmark (validation), tools (building)
- Labels: "Builds", "Tests", "Fixes", "Validates"

BOTTOM SECTION - Workflow Timeline:
- Horizontal flow showing collaboration:
  1. RIGHT BRAIN: "Analyze & Plan" (3.2s)
  2. CORPUS CALLOSUM: "Transfer Plan" (0.1s)
  3. LEFT BRAIN: "Execute TDD" (3h 47m)
  4. CORPUS CALLOSUM: "Send Results" (0.1s)
  5. RIGHT BRAIN: "Update Knowledge" (2.5s)

STYLE: Technical comparison diagram, clean separation, professional engineering style, 
clear labels, suitable for architecture documentation. Use AWS architecture diagram 
aesthetic with distinct color coding.
```

---

### Diagram 3: Five-Tier Memory System
---

### Diagram 3: Five-Tier Memory System
```
Create a vertical layered architecture diagram showing CORTEX memory tiers.

DIAGRAM TYPE: Vertical stack diagram with data flow

TIER 0 (Bottom Foundation):
- Rectangle with solid border
- Label: "TIER 0: INSTINCT - Immutable Core Rules"
- Content: "TDD, SOLID, DoR/DoD, Rule #22, Brain Protection"
- Icon: Lock (protected/immutable)
- Color: Dark gray (#546E7A)
- Size: Widest (supports all other tiers)

TIER 1 (Above Tier 0):
- Rectangle
- Label: "TIER 1: WORKING MEMORY - Last 20 Conversations"
- Content: "conversation-history.jsonl, FIFO queue, <50ms queries"
- Icon: Clock + Database
- Color: Light blue (#4A90E2)
- Indicator: "8/20 capacity"

TIER 2 (Middle):
- Rectangle
- Label: "TIER 2: KNOWLEDGE GRAPH - Long-term Learning"
- Content: "knowledge-graph.yaml, 3,247 patterns, FTS5 search"
- Icon: Neural network nodes
- Color: Purple (#7B1FA2)
- Indicator: "3,247 patterns learned"

TIER 3 (Above Tier 2):
- Rectangle
- Label: "TIER 3: DEVELOPMENT CONTEXT - Project Intelligence"
- Content: "Git metrics, file hotspots, commit velocity, churn analysis"
- Icon: Bar chart/dashboard
- Color: Orange (#FF6B35)
- Indicator: "Last updated: 45 min ago"

TIER 4 (Top):
- Rectangle
- Label: "TIER 4: EVENT STREAM - Activity Log"
- Content: "events.jsonl, auto-learning triggers, 23 events pending"
- Icon: Scroll/log file
- Color: Green (#00C853)
- Indicator: "23 events pending"

DATA FLOW ARROWS:
- Vertical arrows showing:
  * Events (Tier 4) → Patterns (Tier 2)
  * Conversations (Tier 1) → Patterns (Tier 2)
  * All tiers query Tier 0 (foundation principles)
- Labels on arrows: "Extract patterns", "Query rules", "Update graph"

SIDE ANNOTATIONS:
- Query speed indicators (Tier 1: <50ms, Tier 2: <150ms, Tier 3: <200ms)
- Capacity indicators for each tier
- Update frequency (Tier 1: real-time, Tier 2: on threshold, Tier 3: hourly)

STYLE: Layered architecture diagram, clear separation between tiers, professional 
color coding, technical documentation style. Similar to OSI model or database 
architecture diagrams.
```

---

### Diagram 4: Request Flow Sequence Diagram
---

### Diagram 4: Request Flow Sequence Diagram
```
Create a UML sequence diagram showing complete request processing flow.

DIAGRAM TYPE: UML Sequence Diagram (time flows top to bottom)

ACTORS (Vertical Lifelines):
1. User
2. Entry Point (cortex.md)
3. Intent Router (RIGHT BRAIN)
4. Tier 2 (Knowledge Graph)
5. Tier 3 (Dev Context)
6. Work Planner (RIGHT BRAIN)
7. Corpus Callosum
8. Code Executor (LEFT BRAIN)
9. Test Generator (LEFT BRAIN)
10. Commit Handler (LEFT BRAIN)

SEQUENCE FLOW:
1. User → Entry Point: "Add purple button to HostControlPanel"
2. Entry Point → Intent Router: route_request()
3. Intent Router → Tier 2: query_patterns("button addition")
4. Tier 2 → Intent Router: [12 similar patterns found]
5. Intent Router → Tier 3: get_context("HostControlPanel.razor")
6. Tier 3 → Intent Router: [file hotspot, 28% churn rate]
7. Intent Router → Work Planner: create_plan()
8. Work Planner → Corpus Callosum: send_strategic_plan()
9. Corpus Callosum → Test Generator: execute_phase_1_RED()
10. Test Generator → Test Generator: create_tests() [self-call]
11. Test Generator → Corpus Callosum: tests_created(RED)
12. Corpus Callosum → Code Executor: execute_phase_2_GREEN()
13. Code Executor → Code Executor: implement_feature() [self-call]
14. Code Executor → Corpus Callosum: implementation_complete(GREEN)
15. Corpus Callosum → Commit Handler: execute_phase_3_COMMIT()
16. Commit Handler → User: Feature complete ✓

ANNOTATIONS:
- Time markers on right: 0.8s, 1.5s, 3.2s, 18m, 21m, 22m
- Database query boxes for Tier 2/Tier 3 interactions
- Activation boxes showing processing time
- Return messages with data payloads

STYLE: Standard UML sequence diagram, professional software engineering 
documentation style. Clear lifelines, proper message arrows (solid for calls, 
dashed for returns), activation boxes, time progression.
```

---

### Diagram 5: Plugin System Architecture
```
Create a component diagram showing plugin architecture and extensibility.

DIAGRAM TYPE: Component diagram with hub-and-spoke layout

CENTER COMPONENT:
- Box labeled "CORTEX Core"
- Annotation: "Minimal core, <500 lines per file"
- Color: Light gray (#F5F5F5)
- Border: Solid line

HUB: Plugin Registry (surrounding core)
- Octagonal shape around core
- 8 hook points labeled:
  * ON_STARTUP
  * ON_DOC_REFRESH
  * ON_SELF_REVIEW
  * ON_DB_MAINTENANCE
  * ON_COMMIT
  * ON_ERROR
  * ON_BRAIN_UPDATE
  * ON_SHUTDOWN
- Color: Medium gray
- Connection points glowing when active

PLUGINS (Spokes connecting to hub):
1. Cleanup Plugin
   - Icon: Broom
   - Connected to: ON_DB_MAINTENANCE
   - Status: Active (green indicator)
   
2. Documentation Plugin
   - Icon: Book
   - Connected to: ON_DOC_REFRESH
   - Status: Active (green indicator)
   
3. Self-Review Plugin
   - Icon: Magnifying glass
   - Connected to: ON_SELF_REVIEW
   - Status: Active (green indicator)
   
4. Maintenance Plugin
   - Icon: Wrench
   - Connected to: ON_STARTUP
   - Status: Active (green indicator)
   
5. Custom Plugin (placeholder)
   - Icon: Puzzle piece
   - Connected to: Multiple hooks
   - Status: Disabled (gray indicator)

PLUGIN LIFECYCLE (bottom panel):
- State diagram showing: Loaded → Initialized → Executing → Cleanup
- Arrows between states
- Error state (red) branching from any state

CODE SNIPPET (side panel):
```python
class BasePlugin:
    def initialize() → bool
    def execute(context) → Result
    def cleanup() → bool
```

BENEFITS CALLOUTS:
- "✓ Core stays minimal"
- "✓ Easy extension"
- "✓ Enable/disable features"
- "✓ No core modifications"

STYLE: Professional component diagram, modular design, clear plugin boundaries,
hub-and-spoke layout. Similar to microservices architecture diagrams.
```

---

### Diagram 6: Workflow Pipeline DAG
```
Create a directed acyclic graph (DAG) showing workflow pipeline execution.

DIAGRAM TYPE: DAG flowchart

NODES (hexagonal shapes):
1. "Clarify DoD/DoR" (yellow, #FFD600)
2. "Threat Model" (orange, #FF6B35)
3. "Create Plan" (blue, #0066CC)
4. "TDD Cycle" (green, #00C853)
5. "Run Tests" (purple, #7B1FA2)
6. "Cleanup" (cyan, #00BCD4) - parallel with 7
7. "Document" (cyan, #00BCD4) - parallel with 6
8. "Commit" (gray, #546E7A)

EDGES (directed arrows):
- 1 → 2 (Clarify must complete before threat model)
- 2 → 3 (Threat model must complete before planning)
- 3 → 4 (Plan must complete before TDD)
- 4 → 5 (TDD must complete before tests)
- 5 → 6 (Tests must pass before cleanup)
- 5 → 7 (Tests must pass before documentation)
- 6 → 8 (Cleanup must complete before commit)
- 7 → 8 (Documentation must complete before commit)
- Dashed arrows for optional dependencies

NODE ANNOTATIONS:
- Agent icon showing which agent handles each stage
- Clock icon showing timeout (e.g., "30m")
- Status indicator: ⏳ Pending, ▶️ Running, ✅ Complete, ❌ Failed

CHECKPOINT MARKERS:
- Diamond shapes at critical stages (after Plan, after TDD, after Tests)
- "Resume point" labels

PARALLEL EXECUTION INDICATOR:
- Dashed box around nodes 6 and 7 labeled "Parallel execution (max 2)"

BOTTOM LEGEND:
- Color coding: Validation (yellow), Security (orange), Planning (blue), 
  Execution (green), Testing (purple), Finalization (cyan), Control (gray)

YAML CONFIG SNIPPET (side):
```yaml
workflow:
  stages:
    - id: plan
      agent: work_planner
      depends_on: [clarify, threat_model]
      timeout: 30m
    - id: tdd_cycle
      agent: code_executor
      depends_on: [plan]
      checkpoint: true
```

STYLE: Professional DAG flowchart, similar to GitHub Actions or Azure DevOps 
pipelines. Clean lines, clear dependencies, color-coded stages, technical 
documentation quality.
```

---

### Diagram 7: State Machine - Conversation Lifecycle
```
Create a state machine diagram for conversation management:

STATES (circular nodes):
1. "New Request" (gray circle)
2. "Planning" (yellow circle)
3. "Executing" (green circle, pulsing)
4. "Paused" (orange circle with pause icon)
5. "Checkpoint" (blue circle with save icon)
6. "Completed" (green circle with checkmark)
7. "Failed" (red circle with X)

TRANSITIONS (arrows between states):
- "Start" → Planning
- Planning → Executing (after plan approved)
- Executing → Paused (interruption detected)
- Executing → Checkpoint (phase complete)
- Checkpoint → Executing (continue)
- Paused → Executing (resume command)
- Executing → Completed (all phases done)
- Executing → Failed (error, no recovery)
- Failed → Checkpoint (rollback)

DATABASE TABLES (side panel):
- `conversations`: conversation_id, status, current_phase, resume_prompt
- `tasks`: task_id, phase, status, files_modified
- `checkpoints`: checkpoint_id, state_snapshot, can_rollback

EXAMPLE FLOW (bottom timeline):
```
User: "Add invoice export"
→ Planning (5 min)
→ Executing: Phase 1 (RED) ✓
→ Checkpoint saved
→ Executing: Phase 2 (GREEN)
[Battery dies - PAUSED]
User: "Continue"
→ Resume from Checkpoint
→ Executing: Phase 2 (GREEN) ✓
→ Executing: Phase 3 (REFACTOR) ✓
→ Completed
```

Style: State machine diagram with clean, rounded shapes. Use traffic light 
colors (red/yellow/green) for status. Show time progression. Add database 
schema visualization on side. Professional software engineering diagram style.
```

---

## 📊 Performance & Metrics Visualizations

### 11. Performance Optimization Results
```
Create a before/after comparison dashboard:

LEFT SIDE - CORTEX 1.0 Performance:
- Tier 1 Query: 50ms (gauge meter, yellow zone)
- Tier 2 Search: 180ms (gauge meter, red zone - exceeds target)
- Tier 3 Metrics: 250ms (gauge meter, red zone)
- Context Injection: 200ms (gauge meter, orange zone)
- Overall: "Needs Optimization ⚠️"

RIGHT SIDE - CORTEX 2.0 Performance:
- Tier 1 Query: 25ms (gauge meter, deep green zone - 2x faster!)
- Tier 2 Search: 95ms (gauge meter, green zone - within target)
- Tier 3 Metrics: 120ms (gauge meter, green zone)
- Context Injection: 80ms (gauge meter, green zone - parallel loading)
- Overall: "Optimized ✓"

TARGET LINES (on gauges):
- Tier 1: 50ms target line
- Tier 2: 150ms target line
- Tier 3: 200ms target line
- Context: 120ms target line

OPTIMIZATION TECHNIQUES (annotations):
- FTS5 optimization
- Query caching (cache hit rate: 72%)
- Parallel loading (3 tiers simultaneously)
- Lazy loading (Tier 3 throttled updates)
- Connection pooling

PERFORMANCE TREND (bottom graph):
- X-axis: Months (Jan → Jun)
- Y-axis: Average query time (ms)
- Line graph showing decrease from 180ms to 95ms
- Markers for optimization milestones

Style: Dashboard/metrics style. Use speedometer gauges. Green = good, 
yellow = acceptable, red = needs work. Clean, modern, data visualization 
aesthetic like Grafana or Datadog dashboards.
```

### 12. File Size Reduction (Modular Architecture)
```
Create a before/after file structure comparison:

LEFT SIDE - CORTEX 1.0 (Monolithic):
```
src/
├── knowledge_graph.py        1144 lines 🔴 TOO LARGE
├── working_memory.py          813 lines 🔴 TOO LARGE
├── context_intelligence.py    776 lines 🔴 TOO LARGE
└── error_corrector.py         692 lines 🔴 TOO LARGE
Total: 3,425 lines in 4 files
```

Visual: Large, bloated file icons in red

RIGHT SIDE - CORTEX 2.0 (Modular):
```
src/
├── knowledge_graph/
│   ├── knowledge_graph.py       150 lines ✅
│   ├── patterns/
│   │   ├── pattern_store.py     200 lines ✅
│   │   ├── pattern_search.py    250 lines ✅
│   │   └── pattern_decay.py     120 lines ✅
│   ├── relationships/
│   │   └── relationship_manager.py 180 lines ✅
│   └── tags/
│       └── tag_manager.py       120 lines ✅
├── working_memory/
│   └── [5 focused modules]
├── context_intelligence/
│   └── [6 focused modules]
└── error_corrector/
    └── [5 strategy modules]
Total: 3,425 lines in 27 files
```

Visual: Organized folder tree with small, green file icons

METRICS (center):
- Files <500 lines: 0% → 100%
- Average file size: 856 lines → 127 lines
- Maintainability score: 42% → 91%
- Test isolation: Poor → Excellent
- Merge conflicts: Frequent → Rare

BENEFITS CALLOUTS:
- "✓ Single Responsibility"
- "✓ Easy to Navigate"
- "✓ Testable Modules"
- "✓ Reduced Conflicts"

Style: Code editor/file explorer aesthetic. Use folder/file tree visualization. 
Color coding (red = problem, green = good). Show transformation with large arrow 
pointing from left to right.
```

---

## 🎓 Educational Flow Diagrams

### 13. "Make It Purple" - Context Resolution Journey
```
Create an educational flow diagram showing how CORTEX resolves "Make it purple":

SCENARIO: User says "Make it purple" 3 hours after morning conversation

STEP 1 - Entry Point:
- User input bubble: "Make it purple"
- CORTEX receives ambiguous command

STEP 2 - Tier 1 Query (Working Memory):
- CORTEX queries last 20 conversations
- Searches for recent context containing "button", "FAB", "animation"
- FINDS: Conversation #8 (3 hours ago) - "Add pulse animation to FAB button"

STEP 3 - Context Resolution:
- "it" = FAB button
- "purple" = color modification
- Intent = EXECUTE (modify existing feature)

STEP 4 - Tier 2 Query (Knowledge Graph):
- Searches for: "button color change" pattern
- FINDS: 12 similar modifications
- Pattern: "Update CSS color variable"

STEP 5 - Execution:
- LEFT BRAIN (Builder) modifies: `noor-canvas.css`
- Changes: `--fab-color: #4285F4` → `--fab-color: #9333EA`
- Tests updated to expect purple (Tester)
- Validation passes (Inspector)

STEP 6 - Result:
- ✅ FAB button now purple
- Time: 18 seconds
- User happy, no confusion

WITHOUT CORTEX (comparison bubble):
- ❌ "Make what purple? Which button? Where?"
- ⏱️ 5 minutes explaining context
- 😤 User frustration

Style: Comic strip / storyboard style. Show each step in a panel with 
illustrations. Use speech bubbles. Contrast WITH vs WITHOUT CORTEX scenarios. 
Educational, friendly, easy to understand for non-technical readers.
```

### 14. Brain Protector Challenge Flow (Rule #22)
```
Create a dramatic, educational diagram showing Brain Protector in action:

SCENARIO: Developer tries to skip TDD at 2am

PANEL 1 - The Risky Request:
- Developer (tired, frustrated): "Skip tests, just push to production!"
- Clock showing 2:17 AM
- Coffee mug (empty)

PANEL 2 - CORTEX Detection:
- Brain Protector (RIGHT BRAIN) activates
- Alert: "🚨 Rule #22 Violation Detected"
- Analyzing threat...

PANEL 3 - Data Analysis:
- Historical data visualization:
  - Test-first success: 94%
  - Test-skip success: 67%
  - Last outage: Caused by test-skip deploy
- Risk level: HIGH

PANEL 4 - The Challenge:
```
═══════════════════════════════════
🧠 BRAIN PROTECTION CHALLENGE

Request: Skip TDD, deploy without tests
Threat: Production outage risk (+180%)
Historical: Last skip caused 4hr outage

SAFE ALTERNATIVES:
1. Minimal test (10 min) → 94% success ✅
2. Spike branch → Delete after learning
3. Sleep now → Resume tomorrow fresh

RECOMMENDATION: Alternative 1
═══════════════════════════════════
```

PANEL 5 - Developer Response:
- Developer (sighs): "You're right. I'll write the test."
- Coffee mug: Refilled

PANEL 6 - Outcome:
- Feature deployed: ✅ Success
- Tests: ✅ All passing
- Production: ✅ Stable
- Developer: 😌 Confident
- Brain Protector: 😎 "Told you so"

WITHOUT RULE #22 (alternate ending):
- Feature deployed: ❌ Production broken
- Tests: ❌ None written
- 3am: 🔥 Pager going off
- Developer: 😱 Panicking
- 4am: Still fixing...

Style: Comic book style with panels. Dramatic, engaging, slightly humorous. 
Show facial expressions. Use contrasting colors for WITH vs WITHOUT scenarios. 
Educational but entertaining.
```

---

## 🚀 Success Metrics & Growth

### 15. CORTEX Evolution Timeline
```
Create an evolutionary timeline showing CORTEX growth from KDS to 2.0:

TIMELINE (horizontal):

2024 Q4 - KDS v1-v7 (Basic Event Stream):
- Icon: Simple notebook
- Features: JSONL events, basic tracking
- Status: ❌ No intelligence
- Metric: 0 patterns learned

2025 Q1 - KDS v8 (Multi-tier Brain):
- Icon: Brain outline
- Features: Tier 1-3 memory, pattern learning
- Status: 🟡 Learning begins
- Metric: 247 patterns learned

2025 Q2 - CORTEX 1.0 (Dual Hemisphere):
- Icon: Brain with two colors
- Features: Strategic + Tactical agents, Rule #22
- Status: ✅ Intelligence achieved
- Metric: 1,523 patterns, 85% test coverage

2025 Q3 - CORTEX 1.0 Refinements:
- Icon: Brain with shield
- Features: Brain Protector, enhanced protection
- Status: ✅ Self-protecting
- Metric: 2,891 patterns, 94% success rate

2025 Q4 - CORTEX 2.0 Design:
- Icon: Modular brain with plugins
- Features: 27 design documents completed
- Status: 📋 Design complete
- Metric: Full roadmap, implementation ready

2026 Q1 - CORTEX 2.0 Release (Projected):
- Icon: Evolved brain with ecosystem
- Features: Plugins, workflows, self-review, resume
- Status: 🚀 Evolution complete
- Metric: 3,247+ patterns, +20% performance

KEY METRICS GRAPH (bottom):
- Lines showing growth:
  - Pattern count: 0 → 3,247
  - Test coverage: 45% → 85%
  - Success rate: 67% → 94%
  - Average completion time: 35min → 18min

Style: Timeline infographic. Use milestone markers. Show evolutionary progress 
with icons getting more sophisticated. Include metrics graphs. Professional but 
engaging. Tech company roadmap aesthetic.
```

---

## 🔄 Data Flow & Integration Diagrams

### Diagram 10: TDD Workflow Flow
```
Create a flowchart showing Test-Driven Development workflow in CORTEX.

DIAGRAM TYPE: Flowchart with decision points

START: User request enters system

PHASE 1 - RED (Create Failing Test):
- Rectangle: "Test Generator analyzes requirement"
- Rectangle: "Create test with expected behavior"
- Rectangle: "Run test suite"
- Diamond: "Test fails as expected?"
  - NO → Rectangle: "Fix test specification" → Loop back
  - YES → Continue to Phase 2
- Color: Red (#D32F2F)

PHASE 2 - GREEN (Make Test Pass):
- Rectangle: "Code Executor implements minimum code"
- Rectangle: "Run test suite"
- Diamond: "All tests pass?"
  - NO → Rectangle: "Fix implementation" → Loop back
  - YES → Continue to Phase 3
- Color: Green (#00C853)

PHASE 3 - REFACTOR (Clean Up):
- Rectangle: "Health Validator checks code quality"
- Diamond: "Zero errors/warnings?"
  - NO → Rectangle: "Apply cleanup fixes" → Loop back
  - YES → Continue to Commit
- Rectangle: "Commit Handler creates semantic commit"
- Color: Blue (#0066CC)

END: Feature complete, all tests green

ANNOTATIONS:
- Time indicators at each phase
- Success rate: 94% with TDD vs 67% without
- Database interactions shown at each phase (Tier 4 event logging)

STYLE: Professional flowchart, standard shapes (rectangle for process, diamond 
for decision), clear flow arrows, color-coded phases, technical documentation quality.
```

---

### Diagram 11: Context Resolution Flowchart
```
Create a flowchart showing how CORTEX resolves ambiguous references.

DIAGRAM TYPE: Decision tree flowchart

SCENARIO: User types "Make it purple" (ambiguous reference)

START: Input received "Make it purple"

STEP 1 - Parse Input:
- Rectangle: "Intent Router parses command"
- Extract: subject="it" (ambiguous), action="make", attribute="purple"

STEP 2 - Query Tier 1:
- Rectangle: "Search last 20 conversations for context"
- Diamond: "Found recent mention?"
  - YES → Rectangle: "Resolve 'it' = FAB button" → STEP 4
  - NO → Continue to STEP 3

STEP 3 - Query Tier 2:
- Rectangle: "Search knowledge graph for patterns"
- Diamond: "Found similar pattern?"
  - YES → Rectangle: "Suggest likely targets" → STEP 4
  - NO → Rectangle: "Ask user for clarification" → END (wait for user)

STEP 4 - Resolve Context:
- Rectangle: "Context resolved: FAB button color change"
- Rectangle: "Route to Code Executor (LEFT BRAIN)"

STEP 5 - Execute:
- Rectangle: "Modify CSS: --fab-color: #9333EA"
- Rectangle: "Update tests to expect purple"
- Rectangle: "Validate change"

END: Success - "FAB button is now purple"

TIMING ANNOTATIONS:
- Tier 1 query: <50ms
- Tier 2 query: <150ms (if needed)
- Execution: 18 seconds

WITH/WITHOUT COMPARISON (side panel):
- WITH CORTEX: 18 seconds, zero clarification needed
- WITHOUT CORTEX: 5 minutes explaining context, user frustration

STYLE: Clear flowchart with decision diamonds, color-coded sections (query=blue, 
execute=green, error=red), timing annotations, professional documentation style.
```

---

## 📝 Best Practices for Technical Diagrams

**When creating system diagrams:**

1. **Specify Diagram Type Explicitly**
   - "Create a UML sequence diagram..."
   - "Create a component architecture diagram..."
   - "Create a data flow diagram..."
   - "Create a state machine diagram..."

2. **Use Technical Terminology**
   - Components, modules, interfaces, APIs
   - Data flow, control flow, message passing
   - States, transitions, events
   - Layers, tiers, boundaries

3. **Color Coding System**
   - Blue (#0066CC): Tactical execution, data processing
   - Orange (#FF6B35): Strategic planning, analysis
   - Purple (#7B1FA2): Communication, bridges, APIs
   - Green (#00C853): Success states, passing tests
   - Red (#D32F2F): Error states, failures
   - Yellow (#FFD600): Warnings, validation stages
   - Gray (#546E7A): Infrastructure, foundation

4. **Label Everything**
   - Component names
   - Data types
   - Flow directions
   - Timing/performance metrics
   - Status indicators

5. **Reference Professional Styles**
   - "AWS architecture diagram style"
   - "UML standard notation"
   - "C4 model diagram"
   - "Grafana dashboard aesthetic"
   - "GitHub Actions pipeline visualization"

6. **Avoid Narrative Elements**
   - ❌ Don't: "cute robot", "warm lighting", "emotional expression"
   - ✅ Do: "rectangular component", "data flow arrow", "state indicator"

6. **Avoid Narrative Elements**
   - ❌ Don't: "cute robot", "warm lighting", "emotional expression"
   - ✅ Do: "rectangular component", "data flow arrow", "state indicator"

7. **Request Professional Output**
   - "Professional software architecture diagram"
   - "Technical documentation quality"
   - "Engineering blueprint style"
   - "Suitable for system design review"

---

## 🔗 Related Documentation

**For narrative story content** (characters, illustrations, story-telling):
- See: `prompts/user/cortex-gemini-image-prompts.md` (contains story illustrations)
- Story documents: `docs/story/CORTEX-STORY/Awakening Of CORTEX.md`

**For complete CORTEX documentation:**
- [Technical Deep-Dive](Technical-CORTEX.md) - Complete technical specifications
- [Evolution History](History.md) - Development timeline
- [CORTEX 2.0 Design Index](../../../cortex-brain/cortex-2.0-design/00-INDEX.md) - Design documents

**For implementation guidance:**
- [Core Entry Point](../../../prompts/user/cortex.md) - Universal CORTEX interface
- [Plugin System Docs](../../../cortex-brain/cortex-2.0-design/02-plugin-system.md)
- [Workflow Pipeline Docs](../../../cortex-brain/cortex-2.0-design/21-workflow-pipeline-system.md)

---

## 📊 Example Diagram Outputs

**Good Technical Diagram:**
```
┌─────────────────────────────────────────┐
│     Universal Entry Point (cortex.md)  │
└─────────────┬───────────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   Intent Router     │
    │   (RIGHT BRAIN)     │
    └─────────┬───────────┘
              │
         ┌────┴────┐
         ▼         ▼
   ┌─────────┐ ┌──────────┐
   │ Tier 2  │ │  Tier 3  │
   │ Query   │ │  Query   │
   └────┬────┘ └────┬─────┘
        └──────┬────┘
               ▼
        ┌──────────────┐
        │ Work Planner │
        └──────┬───────┘
               │
        [Corpus Callosum]
               │
               ▼
        ┌──────────────┐
        │ Code Executor│
        │ (LEFT BRAIN) │
        └──────────────┘
```

**Key Characteristics:**
- Clean ASCII/box diagram structure
- Clear component boundaries
- Labeled data flow
- Professional hierarchy
- No decorative elements

---

**Last Updated:** November 7, 2025  
**Version:** 2.0 (Technical Diagrams Only)  
**Purpose:** System architecture visualization for CORTEX design documentation
