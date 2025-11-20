# DALL-E Prompt: Setup Orchestration Workflow

## Visual Composition
- **Layout:** Vertical workflow diagram showing sequential setup phases
- **Orientation:** Portrait (9:16 aspect ratio) emphasizing downward progression
- **Flow Direction:** Top-to-bottom with branching decision trees
- **Phase Completion:** Progressive checklist showing installation progress

## Color Palette
- **Environment Detection:** Cyan (#17a2b8) - System analysis
- **Dependency Resolution:** Blue (#4d96ff) - Package management
- **Configuration:** Purple (#9b59b6) - Settings setup
- **Initialization:** Green (#96ceb4) - System preparation
- **Validation:** Orange (#ff8c42) - Health checks
- **Completion:** Success Green (#28a745) - Setup complete
- **Error States:** Red (#ff6b6b) - Problems detected
- **Background:** White (#ffffff) with setup checklist pattern

## Components & Elements

### Start Node (Top)
- **Position:** 10% from top, centered
- **Visual:** Green circle with play icon
- **Label:** "START SETUP"
- **Size:** 120px diameter
- **Trigger:** User command "cortex setup"

### Phase 1: Environment Detection (Cyan)
- **Position:** 18% from top
- **Visual:** Rounded rectangle with magnifying glass icon
- **Label:** "ENVIRONMENT ANALYSIS"
- **Size:** 300px x 150px
- **Sub-tasks:**
  - "Detect OS" (Windows/Mac/Linux icons)
  - "Check Python Version" (3.8+ requirement badge)
  - "Verify Shell" (PowerShell/Bash detection)
  - "Scan Dependencies" (package list icon)
- **Progress:** 4/4 tasks with checkmarks

### Decision 1: Environment Compatible?
- **Position:** After Phase 1
- **Visual:** Diamond shape
- **Label:** "Environment OK?"
- **Size:** 100px diamond
- **Paths:**
  - ✓ Yes (green arrow) → Phase 2
  - ✗ No (red arrow) → "Install Prerequisites" (side branch)

### Side Branch: Install Prerequisites (Red)
- **Position:** Right side branch from Decision 1
- **Visual:** Red rounded rectangle with download icon
- **Label:** "PREREQUISITE INSTALLER"
- **Actions:**
  - "Install Python 3.10+"
  - "Install Git"
  - "Install SQLite"
- **Reconnect:** Green arrow loops back to Environment Detection

### Phase 2: Dependency Resolution (Blue)
- **Position:** 35% from top
- **Visual:** Rounded rectangle with package box icon
- **Label:** "DEPENDENCY INSTALLATION"
- **Size:** 300px x 180px
- **Sub-tasks:**
  - "Create Virtual Environment" venv icon
  - "Install requirements.txt" pip icon (loading 47/52)
  - "Verify Package Integrity" checksum icon
  - "Build Native Extensions" compiler icon
- **Progress:** Loading bar showing 90% complete

### Phase 3: Configuration (Purple)
- **Position:** 52% from top
- **Visual:** Rounded rectangle with gear/settings icon
- **Label:** "CONFIGURATION SETUP"
- **Size:** 300px x 200px
- **Sub-tasks:**
  - "Generate cortex.config.json" (from template)
  - "Set API Keys" (masked input ****)
  - "Configure Brain Path" folder icon
  - "Setup Database Schema" database icon
  - "Initialize Working Memory" memory chip icon
- **Interaction:** User input required indicator (orange badge)

### Decision 2: Manual vs Automated?
- **Position:** After Phase 3
- **Visual:** Diamond with two distinct paths
- **Label:** "Configuration Mode?"
- **Size:** 120px diamond
- **Paths:**
  - **Auto:** Blue arrow → Use defaults, skip to Phase 4
  - **Manual:** Purple arrow → Interactive wizard (side panel)

### Side Panel: Interactive Wizard (Purple)
- **Position:** Left side branch from Decision 2
- **Visual:** Purple panel with form fields
- **Label:** "CONFIGURATION WIZARD"
- **Steps:**
  1. "Brain Storage Location" file picker
  2. "Agent Selection" checkbox list
  3. "LLM Provider" dropdown (OpenAI/Anthropic/Local)
  4. "Performance Tier" slider (Basic/Standard/Advanced)
- **Navigation:** Back/Next buttons, progress dots (●●●○)

### Phase 4: Initialization (Green)
- **Position:** 72% from top
- **Visual:** Rounded rectangle with rocket icon
- **Label:** "SYSTEM INITIALIZATION"
- **Size:** 300px x 160px
- **Sub-tasks:**
  - "Create Brain Structure" folder tree growing animation
  - "Initialize SQLite Database" database creation
  - "Load Agent Definitions" agent icons appearing
  - "Warm Up Cache" thermometer filling
- **Progress:** Animated checkmarks appearing sequentially

### Phase 5: Validation (Orange)
- **Position:** 85% from top
- **Visual:** Rounded rectangle with checklist icon
- **Label:** "HEALTH VALIDATION"
- **Size:** 300px x 140px
- **Health Checks:**
  - "Database Connectivity" 🟢 Pass
  - "File System Access" 🟢 Pass
  - "Agent Availability" 🟢 Pass
  - "Memory Allocation" 🟢 Pass
- **Status:** All green checkmarks

### Decision 3: All Tests Pass?
- **Position:** After Phase 5
- **Visual:** Diamond shape
- **Label:** "Validation OK?"
- **Size:** 100px diamond
- **Paths:**
  - ✓ Yes → Completion
  - ✗ No → "Troubleshoot Issues" (loops back to failed phase)

### Completion Node (Bottom)
- **Position:** 95% from top
- **Visual:** Green circle with checkmark icon
- **Label:** "SETUP COMPLETE"
- **Size:** 140px diameter
- **Celebration:** Confetti/sparkle effects around circle
- **Message:** "CORTEX is ready to use!" banner below

## Progress Tracker (Side)

### Overall Progress Bar
- **Position:** Right edge, vertical spanning 20-90% height
- **Visual:** Tall thin rectangle (40px x 800px)
- **Segments:** 5 colored sections matching phases
- **Current:** Highlighted/glowing segment
- **Percentage:** "68%" label at current position

### Phase Checklist
- **Position:** Left edge, vertical list
- **Visual:** Checkbox list with status icons
- **Items:**
  - ✓ Environment Detection
  - ✓ Dependencies Installed
  - ⏳ Configuration (in progress)
  - ⬜ Initialization
  - ⬜ Validation
- **Styling:** Completed (green checkmark), Active (spinner), Pending (empty box)

## Typography & Labels

### Phase Headers
- **Font:** Bold sans-serif, 20pt
- **Color:** White on colored phase background
- **Position:** Top of each phase box
- **Style:** ALL CAPS

### Sub-task Labels
- **Font:** Regular sans-serif, 12pt
- **Color:** Dark gray (#2c3e50)
- **Position:** Inside phases, bulleted list
- **Icon Prefix:** Status icon (checkmark/spinner/empty)

### Decision Labels
- **Font:** Medium sans-serif, 14pt
- **Position:** Inside diamond shapes
- **Color:** Black

### Path Labels
- **Font:** Italic sans-serif, 13pt
- **Position:** Along arrows
- **Examples:** "Success", "Failed", "Auto Mode"

## Technical Accuracy

### Environment Requirements
- **Python:** 3.8+ (3.10+ recommended)
- **Git:** Required for repository cloning
- **SQLite:** Built-in but must verify
- **Disk Space:** Minimum 500MB free
- **RAM:** 4GB minimum, 8GB recommended

### Configuration Options
- **Brain Path:** User-definable storage location
- **LLM Provider:** Support for multiple backends
- **Agent Selection:** Modular agent activation
- **Performance Mode:** Resource allocation tiers

### Validation Checks
- Database write/read test
- File system permissions check
- Network connectivity (if needed)
- Agent initialization verification
- Memory allocation success

### Error Recovery
- Automatic retry for transient failures (3 attempts)
- Detailed error messages with troubleshooting links
- Rollback capability if critical failure
- Log file generation for support

## Style & Aesthetic
- **Design Language:** Modern installation wizard meets technical flowchart
- **Detail Level:** High - show every sub-task with status
- **Visual Metaphor:** Software installer + progress tracker
- **Clean:** Minimal clutter, focus on current phase
- **Professional:** Enterprise onboarding quality

## Mood & Atmosphere
- **Guided & Supportive:** Clear step-by-step progression
- **Transparent:** User sees what's happening at each stage
- **Confidence-Inspiring:** Multiple validation checks
- **Celebratory:** Success state with positive reinforcement

## Output Specifications
- **Resolution:** 1440x2560 (Portrait, 2K)
- **Format:** PNG with transparency
- **DPI:** 300
- **Accessibility:** WCAG AA contrast
- **File Size:** <500KB

## Usage Context
- **Installation Guide:** Visual setup walkthrough
- **User Documentation:** Getting started tutorial
- **Troubleshooting:** Identifying setup failure points
- **Support Documentation:** Setup process reference

## DALL-E Generation Instruction

**Primary Prompt:**
"Create professional vertical setup workflow diagram for CORTEX system installation. Top-to-bottom flow with 5 main phases as rounded rectangles (300px x 150px): Environment Detection (cyan #17a2b8), Dependency Resolution (blue #4d96ff), Configuration (purple #9b59b6), Initialization (green #96ceb4), Validation (orange #ff8c42). Each phase shows sub-tasks with progress indicators. Diamond decision points between phases. Green start node at top (120px), green completion node at bottom (140px) with checkmark and confetti. Right side shows vertical progress bar (68% complete). Left side shows phase checklist with checkmarks and spinners. Side branches for prerequisite installation and interactive wizard. Clean white background. Modern installer aesthetic with professional labeling. Portrait orientation."

**Refinement Prompt:**
"Add more detail to sub-tasks with specific icons (Python logo, Git logo, database icons). Show loading indicators and progress bars within phases. Include user input fields in configuration wizard side panel. Add celebration effects (confetti/sparkles) around completion node. Make decision diamonds more prominent. Include retry arrows for failed validations."