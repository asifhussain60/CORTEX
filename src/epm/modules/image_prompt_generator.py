"""
Image Prompt Generator Module - EPM Documentation Pipeline

Generates Gemini-compatible image generation prompts for CORTEX architecture
visualization. Supports the 3-part structure: prompts, narratives, generated images.

Architecture:
    - Extracts data from capabilities.yaml + module-definitions.yaml
    - Generates individual prompt files per diagram
    - Creates narrative explanations for each diagram
    - Organizes in directory structure for Copilot image merging

Author: Asif Hussain
Version: 1.0 (EPM Integration)
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

logger = logging.getLogger(__name__)


class ImagePromptGenerator:
    """
    Generate image prompts with Copilot-merge workflow support.
    
    Structure:
        docs/diagrams/
            prompts/           # AI generation prompts (input)
            narratives/        # Human-readable explanations (context)
            generated/         # AI-generated images (output)
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize generator.
        
        Args:
            output_dir: Base output directory (typically docs/diagrams)
        """
        self.output_dir = Path(output_dir)
        self.prompts_dir = self.output_dir / 'prompts'
        self.narratives_dir = self.output_dir / 'narratives'
        self.generated_dir = self.output_dir / 'generated'
        
        # Color palette for consistent branding
        self.colors = {
            'tier0': '#6B46C1',  # Deep Purple (Instinct)
            'tier1': '#3B82F6',  # Bright Blue (Memory)
            'tier2': '#10B981',  # Emerald Green (Knowledge)
            'tier3': '#F59E0B',  # Warm Orange (Context)
            'left_brain': '#3B82F6',   # Cool blue
            'right_brain': '#F59E0B',  # Warm orange
            'connections': '#6B7280'   # Gray
        }
    
    def generate_all(
        self,
        capabilities: Dict[str, Any],
        modules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate all image prompts and narratives from YAML configuration.
        
        This method now reads from diagram-definitions.yaml instead of using
        hardcoded diagram lists, ensuring configuration-driven generation.
        
        Args:
            capabilities: CORTEX capabilities data
            modules: Module definitions data
            
        Returns:
            Summary with paths and statistics
        """
        logger.info("Generating image prompts from diagram-definitions.yaml...")
        
        # Create directory structure
        self._create_directory_structure()
        
        # Load diagram configuration from YAML
        diagram_config = self._load_diagram_config()
        if not diagram_config:
            logger.error("Failed to load diagram-definitions.yaml")
            return {
                'success': False,
                'error': 'Could not load diagram configuration',
                'diagrams_generated': 0
            }
        
        # Extract architecture data
        tiers = capabilities.get('tiers', [])
        agents = capabilities.get('agents', [])
        plugins = capabilities.get('plugins', [])
        
        # Generate each diagram from configuration
        results = {}
        diagrams = diagram_config.get('diagrams', [])
        
        logger.info(f"Found {len(diagrams)} diagrams in configuration")
        
        for diagram_def in diagrams:
            diagram_id = diagram_def.get('id')
            diagram_type = diagram_def.get('type')
            
            logger.info(f"Generating diagram: {diagram_id} (type: {diagram_type})")
            
            # Route to appropriate generator based on type
            result = self._generate_diagram_by_type(
                diagram_def, 
                capabilities, 
                tiers, 
                agents, 
                plugins
            )
            
            if result:
                results[diagram_id] = result
            else:
                logger.warning(f"Failed to generate diagram: {diagram_id}")
        
        # Generate README for workflow instructions
        self._generate_readme()
        
        # Generate style guide
        self._generate_style_guide()
        
        return {
            'success': True,
            'diagrams_generated': len(results),
            'prompts_dir': str(self.prompts_dir),
            'narratives_dir': str(self.narratives_dir),
            'generated_dir': str(self.generated_dir),
            'results': results
        }
    
    def _create_directory_structure(self):
        """Create the 3-part directory structure."""
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.narratives_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created diagram structure at {self.output_dir}")
    
    def _load_diagram_config(self) -> Optional[Dict[str, Any]]:
        """
        Load diagram definitions from YAML configuration.
        
        Returns:
            Diagram configuration dict or None if failed
        """
        # Try to locate diagram-definitions.yaml
        config_paths = [
            Path('cortex-brain/admin/documentation/config/diagram-definitions.yaml'),
            Path('admin/documentation/config/diagram-definitions.yaml'),
            Path('../cortex-brain/admin/documentation/config/diagram-definitions.yaml')
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        logger.info(f"Loaded diagram config from: {config_path}")
                        return config
                except Exception as e:
                    logger.error(f"Error loading {config_path}: {e}")
                    continue
        
        logger.error("Could not find diagram-definitions.yaml in any expected location")
        return None
    
    def _generate_diagram_by_type(
        self,
        diagram_def: Dict[str, Any],
        capabilities: Dict[str, Any],
        tiers: List[Dict],
        agents: List[Dict],
        plugins: List[Dict]
    ) -> Optional[Dict[str, str]]:
        """
        Generate diagram based on type from configuration.
        
        Routes to appropriate specialized generator method based on diagram type.
        
        Args:
            diagram_def: Diagram definition from YAML
            capabilities: Full capabilities data
            tiers: Tier data
            agents: Agent data
            plugins: Plugin data
            
        Returns:
            Result dict with paths or None if failed
        """
        diagram_type = diagram_def.get('type')
        diagram_id = diagram_def.get('id')
        
        # Map diagram types to generator methods
        type_map = {
            'tier_architecture': lambda: self._generate_tier_architecture(tiers),
            'agent_system': lambda: self._generate_agent_system(agents),
            'plugin_architecture': lambda: self._generate_plugin_architecture(plugins),
            'plugin_system': lambda: self._generate_plugin_system(plugins, diagram_def),
            'module_structure': lambda: self._generate_module_structure(diagram_def),
            'memory_flow': lambda: self._generate_memory_flow(tiers),
            'agent_coordination': lambda: self._generate_agent_coordination(agents),
            'overview': lambda: self._generate_one_pager(capabilities, agents, plugins),
            'data_flow': lambda: self._generate_data_flow_diagram(diagram_def),
            'pipeline_flow': lambda: self._generate_pipeline_diagram(diagram_def),
            'flowchart': lambda: self._generate_generic_flowchart(diagram_def)
        }
        
        # Special case for basement_scene (no config needed)
        if diagram_id == '06-basement-scene':
            return self._generate_basement_scene()
        
        # Get the appropriate generator
        generator = type_map.get(diagram_type)
        
        if generator:
            try:
                return generator()
            except Exception as e:
                logger.error(f"Error generating {diagram_id}: {e}")
                return None
        else:
            logger.warning(f"Unknown diagram type: {diagram_type} for {diagram_id}")
            # Generate a placeholder for unknown types
            return self._generate_placeholder_diagram(diagram_def)
    
    def _generate_placeholder_diagram(self, diagram_def: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate placeholder for diagram types not yet implemented.
        
        Creates basic prompt and narrative as placeholder.
        """
        diagram_id = diagram_def.get('id')
        diagram_name = diagram_def.get('name', 'Unknown Diagram')
        description = diagram_def.get('description', 'No description available')
        
        prompt = f"""# {diagram_name}

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional diagram illustrating: {description}

This is a placeholder prompt. Full implementation pending.

**Diagram ID:** {diagram_id}
"""
        
        narrative = f"""# {diagram_name}

## Overview

{description}

## Implementation Status

This diagram is in the configuration but requires a specialized generator method.

**Diagram ID:** {diagram_id}
"""
        
        # Write files
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated placeholder for {diagram_id}")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png"),
            'placeholder': True
        }
    
    def _generate_data_flow_diagram(self, diagram_def: Dict[str, Any]) -> Dict[str, str]:
        """Generate data flow diagram from configuration."""
        diagram_id = diagram_def.get('id')
        diagram_name = diagram_def.get('name', 'Data Flow')
        description = diagram_def.get('description', '')
        source = diagram_def.get('source', 'Input')
        target = diagram_def.get('target', 'Output')
        
        prompt = f"""# {diagram_name}

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional data flow diagram showing: {description}

**Flow:** {source} → [Processing] → {target}

Use modern flat design with clear arrows and process boxes.

**Diagram ID:** {diagram_id}
"""
        
        narrative = f"""# {diagram_name}

## Overview

{description}

This diagram illustrates the flow from {source} to {target}.

**Diagram ID:** {diagram_id}
"""
        
        # Write files
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated data flow diagram: {diagram_id}")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png")
        }
    
    def _generate_pipeline_diagram(self, diagram_def: Dict[str, Any]) -> Dict[str, str]:
        """Generate pipeline flow diagram from configuration."""
        diagram_id = diagram_def.get('id')
        diagram_name = diagram_def.get('name', 'Pipeline')
        description = diagram_def.get('description', '')
        stages = diagram_def.get('stages', [])
        
        # Format stages for the prompt
        stages_text = "\n".join([f"- {stage.replace('_', ' ').title()}" for stage in stages]) if stages else "Multiple processing stages"
        
        prompt = f"""# {diagram_name}

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional horizontal pipeline flow diagram showing: {description}

## Design Requirements

**Style:** Modern flowchart with clean boxes and arrows
**Canvas:** 16:9 landscape orientation
**Layout:** Left-to-right flow

## Pipeline Stages:

{stages_text}

## Visual Specifications

**Stage Boxes:**
- Rounded rectangles (8px corner radius)
- Gradient fill (blue to light blue)
- Drop shadow (2px offset, 4px blur)
- White text, bold font
- Equal spacing between stages

**Arrows:**
- Bold arrows (4px width) with arrowheads
- Color: #3B82F6 (blue)
- Labels indicating data flow

**Icons:**
- Small icon in top-right of each box
- Consistent style across all stages

**Background:** Clean white or very light gray

**Diagram ID:** {diagram_id}
"""
        
        narrative = f"""# {diagram_name}

## Overview

{description}

## Pipeline Flow

This diagram illustrates a multi-stage pipeline with the following stages:

{stages_text}

Each stage processes data and passes results to the next stage in sequence.

## Business Value

- **Visibility:** Clear understanding of processing flow
- **Maintainability:** Easy to identify bottlenecks
- **Reliability:** Validation at each stage
- **Scalability:** Stages can be independently optimized

**Diagram ID:** {diagram_id}
"""
        
        # Write files
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated pipeline diagram: {diagram_id}")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png")
        }
    
    def _generate_generic_flowchart(self, diagram_def: Dict[str, Any]) -> Dict[str, str]:
        """Generate generic flowchart from configuration."""
        return self._generate_placeholder_diagram(diagram_def)
    
    def _generate_module_structure(self, diagram_def: Dict[str, Any]) -> Dict[str, str]:
        """Generate module structure diagram showing Python package organization."""
        diagram_id = diagram_def.get('id')
        diagram_name = diagram_def.get('name', 'Module Structure')
        description = diagram_def.get('description', 'Python module organization')
        
        prompt = f"""# {diagram_name}

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional hierarchical module structure diagram showing: {description}

## Design Requirements

**Style:** Clean tree/hierarchy diagram with folder icons
**Canvas:** 1:1 square orientation for hierarchy visualization
**Layout:** Top-down tree structure

## Visual Specifications

**Module Boxes:**
- Folder icons for packages
- File icons for modules
- Nested indentation showing hierarchy
- Color coding:
  - Root: Dark blue (#1E3A8A)
  - Packages: Medium blue (#3B82F6)
  - Modules: Light blue (#93C5FD)

**Connections:**
- Thin lines connecting parent to children
- Tree-like branching structure

**Labels:**
- Module/package names in monospace font
- Small description text below each item

**Background:** Clean white

**Diagram ID:** {diagram_id}
"""
        
        narrative = f"""# {diagram_name}

## Overview

{description}

## Module Organization

This diagram shows the hierarchical structure of Python packages and modules, illustrating:

- **Package Structure:** How code is organized into logical packages
- **Module Dependencies:** Relationships between modules
- **Code Organization:** Clean separation of concerns

## Benefits

- **Maintainability:** Clear structure makes code easy to navigate
- **Scalability:** Modular design supports growth
- **Testing:** Isolated modules are easier to test
- **Collaboration:** Teams understand project organization

**Diagram ID:** {diagram_id}
"""
        
        # Write files
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated module structure diagram: {diagram_id}")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png")
        }
    
    def _generate_plugin_system(self, plugins: List[Dict], diagram_def: Dict[str, Any]) -> Dict[str, str]:
        """Generate plugin system architecture diagram."""
        diagram_id = diagram_def.get('id')
        diagram_name = diagram_def.get('name', 'Plugin System')
        description = diagram_def.get('description', 'Plugin architecture and lifecycle')
        
        # Extract plugin names
        plugin_names = [p.get('name', 'Unknown') for p in plugins[:5]]  # Limit to 5 for clarity
        plugins_text = "\n".join([f"- {name}" for name in plugin_names])
        
        prompt = f"""# {diagram_name}

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional plugin architecture diagram showing: {description}

## Design Requirements

**Style:** Hub-and-spoke architecture with central core
**Canvas:** 16:9 landscape orientation
**Layout:** Central hub with plugins radiating outward

## Core Components:

- **Central Hub:** Core system with plugin manager
- **Plugin Hooks:** Event system (ON_STARTUP, ON_SHUTDOWN, etc.)
- **Example Plugins:**
{plugins_text}

## Visual Specifications

**Hub (Center):**
- Large rounded rectangle
- Gradient fill (purple to blue)
- "Plugin Manager" label
- Hook connection points around perimeter

**Plugins (Spokes):**
- Medium rounded rectangles radiating from hub
- Each with unique icon
- Connected to hub with arrows
- Color: Blue (#3B82F6)

**Hooks:**
- Small circles on hub perimeter
- Labels: ON_STARTUP, ON_SHUTDOWN, ON_EVENT, etc.
- Connection lines to plugins

**Lifecycle Panel:**
- Bottom corner: Loaded → Initialized → Executing → Cleanup
- State flow with arrows

**Background:** Clean white with subtle grid

**Diagram ID:** {diagram_id}
"""
        
        narrative = f"""# {diagram_name}

## Overview

{description}

## Plugin Architecture

The plugin system enables extensibility without modifying core code:

- **Central Hub:** Plugin manager coordinates all plugins
- **Event Hooks:** Plugins respond to system events
- **Isolation:** Plugins run independently
- **Lifecycle:** Managed initialization, execution, and cleanup

## Example Plugins

{plugins_text}

## Benefits

- **Extensibility:** Add features without changing core
- **Maintainability:** Plugins are self-contained
- **Flexibility:** Enable/disable features dynamically
- **Testing:** Plugins tested in isolation

**Diagram ID:** {diagram_id}
"""
        
        # Write files
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated plugin system diagram: {diagram_id}")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png")
        }

    def _create_directory_structure(self):
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.narratives_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created diagram structure at {self.output_dir}")
    
    def _generate_tier_architecture(self, tiers: List[Dict]) -> Dict[str, str]:
        """Generate Tier Architecture diagram (16:9 landscape)."""
        diagram_id = "01-tier-architecture"
        
        # Build tier details
        tier_details = []
        for tier in tiers:
            tier_id = tier.get('id', 'unknown')
            name = tier.get('name', 'Unknown')
            storage = tier.get('storage_type', 'N/A')
            color = self.colors.get(f'tier{tier_id}', '#6B7280')
            tier_details.append({
                'id': tier_id,
                'name': name,
                'storage': storage,
                'color': color
            })
        
        # Generate prompt
        prompt = f"""# Diagram 01: CORTEX 4-Tier Brain Architecture

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional, modern vertical architecture diagram showing CORTEX's 4-tier brain system. Use a clean infographic style suitable for corporate presentations and technical documentation.

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional, modern vertical architecture diagram showing CORTEX's 4-tier brain system. Use a clean infographic style suitable for corporate presentations and technical documentation.

## Design Requirements

**Style:** Professional technical infographic with modern flat design aesthetic, crisp edges, clean lines, high contrast for readability

**Canvas:** 16:9 landscape orientation (3840x2160 pixels equivalent)

## Tier Layout (Bottom to Top - Vertical Stack)

{self._format_tier_list(tier_details)}

**Spacing:** 40px between tier boxes, 60px margin from canvas edges

## Visual Specifications

**Tier Boxes:**
- Rounded rectangles (12px corner radius)
- Subtle gradient fill from tier color to lighter shade
- Soft drop shadow (4px offset, 8px blur, 20% opacity)
- White or light text for contrast
- Each box: 800px wide × 180px tall

**Icons (Per Tier):**
- Position: Top-left corner of each tier box
- Size: 48×48px, white with subtle glow
- Style: Outlined icons, consistent stroke width
- Tier 0: Shield icon
- Tier 1: Database cylinder icon
- Tier 2: Connected nodes (network graph) icon
- Tier 3: Bar chart / analytics icon

**Arrows Between Tiers:**
- Upward-pointing, centered between boxes
- Color: #6B7280 (medium gray)
- Thickness: 3px with arrowhead
- Label: "Data Flow ↑" in small gray text

**Typography:**
- Title: "CORTEX 4-Tier Brain Architecture" - Bold, 36pt, sans-serif, centered at top
- Tier names: Bold, 24pt, white text
- Storage type: Regular, 14pt, white text with 80% opacity
- Layer labels: Regular, 12pt, gray text

**Legend (Bottom Right):**
- Box: 200px × 120px, white with light border
- Content: "Immutable → Dynamic" gradient explanation
- Arrow direction key
- Small color swatches with labels

**Background:**
- Clean white or very light gray (#F9FAFB)
- No distracting patterns or textures

**Overall Quality:**
- High contrast for readability
- Professional color palette (no harsh colors)
- Balanced composition (not too busy)
- Print-quality resolution (300 DPI equivalent)
- Conference slide ready

## Technical Accuracy

- Tier 0: governance/rules.md (YAML, immutable)
- Tier 1: conversations.db (SQLite, FIFO queue, last 20)
- Tier 2: knowledge-graph.db (SQLite + FTS5)
- Tier 3: context-intelligence.db (SQLite analytics)

*Generated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        # Generate narrative
        narrative = f"""# Tier Architecture Narrative

## For Leadership

The 4-Tier Brain Architecture shows how CORTEX stores and processes information, similar to human memory systems.

**Tier 0 (Foundation)** - Like your core values, these are fundamental rules that never change. They protect CORTEX from making bad decisions.

**Tier 1 (Working Memory)** - Like short-term memory, remembers your last 20 conversations. When you say "make it purple," CORTEX remembers what "it" refers to.

**Tier 2 (Long-Term Memory)** - Like learning from experience, stores patterns from past work. If you've done authentication before, CORTEX suggests similar approaches.

**Tier 3 (Context Intelligence)** - Like situational awareness, analyzes your project's health. Warns about risky files, suggests optimal work times.

## For Developers

**Architecture Pattern:** Layered persistence with progressive intelligence

```
Tier 3 (Context) ──▶ Analyzes project metrics
         ↑
Tier 2 (Knowledge) ──▶ Learns from patterns
         ↑
Tier 1 (Memory) ──▶ Tracks conversations
         ↑
Tier 0 (Instinct) ──▶ Enforces core rules
```

**Storage Strategy:**
- **Tier 0:** YAML files (immutable, version controlled)
- **Tier 1:** SQLite with FIFO queue (20 conversation limit)
- **Tier 2:** SQLite with FTS5 (full-text search, pattern decay)
- **Tier 3:** SQLite with analytics (git history, file churn)

**Performance:**
- Tier 1: <50ms query (target), 18ms actual ⚡
- Tier 2: <150ms search (target), 92ms actual ⚡
- Tier 3: <200ms analysis (target), 156ms actual ⚡

## Key Takeaways

1. **Data flows upward** - Raw conversations → Patterns → Intelligence
2. **Each tier has specific purpose** - No overlap or duplication
3. **Progressive intelligence** - More processing at higher tiers
4. **Performance optimized** - SQLite + indexes + caching
5. **Local-first** - No external dependencies or cloud services

## Usage Scenarios

**Scenario 1: First-Time User**
- Tier 0 loads core rules
- Tier 1 starts empty (no conversations yet)
- Tier 2 has default patterns
- Tier 3 analyzes existing git history

**Scenario 2: Experienced User**
- Tier 0 enforces quality standards
- Tier 1 remembers recent context ("make it purple" works)
- Tier 2 suggests proven workflows
- Tier 3 warns about risky files proactively

*Version: 1.0*  
*Last Updated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        # Write files
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated {diagram_id} prompt and narrative")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png")
        }
    
    def _generate_agent_system(self, agents: List[Dict]) -> Dict[str, str]:
        """Generate Agent System diagram (1:1 square)."""
        diagram_id = "02-agent-system"
        
        # Separate by hemisphere
        left_agents = [a for a in agents if a.get('hemisphere') == 'LEFT']
        right_agents = [a for a in agents if a.get('hemisphere') == 'RIGHT']
        
        prompt = f"""# Diagram 02: CORTEX Agent System (Dual Hemispheres)

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional split-view diagram showing CORTEX's 10 specialist agents organized by hemisphere. Use modern flat design with clear visual separation and professional color scheme suitable for technical presentations.

## Design Requirements

**Style:** Modern flat design infographic, clean corporate aesthetic, high readability, professional color coordination

**Canvas:** 1:1 square aspect ratio (2160x2160 pixels equivalent)

## Layout Structure

**Split Canvas Vertically (50/50):**
- LEFT Hemisphere: Cool blue section ({self.colors['left_brain']})
- RIGHT Hemisphere: Warm orange section ({self.colors['right_brain']})
- Center Bridge: Gray connector ({self.colors['connections']})

## LEFT Hemisphere (Tactical Execution) - {len(left_agents)} Agents

**Background:** Subtle blue gradient (light to medium blue)
**Header:** "LEFT BRAIN" - Bold, 28pt, white text, top of section
**Subheader:** "Tactical Execution" - Regular, 16pt, white with 90% opacity

**Agent List:**
{self._format_agent_list(left_agents)}

**Agent Boxes:**
- Vertical stack, evenly spaced
- Rounded rectangles (8px radius)
- White background with subtle shadow
- Agent icon (left) + Name (center) + Description (right)
- Size: 480px wide × 80px tall
- Spacing: 20px between boxes

## RIGHT Hemisphere (Strategic Planning) - {len(right_agents)} Agents

**Background:** Subtle orange gradient (light to medium orange)
**Header:** "RIGHT BRAIN" - Bold, 28pt, white text, top of section
**Subheader:** "Strategic Planning" - Regular, 16pt, white with 90% opacity

**Agent List:**
{self._format_agent_list(right_agents)}

**Agent Boxes:** Same styling as LEFT hemisphere

## Corpus Callosum (Center Bridge)

**Position:** Vertical strip in center (80px wide)
**Color:** Gradient from blue (top) to orange (bottom)
**Label:** "Corpus Callosum" rotated 90° - Bold, 18pt, white
**Connectors:** 4-6 bidirectional arrows connecting both sides
**Symbol:** Bridge icon at center

## Agent Icons (Consistent Style)
## Agent Icons (Consistent Style)

**Style:** Flat design, outlined icons with 2px stroke, consistent size
**Color:** Match hemisphere color (blue for LEFT, orange for RIGHT)
**Size:** 40×40px per icon
**Position:** Left side of each agent box

**Icon Mappings:**
- Code Executor: `</>` code brackets icon
- Test Generator: ✓ checkmark in circle icon
- Error Corrector: 🔧 wrench icon
- Health Validator: ❤️ heartbeat/pulse icon  
- Commit Handler: Git branch symbol icon
- Intent Router: 🚦 traffic light icon
- Work Planner: 📋 clipboard/checklist icon
- Screenshot Analyzer: 📷 camera icon
- Change Governor: 🛡️ shield icon
- Brain Protector: 🔒 lock icon

## Typography

**Title:** "CORTEX Agent System" - Bold, 36pt, centered at top
**Hemisphere Headers:** Bold, 28pt, white
**Subheaders:** Regular, 16pt, white with 90% opacity
**Agent Names:** Bold, 18pt, dark gray (#374151)
**Agent Descriptions:** Regular, 12pt, medium gray (#6B7280)

## Visual Polish

**Shadows:** Subtle drop shadows on agent boxes (2px offset, 4px blur, 15% opacity)
**Borders:** None on agent boxes (clean flat design)
**Whitespace:** Generous padding (20px inside boxes, 40px margins)
**Alignment:** Perfect vertical alignment on both sides
**Balance:** Symmetrical layout, equal number of agents per side

**Background:** Clean white or very light gray (#FAFAFA)

**Overall Quality:**
- High contrast for readability
- Professional color harmony
- Balanced composition
- Conference presentation ready
- Print quality (300 DPI equivalent)

## Technical Accuracy

LEFT Brain (Execution):
- Precise, methodical, test-driven
- RED → GREEN → REFACTOR cycle
- Zero-tolerance for errors

RIGHT Brain (Strategy):
- Visionary, context-aware, holistic
- Breaks work into phases
- Protects architectural integrity

*Generated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        narrative = f"""# Agent System Narrative

## For Leadership

CORTEX uses a brain-inspired architecture with two specialized teams working together:

**LEFT Brain Team (Executors)** - Like skilled craftspeople, they implement features with precision. They write code, create tests, fix bugs, and ensure quality. Think "builders."

**RIGHT Brain Team (Strategists)** - Like architects and project managers, they plan work, analyze requirements, and protect project quality. Think "planners."

The **Corpus Callosum** is the communication bridge - LEFT brain executes RIGHT brain's plans, RIGHT brain learns from LEFT brain's results.

## For Developers

**Architecture Pattern:** Distributed agent system with hemisphere specialization

**Agent Responsibilities:**

LEFT Hemisphere (Tactical):
1. **Code Executor** - Implements features (TDD enforced)
2. **Test Generator** - Creates test suites (RED phase)
3. **Error Corrector** - Fixes bugs (learns from Tier 2)
4. **Health Validator** - Enforces DoD (zero errors/warnings)
5. **Commit Handler** - Creates semantic commits

RIGHT Hemisphere (Strategic):
1. **Intent Router** - Detects user intent (PLAN, EXECUTE, etc.)
2. **Work Planner** - Creates multi-phase roadmaps
3. **Screenshot Analyzer** - Extracts requirements from images
4. **Change Governor** - Protects architecture
5. **Brain Protector** - Enforces Rule #22 (challenge changes)

**Coordination:**
- Message-based (corpus-callosum/coordination-queue.jsonl)
- Asynchronous with acknowledgments
- Both hemispheres must agree on major actions

## Key Takeaways

1. **Separation of concerns** - Strategy vs execution
2. **Coordinated autonomy** - Agents collaborate but don't interfere
3. **Learning loop** - Execution results feed strategic planning
4. **Quality gates** - Multiple validation layers

## Usage Scenarios

**Scenario 1: Simple Request ("Add a button")**
1. RIGHT: Intent Router → EXECUTE detected
2. RIGHT: Routes to LEFT Code Executor
3. LEFT: Code Executor implements with TDD
4. LEFT: Health Validator checks quality
5. LEFT: Commit Handler saves work
6. RIGHT: Knowledge Graph learns pattern

**Scenario 2: Risky Request ("Delete brain data")**
1. RIGHT: Intent Router → PROTECT detected
2. RIGHT: Brain Protector challenges request
3. RIGHT: Offers safer alternatives
4. User approves alternative
5. LEFT: Executes safe cleanup

*Version: 1.0*  
*Last Updated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated {diagram_id} prompt and narrative")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png")
        }
    
    def _generate_plugin_architecture(self, plugins: List[Dict]) -> Dict[str, str]:
        """Generate Plugin Architecture diagram (1:1 square)."""
        diagram_id = "03-plugin-architecture"
        
        prompt = f"""# Diagram 03: CORTEX Plugin Architecture (Hub-and-Spoke)

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional hub-and-spoke architecture diagram showing CORTEX's extensible plugin system. Use modern flat design with radial symmetry and clean corporate aesthetic suitable for technical presentations.

## Design Requirements

**Style:** Professional hub-and-spoke infographic, modern flat design, radial layout, high-contrast colors, corporate presentation quality

**Canvas:** 1:1 square aspect ratio (2160×2160 pixels equivalent)

## Layout Structure

**Center Hub (CORTEX Core):**
- Position: Exact center of canvas
- Size: 400×400px circle
- Visual: Concentric rings showing tiers (4 rings)
- Background: White with subtle blue gradient
- Border: 4px solid {self.colors['tier1']} (blue)
- Shadow: 6px offset, 12px blur, 20% opacity

**Tier Rings (Inside Hub):**
- Tier 0 (innermost): 80px diameter, {self.colors['tier0']} fill
- Tier 1: 160px diameter, {self.colors['tier1']} fill, 70% opacity
- Tier 2: 240px diameter, {self.colors['tier2']} fill, 50% opacity
- Tier 3 (outermost): 320px diameter, {self.colors['tier3']} fill, 30% opacity

**Hub Center Label:**
- Text: "CORTEX CORE"
- Font: Bold, 24pt, white
- Position: Center of hub
- Subtext: "Brain + Agents" - Regular, 12pt, white with 80% opacity

**Plugins (Spokes - 8 total):**
{self._format_plugin_list(plugins)}

**Plugin Positioning:**
- Arranged in perfect circle around hub
- Distance from hub center: 800px radius
- Equal angular spacing: 45° apart (360° / 8 plugins)
- Starting position: Top (12 o'clock)
- Rotation: Clockwise

**Plugin Boxes:**
- Size: 280×120px rounded rectangles (16px radius)
- Background: White with subtle gradient
- Border: 3px solid {self.colors['tier2']} (emerald green)
- Shadow: 3px offset, 6px blur, 15% opacity
- Icon position: Left side (60×60px)
- Text position: Right side (name + description)

**Connection Lines (Spokes):**
- Style: 3px solid lines, {self.colors['tier2']} color
- Pattern: Dashed (8px dash, 6px gap)
- Start: Edge of hub circle
- End: Edge of plugin box (nearest point)
- Arrow: Small arrowhead at plugin end (12px)
- Label: "Plugin API" midway on line (10pt, gray)

## Plugin Icons & Details

**Icon Style:** 60×60px, flat design, outlined, {self.colors['tier2']} color

**Plugin 1 (Top - 0°):** Recommendation API
- Icon: ⭐ Star with sparkles
- Name: "Recommendation API" (Bold, 16pt)
- Description: "Code suggestions" (Regular, 11pt, gray)

**Plugin 2 (45°):** Platform Switch  
- Icon: 💻 Computer monitor
- Name: "Platform Switch" (Bold, 16pt)
- Description: "Cross-platform" (Regular, 11pt, gray)

**Plugin 3 (90°):** System Refactor
- Icon: ⚙️ Gear mechanism
- Name: "System Refactor" (Bold, 16pt)
- Description: "Code restructuring" (Regular, 11pt, gray)

**Plugin 4 (135°):** Doc Refresh
- Icon: 📄 Document with refresh symbol
- Name: "Doc Refresh" (Bold, 16pt)
- Description: "Auto documentation" (Regular, 11pt, gray)

**Plugin 5 (180° - Bottom):** Extension Scaffold
- Icon: 🧩 Puzzle piece
- Name: "Extension Scaffold" (Bold, 16pt)
- Description: "VS Code extensions" (Regular, 11pt, gray)

**Plugin 6 (225°):** Configuration Wizard
- Icon: 🪄 Magic wand with stars
- Name: "Config Wizard" (Bold, 16pt)
- Description: "Setup assistance" (Regular, 11pt, gray)

**Plugin 7 (270°):** Code Review
- Icon: 🔍 Magnifying glass
- Name: "Code Review" (Bold, 16pt)
- Description: "Quality analysis" (Regular, 11pt, gray)

**Plugin 8 (315°):** Cleanup
- Icon: 🧹 Broom
- Name: "Cleanup" (Bold, 16pt)
- Description: "Workspace maintenance" (Regular, 11pt, gray)

## Visual Hierarchy

**Title:** "CORTEX Plugin Architecture"
- Position: Top center, above diagram
- Font: Bold, 36pt, dark gray (#374151)

**Subtitle:** "Zero-Footprint Extensibility"
- Position: Below title
- Font: Regular, 18pt, medium gray (#6B7280)

**Legend Box:**
- Position: Bottom right corner
- Size: 300×180px, white with border
- Content:
  * Hub icon → "Core Brain (4 Tiers)"
  * Plugin icon → "Zero-Footprint Plugin"
  * Dashed line → "Plugin API Connection"
  * Note: "No external dependencies"

## Typography

**Plugin Names:** Bold, 16pt, dark gray (#374151)
**Descriptions:** Regular, 11pt, medium gray (#6B7280)
**Hub Label:** Bold, 24pt, white
**Title:** Bold, 36pt, dark gray
**Legend Text:** Regular, 12pt, dark gray

## Visual Polish

**Background:** Clean white or very light gray (#FAFAFA)
**Spacing:** 80px margin around canvas edges
**Alignment:** Perfect radial symmetry
**Shadows:** Subtle, consistent across all elements
**Contrast:** High readability for text
**Balance:** Even distribution of visual weight

**Overall Quality:**
- Professional hub-and-spoke layout
- Clear information hierarchy
- Balanced radial composition
- Conference presentation ready
- Print quality (300 DPI equivalent)

## Technical Accuracy

**Zero-Footprint Principle:**
- Plugins use CORTEX brain tiers (no external APIs)
- Tier 2 (Knowledge Graph) for learned patterns
- Tier 3 (Context Intelligence) for file analysis
- Natural language routing via Intent Router
- BasePlugin interface for consistency

**Plugin API:**
- get_natural_language_patterns() → trigger phrases
- execute(request, context) → main logic
- Access to brain tiers for intelligence

*Generated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        narrative = f"""# Plugin Architecture Narrative

## For Leadership

CORTEX is extensible - like installing apps on your phone. Plugins add specialized capabilities without changing the core system.

**Zero-Footprint Promise:** Plugins don't require external tools or cloud services. They use CORTEX's built-in intelligence (brain tiers).

**Example:** Recommendation API plugin suggests code improvements using patterns learned from past work (Tier 2) and file stability analysis (Tier 3). No external API needed.

## For Developers

**Architecture Pattern:** Hub-and-spoke with zero-footprint plugins

**Plugin Interface:**
```python
class BasePlugin:
    def get_natural_language_patterns(self) -> List[str]:
        # What phrases trigger this plugin?
        
    def execute(self, request, context) -> Dict:
        # Access CORTEX brain tiers
        patterns = self.knowledge_graph.search_patterns(request)
        stability = self.context_intelligence.get_file_stability(file)
        return results
```

**Available Plugins:**
{self._format_plugin_descriptions(plugins)}

**Registration:**
- Plugins register natural language triggers
- Intent Router matches user requests
- Plugin executes with full brain access
- Results integrate into conversation

## Key Takeaways

1. **Zero external dependencies** - All intelligence from CORTEX brain
2. **Natural language activation** - No special commands needed
3. **Full brain access** - Plugins leverage Tier 2 + Tier 3
4. **Seamless integration** - Results appear in normal conversation
5. **Easy development** - BasePlugin provides structure

## Usage Scenarios

**Scenario 1: Code Quality Analysis**
```
User: "recommend improvements"
→ Intent Router matches Recommendation API plugin
→ Plugin queries Tier 2 for similar code patterns
→ Plugin checks Tier 3 for file stability issues
→ Returns intelligent recommendations
```

**Scenario 2: Platform Adaptation**
```
User: "setup environment"
→ Platform Switch plugin auto-detects OS
→ Provides Mac/Windows/Linux-specific instructions
→ No user configuration needed
```

*Version: 1.0*  
*Last Updated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated {diagram_id} prompt and narrative")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png")
        }
    
    def _generate_memory_flow(self, tiers: List[Dict]) -> Dict[str, str]:
        """Generate Memory Flow diagram (16:9 landscape)."""
        diagram_id = "04-memory-flow"
        
        prompt = f"""# Diagram 04: CORTEX Memory Flow (Conversation → Knowledge)

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional left-to-right flow diagram showing CORTEX's 5-stage memory transformation pipeline. Use modern infographic style with clear progression and data flow visualization suitable for technical presentations.

## Design Requirements

**Style:** Professional process flow infographic, modern flat design, horizontal progression, clean arrows, corporate presentation quality

**Canvas:** 16:9 landscape aspect ratio (3840×2160 pixels equivalent)

## Flow Pipeline (5 Stages, Left to Right)

### Stage 1: User Conversation (Input)
**Position:** Far left (x: 300px from left edge)
**Visual:**
- Icon: 💬 Chat bubble (80×80px, outlined, {self.colors['tier1']})
- Box: 500×300px rounded rectangle (16px radius)
- Background: Light blue gradient (#E0F2FE to #BFDBFE)
- Border: 3px solid {self.colors['tier1']}
- Shadow: 3px offset, 6px blur, 15% opacity

**Content:**
- Title: "User Conversation" (Bold, 20pt, dark gray)
- Sample text (Speech bubble style):
  * "Add authentication to dashboard"
  * "Make the button purple"
  * "Fix null reference error"
- Timestamp: "Real-time" (Regular, 12pt, gray)

**Arrow to Stage 2:**
- 4px solid line, {self.colors['tier1']} color
- Length: 200px horizontal
- Label: "Capture" (14pt, gray, above arrow)
- Arrowhead: 20px triangle

### Stage 2: Tier 1 Capture (Working Memory)
**Position:** x: 1100px from left
**Visual:**
- Icon: 🗃️ Database cylinder (80×80px, {self.colors['tier1']})
- Box: 500×300px rounded rectangle (16px radius)
- Background: White with {self.colors['tier1']} 10% tint
- Border: 3px solid {self.colors['tier1']}
- Shadow: 3px offset, 6px blur, 15% opacity

**Content:**
- Title: "Tier 1 Storage" (Bold, 20pt)
- Description: "Last 20 conversations" (Regular, 14pt)
- Example data (Monospace, 11pt, light gray box):
  ```
  conversation_id: conv_20251116_143000
  user: "Add authentication..."
  entities: [dashboard, authentication]
  timestamp: 2025-11-16 14:30:00
  ```
- Capacity: "18/20 slots used" (12pt, gray)

**Arrow to Stage 3:**
- 4px solid line, gray color
- Length: 200px horizontal
- Label: "Extract" (14pt, gray, above arrow)
- Arrowhead: 20px triangle

### Stage 3: Pattern Extraction (Processing)
**Position:** x: 1900px from left
**Visual:**
- Icon: 🔄 Network graph (80×80px, outlined, gray)
- Box: 500×300px rounded rectangle (16px radius)
- Background: Light gray gradient (#F3F4F6 to #E5E7EB)
- Border: 3px dashed {self.colors['connections']}
- Shadow: 3px offset, 6px blur, 15% opacity

**Content:**
- Title: "Pattern Extraction" (Bold, 20pt)
- Processing indicators:
  * Intent detection → "EXECUTE"
  * Entity parsing → ["dashboard", "authentication"]
  * File identification → ["Dashboard.tsx"]
  * Relationship mapping → "UI + Auth"
- Processing time: "<50ms" (12pt, green checkmark)

**Arrow to Stage 4:**
- 4px solid line, {self.colors['tier2']} color
- Length: 200px horizontal
- Label: "Store" (14pt, gray, above arrow)
- Arrowhead: 20px triangle

### Stage 4: Tier 2 Storage (Knowledge Graph)
**Position:** x: 2700px from left
**Visual:**
- Icon: 🧩 Connected nodes (80×80px, {self.colors['tier2']})
- Box: 500×300px rounded rectangle (16px radius)
- Background: White with {self.colors['tier2']} 10% tint
- Border: 3px solid {self.colors['tier2']}
- Shadow: 3px offset, 6px blur, 15% opacity

**Content:**
- Title: "Tier 2 Knowledge" (Bold, 20pt)
- Description: "Patterns + Relationships" (Regular, 14pt)
- Learned patterns (Monospace, 11pt, light gray box):
  ```
  pattern: "feature_implementation"
  confidence: 0.88
  files: [Dashboard.tsx, AuthService.cs]
  success_rate: 0.94
  ```
- Pattern count: "34 patterns learned" (12pt, gray)

**Arrow to Stage 5:**
- 4px solid line, {self.colors['tier3']} color
- Length: 200px horizontal
- Label: "Analyze" (14pt, gray, above arrow)
- Arrowhead: 20px triangle

### Stage 5: Tier 3 Analytics (Intelligence)
**Position:** x: 3500px from left (far right)
**Visual:**
- Icon: 📊 Bar chart (80×80px, {self.colors['tier3']})
- Box: 500×300px rounded rectangle (16px radius)
- Background: White with {self.colors['tier3']} 10% tint
- Border: 3px solid {self.colors['tier3']}
- Shadow: 3px offset, 6px blur, 15% opacity

**Content:**
- Title: "Tier 3 Context" (Bold, 20pt)
- Description: "Project Health + Productivity" (Regular, 14pt)
- Analytics (Monospace, 11pt, light gray box):
  ```
  Dashboard.tsx:
    churn_rate: 0.28 (⚠️ unstable)
    changes: 67 (last 30 days)
    recommendation: "Add extra tests"
  ```
- Health score: "87% project health" (12pt, green)

## Visual Flow Indicators

**Overhead Title:**
- Text: "CORTEX Memory Flow Pipeline"
- Position: Top center (y: 100px from top)
- Font: Bold, 42pt, dark gray (#374151)

**Subtitle:**
- Text: "From Conversation to Intelligence in 5 Stages"
- Position: Below title (y: 160px from top)
- Font: Regular, 22pt, medium gray (#6B7280)

**Timeline Bar (Bottom):**
- Position: Bottom of canvas (y: 1950px from top)
- Width: Full width minus 200px margins
- Visual: Horizontal progress bar (10px height)
- Gradient: {self.colors['tier1']} → {self.colors['tier2']} → {self.colors['tier3']}
- Labels: "Input" (left) → "Processing" (center) → "Intelligence" (right)

## Typography

**Stage Titles:** Bold, 20pt, dark gray (#374151)
**Descriptions:** Regular, 14pt, medium gray (#6B7280)
**Example Code:** Monospace (Consolas), 11pt, dark gray
**Arrow Labels:** Regular, 14pt, medium gray
**Timestamps:** Regular, 12pt, light gray (#9CA3AF)

## Visual Polish

**Background:** Clean white or very light gray (#FAFAFA)
**Spacing:** 
- 200px horizontal between stages
- 60px vertical padding inside boxes
- 100px margins from canvas edges

**Shadows:** Subtle, consistent (3px offset, 6px blur, 15% opacity)
**Contrast:** High readability for all text
**Alignment:** Perfect horizontal alignment of stage boxes
**Balance:** Equal visual weight across all 5 stages

**Overall Quality:**
- Professional process flow layout
- Clear left-to-right progression
- Data transformation clearly visualized
- Conference presentation ready
- Print quality (300 DPI equivalent)

## Technical Accuracy

**Data Flow:**
1. User conversation → Tier 1 (captured in real-time)
2. Tier 1 → Pattern extraction (intent, entities, files)
3. Extraction → Tier 2 (stored as learned patterns)
4. Tier 2 → Tier 3 (enriched with git analysis)
5. Tier 3 → Proactive insights (warnings, recommendations)

**Performance:**
- Tier 1 query: <50ms (actual: 18ms avg)
- Pattern search: <150ms (actual: 92ms avg)
- Context analysis: <200ms (actual: 156ms avg)

*Generated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        narrative = f"""# Memory Flow Narrative

## For Leadership

This diagram shows CORTEX's "learning cycle" - how everyday conversations become long-term knowledge.

**Stage 1:** You have a conversation with Copilot  
**Stage 2:** CORTEX captures it (working memory)  
**Stage 3:** Extracts key information (what, why, how)  
**Stage 4:** Stores patterns (learning)  
**Stage 5:** Analyzes project health (intelligence)

**Real-World Analogy:** Like taking notes in a meeting (Stage 2), highlighting key points (Stage 3), filing them in a knowledge base (Stage 4), and updating project dashboards (Stage 5).

## For Developers

**Architecture Pattern:** ETL pipeline with progressive enrichment

**Pipeline Stages:**

1. **Capture (Tier 1)**
   - Raw conversation stored in SQLite
   - FIFO queue (oldest deleted at 21st conversation)
   - <30ms write latency

2. **Extraction (Processing Layer)**
   - Entity detection (files, classes, methods)
   - Intent classification (PLAN, EXECUTE, TEST, etc.)
   - Context enrichment (git branch, active files)

3. **Pattern Storage (Tier 2)**
   - Similar conversations clustered
   - Workflow templates extracted
   - File relationships updated
   - ~100ms processing time

4. **Analytics Update (Tier 3)**
   - File stability recalculated
   - Session productivity tracked
   - Git metrics refreshed
   - ~200ms analysis time

**Data Transformations:**

```
Raw conversation:
  "Add authentication to dashboard"

Entities extracted:
  {{
    "action": "add",
    "feature": "authentication",
    "location": "dashboard",
    "files": {{"["}}"Dashboard.tsx", "AuthService.ts"{{"]"}}
  }}

Intent detected:
  EXECUTE (confidence: 0.92)

Pattern matched:
  "feature_implementation" (similarity: 0.85)

Context updated:
  Dashboard.tsx churn_rate: 0.28 (warning threshold exceeded)
```

## Key Takeaways

1. **Automatic learning** - No manual knowledge capture
2. **Progressive enrichment** - More intelligence at each stage
3. **Fast processing** - <500ms total pipeline
4. **Quality improves over time** - More conversations = better patterns
5. **Privacy-preserving** - All local (no cloud)

## Usage Scenarios

**Scenario 1: First Week Using CORTEX**
- Tier 1: 5 conversations captured
- Tier 2: Basic patterns forming
- Tier 3: Analyzing git history only

**Scenario 2: After 3 Months**
- Tier 1: 20 conversations (FIFO limit)
- Tier 2: 150 patterns learned
- Tier 3: Productivity insights available
- CORTEX suggests proven workflows
- Warns about risky files proactively

*Version: 1.0*  
*Last Updated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated {diagram_id} prompt and narrative")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png")
        }
    
    def _generate_agent_coordination(self, agents: List[Dict]) -> Dict[str, str]:
        """Generate Agent Coordination sequence diagram (9:16 portrait)."""
        diagram_id = "05-agent-coordination"
        
        prompt = f"""# Diagram 05: CORTEX Agent Coordination (Multi-Agent Workflow)

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional vertical sequence diagram showing CORTEX's multi-agent collaboration workflow. Use modern UML-style swimlane format with clear temporal progression suitable for technical documentation.

## Design Requirements

**Style:** Professional sequence diagram with swimlanes, UML-inspired, modern flat design, clear temporal flow, corporate presentation quality

**Canvas:** 9:16 portrait aspect ratio (2160×3840 pixels equivalent)

## Swimlane Layout (4 Columns, Left to Right)

### Column 1: User (Width: 400px)
**Background:** Light gray (#F3F4F6)
**Header:** 
- Text: "USER" (Bold, 24pt, dark gray)
- Icon: 👤 User silhouette (40×40px)
- Height: 100px header bar

### Column 2: RIGHT Brain (Width: 600px)
**Background:** Light orange gradient (#FEF3C7 to #FDE68A)
**Header:**
- Text: "RIGHT BRAIN (Strategic)" (Bold, 24pt, white)
- Icon: 🧠 Brain icon (40×40px)
- Subtext: "Planning + Protection" (Regular, 14pt, white 80%)
- Height: 100px header bar
- Border: 3px solid {self.colors['right_brain']}

### Column 3: Corpus Callosum (Width: 300px)
**Background:** Vertical gradient (blue to orange)
**Header:**
- Text: "CORPUS CALLOSUM" (Bold, 20pt, white, rotated 90°)
- Icon: 🌉 Bridge (30×30px)
- Subtext: "Coordination" (Regular, 12pt, white)
- Height: 100px header bar

### Column 4: LEFT Brain (Width: 600px)
**Background:** Light blue gradient (#DBEAFE to #BFDBFE)
**Header:**
- Text: "LEFT BRAIN (Tactical)" (Bold, 24pt, white)
- Icon: ⚙️ Gear icon (40×40px)
- Subtext: "Execution + Testing" (Regular, 14pt, white 80%)
- Height: 100px header bar
- Border: 3px solid {self.colors['left_brain']}

## Workflow Sequence (Example: "Add Authentication")

**Vertical Timeline** (Top to Bottom, numbered steps)

### Step 1: User Request (y: 200px from top)
**User Column:**
- Speech bubble: 300×120px, white with shadow
- Text: "Add authentication to dashboard" (16pt)
- Icon: 💬 Chat bubble
- Timestamp: "14:30:00" (12pt, gray)

**Arrow:** Solid line (4px, blue) → RIGHT Brain (Intent Router)

### Step 2: Intent Detection (y: 400px)
**RIGHT Brain Column:**
- Box: "Intent Router" (500×100px, white, rounded)
- Icon: 🚦 (40×40px)
- Action: "Detects PLAN intent" (14pt)
- Details: "Confidence: 0.88" (12pt, monospace, gray box)

**Arrow:** Solid line (4px, orange) → RIGHT Brain (Work Planner)

### Step 3: Plan Creation (y: 600px)
**RIGHT Brain Column:**
- Box: "Work Planner" (500×100px, white, rounded)
- Icon: 📋 (40×40px)
- Action: "Creates 3-phase plan" (14pt)
- Details: "Phase 1: Tests | Phase 2: Impl | Phase 3: Validate" (11pt)

**Arrow:** Dashed line (4px, gray) → Corpus Callosum
**Label:** "Task Assignment" (12pt, above arrow)

### Step 4: Message Transfer (y: 800px)
**Corpus Callosum Column:**
- Box: "Message Queue" (250×100px, white, rounded)
- Icon: 📨 Envelope (40×40px)
- Text: "Queuing Phase 1 tasks..." (12pt)
- Status: "Ready" (12pt, green checkmark)

**Arrow:** Solid line (4px, blue) → LEFT Brain (Code Executor)

### Step 5: Test Creation (y: 1000px)
**LEFT Brain Column:**
- Box: "Test Generator" (500×100px, white, rounded)
- Icon: ✓ (40×40px)
- Action: "Create failing tests" (14pt)
- Details: "RED phase: 0/8 passing" (11pt, red text)

**Arrow:** Dashed line (4px, blue) → LEFT Brain (Code Executor)

### Step 6: Implementation (y: 1200px)
**LEFT Brain Column:**
- Box: "Code Executor" (500×100px, white, rounded)
- Icon: `</>` (40×40px)
- Action: "Implement AuthService" (14pt)
- Details: "TDD cycle enforced" (11pt)

**Arrow:** Solid line (4px, blue) → LEFT Brain (Code Executor - same agent)
**Label:** "Make tests pass" (12pt)

### Step 7: Tests Passing (y: 1400px)
**LEFT Brain Column:**
- Box: "Code Executor" (500×100px, white, rounded)
- Icon: `</>` (40×40px)
- Status: "GREEN phase: 8/8 passing ✅" (14pt, green)
- Details: "All tests pass" (11pt)

**Arrow:** Solid line (4px, blue) → LEFT Brain (Health Validator)

### Step 8: Validation (y: 1600px)
**LEFT Brain Column:**
- Box: "Health Validator" (500×100px, white, rounded)
- Icon: ❤️ (40×40px)
- Action: "Enforce Definition of Done" (14pt)
- Checks:
  * Tests: ✅ 8/8 passing
  * Errors: ✅ 0 found
  * Warnings: ✅ 0 found
  * Build: ✅ Success

**Arrow:** Dashed line (4px, gray) → Corpus Callosum
**Label:** "Completion Report" (12pt)

### Step 9: Knowledge Update (y: 1800px)
**Corpus Callosum:**
- Box: "Message Queue" (250×100px, white, rounded)
- Icon: 📨 (40×40px)
- Text: "Forwarding results..." (12pt)

**Arrow:** Solid line (4px, orange) → RIGHT Brain (Knowledge Graph)

### Step 10: Learning (y: 2000px)
**RIGHT Brain Column:**
- Box: "Knowledge Graph (Tier 2)" (500×120px, white, rounded)
- Icon: 🧩 (40×40px)
- Action: "Store workflow pattern" (14pt)
- Details:
  ```
  pattern: "authentication_workflow"
  confidence: 0.92
  success: true
  files: [AuthService.cs, AuthTests.cs]
  ```

**Arrow:** Dashed line (4px, orange) → User
**Label:** "Feature Complete" (12pt, green)

### Step 11: Confirmation (y: 2200px)
**User Column:**
- Notification: 300×100px, white with green border
- Icon: ✅ Checkmark (40×40px)
- Text: "Authentication feature ready!" (16pt)
- Subtext: "8 tests passing, 0 errors" (12pt, gray)

## Visual Elements

**Arrow Specifications:**
- Solid arrows: Requests/commands (4px thickness)
- Dashed arrows: Responses/results (4px thickness, 8px dash, 6px gap)
- Arrowheads: 15px triangles
- Colors: Blue (LEFT), Orange (RIGHT), Gray (Corpus)
- Labels: 12pt, centered above arrow

**Agent Boxes:**
- Size: 500×100px (brain agents), 300×100px (user/messages)
- Radius: 12px rounded corners
- Background: White with hemisphere-colored shadow
- Border: 2px solid (hemisphere color)
- Shadow: 2px offset, 4px blur, 15% opacity

**Timeline Indicator (Left Edge):**
- Vertical line: 2px solid gray, full height
- Time markers: Every 200px (T+0s, T+0.5s, T+1s, etc.)
- Labels: 10pt, gray

**Step Numbers (Left of Timeline):**
- Circles: 40×40px, {self.colors['tier1']} fill
- Numbers: Bold, 18pt, white
- Vertical spacing: Aligned with each workflow step

## Typography

**Swimlane Headers:** Bold, 24pt, white (or dark gray for User)
**Agent Names:** Bold, 16pt, dark gray (#374151)
**Actions:** Regular, 14pt, dark gray
**Details:** Monospace (Consolas), 11pt, medium gray (#6B7280)
**Timestamps:** Regular, 12pt, light gray (#9CA3AF)
**Arrow Labels:** Regular, 12pt, medium gray

## Visual Polish

**Background:** Clean white or very light gray (#FAFAFA)
**Spacing:**
- 200px vertical between workflow steps
- 40px padding inside agent boxes
- 100px margins from canvas edges

**Shadows:** Subtle, consistent (2px offset, 4px blur, 15% opacity)
**Contrast:** High readability for all text
**Alignment:** Perfect vertical alignment of sequence flow
**Balance:** Even distribution across swimlanes

**Overall Quality:**
- Professional UML sequence diagram style
- Clear temporal progression (top to bottom)
- Agent collaboration clearly visualized
- Conference presentation ready
- Print quality (300 DPI equivalent)

## Technical Accuracy

**Coordination Protocol:**
1. RIGHT Brain detects intent, creates strategy
2. Corpus Callosum delivers tasks via message queue
3. LEFT Brain executes with TDD enforcement
4. LEFT Brain validates quality (DoD)
5. Results flow back to RIGHT Brain for learning

**Performance:**
- Total workflow: <5 seconds (typical feature)
- Message passing: <10ms per transfer
- Validation: <150ms

**Multi-Agent Benefits:**
- Separation of concerns (strategy vs execution)
- Parallel processing where possible
- Quality gates at each stage
- Continuous learning loop

*Generated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        narrative = f"""# Agent Coordination Narrative

## For Leadership

This sequence diagram shows CORTEX agents working together like a well-orchestrated team.

**The Process:**
1. **You make a request** → Intent Router understands what you need
2. **Planner creates strategy** → Work Planner breaks work into phases
3. **Executors implement** → Code Executor + Test Generator work in tandem
4. **Validators verify quality** → Health Validator ensures standards met
5. **System learns** → Knowledge Graph captures patterns for future use

**Key Insight:** Multiple specialists collaborate automatically. You make one request, CORTEX coordinates 5-6 agents behind the scenes.

## For Developers

**Architecture Pattern:** Message-driven agent choreography

**Coordination Mechanism:**
- **Corpus Callosum** acts as message broker
- Agents communicate via coordination-queue.jsonl
- Asynchronous with acknowledgments
- No direct agent-to-agent coupling

**Example Workflow:**

```
User: "Add authentication to dashboard"

Step 1: Intent Router (RIGHT)
  ↓ message: {{"intent": "PLAN", "confidence": 0.88}}

Step 2: Work Planner (RIGHT)
  ↓ Creates 3-phase plan
  ↓ message: {{"phase": 1, "tasks": [...]}}

Step 3: Corpus Callosum
  ↓ Routes to LEFT hemisphere
  ↓ message: {{"target": "code-executor", "plan": ...}}

Step 4: Code Executor (LEFT)
  ↓ Requests test creation first (TDD)
  ↓ message: {{"action": "generate_tests", "feature": "auth"}}

Step 5: Test Generator (LEFT)
  ↓ Creates failing tests
  ↓ Tests: RED ❌ (expected)

Step 6: Code Executor (LEFT)
  ↓ Implements feature
  ↓ Tests: GREEN ✅

Step 7: Health Validator (LEFT)
  ↓ Validates DoD
  ↓ Result: PASS ✅

Step 8: Knowledge Graph (RIGHT)
  ↓ Stores "authentication_workflow" pattern
  ↓ Learning complete
```

**Message Structure:**
```json
{{
  "from": "work-planner",
  "to": "code-executor",
  "type": "task_assignment",
  "timestamp": "2025-11-16T10:30:00Z",
  "payload": {{
    "phase": 1,
    "tasks": ["Create AuthService", "Add login endpoint"],
    "success_criteria": ["All tests pass"]
  }}
}}
```

## Key Takeaways

1. **Asynchronous coordination** - Agents don't block each other
2. **Message-based** - Clear communication protocol
3. **Hemispheric separation** - Strategy (RIGHT) vs execution (LEFT)
4. **Learning loop** - Execution results inform future planning
5. **Quality gates** - Multiple validation checkpoints

## Usage Scenarios

**Scenario 1: Simple Feature**
- 3 agents involved (Router → Executor → Validator)
- ~1 second total time
- Minimal coordination overhead

**Scenario 2: Complex Feature (shown in diagram)**
- 6+ agents involved
- ~3 seconds total time
- Full planning and validation pipeline

**Scenario 3: Risky Change**
- Brain Protector intervenes early
- Challenges request before execution
- Saves wasted effort

*Version: 1.0*  
*Last Updated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated {diagram_id} prompt and narrative")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png")
        }
    
    def _generate_basement_scene(self) -> Dict[str, str]:
        """Generate Basement Scene (origin story) - Optional."""
        diagram_id = "06-basement-scene"
        
        prompt = f"""# Diagram 06: The Basement (Origin Story) [OPTIONAL]

**AI Generation Instructions for ChatGPT DALL-E:**

Create a warm, atmospheric illustration showing CORTEX's origin story - the moment of breakthrough. Use semi-realistic digital illustration style with cinematic lighting suitable for storytelling and humanizing technical content.

## Design Requirements

**Style:** Semi-realistic digital illustration, cinematic lighting, warm atmosphere, slightly whimsical but professional, developer-relatable scene

**Canvas:** 16:9 landscape aspect ratio (3840×2160 pixels equivalent)

**Mood:** Focused creativity, "eureka moment", late-night breakthrough, inviting workspace

## Scene Composition

### Central Figure: Asif "Codeinstein" Hussain
**Position:** Seated at desk, center-right of frame
**Character Design:**
- Age: Mid-30s, software developer aesthetic
- Hair: Slightly wild/Einstein-esque (creativity indicator)
- Expression: Focused concentration with slight smile (breakthrough moment)
- Clothing: Casual developer attire (hoodie or t-shirt)
- Posture: Leaning slightly forward, engaged with monitors
- Hand position: One hand on keyboard, one gesturing at whiteboard

**Lighting on Figure:**
- Key light: Cool blue glow from monitors (front)
- Fill light: Warm amber from desk lamp (side)
- Rim light: Subtle purple from whiteboard marker (back)

### Workspace Layout (Desk Area)

**Triple Monitor Setup:**
- **Left Monitor (30% of desk width):**
  * Display: GitHub Copilot Chat window
  * Content: Conversation bubbles visible
  * Text sample: "Make the button purple" (user), "Which button?" (Copilot) - showing amnesia problem
  * Glow: Blue (#3B82F6)

- **Center Monitor (40% of desk width, slightly larger):**
  * Display: CORTEX architecture diagram
  * Content: 4-tier vertical boxes (Tier 0-3) with arrows
  * Colors: Purple, Blue, Green, Orange tiers visible
  * Glow: Multicolored (dominant blue-green)

- **Right Monitor (30% of desk width):**
  * Display: Test results terminal
  * Content: Green checkmarks, "834 tests passed ✅"
  * Text: "All validation checks: PASS"
  * Glow: Green (#10B981)

**Desk Items (Left to Right):**
1. Coffee mug (left edge) - Text: "I ❤️ GitHub Copilot"
2. Keyboard (illuminated backlight, blue LEDs)
3. Mouse (RGB lighting)
4. Rubber duck (yellow, debugging companion)
5. Notebook (open, handwritten notes visible)
6. Desk lamp (warm amber light, angled toward whiteboard)

### Background Elements

**Whiteboard (Left Side of Frame):**
- Size: 4×6 feet, mounted on wall
- Content: Hand-drawn CORTEX brain architecture
  * Title: "CORTEX" (large, hand-drawn letters)
  * Subtitle: "The Brain for Copilot"
  * Simple 4-tier diagram with boxes and arrows
  * Sticky notes attached: "Rule #22: Challenge brain changes", "TDD = RED → GREEN → REFACTOR"
  * Mathematical notation: SQLite + YAML symbols
  * Sketch of human brain for inspiration
- Marker: Purple dry-erase marker in tray
- Glow: Subtle purple LED strip along top edge

**Wall (Behind Desk):**
- Color: Dark gray (#374151) with subtle texture
- Decorations:
  * Framed quote: "Make it work, make it right, make it fast" - Kent Beck
  * CORTEX logo poster (small, upper left)
  * Technical diagrams/printouts pinned with thumbtacks
  * Bookshelf visible at edge with technical books
    - "Clean Code" by Robert Martin (spine visible)
    - "Design Patterns" by Gang of Four
    - "The Pragmatic Programmer"

**Window (Upper Right Corner):**
- Size: Small window showing night sky
- View: Dark blue night sky with stars, city lights distant
- Time indicator: Deep darkness = late night (2-3 AM)
- Reflection: Faint monitor glow visible on glass

**Floor:**
- Material: Dark hardwood or industrial concrete
- Details: Power cables, RGB light strips along baseboards
- Items: Backpack leaning against desk leg, water bottle

### Atmospheric Details

**Lighting Setup (Professional Cinematic):**
- **Primary Light:** Blue monitor glow (cool, intense, 60% brightness)
- **Secondary Light:** Amber desk lamp (warm, soft, 40% brightness)
- **Accent Lights:** 
  * Green test results monitor (subtle, 20% brightness)
  * Purple whiteboard LED (accent, 15% brightness)
  * RGB keyboard/mouse (multicolor, 10% brightness)
- **Ambient:** Very dark room, minimal overhead light
- **Contrast:** High contrast between lit areas and shadows

**Color Palette:**
- **Cool tones:** {self.colors['tier1']} (monitor blue), {self.colors['tier2']} (green accents)
- **Warm tones:** {self.colors['tier3']} (amber lamp), #FEF3C7 (paper/notes)
- **Accent:** {self.colors['tier0']} (purple whiteboard glow)
- **Neutrals:** #374151 (dark gray walls), #1F2937 (shadows)

**Visual Effects:**
- Monitor light spill on desk surface (realistic glow)
- Soft shadows behind monitors and objects
- Subtle lens flare from desk lamp
- Depth of field: Monitors sharp, background slightly soft
- Atmospheric glow around light sources

### Typography & Text Elements

**Whiteboard Text (Hand-Drawn Style):**
- "CORTEX" - Large, bold, hand-drawn letters (48pt equivalent)
- "The Brain for Copilot" - Smaller, 24pt equivalent
- "Tier 0-3" labels with arrows
- "November 2024" in corner (18pt, date stamp)

**Monitor Text (Digital Font):**
- Code samples: Monospace (Consolas), 12pt, high contrast
- Chat text: Sans-serif, 14pt, white on blue background
- Test results: Monospace, green on black terminal

**Desk Items:**
- Coffee mug: "I ❤️ GitHub Copilot" (printed, 10pt)
- Notebook: Handwritten code snippets (cursive/print mix)
- Books: Titles on spines (10-12pt, varied fonts)

### Easter Eggs (Optional Details)

**Subtle Storytelling Elements:**
1. **Whiteboard Post-its:**
   * Yellow: "Rule #22: Challenge brain changes"
   * Green: "TDD = RED → GREEN → REFACTOR"
   * Pink: "Zero errors, zero warnings"

2. **Desk Details:**
   * Rubber duck with tiny developer hat
   * Coffee mug ring stains (late-night work session)
   * Crumpled paper balls in trash (iteration)

3. **Monitor Reflections:**
   * Faint reflection of character in screens
   * Code visible in background windows

4. **Bookshelf Titles:**
   * "Clean Code" prominently visible
   * Other software engineering classics

## Composition & Framing

**Camera Angle:** Slightly elevated (15° above desk level), looking down
**Focal Point:** Character and center monitor (rule of thirds)
**Depth Layers:**
- Foreground: Desk items (sharp focus)
- Midground: Character and monitors (sharpest focus)
- Background: Whiteboard and wall (slightly soft)

**Aspect Ratio Utilization:**
- Left 40%: Whiteboard and wall decorations
- Center 40%: Character, desk, monitors (main focus)
- Right 20%: Window and bookshelf

## Visual Polish

**Technical Realism:**
- Accurate monitor bezels and stands
- Realistic keyboard layout (mechanical keyboard style)
- Proper cable management (some visible, some hidden)
- Authentic desk lamp design (adjustable arm)

**Artistic Quality:**
- Cinematic color grading (orange and teal tones)
- Professional illustration quality
- Attention to light reflection physics
- Subtle texture on surfaces (wood grain, fabric)

**Emotional Tone:**
- Inviting, not isolating
- Focused, not stressed
- Creative, not chaotic
- Professional, but relatable

**Overall Quality:**
- Semi-realistic digital illustration style
- Cinematic lighting and composition
- Conference presentation suitable
- High emotional engagement
- Print quality (300 DPI equivalent)

## Technical Accuracy

**CORTEX Timeline:**
- Origin: November 2024 (shown on whiteboard)
- Problem: Copilot amnesia (shown in chat window)
- Solution: 4-tier brain architecture (shown on center monitor)
- Validation: Test-driven development (shown on right monitor)

**Workspace Authenticity:**
- Real developer setup (triple monitors common)
- Late-night coding sessions (realistic scenario)
- Whiteboard brainstorming (standard practice)
- Coffee and rubber duck (developer culture)

**Story Elements:**
- Moment of breakthrough (character expression)
- Problem-solution visualization (monitors show both)
- Quality emphasis (test results visible)
- Creative process (sketches, notes, iteration artifacts)

## Usage Context

**Best for:**
- Origin story presentations
- Team culture demonstrations
- "About" page illustrations
- Developer blog posts
- Conference talk intros
- Humanizing technical content

**Skip for:**
- Pure technical documentation
- API references
- Enterprise sales materials (too casual)
- Formal architecture specs

*Generated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        narrative = f"""# Basement Scene Narrative

## For Leadership

This illustration captures the human story behind CORTEX - the late-night breakthrough moment in November 2024 when Asif "Codeinstein" Hussain solved the amnesia problem.

**The Problem:** GitHub Copilot is brilliant but forgets everything between conversations.

**The Solution:** Give Copilot a brain - a 4-tier memory system inspired by human neuroscience.

**Why This Matters:** CORTEX bridges brilliant AI capabilities with practical development assistance. It's about understanding what developers actually need.

## For Developers

**Origin Story:**

The "amnesia problem" was frustrating - Copilot couldn't remember conversations from earlier in the day. Asif realized Copilot needed layered memory like humans: short-term (Tier 1), long-term (Tier 2), contextual (Tier 3), and instinct (Tier 0).

**Development Journey:**
- Phase 0: Proof of concept (SQLite + YAML)
- Phase 1: 4-tier architecture
- Phase 2: 10 specialist agents
- Phase 3: Token optimization (97% reduction)
- CORTEX 2.0: Production release (November 2025)

## Key Takeaways

1. Human-centered design solving real developer pain
2. Neuroscience inspiration - brain architecture works
3. Pragmatic engineering - SQLite + YAML (simple, reliable)
4. Quality obsession - TDD, zero errors policy
5. Continuous improvement - CORTEX 3.0 planned

*Version: 1.0*  
*Last Updated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated {diagram_id} prompt and narrative (optional)")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png"),
            'optional': True
        }
    
    def _generate_one_pager(
        self,
        capabilities: Dict[str, Any],
        agents: List[Dict],
        plugins: List[Dict]
    ) -> Dict[str, str]:
        """Generate CORTEX One-Pager diagram (16:9 landscape, comprehensive)."""
        diagram_id = "07-cortex-one-pager"
        
        # Extract key data
        tiers = capabilities.get('tiers', [])
        
        prompt = f"""# Diagram 07: CORTEX One-Pager (Comprehensive Overview)

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional one-page infographic showing CORTEX's complete architecture, features, and value proposition. Use modern corporate presentation style with high information density, clear visual hierarchy, and executive-friendly design.

## Design Requirements

**Style:** Professional technical infographic, modern corporate design, high information density without clutter, executive presentation quality

**Canvas:** 16:9 landscape aspect ratio (3840×2160 pixels equivalent)

**Audience:** Technical decision-makers, team leads, executives evaluating CORTEX

## Header Section (Top 15% of Canvas)

**Position:** y: 0-320px from top, full width

**Title Block (Centered):**
- Main Title: "CORTEX" 
  * Font: Bold, 72pt, gradient fill ({self.colors['tier1']} to {self.colors['tier0']})
  * Position: Centered horizontally, y: 80px from top
  
- Tagline: "Memory & Intelligence System for GitHub Copilot"
  * Font: Regular, 28pt, medium gray (#6B7280)
  * Position: Below title, y: 180px from top

- Version Badge:
  * Text: "v2.0 Production Ready"
  * Style: Rounded pill (120px × 40px), white border, {self.colors['tier2']} fill
  * Position: Top right corner (x: 3600px, y: 60px)

**Quick Stats Bar (Below Tagline):**
- Position: y: 240px from top, centered
- 4 metrics in horizontal row, 200px spacing

**Metric 1:** 97.2% Token Reduction
- Icon: ⚡ Lightning (40×40px, {self.colors['tier3']})
- Number: "97.2%" (Bold, 32pt)
- Label: "Token Reduction" (Regular, 16pt, gray)

**Metric 2:** 93.4% Cost Savings
- Icon: 💰 Dollar sign (40×40px, {self.colors['tier2']})
- Number: "93.4%" (Bold, 32pt)
- Label: "Cost Savings" (Regular, 16pt, gray)

**Metric 3:** <500ms Latency
- Icon: 🚀 Rocket (40×40px, {self.colors['tier1']})
- Number: "<500ms" (Bold, 32pt)
- Label: "Response Time" (Regular, 16pt, gray)

**Metric 4:** 100% Test Pass
- Icon: ✅ Checkmark (40×40px, {self.colors['tier2']})
- Number: "100%" (Bold, 32pt)
- Label: "Tests Passing" (Regular, 16pt, gray)

## Main Content Area (3-Column Layout)

**Position:** y: 380px to 2000px (vertical space)
**Layout:** 3 equal columns (1180px width each), 80px gutters

### LEFT Column: 4-Tier Brain Architecture

**Column Header:**
- Text: "🧠 Brain Architecture" (Bold, 32pt, {self.colors['tier1']})
- Position: Top of column (y: 400px)

**Tier Stack (Vertical, Bottom-Up):**

**Tier 3: Context Intelligence (Bottom)**
- Position: y: 1800px
- Box: 1100×280px, rounded (16px), gradient background ({self.colors['tier3']} 20% tint)
- Border: 4px solid {self.colors['tier3']}
- Icon: 📊 Bar chart (60×60px, {self.colors['tier3']})
- Title: "TIER 3: Context Intelligence" (Bold, 24pt)
- Content:
  * "Git Analysis (30 days)" (16pt)
  * "File Stability Tracking" (16pt)
  * "Code Health Metrics" (16pt)
  * "Session Analytics" (16pt)
- Storage: "context-intelligence.db" (14pt, monospace, gray box)

**Tier 2: Knowledge Graph (Middle-Bottom)**
- Position: y: 1450px
- Box: 1100×280px, rounded (16px), gradient background ({self.colors['tier2']} 20% tint)
- Border: 4px solid {self.colors['tier2']}
- Icon: 🧩 Puzzle pieces (60×60px, {self.colors['tier2']})
- Title: "TIER 2: Knowledge Graph" (Bold, 24pt)
- Content:
  * "Pattern Learning" (16pt)
  * "File Relationships" (16pt)
  * "Workflow Templates" (16pt)
  * "Intent Patterns" (16pt)
- Storage: "knowledge-graph.db" (14pt, monospace, gray box)

**Tier 1: Working Memory (Middle-Top)**
- Position: y: 1100px
- Box: 1100×280px, rounded (16px), gradient background ({self.colors['tier1']} 20% tint)
- Border: 4px solid {self.colors['tier1']}
- Icon: 🗃️ Database (60×60px, {self.colors['tier1']})
- Title: "TIER 1: Working Memory" (Bold, 24pt)
- Content:
  * "Last 20 Conversations" (16pt)
  * "Entity Tracking" (16pt)
  * "Context Continuity" (16pt)
  * "FIFO Queue" (16pt)
- Storage: "conversations.db" (14pt, monospace, gray box)

**Tier 0: Governance (Top)**
- Position: y: 750px
- Box: 1100×280px, rounded (16px), gradient background ({self.colors['tier0']} 20% tint)
- Border: 4px solid {self.colors['tier0']}
- Icon: 🛡️ Shield (60×60px, {self.colors['tier0']})
- Title: "TIER 0: Instinct (Immutable)" (Bold, 24pt)
- Content:
  * "Test-Driven Development" (16pt)
  * "Definition of Ready/Done" (16pt)
  * "Brain Protection Rules" (16pt)
  * "SOLID Principles" (16pt)
- Storage: "brain-protection-rules.yaml" (14pt, monospace, gray box)

**Data Flow Arrows:**
- Vertical arrows between tiers (3px, gray, upward)
- Labels: "Data Flow ↑" (14pt, centered on arrows)

### CENTER Column: 10 Specialist Agents

**Column Header:**
- Text: "🤖 Dual-Hemisphere Agents" (Bold, 32pt, gray)
- Position: Top of column (y: 400px)

**Hemispheric Split:**

**LEFT Hemisphere Section (Top Half)**
- Background: Light blue tint (#E0F2FE), 1100×800px
- Border: 3px solid {self.colors['left_brain']}
- Header: "LEFT BRAIN: Tactical Execution" (Bold, 24pt, white on blue bar)
- Position: y: 500px

**5 LEFT Agents (Vertical Stack, 140px height each):**

1. **Code Executor** (y: 600px)
   - Icon: `</>` (40×40px, {self.colors['left_brain']})
   - Name: "Code Executor" (Bold, 18pt)
   - Role: "Implements with TDD" (14pt, gray)

2. **Test Generator** (y: 760px)
   - Icon: ✓ (40×40px, {self.colors['left_brain']})
   - Name: "Test Generator" (Bold, 18pt)
   - Role: "Creates test suites (RED)" (14pt, gray)

3. **Error Corrector** (y: 920px)
   - Icon: 🔧 (40×40px, {self.colors['left_brain']})
   - Name: "Error Corrector" (Bold, 18pt)
   - Role: "Fixes bugs, learns" (14pt, gray)

4. **Health Validator** (y: 1080px)
   - Icon: ❤️ (40×40px, {self.colors['left_brain']})
   - Name: "Health Validator" (Bold, 18pt)
   - Role: "Enforces DoD (0 errors)" (14pt, gray)

5. **Commit Handler** (y: 1240px)
   - Icon: 🌿 (40×40px, {self.colors['left_brain']})
   - Name: "Commit Handler" (Bold, 18pt)
   - Role: "Semantic commits" (14pt, gray)

**Corpus Callosum (Center Strip)**
- Position: y: 1360px, centered horizontally in column
- Box: 1100×100px, horizontal gradient (blue to orange)
- Icon: 🌉 Bridge (40×40px, white)
- Text: "Corpus Callosum - Coordination Bridge" (Bold, 20pt, white, centered)

**RIGHT Hemisphere Section (Bottom Half)**
- Background: Light orange tint (#FEF3C7), 1100×800px
- Border: 3px solid {self.colors['right_brain']}
- Header: "RIGHT BRAIN: Strategic Planning" (Bold, 24pt, white on orange bar)
- Position: y: 1500px

**5 RIGHT Agents (Vertical Stack, 140px height each):**

1. **Intent Router** (y: 1600px)
   - Icon: 🚦 (40×40px, {self.colors['right_brain']})
   - Name: "Intent Router" (Bold, 18pt)
   - Role: "Detects user intent" (14pt, gray)

2. **Work Planner** (y: 1760px)
   - Icon: 📋 (40×40px, {self.colors['right_brain']})
   - Name: "Work Planner" (Bold, 18pt)
   - Role: "Creates multi-phase plans" (14pt, gray)

3. **Screenshot Analyzer** (y: 1920px)
   - Icon: 📷 (40×40px, {self.colors['right_brain']})
   - Name: "Screenshot Analyzer" (Bold, 18pt)
   - Role: "Extracts UI requirements" (14pt, gray)

4. **Change Governor** (y: 2080px)
   - Icon: 🛡️ (40×40px, {self.colors['right_brain']})
   - Name: "Change Governor" (Bold, 18pt)
   - Role: "Protects architecture" (14pt, gray)

5. **Brain Protector** (y: 2240px)
   - Icon: 🔒 (40×40px, {self.colors['right_brain']})
   - Name: "Brain Protector" (Bold, 18pt)
   - Role: "Enforces Rule #22" (14pt, gray)

### RIGHT Column: Features & Capabilities

**Column Header:**
- Text: "⚡ Features & Value" (Bold, 32pt, {self.colors['tier3']})
- Position: Top of column (y: 400px)

**Feature Section 1: Zero-Footprint Plugins (y: 500-900px)**

**Subheader:**
- Text: "Zero-Footprint Plugins" (Bold, 24pt)
- Icon: 🧩 Puzzle piece (40×40px)

**Plugin Grid (2×4, circular arrangement):**
- 8 plugin boxes (200×100px each), 40px spacing

**Plugins:**
1. **Recommendation API** - Icon: ⭐ Star
2. **Platform Switch** - Icon: 💻 Computer
3. **System Refactor** - Icon: ⚙️ Gear
4. **Doc Refresh** - Icon: 📄 Document
5. **Extension Scaffold** - Icon: 🧩 Puzzle
6. **Config Wizard** - Icon: 🪄 Wand
7. **Code Review** - Icon: 🔍 Magnifying glass
8. **Cleanup** - Icon: 🧹 Broom

**Plugin Note:**
- Text box (1000×80px, light gray, rounded)
- Text: "No external dependencies - Uses CORTEX brain (Tier 2/3)"
- Icon: ✅ Checkmark
- Font: 14pt, italic

**Feature Section 2: Key Capabilities (y: 980-1400px)**

**Subheader:**
- Text: "Core Capabilities" (Bold, 24pt)
- Icon: 🎯 Target (40×40px)

**Capability List (4 items, vertical):**

1. **Natural Language Interface**
   - Icon: 💬 Chat (30×30px)
   - Text: "No slash commands - Just tell CORTEX what you need" (16pt)

2. **Test-Driven Development**
   - Icon: 🔄 Cycle (30×30px)
   - Text: "Enforced RED → GREEN → REFACTOR workflow" (16pt)

3. **Brain Protection**
   - Icon: 🛡️ Shield (30×30px)
   - Text: "Rule #22: Challenge risky changes to core" (16pt)

4. **Continuous Learning**
   - Icon: 📈 Chart up (30×30px)
   - Text: "Gets smarter with every project" (16pt)

**Feature Section 3: Technical Stats (y: 1480-1900px)**

**Subheader:**
- Text: "Performance & Quality" (Bold, 24pt)
- Icon: 📊 Chart (40×40px)

**Stat Grid (2×3):**

**Row 1:**
- **Tests:** "834 tests | 100% pass" (Bold, 18pt, green checkmark)
- **Coverage:** "627/834 modules" (Bold, 18pt, green)

**Row 2:**
- **Latency:** "<500ms pipeline" (Bold, 18pt, blue)
- **Storage:** "SQLite + YAML" (Bold, 18pt, gray)

**Row 3:**
- **Token Reduction:** "97.2% optimized" (Bold, 18pt, orange)
- **Cost Savings:** "93.4% reduced" (Bold, 18pt, green)

**Feature Section 4: Quick Start (y: 1980-2100px)**

**Subheader:**
- Text: "Get Started" (Bold, 24pt)
- Icon: 🚀 Rocket (40×40px)

**Quick Start Box:**
- Background: Light blue gradient, rounded (16px)
- Border: 3px solid {self.colors['tier1']}
- Content (Monospace, 14pt):
  ```
  # Install CORTEX
  python setup.py install
  
  # Start using (no commands!)
  "Add authentication feature"
  "Test the login system"
  "Show project health"
  ```
- Note: "Natural language only" (12pt, italic, gray)

## Footer Section (Bottom 10% of Canvas)

**Position:** y: 2150px to 2160px (bottom 10px bar)

**Left Side:**
- Text: "© 2024-2025 Asif Hussain | github.com/asifhussain60/CORTEX"
- Font: Regular, 12pt, white on {self.colors['tier0']} background

**Center:**
- Logo: CORTEX icon (30×30px, white)

**Right Side:**
- Text: "v2.0 Production | Last Updated: November 2025"
- Font: Regular, 12pt, white

## Visual Polish

**Typography:**
- Headers: Bold, 24-32pt, color-coded by section
- Body: Regular, 14-16pt, dark gray (#374151)
- Labels: Regular, 12-14pt, medium gray (#6B7280)
- Code: Monospace (Consolas), 12pt, dark gray on light gray box

**Spacing:**
- Column gutters: 80px
- Section spacing: 40px vertical
- Item spacing: 20px within sections
- Margins: 60px from canvas edges

**Visual Effects:**
- Subtle gradients on tier boxes (10-20% opacity)
- Drop shadows: 2px offset, 4px blur, 10% opacity
- Borders: 3-4px solid, color-coded
- Icon glows: Subtle glow matching section color

**Background:**
- Base: Clean white (#FFFFFF)
- Gradient overlay: Very subtle radial gradient (white center to #F9FAFB edges)

**Overall Quality:**
- High information density without clutter
- Clear visual hierarchy (size, color, position)
- Professional corporate infographic style
- Executive presentation ready
- Conference poster quality
- Print quality (300 DPI equivalent)

## Technical Accuracy

**Complete System Overview:**
- 4-tier brain architecture (Tier 0-3)
- 10 specialist agents (5 LEFT, 5 RIGHT)
- 8 zero-footprint plugins
- Performance metrics validated
- Natural language interface emphasized
- Test-driven development enforced
- Brain protection active (Rule #22)

**Value Proposition Clear:**
- Solves Copilot amnesia problem
- No external dependencies
- Production-ready quality
- Continuous learning system
- Cost-effective (93.4% savings)
- Fast (<500ms response)

*Generated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        narrative = f"""# One-Pager Narrative
- Tier 0: #6B46C1 (Deep Purple)
- Tier 1: #3B82F6 (Bright Blue)
- Tier 2: #10B981 (Emerald Green)
- Tier 3: #F59E0B (Warm Orange)
- LEFT Brain: #3B82F6 (Cool Blue)
- RIGHT Brain: #F59E0B (Warm Orange)
- Background: White or light gradient
- Accents: #6B7280 (Gray)

**Typography:**
- Main title: "CORTEX" - Bold, 32pt, centered at top
- Subtitle: "Memory & Intelligence for GitHub Copilot" - 16pt
- Section headers: Bold, 18pt
- Body text: Regular, 12pt
- Metrics/badges: Bold, 14pt

**Icons & Graphics:**
- Consistent icon style (outlined or flat)
- Size: 24x24px minimum
- Color-matched to sections
- Professional, recognizable symbols

**Layout Grid:**
- 3-column layout (Brain | Agents | Features)
- Consistent spacing: 30px gutters
- Margins: 40px from edges
- Alignment: Grid-based, clean lines

**Badges/Metrics:**
- Rounded rectangles with gradient fills
- Icon + number + label format
- Examples:
  * "97.2% Token Reduction"
  * "93.4% Cost Savings"
  * "<500ms Latency"
  * "100% Tests Pass"

## Content Details

**Title Section (Top):**
```
CORTEX
Memory & Intelligence for GitHub Copilot
```

**Left Column - Brain Architecture:**
```
4-Tier Brain System
↑ Tier 3: Context Intelligence (Analytics)
↑ Tier 2: Knowledge Graph (Patterns)
↑ Tier 1: Working Memory (Last 20)
↑ Tier 0: Instinct (Governance)
```

**Center Column - Agents:**
```
10 Specialist Agents

LEFT Brain (Execution)     RIGHT Brain (Strategy)
• Code Executor           • Intent Router
• Test Generator          • Work Planner
• Error Corrector         • Screenshot Analyzer
• Health Validator        • Change Governor
• Commit Handler          • Brain Protector

         [Corpus Callosum Bridge]
```

**Right Column - Features:**
```
Zero-Footprint Plugins
[Plugin icons in circle: Recommendation, Platform Switch, 
 Refactor, Doc Refresh, Code Review, Config Wizard]

Performance Metrics
[97.2% Token Reduction] [93.4% Cost Savings]
[<500ms Latency] [100% Test Pass Rate]

Key Capabilities
✓ Natural language interface
✓ Test-driven development (TDD)
✓ Brain protection (Rule #22)
✓ Local-first (no cloud)
```

**Footer:**
```
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX
```

## Technical Specifications

**Resolution:**
- PNG, 3840x2160 pixels (4K landscape)
- 300 DPI for print quality
- Transparent or white background

**Aspect Ratio:** 16:9 (landscape orientation)

**File Size:** Target <5MB (PNG compression)

**Use Cases:**
- Executive presentations (print at 11"x17")
- README hero image
- Conference slides
- Documentation overview page
- Social media sharing (Twitter, LinkedIn)

## Technical Accuracy

**Brain Performance:**
- Tier 1: <50ms (18ms actual)
- Tier 2: <150ms (92ms actual)
- Tier 3: <200ms (156ms actual)

**Token Optimization:**
- Input: 74,047 → 2,078 tokens (97.2% reduction)
- Cost: $0.00074 → $0.00005 per request (93.4% savings)

**Quality Metrics:**
- 834 tests total
- 100% pass rate (0 failures)
- Zero errors, zero warnings policy

**Architecture:**
- 4 tiers: Tier 0-3 (Instinct → Context)
- 10 agents: 5 LEFT (execution) + 5 RIGHT (strategy)
- 8+ plugins: Zero-footprint, brain-powered

*Generated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        narrative = f"""# CORTEX One-Pager Narrative

## For Leadership

This single-image overview captures everything CORTEX does at a glance.

**Three Pillars:**

1. **Brain Architecture (LEFT)** - Four-tier memory system inspired by human cognition
   - Tier 0: Core principles (never change)
   - Tier 1: Recent conversations (short-term memory)
   - Tier 2: Learned patterns (long-term learning)
   - Tier 3: Project intelligence (situational awareness)

2. **Agent System (CENTER)** - Ten specialists working in harmony
   - LEFT Brain: Executes work with precision (builders)
   - RIGHT Brain: Plans strategy and protects quality (architects)
   - Corpus Callosum: Coordinates collaboration

3. **Features & Results (RIGHT)** - Proven capabilities and metrics
   - Zero-footprint plugins (no external dependencies)
   - 97.2% token reduction (massive cost savings)
   - <500ms performance (lightning fast)
   - 100% test pass rate (production quality)

**The Value Proposition:**

CORTEX transforms GitHub Copilot from a brilliant amnesiac into an experienced teammate with memory, learning capabilities, and project awareness. Developers save time, reduce frustration, and deliver higher quality code.

**ROI Example:**
- Before: Repeat context every conversation (5-10 min/day wasted)
- After: Natural conversations with context continuity
- Cost savings: 93.4% reduction in token costs
- Time savings: ~40 hours/year per developer

## For Developers

**Architecture at a Glance:**

This diagram provides a complete system overview showing:

1. **Data Flow (LEFT → CENTER → RIGHT)**
   ```
   Conversations → Brain Tiers → Agent Processing → Results
   ```

2. **Component Relationships**
   - Brain tiers feed agent intelligence
   - Agents coordinate via corpus callosum
   - Plugins leverage brain intelligence
   - All components < 500ms end-to-end

3. **System Capabilities**
   - Natural language interface (no commands to memorize)
   - Test-driven development (RED → GREEN → REFACTOR)
   - Brain protection (immutable governance rules)
   - Local-first (SQLite + YAML, no cloud)

**Technical Depth:**

**Brain Storage:**
```
Tier 0: YAML files (immutable, version controlled)
Tier 1: conversations.db (SQLite, FIFO queue)
Tier 2: knowledge-graph.db (SQLite + FTS5)
Tier 3: context-intelligence.db (SQLite analytics)
```

**Agent Coordination:**
```
User Request
  ↓ Intent Router (RIGHT)
  ↓ Routes to appropriate agent
  ↓ Work Planner creates strategy (RIGHT)
  ↓ Corpus Callosum delivers tasks
  ↓ Code Executor implements (LEFT)
  ↓ Test Generator validates (LEFT)
  ↓ Health Validator checks quality (LEFT)
  ↓ Knowledge Graph learns (RIGHT)
  ↓ Complete
```

**Plugin Architecture:**
```python
class RecommendationAPIPlugin(BasePlugin):
    def execute(self, request, context):
        # Access brain intelligence
        patterns = tier2.search_patterns(request)
        stability = tier3.get_file_stability(file)
        # Generate recommendations
        return intelligent_suggestions
```

**Performance Benchmarks:**
- Intent detection: ~50ms
- Pattern search: 92ms (target <150ms) ⚡
- Context analysis: 156ms (target <200ms) ⚡
- Conversation capture: 18ms (target <50ms) ⚡
- End-to-end: <500ms total

**Cost Analysis:**
```
Before CORTEX:
  74,047 input tokens × $0.00001 × 1.0 = $0.00074

After CORTEX:
  2,078 input tokens × $0.00001 × 1.0 = $0.00002
  
Savings: 93.4% per request
Annual (1,000 requests/month): $8,636 saved
```

## Key Takeaways

1. **Comprehensive Overview** - One image captures entire system
2. **Three-part Structure** - Brain + Agents + Results
3. **Visual Hierarchy** - Clear information flow
4. **Metrics Highlighted** - Proven performance and savings
5. **Self-contained** - Understandable without additional context

## Usage Scenarios

**When to Use This Image:**

✅ **Executive Presentations**
- Print at 11"x17" for meetings
- High-level overview without technical depth
- Emphasizes ROI and proven results

✅ **Documentation Hero**
- README.md top image
- First thing users see
- Provides instant system understanding

✅ **Conference Slides**
- Technical architecture overview
- Self-explanatory for 30-second glance
- Works without speaker notes

✅ **Social Media**
- Twitter/LinkedIn sharing
- Eye-catching infographic style
- Drives to repository/documentation

✅ **Onboarding**
- New team member orientation
- System architecture introduction
- Reference during training

**When NOT to Use:**

❌ **Deep Technical Docs** - Too high-level, use detailed diagrams instead
❌ **API Reference** - Not suitable for code-level documentation
❌ **Debugging Guides** - Lacks operational detail

## Design Notes

**Information Density:**
- High but not overwhelming
- Each section tells complete story
- Visual flow guides eye left → right
- Color coding aids comprehension

**Accessibility:**
- Text legible at 50% zoom
- Icons distinct and recognizable
- Color-blind friendly (patterns + icons, not just color)
- Alt text: "CORTEX system architecture overview showing 4-tier brain, 10 specialist agents, and key performance metrics"

**Branding Consistency:**
- Uses official CORTEX color palette
- Typography matches documentation
- Icon style consistent throughout
- Professional, technical aesthetic

**Print Considerations:**
- 300 DPI ensures crisp printing
- 16:9 aspect fits standard presentation formats
- Colors calibrated for both screen and print
- White background reduces ink usage

*Version: 1.0*  
*Last Updated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        prompt_path = self.prompts_dir / f"{diagram_id}.md"
        narrative_path = self.narratives_dir / f"{diagram_id}.md"
        
        prompt_path.write_text(prompt, encoding='utf-8')
        narrative_path.write_text(narrative, encoding='utf-8')
        
        logger.info(f"Generated {diagram_id} prompt and narrative")
        
        return {
            'id': diagram_id,
            'prompt_path': str(prompt_path),
            'narrative_path': str(narrative_path),
            'generated_path': str(self.generated_dir / f"{diagram_id}-v1.png")
        }
    
    def _generate_readme(self):
        """Generate README with workflow instructions."""
        readme_content = f"""# CORTEX Diagram Generation Workflow

**Generated:** {datetime.now().strftime('%B %d, %Y, %I:%M %p')}

## Directory Structure

```
docs/diagrams/
├── prompts/           # AI generation prompts (INPUT)
│   ├── 01-tier-architecture.md
│   ├── 02-agent-system.md
│   ├── 03-plugin-architecture.md
│   ├── 04-memory-flow.md
│   ├── 05-agent-coordination.md
│   ├── 06-basement-scene.md
│   └── 07-cortex-one-pager.md
├── narratives/        # Human-readable explanations (CONTEXT)
│   ├── 01-tier-architecture.md
│   ├── 02-agent-system.md
│   └── ... (matching prompts)
├── generated/         # AI-generated images (OUTPUT)
│   ├── 01-tier-architecture-v1.png
│   ├── 02-agent-system-v1.png
│   └── ... (versions tracked)
└── README.md         # This file
```

## Workflow

### Step 1: Generate Prompts (AUTOMATED)
```bash
# Run EPM documentation generator
python scripts/generate_docs.py --profile comprehensive
# Image prompts generated automatically
```

### Step 2: Create Images (MANUAL - Use AI)

For each prompt file in `prompts/`:

1. **Open prompt file** (e.g., `prompts/01-tier-architecture.md`)
2. **Copy prompt content** (everything after "AI Generation Instructions")
3. **Paste into Gemini/ChatGPT:**
   - Gemini: https://gemini.google.com
   - ChatGPT: https://chat.openai.com (with DALL-E)
4. **Download generated image**
5. **Save to `generated/` directory:**
   - Naming: `##-diagram-name-v1.png`
   - Version tracking: v1, v2, v3 (for iterations)
6. **Repeat if quality issues:**
   - Tweak prompt if needed
   - Save as new version (v2)

### Step 3: Merge Images (AUTOMATED - GitHub Copilot)

```bash
# After images are in generated/ directory
# GitHub Copilot can automatically embed them in docs

# Example: In markdown file, reference:
![Tier Architecture](diagrams/generated/01-tier-architecture-v1.png)

# Copilot will:
# 1. Detect image path
# 2. Verify file exists
# 3. Insert proper markdown syntax
# 4. Suggest alt text from narrative
```

### Step 4: Review & Iterate

1. **Check image quality:**
   - Resolution (300 DPI minimum)
   - Color accuracy (use color picker)
   - Text legibility
   - Icon clarity

2. **Review narratives:**
   - Match image content
   - Technical accuracy
   - Clarity for audience

3. **Iterate if needed:**
   - Update prompt in `prompts/` directory
   - Regenerate image
   - Save as new version

## Diagram Specifications

| Diagram | ID | Aspect Ratio | Size | Priority |
|---------|----|--------------|----- |----------|
| Tier Architecture | 01 | 16:9 (landscape) | 3840x2160 | Critical |
| Agent System | 02 | 1:1 (square) | 2160x2160 | Critical |
| Plugin Architecture | 03 | 1:1 (square) | 2160x2160 | High |
| Memory Flow | 04 | 16:9 (landscape) | 3840x2160 | High |
| Agent Coordination | 05 | 9:16 (portrait) | 1620x2880 | Medium |
| Basement Scene | 06 | 16:9 (landscape) | 3840x2160 | Optional |
| CORTEX One-Pager | 07 | 16:9 (landscape) | 3840x2160 | Critical |

## Color Palette (Consistent Branding)

```yaml
Tier 0 (Instinct):    #6B46C1  (Deep Purple)
Tier 1 (Memory):      #3B82F6  (Bright Blue)
Tier 2 (Knowledge):   #10B981  (Emerald Green)
Tier 3 (Context):     #F59E0B  (Warm Orange)
LEFT Brain:           #3B82F6  (Cool Blue)
RIGHT Brain:          #F59E0B  (Warm Orange)
Connections:          #6B7280  (Gray)
```

## Quality Checklist

Before finalizing each diagram:

- [ ] Resolution: 300 DPI minimum
- [ ] Colors match palette (use color picker)
- [ ] Text is legible at 50% zoom
- [ ] Icons are distinct and recognizable
- [ ] Layout follows prompt specifications
- [ ] Aspect ratio correct
- [ ] File size reasonable (<5MB per PNG)
- [ ] Narrative matches image content
- [ ] Technical accuracy verified
- [ ] Appropriate for target audience

## Troubleshooting

**Issue: AI-generated image doesn't match prompt**
- Solution: Refine prompt with more specific instructions
- Try different AI (Gemini vs ChatGPT)
- Iterate 2-3 times for best results

**Issue: Colors don't match palette**
- Solution: Specify exact hex codes in prompt
- Use "Color: #RRGGBB" format explicitly
- May need post-processing in image editor

**Issue: Text unreadable**
- Solution: Request larger font sizes
- Increase canvas size (e.g., 4K → 8K)
- Simplify diagram (fewer elements)

**Issue: Layout wrong (portrait vs landscape)**
- Solution: Explicitly state aspect ratio in prompt
- Use canvas size examples (3840x2160 = 16:9)
- Specify orientation ("landscape" or "portrait")

## Next Steps

1. ✅ Prompts generated (automated by EPM)
2. ⏳ Create images using AI (manual, ~30 min per diagram)
3. ⏳ Save to `generated/` directory
4. ⏳ Review quality against checklist
5. ⏳ Iterate if needed (v2, v3)
6. ⏳ Embed in documentation (Copilot-assisted)
7. ⏳ Publish to MkDocs site

**Estimated Total Time:** 4-5 hours for all 7 diagrams

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Version:** 1.0  
**Last Updated:** {datetime.now().strftime('%B %d, %Y')}
"""
        
        readme_path = self.output_dir / 'README.md'
        readme_path.write_text(readme_content, encoding='utf-8')
        logger.info(f"Generated workflow README at {readme_path}")
    
    def _generate_style_guide(self):
        """Generate comprehensive style guide document."""
        style_guide_content = f"""# CORTEX Visual Style Guide

**Version:** 1.0  
**Generated:** {datetime.now().strftime('%B %d, %Y')}

## Color Palette

### Primary Colors (Tiers)

| Tier | Color Name | Hex Code | RGB | Usage |
|------|-----------|----------|-----|-------|
| Tier 0 | Deep Purple | `#6B46C1` | rgb(107, 70, 193) | Instinct/Governance |
| Tier 1 | Bright Blue | `#3B82F6` | rgb(59, 130, 246) | Working Memory |
| Tier 2 | Emerald Green | `#10B981` | rgb(16, 185, 129) | Knowledge Graph |
| Tier 3 | Warm Orange | `#F59E0B` | rgb(245, 158, 11) | Context Intelligence |

### Secondary Colors (Agents)

| Element | Color Name | Hex Code | Usage |
|---------|-----------|----------|-------|
| LEFT Brain | Cool Blue | `#3B82F6` | Execution agents |
| RIGHT Brain | Warm Orange | `#F59E0B` | Strategy agents |
| Connections | Gray | `#6B7280` | Arrows, links |
| Background | White/Light Gray | `#FFFFFF` / `#F9FAFB` | Canvas |

## Typography

### Font Families

**Primary Font:** Inter, system-ui, sans-serif
**Monospace Font:** 'Courier New', Consolas, monospace

### Font Sizes

| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| Diagram Titles | 24pt | Bold | Main diagram heading |
| Section Headers | 18pt | Bold | Tier names, agent groups |
| Body Text | 14pt | Regular | Labels, descriptions |
| Small Text | 11pt | Regular | Annotations, metadata |
| Code Samples | 12pt | Regular | Monospace code |

### Text Contrast

- Dark text on light backgrounds: Minimum contrast ratio 4.5:1
- Light text on dark backgrounds: Minimum contrast ratio 7:1
- Use color picker to verify accessibility

## Layout Principles

### Spacing

- **Margin:** 40px minimum from canvas edge
- **Padding:** 20px inside boxes/containers
- **Gap:** 30px between major elements
- **Line spacing:** 1.5x for readability

### Alignment

- **Left-align:** Text within boxes
- **Center-align:** Diagram titles
- **Consistent:** Grid-based alignment for elements

### Visual Hierarchy

1. **Primary:** Main diagram elements (tiers, agents)
2. **Secondary:** Connecting arrows, relationships
3. **Tertiary:** Labels, annotations
4. **Quaternary:** Metadata, timestamps

## Iconography

### Standard Icons

| Concept | Icon | Unicode | Usage |
|---------|------|---------|-------|
| Database | 🗄️ | U+1F5C4 | Tier 1 storage |
| Network | 🔗 | U+1F517 | Tier 2 relationships |
| Analytics | 📊 | U+1F4CA | Tier 3 metrics |
| Shield | 🛡️ | U+1F6E1 | Tier 0 protection |
| Code | 💻 | U+1F4BB | Code Executor |
| Test | ✅ | U+2705 | Test Generator |
| Wrench | 🔧 | U+1F527 | Error Corrector |
| Heart | ❤️ | U+2764 | Health Validator |
| Git | 🌿 | U+1F33F | Commit Handler |

### Icon Guidelines

- **Size:** 32x32px minimum
- **Style:** Outlined or flat (consistent within diagram)
- **Color:** Match element color or neutral gray
- **Placement:** Top-left or center of container

## Diagram Types

### 1. Architecture Diagrams (Vertical Stacks)

**Best for:** Tier architecture, layered systems

**Layout:**
- Vertical orientation (bottom to top)
- Boxes with rounded corners (8px radius)
- Upward arrows showing data flow
- Legend in bottom-right corner

**Aspect Ratio:** 16:9 (landscape)

### 2. Agent System Diagrams (Dual Hemispheres)

**Best for:** LEFT/RIGHT brain agents, coordination

**Layout:**
- Split canvas vertically (LEFT | RIGHT)
- Color-coded hemispheres
- Central bridge (Corpus Callosum)
- Agents in vertical lists

**Aspect Ratio:** 1:1 (square)

### 3. Flow Diagrams (Left-to-Right)

**Best for:** Process flows, transformations

**Layout:**
- Horizontal orientation (left to right)
- Stages as boxes
- Arrows showing progression
- Example data at each stage

**Aspect Ratio:** 16:9 (landscape)

### 4. Sequence Diagrams (Top-to-Bottom)

**Best for:** Multi-agent workflows, time sequences

**Layout:**
- Vertical swimlanes
- Time flows downward
- Messages as horizontal arrows
- Step numbers in circles

**Aspect Ratio:** 9:16 (portrait)

## Technical Specifications

### Resolution

- **Minimum:** 300 DPI for print quality
- **Recommended:** 3840x2160 (4K) for 16:9
- **Web:** 1920x1080 acceptable for online use

### File Formats

- **Primary:** PNG (lossless, transparency support)
- **Alternative:** SVG (vector, scalable)
- **Avoid:** JPEG (lossy compression)

### File Naming

Pattern: `##-diagram-name-vN.ext`

Examples:
- `01-tier-architecture-v1.png`
- `02-agent-system-v2.svg`
- `05-agent-coordination-v1.png`

### Version Control

- **v1:** Initial version
- **v2:** First revision
- **v3+:** Subsequent iterations
- Keep all versions (storage is cheap)

## Accessibility

### Color Blindness

- Don't rely solely on color to convey information
- Use patterns, textures, or icons as backups
- Test with color blindness simulators

### Screen Readers

- Provide alt text for all images
- Use descriptive filenames
- Include text transcripts in narratives

### Zoom/Magnification

- Text legible at 200% zoom
- Icons recognizable at 150% zoom
- Layout doesn't break at high zoom levels

## Examples

### Good Practices ✅

- Clear visual hierarchy
- Consistent color usage
- Readable text (legible at 50% zoom)
- Proper spacing (not cramped)
- Aligned to grid
- Appropriate aspect ratio

### Bad Practices ❌

- Inconsistent colors (random palette)
- Tiny unreadable text
- Cluttered layout (too many elements)
- Poor contrast (gray on white)
- Misaligned elements
- Wrong aspect ratio (stretched)

## Quality Checklist

Before finalizing any diagram:

- [ ] Colors match style guide palette
- [ ] Text is readable at 50% zoom
- [ ] Icons are distinct (32x32px minimum)
- [ ] Spacing is consistent (20-40px)
- [ ] Alignment follows grid
- [ ] Aspect ratio correct
- [ ] Resolution 300 DPI or higher
- [ ] File naming follows convention
- [ ] Alt text provided
- [ ] Narrative matches diagram

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Version:** 1.0  
**Last Updated:** {datetime.now().strftime('%B %d, %Y')}
"""
        
        style_guide_path = self.output_dir / 'STYLE-GUIDE.md'
        style_guide_path.write_text(style_guide_content, encoding='utf-8')
        logger.info(f"Generated style guide at {style_guide_path}")
    
    # Helper methods
    
    def _format_tier_list(self, tier_details: List[Dict]) -> str:
        """Format tier list for prompts."""
        lines = []
        for tier in tier_details:
            lines.append(
                f"**Tier {tier['id']}: {tier['name']}**\n"
                f"- Storage: {tier['storage']}\n"
                f"- Color: {tier['color']}"
            )
        return '\n\n'.join(lines)
    
    def _format_agent_list(self, agents: List[Dict]) -> str:
        """Format agent list for prompts."""
        lines = []
        for agent in agents:
            name = agent.get('name', 'Unknown')
            role = agent.get('role', 'N/A')
            lines.append(f"- **{name}**: {role}")
        return '\n'.join(lines)
    
    def _format_plugin_list(self, plugins: List[Dict]) -> str:
        """Format plugin list for prompts."""
        lines = []
        for i, plugin in enumerate(plugins, 1):
            name = plugin.get('name', 'Unknown')
            desc = plugin.get('description', 'N/A')
            lines.append(f"{i}. **{name}** - {desc}")
        return '\n'.join(lines)
    
    def _format_plugin_descriptions(self, plugins: List[Dict]) -> str:
        """Format plugin descriptions for narratives."""
        lines = []
        for plugin in plugins:
            name = plugin.get('name', 'Unknown')
            desc = plugin.get('description', 'N/A')
            lines.append(f"- **{name}:** {desc}")
        return '\n'.join(lines)
