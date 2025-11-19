"""
Generate Image Prompts Doc Module - Story Refresh Operation

This module generates Image-Prompts.md with Gemini-compatible system diagram
prompts for visualizing CORTEX architecture.

Author: Asif Hussain
Version: 2.0 (Architecture-driven prompt generation)
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class GenerateImagePromptsDocModule(BaseOperationModule):
    """
    Generate Image-Prompts.md for CORTEX architecture visualization.
    
    This module creates Gemini-compatible image generation prompts for:
    - 4-tier brain architecture diagram
    - 10 specialist agents (LEFT/RIGHT brain)
    - Plugin system architecture
    - Memory flow diagrams
    - Agent coordination patterns
    
    What it does:
        1. Extracts architecture structure from context
        2. Generates detailed Gemini prompts for each diagram
        3. Includes style guides and technical specifications
        4. Writes to Image-Prompts.md
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="generate_image_prompts_doc",
            name="Generate Image Prompts Doc",
            description="Generate Image-Prompts.md with Gemini-compatible system diagrams",
            phase=OperationPhase.PROCESSING,
            version="2.0",
            author="Asif Hussain",
            dependencies=["evaluate_cortex_architecture"]
        )
    
    def validate(self, context: Dict[str, Any]) -> OperationResult:
        """Validate prerequisites."""
        if 'feature_inventory' not in context:
            return OperationResult(
                success=False,
                status=OperationStatus.VALIDATION_FAILED,
                message="Missing feature_inventory (run evaluate_cortex_architecture first)"
            )
        
        return OperationResult(
            success=True,
            status=OperationStatus.VALIDATED,
            message="Prerequisites validated"
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Generate Image-Prompts.md."""
        try:
            logger.info("Generating Image-Prompts.md...")
            
            # Get output path
            output_dir = Path(context.get('output_dir', 'docs/story/CORTEX-STORY'))
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / 'Image-Prompts.md'
            
            # Backup existing file
            if output_path.exists():
                backup_dir = output_dir / '.backups'
                backup_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = backup_dir / f'Image-Prompts_{timestamp}.md'
                output_path.rename(backup_path)
                logger.info(f"Backed up to {backup_path}")
            
            # Extract architecture data
            feature_inventory = context.get('feature_inventory', {})
            tiers = feature_inventory.get('tiers', [])
            agents = feature_inventory.get('agents', [])
            plugins = feature_inventory.get('plugins', [])
            
            # Generate content
            content = self._generate_image_prompts(tiers, agents, plugins)
            
            # Write file
            output_path.write_text(content, encoding='utf-8')
            logger.info(f"Image prompts written: {output_path}")
            
            # Store in context
            context['image_prompts_path'] = output_path
            context['image_prompts_content'] = content
            
            return OperationResult(
                success=True,
                status=OperationStatus.COMPLETED,
                message=f"Image prompts generated: {output_path.name}",
                data={
                    "output_path": str(output_path),
                    "prompt_count": 6,
                    "tiers": len(tiers),
                    "agents": len(agents),
                    "plugins": len(plugins)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate image prompts: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Image prompts generation failed: {e}"
            )
    
    def _generate_image_prompts(
        self,
        tiers: List[Dict],
        agents: List[Dict],
        plugins: List[Dict]
    ) -> str:
        """Generate complete image prompts document."""
        sections = []
        
        # Header
        sections.append(self._generate_header())
        
        # Style guide
        sections.append(self._generate_style_guide())
        
        # Tier architecture diagram
        sections.append(self._generate_tier_diagram_prompt(tiers))
        
        # Agent system diagram
        sections.append(self._generate_agent_diagram_prompt(agents))
        
        # Plugin architecture diagram
        sections.append(self._generate_plugin_diagram_prompt(plugins))
        
        # Memory flow diagram
        sections.append(self._generate_memory_flow_prompt(tiers))
        
        # Agent coordination diagram
        sections.append(self._generate_coordination_prompt(agents))
        
        # Basement scene (Asif Codeinstein)
        sections.append(self._generate_basement_scene_prompt())
        
        # Footer
        sections.append(self._generate_footer())
        
        return '\n\n'.join(sections)
    
    def _generate_header(self) -> str:
        """Generate document header."""
        return f"""# CORTEX Visual Journey: Image Generation Prompts

**Gemini-Compatible System Diagrams**

*Generated: {datetime.now().strftime('%B %d, %Y')}*  
*Version: CORTEX 2.0*

---

> **Purpose**: These prompts generate visual representations of CORTEX architecture  
> **Target AI**: Google Gemini (optimized for system diagrams)  
> **Style**: Technical diagrams with narrative elements

---"""
    
    def _generate_style_guide(self) -> str:
        """Generate style guide section."""
        return """## 🎨 Visual Style Guide

**All diagrams should follow these conventions:**

**Color Palette:**
- **Tier 0 (Instinct)**: Deep Purple (`#6B46C1`) - Immutable foundation
- **Tier 1 (Memory)**: Bright Blue (`#3B82F6`) - Active conversation
- **Tier 2 (Knowledge)**: Emerald Green (`#10B981`) - Learned patterns
- **Tier 3 (Context)**: Warm Orange (`#F59E0B`) - Development metrics
- **LEFT Brain**: Cool tones (blues, greens)
- **RIGHT Brain**: Warm tones (oranges, reds)
- **Connections**: Gray (`#6B7280`) with arrows

**Typography:**
- Headers: Bold, sans-serif
- Labels: Regular weight, clear
- Code references: Monospace font

**Layout:**
- Top-to-bottom flow for hierarchies
- Left-to-right for agent coordination
- Circular for brain hemispheres
- Clear spacing between elements"""
    
    def _generate_tier_diagram_prompt(self, tiers: List[Dict]) -> str:
        """Generate tier architecture diagram prompt with professional DALL-E specifications."""
        tier_details = []
        for tier in tiers:
            tier_id = tier.get('id', 'unknown')
            name = tier.get('name', 'Unknown')
            storage = tier.get('storage_type', 'N/A')
            tier_details.append(f"- **Tier {tier_id}**: {name} ({storage})")
        
        tier_list = '\n'.join(tier_details)
        
        return f"""## 📊 Diagram 1: CORTEX 5-Tier Cognitive Architecture

**DALL-E Professional Prompt:**

```
Create a sophisticated technical architecture diagram showing CORTEX's five-tier cognitive system as a vertical layered architecture, styled as a professional AWS/Azure architecture diagram.

COMPOSITION & LAYOUT:
- Vertical orientation (portrait): 1024x1792px
- Five horizontal layers stacked bottom-to-top representing increasing abstraction
- Each tier occupies ~20% vertical space with 5% spacing between layers
- Foundation at bottom (Tier 0) is widest; layers taper slightly upward
- Clean white background with subtle gradient (light gray #F8F9FA at edges)

TIER SPECIFICATIONS:

TIER 0 - INSTINCT (Foundation, Bottom Layer):
- Color: Deep burgundy/crimson (#8B1538) with dark charcoal border (#2C2C2E)
- Visual: Thick foundation block with marble texture suggesting permanence
- Icon: Golden shield with lock symbol (left side, 64px)
- Label: "TIER 0: INSTINCT - Immutable Core Principles" (bold, 18pt, white)
- Content annotations: "TDD Enforcement • SOLID Principles • Rule #22 Brain Protection • Definition of Ready/Done"
- Border: 4px solid border with subtle drop shadow
- Special effect: Faint golden glow around edges suggesting foundational importance

TIER 1 - WORKING MEMORY (Above Tier 0):
- Color: Azure blue (#0078D4) with midnight blue border (#001F3F)
- Visual: Translucent rectangular panel with flowing particle effects
- Icon: Rotating database cylinder (animated suggestion, left side, 56px)
- Label: "TIER 1: WORKING MEMORY - Last 20 Conversations" (bold, 16pt, white)
- Content annotations: "SQLite conversation-history.jsonl • FIFO Queue (18/20) • <50ms query time • Entity tracking"
- Data visualization: Small line graph showing recent conversation activity (last 7 days)
- Special effect: Subtle blue pulse animation around edges, small data packets flowing upward

TIER 2 - KNOWLEDGE GRAPH (Middle Layer):
- Color: Emerald green (#10B981) with forest green border (#065F46)
- Visual: Neural network node visualization with interconnected spheres
- Icon: Glowing neural network (left side, 56px, animated with subtle connections)
- Label: "TIER 2: KNOWLEDGE GRAPH - Long-Term Learning" (bold, 16pt, white)
- Content annotations: "knowledge-graph.yaml • 3,247 patterns learned • FTS5 full-text search • Pattern confidence scoring"
- Data visualization: Small network graph showing pattern relationships (8-10 nodes interconnected)
- Special effect: Green connections between nodes pulsing with data flow, holographic overlay

TIER 3 - CONTEXT INTELLIGENCE (Above Middle):
- Color: Vibrant orange (#F59E0B) with burnt orange border (#D97706)
- Visual: Dashboard panel with mini metrics and gauges
- Icon: Analytics chart with upward trend (left side, 56px)
- Label: "TIER 3: CONTEXT INTELLIGENCE - Development Analytics" (bold, 16pt, white)
- Content annotations: "Git analysis (1,237 commits) • File hotspots detected • Code health 87% • Session productivity patterns"
- Data visualization: Three mini gauges showing commit velocity, code health, test coverage (all in green zones)
- Special effect: Orange glow with floating metric bubbles

TIER 4 - EVENT STREAM (Top Layer):
- Color: Purple gradient (#9333EA to #7C3AED) with deep purple border (#6B21A8)
- Visual: Flowing stream with event particles
- Icon: Scrolling log/stream (left side, 56px, animated upward motion)
- Label: "TIER 4: REAL-TIME EVENTS - Activity Stream" (bold, 16pt, white)
- Content annotations: "events.jsonl • Agent action logs • 23 events pending • Auto-learning triggers"
- Data visualization: Event timeline showing recent activity (color-coded by event type)
- Special effect: Purple particles flowing upward suggesting continuous data ingestion

DATA FLOW VISUALIZATION:
- Thick vertical arrows between tiers showing bidirectional data flow
- Upward arrows (blue): Raw data moving up the stack (labeled "Query", "Extract", "Analyze")
- Downward arrows (green): Processed insights flowing down (labeled "Context", "Patterns", "Guidance")
- Arrow width proportional to data volume (Tier 1→2 arrow is thickest)
- Semi-transparent gradient arrows with subtle glow effects

SIDE ANNOTATIONS:
- Right side vertical timeline showing: "Immutable Foundation → Working Memory → Learned Patterns → Dev Context → Live Events"
- Left side performance metrics: Query speeds for each tier (<50ms, <150ms, <200ms, real-time)
- Bottom legend: Color-coded key with tier numbers, names, and primary functions

PERIPHERAL ELEMENTS:
- Circular plugin nodes around perimeter (8 total) in light gray (#E5E7EB)
- Plugins: "Cleanup", "Documentation", "Self-Review", "Maintenance", "Crawler", "Validator", "Health Check", "Backup"
- Dashed connection lines from plugins to relevant tiers
- Plugin icons: broom, book, magnifying glass, wrench, spider, checkmark, heartbeat, shield

TECHNICAL SPECIFICATIONS:
- Typography: SF Pro Display / Segoe UI (sans-serif, professional tech aesthetic)
- Line weights: 2px for borders, 4px for data flow arrows, 1px for connection lines
- Spacing: Consistent 40px margins, 20px padding within tiers
- Shadow effects: Subtle drop shadows (2px offset, 4px blur, 10% opacity)
- Accessibility: High contrast labels, clear visual hierarchy, colorblind-safe palette

STYLE REFERENCES:
- AWS Architecture Diagrams (clean, professional, iconography)
- Microsoft Azure Well-Architected Framework visuals (layered tiers)
- Google Cloud Platform architecture diagrams (color-coded components)
- Modern SaaS product architecture diagrams (Stripe, Cloudflare, Vercel)

OUTPUT REQUIREMENTS:
- Resolution: 1024x1792px (portrait orientation for vertical architecture)
- Format: PNG with transparent background where appropriate
- Color depth: 24-bit RGB
- Anti-aliasing: Enabled for smooth lines and text
- Export quality: Maximum (suitable for documentation and presentations)
```

**Expected output**: Professional-grade vertical architecture diagram suitable for technical documentation, investor presentations, and engineering blog posts. Should communicate system sophistication and enterprise quality at a glance."""
    
    def _generate_agent_diagram_prompt(self, agents: List[Dict]) -> str:
        """Generate agent system diagram with sophisticated dual-hemisphere visualization."""
        left_agents = [a for a in agents if a.get('hemisphere') == 'LEFT']
        right_agents = [a for a in agents if a.get('hemisphere') == 'RIGHT']
        
        left_list = '\n'.join([f"  - {a.get('name', 'Unknown')}: {a.get('role', '')}" for a in left_agents])
        right_list = '\n'.join([f"  - {a.get('name', 'Unknown')}: {a.get('role', '')}" for a in right_agents])
        
        return f"""## 🧠 Diagram 2: Dual-Hemisphere Agent Coordination System

**DALL-E Professional Prompt:**

```
Create a sophisticated technical illustration showing CORTEX's dual-hemisphere cognitive agent system using a modern split-brain architectural visualization inspired by neuroscience and enterprise software diagrams.

COMPOSITION & LAYOUT:
- Horizontal orientation (landscape): 1792x1024px
- Split-screen composition: LEFT BRAIN (left 45%) | CORPUS CALLOSUM (center 10%) | RIGHT BRAIN (right 45%)
- Clean white/light gray gradient background (#FAFBFC)
- Subtle geometric patterns in background suggesting neural connectivity

LEFT HEMISPHERE - TACTICAL EXECUTION (Left Panel):
- Base color: Cool blue gradient (#0066CC to #4A90E2)
- Title: "LEFT BRAIN - Tactical Execution" (24pt bold, positioned top-left, white text with subtle shadow)
- Visual theme: Precise geometric shapes, straight lines, grid-aligned elements
- Icon theme: Gears, checkmarks, tools, build symbols

AGENT COMPONENTS (5 agents arranged in optimized workflow grid):

1. **Code Executor** (top-center, primary position):
   - Icon: Rotating gear/cog (64px, metallic blue with gradient)
   - Shape: Rounded square with 16px radius, gradient fill (#1976D2 to #2196F3)
   - Label: "CODE EXECUTOR" (14pt, bold)
   - Subtitle: "Implementation Engine" (10pt, italic)
   - Badge: "TDD Enforced" (small ribbon, green checkmark)
   - Connections: Receives from Corpus Callosum, sends to Test Generator

2. **Test Generator** (left-middle):
   - Icon: Beaker with checkmark (56px, glowing green accent)
   - Shape: Hexagon, gradient fill (#388E3C to #4CAF50)
   - Label: "TEST GENERATOR" (14pt, bold)
   - Subtitle: "Quality Assurance" (10pt, italic)
   - Badge: "RED Phase" (small ribbon, red indicator)
   - Connections: Receives from Code Executor, sends to Health Validator

3. **Error Corrector** (bottom-left):
   - Icon: Wrench with warning triangle (56px, orange accent)
   - Shape: Circle with border, gradient fill (#F57C00 to #FF9800)
   - Label: "ERROR CORRECTOR" (14pt, bold)
   - Subtitle: "Bug Hunter" (10pt, italic)
   - Badge: "Learning Mode" (small ribbon, yellow indicator)
   - Connections: Bidirectional with all other left agents

4. **Health Validator** (right-middle):
   - Icon: Heartbeat/EKG line in shield (56px, green pulse effect)
   - Shape: Rounded square, gradient fill (#00796B to #009688)
   - Label: "HEALTH VALIDATOR" (14pt, bold)
   - Subtitle: "DoD Enforcer" (10pt, italic)
   - Badge: "Zero Errors" (small ribbon, green checkmark)
   - Connections: Receives from Test Generator, sends to Commit Handler

5. **Commit Handler** (bottom-right):
   - Icon: Git branch with commit node (56px, dark blue)
   - Shape: Pentagon, gradient fill (#1565C0 to #1976D2)
   - Label: "COMMIT HANDLER" (14pt, bold)
   - Subtitle: "Version Control" (10pt, italic)
   - Badge: "Semantic" (small ribbon, blue indicator)
   - Connections: Final output to user, reports back to Corpus Callosum

CORPUS CALLOSUM - COORDINATION HUB (Center Bridge):
- Color: Purple gradient vertical band (#7B1FA2 to #9C27B0)
- Width: 120px, full height of canvas
- Title: "CORPUS CALLOSUM" (16pt, vertical text, white, rotated 90°)
- Subtitle: "Message Coordination Queue" (10pt, vertical, white)
- Visual: Flowing particle stream animation suggestion (hundreds of small dots moving bidirectionally)
- Network graph overlay: Small neural network pattern in lighter purple (#BA68C8)
- Glowing effect: Subtle animated glow suggesting active communication

BIDIRECTIONAL DATA FLOW (Through Corpus Callosum):
- LEFT→RIGHT (Strategic requests): Thick arrow (12px width), orange (#FF6B35)
  Labels: "Strategic Plan", "Context Request", "Pattern Query"
- RIGHT→LEFT (Execution tasks): Thick arrow (12px width), blue (#0066CC)
  Labels: "Task Assignment", "Execution Context", "DoR Validated"
- Arrow style: Gradient with glow effect, rounded ends, subtle animation suggestion

RIGHT HEMISPHERE - STRATEGIC PLANNING (Right Panel):
- Base color: Warm orange gradient (#FF6B35 to #FF8C42)
- Title: "RIGHT BRAIN - Strategic Planning" (24pt bold, positioned top-right, white text with subtle shadow)
- Visual theme: Organic curved shapes, flowing lines, creative arrangement
- Icon theme: Lightbulbs, chess pieces, shields, magnifying glasses

AGENT COMPONENTS (5 agents arranged in creative organic layout):

1. **Intent Router** (top-center, gateway position):
   - Icon: Compass with directional arrows (64px, glowing gold accent)
   - Shape: Octagon, gradient fill (#F57C00 to #FF9800)
   - Label: "INTENT ROUTER" (14pt, bold)
   - Subtitle: "Natural Language Gateway" (10pt, italic)
   - Badge: "0.92 Confidence" (small ribbon, green indicator)
   - Connections: Entry point from user, distributes to all right agents

2. **Work Planner** (left-middle, strategic position):
   - Icon: Chess knight piece with blueprint (56px, silver/white)
   - Shape: Diamond (rotated square), gradient fill (#D84315 to #FF5722)
   - Label: "WORK PLANNER" (14pt, bold)
   - Subtitle: "Strategic Architecture" (10pt, italic)
   - Badge: "Phase-Based" (small ribbon, blue indicator)
   - Connections: Sends strategic plans to Corpus Callosum

3. **Screenshot Analyzer** (top-right):
   - Icon: Camera with AI sparkle (56px, cyan accent)
   - Shape: Rounded rectangle, gradient fill (#00ACC1 to #00BCD4)
   - Label: "SCREENSHOT ANALYZER" (14pt, bold)
   - Subtitle: "Visual Intelligence" (10pt, italic)
   - Badge: "OCR Active" (small ribbon, cyan indicator)
   - Connections: Processes visual input, feeds to Work Planner

4. **Change Governor** (bottom-left):
   - Icon: Shield with gavel (56px, gold accent)
   - Shape: Shield, gradient fill (#F9A825 to #FDD835)
   - Label: "CHANGE GOVERNOR" (14pt, bold)
   - Subtitle: "Architecture Guardian" (10pt, italic)
   - Badge: "Protected" (small ribbon, red lock icon)
   - Connections: Monitors all changes, can veto risky operations

5. **Brain Protector** (bottom-right, guardian position):
   - Icon: Lock with neural network (56px, crimson accent with glow)
   - Shape: Pentagon with fortified border, gradient fill (#C62828 to #E53935)
   - Label: "BRAIN PROTECTOR" (14pt, bold)
   - Subtitle: "Rule #22 Enforcer" (10pt, italic)
   - Badge: "6 Layers Active" (small ribbon, red indicator)
   - Connections: Has veto power over all operations, connects to all agents

WORKFLOW TIMELINE (Bottom of diagram):
- Horizontal timeline showing typical request flow (8 seconds total duration)
- Stage 1 (0.0s): User Request → Intent Router (RIGHT)
- Stage 2 (0.8s): Intent Detection → Work Planner (RIGHT)
- Stage 3 (1.2s): Strategic Plan Created → Corpus Callosum Transfer
- Stage 4 (1.3s): Plan Received → Code Executor (LEFT)
- Stage 5 (5.5s): Implementation → Test Generator → Health Validator (LEFT)
- Stage 6 (7.8s): Tests Pass → Commit Handler (LEFT)
- Stage 7 (8.0s): Completion Report → User
- Color-coded timeline: RIGHT BRAIN (orange), CORPUS CALLOSUM (purple), LEFT BRAIN (blue)
- Time markers with small clock icons

PERIPHERAL ELEMENTS:
- "USER" icon (top-center, above Intent Router): Stick figure with speech bubble
- "TIER 2 KNOWLEDGE GRAPH" (bottom-center): Small database icon with bidirectional connections to both hemispheres
- Performance metrics sidebar (right edge): 
  * "Avg Response Time: 2.3s"
  * "Intent Accuracy: 92%"
  * "Test Pass Rate: 94%"
  * "Agent Coordination: 10/10 active"

CONNECTION STYLING:
- Agent-to-agent connections: 3px lines with gradient colors matching source agent
- Corpus Callosum connections: 6px thick lines with glow effect
- Data flow indicators: Small animated arrows along connection lines
- Connection style: Smooth curves (Bezier) not straight lines, suggesting organic coordination

TYPOGRAPHY & DETAILS:
- Font: SF Pro Display / Segoe UI / Roboto (professional sans-serif)
- Agent labels: 14pt bold, white text with 1px dark shadow for depth
- Subtitles: 10pt regular, semi-transparent white
- Badges: 8pt, contrasting colors, subtle gradient backgrounds
- Timeline text: 12pt regular, dark gray on light background

VISUAL EFFECTS:
- Subtle glow around active agents (2-3px outer glow, matching agent color)
- Drop shadows: 4px offset, 6px blur, 15% opacity
- Gradient backgrounds within each hemisphere (lighter at top, darker at bottom)
- Particle effects in Corpus Callosum (small dots suggesting data packets)
- Neural network pattern overlay in background (very subtle, 5% opacity)

ACCESSIBILITY:
- High contrast text (WCAG AAA compliant)
- Distinct shapes for each agent type (not just color differentiation)
- Clear labels and hierarchy
- Colorblind-safe palette (verified with Coblis simulator)

STYLE REFERENCES:
- Neuroscience brain imaging visualizations (split-brain studies)
- Enterprise software architecture diagrams (Microservices, Event-Driven Architecture)
- Apple Human Interface Guidelines (clean, minimal, effective use of space)
- GitHub's design system (Primer): professional tech aesthetic

OUTPUT REQUIREMENTS:
- Resolution: 1792x1024px (landscape orientation for dual-hemisphere layout)
- Format: PNG with transparent background capability
- Color depth: 24-bit RGB
- Anti-aliasing: Enabled for smooth curves and text
- Export quality: Maximum (suitable for documentation, presentations, social media)
```

**Expected output**: Sophisticated dual-hemisphere diagram showing clear separation of strategic (RIGHT) vs tactical (LEFT) processing, with prominent central coordination system. Should communicate enterprise-grade architecture and intelligent agent orchestration suitable for technical presentations and investor materials."""
    
    def _generate_plugin_diagram_prompt(self, plugins: List[Dict]) -> str:
        """Generate plugin architecture diagram with hub-and-spoke professional visualization."""
        plugin_list = '\n'.join([f"  - {p.get('name', 'Unknown')}" for p in plugins[:8]])
        
        return f"""## 🔌 Diagram 3: Plugin System Architecture (Hub-and-Spoke)

**DALL-E Professional Prompt:**

```
Create a sophisticated technical diagram showing CORTEX's extensible plugin architecture using a modern hub-and-spoke design pattern inspired by microservices architecture and API gateway patterns.

COMPOSITION & LAYOUT:
- Square orientation: 1536x1536px (optimized for social media and documentation)
- Radial/circular layout with central hub and peripheral plugin nodes
- Clean white background with subtle radial gradient (#FFFFFF center to #F5F7FA edges)
- Grid overlay (very subtle, 2% opacity) suggesting architectural precision

CENTRAL HUB - CORTEX CORE (Center of diagram):
- Size: 280px diameter circular node
- Color: Purple gradient (#6B46C1 to #805AD5) radiating outward
- Border: 6px solid border (#4C1D95), subtle outer glow
- Icon: Stylized brain with circuit board pattern overlay (120px, white/silver with gradient)
- Title: "CORTEX CORE" (20pt bold, white, centered)
- Subtitle: "Plugin Registry & Orchestration" (12pt, white, semi-transparent)
- Version badge: "v2.0" (small circular badge, top-right of core, #10B981 green)
- Visual effect: Subtle pulsing animation suggestion (2-second cycle, 95-100% scale)

PLUGIN REGISTRY RING (Surrounding core):
- Distance from core: 140px radius
- Visual: Octagonal ring made of 8 connection points
- Each connection point: Small hexagonal node (40px), light purple (#A78BFA)
- Labels on connection points (rotating around): 
  * "ON_STARTUP", "ON_DOC_REFRESH", "ON_SELF_REVIEW", "ON_DB_MAINTENANCE"
  * "ON_COMMIT", "ON_ERROR", "ON_BRAIN_UPDATE", "ON_SHUTDOWN"
- Connection style: Thin lines (2px) connecting hub to registry ring, dotted pattern
- Active status indicators: Small glowing dots (8px) next to active hooks (green #10B981)

PLUGIN NODES (8 plugins arranged radially, 360° / 8 = 45° spacing):
- Distance from core: 420px radius
- Plugin node size: 160px x 160px rounded rectangles (24px corner radius)
- Connection lines: 4px lines from registry ring to plugins, gradient from purple (ring) to plugin color

PLUGIN #1: Cleanup Plugin (0°, top position):
- Color: Cyan gradient (#0891B2 to #06B6D4)
- Icon: Broom with sparkles (72px, white)
- Label: "CLEANUP" (16pt bold, white)
- Subtitle: "Database Optimization" (10pt, white semi-transparent)
- Status badge: "ACTIVE" (small green dot, top-right corner)
- Connected hook: "ON_DB_MAINTENANCE" (line highlighted with glow)
- Metrics: "Last run: 2h ago" (8pt, below node)

PLUGIN #2: Documentation Plugin (45°, top-right):
- Color: Blue gradient (#2563EB to #3B82F6)
- Icon: Open book with sparkle (72px, white)
- Label: "DOCUMENTATION" (16pt bold, white)
- Subtitle: "Enterprise Doc Generation" (10pt, white semi-transparent)
- Status badge: "ACTIVE" (small green dot, top-right corner)
- Connected hook: "ON_DOC_REFRESH" (line highlighted)
- Metrics: "14 docs generated" (8pt, below node)

PLUGIN #3: Self-Review Plugin (90°, right position):
- Color: Orange gradient (#EA580C to #F97316)
- Icon: Magnifying glass with checkmark (72px, white)
- Label: "SELF-REVIEW" (16pt bold, white)
- Subtitle: "Quality Assurance" (10pt, white semi-transparent)
- Status badge: "ACTIVE" (small green dot, top-right corner)
- Connected hook: "ON_SELF_REVIEW" (line highlighted)
- Metrics: "92% pass rate" (8pt, below node)

PLUGIN #4: Maintenance Plugin (135°, bottom-right):
- Color: Green gradient (#059669 to #10B981)
- Icon: Wrench with gear (72px, white)
- Label: "MAINTENANCE" (16pt bold, white)
- Subtitle: "System Health" (10pt, white semi-transparent)
- Status badge: "ACTIVE" (small green dot, top-right corner)
- Connected hook: "ON_STARTUP" (line highlighted)
- Metrics: "Health: 94%" (8pt, below node)

PLUGIN #5: Vision API Plugin (180°, bottom position):
- Color: Purple gradient (#7C3AED to #8B5CF6)
- Icon: Camera with AI sparkle (72px, white)
- Label: "VISION API" (16pt bold, white)
- Subtitle: "Image Analysis" (10pt, white semi-transparent)
- Status badge: "BETA" (small yellow dot, top-right corner)
- Connected hook: "ON_STARTUP" (dotted line, not fully active)
- Metrics: "Mock mode" (8pt, below node)

PLUGIN #6: Crawler Plugin (225°, bottom-left):
- Color: Teal gradient (#0D9488 to #14B8A6)
- Icon: Spider/web crawler (72px, white)
- Label: "CRAWLER" (16pt bold, white)
- Subtitle: "Codebase Discovery" (10pt, white semi-transparent)
- Status badge: "ACTIVE" (small green dot, top-right corner)
- Connected hook: "ON_BRAIN_UPDATE" (line highlighted)
- Metrics: "3,247 files indexed" (8pt, below node)

PLUGIN #7: Health Check Plugin (270°, left position):
- Color: Pink gradient (#DB2777 to #EC4899)
- Icon: Heartbeat/EKG line (72px, white)
- Label: "HEALTH CHECK" (16pt bold, white)
- Subtitle: "System Monitoring" (10pt, white semi-transparent)
- Status badge: "ACTIVE" (small green dot, top-right corner)
- Connected hook: "ON_ERROR" (line highlighted)
- Metrics: "Uptime: 99.8%" (8pt, below node)

PLUGIN #8: Custom Plugin (315°, top-left):
- Color: Gray gradient (#6B7280 to #9CA3AF), dashed border indicating placeholder
- Icon: Puzzle piece (72px, light gray)
- Label: "CUSTOM PLUGIN" (16pt bold, light gray)
- Subtitle: "Your Extension Here" (10pt, light gray semi-transparent)
- Status badge: "DISABLED" (small gray dot, top-right corner)
- Connected hook: Multiple hooks (lines shown dotted, not active)
- Metrics: "Template available" (8pt, below node)

PLUGIN LIFECYCLE STATE MACHINE (Bottom panel, 380px x 120px):
- Background: Light gray rounded rectangle (#F3F4F6)
- Title: "Plugin Lifecycle" (14pt bold, dark gray #374151)
- State diagram showing:
  * State 1: "LOADED" (circle, blue #3B82F6)
  * State 2: "INITIALIZED" (circle, yellow #F59E0B)
  * State 3: "EXECUTING" (circle, green #10B981)
  * State 4: "CLEANUP" (circle, cyan #06B6D4)
  * State 5: "ERROR" (circle, red #EF4444, branching from any state)
- Arrows between states with labels: "register()", "execute()", "teardown()", "exception"
- Current state indicator: Green glow around "EXECUTING" state

CODE SNIPPET PANEL (Top-right corner, 320px x 200px):
- Background: Dark navy (#0F172A) with subtle code editor styling
- Title: "BasePlugin Interface" (12pt bold, cyan #06B6D4)
- Code (10pt monospace, syntax highlighted):
```python
class BasePlugin:
    def initialize() → bool:
        # Setup plugin resources
        
    def execute(context) → Result:
        # Main plugin logic
        
    def cleanup() → bool:
        # Release resources
        
    def on_error(error) → None:
        # Handle failures
```
- Line numbers in gray, keywords in purple, comments in green

BENEFIT CALLOUTS (Four corners, small floating cards):
- Top-left: "✓ Core Stays Minimal" (white card, green checkmark, 12pt)
- Top-right: "✓ Easy Extension" (white card, green checkmark, 12pt)
- Bottom-left: "✓ Enable/Disable Features" (white card, green checkmark, 12pt)
- Bottom-right: "✓ No Core Modifications" (white card, green checkmark, 12pt)

VISUAL EFFECTS:
- Plugin nodes: Subtle drop shadow (4px offset, 8px blur, 15% opacity)
- Active connection lines: Animated gradient flow suggestion (particles moving from hub to plugins)
- Hub glow: Radial gradient extending 40px beyond border (purple to transparent)
- Hover effect suggestion: Slightly larger scale for interactive elements
- Status badges: Small glow matching badge color

TYPOGRAPHY:
- Headers: SF Pro Display Bold / Segoe UI Bold (clear hierarchy)
- Labels: SF Pro Text / Segoe UI Regular (professional sans-serif)
- Code: SF Mono / Consolas / Fira Code (monospace for code snippets)
- All text: High contrast for readability

TECHNICAL SPECIFICATIONS:
- Line weights: 2px (dotted), 4px (active connections), 6px (core border)
- Spacing: Consistent 24px margins, 16px padding within cards
- Color palette: Vibrant but professional (verified for print and screen)
- Accessibility: WCAG AAA contrast ratios, distinct shapes not just colors

STYLE REFERENCES:
- Microservices architecture diagrams (hub-and-spoke pattern)
- API Gateway visualizations (central routing, peripheral services)
- Kubernetes architecture diagrams (orchestration layer)
- Figma/Sketch plugin marketplaces (modern UI card designs)

OUTPUT REQUIREMENTS:
- Resolution: 1536x1536px (square, optimized for social media and documentation)
- Format: PNG with transparent background capability
- Color depth: 24-bit RGB
- Anti-aliasing: Enabled for smooth curves, circles, and text
- Export quality: Maximum (suitable for blog posts, presentations, GitHub README)
```

**Expected output**: Professional hub-and-spoke plugin architecture diagram communicating extensibility, modularity, and enterprise-grade design. Should be visually compelling for both technical and non-technical audiences, suitable for landing pages and technical documentation."""
    
    def _generate_memory_flow_prompt(self, tiers: List[Dict]) -> str:
        """Generate memory flow diagram with data transformation visualization."""
        return """## 💾 Diagram 4: Memory Flow & Data Transformation Pipeline

**DALL-E Professional Prompt:**

```
Create a sophisticated technical diagram showing CORTEX's conversation memory flow from capture through long-term storage, using a modern data pipeline visualization style inspired by enterprise ETL (Extract, Transform, Load) systems and stream processing architectures.

COMPOSITION & LAYOUT:
- Horizontal orientation: 1792x1024px landscape
- Left-to-right flow representing temporal progression
- Clean white background with subtle horizontal flow lines (#F3F4F6, 1% opacity)
- Five distinct processing stages arranged horizontally with clear visual separation

STAGE 1: CONVERSATION CAPTURE (Left edge, 0-280px):
- Background: Light blue rounded rectangle (#DBEAFE, 240px x 860px, 24px radius)
- Title: "CAPTURE" (18pt bold, dark blue #1E40AF, top of section)
- Subtitle: "Real-Time Conversation Monitoring" (11pt, gray #6B7280)

Input Sources (stacked vertically, 3 sources):
1. VS Code Chat Window:
   - Icon: VS Code logo (64px)
   - Label: "GitHub Copilot Chat" (14pt semi-bold)
   - Status: Green pulse indicator (12px circle, animated)
   - Metrics: "Active session" (10pt, gray)

2. PowerShell Script:
   - Icon: Terminal/PowerShell icon (64px, blue)
   - Label: "cortex-capture.ps1" (14pt semi-bold, monospace)
   - Status: Blue dot (manual trigger)
   - Metrics: "Manual capture" (10pt, gray)

3. Python CLI:
   - Icon: Python logo (64px)
   - Label: "cortex remember" (14pt semi-bold, monospace)
   - Status: Blue dot (command-based)
   - Metrics: "CLI trigger" (10pt, gray)

Ambient Daemon (bottom of section):
- Visual: Circular daemon icon (72px, purple gradient #7C3AED)
- Label: "Ambient Capture Daemon" (12pt bold)
- Status: "Monitoring..." (10pt, green text)
- Frequency: "Every 30s" (9pt, gray)
- Connection: Dashed lines from daemon to all 3 sources

TRANSITION 1 → 2: CAPTURE TO TIER 1 (280-380px):
- Visual: Wide arrow (100px wide, gradient from light blue to yellow)
- Arrow style: Modern flat design, subtle shadow
- Label inside arrow: "Raw Text Extraction" (11pt white, centered)
- Data flow indicator: Small dots/particles flowing through arrow (animation suggestion)
- Metadata badge: "JSON formatting" (small pill, top of arrow)

STAGE 2: TIER 1 WORKING MEMORY (380-660px):
- Background: Yellow/amber rounded rectangle (#FEF3C7, 240px x 860px, 24px radius)
- Title: "TIER 1: WORKING MEMORY" (18pt bold, amber #D97706)
- Subtitle: "Short-Term Context (Last 20 Conversations)" (11pt, gray)

Storage Component (top half):
- Visual: Database cylinder icon (80px, SQLite logo style)
- Label: "conversations.db" (14pt semi-bold, monospace)
- Size indicator: "2.4 MB" (10pt, gray)
- Schema visualization (small table):
  * conversations (ID, user_message, assistant_response, timestamp)
  * messages (last 10 per conversation)
  * entities (file, class, method references)

FIFO Queue Visualization (middle):
- Visual: Horizontal queue with 20 slots (10px x 40px boxes each)
- First 18 slots: Filled (green #10B981)
- Slot 19: Current (yellow #F59E0B, pulsing)
- Slot 20: Empty (gray #E5E7EB)
- Label: "18/20 Conversations" (12pt, centered below)
- Arrow indicator: "Oldest → Newest" (small, gray)

Entity Extraction Engine (bottom half):
- Visual: Gear/cog icon with magnifying glass (64px)
- Label: "Entity Extractor" (12pt bold)
- Extraction types (small colored pills):
  * Files: 142 tracked (blue pill)
  * Classes: 87 tracked (purple pill)
  * Functions: 203 tracked (green pill)

Performance Metrics (bottom corner):
- Query Time: "18ms avg ⚡" (10pt, green)
- Storage: "48% capacity" (10pt, amber)

TRANSITION 2 → 3: TIER 1 TO TIER 2 (660-760px):
- Visual: Wide arrow (100px wide, gradient from yellow to purple)
- Label: "Pattern Extraction" (11pt white, centered)
- Process visualization: Small icons flowing through arrow
  * Workflow icon (wrench)
  * Intent pattern icon (target)
  * File relationship icon (linked nodes)
- Badge: "Confidence > 0.7" (small pill, top of arrow)

STAGE 3: TIER 2 KNOWLEDGE GRAPH (760-1040px):
- Background: Purple rounded rectangle (#E9D5FF, 240px x 860px, 24px radius)
- Title: "TIER 2: KNOWLEDGE GRAPH" (18pt bold, purple #7C3AED)
- Subtitle: "Long-Term Pattern Memory" (11pt, gray)

Knowledge Graph Visualization (top section):
- Visual: Network graph with nodes and edges
  * Central node: "CORTEX Patterns" (large circle, purple gradient)
  * Connected nodes: "Intent Patterns" (8 patterns), "Workflows" (5 templates), "File Relationships" (12 connections)
- Edge labels: Confidence scores (0.85, 0.92, 0.78, etc.)
- Visual style: Glowing connections, modern graph database aesthetic

Pattern Storage (middle):
- Database icon (80px, graph database style)
- Label: "knowledge-graph.db" (14pt semi-bold, monospace)
- Contents visualization (small cards):
  * 34 Patterns learned
  * 12 Workflow templates
  * 156 File relationships
- FTS5 search badge: "Full-text search enabled" (small pill)

Pattern Decay Engine (bottom left):
- Visual: Hourglass with decay curve graph (64px)
- Label: "Pattern Decay" (11pt bold)
- Decay rate: "5% per 30 days" (9pt, gray)
- Pruning threshold: "Confidence < 0.3" (9pt, red text)

Namespace Isolation (bottom right):
- Visual: Shield icon with namespace labels (64px)
- Namespaces: "cortex.*", "workspace.*", "archived.*" (small pills)
- Label: "Scope Protection" (11pt bold)

Performance Metrics (bottom corner):
- Search Time: "92ms avg ⚡" (10pt, purple)
- Storage: "5.2 MB" (10pt, purple)

TRANSITION 3 → 4: TIER 2 TO TIER 3 (1040-1140px):
- Visual: Wide arrow (100px wide, gradient from purple to teal)
- Label: "Context Aggregation" (11pt white, centered)
- Data types flowing: Git commits, file metrics, session analytics (small icons)
- Badge: "Last 30 days" (small pill, top of arrow)

STAGE 4: TIER 3 CONTEXT INTELLIGENCE (1140-1420px):
- Background: Teal rounded rectangle (#CCFBF1, 240px x 860px, 24px radius)
- Title: "TIER 3: CONTEXT INTELLIGENCE" (18pt bold, teal #0D9488)
- Subtitle: "Project Health & Analytics" (11pt, gray)

Git Analysis Engine (top section):
- Visual: Git branch visualization (64px, tree structure)
- Label: "Git Activity Analyzer" (12pt bold)
- Metrics display (small dashboard):
  * 1,237 commits analyzed
  * 42 commits/week velocity
  * 23 file hotspots identified

File Stability Monitor (middle left):
- Visual: Thermometer/gauge icon (64px)
- Label: "File Stability" (11pt bold)
- Status indicators (small list):
  * 89 files: STABLE (green)
  * 34 files: UNSTABLE (yellow)
  * 19 files: VOLATILE (red, warning icon)
- Example: "HostControlPanel.razor: 28% churn ⚠️"

Session Analytics (middle right):
- Visual: Clock with productivity graph (64px)
- Label: "Session Analytics" (11pt bold)
- Insights (small cards):
  * Best time: "10am-12pm" (green)
  * Avg session: "45 min" (teal)
  * Success rate: "94%" (green)

Code Health Dashboard (bottom):
- Visual: Heart with EKG line (64px)
- Metrics (horizontal pills):
  * Test Coverage: 76% (green bar)
  * Build Success: 97% (green bar)
  * Error Count: 0 (green checkmark)
  * Warning Count: 2 (yellow warning)

Performance Metrics (bottom corner):
- Analysis Time: "156ms avg ⚡" (10pt, teal)
- Lookback: "30 days" (10pt, teal)

TRANSITION 4 → OUTPUT: TIER 3 TO AGENTS (1420-1520px):
- Visual: Wide arrow (100px wide, gradient from teal to multi-color)
- Label: "Context Delivery" (11pt white, centered)
- Recipient icons: 10 agent icons flowing through arrow (mini versions)
- Badge: "Real-time updates" (small pill, top of arrow)

STAGE 5: AGENT CONSUMPTION (Right edge, 1520-1792px):
- Background: Light gray rounded rectangle (#F3F4F6, 240px x 860px, 24px radius)
- Title: "AGENTS" (18pt bold, dark gray #374151)
- Subtitle: "Context-Aware Decision Making" (11pt, gray)

Agent Grid (3 rows x 2 columns):
1. Intent Router: Brain icon (48px) + "Detects patterns" (9pt)
2. Work Planner: Checklist icon (48px) + "Recalls workflows" (9pt)
3. Code Executor: Hammer icon (48px) + "Avoids past errors" (9pt)
4. Test Generator: Flask icon (48px) + "Knows test patterns" (9pt)
5. Brain Protector: Shield icon (48px) + "Enforces rules" (9pt)
6. Context Arrow: "...5 more agents" (gray text)

Context Benefits (bottom section):
- Benefit pills (stacked):
  * "Remembers last 20 conversations" (purple)
  * "Learns from patterns" (purple)
  * "Warns of hotspots" (teal)
  * "Suggests workflows" (purple)

TIMELINE ANNOTATION (Bottom of entire diagram):
- Visual: Horizontal timeline bar spanning full width
- Time markers:
  * Capture: "Real-time" (0-1s)
  * Tier 1: "Immediate" (< 50ms)
  * Tier 2: "Pattern extraction" (24h batch)
  * Tier 3: "Weekly analysis" (7d interval)
  * Agents: "On demand" (< 100ms)

VISUAL EFFECTS:
- Data flow animation: Subtle particles/dots flowing left-to-right through arrows
- Active storage: Pulsing glow on database icons
- Queue filling: Green gradient showing capacity usage
- Graph edges: Animated glow on knowledge graph connections
- All cards: Subtle drop shadow (3px offset, 6px blur, 10% opacity)

TYPOGRAPHY:
- Headers: SF Pro Display Bold / Segoe UI Bold (18pt)
- Section titles: SF Pro Text Semi-Bold / Segoe UI Semi-Bold (12-14pt)
- Labels: SF Pro Text / Segoe UI Regular (10-11pt)
- Metrics: SF Mono / Consolas (9-10pt monospace for numbers)
- All text: Dark gray (#1F2937) on light backgrounds for WCAG AAA contrast

TECHNICAL SPECIFICATIONS:
- Arrow widths: 100px (major transitions)
- Section spacing: 20px gaps between stages
- Padding: 24px within each stage card
- Line weights: 2px (connections), 3px (arrows), 4px (emphasis)
- Color consistency: 5 distinct stage colors (blue, yellow, purple, teal, gray)

STYLE REFERENCES:
- AWS Step Functions workflow diagrams (state machine visualization)
- Apache Kafka stream processing pipelines (data flow)
- Datadog/New Relic dashboards (monitoring metrics)
- Figma/Miro flowcharts (modern clean design)

OUTPUT REQUIREMENTS:
- Resolution: 1792x1024px (16:9 landscape)
- Format: PNG with white background
- Color depth: 24-bit RGB
- Anti-aliasing: Enabled for smooth arrows, curves, and text
- Export quality: Maximum (suitable for technical documentation, presentations)
```

**Expected output**: Professional data pipeline diagram showing CORTEX's memory flow from real-time capture through intelligent context delivery, communicating the sophisticated multi-tier memory architecture with clear visual hierarchy and temporal progression."""
    
    def _generate_coordination_prompt(self, agents: List[Dict]) -> str:
        """Generate agent coordination diagram prompt."""
        return """## 🤝 Diagram 5: Agent Coordination Pattern

**Prompt for Gemini:**

```
Create a sequence diagram showing how CORTEX agents coordinate on a request:

Scenario: User says "Add a purple button to dashboard"

Sequence:
1. Intent Detector receives request
2. Detects intent: EXECUTE (not PLAN or TEST)
3. Routes to Executor Agent (LEFT brain)
4. Executor requests context from Pattern Matcher (RIGHT brain)
5. Pattern Matcher queries Tier 2 knowledge graph
6. Pattern Matcher returns: "Similar to Issue #42"
7. Executor implements feature
8. Executor notifies Tester Agent
9. Tester generates test cases
10. Validator checks quality
11. Documenter updates docs
12. Return success to user

Visual requirements:
- Vertical sequence diagram (UML style)
- Agents as vertical lifelines
- Horizontal arrows for messages
- Label each message with brief description
- Use agent hemisphere colors
- Show async operations with dashed lines
- Add timing markers (T+0ms, T+150ms, etc.)
- Highlight critical path
- Style: Professional UML, clear labels
- Format: Tall portrait (9:16 aspect ratio)
```

**Expected output**: UML sequence diagram showing multi-agent collaboration."""
    
    def _generate_basement_scene_prompt(self) -> str:
        """Generate Asif Codeinstein basement scene prompt."""
        return """## 🏠 Diagram 6: The Basement Lab (Narrative Scene)

**Prompt for Gemini:**

```
Create an illustration of Asif Codeinstein's basement lab where CORTEX was created:

Scene elements:
- New Jersey basement (concrete walls, small windows near ceiling)
- Asif at desk with multiple monitors showing code
- GitHub Copilot as physical machine (retro computer with green screen)
- Coffee cups everywhere (some moldy)
- Wizard of Oz poster on wall (inspiration source)
- Sticky notes with "CORTEX" sketches
- Bookshelf with AI/ML books
- Cat sleeping on keyboard
- Clock showing 2:47 AM
- "Day 43 without sleep" whiteboard

Mood: Humorous, relatable, slightly chaotic genius vibe

Visual requirements:
- Cartoon/illustration style (not photorealistic)
- Warm lighting from monitors (cold light from basement bulb)
- Exaggerated details (stack of pizza boxes, tangled cables)
- Asif: hoodie, wild hair, determined expression
- Copilot machine: retro terminal with personality
- Style: Xkcd meets The Oatmeal (funny technical comics)
- Format: Wide landscape (16:9 aspect ratio)
```

**Expected output**: Humorous, engaging illustration capturing the origin story."""
    
    def _generate_footer(self) -> str:
        """Generate document footer."""
        return """---

## 📝 Usage Instructions

**To generate these images:**

1. Copy each prompt (text in code blocks)
2. Paste into Google Gemini Image Generation
3. Adjust style parameters if needed
4. Download high-resolution versions
5. Save to `docs/story/CORTEX-STORY/images/`

**Naming convention:**
- `01-tier-architecture.png`
- `02-agent-system.png`
- `03-plugin-architecture.png`
- `04-memory-flow.png`
- `05-agent-coordination.png`
- `06-basement-scene.png`

**Recommended settings:**
- Resolution: 1920x1080 (landscape) or 1080x1920 (portrait)
- Format: PNG (transparent backgrounds where applicable)
- Quality: High (for documentation use)

---

**Related Documentation:**
- [THE-AWAKENING-OF-CORTEX.md](THE-AWAKENING-OF-CORTEX.md) - Narrative story
- [Technical-CORTEX.md](Technical-CORTEX.md) - Technical deep-dive
- [History.md](History.md) - Evolution timeline

---

*These prompts are optimized for Google Gemini but can be adapted for other AI image generators (DALL-E, Midjourney, Stable Diffusion) with minor modifications.*

**THE END**"""
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """Rollback by removing generated file."""
        try:
            prompts_path = context.get('image_prompts_path')
            
            if prompts_path and Path(prompts_path).exists():
                Path(prompts_path).unlink()
                logger.info(f"Removed image prompts: {prompts_path}")
            
            context.pop('image_prompts_path', None)
            context.pop('image_prompts_content', None)
            
            return True
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}", exc_info=True)
            return False
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """Determine if module should run."""
        return 'feature_inventory' in context
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return "Generating Gemini-compatible image prompts..."


def register() -> BaseOperationModule:
    """Register this module."""
    return GenerateImagePromptsDocModule()
