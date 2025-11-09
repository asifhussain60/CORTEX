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

## 📐 CORTEX 2.0 New Feature Diagrams (November 2025)

### Diagram 23: Token Optimization System (Napkin.ai Format)

```napkin
# Token Optimization System Architecture

## Central Node
token_optimizer [Token Optimization Engine]

## Analysis Layer
token_optimizer -> ml_analyzer [ML Pattern Analyzer]
token_optimizer -> cache_manager [Cache Explosion Prevention]
token_optimizer -> context_reducer [Context Reduction Engine]

## Data Sources
ml_analyzer -> conversation_history [Conversation Patterns]
ml_analyzer -> usage_metrics [Token Usage Metrics]
cache_manager -> cache_monitor [Cache Size Monitor]
context_reducer -> relevance_scorer [Relevance Scoring]

## Optimization Strategies
ml_analyzer -> strategy_1 [Smart Summarization (50-70% reduction)]
cache_manager -> strategy_2 [Incremental Caching]
context_reducer -> strategy_3 [Contextual Pruning]

## Output
strategy_1 -> optimized_context [Optimized Context]
strategy_2 -> optimized_context
strategy_3 -> optimized_context
optimized_context -> copilot [GitHub Copilot]

## Metrics
optimized_context -> metrics [Real-time Metrics Dashboard]
metrics -> token_saved [Tokens Saved]
metrics -> cost_reduction [Cost Reduction %]
metrics -> performance_impact [Performance Impact]

# Style
theme: professional
layout: hierarchical
colors: 
  - token_optimizer: #FF6B35
  - ml_analyzer: #4A90E2
  - cache_manager: #7B1FA2
  - context_reducer: #00C853
  - optimized_context: #FFD600
```

**Alternative text prompt:**
"Create a technical system architecture diagram showing CORTEX Token Optimization System. Use hierarchical layout with central 'Token Optimization Engine' node connected to three analysis layers: ML Pattern Analyzer, Cache Explosion Prevention, Context Reduction Engine. Show data flows from conversation patterns and usage metrics feeding into optimization strategies (Smart Summarization 50-70% reduction, Incremental Caching, Contextual Pruning). All strategies output to optimized context feeding GitHub Copilot. Include metrics dashboard showing tokens saved, cost reduction %, and performance impact. Style: Software architecture diagram, clean boxes and arrows, professional color coding (orange for engine, blue for analysis, purple for cache, green for reduction, yellow for output). Tool: Napkin.ai"

---

### Diagram 24: Modular Entry Point Architecture (Napkin.ai Format)

```napkin
# Modular Entry Point vs Monolithic Comparison

## OLD Architecture (Left Side)
monolithic [Monolithic Entry Point\n74,047 tokens\n8,701 lines\n$2.22 per request]

monolithic -> load_all [Loads Everything\nEvery Time]
load_all -> story [Story (3,000 tokens)]
load_all -> technical [Technical (4,500 tokens)]
load_all -> agents [Agents (6,000 tokens)]
load_all -> design [Design Docs (45,000 tokens)]
load_all -> examples [Examples (15,000 tokens)]

load_all -> slow [2-3 seconds parse time]
load_all -> expensive [$25,920/year cost]

## NEW Architecture (Right Side)
modular [Modular Entry Point\n450 tokens\n300 lines\n$0.06 per request]

modular -> slim_entry [Slim Entry\nLoad on Demand]
slim_entry -> story_module [story.md\n800-1,000 tokens\nWhen needed]
slim_entry -> tech_module [technical-reference.md\n1,200-1,500 tokens\nWhen needed]
slim_entry -> agent_module [agents-guide.md\n900-1,100 tokens\nWhen needed]
slim_entry -> setup_module [setup-guide.md\n600-800 tokens\nWhen needed]

slim_entry -> fast [80ms parse time\n97% faster]
slim_entry -> cheap [$2,592/year cost\n$23,328 saved]

## Comparison Metric
monolithic -> comparison [vs]
modular -> comparison
comparison -> result [97.2% Token Reduction\n97% Cost Savings\n97% Speed Improvement]

# Style
theme: comparison
layout: side-by-side
colors:
  - monolithic: #D32F2F
  - modular: #00C853
  - comparison: #FFD600
  - result: #4A90E2
```

