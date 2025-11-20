# DALL-E Prompt: Conversation Tracking Pipeline

## Visual Composition
- **Layout:** Left-to-right horizontal pipeline flowchart
- **Orientation:** Landscape (16:9 aspect ratio)
- **Pipeline Metaphor:** Assembly line with distinct processing stages
- **Data Flow:** Single main pipeline with branching decision points

## Color Palette
- **Capture Stage (Orange):** #ff8c42 - Initial data collection
- **Parse Stage (Yellow):** #ffd93d - Data transformation
- **Store Stage (Blue):** #45b7d1 - Database persistence
- **Inject Stage (Green):** #96ceb4 - Context integration
- **Error Paths (Red):** #ff6b6b - Exception handling
- **Background:** Light Gray (#f5f7fa) with pipeline track pattern
- **Connectors:** Dark Charcoal (#2c3e50) arrows

## Components & Elements

### Input Source (Far Left)
- **Position:** 5% from left edge
- **Visual:** GitHub Copilot Chat interface mockup
- **Icon:** GitHub logo + chat bubble combination
- **Label:** "GitHub Copilot Chat Interface"
- **Size:** Medium rectangle (150px x 100px)
- **Details:** Show sample conversation text inside interface

### Stage 1: Capture (Orange)
- **Position:** 20% from left
- **Visual:** Rounded rectangle with camera icon
- **Label:** "CONVERSATION CAPTURE"
- **Sub-components:**
  - "JSON Export" small box
  - "Metadata Extract" small box
  - "Timestamp" clock icon
- **Size:** Large (200px x 150px)
- **Border:** 4px orange outline

### Checkpoint 1: Validation
- **Position:** Between Capture and Parse
- **Visual:** Diamond shape (decision point)
- **Label:** "Valid Format?"
- **Paths:**
  - **Yes:** Green arrow to Parse stage
  - **No:** Red arrow to Error Handler
- **Size:** Diamond 80px x 80px

### Stage 2: Parse (Yellow)
- **Position:** 42% from left
- **Visual:** Rounded rectangle with document split icon
- **Label:** "MARKDOWN PARSER"
- **Sub-components:**
  - "Extract Code Blocks"
  - "Parse Metadata"
  - "Identify Speakers" (User vs AI)
- **Size:** Large (200px x 150px)
- **Details:** Show markdown syntax symbols (###, ```, **)

### Checkpoint 2: Quality Check
- **Position:** Between Parse and Store
- **Visual:** Diamond shape
- **Label:** "Complete Data?"
- **Paths:**
  - **Yes:** Green arrow to Store
  - **No:** Orange arrow loops back to Parser with "Retry" label
- **Size:** Diamond 80px x 80px

### Stage 3: Store (Blue)
- **Position:** 64% from left
- **Visual:** Rounded rectangle with database cylinder icon
- **Label:** "DATABASE STORAGE"
- **Sub-components:**
  - "SQLite Write" database icon
  - "Index Creation" index card icon
  - "Relationship Mapping" network icon
- **Size:** Large (200px x 150px)
- **Details:** Show database table structure preview

### Checkpoint 3: Persistence Verification
- **Position:** After Store
- **Visual:** Diamond shape
- **Label:** "Saved Successfully?"
- **Paths:**
  - **Yes:** Green arrow to Inject
  - **No:** Red arrow to Error Handler with "Rollback" label
- **Size:** Diamond 80px x 80px

### Stage 4: Inject (Green)
- **Position:** 86% from right
- **Visual:** Rounded rectangle with syringe/injection icon
- **Label:** "CONTEXT INJECTION"
- **Sub-components:**
  - "Load Recent Context" (last 3 conversations)
  - "Pattern Detection" magnifying glass icon
  - "Merge with Working Memory"
- **Size:** Large (200px x 150px)
- **Details:** Show context buffer visualization (3-5 message icons)

### Output Destination (Far Right)
- **Position:** 95% from left
- **Visual:** Brain icon representing CORTEX Working Memory
- **Label:** "Working Memory (Tier 1)"
- **Icon:** Brain with highlighted Tier 1 section
- **Size:** Medium circle (120px diameter)
- **Connection:** Final green arrow terminating at brain

## Pipeline Infrastructure

### Main Pipeline Track
- **Visual:** Gray conveyor belt pattern running horizontally
- **Width:** 40px ribbon spanning full width
- **Details:** Subtle motion lines suggesting left-to-right flow
- **Position:** Behind all stages (z-index: -1)

### Data Packets
- **Visual:** Small envelope icons traveling along pipeline
- **Color:** Changing color to match current stage
- **Quantity:** 3-4 packets at different positions showing continuous flow
- **Animation Indicator:** Motion blur trails

### Error Handler (Bottom)
- **Position:** Bottom center (floating separate from main pipeline)
- **Visual:** Red rounded rectangle with alert icon
- **Label:** "ERROR HANDLER & RETRY LOGIC"
- **Size:** Medium (180px x 80px)
- **Connections:** Receives red arrows from checkpoints
- **Output:** Yellow "Retry" arrow looping back to appropriate stage

## Message Flow & Connections

### Primary Flow (Green Path)
- **Arrow Style:** Thick solid arrows (6px)
- **Color:** Dark gray (#2c3e50) with green (#96ceb4) glow
- **Flow:** Input → Capture → Parse → Store → Inject → Output
- **Labels:** "Raw Data", "Structured JSON", "Parsed Markdown", "DB Record", "Enriched Context"

### Error Flow (Red Path)
- **Arrow Style:** Medium dashed arrows (4px)
- **Color:** Red (#ff6b6b)
- **Triggers:** Failed validation, incomplete data, storage errors
- **Endpoints:** All redirect to Error Handler

### Retry Flow (Orange Loop)
- **Arrow Style:** Curved arrows looping back
- **Color:** Orange (#ff8c42)
- **Path:** Error Handler → Original failure point
- **Label:** "Retry (Max 3 attempts)"

## Typography & Labels

### Stage Headers
- **Font:** Bold sans-serif, 20pt
- **Color:** White text on colored stage background
- **Position:** Top of each stage box
- **Style:** ALL CAPS for emphasis

### Sub-component Labels
- **Font:** Regular sans-serif, 12pt
- **Color:** Dark gray (#2c3e50)
- **Position:** Inside stage boxes, bulleted list
- **Icon Prefix:** Small icon before each label

### Flow Labels
- **Font:** Italic sans-serif, 14pt
- **Position:** Along arrows, centered on path
- **Background:** White pill shape for contrast

### Decision Point Labels
- **Font:** Medium sans-serif, 14pt
- **Position:** Inside diamond shapes
- **Color:** Black (#000000)

## Technical Accuracy

### Capture Stage Requirements
- Must show GitHub Copilot Chat as source
- JSON format specification required
- Timestamp must be UTC format indication

### Parse Stage Requirements
- Markdown processing must be explicit
- Code block extraction highlighted
- Speaker identification (User/AI) must be shown

### Store Stage Requirements
- SQLite database specifically mentioned
- Show indexing for searchability
- Display relationship mapping to knowledge graph

### Inject Stage Requirements
- Context window size indicated (recent N conversations)
- Pattern detection capability shown
- Integration with Tier 1 Working Memory explicit

### Error Handling
- Maximum retry attempts specified (3)
- Rollback capability shown for failed storage
- Clear error routing from each checkpoint

## Style & Aesthetic
- **Design Language:** Industrial pipeline meets software flowchart
- **Detail Level:** High - show internal components of each stage
- **Visual Metaphor:** Assembly line/manufacturing process
- **Modern & Clean:** Flat design with subtle shadows (2px, 20% opacity)
- **Professional:** Enterprise process documentation quality

## Mood & Atmosphere
- **Systematic & Reliable:** Suggests robust data processing
- **Transparent & Auditable:** Clear visibility into each stage
- **Efficient:** Conveys streamlined automation
- **Resilient:** Error handling demonstrates fault tolerance

## Output Specifications
- **Resolution:** 2560x1440 (2K)
- **Format:** PNG with transparency
- **DPI:** 300 (print-ready)
- **Accessibility:** WCAG AA contrast
- **File Size:** <500KB

## Usage Context
- **Technical Documentation:** Conversation tracking system explanation
- **Developer Training:** Understanding data pipeline architecture
- **Process Documentation:** Workflow and data transformation stages
- **System Monitoring:** Identifying pipeline bottlenecks

## DALL-E Generation Instruction

**Primary Prompt:**
"Create a professional horizontal pipeline flowchart showing conversation tracking stages in CORTEX system. Left-to-right flow with four main stages: Capture (orange #ff8c42), Parse (yellow #ffd93d), Store (blue #45b7d1), Inject (green #96ceb4). Each stage as rounded rectangle (200px x 150px) with icons and sub-components. Diamond-shaped checkpoints between stages for validation. GitHub Copilot Chat interface on far left as input source. Brain icon on far right as output destination. Gray conveyor belt pattern beneath stages. Show error handler box at bottom with red dashed arrows from checkpoints. Include data packet icons traveling along pipeline. Clean modern flowchart style with professional labeling."

**Refinement Prompt:**
"Add more detail to stage internals showing specific sub-processes. Make error paths more prominent with red color. Include retry loop arrows from error handler back to stages. Add motion indicators to data packets. Enhance database cylinder icon in Store stage. Show context buffer visualization in Inject stage."