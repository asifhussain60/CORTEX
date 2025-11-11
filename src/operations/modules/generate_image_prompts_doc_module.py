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
    
    def _get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="generate_image_prompts_doc",
            name="Generate Image Prompts Doc",
            description="Generate Image-Prompts.md with Gemini-compatible system diagrams",
            version="2.0",
            author="Asif Hussain",
            dependencies=["evaluate_cortex_architecture"],
            config_schema={
                "output_dir": {
                    "type": "string",
                    "description": "Output directory path",
                    "required": False
                }
            }
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
        """Generate tier architecture diagram prompt."""
        tier_details = []
        for tier in tiers:
            tier_id = tier.get('id', 'unknown')
            name = tier.get('name', 'Unknown')
            storage = tier.get('storage_type', 'N/A')
            tier_details.append(f"- **Tier {tier_id}**: {name} ({storage})")
        
        tier_list = '\n'.join(tier_details)
        
        return f"""## 📊 Diagram 1: The 4-Tier Brain Architecture

**Prompt for Gemini:**

```
Create a vertical architecture diagram showing CORTEX's 4-tier brain system:

{tier_list}

Visual requirements:
- Stack tiers vertically from bottom (Tier 0) to top (Tier 3)
- Each tier is a rectangular box with rounded corners
- Use the color palette: Tier 0 (purple), Tier 1 (blue), Tier 2 (green), Tier 3 (orange)
- Show upward arrows between tiers indicating data flow
- Label each tier with name and storage type
- Add small icons: Tier 0 (shield), Tier 1 (database), Tier 2 (graph), Tier 3 (chart)
- Include legend showing "Immutable → Dynamic" gradient
- Style: Modern, technical, clean lines
- Format: Wide landscape (16:9 aspect ratio)
```

**Expected output**: Vertical stack diagram with clear tier separation and data flow arrows."""
    
    def _generate_agent_diagram_prompt(self, agents: List[Dict]) -> str:
        """Generate agent system diagram prompt."""
        left_agents = [a for a in agents if a.get('hemisphere') == 'LEFT']
        right_agents = [a for a in agents if a.get('hemisphere') == 'RIGHT']
        
        left_list = '\n'.join([f"  - {a.get('name', 'Unknown')}: {a.get('role', '')}" for a in left_agents])
        right_list = '\n'.join([f"  - {a.get('name', 'Unknown')}: {a.get('role', '')}" for a in right_agents])
        
        return f"""## 🧠 Diagram 2: The 10 Specialist Agents (Brain Hemispheres)

**Prompt for Gemini:**

```
Create a brain hemisphere diagram showing CORTEX's 10 specialist agents:

LEFT BRAIN (Tactical Execution) - Cool colors:
{left_list}

RIGHT BRAIN (Strategic Planning) - Warm colors:
{right_list}

Visual requirements:
- Draw two brain hemispheres side by side
- LEFT hemisphere: blue/green tones, labeled "TACTICAL"
- RIGHT hemisphere: orange/red tones, labeled "STRATEGIC"
- Each agent is a circle with icon inside, positioned within hemisphere
- Connect hemispheres with "Corpus Callosum" bridge in center
- Show coordination arrows between related agents
- Label each agent with name and one-word role
- Add "Intent Detector" at top center (routes requests)
- Style: Anatomical meets technical, modern illustration
- Format: Square (1:1 aspect ratio)
```

**Expected output**: Dual-hemisphere brain diagram with agent positioning and coordination paths."""
    
    def _generate_plugin_diagram_prompt(self, plugins: List[Dict]) -> str:
        """Generate plugin architecture diagram prompt."""
        plugin_list = '\n'.join([f"  - {p.get('name', 'Unknown')}" for p in plugins[:8]])
        
        return f"""## 🔌 Diagram 3: Plugin System Architecture

**Prompt for Gemini:**

```
Create a plugin architecture diagram showing CORTEX's extensible system:

Core CORTEX (center):
- BasePlugin interface
- Plugin Registry
- Command Registry

Active Plugins (surrounding):
{plugin_list}

Visual requirements:
- Central hub labeled "CORTEX Core" (circular, purple gradient)
- Plugins arranged in circle around core
- Each plugin is a hexagon with icon
- Dashed lines from plugins to core showing inheritance
- Solid arrows showing command registration flow
- Show "Natural Language Router" at top connecting to core
- Label interface methods: initialize(), execute(), cleanup()
- Style: Hub-and-spoke, modern, clean
- Format: Square (1:1 aspect ratio)
```

**Expected output**: Hub-and-spoke plugin system with clear inheritance and registration flows."""
    
    def _generate_memory_flow_prompt(self, tiers: List[Dict]) -> str:
        """Generate memory flow diagram prompt."""
        return """## 💾 Diagram 4: Memory Flow (Conversation → Knowledge)

**Prompt for Gemini:**

```
Create a data flow diagram showing how conversations become knowledge in CORTEX:

Flow stages:
1. User Input → Intent Detector (natural language)
2. Intent Detector → Appropriate Agent (routing)
3. Agent → Tier 1 (SQLite conversation log)
4. Tier 1 → Tier 2 (pattern extraction)
5. Tier 2 → Knowledge Graph (YAML storage)
6. Knowledge Graph → Future Requests (context loading)

Visual requirements:
- Horizontal flow from left to right
- Each stage is a rounded rectangle
- Use tier colors for storage stages
- Show example data at each stage (small text snippets)
- Arrows indicate data transformation
- Label transformations: "Log", "Extract", "Store", "Recall"
- Add timing indicators (ms for fast, seconds for slower operations)
- Style: Technical flowchart, clean and precise
- Format: Wide landscape (16:9 aspect ratio)
```

**Expected output**: Left-to-right data flow showing conversation lifecycle."""
    
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