**Alternative text prompt:**
"Create a comparison diagram showing OLD vs NEW CORTEX entry point architecture. LEFT SIDE: Monolithic Entry Point (red box, 74,047 tokens, 8,701 lines, $2.22 per request) loading everything every time - Story (3,000 tokens), Technical (4,500), Agents (6,000), Design Docs (45,000), Examples (15,000). Shows slow (2-3 sec) and expensive ($25,920/year). RIGHT SIDE: Modular Entry Point (green box, 450 tokens, 300 lines, $0.06 per request) with slim entry loading on demand - story.md (800-1,000 tokens), technical-reference.md (1,200-1,500), agents-guide.md (900-1,100), setup-guide.md (600-800). Shows fast (80ms, 97% faster) and cheap ($2,592/year, $23,328 saved). CENTER: Comparison arrow showing 97.2% token reduction, 97% cost savings, 97% speed improvement. Style: Professional comparison diagram, AWS architecture aesthetic. Tool: Napkin.ai"

---

### Diagram 25: Ambient Capture Daemon Flow (Napkin.ai Format)

```napkin
# Ambient Capture Daemon Architecture

## Trigger Detection
vscode_window [VS Code Window Focus]
conversation_length [Conversation > 5 Messages]
keywords [Keywords Detected\nimpl ement, test, fix, review]
git_ops [Git Operations\ncommit, branch, PR]

## Central Daemon
vscode_window -> daemon [Ambient Capture Daemon]
conversation_length -> daemon
keywords -> daemon
git_ops -> daemon

## Filtering Layer
daemon -> filter [Smart Filter Engine]
filter -> noise_filter [Ignore Noise\nsyntax errors, auto-saves, typos]
filter -> value_filter [Capture Value\narchitecture, debugging, features]

## Intelligence Layer
value_filter -> pattern_detector [Pattern Detection\n15-20 patterns]
value_filter -> deduplicator [Smart Deduplication]
value_filter -> enricher [Context Enrichment\ngit status, files changed]
value_filter -> tagger [Auto-Tagging\nfeature, bug, review, refactor]

## Storage
pattern_detector -> tier1 [Tier 1: Working Memory]
deduplicator -> tier1
enricher -> tier1
tagger -> tier1

tier1 -> resume [Resume Capability]

## Metrics
daemon -> metrics_dash [Metrics Dashboard]
metrics_dash -> capture_rate [94% Capture Accuracy]
metrics_dash -> false_positive [3% False Positive Rate]
metrics_dash -> loss_rate [2% Loss Rate\ndown from 40%]

# Style
theme: flowchart
layout: top-down
colors:
  - daemon: #FF6B35
  - filter: #7B1FA2
  - pattern_detector: #4A90E2
  - tier1: #00C853
  - metrics_dash: #FFD600
```

**Alternative text prompt:**
"Create a technical flowchart showing Ambient Capture Daemon architecture. TOP: Four trigger boxes (VS Code window focus, Conversation >5 messages, Keywords detected, Git operations) feeding into central Ambient Capture Daemon (orange). MIDDLE: Daemon connects to Smart Filter Engine (purple) which splits into noise filter (ignore: syntax errors, auto-saves, typos) and value filter (capture: architecture, debugging, features). LOWER-MIDDLE: Value filter feeds Intelligence Layer with four components: Pattern Detection (15-20 patterns), Smart Deduplication, Context Enrichment (git status, files changed), Auto-Tagging (feature, bug, review, refactor) - all in blue. BOTTOM: Intelligence components feed Tier 1 Working Memory (green) enabling Resume Capability. RIGHT: Metrics Dashboard (yellow) showing 94% capture accuracy, 3% false positive rate, 2% loss rate (down from 40%). Style: Technical flowchart, professional data flow diagram. Tool: Napkin.ai"

