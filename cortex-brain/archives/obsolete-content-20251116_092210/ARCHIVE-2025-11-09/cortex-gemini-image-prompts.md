# CORTEX Technical System Diagrams

**Purpose:** Technical schematic diagrams, flowcharts, and architecture visualizations for CORTEX brain system

**Target:** Google Gemini Image Generation API / Technical Documentation

**Format:** Pure technical diagrams organized by system capability chapters - no cartoons, only professional schematics

**Style Guide:**
- Clean, professional technical diagrams
- Engineering blueprint aesthetic
- Clear labels and annotations
- Consistent color coding across diagrams
- Suitable for technical documentation and architecture reviews

---

## Chapter 1: Memory Architecture & Storage Tiers

### Diagram 1.1: Five-Tier Memory Architecture (Complete System)

**Prompt 1.4: Three-Tier Memory Architecture Diagram**
```
Create a clean, professional technical architecture diagram showing the CORTEX three-tier memory system. Use a layered pyramid structure with four levels:

TIER 0 (base - gray): Labeled "INSTINCT - Permanent Rules" with icons for TDD, DoD, DoR
TIER 1 (bottom - blue): Labeled "SHORT-TERM MEMORY - Last 20 Conversations" with FIFO queue visualization (numbered boxes 1-20)
TIER 2 (middle - green): Labeled "LONG-TERM MEMORY - Knowledge Graph" with network nodes connected by lines
TIER 3 (top - purple): Labeled "DEVELOPMENT CONTEXT - Project Intelligence" with charts/graphs icon

Add arrows showing data flow: Events → Tier 1 (recent) → Tier 2 (patterns) → Tier 3 (insights). Include small icons representing different data types. Use modern flat design, tech blue color scheme, clear typography, white background with subtle grid pattern.
```

**Prompt 1.5: FIFO Queue Visualization**
```
Create a technical infographic showing the FIFO (First-In-First-Out) conversation queue mechanism. Show a horizontal timeline with 20 numbered slots. Slots 1-19 are filled (gradient blue to green showing age). Slot 20 is empty (dashed outline). An arrow shows "New Conversation" entering at slot 20, pushing "Oldest Conversation" (slot 1) out the left side. The ejected conversation has an arrow pointing to a "Knowledge Graph" icon below, labeled "Patterns Extracted Before Deletion". Add labels: "Capacity: 20 conversations", "Current: 19/20", "Oldest: 47 days ago". Use clean infographic style, bright colors, clear arrows, minimal text.
```

**Prompt 1.6: Memory Resolution Flow**
```
Create a flowchart diagram showing how CORTEX resolves ambiguous references. Start with user input "Make it purple" (red box). Arrow flows to "Query Tier 1" (blue box). Branch to "Search last 20 conversations" with magnifying glass icon. Show result "Found: purple_button in Conversation #18" (green box). Arrow to "Context Resolved" with checkmark. Add a parallel failed path showing "Not Found" (orange box) leading to "Ask User for Clarification" (yellow box). Use standard flowchart shapes, tech color palette, clear connector lines, white background.
```

---

## Chapter 2: The Two Hemispheres

### Story Illustrations

**Prompt 2.1: The Monolithic Disaster**
```
Create a humorous illustration showing Asifinstein staring in horror at his monitor. The screen displays a gigantic code file labeled "TranscriptCanvasPdfExport.razor - 847 LINES" with code scrolling endlessly. The code is a jumbled mess with comments like "// TODO: Separate this", "// This should be a service", "// API logic here??". Asifinstein's hair is standing up in shock. His AI assistant looks proud of itself with a thumbs-up gesture, completely unaware of the problem. Background shows a "Separation of Concerns" poster ironically hanging on the wall. Art style: Comic/manga reaction shot style, exaggerated facial expressions, dramatic lighting, humor emphasis.
```

**Prompt 2.2: The Napkin Sketch - Two Hemispheres**
```
Create a warm, intimate illustration showing Asifinstein at a café during lunch, sketching on a napkin. The napkin shows a simple brain diagram split into two hemispheres labeled "LEFT: Execute" and "RIGHT: Plan" with a bridge labeled "Corpus Callosum" connecting them. Around the sketch, show handwritten notes: "Think first, then act", "Strategy + Tactics", "No more monoliths!". A coffee cup sits nearby. Soft afternoon sunlight streams through a window. His expression is thoughtful and inspired. Art style: Realistic sketch aesthetic, warm colors, café atmosphere, natural lighting, inspirational moment.
```

