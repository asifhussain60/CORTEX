# KDS Mind Palace: Visual Blueprint Prompts

**Purpose:** Gemini AI image generation prompts for visualizing the KDS Whole-Brain Architecture  
**How to Use:** Copy each prompt into Gemini (gemini.google.com) to generate architectural diagrams  
**Image Style:** Technical diagrams, infographics, architectural blueprints  
**Last Updated:** November 4, 2025

---

## 🎨 How to Generate Images

1. Go to [gemini.google.com](https://gemini.google.com)
2. Copy a prompt from below
3. Paste into Gemini chat
4. Click "Generate image" or press Enter
5. Save the generated image to `generated-images/` folder
6. Repeat for all 8 prompts

**Recommended naming:**
- `01-complete-mind-palace.png`
- `02-hemispheres.png`
- `03-memory-flow.png`
- etc.

---

## Prompt 1: The Complete Mind Palace (5-Tier Architecture)

```
Create a detailed architectural diagram of the KDS Mind Palace showing 5 distinct floors stacked vertically:

STRUCTURE:
- A grand palace building with 5 visible floors plus a foundation
- Front entrance with "One Door" label (large, welcoming)
- Each floor has distinct visual characteristics and a character

FLOORS (bottom to top):
Foundation/Ground Floor - "The Keeper" (Core Instincts)
  - Stone foundation with eternal flame
  - Pillars inscribed with rules: "TDD", "SOLID", "Quality"
  - Ancient, permanent, unchanging aesthetic
  - Color: Deep gray stone with golden inscriptions

1st Floor - "The Scribe" (Active Memory)
  - Glass-walled observatory with 20 glowing scrolls
  - FIFO queue visualization (scrolls entering/leaving)
  - Fast-moving, transparent, dynamic aesthetic
  - Color: Clear glass with blue-white light
  - Label: "Last 20 Conversations"

2nd Floor - "The Librarian" (Recollection)
  - Vast library with glowing web of knowledge
  - Interconnected nodes and threads between books
  - Systematic, organized, connected aesthetic
  - Color: Warm amber with golden threads
  - Label: "Learned Patterns & Workflows"

3rd Floor - "The Observer" (Awareness)
  - Observatory deck with telescopes and monitoring screens
  - Charts showing metrics, graphs, and project health
  - Data-driven, analytical, far-seeing aesthetic
  - Color: Cool blue with dashboard displays
  - Label: "Project Context & Metrics"

Top Floor - "The Dreamer" (Imagination)
  - Creative studio with floating idea clouds
  - Experimental lab benches, sketch boards
  - Colorful, creative, experimental aesthetic
  - Color: Vibrant purple with rainbow accents
  - Label: "Ideas & Experiments"

FRONT ENTRANCE:
- Single grand door labeled "One Door"
- Friendly gatekeeper figure standing welcomingly
- Sign: "Speak in plain words. I'll take it from there."

VISUAL STYLE:
- Architectural cross-section view
- Clean, professional infographic style
- Each floor clearly labeled with tier name
- Characters visible in their respective floors
- Soft lighting highlighting each tier
- Modern but with classical architectural elements
```

---

## Prompt 2: Left Brain vs Right Brain Hemispheres

```
Create a split-view diagram showing the KDS Mind Palace divided into two hemispheres like a human brain:

LEFT SIDE (Analytical/Tactical):
- Title: "LEFT BRAIN - The Tactical Executor"
- Color scheme: Cool blues and grays
- Agents shown as precision instruments:
  * The Builder (code-executor.md) - Surgical tools icon
  * The Tester (test-generator.md) - Microscope icon
  * The Fixer (error-corrector.md) - Repair wrench icon
  * The Inspector (health-validator.md) - Checklist icon
  * The Archivist (commit-handler.md) - Filing cabinet icon
- Visual metaphors: Gears, circuits, precise measurements
- Labels: "Sequential Processing", "Detail Verification", "TDD Enforcement"
- Show RED → GREEN → REFACTOR cycle

RIGHT SIDE (Creative/Strategic):
- Title: "RIGHT BRAIN - The Strategic Planner"
- Color scheme: Warm purples and oranges
- Agents shown as thinking/planning tools:
  * The Dispatcher (intent-router.md) - Compass icon
  * The Planner (work-planner.md) - Blueprint icon
  * The Analyst (screenshot-analyzer.md) - Magnifying glass icon
  * The Governor (change-governor.md) - Shield icon
  * The Brain Protector (brain-protector.md) - Guardian icon
- Visual metaphors: Clouds, networks, patterns
- Labels: "Holistic Thinking", "Pattern Recognition", "Risk Assessment"
- Show multi-phase planning workflow

CENTER (Corpus Callosum):
- Bridge connecting both hemispheres
- Message queue flowing between sides
- Labeled: "Coordination & Communication"
- Arrows showing bidirectional information flow
- Icon: Network hub or bridge

ANNOTATIONS:
- "Right brain plans → Corpus callosum delivers → Left brain executes"
- "Left brain results → Feed back → Right brain learns"
- "Tier 0 (Instincts) guards both hemispheres"

VISUAL STYLE:
- Clean, modern infographic
- Professional medical diagram aesthetic
- Clear separation between hemispheres
- Icons for each agent
- Flowing connectors showing communication
```

---

## Prompt 3: Memory Flow (Conversations → Knowledge → Instincts)

```
Create a flowchart diagram showing how memories transform through KDS tiers:

FLOW STAGES (left to right):

STAGE 1: USER INPUT
- Person icon speaking
- Speech bubble: "I want to add a FAB button"
- Arrow pointing right labeled "Captured"

STAGE 2: TIER 1 (Active Memory)
- Glass container with 20 glowing orbs (conversations)
- One orb highlighted: "FAB button conversation"
- Label: "Stored for immediate recall"
- Timer: "Kept until 20 newer conversations"
- Arrow pointing right labeled "Patterns extracted when deleted"

STAGE 3: TIER 2 (Recollection)
- Web/network of interconnected nodes
- Node highlighted: "ui_component_creation pattern"
- Confidence meter: 0.87
- Sample size: 23 instances
- Label: "Consolidated into learned pattern"
- Arrow pointing right labeled "If proven successful (95%+ confidence)"

STAGE 4: TIER 0 (Core Instincts)
- Stone pillar with inscription
- Eternal flame icon
- Text: "Component IDs prevent test brittleness"
- Label: "Promoted to permanent wisdom"
- Badge: "Survives amnesia"

ANNOTATIONS:
- Below TIER 1: "Short-term (20 conversations)"
- Below TIER 2: "Long-term (application lifetime)"
- Below TIER 0: "Eternal (cross-project)"
- Show FIFO deletion arrow from TIER 1
- Show pattern extraction arrow before deletion
- Show promotion criteria: "Confidence ≥0.95 + Proven across projects"

SIDE FLOW (Amnesia):
- When user switches projects:
  * TIER 1: Red X "Deleted"
  * TIER 2: Yellow warning "Partially deleted (app-specific)"
  * TIER 0: Green checkmark "Preserved"
- Arrow showing generic patterns moving from TIER 2 → TIER 0

VISUAL STYLE:
- Left-to-right flowchart
- Color-coded stages (blue → amber → gray)
- Clear arrows showing transformations
- Icons for each tier
- Decision diamonds for promotion criteria
```

---

## Prompt 4: Imagination Tier (Creative Reservoir)

```
Create a detailed view of the Imagination tier (Tier 4) showing idea management workflow:

MAIN AREA - Creative Studio Layout:

SECTION 1: IDEAS BACKLOG (Cork Board)
- Pinned cards with different priority colors:
  * Red card: "Real-time collaboration" (Priority: High, Oct 15)
  * Yellow card: "Voice commands" (Priority: Medium, Oct 28)
  * Green card: "Keyboard shortcuts" (Priority: High, Nov 1)
- Thumbtacks and string connecting related ideas
- Label: "Captured Ideas - No Flow Interruption"

SECTION 2: EXPERIMENTS IN PROGRESS (Lab Bench)
- Test tubes and beakers with labels:
  * Flask with checkmark: "Percy visual testing" → Status: Successful
  * Beaker bubbling: "SQLite for BRAIN storage" → Status: In Progress (1 week)
  * Test tube with X: "Auto-generated comments" → Status: Failed (lesson learned)
- Progress indicators (25%, 60%, 100%)
- Label: "Active Experiments - Track & Measure"

SECTION 3: FORGOTTEN INSIGHTS (Trophy Case)
- Display cases with badges:
  * Trophy: "Component IDs prevent brittleness" → Promoted to TIER 0
  * Medal: "Small commits = less rework" → Applied successfully
  * Ribbon: "Test-first reduces rework 68%" → Proven pattern
- Promotion arrows pointing up to a pillar (TIER 0)
- Label: "Successful Experiments - Promoted to Instincts"

SECTION 4: DEFERRED DECISIONS (Filing Cabinet)
- File folders labeled:
  * "Database choice" → Revisit when: High-volume scenario
  * "Caching strategy" → Revisit when: Performance issues
  * "Authentication method" → Revisit when: Security requirements clear
- Trigger conditions for each folder
- Label: "Pending Decisions - Clear Revisit Triggers"

CHARACTER:
- The Dreamer (enthusiastic figure in a lab coat and creative beret)
- Gesturing between different sections
- Thought bubbles with lightbulbs

WORKFLOW ARROWS:
- User captures idea → IDEAS BACKLOG
- Idea promoted → EXPERIMENTS IN PROGRESS
- Successful experiment → FORGOTTEN INSIGHTS → TIER 0
- Failed experiment → Lesson captured → TIER 2 (error patterns)
- Unclear requirement → DEFERRED DECISIONS

VISUAL STYLE:
- Creative, colorful workspace
- Vibrant purple and rainbow accents
- Mix of organized chaos and structured sections
- Floating idea clouds in background
- Sketch-like, brainstorming aesthetic
```

---

## Prompt 5: Four-Layer Enforcement System

```
Create a security diagram showing the 4-layer protection system that guards brain integrity:

CONCENTRIC CIRCLES (fortress-style):

LAYER 1 (Outermost) - EVENT TAGGER
- Shield icon with tag symbol
- Function: "Classify every memory"
- Tags shown: "NOOR-CANVAS", "KDS", "Cross-Project"
- Color: Light blue protective barrier
- Label: "First Line - Categorization"

LAYER 2 - SOURCE CLASSIFIER
- Shield icon with sorting symbol
- Function: "Route to correct tier"
- Arrows pointing to different tiers:
  * Application patterns → TIER 2
  * KDS intelligence → TIER 0
  * Cross-project ideas → TIER 4
- Color: Green protective barrier
- Label: "Second Line - Tier Routing"

LAYER 3 - EXTRACTION SCRIPT
- Shield icon with migration arrow
- Function: "Rescue misplaced knowledge"
- Detection: "KDS wisdom in TIER 2? → Migrate to TIER 0"
- Patrol frequency: "Continuous monitoring"
- Color: Yellow protective barrier
- Label: "Third Line - Integrity Patrol"

LAYER 4 (Innermost) - AMNESIA SAFEGUARD
- Shield icon with checklist
- Function: "Pre-reset validation"
- Validation steps:
  ✓ Core Instincts preserved
  ✓ Cross-project ideas tagged
  ✓ Application data marked for deletion
  ✓ Tier separation verified
- Color: Red protective barrier
- Label: "Final Line - Pre-Reset Validation"

CENTER (Protected Core):
- TIER 0 (Core Instincts) fortress
- Eternal flame
- Label: "Protected Knowledge"

THREATS BLOCKED:
- Outside the layers, show blocked threats:
  * "Application path in TIER 0" → Blocked by Layer 3
  * "Conversation data in TIER 2" → Blocked by Layer 2
  * "Generic pattern in TIER 3" → Migrated by Layer 3

VISUAL STYLE:
- Concentric shield diagram
- Fortress/castle defense aesthetic
- Clear layer separation
- Color-coded protection levels
- Arrows showing threat detection and blocking
```

---

## Prompt 6: One Door Interface (Universal Entry Point)

```
Create an interface diagram showing the One Door routing system:

CENTER - THE ONE DOOR:
- Large, ornate door (single entrance)
- Friendly gatekeeper character
- Sign above: "Speak in plain words. I'll take it from there."
- Welcome mat with footprints

USER INPUT EXAMPLES (Floating speech bubbles):
- "I want to add a FAB button" → Detected: PLAN intent
- "Continue" → Detected: EXECUTE intent
- "Make it purple" → Detected: EXECUTE intent (with context resolution)
- "Wrong file!" → Detected: CORRECT intent
- "Create tests" → Detected: TEST intent
- "How do I...?" → Detected: ASK intent

INTENT DETECTION ENGINE (Behind the door):
- Gear/brain hybrid icon
- Processes:
  1. Natural language analysis
  2. Keyword matching
  3. Context resolution (query TIER 1)
  4. Confidence scoring (0.0 - 1.0)
  5. Agent routing

ROUTING PATHWAYS (From door outward):
Split into three paths:

LEFT PATH (Analytical) - 70% of traffic:
- Routes to: Builder, Tester, Fixer, Inspector, Archivist
- Label: "Implementation & Validation"
- Color: Blue pathway

RIGHT PATH (Creative) - 20% of traffic:
- Routes to: Dispatcher, Planner, Analyst, Governor, Brain Protector
- Label: "Planning & Protection"
- Color: Purple pathway

CENTER PATH (Meta) - 10% of traffic:
- Routes to: Knowledge Retriever, Metrics Reporter, Session Resumer
- Label: "Knowledge & Meta Operations"
- Color: Green pathway

CONTEXT ENRICHMENT (Sidebar):
Before routing, door queries:
- TIER 1: Recent conversations
- TIER 2: Learned patterns
- TIER 3: Project metrics
- TIER 4: Captured ideas
- All within <1 second

VISUAL STYLE:
- Grand entrance focal point
- Pathways radiating outward
- Speech bubbles with intents
- Percentage labels on pathways
- Professional, welcoming aesthetic
```

---

## Prompt 7: Tier Health Dashboard Visualization

```
Create a dashboard interface showing real-time brain health monitoring:

DASHBOARD LAYOUT (Grid style):

TOP ROW - OVERALL HEALTH:
- Large score: "92% (A)" with green checkmark
- Trend arrow: ↑ +5% from last month
- Color: Green gradient background
- Label: "Overall Brain Health"

TIER STATUS CARDS (5 cards in a row):

Card 1: TIER 0 (Instincts)
- Icon: Pillar with flame
- Score: 98%
- Status: Green ✓
- Metric: "10/10 rules enforced"
- Last check: "2 min ago"

Card 2: TIER 1 (Memory)
- Icon: Scrolls
- Score: 94%
- Status: Green ✓
- Metric: "8/20 conversations"
- Progress bar: [████████░░░░░░░░░░░░] 40%
- Last check: "30 sec ago"

Card 3: TIER 2 (Recollection)
- Icon: Library web
- Score: 89%
- Status: Green ✓
- Metric: "3,847 patterns"
- Confidence avg: 0.92
- Last check: "5 min ago"

Card 4: TIER 3 (Awareness)
- Icon: Observatory
- Score: 87%
- Status: Yellow ⚠
- Metric: "1,547 commits analyzed"
- Warning: "Last updated 18 hours ago"
- Last check: "1 hour ago"

Card 5: TIER 4 (Imagination)
- Icon: Lightbulb cloud
- Score: 91%
- Status: Green ✓
- Metric: "34 active ideas"
- Experiments: 3 in progress
- Last check: "10 min ago"

MIDDLE ROW - PERFORMANCE METRICS:

Chart 1: Response Times (Line graph)
- X-axis: Last 24 hours
- Y-axis: Milliseconds
- Lines:
  * Intent routing: 180ms avg (green line)
  * TIER queries: 287ms avg (blue line)
  * Whole-brain: 843ms avg (purple line)
- Target threshold line at 1000ms
- All lines below threshold

Chart 2: Learning Trends (Bar graph)
- X-axis: Last 6 months
- Y-axis: Pattern confidence avg
- Bars showing steady increase: 0.78 → 0.82 → 0.85 → 0.88 → 0.91 → 0.92
- Trend: ↑ +14% over period

Chart 3: Storage Efficiency (Pie chart)
- Total: 412KB
- Segments:
  * TIER 1: 47KB (11%)
  * TIER 2: 203KB (49%)
  * TIER 3: 98KB (24%)
  * Events: 64KB (16%)
- Green indicator: "Below 500KB target"

BOTTOM ROW - ALERTS & RECOMMENDATIONS:

Alert Panel:
⚠️ Yellow Warning: "TIER 3 data stale (>24 hours)"
   Action: "Run development context collection"
   
✅ Success: "Intent routing accuracy improved +3%"
   Continue: "Current trajectory excellent"

📊 Recommendation: "Collect 20+ more feature samples"
   Why: "Improve estimation accuracy (currently 8% MoM)"

REFRESH BUTTON:
- Bottom right corner
- Last updated: "2025-11-04 14:32:15"
- Auto-refresh: Every 5 minutes

VISUAL STYLE:
- Modern dashboard interface
- Clean, professional design
- Color-coded status indicators
- Real-time data visualization
- Responsive grid layout
```

---

## Prompt 8: Whole-Brain Integration Workflow

```
Create a workflow diagram showing a complete request flowing through all brain tiers:

USER REQUEST (Top):
- Person icon with speech bubble: "I want to add dark mode toggle"
- Timestamp: "2025-11-04 10:00:00"

WORKFLOW STAGES (Vertical flow with time annotations):

STAGE 1: ONE DOOR (t+0ms)
- Gatekeeper receives request
- Action: "Natural language analysis"
- Output: "PLAN intent detected (confidence: 0.93)"
- Time: <200ms

STAGE 2: TIER 0 (Core Instincts) (t+200ms)
- Keeper validates request
- Check: "Aligns with UI enhancement principles"
- Check: "No instinct violations"
- Output: "Approved - proceed to enrichment"
- Time: <50ms

STAGE 3: CONTEXT ENRICHMENT (t+250ms)
Parallel queries to all tiers:

TIER 1 (Active Memory):
- Query: "Recent UI discussions"
- Finds: "Color scheme conversation 3 days ago"
- Output: "User prefers purple theme"

TIER 2 (Recollection):
- Query: "Similar patterns"
- Finds: "ui_theme_toggle workflow (confidence: 0.87)"
- Output: "Workflow template with 91% success rate"

TIER 3 (Awareness):
- Query: "Project health"
- Finds: "Settings component stable (12% churn)"
- Finds: "Similar features took avg 4.5 hours"
- Output: "No hotspot warnings, reliable estimate"

TIER 4 (Imagination):
- Query: "Related ideas"
- Finds: "Dark mode in backlog (priority: medium, 2 weeks old)"
- Output: "Promote idea to active planning"

Total time: <500ms (parallel execution)

STAGE 4: RIGHT BRAIN PLANNING (t+750ms)
- Work Planner synthesizes all inputs
- Creates comprehensive plan:
  * Phase 0: Architectural discovery (1 hour)
  * Phase 1: Test infrastructure (2 hours)
  * Phase 2: Implementation (3 hours)
  * Phase 3: Validation (1 hour)
- Uses workflow template from TIER 2
- Incorporates purple theme preference from TIER 1
- Flags no hotspots from TIER 3
- Promotes idea from TIER 4
- Total plan time: ~7 hours
- Time: <3 minutes

STAGE 5: CORPUS CALLOSUM (t+4 minutes)
- Plan delivered to LEFT BRAIN
- Coordination message logged
- Execution queue prepared
- Time: <50ms

STAGE 6: LEFT BRAIN EXECUTION (t+4 minutes onward)
- Builder, Tester, Inspector work in sequence
- RED → GREEN → REFACTOR cycle
- Results logged to events.jsonl
- Time: 7 hours (actual implementation)

STAGE 7: LEARNING FEEDBACK (t+11 hours)
- Outcomes logged to TIER 4 (events)
- Brain updater processes results
- Updates:
  * TIER 1: Conversation completed successfully
  * TIER 2: ui_theme_toggle confidence: 0.87 → 0.89
  * TIER 3: Velocity updated with 7-hour data point
  * TIER 4: Experiment "dark mode" marked successful
- Time: <30 seconds

ANNOTATIONS (Side):
- "All relevant tiers consulted before planning"
- "Context enrichment happens in parallel"
- "Plan incorporates insights from 4 tiers"
- "Learning feedback closes the loop"
- "Whole-brain processing: <5 minutes (excluding execution)"

VISUAL STYLE:
- Top-to-bottom flowchart
- Time annotations on left
- Tier icons at each stage
- Parallel query branches (TIER 1-4)
- Color-coded stages
- Clear time progression
```

---

## 🎨 Bonus Prompts

### Bonus 1: FIFO Queue Animation

```
Create an animated storyboard (3 frames) showing Tier 1 FIFO queue in action:

FRAME 1: "Before (20 conversations full)"
- 20 glowing scrolls in queue
- Oldest: "conv-001" (leftmost, faded)
- Newest: "conv-020" (rightmost, bright)
- Label: "Queue at capacity"

FRAME 2: "New conversation arrives"
- New scroll approaching from right: "conv-021" (glowing)
- Arrow pointing to queue entrance
- "conv-001" highlighted in red (about to be deleted)
- Label: "FIFO triggers deletion"

FRAME 3: "After (20 conversations, oldest gone)"
- "conv-001" has vanished
- "conv-002" now leftmost (faded)
- "conv-021" now in queue (bright)
- Extraction icon above "conv-001" position: "Patterns extracted before deletion"
- Label: "Continuity maintained, capacity preserved"

VISUAL STYLE:
- Sequential storyboard panels
- Scrolls with glow effects
- Motion arrows
- Red/green highlighting
- Before/after comparison
```

---

### Bonus 2: Amnesia Transformation

```
Create a before/after comparison showing brain state during project switch:

LEFT SIDE: "Before Amnesia (NOOR-CANVAS Project)"
TIER 0: Pillar with 8 inscriptions
TIER 1: 20 scrolls (conversations about Blazor components)
TIER 2: Web with 500 patterns (SignalR, Entity Framework, Blazor)
TIER 3: Charts showing 1,249 commits, file hotspots
TIER 4: 12 ideas (some NOOR-specific, some cross-project)

CENTER: Lightning bolt with "AMNESIA" text

RIGHT SIDE: "After Amnesia (Healthcare Project)"
TIER 0: Same pillar, now with 10 inscriptions (2 promoted during NOOR)
TIER 1: Empty (0 scrolls)
TIER 2: Web with 50 generic patterns (UI patterns, testing, TDD workflows)
TIER 3: Blank slate (ready for new commits)
TIER 4: 3 preserved cross-project ideas

FLOW ARROWS (Showing what happened):
- TIER 0: Green arrow "Preserved + Enhanced"
- TIER 1: Red X "Deleted"
- TIER 2: Yellow arrow "Extracted generic patterns" (500 → 50)
- TIER 3: Red X "Reset"
- TIER 4: Orange arrow "Selectively preserved" (12 → 3)

BACKUP INDICATOR:
- Cloud icon: "Backup created pre-amnesia"
- Rollback possible

VISUAL STYLE:
- Split-screen comparison
- Before (left) vs After (right)
- Transformation arrows
- Color-coded preservation/deletion
- Clean, explanatory diagram
```

---

## 📁 Organizing Generated Images

After generating all images:

```
KDS/docs/Mind-Palace/2025-11-04-Mind-Palace-v6/generated-images/
├── 01-complete-mind-palace.png
├── 02-hemispheres.png
├── 03-memory-flow.png
├── 04-imagination-tier.png
├── 05-enforcement-system.png
├── 06-one-door-interface.png
├── 07-tier-health-dashboard.png
├── 08-integration-workflow.png
├── bonus-fifo-queue-animation.png
└── bonus-amnesia-transformation.png
```

---

## 🔗 Using Images in Documentation

Once generated, embed images in markdown documents:

```markdown
![The Complete Mind Palace](generated-images/01-complete-mind-palace.png)
*The 5-tier KDS Mind Palace with One Door entrance*

![Left Brain vs Right Brain](generated-images/02-hemispheres.png)
*Tactical execution (LEFT) and strategic planning (RIGHT) hemispheres*
```

---

## ✅ Quality Checklist

For each generated image, verify:

- [ ] All tiers/layers clearly labeled
- [ ] Color scheme matches prompt
- [ ] Text is readable
- [ ] Icons/characters visible
- [ ] Workflow arrows clear
- [ ] Annotations present
- [ ] Professional appearance
- [ ] Matches architectural truth

If image quality is poor:
1. Regenerate with more specific prompt
2. Add "high quality, professional, clean lines" to prompt
3. Request "4K resolution, vector style" for clarity

---

## 🎓 Customization Tips

### For Different Styles

**Technical Documentation:**
```
Add to any prompt: "...in the style of a technical architecture diagram, clean lines, professional, monochromatic with accent colors"
```

**Educational Materials:**
```
Add to any prompt: "...in the style of an educational infographic, friendly, approachable, vibrant colors, clear labels"
```

**Presentations:**
```
Add to any prompt: "...in the style of a presentation slide, high contrast, large text, minimalist, dark background"
```

---

## 📊 Image Usage Scenarios

### For Team Onboarding
Use images 1, 6, and 3 to explain:
1. Overall architecture (Image 1)
2. How to interact (Image 6 - One Door)
3. How memory works (Image 3)

### For Technical Deep Dives
Use images 2, 5, and 8 to explain:
1. Agent organization (Image 2 - Hemispheres)
2. Protection system (Image 5)
3. Request processing (Image 8 - Integration)

### For Stakeholder Presentations
Use images 1, 7, and bonus 2 to explain:
1. High-level architecture (Image 1)
2. Health monitoring (Image 7 - Dashboard)
3. Project switching capability (Bonus 2 - Amnesia)

---

**Visual Blueprint Prompts: Bringing the Mind Palace to life, one image at a time.** 🎨🧠✨

**Status:** ✅ Complete (10 prompts ready)  
**Next:** Generate images using Gemini  
**Version:** 1.0 (November 2025)  
**Part of:** The KDS Mind Palace Collection