---

### Diagram 26: Crawler Orchestration System (Napkin.ai Format)

```napkin
# Unified Workspace Discovery Architecture

## Discovery Request
user_request [Workspace Discovery Request]

## Orchestrator
user_request -> orchestrator [Crawler Orchestration Engine]

## Crawler Types
orchestrator -> db_crawler [Database Crawler]
orchestrator -> api_crawler [API Crawler]
orchestrator -> ui_crawler [UI Framework Crawler]
orchestrator -> code_crawler [Code Structure Crawler]
orchestrator -> config_crawler [Configuration Crawler]

## Database Discovery
db_crawler -> sql_detect [SQL Databases\nPostgreSQL, MySQL, SQL Server]
db_crawler -> nosql_detect [NoSQL Databases\nMongoDB, Redis, Elasticsearch]
db_crawler -> orm_detect [ORM Detection\nEntity Framework, SQLAlchemy]

## API Discovery
api_crawler -> rest_detect [REST APIs\nSwagger/OpenAPI]
api_crawler -> graphql_detect [GraphQL\nSchema detection]
api_crawler -> grpc_detect [gRPC\nProto file analysis]

## UI Discovery
ui_crawler -> react_detect [React Components\nJSX/TSX analysis]
ui_crawler -> angular_detect [Angular Modules\nTypeScript analysis]
ui_crawler -> vue_detect [Vue Components\nSFC analysis]

## Unified Schema
sql_detect -> unified_schema [Unified Workspace Schema]
rest_detect -> unified_schema
react_detect -> unified_schema
orm_detect -> unified_schema
nosql_detect -> unified_schema
graphql_detect -> unified_schema
angular_detect -> unified_schema
grpc_detect -> unified_schema
vue_detect -> unified_schema

## Output
unified_schema -> knowledge_graph [Tier 2: Knowledge Graph]
unified_schema -> context_layer [Tier 3: Development Context]

# Style
theme: hierarchical
layout: tree
colors:
  - orchestrator: #FF6B35
  - db_crawler: #4A90E2
  - api_crawler: #7B1FA2
  - ui_crawler: #00C853
  - unified_schema: #FFD600
  - knowledge_graph: #00BCD4
```

**Alternative text prompt:**
"Create a hierarchical tree diagram showing Crawler Orchestration System. TOP: Workspace Discovery Request feeds Crawler Orchestration Engine (orange box). SECOND LEVEL: Five crawler types branch out: Database Crawler (blue), API Crawler (purple), UI Framework Crawler (green), Code Structure Crawler, Configuration Crawler. THIRD LEVEL: Each crawler branches to specific technologies - Database: SQL (PostgreSQL, MySQL), NoSQL (MongoDB, Redis), ORM (Entity Framework). API: REST (Swagger), GraphQL, gRPC. UI: React (JSX/TSX), Angular (TypeScript), Vue (SFC). CONVERGENCE: All discoveries converge to Unified Workspace Schema (yellow central node). BOTTOM: Schema feeds two destinations: Tier 2 Knowledge Graph and Tier 3 Development Context (cyan boxes). Style: Technical tree diagram, AWS architecture style, professional hierarchy. Tool: Napkin.ai"

---

### Diagram 27: Human-Readable Documentation System (Napkin.ai Format)