**Prompt 2.3: The Coordinated Dance**
```
Create an abstract artistic representation of two brain hemispheres working together. LEFT hemisphere (geometric, mechanical, precise - shown in cool blues) has gears, circuit patterns, and code symbols. RIGHT hemisphere (organic, flowing, creative - shown in warm oranges) has neural networks, lightbulbs, and strategic planning symbols. Between them, a glowing bridge (Corpus Callosum) pulses with data packets flowing back and forth. Messages visible: "Strategic Plan" → flowing right to left, "Execution Complete" → flowing left to right. Background shows a unified project emerging below from their cooperation. Art style: Modern digital art, split-screen contrast, dynamic composition, flowing data visualization.
```

### Technical Diagrams

**Prompt 2.4: Hemisphere Architecture Diagram**
```
Create a professional system architecture diagram showing LEFT and RIGHT brain hemispheres. 

LEFT side (blue section):
- Title: "LEFT BRAIN - Tactical Executor"
- Boxes: "code-executor.md", "test-generator.md", "error-corrector.md", "health-validator.md", "commit-handler.md"
- Labels: "RED → GREEN → REFACTOR", "Sequential", "Detail-Oriented"

RIGHT side (orange section):
- Title: "RIGHT BRAIN - Strategic Planner"
- Boxes: "intent-router.md", "work-planner.md", "screenshot-analyzer.md", "change-governor.md", "brain-protector.md"
- Labels: "Architecture", "Patterns", "Holistic Thinking"

CENTER:
- Bridge labeled "CORPUS CALLOSUM"
- Bidirectional arrows showing message flow
- Queue icon: "coordination-queue.jsonl"

Use modern flat design, clear separation, professional color scheme, clean typography.
```

**Prompt 2.5: Strategic to Tactical Flow**
```
Create a sequence diagram showing the flow from strategic planning to tactical execution. 

Timeline (left to right):
1. User Request (speech bubble icon)
2. RIGHT BRAIN Analysis (brain icon with magnifying glass)
   - "Query Tier 2: Patterns"
   - "Query Tier 3: Context"
   - "Create Strategic Plan"
3. Corpus Callosum (bridge icon with bidirectional arrows)
4. LEFT BRAIN Execution (brain icon with gears)
   - "Phase 1: RED (tests)"
   - "Phase 2: GREEN (code)"
   - "Phase 3: REFACTOR (validate)"
5. Feedback Loop (circular arrow back to RIGHT BRAIN)
   - "Update Knowledge Graph"

Use clean UML-style sequence diagram, clear time progression, distinct colors for each hemisphere.
```

**Prompt 2.6: Before/After Comparison**
```
Create a split-screen comparison infographic:

LEFT side: "BEFORE (Single Hemisphere)"
- Show a confused brain icon with swirls
- Code blob labeled "Monolithic File"
- Red X marks: "❌ No planning", "❌ Refactoring needed", "❌ Architecture mismatch"
- Sad developer emoji

RIGHT side: "AFTER (Two Hemispheres)"
- Show two connected brain hemispheres (organized)
- Properly separated components: "Service", "API", "Component"
- Green checkmarks: "✅ Planned first", "✅ Architecture-aligned", "✅ Zero refactoring"
- Happy developer emoji

Use clean infographic style, clear visual contrast, icons and emojis, bright colors.
```

---

## Chapter 3: The Self-Learning System

### Story Illustrations

**Prompt 3.1: The Repetition Nightmare**
```
Create a comic-style illustration showing Asifinstein at his desk repeating the same explanation for the 47th time. Show him with a tally board behind him counting "Element IDs prevent fragility: IIII IIII IIII IIII IIII IIII IIII IIII IIII II" (47 marks). His expression is exhausted and zombie-like. The AI assistant looks cheerful and attentive (not remembering it was told before). Thought bubble from Asifinstein: "I feel like a broken record..." Calendar on wall shows "Week 2" circled in red. Coffee cups stacked like a tower. Art style: Office humor comic, exaggerated fatigue, comedic timing, relatable developer frustration.
```

**Prompt 3.2: The Learning Breakthrough**
```
Create an inspirational illustration showing Asifinstein coding late at night (weekend scene). His screen shows code for "brain-updater.md" and "events.jsonl" with glowing lines connecting them. A holographic visualization above his desk shows patterns forming: "button_with_id" → "export_workflow" → "file_relationships" connecting like constellation lines. His face shows excitement and determination. The AI assistant hologram in the corner has a glowing brain that's literally growing/expanding with neural connections forming. Art style: Cinematic night scene, glowing UI elements, inspirational tech moment, warm desk lamp lighting contrasted with cool screen glow.
```

