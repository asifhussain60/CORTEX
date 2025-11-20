# DALL-E Prompt: Plugin System Architecture

## Visual Composition
- **Layout:** Hub-and-spoke radial architecture with central core
- **Orientation:** Square (1:1 aspect ratio) for balanced radial symmetry
- **Central Hub:** Core system in center with plugins radiating outward
- **Plugin Distribution:** 360° arrangement around core (12 plugins, 30° apart)

## Color Palette
- **Core System:** Dark Navy (#2c3e50) - Stable foundation
- **Plugin Registry:** Orange (#ff8c42) - Coordination layer  
- **Plugin Types (Rainbow Spectrum):**
  - Documentation: Green (#96ceb4)
  - Testing: Blue (#4d96ff)
  - Security: Red (#ff6b6b)
  - Integration: Purple (#9b59b6)
  - Monitoring: Yellow (#ffd93d)
  - Utility: Turquoise (#4ecdc4)
- **Connection Lines:** Gray (#95a5a6) with glow effect
- **Background:** Light (#f5f7fa) with subtle gear pattern

## Components & Elements

### Central Core (Center)
- **Position:** Exact center of canvas
- **Visual:** Large hexagon (200px diameter)
- **Color:** Dark navy with gradient
- **Icon:** Cortex brain symbol overlaid
- **Label:** "CORTEX CORE" in white text
- **Details:** Show 6 connection ports (one per hexagon side)

### Plugin Registry Ring (Middle)
- **Position:** Circular ring around core (100px radius from center)
- **Visual:** Orange dashed circle showing registry boundary
- **Label:** "Plugin Registry" on ring arc
- **Nodes:** 6 small orange circles on ring (registration points)

### Plugins (Outer Ring)
- **Position:** Radial placement at 400px radius from center
- **Visual:** Rounded squares (80px x 80px)
- **Quantity:** 12 plugins arranged in circle
- **Each Plugin Contains:**
  - Icon representing function
  - Plugin name label
  - Version badge (v1.0)
  - Active status indicator (green dot)

### Plugin Details (12 Specific Plugins)

**Top Section (12 o'clock to 3 o'clock):**
1. **Doc Generator** - Green, document icon
2. **Test Runner** - Blue, microscope icon
3. **Security Scanner** - Red, shield icon

**Right Section (3 o'clock to 6 o'clock):**
4. **GitHub Integration** - Purple, GitHub logo
5. **Telemetry** - Yellow, chart icon
6. **Cache Manager** - Turquoise, database icon

**Bottom Section (6 o'clock to 9 o'clock):**
7. **Health Monitor** - Yellow, heartbeat icon
8. **Backup Manager** - Red, archive icon
9. **API Gateway** - Purple, network icon

**Left Section (9 o'clock to 12 o'clock):**
10. **Logger** - Green, file icon
11. **Validator** - Blue, checkmark icon
12. **Optimizer** - Turquoise, lightning icon

## Relationships & Flow

### Plugin Registration (Dashed Lines)
- **Path:** Each plugin → Registry ring → Core
- **Style:** Dashed line (2px) with arrows
- **Color:** Light gray (#bdc3c7)
- **Label:** Small "register" text on line

### Active Communication (Solid Lines)
- **Path:** Core ↔ Active plugins (4-5 highlighted)
- **Style:** Solid glowing line (4px) with bidirectional arrows
- **Color:** Matches plugin color with 50% glow
- **Animation Indicator:** Pulse effect on line
- **Data Packets:** Small icons traveling along lines

### Inter-Plugin Communication
- **Paths:** Occasional arcs between adjacent plugins
- **Style:** Thin curved lines (1px)
- **Color:** Faint gray (#ecf0f1)
- **Purpose:** Show optional plugin-to-plugin messaging

## Typography & Labels

### Core Label
- **Text:** "CORTEX CORE"
- **Font:** Bold sans-serif, 22pt
- **Color:** White (#ffffff)
- **Position:** Center of hexagon

### Plugin Names
- **Font:** Medium sans-serif, 12pt
- **Position:** Below plugin icon
- **Color:** Dark text matching plugin color (darker shade)

### Registry Label
- **Font:** Italic sans-serif, 14pt
- **Position:** Curved along registry ring arc (top)
- **Color:** Orange (#ff8c42)

### Version Badges
- **Font:** Mono sans-serif, 9pt
- **Position:** Top-right corner of each plugin box
- **Style:** Small pill-shaped badge

## Technical Accuracy

### Core Requirements
- Central core MUST have 6 connection ports (hexagon design)
- Show plugin lifecycle: unloaded, registered, active, disabled
- Registry acts as intermediary (no direct core-to-plugin connections)

### Plugin Lifecycle States
- **Active:** Bright color + green status dot + glow
- **Registered:** Normal color + gray status dot
- **Disabled:** Desaturated color + red X overlay
- Show 4-5 active, 6-7 registered, 1-2 disabled

### Registry Functionality
- Acts as plugin discovery service
- Manages plugin versioning
- Handles dependency resolution
- Validates plugin interfaces

### Communication Patterns
- Core initiates requests (outbound solid arrows)
- Plugins respond with data (inbound dashed arrows)
- Event broadcasts shown as radiating waves from core

## Style & Aesthetic
- **Design Language:** Modular architecture diagram with technical overlay
- **Detail Level:** Medium - show plugin categories without overwhelming detail
- **Visual Metaphor:** Hub-and-spoke network, ecosystem
- **Modern:** Flat design with subtle gradients and glows
- **Scalability:** Suggest ability to add more plugins (empty plugin slot hints)

## Mood & Atmosphere
- **Extensible & Modular:** Shows easy plugin addition
- **Organized & Controlled:** Registry manages integration
- **Active & Dynamic:** Communication flows show live system
- **Enterprise-Ready:** Professional plugin management

## Output Specifications
- **Resolution:** 2560x2560 (Square, 2K)
- **Format:** PNG with transparency
- **DPI:** 300
- **Accessibility:** WCAG AA contrast
- **File Size:** <550KB

## Usage Context
- **Architecture Documentation:** Plugin system design
- **Developer Guide:** Creating custom plugins
- **Extension Marketplace:** Visual plugin catalog
- **Technical Presentations:** Explaining extensibility

## DALL-E Generation Instruction

**Primary Prompt:**
"Create professional hub-and-spoke plugin architecture diagram for CORTEX system. Central dark navy hexagon (#2c3e50) labeled 'CORTEX CORE' with brain icon. Orange dashed ring (#ff8c42) at 100px radius showing 'Plugin Registry'. 12 plugin boxes (80px squares) arranged in circle at 400px radius, each with unique icon and color: Doc Generator (green), Test Runner (blue), Security Scanner (red), GitHub Integration (purple), Telemetry (yellow), Cache Manager (turquoise), and 6 more varied plugins. Show solid glowing lines connecting core to 4-5 active plugins, dashed lines from all plugins to registry ring. Light background with subtle gear pattern. Modern flat design with professional labels. Rainbow spectrum of plugin colors. Square aspect ratio for balanced symmetry."

**Refinement Prompt:**
"Add version badges (v1.0) to plugin boxes. Include status indicators (green dots for active, gray for registered). Show data packet icons traveling along active communication lines. Add subtle glow effects to active connection lines. Make plugin icons more detailed and recognizable. Include 1-2 disabled plugins with desaturated colors and red X overlay."