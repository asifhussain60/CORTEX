# CORTEX System Diagrams - Technical Visualization Prompts
**Purpose:** Generate professional system diagrams that visually reveal CORTEX architecture and design

**Target:** Google Gemini Image Generation  
**Format:** Technical diagrams only - flowcharts, sequence diagrams, architecture diagrams, UML  
**Style:** Professional engineering documentation, not cartoons

**Last Updated:** 2025-11-10  
**Version:** 2.0 (Gemini-Compatible Single-Paragraph Prompts)

---

## 🎯 Prompt Design Guidelines

**For Technical Diagrams:**
- Each prompt is a complete, single paragraph
- Uses clear, professional language
- Specifies diagram type explicitly (flowchart, sequence diagram, architecture diagram, UML)
- Includes precise labels, annotations, and technical terminology
- Requests "technical diagram style" or "software architecture diagram"
- Avoids narrative/story elements

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

## 📐 System Architecture Diagrams

### Diagram 1: CORTEX Complete System Architecture

Create a technical system architecture diagram showing CORTEX 2.0 components and data flow as a layered architecture from top to bottom with five distinct layers: Layer 1 at the top is a gray box labeled "Universal Entry Point (cortex.md)" with a single door icon, Layer 2 contains a large orange container box labeled "RIGHT BRAIN - Strategic Planning" (#FF6B35) with five hexagonal interconnected child nodes for Intent Router, Work Planner, Brain Protector, Change Governor, and Screenshot Analyzer, Layer 3 is a horizontal purple bar (#7B1FA2) labeled "Corpus Callosum - Coordination Queue" with bidirectional arrows connecting Layers 2 and 4, Layer 4 contains a large blue container box labeled "LEFT BRAIN - Tactical Execution" (#0066CC) with five rectangular child nodes arranged in a grid for Code Executor, Test Generator, Error Corrector, Health Validator, and Commit Handler, and Layer 5 at the foundation has five horizontal bands stacked bottom-up showing Tier 0: Instinct (dark gray #546E7A with lock icon), Tier 1: Working Memory (light blue with SQLite icon), Tier 2: Knowledge Graph (purple with network icon), Tier 3: Dev Context (orange with chart icon), and Tier 4: Event Stream (green with log icon), with circular plugin nodes around the periphery (Cleanup, Documentation, Self-Review, Maintenance) connected via dashed lines, and arrows showing data flow from User → Entry → Right Brain → Corpus Callosum → Left Brain → Memory Tiers with feedback arrows from Memory Tiers back to Right Brain for the learning loop, using a modern AWS-style software architecture diagram with clean lines, professional color palette, clear labels, and isometric 3D perspective suitable for technical documentation.

---

### Diagram 2: Dual-Hemisphere Brain Architecture

Create a split-screen comparison diagram showing RIGHT BRAIN versus LEFT BRAIN architecture with three main sections: the left panel titled "RIGHT BRAIN - Strategic Planning" shows component boxes arranged organically with curved flowing lines connecting Intent Router (entry point), Work Planner (strategic planning), Brain Protector (rule enforcement), Change Governor (architecture guardian), and Screenshot Analyzer (visual analysis), all in an orange gradient (#FF6B35 to #FF8C42) with icons for lightbulb (ideas), chess piece (strategy), and shield (protection) and labels "Plans", "Analyzes", "Protects", "Routes", the center section shows a vertical purple gradient bridge (#7B1FA2) labeled "Corpus Callosum - Message Coordination" with bidirectional arrows showing "Strategic Plan", "Context", "Patterns" flowing right to left and "Execution Results", "Test Status", "Health Metrics" flowing left to right with a network/connection symbol, the right panel titled "LEFT BRAIN - Tactical Execution" shows component boxes arranged in a precise grid with straight lines connecting Test Generator (RED phase), Code Executor (GREEN phase), Error Corrector (error handling), Health Validator (REFACTOR phase), and Commit Handler (version control), all in a blue gradient (#0066CC to #4A90E2) with icons for gear (execution), checkmark (validation), and tools (building) and labels "Builds", "Tests", "Fixes", "Validates", and a bottom timeline showing the workflow collaboration: RIGHT BRAIN "Analyze & Plan" (3.2s) → CORPUS CALLOSUM "Transfer Plan" (0.1s) → LEFT BRAIN "Execute TDD" (3h 47m) → CORPUS CALLOSUM "Send Results" (0.1s) → RIGHT BRAIN "Update Knowledge" (2.5s), using a technical comparison diagram style with clean separation, professional engineering aesthetic, clear labels, and AWS architecture diagram color coding suitable for architecture documentation.

---

### Diagram 3: Five-Tier Memory System

Create a vertical layered architecture diagram showing CORTEX memory tiers as a stack with data flow, where Tier 0 at the bottom foundation is the widest dark gray rectangle (#546E7A) with a solid border, lock icon, and label "TIER 0: INSTINCT - Immutable Core Rules" containing "TDD, SOLID, DoR/DoD, Rule #22, Brain Protection", above it Tier 1 is a light blue rectangle (#4A90E2) labeled "TIER 1: WORKING MEMORY - Last 20 Conversations" with "conversation-history.jsonl, FIFO queue, <50ms queries", clock and database icons, and "8/20 capacity" indicator, above that Tier 2 is a purple rectangle (#7B1FA2) labeled "TIER 2: KNOWLEDGE GRAPH - Long-term Learning" with "knowledge-graph.yaml, 3,247 patterns, FTS5 search", neural network node icons, and "3,247 patterns learned" indicator, above that Tier 3 is an orange rectangle (#FF6B35) labeled "TIER 3: DEVELOPMENT CONTEXT - Project Intelligence" with "Git metrics, file hotspots, commit velocity, churn analysis", bar chart/dashboard icons, and "Last updated: 45 min ago" indicator, at the top Tier 4 is a green rectangle (#00C853) labeled "TIER 4: EVENT STREAM - Activity Log" with "events.jsonl, auto-learning triggers, 23 events pending", scroll/log file icons, and "23 events pending" indicator, with vertical arrows showing data flow from Events (Tier 4) to Patterns (Tier 2), Conversations (Tier 1) to Patterns (Tier 2), and all tiers querying Tier 0 with labels "Extract patterns", "Query rules", "Update graph", and side annotations showing query speed indicators (Tier 1: <50ms, Tier 2: <150ms, Tier 3: <200ms), capacity indicators for each tier, and update frequency (Tier 1: real-time, Tier 2: on threshold, Tier 3: hourly), using a layered architecture diagram style with clear separation between tiers, professional color coding, and technical documentation quality similar to OSI model or database architecture diagrams.

---

### Diagram 4: Request Flow Sequence Diagram

Create a UML sequence diagram showing complete request processing flow with time flowing top to bottom, displaying ten vertical lifelines for User, Entry Point (cortex.md), Intent Router (RIGHT BRAIN), Tier 2 (Knowledge Graph), Tier 3 (Dev Context), Work Planner (RIGHT BRAIN), Corpus Callosum, Code Executor (LEFT BRAIN), Test Generator (LEFT BRAIN), and Commit Handler (LEFT BRAIN), with the following sequence: User sends "Add purple button to HostControlPanel" to Entry Point, Entry Point calls route_request() on Intent Router, Intent Router calls query_patterns("button addition") on Tier 2, Tier 2 returns [12 similar patterns found] to Intent Router, Intent Router calls get_context("HostControlPanel.razor") on Tier 3, Tier 3 returns [file hotspot, 28% churn rate] to Intent Router, Intent Router calls create_plan() on Work Planner, Work Planner calls send_strategic_plan() on Corpus Callosum, Corpus Callosum calls execute_phase_1_RED() on Test Generator, Test Generator has a self-call to create_tests(), Test Generator returns tests_created(RED) to Corpus Callosum, Corpus Callosum calls execute_phase_2_GREEN() on Code Executor, Code Executor has a self-call to implement_feature(), Code Executor returns implementation_complete(GREEN) to Corpus Callosum, Corpus Callosum calls execute_phase_3_COMMIT() on Commit Handler, and Commit Handler returns "Feature complete ✓" to User, with time markers on the right showing 0.8s, 1.5s, 3.2s, 18m, 21m, 22m, database query boxes for Tier 2/Tier 3 interactions, activation boxes showing processing time, and return messages with data payloads, using standard UML sequence diagram notation with clear lifelines, proper message arrows (solid for calls, dashed for returns), activation boxes, and time progression in professional software engineering documentation style.

---

### Diagram 5: Plugin System Architecture

Create a component diagram showing plugin architecture and extensibility with a hub-and-spoke layout, where the center has a light gray box (#F5F5F5) with solid border labeled "CORTEX Core" annotated "Minimal core, <500 lines per file", surrounded by a medium gray octagonal Plugin Registry hub with eight labeled hook points (ON_STARTUP, ON_DOC_REFRESH, ON_SELF_REVIEW, ON_DB_MAINTENANCE, ON_COMMIT, ON_ERROR, ON_BRAIN_UPDATE, ON_SHUTDOWN) with glowing connection points when active, and five plugin spokes connecting to the hub: Cleanup Plugin with broom icon connected to ON_DB_MAINTENANCE showing green active status, Documentation Plugin with book icon connected to ON_DOC_REFRESH showing green active status, Self-Review Plugin with magnifying glass icon connected to ON_SELF_REVIEW showing green active status, Maintenance Plugin with wrench icon connected to ON_STARTUP showing green active status, and Custom Plugin placeholder with puzzle piece icon connected to multiple hooks showing gray disabled status, with a bottom panel showing plugin lifecycle state diagram (Loaded → Initialized → Executing → Cleanup) with arrows between states and a red error state branching from any state, a side code snippet panel showing "class BasePlugin: def initialize() → bool, def execute(context) → Result, def cleanup() → bool", and benefit callouts stating "✓ Core stays minimal", "✓ Easy extension", "✓ Enable/disable features", "✓ No core modifications", using professional component diagram style with modular design, clear plugin boundaries, and hub-and-spoke layout similar to microservices architecture diagrams.

---

### Diagram 6: Workflow Pipeline DAG

Create a directed acyclic graph (DAG) flowchart showing workflow pipeline execution with eight hexagonal nodes: "Clarify DoD/DoR" in yellow (#FFD600), "Threat Model" in orange (#FF6B35), "Create Plan" in blue (#0066CC), "TDD Cycle" in green (#00C853), "Run Tests" in purple (#7B1FA2), "Cleanup" in cyan (#00BCD4) parallel with "Document" also in cyan (#00BCD4), and "Commit" in gray (#546E7A), with directed arrows showing dependencies where node 1 → 2 (Clarify must complete before threat model), 2 → 3 (Threat model must complete before planning), 3 → 4 (Plan must complete before TDD), 4 → 5 (TDD must complete before tests), 5 → 6 and 5 → 7 (Tests must pass before both cleanup and documentation which run in parallel), and 6 → 8 and 7 → 8 (Both cleanup and documentation must complete before commit), with dashed arrows for optional dependencies, each node annotated with agent icons showing which agent handles each stage, clock icons showing timeouts (e.g., "30m"), and status indicators (⏳ Pending, ▶️ Running, ✅ Complete, ❌ Failed), diamond checkpoint markers at critical stages (after Plan, after TDD, after Tests) labeled "Resume point", a dashed box around nodes 6 and 7 labeled "Parallel execution (max 2)", a bottom legend showing color coding (Validation yellow, Security orange, Planning blue, Execution green, Testing purple, Finalization cyan, Control gray), and a side YAML config snippet showing "workflow: stages: - id: plan, agent: work_planner, depends_on: [clarify, threat_model], timeout: 30m - id: tdd_cycle, agent: code_executor, depends_on: [plan], checkpoint: true", using professional DAG flowchart style similar to GitHub Actions or Azure DevOps pipelines with clean lines, clear dependencies, color-coded stages, and technical documentation quality.

---

## 📊 Performance & Metrics Visualizations

### Diagram 7: Performance Optimization Dashboard

Create a before-and-after comparison dashboard showing CORTEX 1.0 Performance on the left side with four gauge meters in yellow/red zones: Tier 1 Query at 50ms (yellow zone), Tier 2 Search at 180ms (red zone exceeds target), Tier 3 Metrics at 250ms (red zone), Context Injection at 200ms (orange zone), labeled "Needs Optimization ⚠️", and CORTEX 2.0 Performance on the right side with four gauge meters in deep green zones: Tier 1 Query at 25ms (green zone, 2x faster!), Tier 2 Search at 95ms (green zone within target), Tier 3 Metrics at 120ms (green zone), Context Injection at 80ms (green zone with parallel loading annotation), labeled "Optimized ✓", with target lines on each gauge (Tier 1: 50ms, Tier 2: 150ms, Tier 3: 200ms, Context: 120ms), annotations for optimization techniques (FTS5 optimization, Query caching with 72% cache hit rate, Parallel loading for 3 tiers simultaneously, Lazy loading with Tier 3 throttled updates, Connection pooling), and a bottom performance trend line graph with X-axis showing months (Jan → Jun), Y-axis showing average query time (ms), a line decreasing from 180ms to 95ms, and markers for optimization milestones, using dashboard/metrics style with speedometer gauges, traffic light colors (green = good, yellow = acceptable, red = needs work), clean modern data visualization aesthetic similar to Grafana or Datadog dashboards.

---

### Diagram 8: Modular Architecture File Comparison

Create a before-and-after file structure comparison with the left side showing CORTEX 1.0 Monolithic architecture as a code tree "src/ ├── knowledge_graph.py 1144 lines 🔴 TOO LARGE ├── working_memory.py 813 lines 🔴 TOO LARGE ├── context_intelligence.py 776 lines 🔴 TOO LARGE └── error_corrector.py 692 lines 🔴 TOO LARGE Total: 3,425 lines in 4 files" with large bloated red file icons, the right side showing CORTEX 2.0 Modular architecture as an organized folder tree "src/ ├── knowledge_graph/ │ ├── knowledge_graph.py 150 lines ✅ │ ├── patterns/ │ │ ├── pattern_store.py 200 lines ✅ │ │ ├── pattern_search.py 250 lines ✅ │ │ └── pattern_decay.py 120 lines ✅ │ ├── relationships/ │ │ └── relationship_manager.py 180 lines ✅ │ └── tags/ │ └── tag_manager.py 120 lines ✅ ├── working_memory/ [5 focused modules] ├── context_intelligence/ [6 focused modules] └── error_corrector/ [5 strategy modules] Total: 3,425 lines in 27 files" with small organized green file icons, center metrics showing "Files <500 lines: 0% → 100%", "Average file size: 856 lines → 127 lines", "Maintainability score: 42% → 91%", "Test isolation: Poor → Excellent", "Merge conflicts: Frequent → Rare", benefit callouts stating "✓ Single Responsibility", "✓ Easy to Navigate", "✓ Testable Modules", "✓ Reduced Conflicts", and a large arrow pointing from left to right showing the transformation, using code editor/file explorer aesthetic with folder/file tree visualization, color coding (red = problem, green = good), and clear visual transformation.

---

## 🎓 Educational Flow Diagrams

### Diagram 9: Context Resolution Journey ("Make It Purple")

Create an educational flow diagram showing how CORTEX resolves "Make it purple" in six sequential steps with the scenario that the user says "Make it purple" 3 hours after a morning conversation: Step 1 shows a user input bubble "Make it purple" with CORTEX receiving the ambiguous command, Step 2 shows Tier 1 Query (Working Memory) where CORTEX queries the last 20 conversations searching for recent context containing "button", "FAB", "animation" and finds Conversation #8 (3 hours ago) about "Add pulse animation to FAB button", Step 3 shows Context Resolution determining "it" = FAB button, "purple" = color modification, Intent = EXECUTE (modify existing feature), Step 4 shows Tier 2 Query (Knowledge Graph) searching for "button color change" pattern and finding 12 similar modifications with the pattern "Update CSS color variable", Step 5 shows Execution where LEFT BRAIN (Builder) modifies noor-canvas.css changing "--fab-color: #4285F4 → --fab-color: #9333EA", tests are updated to expect purple by Tester, and validation passes by Inspector, Step 6 shows the result with checkmark "FAB button now purple", "Time: 18 seconds", "User happy, no confusion", and a comparison bubble showing WITHOUT CORTEX scenario with X mark "Make what purple? Which button? Where?", "5 minutes explaining context", angry face "User frustration", using comic strip/storyboard panel style with illustrations for each step, speech bubbles, contrasting WITH versus WITHOUT CORTEX scenarios in different colors, and an educational friendly tone that's easy to understand for non-technical readers.

---

### Diagram 10: Brain Protector Challenge Flow (Rule #22)

Create a dramatic educational diagram showing Brain Protector in action with six comic-style panels for the scenario where a developer tries to skip TDD at 2am: Panel 1 "The Risky Request" shows a tired frustrated developer saying "Skip tests, just push to production!" with a clock showing 2:17 AM and an empty coffee mug, Panel 2 "CORTEX Detection" shows Brain Protector (RIGHT BRAIN) activating with alert "🚨 Rule #22 Violation Detected" and "Analyzing threat...", Panel 3 "Data Analysis" shows historical data visualization with Test-first success: 94%, Test-skip success: 67%, Last outage: Caused by test-skip deploy, and Risk level: HIGH, Panel 4 "The Challenge" shows a bordered text box "🧠 BRAIN PROTECTION CHALLENGE - Request: Skip TDD, deploy without tests - Threat: Production outage risk (+180%) - Historical: Last skip caused 4hr outage - SAFE ALTERNATIVES: 1. Minimal test (10 min) → 94% success ✅ 2. Spike branch → Delete after learning 3. Sleep now → Resume tomorrow fresh - RECOMMENDATION: Alternative 1", Panel 5 "Developer Response" shows the developer sighing "You're right. I'll write the test." with a refilled coffee mug, Panel 6 "Outcome" shows Feature deployed ✅ Success, Tests ✅ All passing, Production ✅ Stable, Developer 😌 Confident, Brain Protector 😎 "Told you so", with an alternate ending box showing WITHOUT RULE #22: Feature deployed ❌ Production broken, Tests ❌ None written, 3am 🔥 Pager going off, Developer 😱 Panicking, 4am Still fixing..., using comic book panel style with dramatic colors, facial expressions showing emotions, contrasting colors for WITH versus WITHOUT scenarios (green for success, red for failure), and an educational but entertaining approach.

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

**Last Generated:** 2025-11-10 17:27:23  
**Generator:** CORTEX Documentation Refresh Plugin v2.0  
**Source:** CopilotRecommendedDiagrams.md  
**Format:** Single-paragraph Gemini-compatible prompts for technical diagrams