**Prompt 3.3: The Proof - Week 3 Success**
```
Create a celebratory illustration showing Asifinstein leaning back in his chair with hands behind head, looking satisfied. His monitor displays a dashboard with impressive stats: "Routing Accuracy: 97% ↑", "Patterns Learned: 6,847", "Explanations Needed: 0 ✓". The AI assistant is giving a confident thumbs up, with its brain visualization now fully illuminated and organized. A checklist on the wall shows crossed-off items: "✓ Element IDs explained: 0 times", "✓ Wrong files: 0", "✓ Forgotten conventions: 0". Morning sunlight streams through window. Art style: Success moment, bright and optimistic, achievement unlocked aesthetic, game UI elements.
```

### Technical Diagrams

**Prompt 3.4: Auto-Learning Pipeline Diagram**
```
Create a technical flow diagram showing the automatic learning pipeline:

Step 1 (top): "Agent Actions" (multiple agent icons: executor, tester, planner)
↓ (arrows with "log event" labels)
Step 2: "events.jsonl" (document icon with flowing lines)
↓ (conditional check diamond)
Step 3: "Threshold Check" (diamond shape)
- "50+ events?" OR "24+ hours?"
↓ (YES path - green arrow)
Step 4: "brain-updater.md" (brain with gear icon)
- "Extract Patterns"
- "Calculate Confidence"
- "Update Graph"
↓ (arrow)
Step 5: "knowledge-graph.yaml" (network diagram icon)
- "Patterns +20"
- "Confidence Updated"
↓ (circular arrow back to Step 1)
Step 6: "Next Request Benefits" (cycle continues)

Use flowchart style, clear decision points, modern tech colors, clean arrows.
```

**Prompt 3.5: Confidence Score Growth Chart**
```
Create a line chart infographic showing pattern confidence growing over time:

Title: "Pattern Learning: button_with_id_test_first"

X-axis: Timeline (Day 1, Day 7, Day 21)
Y-axis: Confidence Score (0.0 to 1.0)

Line graph showing growth:
- Day 1: 0.50 (Low) - red zone - "First Example"
- Day 7: 0.78 (Moderate) - yellow zone - "5 Examples"
- Day 21: 0.92 (High) - green zone - "12 Examples"

Add data points with annotations:
- "Evidence Count: 1 → 5 → 12"
- "Success Rate: 100% → 100% → 96%"
- "Average Time: 20min → 18min → 17.5min"

Use professional chart style, clear legend, gradient zones, data point markers.
```

**Prompt 3.6: Learning Categories Matrix**
```
Create an infographic matrix showing 5 learning categories:

Grid layout (2x3):

1. Intent Patterns (purple icon - brain with speech bubble)
   - "add a button" → PLAN
   - Confidence: 0.95

2. File Relationships (blue icon - linked files)
   - HostControlPanel + noor-canvas.css
   - Co-mod: 78%

3. Workflow Patterns (green icon - process flow)
   - button_addition_test_first
   - Success: 96%

4. Validation Insights (orange icon - shield with checkmark)
   - "Element IDs prevent fragility"
   - Evidence: 13

5. Correction History (red icon - warning triangle)
   - Wrong file mistakes: 3
   - Pattern learned

Use card-based layout, distinct colors per category, icons, minimal text, modern UI design.
```

---

## Chapter 4: The Guardian That Says "No"

### Story Illustrations

**Prompt 4.1: The Dangerous Request**
```
Create a dramatic illustration showing Asifinstein typing quickly with stressed expression (bags under eyes, messy hair, multiple empty coffee cups). The screen shows him typing "Skip tests, we need this FAST" with his finger hovering over Enter key. Behind him, a translucent holographic guardian figure (representing Brain Protector - shield icon combined with brain) materializes with a raised hand in "STOP" gesture. Red warning symbols glow around the guardian. Clock on wall shows late hour (2:47 AM). Art style: Dramatic moment, cinematic lighting, red warning lights, tension before the challenge, guardian angel aesthetic but tech-themed.
```

