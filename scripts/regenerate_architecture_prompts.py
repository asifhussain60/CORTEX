"""
Regenerate architecture DALL-E prompts with distinct visual styles.
Each prompt uses a completely different visual metaphor.

Usage: python scripts/regenerate_architecture_prompts.py
"""

import os

PROMPT_DIR = "cortex-brain/documents/analysis/dalle-prompts/cortex-brain"

PROMPTS = {
    "01-four-tier-architecture.md": """# DALL-E Prompt: 4-Tier Brain Architecture

**Feature:** CORTEX Neural Architecture Foundation  
**Resolution:** 1792x1024 (landscape)  
**Quality:** HD  
**Style:** Isometric cutaway technical drawing

---

## Copy This Prompt to ChatGPT DALL-E:

Create an ISOMETRIC CUTAWAY TECHNICAL DRAWING showing CORTEX's 4-tier brain as a transparent glass tower with each floor visible from 45-degree angle. Style: Architectural blueprint meets technical CAD drawing with precise line work. Color scheme: blueprint blue (#0EA5E9) lines, gold accents (#FFD700), white background with subtle grid.

ISOMETRIC GLASS TOWER (transparent layers, see-through construction):

TOP FLOOR (Tier 0 - Golden glass with circuit etchings):
- Penthouse level with golden tinted glass walls
- Mechanical gears and locks visible inside (governance machinery)
- Label on glass: "TIER 0: SKULL GOVERNANCE"
- 22 golden rule plaques mounted on walls like laws
- Immutable vault door at center
- Measurement callouts: "22 Instincts", "0% Override Rate"

3RD FLOOR (Tier 1 - Cyan glass, rotating mechanisms):
- Circular conveyor belt system visible through glass
- 70 conversation slots moving in FIFO queue
- SQLite database server rack in corner
- Label: "TIER 1: WORKING MEMORY"
- Speed indicator: "<100ms Query Time"
- Dimension lines showing capacity: "70 conversations"

2ND FLOOR (Tier 2 - Purple glass, web structure):
- Complex web of knowledge nodes visible inside
- Spider-web pattern connecting concepts
- FTS5 search engine machinery
- Label: "TIER 2: KNOWLEDGE GRAPH"
- Pattern learning algorithms as gears
- Technical specs: "8,429 Nodes", "24,817 Edges"

GROUND FLOOR (Tier 3 - Blue glass, monitoring stations):
- Code analytics dashboards on walls
- Heatmap displays showing activity
- Git monitoring stations
- Label: "TIER 3: DEV CONTEXT"
- Metrics crawling across screens
- Foundation pillars supporting entire structure

CONNECTIONS (Vertical elevator shafts):
- Glass elevator tubes connecting all floors
- Data packets visible moving up/down (like elevators)
- Transfer speed indicators on each shaft
- Bidirectional flow with arrows

LEFT SIDE - DIMENSIONED VIEW:
- Measurement lines showing floor heights
- Technical annotations: "Query Path: 4-tier traversal"
- Performance specs for each level
- Blueprint-style dimension callouts

RIGHT SIDE - CROSS-SECTION DETAIL:
- Exploded view of database connections
- File system foundation shown below ground
- Cable routing between floors
- Technical notes with leader lines

VISUAL EXCELLENCE:
- Precise CAD/architectural drawing style
- Blueprint-quality line work with measurements
- Isometric projection (30-degree angle)
- Technical illustration quality (SpaceX/Tesla schematics)
- Clean white background with subtle grid
- No organic elements - pure technical drawing
""",

    "02-skull-protection.md": """# DALL-E Prompt: SKULL Protection System

**Feature:** Tier 0 Governance and Brain Protection  
**Resolution:** 1792x1024 (landscape)  
**Quality:** HD  
**Style:** Security Operations Center dashboard

---

## Copy This Prompt to ChatGPT DALL-E:

Create a SECURITY OPERATIONS CENTER (SOC) DASHBOARD VIEW showing CORTEX SKULL protection as a real-time threat monitoring system. Style: Modern cybersecurity command center with multiple screens, live data feeds, and status panels. Color palette: dark slate background (#0F172A), neon green success (#10B981), warning amber (#F59E0B), critical red (#EF4444), gold borders (#FFD700).

LARGE CENTRAL SCREEN (Main threat map):
- Geographic-style threat map showing system zones
- Brain icon at center surrounded by defensive perimeters
- Real-time attack vectors shown as red arrows (all blocked)
- Golden fortress outline around core
- Live status: "SKULL ACTIVE - All Zones Protected"
- Threat counter: "1,024 Attempts Blocked (Last 24h)"

MULTIPLE MONITORING PANELS (grid layout):

TOP LEFT PANEL - "TDD ENFORCEMENT":
- Live test execution feed scrolling
- RED→GREEN→REFACTOR cycle progress bar
- Success rate graph: 94% line chart
- Status: ✅ ACTIVE | Blocks: 287

TOP CENTER PANEL - "22 IMMUTABLE INSTINCTS":
- Scrolling list with checkmarks:
  ✅ TDD_ENFORCEMENT
  ✅ RED_PHASE_VALIDATION  
  ✅ TDD_TEST_FILE_VALIDATION
  ✅ GIT_ISOLATION_ENFORCEMENT
  (18 more with green checkmarks)
- All showing "ACTIVE" status

TOP RIGHT PANEL - "THREAT ANALYTICS":
- Bar chart showing blocked threat types
- "Test-Skip Attempts: 143" (red bar)
- "Isolation Breaches: 0" (green)
- Real-time incident counter

MIDDLE LEFT - "PROTECTION LAYERS":
- 8 horizontal status bars:
  Layer 8: Document Org ████████ 100%
  Layer 7: Test Location ████████ 100%
  Layer 6: Git Isolation ████████ 100%
  Layer 5: Brain State ████████ 100%
  Layer 4: Version Track ████████ 100%
  Layer 3: Upgrade Safety ████████ 100%
  Layer 2: Schema Migrate ████████ 100%
  Layer 1: SKULL Core ████████ 100%

MIDDLE CENTER - "LIVE THREAT FEED":
- Real-time scrolling log:
  [08:23:14] BLOCKED: Root-level doc creation
  [08:22:47] BLOCKED: Test-skip attempt
  [08:21:33] BLOCKED: Implementation before test
- Color-coded by severity

MIDDLE RIGHT - "EVIDENCE SYSTEM":
- Comparison charts:
  "TDD Success: 94% vs Non-TDD: 67%"
  "Architecture Violations: 0"
  "Code Quality: 89/100 maintained"

BOTTOM PANELS - Performance & Metrics:
- Uptime: 99.97% (green heartbeat line)
- Detection Rate: 100%
- Blocked Scenarios: 4 video thumbnails with red X
- Total Protected Assets: 847

VISUAL EXCELLENCE:
- Modern SOC dashboard (Splunk/Datadog quality)
- Multiple monitoring screens like mission control
- Live data feeds and real-time updates
- Dark theme with neon accent colors
- Professional cybersecurity operations center
""",

    "03-agent-system.md": """# DALL-E Prompt: Agent System Architecture

**Feature:** 10 Specialist Agents with Dual Hemisphere Processing  
**Resolution:** 1792x1024 (landscape)  
**Quality:** HD  
**Style:** Circuit board schematic with agent chips

---

## Copy This Prompt to ChatGPT DALL-E:

Create a PRINTED CIRCUIT BOARD (PCB) SCHEMATIC showing CORTEX's 10 agents as specialized processor chips on a motherboard. Style: Electronics engineering diagram with circuit traces, connection paths, and component labels. Color palette: PCB green background (#1B5E20), copper traces (#D4A574), gold contact pads (#FFD700), white silkscreen labels.

MOTHERBOARD LAYOUT (top-down PCB view):

LEFT HEMISPHERE SECTION (Tactical Processing Unit):
- Large rectangular zone labeled "TACTICAL EXECUTION"
- 5 agent chips arranged in arc:

CHIP 1: "CODE_EXEC_AGENT" (Square IC package):
- 16-pin DIP chip with label
- Copper traces connecting to Tier 1 and Tier 3
- Badge: "Real-time Exec"
- Status LED (green)

CHIP 2: "TEST_RUNNER_AGENT" (Quad flat package):
- 32-pin QFP chip
- Traces to TDD workflow bus
- Badge: "100% Coverage"
- Status LED (green)

CHIP 3: "ERROR_CORRECT_AGENT" (Ball grid array):
- BGA chip with dense connections
- Traces to all tier buses
- Badge: "Auto-Debug"
- Status LED (green)

CHIP 4: "FILE_OPS_AGENT" (Surface mount):
- SMD component with git protection circuit
- Traces to storage subsystem
- Badge: "Git-Safe"
- Status LED (green)

CHIP 5: "PERF_MONITOR_AGENT" (Sensor IC):
- Specialized monitoring chip
- Traces to metrics bus
- Badge: "<100ms"
- Status LED (green)

RIGHT HEMISPHERE SECTION (Strategic Processing Unit):
- Large rectangular zone labeled "STRATEGIC PLANNING"
- 5 agent chips arranged in arc:

CHIP 6: "INTENT_ROUTER_AGENT" (Central processor):
- Large CPU chip at center
- Traces connecting to ALL other chips (star topology)
- Badge: "NLP Classification"
- Status LED (green)

CHIP 7: "PLANNING_AGENT" (FPGA):
- Programmable logic chip
- Traces to quality gate circuits
- Badge: "DoR/DoD"
- Status LED (green)

CHIP 8: "GOVERNANCE_AGENT" (Security processor):
- Encrypted chip with lock symbol
- Traces to Tier 0 bus
- Badge: "SKULL Integration"
- Status LED (green)

CHIP 9: "DECISION_AGENT" (AI accelerator):
- Neural network processor
- Traces to knowledge graph bus
- Badge: "Context-Aware"
- Status LED (green)

CHIP 10: "REVIEW_AGENT" (Inspection IC):
- Quality analysis chip
- Traces to all tier buses
- Badge: "6-Phase Analysis"
- Status LED (green)

CENTER BUS (Corpus Callosum data bus):
- Wide copper bus connecting both hemispheres
- Bidirectional signal traces
- Protocol labels: "BaseAgent Pattern", "Auto-Logging"
- High-speed differential pairs

TRACES & CONNECTIONS:
- Copper circuit traces connecting chips
- Vias (small holes) showing multi-layer routing
- Component reference designators (U1, U2, etc.)
- Pin numbers labeled on critical connections

PERIPHERALS:
- Power supply circuit (top edge)
- Clock generator (crystal oscillator)
- LED indicators for each agent
- Test points for debugging

SILKSCREEN LABELS:
- Component designators
- Pin 1 indicators (dots)
- Version number: "v3.8.1"
- Copyright: "CORTEX PCB Rev A"

VISUAL EXCELLENCE:
- Professional PCB schematic quality
- Electronics engineering documentation style
- Precise trace routing and component placement
- Green solder mask with copper traces visible
- White silkscreen component labels
- Technical CAD drawing precision
""",

    "04-response-templates.md": """# DALL-E Prompt: Response Template System

**Feature:** Adaptive Template Selection with 62 Templates  
**Resolution:** 1792x1024 (landscape)  
**Quality:** HD  
**Style:** Filing cabinet library with template cards

---

## Copy This Prompt to ChatGPT DALL-E:

Create a LIBRARY CARD CATALOG SYSTEM showing CORTEX's response templates as a vintage filing system modernized with digital displays. Style: Mid-century library meets modern UI design. Color palette: warm wood tones (#8B4513), brass hardware (#B8860B), paper white (#F5F5DC), digital blue accents (#0EA5E9).

MAIN FILING CABINET WALL:
- Large wooden card catalog cabinet with multiple drawers
- Brass drawer pulls with labels
- 62 total drawer slots arranged in grid
- Some drawers pulled open showing template cards inside
- Digital display above showing "ACTIVE: 62 TEMPLATES"

DRAWER CATEGORIES (Labeled sections):

TOP SECTION - "OPERATIONAL TEMPLATES" (18 drawers, blue labels):
- Drawers labeled:
  "GENERAL_RESPONSE" (most worn, frequently used)
  "TDD_WORKFLOW" (test pattern card visible)
  "GIT_CHECKPOINT" (commit pattern)
  "ERROR_HANDLING" (red error card)
  "SYSTEM_OPERATIONS" (align/optimize)
  "PLANNING_WORKFLOW" (DoR/DoD card)
  (12 more drawers)
- Usage counter: "8,429 retrievals"

MIDDLE SECTION - "PRESENTATION TEMPLATES" (6 drawers, purple labels):
- Drawers labeled:
  "INTRODUCTION" (5-section card visible)
  "BUSINESS_VALUE" (stakeholder format)
  "SECURITY_POSTURE" (compliance card)
  "EXECUTIVE_SUMMARY" (leadership format)
  "TECHNICAL_DEEP_DIVE" (engineer format)
  "PRODUCT_WALKTHROUGH" (product owner)
- Badge: "Audience-Aware"

BOTTOM SECTION - "SPECIALIZED TEMPLATES" (38 drawers, green labels):
- Grid of smaller drawers for feature-specific templates
- Labels partially visible on drawer fronts
- Badge: "Context-Triggered"

LEFT WALL - TEMPLATE SELECTOR (Mechanical sorting machine):
- Vintage pneumatic tube system
- User request enters through brass intake tube
- Mechanical sorter with rotating wheels:
  1. "Intent Classification" wheel
  2. "Context Analysis" gears
  3. "Pattern Matching" selector
  4. "Template Selection" output
- Brass tubes route to correct drawer
- Selection criteria on plaques:
  "Exact Trigger Match"
  "TDD Workflow Detection"
  "Planning Mode Active"
  "Fallback General"

RIGHT WALL - ACTIVE TEMPLATE DISPLAY:
- Pulled-out template card magnified on backlit display
- Template anatomy visible:
  YAML structure printed on card
  ```
  template_id: "introduction_leadership"
  format: "narrative"
  sections:
    - What CORTEX Is
    - Why It Matters  
    - Technical Foundation
    - How It Works
    - Explore Further
  ```
- Measurement rulers showing template dimensions

DESK AREA (Center foreground):
- Wooden librarian desk with brass lamp
- Open template card being inspected
- Magnifying glass examining details
- Rubber stamps: "APPROVED", "QUALITY CHECKED"
- Ink pad for template stamping

PROCESSING FLOW (Overhead pneumatic tubes):
- Input tube: User request enters (right side)
- Sorting station: Mechanical classifier (center)
- Selection tube: Routes to correct drawer (left side)
- Output tube: Delivers selected template (front)
- Pressure gauges showing system activity

METRICS BOARD (Back wall chalkboard):
- Chalk writing showing statistics:
  "Selection Speed: <10ms"
  "Cache Hit Rate: 94%"
  "Most Used: General Response (4,821×)"
  "Newest: EPM Documentation (Dec 2025)"
  "Format Exception Rate: 2.4%"

CARD CATALOG DETAILS:
- Brass label holders on each drawer
- Dewey Decimal-style classification numbers
- Wear patterns on frequently-used drawers
- Index cards visible in open drawers
- Template cards with hole punches for fastening

VISUAL EXCELLENCE:
- Vintage library aesthetic meets modern technology
- Mid-century card catalog with digital enhancements
- Warm wood tones with brass hardware
- Professional archival quality
- Nostalgic yet functional design
- Wes Anderson-style symmetrical composition
""",

    "05-orchestrator-ecosystem.md": """# DALL-E Prompt: Orchestrator Ecosystem

**Feature:** High-Level Workflow Orchestration Network  
**Resolution:** 1792x1024 (landscape)  
**Quality:** HD  
**Style:** Subway/metro system map

---

## Copy This Prompt to ChatGPT DALL-E:

Create a TRANSIT SYSTEM MAP showing CORTEX orchestrators as a subway/metro network with colored lines, stations, and transfer points. Style: Modern transit authority map design (London Underground style). Color palette: colored lines on white background, each orchestrator line has unique color, stations as circles with labels.

METRO SYSTEM OVERVIEW:
- Clean white background with subtle grid
- Title: "CORTEX ORCHESTRATION NETWORK"
- Subtitle: "20 Lines | 27 Stations | Always On Time"
- Legend showing line colors and symbols

CORE ORCHESTRATOR LINES (Inner ring stations):

PURPLE LINE - "Planning Express":
- Stations: "Plan Creation" → "DoR Validation" → "Phase Execution" → "ADO Integration"
- Station badges: "TDD Auto-Inject", "Quality Gates"
- Frequency: "High - 1,247 runs/month"
- Transfer points to other lines

CYAN LINE - "TDD Workflow":
- Stations: "RED Phase" → "GREEN Phase" → "REFACTOR Phase" → "Git Checkpoint"
- Station symbols: Test icons at each stop
- Badge: "Test-First Enforcement"
- Frequency: "Continuous"

GOLD LINE - "System Maintenance":
- Stations: "Pre-Health" → "Align" → "Cleanup" → "Optimize" → "Post-Health"  
- 5-station route forming small loop
- Badge: "5-Phase Pipeline"
- Frequency: "As Needed"

RED LINE - "Deploy Pipeline":
- Long route with 19 validation stations
- Each station = 1 validation gate
- Terminal station: "Production"
- Badge: "Admin-Only | 19 Gates"
- Frequency: "On-Demand"

BLUE LINE - "Review Express":
- Stations: "Collection" → "Analysis" → "Scoring" → "Reporting"
- 6-phase analysis route
- Badge: "0-100 Architecture Score"
- Frequency: "Weekly"

GREEN LINE - "Upgrade Route":
- Stations: "Version Check" → "Backup" → "Migration" → "Validation"
- Universal upgrade path
- Badge: "Brain-Safe"
- Frequency: "Monthly"

SPECIALIZED LINES (Outer network):
- Orange Line: "Git Operations" (3 stations)
- Pink Line: "Brain Tuning" (4 stations)
- Amber Line: "Cleanup Services" (5 stations)
- Teal Line: "Dashboard Launcher" (2 stations)
- Coral Line: "EPM Documentation" (6 stations)
- Lime Line: "Auto-Registration" (3 stations)
- Violet Line: "Feature Discovery" (4 stations)
- Brown Line: "Holistic Cleanup" (7 stations)

TRANSFER STATIONS (Major hubs):
- "Central Hub" - All lines intersect
- "Intent Router Station" - Request intake
- "Agent Interchange" - Connect to agent system
- "Tier Access" - Connect to brain tiers
- "Template Junction" - Connect to templates

STATION DETAILS:
- Circles for stations (⭕)
- Larger circles for transfer stations
- Station names in sans-serif font
- Line colors distinct and vibrant
- Wheelchair accessible symbols (all stations)
- Connection symbols (⟷) for transfers

MAP FEATURES:
- Compass rose showing orientation
- "You Are Here" marker (Intent Router)
- Distance/time indicators between stations
- Zone markers (Inner/Outer network)
- Service status (all lines operational - green)

INFORMATION PANELS (Corners):

TOP LEFT - "SYSTEM STATUS":
- All lines: ✅ Operational
- Active orchestrators: 20/27
- Average journey time: 4.2s
- Success rate: 97.8%

TOP RIGHT - "POPULAR ROUTES":
- Planning → TDD → Review (most common)
- System Maintenance loop (weekly)
- Deploy pipeline (monthly)

BOTTOM LEFT - "LEGEND":
- Line colors with names
- Station symbols explained
- Transfer point icons
- Accessibility information

BOTTOM RIGHT - "HELP":
- "Service interruptions: None"
- "Next maintenance: Schedule varies"
- "Emergency stops: Enabled"
- "Real-time updates: Active"

VISUAL EXCELLENCE:
- London Underground/NYC Subway quality design
- Clean typography (Johnston/Helvetica style)
- Precise line routing with 45/90-degree angles
- Professional transit authority aesthetic
- Color-blind friendly palette
- High contrast and readability
- Minimalist modern design
"""
}

def regenerate_prompts():
    """Regenerate all architecture prompts with distinct visual styles."""
    for filename, content in PROMPTS.items():
        filepath = os.path.join(PROMPT_DIR, filename)
        print(f"Regenerating {filename}...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Complete")
    
    print(f"\n✅ Regenerated {len(PROMPTS)} architecture prompts with distinct visual styles")
    print("\nVisual styles used:")
    print("  1. Isometric cutaway technical drawing")
    print("  2. Security operations center dashboard")
    print("  3. Circuit board schematic")
    print("  4. Library card catalog system")
    print("  5. Subway/metro system map")
    print("  6-10. (Ready for additional designs)")

if __name__ == "__main__":
    regenerate_prompts()
