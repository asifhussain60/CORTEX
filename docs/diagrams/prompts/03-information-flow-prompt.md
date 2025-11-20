# DALL-E Prompt: Information Flow Sequence

## Visual Composition
- **Layout:** Horizontal sequence diagram with time progression left-to-right
- **Orientation:** Landscape (16:9 aspect ratio)
- **Timeline:** Horizontal arrow spanning full width showing temporal progression
- **Swimlanes:** Vertical columns for each participant (User, Entry Point, Agents, Brain Tiers)

## Color Palette
- **User Column:** Purple (#9b59b6) - External actor
- **Entry Point:** Red (#ff6b6b) - Request validation gateway
- **Agent Layer:** Multi-color gradient - Each agent type different color
- **Brain Tiers:** Blue gradient (#45b7d1 to #96ceb4) - Processing layers
- **Message Arrows:** Dark gray (#2c3e50) with colored highlights
- **Background:** Clean white (#ffffff) with subtle grid (#f0f0f0)
- **Timeline Bar:** Orange (#ff8c42) highlighting critical path

## Components & Elements

### Timeline (Top)
- **Position:** Spanning full width, 5% from top
- **Visual:** Thick orange arrow with time markers
- **Labels:** "T0", "T1", "T2", "T3", "T4" showing 5 key moments
- **Duration Indicators:** "~50ms", "~200ms", "~100ms" between stages

### Participant Swimlanes (Left to Right)

#### 1. User (Purple)
- **Position:** Leftmost column (15% width)
- **Icon:** Person silhouette at top
- **Lifeline:** Dashed vertical line down center
- **Interaction Box:** "GitHub Copilot Chat" interface mockup

#### 2. Entry Point / Tier 0 (Red)
- **Position:** Second column (20% width)
- **Icon:** Shield with gateway symbol
- **Lifeline:** Solid red line showing always-active state
- **Components:** "Validator", "Router", "Brain Protection" boxes

#### 3. Agent Layer (Multi-color)
- **Position:** Center column (30% width)
- **Icons:** Multiple agent symbols (6 small icons)
- **Lifeline:** Multiple parallel dashed lines (one per agent)
- **Agents Shown:** Executor, Planner, Tester (3 visible of 6 total)

#### 4. Brain Tiers (Blue Gradient)
- **Position:** Right side (35% width)
- **Sub-columns:** Tier 1 (Working Memory), Tier 2 (Knowledge Graph), Tier 3 (Storage)
- **Icons:** Memory chip, network nodes, database cylinder
- **Lifelines:** Three parallel solid lines

## Message Flow Sequence

### Step 1: User Request (T0)
- **Arrow:** User → Entry Point
- **Style:** Solid purple arrow, 5px width
- **Label:** "1. User Query: 'Create auth system'"
- **Position:** Near top of diagram

### Step 2: Validation (T0 + 50ms)
- **Arrow:** Entry Point internal (self-call)
- **Style:** Curved arrow pointing back to same column
- **Label:** "2. Validate & Route"
- **Visual:** Small processing box on lifeline

### Step 3: Agent Selection (T1)
- **Arrow:** Entry Point → Agent Layer
- **Style:** Solid red arrow branching to multiple agents
- **Label:** "3. Dispatch to Planner Agent"
- **Branch:** One main arrow splitting into agent-specific paths

### Step 4: Context Retrieval (T1 + 100ms)
- **Arrow:** Agent Layer → Brain Tier 1
- **Style:** Dashed arrow (async call)
- **Label:** "4. Fetch Context"
- **Sub-arrow:** Tier 1 → Tier 2 ("Query Knowledge Graph")

### Step 5: Pattern Lookup (T2)
- **Arrow:** Brain Tier 2 → Brain Tier 3
- **Style:** Thin solid arrow
- **Label:** "5. Load Historical Patterns"
- **Return:** Dashed arrow back ("Pattern Data")

### Step 6: Agent Processing (T2 + 200ms)
- **Visual:** Processing box expanding on Agent lifeline
- **Label:** "6. Generate Implementation Plan"
- **Icon:** Spinning gear animation indicator

### Step 7: Result Return (T3)
- **Arrow:** Agent Layer → Entry Point
- **Style:** Dashed return arrow, 4px width
- **Label:** "7. Structured Response"
- **Color:** Green (#96ceb4) indicating success

### Step 8: Format Output (T3 + 50ms)
- **Arrow:** Entry Point internal
- **Label:** "8. Format for User"
- **Visual:** Small transformation box

### Step 9: Deliver Response (T4)
- **Arrow:** Entry Point → User
- **Style:** Solid purple arrow, 5px width
- **Label:** "9. Formatted Implementation Plan"
- **Endpoint:** Arrow terminates at User interaction box

## Activation Boxes
- **Visual:** Thin rectangular boxes overlaid on lifelines during processing
- **Color:** Slightly darker than lifeline color with 80% opacity
- **Height:** Proportional to processing duration (longer = taller)
- **Key Activations:**
  - Entry Point: Two activations (validation, formatting)
  - Agent: One large activation (main processing)
  - Brain Tiers: Three small activations (data retrieval)

## Typography & Labels

### Participant Names
- **Position:** Top of each swimlane
- **Font:** Bold sans-serif, 18pt
- **Style:** Underlined text in participant color

### Message Labels
- **Position:** Above or below arrow (alternating for clarity)
- **Font:** Regular sans-serif, 14pt
- **Format:** Number prefix ("1.", "2.") + Action description
- **Background:** Semi-transparent white pill for readability

### Timing Annotations
- **Position:** Near timeline, aligned with message
- **Font:** Monospace italic, 11pt
- **Color:** Gray (#7f8c8d)
- **Format:** "~XXXms" or "Async"

## Technical Accuracy

### Request Flow Rules
- ALL requests MUST enter through Entry Point (no bypassing)
- Agent selection happens at Entry Point (router responsibility)
- Brain tier access is ALWAYS through Agent Layer
- Return path MUST reverse through same route

### Timing Realism
- Validation: 30-50ms (fast)
- Agent processing: 100-500ms (variable)
- Database queries: 50-200ms (depends on complexity)
- Total round-trip: 400-800ms (typical)

### Asynchronous vs Synchronous
- **Solid arrows:** Synchronous (blocking) calls
- **Dashed arrows:** Asynchronous or return messages
- Clearly distinguish between request and response

## Style & Aesthetic
- **Design Language:** UML sequence diagram with modern styling
- **Line Quality:** Crisp 2px lines, anti-aliased
- **Arrow Heads:** Filled triangles (5px)
- **Grid Background:** Subtle 20px grid in light gray
- **Professional:** Enterprise documentation quality

## Mood & Atmosphere
- **Systematic & Organized:** Clear temporal progression
- **Transparent:** Easy to follow information flow
- **Technical & Precise:** Accurate timing and sequencing
- **Educational:** Teaches system behavior through visualization

## Output Specifications
- **Resolution:** 2560x1440 (2K)
- **Format:** PNG with transparency
- **DPI:** 300 (print-ready)
- **Accessibility:** WCAG AA contrast
- **File Size:** <450KB

## Usage Context
- **Developer Onboarding:** Understanding request lifecycle
- **Architecture Reviews:** Explaining system behavior
- **Performance Analysis:** Identifying bottlenecks
- **Documentation:** Technical sequence diagrams

## DALL-E Generation Instruction

**Primary Prompt:**
"Create a professional UML sequence diagram showing information flow in CORTEX system. Four vertical swimlanes from left to right: User (purple #9b59b6), Entry Point (red #ff6b6b), Agent Layer (multi-color), Brain Tiers (blue #45b7d1). Show 9 numbered message arrows flowing between participants over time. Include timing annotations (~50ms, ~200ms). Display activation boxes showing processing duration. Horizontal timeline at top with orange (#ff8c42) progress indicator. Clean white background with subtle grid. Modern technical illustration style with clear labels."

**Refinement Prompt:**
"Add more detail to activation boxes showing processing depth. Make message arrow labels more prominent with pill-shaped backgrounds. Include small icons for each participant type at column tops. Show branching arrows when Entry Point dispatches to multiple agents. Add return message arrows in dashed style."