```napkin
# Human-Readable Documentation Architecture

## Source Documents
tech_source [Technical-CORTEX.md\nTechnical Deep-Dive]
story_source [Awakening Of CORTEX.md\nNarrative Story]
history_source [History.md\nEvolution Timeline]
image_source [Image-Prompts.md\nDiagram Prompts]

## Doc Refresh Plugin
tech_source -> doc_plugin [Doc Refresh Plugin]
story_source -> doc_plugin
history_source -> doc_plugin
image_source -> doc_plugin

## Design Context
design_docs [CORTEX 2.0 Design\n37 documents] -> doc_plugin

## Generation Process
doc_plugin -> consolidator [Content Consolidator\n95% story / 5% technical]
consolidator -> image_integrator [Image Integration\nContextual placement]
image_integrator -> flow_optimizer [Cohesive Flow\nProgressive disclosure]

## Output Documents
flow_optimizer -> awakening_doc [THE-AWAKENING-OF-CORTEX.md\nConsolidated Story + Tech + Images]
flow_optimizer -> rulebook_doc [CORTEX-RULEBOOK.md\n33 Rules in Plain English]
flow_optimizer -> features_doc [CORTEX-FEATURES.md\nGranular Feature List]

## Image Generation
image_source -> napkin [Napkin.ai]
napkin -> diagrams [Generated Diagrams\nSystem architecture, flows, comparisons]
diagrams -> image_integrator

## Synchronization
design_docs -> sync_checker [Sync Validator]
awakening_doc -> sync_checker
rulebook_doc -> sync_checker
features_doc -> sync_checker
sync_checker -> auto_update [Auto-Update Trigger]
auto_update -> doc_plugin

# Style
theme: workflow
layout: flow
colors:
  - doc_plugin: #FF6B35
  - consolidator: #4A90E2
  - awakening_doc: #00C853
  - napkin: #7B1FA2
  - sync_checker: #FFD600
```

**Alternative text prompt:**
"Create a workflow diagram showing Human-Readable Documentation System. LEFT: Four source documents (Technical-CORTEX.md, Awakening Of CORTEX.md, History.md, Image-Prompts.md) plus CORTEX 2.0 Design (37 documents) all feeding into Doc Refresh Plugin (orange box). CENTER: Plugin flows through generation process: Content Consolidator (95% story/5% technical) → Image Integration (contextual placement) → Cohesive Flow (progressive disclosure). RIGHT: Three output documents: THE-AWAKENING-OF-CORTEX.md (consolidated story+tech+images), CORTEX-RULEBOOK.md (33 rules plain English), CORTEX-FEATURES.md (granular features) - all green boxes. PARALLEL FLOW: Image-Prompts.md feeds Napkin.ai (purple) generating diagrams feeding back to Image Integration. BOTTOM: Sync Validator (yellow) monitors design docs and output docs, triggering auto-update back to plugin when out of sync. Style: Professional workflow diagram, data pipeline visualization. Tool: Napkin.ai"

---

## 🛠️ Napkin.ai Usage Guidelines

**Format:** Node-based syntax optimized for Napkin.ai rendering

**Basic Syntax:**
```napkin
node_id [Node Label]
node1 -> node2 [Edge Label]

# Style
theme: professional|flowchart|comparison|workflow
layout: hierarchical|tree|side-by-side|flow|top-down
colors:
  - node_id: #HEX_COLOR
```

**Best Practices:**
1. Use descriptive node IDs (snake_case)
2. Keep labels concise (max 3-4 words)
3. Add technical details in labels (\n for multi-line)
4. Specify theme and layout for optimal rendering
5. Use consistent color coding across related diagrams

**Color Palette (CORTEX Standard):**
- Orange (#FF6B35): Core engines, orchestrators
- Blue (#4A90E2): Analysis, intelligence layers
- Purple (#7B1FA2): Communication, APIs, caching
- Green (#00C853): Success states, outputs
- Yellow (#FFD600): Metrics, monitoring
- Cyan (#00BCD4): Storage, persistence
- Red (#D32F2F): Error states, old/deprecated

**Tool:** Napkin.ai (https://napkin.ai)  
**Alternative:** Mermaid.js, Draw.io, Lucidchart

---

**Last Updated:** November 9, 2025 via Documentation Refresh Plugin  
**Version:** 2.1 (Technical Diagrams + Napkin.ai Format)  
**Purpose:** System architecture visualization for CORTEX design documentation