**Prompt 4.2: The Challenge Screen**
```
Create a detailed illustration of Asifinstein's monitor displaying the Brain Protection Challenge interface. The screen shows:

Large header: "🧠 BRAIN PROTECTION CHALLENGE"
Warning section with ⚠️ icons and red highlights
Data visualization: Bar chart comparing "Test-first: 94%" vs "Test-skip: 67%" success rates
Historical evidence: "Last 'quick fix' took 24 hours to debug" with timeline
Three numbered options at bottom with buttons
Asifinstein's reflection visible in the screen, hand on chin, thoughtful expression

The UI has a modern, semi-transparent overlay design with glowing edges. Art style: High-tech UI design, heads-up display aesthetic, holographic interface elements, detailed screen content legible but stylized.
```

**Prompt 4.3: The Data Wins**
```
Create an illustration showing Asifinstein having a realization moment. Split-screen memory flashback effect: left side shows him frustrated during a previous 24-hour debugging nightmare (dark, stressful), right side shows present moment where he sees the data on screen proving Brain Protector is right (lightbulb moment). His expression changes from resistant to accepting. Hand moving away from "OVERRIDE" button toward "Accept Alternative 1" button. The AI guardian figure nods approvingly in the background. Art style: Emotional moment, flashback effect with color/saturation contrast, character growth moment, learning from past mistakes theme.
```

### Technical Diagrams

**Prompt 4.4: Protection Layers Diagram**
```
Create a security layer diagram showing six concentric circles/shields protecting a core:

CENTER (core): CORTEX Brain (brain icon)

Layer 6 (outer - light gray): "Commit Integrity"
Layer 5: "Knowledge Quality" (yellow)
Layer 4: "Hemisphere Specialization" (purple)
Layer 3: "SOLID Compliance" (blue)
Layer 2: "Tier Boundary Protection" (green)
Layer 1 (inner - red): "Instinct Immutability"

Each layer has small icons representing its function and 1-2 word labels. Arrows show threats being blocked at different layers. Use shield/fortress metaphor, cybersecurity aesthetic, layered defense visualization, modern flat design.
```

**Prompt 4.5: Challenge Protocol Flowchart**
```
Create a decision tree flowchart for the Brain Protector challenge protocol:

Start: "User Request" (blue circle)
↓
"Detect Risks?" (diamond)
→ NO: "Allow" (green box) → End
→ YES: Continue ↓
"Query Tier 2 Historical Data" (cylinder icon)
↓
"Query Tier 3 Impact Metrics" (chart icon)
↓
"Calculate Severity" (formula icon)
↓
"Severity Level?" (diamond with 3 paths)
→ HIGH (≥0.70): "Issue Challenge + Alternatives" (red box)
→ MEDIUM (0.40-0.70): "Warn + Require Confirmation" (yellow box)
→ LOW (<0.40): "Allow + Log Warning" (green box)

Use standard flowchart symbols, color-coded severity levels, clear decision points.
```

**Prompt 4.6: Challenge Impact Statistics**
```
Create an infographic showing Brain Protector effectiveness:

Title: "Rule #22 Brain Protector - 90 Days Impact"

Stat boxes (large numbers with icons):
- 47 Challenges Issued (shield icon)
- 43 Challenges Accepted (checkmark - 91%)
- 4 Override Attempts (warning - 9%)
- 2 Override Failures (X mark - 50% validated protector)
- 108 Hours Saved (clock icon)
- 95% User Trust (heart icon - "CORTEX was right")

Bar chart comparing:
"With Protection" vs "Without Protection"
- Rework Time: 2.3 hours vs 8.7 hours
- Success Rate: 94% vs 67%
- Technical Debt: Low vs High

Use dashboard style, big numbers, clear visual hierarchy, green/red color coding for good/bad.
```

---

## Chapter 5: The Complete Awakening

### Story Illustrations

**Prompt 5.1: The Effortless Flow**
```
Create a serene, flowing illustration showing Asifinstein working in perfect harmony with CORTEX. Split the image diagonally - top half shows Asifinstein typing one simple request "Add email notifications when user joins session" with a calm, confident expression (morning light, organized desk, single coffee cup). Bottom half shows a beautiful visualization of CORTEX working: RIGHT BRAIN analyzing (glowing neural network), Corpus Callosum transferring (data stream), LEFT BRAIN executing (gears turning smoothly), all happening in 3.2 seconds. Time display: "3.2s analysis → 3h 47m execution". Art style: Zen-like productivity, smooth workflow visualization, harmonious composition, satisfying efficiency aesthetic, morning productivity vibes.
```

