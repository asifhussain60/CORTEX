# CORTEX Visual Diagram Prompts for Gemini

**Purpose:** Image generation prompts for creating comprehensive CORTEX architecture diagrams  
**Target:** Gemini Image Generation / DALL-E / Midjourney  
**Date:** 2025-11-05  
**Style Guide:** Clean, technical diagrams with consistent color scheme

---

## 🎨 Style Guidelines

**Color Palette:**
- **Tier 0 (Instinct):** Deep purple (#6B21A8) - Immutable foundation
- **Tier 1 (STM):** Bright blue (#3B82F6) - Active memory
- **Tier 2 (LTM):** Green (#10B981) - Long-term knowledge
- **Tier 3 (Context):** Orange (#F59E0B) - Real-time intelligence
- **Agents:** Teal (#14B8A6) - Specialist workers
- **Data Flow:** Gray arrows (#6B7280)
- **Success:** Emerald (#059669)
- **Warning:** Amber (#D97706)
- **Error:** Red (#DC2626)

**Typography:**
- Headers: Bold, sans-serif (Helvetica/Arial)
- Labels: Regular, sans-serif
- Technical terms: Monospace font

**Layout:**
- Clean, minimalist design
- Clear hierarchy (top-down or left-right flow)
- Consistent spacing and alignment
- Icons for different components
- Arrows show data flow direction

---

## 📊 Diagram 1: CORTEX 4-Tier Architecture Overview

**Prompt:**
```
Create a professional technical diagram showing CORTEX's 4-tier brain architecture in a vertical stack layout.

VISUAL STRUCTURE:
- Four horizontal layers stacked vertically
- Each tier is a rounded rectangle with gradient fill
- Left side shows tier name and icon
- Right side shows key metrics (size, speed)
- Arrows between tiers show data flow

TIER 0 (Top - Deep Purple #6B21A8):
- Icon: ⚖️ (scales/courthouse)
- Title: "Tier 0: Instinct Layer (Governance)"
- Subtitle: "IMMUTABLE FOUNDATION"
- Content boxes inside:
  * "22 Governance Rules"
  * "TDD, SOLID, DoR/DoD"
  * "Brain Protection System"
- Metrics (right side):
  * "Storage: ~20 KB"
  * "Access: O(1) lookup"
  * "Format: YAML"

TIER 1 (Second - Bright Blue #3B82F6):
- Icon: 💬 (speech bubble/conversation)
- Title: "Tier 1: Working Memory (STM)"
- Subtitle: "SHORT-TERM CONTEXT"
- Content boxes inside:
  * "Last 20 Conversations"
  * "FIFO Queue (automatic)"
  * "Entity Extraction"
  * "Cross-Conversation Linking"
- Metrics (right side):
  * "Storage: <100 KB"
  * "Queries: <50ms"
  * "Format: SQLite + FTS5"
- Arrow DOWN to Tier 2: "Pattern extraction when deleted"

TIER 2 (Third - Green #10B981):
- Icon: 🧠 (brain/patterns)
- Title: "Tier 2: Long-Term Knowledge (LTM)"
- Subtitle: "CONSOLIDATED PATTERNS"
- Content boxes inside:
  * "Intent Patterns (confidence-based)"
  * "File Relationships (co-modification)"
  * "Workflow Templates"
  * "Correction History"
  * "Validation Insights"
- Metrics (right side):
  * "Storage: <120 KB"
  * "Queries: <100ms"
  * "Format: SQLite + FTS5"
- Arrow DOWN to Tier 3: "Informs planning"

TIER 3 (Bottom - Orange #F59E0B):
- Icon: 📊 (chart/analytics)
- Title: "Tier 3: Context Intelligence"
- Subtitle: "REAL-TIME PROJECT METRICS"
- Content boxes inside:
  * "Git Activity (commits, churn)"
  * "Code Health (velocity, coverage)"
  * "Test Metrics (pass rates)"
  * "Work Patterns (productivity)"
- Metrics (right side):
  * "Storage: <50 KB"
  * "Queries: <10ms"
  * "Format: JSON cache"
  * "Refresh: Every 5 min"

BOTTOM SECTION (Summary):
- Total Storage: "<270 KB (47% smaller than KDS)"
- Total Query Speed: "10-100x faster than KDS"
- Test Coverage: "95%+ (370 permanent tests)"

ARROWS showing data flow:
- User Query (top) → All tiers consulted
- Tier 1 FIFO deletion → Tier 2 pattern extraction
- Tier 2 patterns → Tier 3 context correlation
- All tiers → Agent Decision (bottom)

Style: Clean, technical, professional. Use gradient fills for tiers. Include small icons. Make it clear this is a sophisticated cognitive system.
```

---

## 📊 Diagram 2: CORTEX vs KDS Comparison

**Prompt:**
```
Create a side-by-side comparison diagram showing KDS v8 (left) vs CORTEX v1.0 (right) with dramatic improvements highlighted.

LEFT SIDE - KDS v8 (Grayscale/Muted):
Header: "KDS v8 (Legacy)"
Icon: 🐌 (slow/sluggish)

Problems highlighted in RED boxes:
1. "6-Tier Architecture" (confusing)
   - Tier 0-5 with overlapping concepts
   - Corpus Callosum files (unnecessary)

2. "YAML/JSONL Storage" (slow)
   - Queries: 500-1000ms
   - Storage: 380-570 KB

3. "Verbose Responses" (overwhelming)
   - 30-50 lines average
   - 60% code snippets
   - 4,500-line kds.md

4. "Fragile Quality" (degradation risk)
   - 15% test coverage
   - Manual validation
   - No regression suite

RIGHT SIDE - CORTEX v1.0 (Vibrant/Modern):
Header: "CORTEX v1.0 (Redesigned)"
Icon: ⚡ (fast/efficient)

Solutions highlighted in GREEN boxes:
1. "4-Tier Architecture" (clean)
   - Tier 0-3 simplified
   - Clear separation
   - No file bloat

2. "SQLite Storage" (fast)
   - Queries: <100ms (10-100x faster)
   - Storage: <270 KB (47% smaller)
   - FTS5 full-text search

3. "Concise Responses" (user-friendly)
   - <10 lines average (5x shorter)
   - <20% code snippets (3x less)
   - Modular docs (<1000 lines each)

4. "Robust Quality" (permanent)
   - 95%+ test coverage (6x better)
   - 370 permanent tests
   - Cumulative regression suite

CENTER DIVIDER:
Large arrow pointing RIGHT (left to right)
Text: "MIGRATION"
Below: "3-5 weeks | 100% feature parity | Zero data loss"

BOTTOM METRICS BAR (comparison):
| Metric | KDS v8 | CORTEX v1.0 | Improvement |
Speed: [slow bar] [fast bar] "10-100x faster"
Size: [large bar] [small bar] "47% smaller"
Tests: [small bar] [large bar] "6x better coverage"
Conciseness: [long bar] [short bar] "5x more concise"

Style: Split-screen comparison. Use red/warning colors for KDS issues. Use green/success colors for CORTEX solutions. Make the improvements visually obvious. Professional, technical style.
```

---

## 📊 Diagram 3: Data Flow - User Request Lifecycle

**Prompt:**
```
Create a flowchart diagram showing how a user request flows through CORTEX from entry to completion, highlighting the intelligence at each step.

FLOW STRUCTURE (top to bottom):

1. USER INPUT (Top):
   - Speech bubble: "Add a purple button"
   - Icon: 👤 (user)

↓ (arrow)

2. ENTRY POINT:
   - Box: "#file:cortex.md (Universal Entry)"
   - Icon: 🚪 (door)
   - Label: "Single command for ALL interactions"

↓ (arrow)

3. TIER 1 QUERY (Blue box):
   - Icon: 💬
   - Action: "Check conversation history"
   - Output: "Context: HostControlPanel.razor mentioned 2 messages ago"
   - Speed: "<50ms"

↓ (arrow splits into 3)

4. PARALLEL TIER QUERIES:
   
   LEFT - TIER 0 (Purple box):
   - Icon: ⚖️
   - Action: "Validate against governance rules"
   - Output: "TDD required ✓, DoR met ✓"
   
   MIDDLE - TIER 2 (Green box):
   - Icon: 🧠
   - Action: "Find similar patterns"
   - Output: "Pattern found: 'button_addition_test_first' (conf: 0.97)"
   - Speed: "<100ms"
   
   RIGHT - TIER 3 (Orange box):
   - Icon: 📊
   - Action: "Check project context"
   - Output: "HostControlPanel.razor = hotspot (28% churn)"
   - Speed: "<10ms"

↓ (arrows converge)

5. INTENT ROUTER (Teal box):
   - Icon: 🧭
   - Decision: "Intent: PLAN (confidence 0.95)"
   - Action: "Route to Work Planner"
   - Enrichment: "Context + Pattern + Metrics attached"

↓ (arrow)

6. WORK PLANNER (Teal box):
   - Icon: 📋
   - Action: "Create multi-phase plan"
   - Uses:
     * Tier 2 pattern (button_addition_test_first)
     * Tier 3 context (file hotspot warning)
   - Output: "4-phase plan with TDD workflow"

↓ (arrow)

7. EXECUTION (Multiple Teal boxes in sequence):
   - Phase 0: "Prepare element ID" (Test Generator)
   - Phase 1: "RED - Failing test" (Test Generator)
   - Phase 2: "GREEN - Implementation" (Code Executor)
   - Phase 3: "REFACTOR - Validation" (Health Validator)

↓ (arrow)

8. COMMIT (Teal box):
   - Icon: 📦
   - Action: "Commit Handler validates and commits"
   - Output: "feat(host-panel): Add purple action button"

↓ (arrow)

9. LEARNING (Arrow back UP to tiers):
   - Event logged → Tier 2
   - Pattern reinforced (confidence ↑)
   - Tier 3 metrics updated
   - Tier 1 conversation stored

↓ (arrow)

10. USER RESPONSE (Bottom):
    - Icon: ✅
    - Summary: "Purple button added to HostControlPanel.razor"
    - Files: 2 modified
    - Tests: 3 created (all passing)
    - Time: 84 seconds
    - Next: Ready for next feature

TIMING ANNOTATIONS (right side):
- Tier queries: <160ms total
- Planning: ~2 seconds
- Execution: 75 seconds
- Total: 84 seconds (under 2-minute estimate)

Style: Vertical flowchart with clear arrows. Use tier colors for each component. Show parallel processing where applicable. Include timing annotations. Professional, technical style.
```

---

## 📊 Diagram 4: Pattern Learning Lifecycle

**Prompt:**
```
Create a circular lifecycle diagram showing how CORTEX learns from interactions and improves over time.

CIRCULAR FLOW (clockwise):

1. TOP (12 o'clock): USER INTERACTION
   - Icon: 👤💬
   - Example: "Add share button"
   - Box: "New request received"

↓ (clockwise arrow)

2. RIGHT-TOP (2 o'clock): EVENT LOGGING
   - Icon: 📝
   - Box: "Actions logged to event stream"
   - Examples:
     * intent_detected
     * file_modified
     * test_created
     * task_completed

↓ (clockwise arrow)

3. RIGHT (3 o'clock): TIER 1 STORAGE
   - Icon: 💬 (Blue)
   - Box: "Conversation saved to STM"
   - Details:
     * Messages stored
     * Entities extracted
     * Context linked

↓ (clockwise arrow)

4. RIGHT-BOTTOM (4 o'clock): FIFO TRIGGER
   - Icon: 🔄
   - Box: "20th conversation reached"
   - Action: "Oldest conversation deleted"

↓ (clockwise arrow)

5. BOTTOM (6 o'clock): PATTERN EXTRACTION
   - Icon: 🧠 (Green)
   - Box: "Brain Updater processes events"
   - Extracts:
     * Intent patterns
     * File relationships
     * Workflow templates
     * Corrections
     * Insights

↓ (clockwise arrow)

6. LEFT-BOTTOM (8 o'clock): TIER 2 STORAGE
   - Icon: 🗄️ (Green)
   - Box: "Patterns stored in LTM"
   - SQLite with confidence scores
   - FTS5 for semantic search

↓ (clockwise arrow)

7. LEFT (9 o'clock): PATTERN REINFORCEMENT
   - Icon: 💪
   - Box: "Pattern matched in new request"
   - Actions:
     * times_used++
     * confidence recalculated
     * success_rate updated

↓ (clockwise arrow)

8. LEFT-TOP (10 o'clock): INTELLIGENT RESPONSE
   - Icon: 🎯
   - Box: "Pattern-informed decision"
   - Benefits:
     * Faster routing
     * Better estimates
     * Proactive warnings
     * Workflow reuse

↓ (clockwise arrow back to TOP)

9. BACK TO USER INTERACTION
   - Next request benefits from learning
   - Cycle repeats, improving continuously

CENTER OF CIRCLE:
Large icon: 🧠⚡
Text: "CONTINUOUS LEARNING"
Metrics:
- "Pattern accuracy: >90%"
- "Reuse rate: >50%"
- "Learning speed: <2min"

DECAY MECHANISM (Side annotation):
Small box outside circle (bottom-left):
- Icon: ⏱️
- Title: "Pattern Decay"
- "60 days: -10% confidence"
- "90 days: -25% confidence"
- "120 days: <0.50 = delete"
- "Keeps knowledge fresh"

CONSOLIDATION (Side annotation):
Small box outside circle (bottom-right):
- Icon: 🔗
- Title: "Pattern Consolidation"
- "80%+ similar → merge"
- "Stronger unified pattern"
- "Reduces duplication"

Style: Circular flow with clockwise arrows. Use tier colors for each stage. Center should be prominent. Include side annotations for decay/consolidation. Clean, modern, technical style.
```

---

## 📊 Diagram 5: Test Coverage Pyramid

**Prompt:**
```
Create a test pyramid diagram showing CORTEX's comprehensive 370-test suite with layers and coverage.

PYRAMID STRUCTURE (bottom to top):

LAYER 1 (Base - Largest, Green):
Title: "Unit Tests"
Count: "295 tests"
Coverage: "95%+"
Icon: 🧪
Components tested:
- Tier 0: 15 tests (rule enforcement)
- Tier 1: 50 tests (conversation CRUD)
- Tier 2: 67 tests (pattern learning)
- Tier 3: 38 tests (metrics collection)
- Agents: 125 tests (specialist logic)
Purpose: "Test individual components in isolation"
Speed: "<5 seconds total"

LAYER 2 (Middle - Medium, Blue):
Title: "Integration Tests"
Count: "45 tests"
Coverage: "90%+"
Icon: 🔗
Components tested:
- Tier 1 ↔ Tier 2: 8 tests (STM → LTM flow)
- Tier 2 ↔ Tier 3: 6 tests (patterns → context)
- Tier workflows: 12 tests (cross-tier coordination)
- Agent handoff: 10 tests (router → agents)
- Auto-recording: 9 tests (3-layer capture)
Purpose: "Test component interactions"
Speed: "10-15 seconds total"

LAYER 3 (Top - Smallest, Orange):
Title: "Regression Tests"
Count: "30 tests"
Coverage: "100% feature parity"
Icon: ✅
Components tested:
- KDS feature parity: 20 tests
- Performance benchmarks: 5 tests
- BRAIN-SHARPENER scenarios: 5 tests
Purpose: "Ensure zero degradation from KDS"
Speed: "5-8 seconds total"

TOTAL (Top of pyramid):
Large text: "370 PERMANENT TESTS"
Subtitle: "95%+ Coverage | <30s Total Runtime"
Icon: 🛡️ (shield)

LEFT SIDE ANNOTATION:
Title: "Why This Matters"
Comparison with KDS:
- KDS: ~15% coverage (❌ fragile)
- CORTEX: 95%+ coverage (✅ robust)
Benefit: "Zero degradation guarantee"

RIGHT SIDE ANNOTATION:
Title: "Test-First Methodology"
Process:
1. Write test (RED)
2. Implement feature (GREEN)
3. Refactor (keep tests GREEN)
4. Tests never deleted
Benefit: "Cumulative protection"

BOTTOM ANNOTATION:
Performance metrics:
- Full suite: <30 seconds
- Per-commit: <5 seconds (unit only)
- Pre-merge: 30 seconds (full suite)
- Nightly: 30 seconds + benchmarks

Style: Classic test pyramid shape. Use green (unit), blue (integration), orange (regression) layers. Include counts and icons. Professional, technical style. Make the 95% coverage visually prominent.
```

---

## 📊 Diagram 6: Response Format Comparison

**Prompt:**
```
Create a before/after comparison showing KDS verbose responses vs CORTEX concise responses.

LAYOUT: Side-by-side panels

LEFT PANEL - KDS v8 Response (Grayscale, looks cluttered):
Header: "KDS v8 Style (Verbose)"
Icon: 📚 (overwhelming)

Example response in a scrollable document:
"""
I'll create the UserService for you. Here's the complete implementation:

```csharp
public interface IUserService
{
    Task<User> GetUserAsync(int id);
    // ... 30 more lines
}
```

Now let's create the implementation:

```csharp
public class UserService : IUserService
{
    private readonly IDbContext _context;
    // ... 50 more lines
}
```

And here's the controller:

```csharp
[ApiController]
public class UserController
{
    // ... 40 more lines
}
```

Now let's add tests:

```csharp
public class UserServiceTests
{
    // ... 45 more lines
}
```
"""

Annotations on left panel:
- "150+ lines total" (RED)
- "4 code blocks" (RED)
- "60% of response is code" (RED)
- "5-8 minutes to read" (RED)
- "Overwhelming for simple tasks" (RED)

RIGHT PANEL - CORTEX v1.0 Response (Vibrant, looks clean):
Header: "CORTEX v1.0 Style (Concise)"
Icon: ✨ (elegant)

Example response in a compact box:
"""
✅ User authentication implemented

**Summary:**
- Created `IUserService` interface with async methods
- Implemented `UserService` with DB context injection
- Added `UserController` with authentication endpoints
- Created `UserServiceTests` (15 tests, all passing)

📄 **Files:** 4 created, 0 errors, 0 warnings

**Next:** Ready to integrate with frontend components
"""

Annotations on right panel:
- "9 lines total" (GREEN)
- "0 code blocks" (GREEN)
- "0% code (summary only)" (GREEN)
- "<30 seconds to read" (GREEN)
- "Action-focused, scannable" (GREEN)

BOTTOM COMPARISON BAR:
| Metric | KDS v8 | CORTEX v1.0 |
Response Length: [long bar 150 lines] [short bar 9 lines]
Code Shown: [large bar 60%] [small bar 0%]
Read Time: [long bar 5-8 min] [short bar <30 sec]
User Satisfaction: [low 😐] [high 😊]

CALLOUT BOX (bottom right):
Title: "Code Available When Needed"
- User can ask: "show me the code"
- Documentation has full details
- But not forced in every response
- "Summary-first, code-last philosophy"

Style: Clean side-by-side comparison. Use visual contrast (cluttered vs clean). Make the improvement obvious. Include emoji annotations for quick scanning. Professional but friendly style.
```

---

## 📊 Diagram 7: CORTEX Folder Structure

**Prompt:**
```
Create a tree-style folder structure diagram showing CORTEX's organized architecture.

TREE STRUCTURE:

📁 CORTEX/ (Root - Purple header)
│
├── 📁 cortex-brain/ (BRAIN Storage - gradient purple/blue)
│   ├── 📁 tier0-instinct/
│   │   ├── 📄 core-principles.yaml (22 governance rules)
│   │   ├── 📄 tier-boundaries.yaml (data separation)
│   │   └── 📄 protection-rules.yaml (brain integrity)
│   │   Size: ~20 KB
│   │
│   ├── 📁 tier1-working-memory/
│   │   ├── 🗄️ conversations.db (SQLite - last 20 convs)
│   │   ├── 📄 schema.sql (database structure)
│   │   └── 📁 migrations/ (version control)
│   │   Size: <100 KB
│   │
│   ├── 📁 tier2-long-term-knowledge/
│   │   ├── 🗄️ patterns.db (SQLite + FTS5)
│   │   ├── 📄 schema.sql (pattern tables)
│   │   └── 📁 migrations/
│   │   Size: <120 KB
│   │
│   └── 📁 tier3-context-intelligence/
│       ├── 📄 metrics.json (real-time cache)
│       ├── 📄 git-activity.json (commit analysis)
│       └── 📄 test-activity.json (test metrics)
│       Size: <50 KB
│
├── 📁 cortex-agents/ (Specialist Agents - Teal)
│   ├── 📁 user/ (User-facing)
│   │   └── 📄 cortex.md (Universal entry point ⭐)
│   │
│   ├── 📁 internal/ (10 specialist agents)
│   │   ├── 📄 intent-router.md
│   │   ├── 📄 work-planner.md
│   │   ├── 📄 code-executor.md
│   │   ├── 📄 test-generator.md
│   │   ├── 📄 error-corrector.md
│   │   ├── 📄 health-validator.md
│   │   ├── 📄 brain-updater.md
│   │   ├── 📄 brain-protector.md
│   │   ├── 📄 change-governor.md
│   │   └── 📄 commit-handler.md
│   │
│   └── 📁 abstractions/ (DIP - Dependency Inversion)
│       ├── 📄 session-loader.md
│       ├── 📄 file-accessor.md
│       ├── 📄 test-runner.md
│       └── 📄 brain-query.md
│
├── 📁 cortex-scripts/ (Automation - Orange)
│   ├── 📁 brain/
│   │   ├── 📄 migrate-jsonl-to-sqlite.ts
│   │   ├── 📄 tier1-health-check.ts
│   │   └── 📄 backup-tier1.ts
│   │
│   ├── 📁 git/
│   │   ├── 📄 setup-hooks.ts
│   │   └── 📄 validate-commit.ts
│   │
│   ├── 📁 monitoring/
│   │   ├── 📄 health-dashboard.ts
│   │   └── 📄 metrics-reporter.ts
│   │
│   └── 📁 setup/
│       ├── 📄 install-cortex.ts
│       └── 📄 configure-workspace.ts
│
├── 📁 cortex-tests/ (Comprehensive Testing - Green)
│   ├── 📁 unit/ (295 tests)
│   │   ├── 📄 tier0-tests.test.ts
│   │   ├── 📄 tier1-tests.test.ts
│   │   ├── 📄 tier2-tests.test.ts
│   │   ├── 📄 tier3-tests.test.ts
│   │   └── 📄 agent-tests.test.ts
│   │
│   ├── 📁 integration/ (45 tests)
│   │   ├── 📄 tier-workflow.test.ts
│   │   └── 📄 agent-handoff.test.ts
│   │
│   ├── 📁 regression/ (30 tests)
│   │   ├── 📄 kds-feature-parity.test.ts
│   │   └── 📄 performance-benchmarks.test.ts
│   │
│   └── 📁 performance/
│       ├── 📄 query-speed.bench.ts
│       └── 📄 storage-efficiency.bench.ts
│
├── 📁 cortex-docs/ (Documentation)
│   ├── 📁 architecture/
│   │   ├── 📄 overview.md
│   │   └── 📄 tier-designs.md
│   │
│   ├── 📁 guides/
│   │   ├── 📄 quick-start.md
│   │   └── 📄 user-guide.md
│   │
│   └── 📁 api/
│       └── 📄 agent-reference.md
│
├── 📁 cortex-design/ (Design Phase Docs - Temporary)
│   ├── 📄 CORTEX-DNA.md (Core principles ⭐)
│   ├── 📄 MIGRATION-STRATEGY.md
│   ├── 📁 feature-inventory/
│   ├── 📁 architecture/
│   ├── 📁 phase-plans/
│   └── 📁 test-specifications/
│
└── 📁 cortex-governance/ (Immutable Rules)
    ├── 📄 core-principles.md (TDD, SOLID, DoR/DoD)
    ├── 📄 tier-boundaries.md (data separation rules)
    └── 📄 protection-rules.md (brain protection contracts)

SUMMARY BOX (bottom):
Total Storage: <270 KB (47% smaller than KDS)
Total Tests: 370 permanent tests (95%+ coverage)
Organization: Clean, logical, maintainable
Single Entry Point: cortex-agents/user/cortex.md ⭐

Style: Tree diagram with folder icons. Use colors to differentiate sections (brain=purple/blue, agents=teal, scripts=orange, tests=green). Include size annotations. Highlight entry point with star. Professional, organized, technical style.
```

---

## 📊 Diagram 8: Performance Benchmarks Dashboard

**Prompt:**
```
Create a performance metrics dashboard showing CORTEX's speed improvements over KDS.

DASHBOARD LAYOUT (4 quadrants):

TOP LEFT - QUERY LATENCY:
Title: "Query Speed Comparison"
Chart type: Horizontal bar chart
Metrics:
- Tier 1 (STM) Query:
  * KDS: 500ms (red bar, long)
  * CORTEX: 47ms (green bar, short)
  * Improvement: ⚡ 10.6x faster

- Tier 2 (LTM) Query:
  * KDS: 850ms (red bar, long)
  * CORTEX: 92ms (green bar, short)
  * Improvement: ⚡ 9.2x faster

- Tier 3 (Context) Query:
  * KDS: 2300ms (red bar, very long)
  * CORTEX: 8ms (green bar, tiny)
  * Improvement: ⚡ 287x faster

- Full-text Search:
  * KDS: N/A (gray, not supported)
  * CORTEX: 134ms (green bar)
  * Improvement: ✨ NEW CAPABILITY

TOP RIGHT - STORAGE EFFICIENCY:
Title: "Storage Size Comparison"
Chart type: Pie charts side-by-side

KDS v8 Pie Chart (left):
Total: 486 KB
Segments:
- Tier 1 (JSONL): 127 KB (26%)
- Tier 2 (YAML): 143 KB (29%)
- Tier 3 (YAML): 89 KB (18%)
- Tier 4 (Events): 67 KB (14%)
- Tier 5 (Health): 60 KB (12%)

CORTEX v1.0 Pie Chart (right):
Total: 258 KB
Segments:
- Tier 0 (YAML): 20 KB (8%)
- Tier 1 (SQLite): 87 KB (34%)
- Tier 2 (SQLite): 103 KB (40%)
- Tier 3 (JSON): 48 KB (19%)

Improvement: ⬇️ 47% smaller (228 KB saved)

BOTTOM LEFT - TEST COVERAGE:
Title: "Quality Assurance"
Chart type: Progress bars

KDS v8:
Bar: 15% filled (red)
Label: "~15% coverage (❌ fragile)"
Tests: "Estimated <60 tests"

CORTEX v1.0:
Bar: 95% filled (green)
Label: "95%+ coverage (✅ robust)"
Tests: "370 permanent tests"
Breakdown:
- Unit: 295 tests
- Integration: 45 tests
- Regression: 30 tests

Improvement: 🛡️ 6.3x better coverage

BOTTOM RIGHT - LEARNING SPEED:
Title: "BRAIN Update Cycle"
Chart type: Circular progress/timeline

KDS v8 (outer ring, slow):
Steps:
1. Collect 50+ events (waiting... 2-8 hours)
2. Parse JSONL (2-3 min)
3. Parse YAML (1-2 min)
4. Extract patterns (3-5 min)
5. Write YAML (30-60 sec)
Total: 5-10 minutes ⏱️ (red)

CORTEX v1.0 (inner ring, fast):
Steps:
1. Event logged (instant)
2. Extract pattern (immediate)
3. SQLite insert (milliseconds)
4. Update indices (auto)
Total: <2 seconds ⚡ (green)

Improvement: 🚀 150-300x faster learning

CENTER SUMMARY BOX:
Overall CORTEX Performance:
✅ 10-100x faster queries
✅ 47% smaller storage
✅ 6x better test coverage
✅ 150x faster learning
✅ 100% feature parity

Target: All benchmarks EXCEEDED ✨

Style: Modern dashboard with 4 quadrants. Use charts (bars, pies, progress). Color code improvements (green=good, red=bad/old). Include icons and emoji for quick understanding. Professional, data-driven style.
```

---

## 📊 Diagram 9: Intent Router Decision Flow

**Prompt:**
```
Create a decision tree flowchart showing how the Intent Router analyzes and routes user requests.

FLOWCHART STRUCTURE (top to bottom with branches):

START (Top):
User message received: "Make it purple"
Icon: 👤💬

↓

STEP 1: TIER 1 CONTEXT CHECK (Blue box):
Icon: 💬
Action: "Query last 10 messages for context"
Query result:
- Message 2 ago: "Add FAB button"
- Message 5 ago: "HostControlPanel.razor"
Resolution: "it" = "FAB button"
Speed: 42ms

↓

STEP 2: TIER 2 PATTERN MATCH (Green box):
Icon: 🧠
Action: "Search intent patterns (FTS5)"
Matches found:
1. "make [pronoun] [color]" - confidence: 0.92
2. "modify [component]" - confidence: 0.78
3. "change style" - confidence: 0.65
Best match: #1 (highest confidence)
Speed: 87ms

↓

DECISION POINT (Diamond):
"Confidence ≥ 0.70?"

├── YES (Right branch - Green):
│   Auto-route decision
│   Icon: ✅
│   
│   ↓
│   
│   STEP 3a: TIER 3 ENRICHMENT (Orange box):
│   Icon: 📊
│   Action: "Gather context for execution"
│   Context added:
│   - File: HostControlPanel.razor (28% churn - hotspot!)
│   - Recent changes: 2 days ago
│   - Related files: noor-canvas.css (75% co-mod)
│   Speed: 6ms
│   
│   ↓
│   
│   ROUTE TO: Code Executor
│   Icon: 🔧 (Teal box)
│   Message: "Modify FAB button color to purple"
│   Attached context:
│   - Target file confirmed
│   - Hotspot warning included
│   - Related files suggested
│   
│   ↓
│   
│   SUCCESS (Green):
│   Icon: ✅
│   "Task routed and executed"
│
└── NO (Left branch - Yellow):
    Low confidence routing
    Icon: ⚠️
    
    ↓
    
    STEP 3b: CLARIFICATION REQUEST (Yellow box):
    Icon: ❓
    Action: "Ask user to clarify intent"
    
    Suggested clarifications:
    1. "Did you mean modify the FAB button? (pattern match: 0.92)"
    2. "Or change something else? (pattern match: 0.78)"
    
    ↓
    
    USER CLARIFIES
    Icon: 👤💬
    
    ↓
    
    LEARN & ROUTE (Green box):
    Icon: 🧠➕
    Actions:
    - Log clarification event
    - Update pattern confidence
    - Route to appropriate agent
    
    ↓
    
    SUCCESS (Green):
    Icon: ✅
    "Pattern learned, task executed"

PARALLEL PROTECTION CHECK (Side branch from DECISION POINT):
Icon: 🛡️
TIER 0 GOVERNANCE (Purple box):
Checks:
1. TDD required? (if code change)
2. DoR criteria met?
3. Violates any rules?
If violations: CHALLENGE USER
If clean: PROCEED

TIMING SUMMARY (Bottom):
Total routing decision: <150ms
- Tier 1 context: 42ms
- Tier 2 pattern match: 87ms
- Tier 3 enrichment: 6ms
- Overhead: 15ms

LEGEND (Bottom right):
Colors:
- Blue: STM (Tier 1)
- Green: LTM (Tier 2)
- Orange: Context (Tier 3)
- Purple: Governance (Tier 0)
- Teal: Agent execution
- Yellow: User interaction

Style: Flowchart with decision diamonds and process boxes. Use tier colors consistently. Show both success paths (auto-route) and edge cases (clarification). Include timing annotations. Professional, technical style.
```

---

## 📊 Diagram 10: Migration Timeline Gantt Chart

**Prompt:**
```
Create a Gantt chart showing the 6-phase CORTEX migration timeline with dependencies and milestones.

GANTT CHART LAYOUT:

HEADER:
Title: "CORTEX Migration Timeline"
Subtitle: "KDS v8 → CORTEX v1.0 (Clean Slate Redesign)"
Total Duration: "3-5 weeks (52-68 hours focused work)"

TIME AXIS (horizontal, top):
Week 1 | Week 2 | Week 3 | Week 4 | Week 5
Day markers: 1-5 per week (assuming 5-day work weeks)

PHASES (vertical rows):

1. PHASE 0: Instinct Layer (Purple bar)
   Duration: 4-6 hours (Day 1)
   Bar: Days 1
   Deliverables:
   - 22 governance rules in YAML
   - Core principles defined
   - Tier boundaries enforced
   Tests: 15 unit tests ✅
   Status: Ready to start

2. PHASE 1: Working Memory (Blue bar)
   Duration: 8-10 hours (Days 2-3)
   Bar: Days 2-3
   Depends on: Phase 0 ✅
   Deliverables:
   - SQLite STM database
   - FIFO queue automation
   - Entity extraction
   - 3-layer auto-recording
   Tests: 50 unit + 8 integration ✅
   Status: Designed

3. PHASE 2: Long-Term Knowledge (Green bar)
   Duration: 10-12 hours (Days 4-6)
   Bar: Days 4-6
   Depends on: Phase 1 ✅
   Deliverables:
   - SQLite LTM with FTS5
   - Intent patterns
   - File relationships
   - Workflow templates
   - Pattern lifecycle
   Tests: 67 unit + 12 integration ✅
   Status: Designed

4. PHASE 3: Context Intelligence (Orange bar)
   Duration: 8-10 hours (Days 7-9)
   Bar: Days 7-9
   Depends on: Phase 2 ✅
   Deliverables:
   - JSON metrics cache
   - Git activity tracking
   - Test metrics
   - Work pattern analysis
   - Proactive warnings
   Tests: 38 unit + 6 integration ✅
   Status: Designed

5. PHASE 4: Specialist Agents (Teal bar)
   Duration: 12-16 hours (Days 10-14)
   Bar: Days 10-14
   Depends on: Phase 3 ✅
   Deliverables:
   - 10 agents refactored
   - Concise response format
   - SQLite brain queries
   - Agent coordination
   Tests: 125 unit tests ✅
   Status: Designed

6. PHASE 5: Entry Point & Workflows (Yellow bar)
   Duration: 6-8 hours (Days 15-17)
   Bar: Days 15-17
   Depends on: Phase 4 ✅
   Deliverables:
   - cortex.md universal entry
   - TDD workflow
   - Commit workflow
   - BRAIN update workflow
   Tests: 45 workflow tests ✅
   Status: Designed

7. PHASE 6: Migration Validation (Magenta bar)
   Duration: 4-6 hours (Days 18-19)
   Bar: Days 18-19
   Depends on: Phase 5 ✅
   Deliverables:
   - Complete test suite passing
   - 100% KDS feature parity
   - Performance benchmarks met
   - Repository renamed
   - Merged to main
   Tests: 30 regression tests ✅
   Status: Final validation

MILESTONES (Diamond markers on timeline):
📍 Day 1: Phase 0 complete (Governance solid)
📍 Day 3: Phase 1 complete (STM working)
📍 Day 6: Phase 2 complete (LTM learning)
📍 Day 9: Phase 3 complete (Context aware)
📍 Day 14: Phase 4 complete (Agents refactored)
📍 Day 17: Phase 5 complete (Entry point live)
📍 Day 19: Phase 6 complete (Migration DONE) 🎉

CUMULATIVE TEST COUNT (bottom graph):
Cumulative tests over time (line graph):
Day 1: 15 tests
Day 3: 73 tests
Day 6: 152 tests
Day 9: 196 tests
Day 14: 321 tests
Day 17: 366 tests
Day 19: 396 tests (includes regression)

Target: 370+ permanent tests

RISK MITIGATION (bottom right box):
Safety measures:
✅ KDS v8 preserved on main
✅ Work on cortex-redesign branch
✅ Each phase validated before next
✅ Rollback capability at all times
✅ Zero data loss guaranteed

Style: Professional Gantt chart with colored bars for each phase. Show dependencies with arrows. Include milestone markers. Add cumulative test graph at bottom. Use consistent tier colors. Technical, project management style.
```

---

## 🎨 Additional Diagram Ideas

### Diagram 11: CORTEX Agent Ecosystem
- Circular diagram showing 10 specialist agents
- Intent Router at center
- Agents around the perimeter
- Arrows showing handoff patterns
- Color-coded by responsibility

### Diagram 12: Knowledge Graph Structure
- Graph database visualization
- Nodes = patterns, files, features
- Edges = relationships, similarities
- Confidence scores on edges
- Clustering visualization

### Diagram 13: Auto-Recording 3-Layer System
- Funnel diagram showing capture rates
- Layer 1 (Copilot): 50% → Target 90%
- Layer 2 (Sessions): 15% → Target 100%
- Layer 3 (Manual): 6%
- Combined: 71% → Target 85%+

### Diagram 14: Pattern Decay & Consolidation
- Timeline showing pattern lifecycle
- Fresh patterns (green)
- Aging patterns (yellow)
- Decaying patterns (orange)
- Merged patterns (purple)
- Deleted patterns (red/crossed out)

### Diagram 15: Security & Protection Layers
- Concentric circles showing protection
- Inner: Tier 0 (immutable core)
- Middle: Validation & anomaly detection
- Outer: Backup & rollback
- Shield icon at center

---

## 📝 Usage Instructions

**For Gemini Image Generation:**
1. Copy any prompt above
2. Paste into Gemini with prefix: "Create a technical diagram: [PROMPT]"
3. Request specific style adjustments if needed
4. Iterate on colors, layout, or details

**For Other AI Image Generators:**
- DALL-E: Works well with these prompts
- Midjourney: May need style keyword adjustments
- Stable Diffusion: Add "technical diagram, clean, professional" prefix

**For Manual Creation:**
- Use prompts as detailed specifications
- Tools: Lucidchart, draw.io, Figma, Adobe Illustrator
- Follow color palette and style guidelines

---

**Last Updated:** 2025-11-05  
**Version:** 1.0  
**Total Diagrams:** 10 core + 5 additional ideas
