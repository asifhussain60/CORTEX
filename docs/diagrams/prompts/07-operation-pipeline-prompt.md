# DALL-E Prompt: Operation Execution Pipeline

## Visual Composition
- **Layout:** Left-to-right horizontal pipeline with branching stages
- **Orientation:** Landscape (16:9 aspect ratio)
- **Pipeline Depth:** 3 parallel tracks showing different operation types
- **Stage Progression:** 6 main stages with checkpoints between

## Color Palette
- **Intake Stage:** Purple (#9b59b6) - Request reception
- **Planning Stage:** Yellow (#ffd93d) - Strategy formulation
- **Validation Stage:** Orange (#ff8c42) - Safety checks
- **Execution Stage:** Green (#96ceb4) - Action implementation
- **Testing Stage:** Blue (#4d96ff) - Quality verification
- **Completion Stage:** Turquoise (#4ecdc4) - Finalization
- **Fast Track:** Gold (#ffd700) - Priority operations
- **Error Path:** Red (#ff6b6b) - Exception handling
- **Background:** Light gray (#f8f9fa) with pipeline rails

## Components & Elements

### Stage 1: Intake (Purple)
- **Position:** 5% from left
- **Visual:** Rounded rectangle with funnel icon
- **Label:** "OPERATION INTAKE"
- **Size:** 180px x 120px
- **Sub-components:**
  - "Parse Request" checkbox
  - "Identify Type" dropdown icon
  - "Priority Assessment" star rating
- **Input:** User request arrow from top-left

### Router 1: Operation Type Classifier
- **Position:** After Intake (20% from left)
- **Visual:** Circular node with 3-way split
- **Label:** "CLASSIFY"
- **Branches:**
  - **Setup Operations** (top track)
  - **Standard Operations** (middle track)  
  - **Cleanup Operations** (bottom track)
- **Size:** 100px diameter circle
- **Icon:** Traffic director symbol

### Stage 2: Planning (Yellow) - 3 Parallel Tracks
- **Position:** 35% from left
- **Visual:** Three stacked rectangles (one per track)
- **Label:** "PLANNING & STRATEGY"
- **Track Specific:**
  - **Setup Track:** "Initialize Resources" + folder icon
  - **Standard Track:** "Analyze Requirements" + chart icon
  - **Cleanup Track:** "Identify Targets" + trash icon
- **Size:** Each 160px x 80px

### Checkpoint 1: Safety Validation
- **Position:** Between Planning and Validation (45% from left)
- **Visual:** Octagon (stop sign shape) with shield
- **Label:** "SAFETY CHECK"
- **Decision:**
  - ✓ Safe → Continue green arrow
  - ✗ Unsafe → Redirect to error handler (red arrow down)
- **Size:** 90px octagon

### Stage 3: Validation (Orange)
- **Position:** 55% from left
- **Visual:** Diamond shape for decision point
- **Label:** "PRE-EXECUTION VALIDATION"
- **Checks:**
  - "Dependencies Met?" 
  - "Resources Available?"
  - "Conflicts Detected?"
- **Size:** 140px x 140px diamond
- **Paths:** Pass (green) / Fail (red loop back to Planning)

### Stage 4: Execution (Green) - Tracks Converge
- **Position:** 70% from left
- **Visual:** Large rounded rectangle with gear icon
- **Label:** "EXECUTE OPERATION"
- **Activity Indicator:** Spinning gear animation symbol
- **Sub-components:**
  - "Module Execution" gear
  - "Progress Tracking" progress bar (75% filled)
  - "Logging" file icon
- **Size:** 200px x 140px

### Stage 5: Testing (Blue)
- **Position:** 82% from left
- **Visual:** Rounded rectangle with microscope icon
- **Label:** "QUALITY VERIFICATION"
- **Tests:**
  - "Unit Tests" checkmark
  - "Integration Tests" checkmark
  - "Validation Tests" in-progress spinner
- **Size:** 160px x 120px

### Checkpoint 2: Success Validation
- **Position:** After Testing (90% from left)
- **Visual:** Diamond decision point
- **Label:** "SUCCESS?"
- **Paths:**
  - ✓ Yes → Completion stage
  - ✗ No → Error recovery (red path)
  - ⚠ Partial → Manual review (orange path)
- **Size:** 80px diamond

### Stage 6: Completion (Turquoise)
- **Position:** 95% from left (end of pipeline)
- **Visual:** Rounded rectangle with trophy icon
- **Label:** "OPERATION COMPLETE"
- **Activities:**
  - "Generate Report" document icon
  - "Update State" save icon
  - "Notify User" bell icon
- **Size:** 180px x 120px
- **Output:** Success arrow to "Results" (top-right)

## Special Paths & Flows

### Fast Track Lane (Gold)
- **Position:** Above main pipeline (10% canvas height)
- **Visual:** Gold express lane with lightning icon
- **Entrance:** From Router 1 for priority operations
- **Stages Bypassed:** Planning, Validation (goes straight to Execution)
- **Label:** "PRIORITY FAST TRACK"
- **Arrow Style:** Gold with speed lines

### Error Recovery Path (Red)
- **Position:** Below main pipeline (85% canvas height)
- **Visual:** Red maintenance track with wrench icon
- **Entry Points:** From safety check, validation, or testing failures
- **Stage:** "ERROR HANDLER & RETRY LOGIC" red box
- **Recovery:** Orange retry arrows looping back to appropriate stage
- **Max Retries:** "3x" badge shown

### Rollback Path (Orange)
- **Visual:** Dashed orange line running beneath execution
- **Trigger:** Critical failure during execution
- **Action:** Undo changes, restore previous state
- **Label:** "Emergency Rollback" with undo icon

## Pipeline Infrastructure

### Pipeline Rails (Visual Track)
- **Style:** Two parallel gray lines (#95a5a6) running full width
- **Position:** Top and bottom of main pipeline (20% and 80% height)
- **Purpose:** Visual guide showing operation flow path

### Progress Indicator
- **Style:** Colored bar showing operation advancement
- **Segments:** Each stage lights up when active (bright color)
- **Current Stage:** Pulsing glow effect
- **Position:** Thin bar along top of pipeline

### Data Packets
- **Visual:** Small envelope/package icons moving along pipeline
- **Color:** Changes to match current stage color
- **Quantity:** 2-3 packets at different pipeline positions
- **Animation:** Motion trails suggesting movement

## Typography & Labels

### Stage Headers
- **Font:** Bold sans-serif, 18pt
- **Color:** White on colored stage background
- **Position:** Top of each stage box
- **Style:** ALL CAPS

### Sub-component Labels
- **Font:** Regular sans-serif, 11pt
- **Color:** Dark gray (#2c3e50)
- **Position:** Inside stages as bulleted list
- **Icon Prefix:** Small icon before each label

### Checkpoint Labels
- **Font:** Medium sans-serif, 14pt
- **Position:** Inside decision shapes
- **Color:** Black (#000000)

### Path Labels
- **Font:** Italic sans-serif, 12pt
- **Position:** Along arrows
- **Background:** White pill for readability
- **Examples:** "Success", "Retry", "Fast Track"

## Technical Accuracy

### Operation Types
- **Setup:** Initialization, resource allocation, environment configuration
- **Standard:** Business logic, data processing, agent execution
- **Cleanup:** Resource deallocation, cache clearing, file removal

### Validation Requirements
- Safety checks MUST occur before execution
- Resource availability MUST be verified
- Conflict detection MUST prevent simultaneous conflicting operations

### Error Handling
- Maximum 3 retry attempts before failure
- Rollback MUST restore system to pre-execution state
- All errors MUST be logged with stack traces

### Success Criteria
- All tests pass (unit + integration)
- State updates persist correctly
- User notification sent successfully

## Style & Aesthetic
- **Design Language:** Industrial manufacturing pipeline meets software workflow
- **Detail Level:** High - show internal stage processes
- **Visual Metaphor:** Factory assembly line
- **Modern:** Flat design with subtle depth
- **Professional:** Enterprise process documentation

## Mood & Atmosphere
- **Systematic & Organized:** Clear stage progression
- **Reliable & Tested:** Multiple validation checkpoints
- **Efficient:** Fast track option for priority operations
- **Resilient:** Comprehensive error handling

## Output Specifications
- **Resolution:** 2560x1440 (2K)
- **Format:** PNG with transparency
- **DPI:** 300
- **Accessibility:** WCAG AA contrast
- **File Size:** <550KB

## Usage Context
- **Developer Documentation:** Understanding operation lifecycle
- **Process Documentation:** Workflow visualization
- **Troubleshooting:** Identifying failure points
- **Performance Optimization:** Finding bottlenecks

## DALL-E Generation Instruction

**Primary Prompt:**
"Create professional horizontal pipeline flowchart showing operation execution in CORTEX system. Left-to-right flow with 6 main stages: Intake (purple #9b59b6), Planning (yellow #ffd93d), Validation (orange #ff8c42), Execution (green #96ceb4), Testing (blue #4d96ff), Completion (turquoise #4ecdc4). Each stage as rounded rectangle (180px x 120px) with icons and sub-components. Pipeline splits into 3 parallel tracks after intake showing Setup, Standard, and Cleanup operations. Diamond checkpoints between stages for validation. Gold fast track lane above main pipeline. Red error recovery path below with retry loops. Gray pipeline rails running full width. Show data packet icons traveling along pipeline. Clean modern flowchart style with professional labeling. Light gray background."

**Refinement Prompt:**
"Add more detail to stage internals. Show progress indicator bar at top of pipeline lighting up active stages. Include spinning gear animation indicator in Execution stage. Add retry count badges (3x) to error recovery path. Show emergency rollback dashed line beneath execution. Make fast track lane more prominent with lightning bolt icons and speed lines."