**Prompt 5.2: The Behavioral Guardian**
```
Create a touching illustration showing CORTEX caring about Asifinstein's well-being. Show Asifinstein looking tired (10:45 AM, disheveled, typing frantically). The screen displays CORTEX's behavioral analysis with caring tone: graphs showing "Productivity: 67% (low)", "Sleep pattern: Disrupted", "Late commits: 3 nights", and a gentle message "Take a 30-minute break. History shows rushed work when tired leads to problems." The AI assistant hologram has a concerned, caring expression (like a friend worried about you). Asifinstein's expression softens as he reads it. Art style: Emotional, human-AI relationship, caring technology theme, warm colors despite fatigue, friendship in the digital age.
```

**Prompt 5.3: The Complete Partnership**
```
Create an inspirational hero-shot illustration showing the complete evolved CORTEX system. Center: Asifinstein standing confidently with arms crossed, smiling. Behind him, a massive holographic visualization of the complete CORTEX brain - all tiers glowing and connected, hemispheres working in harmony, data flowing smoothly. Statistics floating around: "6,847 patterns learned", "97% accuracy", "52% faster", "108 hours saved". The AI assistant stands beside him (no longer an intern, now an equal partner) with a wise, capable expression. Dawn light breaking through window symbolizing new beginning. Art style: Heroic tech achievement, inspirational startup success, partnership triumph, bright optimistic future, motivational poster aesthetic.
```

### Technical Diagrams

**Prompt 5.4: Complete System Architecture**
```
Create a comprehensive architecture diagram showing all CORTEX components:

TOP LAYER: "User Interface"
- Single entry point: cortex.md

SECOND LAYER: "Intent Router" (brain with routing arrows)

THIRD LAYER (split): 
LEFT side: "LEFT BRAIN Agents" (5 boxes in blue)
- code-executor, test-generator, error-corrector, health-validator, commit-handler
RIGHT side: "RIGHT BRAIN Agents" (5 boxes in orange)
- work-planner, screenshot-analyzer, change-governor, brain-protector, intent-router

CENTER: "Corpus Callosum" (bridge with bidirectional arrows)

BOTTOM LAYER: "Storage Tiers" (4 horizontal bands)
- Tier 0: Instinct (gray)
- Tier 1: Short-term Memory (blue)
- Tier 2: Long-term Memory (green)
- Tier 3: Development Context (purple)
- Tier 4: Event Stream (yellow)

All connected with clean arrows showing data flow. Use modern system architecture style, clear component boundaries, professional color scheme.
```

**Prompt 5.5: Week 1 vs Week 12 Comparison**
```
Create a before/after comparison dashboard:

LEFT side: "Week 1 - Learning Phase"
Gauges and metrics:
- Routing Accuracy: 78% (red zone)
- Patterns: 50 (small network diagram)
- Speed: 8 hours/feature (slow)
- Zero Rework: 67% (yellow)
- Manual Explanations: 47/week (high)

RIGHT side: "Week 12 - Mastery Phase"
Same gauges improved:
- Routing Accuracy: 97% (green zone)
- Patterns: 6,847 (large network)
- Speed: 3.8 hours/feature (fast)
- Zero Rework: 91% (green)
- Manual Explanations: 0/week (perfect)

Center: Large arrow showing transformation
"+52% faster, +19% accuracy, +24% quality"

Use dashboard gauge style, clear visual improvement, green↑ arrows showing growth, celebratory design.
```

**Prompt 5.6: Complete Workflow Sequence**
```
Create a detailed timeline/sequence diagram showing one complete CORTEX workflow:

Timeline (left to right with time stamps):

0.0s: User types request
0.8s: Intent Router analyzes (RIGHT BRAIN)
1.1s: Brain Query searches patterns (Tier 2)
1.5s: Context Check analyzes project (Tier 3)
1.7s: Brain Protector validates (no threats)
3.2s: Strategic Plan created (RIGHT BRAIN)
3.3s: Plan sent via Corpus Callosum
3h 47m: LEFT BRAIN executes all phases
  - Phase markers showing RED → GREEN → REFACTOR
3h 47m: Feedback to RIGHT BRAIN
3h 47m: Events logged (7 events)
3h 47m: ✓ Complete

Use Gantt-chart style timeline, color-coded phases, clear time markers, parallel process visualization where applicable.
```

---

## Additional Technical Diagrams (System-Wide)

**Prompt A1: CORTEX Logo/Brand Identity**
```
Create a modern, professional logo for CORTEX. The logo should combine:
- A stylized brain icon (split into LEFT and RIGHT hemispheres with distinct visual styles)
- Circuit/network patterns subtly integrated
- Clean, geometric design
- Text "CORTEX" in modern sans-serif font
- Tagline beneath: "Cognitive Development Partner"
- Color scheme: Tech blue primary, orange accent, white/gray neutrals
- Suitable for: Documentation headers, dashboard, branding

Style: Modern tech logo, scalable vector aesthetic, professional and trustworthy, memorable icon.
```

**Prompt A2: Tier System Infographic**
```
Create a comprehensive infographic poster explaining all CORTEX tiers:

Title: "The CORTEX Brain - Five-Tier Architecture"

Five horizontal sections (different colors):

TIER 0 (gray): 
- Icon: Shield
- "Permanent Rules - Never Modified"
- Examples: TDD, DoD, DoR icons

TIER 1 (blue):
- Icon: Clock with 20
- "Last 20 Conversations - FIFO Queue"
- Visual: 20 conversation bubbles in a queue

TIER 2 (green):
- Icon: Neural network
- "Knowledge Graph - 6,847 Patterns"
- Visual: Interconnected nodes

TIER 3 (purple):
- Icon: Dashboard/metrics
- "Development Context - 30-Day Rolling Window"
- Visual: Charts and graphs

TIER 4 (yellow):
- Icon: Stream/log file
- "Event Stream - Everything Logged"
- Visual: Flowing timeline of events

Use infographic poster style, each tier gets equal space, clear icons, educational design.
```

**Prompt A3: Success Metrics Dashboard**
```
Create a polished analytics dashboard visualization showing CORTEX success:

Title: "CORTEX Performance Dashboard - 90 Days"

Layout: 4 quadrant grid

TOP-LEFT: "Speed"
- Speedometer: 52% faster (green zone)
- Line graph trending up

TOP-RIGHT: "Quality"  
- Shield icon: 91% zero-rework rate
- Bar chart comparing before/after

BOTTOM-LEFT: "Intelligence"
- Brain icon: 97% routing accuracy
- Growth curve showing improvement

BOTTOM-RIGHT: "Learning"
- Network icon: 6,847 patterns learned
- Expanding network visualization

Center: Large number "108 hours saved"

Use professional analytics dashboard style, real-time data aesthetic, clean modern UI, blue/green color scheme.
```

**Prompt A4: Developer Journey Map**
```
Create an emotional journey map showing developer experience with CORTEX:

X-axis: Timeline (Week 1 → Week 12)
Y-axis: Satisfaction/Frustration (Frustrated bottom, Delighted top)

Curve showing:
- Week 1: Low (frustrated with amnesia)
- Week 2: Rising (memory working!)
- Week 4: Peak (learning system active)
- Week 6: Dip (challenge initial resistance)
- Week 8: Rising again (trust building)
- Week 12: Peak (complete partnership)

Key moments marked with icons:
📍 "First memory success"
📍 "Architecture-aligned code"
📍 "First challenge accepted"
📍 "Behavioral care detected"

Use journey mapping style, emotional curve visualization, milestone markers, empathy map aesthetics.
```

---

## Usage Instructions

### For Story Illustrations:
1. Use these prompts with Google Gemini Image Generation
2. Adjust art style preferences as needed
3. Maintain consistent character design for Asifinstein across all images
4. Keep AI assistant hologram consistent in appearance

### For Technical Diagrams:
1. Prioritize clarity over artistic flair
2. Ensure all text is legible
3. Use consistent color coding across related diagrams
4. Maintain professional technical documentation standards

### Recommended Image Specifications:
- Story Illustrations: 1792x1024 (landscape) or 1024x1792 (portrait)
- Technical Diagrams: 1024x1024 (square) or 1792x1024 (landscape)
- Infographics: 1024x1792 (portrait poster format)
- Logo: 1024x1024 (square, transparent background)

### Color Palette Reference:
- **Tech Blue**: #0066CC (primary)
- **Orange Accent**: #FF6B35 (secondary)
- **Success Green**: #00C853
- **Warning Yellow**: #FFD600
- **Error Red**: #D32F2F
- **Purple Insight**: #7B1FA2
- **Neutral Gray**: #546E7A
- **Background**: #FFFFFF or #F5F5F5

---

**Total Prompts:** 28 (18 story illustrations + 10 technical diagrams)

**Generated:** November 6, 2025  
**Version:** 1.0  
**For:** The Awakening of CORTEX Documentation
