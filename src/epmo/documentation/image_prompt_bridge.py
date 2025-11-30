"""
Image Prompt Integration Bridge for CORTEX EPM Documentation

Transforms AST parser and dependency mapper analysis data into inputs
for the EPM image prompt generation system. Creates seamless integration
between Feature 4 code analysis and visual diagram generation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - Part of CORTEX 3.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sys

# Add EPM modules path for ImagePromptGenerator import
sys.path.append(str(Path(__file__).parent.parent.parent / 'epm' / 'modules'))

try:
    from image_prompt_generator import ImagePromptGenerator
except ImportError:
    # Fallback if image_prompt_generator is not available
    ImagePromptGenerator = None
    logging.warning("ImagePromptGenerator not available - visual prompts will be limited")

from .models import (
    EPMDocumentationModel, ImagePrompt, FileAnalysis, ArchitectureMetrics,
    DependencyRelation, HealthMetrics
)

logger = logging.getLogger(__name__)


class ImagePromptIntegrationBridge:
    """
    Bridge between Feature 4 analysis data and EPM image prompt generation.
    
    Transforms code analysis results into structured inputs for AI image
    generation, enabling automatic creation of professional architectural
    visualizations from code structure.
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize integration bridge.
        
        Args:
            output_dir: Output directory for generated prompts (defaults to docs/diagrams)
        """
        self.output_dir = output_dir or Path("docs/diagrams")
        self.image_generator = None
        
        if ImagePromptGenerator:
            try:
                self.image_generator = ImagePromptGenerator(self.output_dir)
                logger.info("Image prompt generator initialized")
            except Exception as e:
                logger.warning(f"Could not initialize image generator: {e}")
    
    def generate_epmo_image_prompts(
        self,
        model: EPMDocumentationModel
    ) -> List[ImagePrompt]:
        """
        Generate image prompts for an EPMO from analysis data.
        
        Args:
            model: Complete EPM documentation model
            
        Returns:
            List of generated image prompts
        """
        logger.info(f"Generating image prompts for EPMO: {model.metadata.epmo_name}")
        
        image_prompts = []
        
        try:
            # Transform EPM model data to capabilities format
            capabilities_data = self._transform_to_capabilities_format(model)
            modules_data = self._transform_to_modules_format(model)
            
            # Generate system architecture prompt
            arch_prompt = self._generate_architecture_prompt(model, capabilities_data)
            if arch_prompt:
                image_prompts.append(arch_prompt)
            
            # Generate dependency visualization prompt
            if model.dependencies:
                dep_prompt = self._generate_dependency_visualization_prompt(model)
                if dep_prompt:
                    image_prompts.append(dep_prompt)
            
            # Generate health dashboard prompt
            if model.health:
                health_prompt = self._generate_health_dashboard_prompt(model)
                if health_prompt:
                    image_prompts.append(health_prompt)
            
            # Generate component overview prompt
            comp_prompt = self._generate_component_overview_prompt(model, modules_data)
            if comp_prompt:
                image_prompts.append(comp_prompt)
            
            # Use EPM image generator if available for additional prompts
            if self.image_generator and capabilities_data:
                try:
                    epm_results = self.image_generator.generate_all(capabilities_data, modules_data)
                    if epm_results.get('success'):
                        epm_prompts = self._convert_epm_results_to_image_prompts(epm_results)
                        image_prompts.extend(epm_prompts)
                except Exception as e:
                    logger.warning(f"EPM image generator error: {e}")
            
            logger.info(f"Generated {len(image_prompts)} image prompts")
            
        except Exception as e:
            logger.error(f"Error generating image prompts: {e}")
        
        return image_prompts
    
    def _transform_to_capabilities_format(self, model: EPMDocumentationModel) -> Dict[str, Any]:
        """Transform EPM model to capabilities format expected by image generator."""
        
        # Extract tier-like structure from file organization
        tiers = []
        file_groups = {}
        
        # Group files by directory structure
        for file_analysis in model.files:
            path_parts = Path(file_analysis.relative_path).parts
            if len(path_parts) > 1:
                tier_name = path_parts[0]
            else:
                tier_name = "core"
            
            if tier_name not in file_groups:
                file_groups[tier_name] = []
            file_groups[tier_name].append(file_analysis)
        
        # Convert file groups to tier structure
        tier_id = 0
        for tier_name, files in file_groups.items():
            tier_data = {
                'id': tier_id,
                'name': tier_name.title(),
                'storage_type': 'file_system',
                'description': f"Contains {len(files)} modules",
                'modules': [f.module_name for f in files]
            }
            tiers.append(tier_data)
            tier_id += 1
        
        # Create agents from classes (conceptual mapping)
        agents = []
        agent_id = 0
        for file_analysis in model.files[:10]:  # Limit to avoid too many agents
            for class_model in file_analysis.classes:
                if class_model.visibility == 'public':
                    agent_data = {
                        'id': agent_id,
                        'name': class_model.name,
                        'role': f"{file_analysis.module_name} component",
                        'responsibilities': [m.name for m in class_model.methods[:3]],
                        'hemisphere': 'left' if agent_id % 2 == 0 else 'right'
                    }
                    agents.append(agent_data)
                    agent_id += 1
        
        # Create plugins from external dependencies
        plugins = []
        if model.architecture and model.architecture.external_dependencies:
            for i, ext_dep in enumerate(model.architecture.external_dependencies[:5]):
                plugin_data = {
                    'id': i,
                    'name': ext_dep,
                    'type': 'external_dependency',
                    'integration_type': 'import'
                }
                plugins.append(plugin_data)
        
        return {
            'tiers': tiers,
            'agents': agents,
            'plugins': plugins,
            'system_name': model.metadata.epmo_name,
            'description': f"Entry Point Module with {len(model.files)} components"
        }
    
    def _transform_to_modules_format(self, model: EPMDocumentationModel) -> List[Dict[str, Any]]:
        """Transform file analysis data to modules format."""
        modules = []
        
        for file_analysis in model.files:
            module_data = {
                'name': file_analysis.module_name,
                'path': file_analysis.relative_path,
                'type': 'python_module',
                'classes': len(file_analysis.classes),
                'functions': len(file_analysis.functions),
                'lines': file_analysis.total_lines,
                'complexity': file_analysis.complexity_score,
                'imports': [imp.module for imp in file_analysis.imports]
            }
            modules.append(module_data)
        
        return modules
    
    def _generate_architecture_prompt(
        self,
        model: EPMDocumentationModel,
        capabilities_data: Dict[str, Any]
    ) -> Optional[ImagePrompt]:
        """Generate architecture overview image prompt."""
        
        total_components = len(model.files)
        external_deps = len(model.architecture.external_dependencies) if model.architecture else 0
        
        prompt_text = f"""
Create a professional software architecture diagram for '{model.metadata.epmo_name}' Entry Point Module.

**System Architecture:**
- Python-based Entry Point Module (EPMO)
- {total_components} core components/modules  
- {external_deps} external dependencies
- Object-oriented design with clear separation of concerns

**Visual Requirements:**
- Modern technical architecture style
- 16:9 landscape orientation 
- Clean component boxes with rounded corners
- Directional arrows showing data flow and dependencies
- Professional color scheme (blues, grays, accent colors)
- Clear typography for component names and relationships

**Components Layout:**
- Core modules as primary building blocks in center
- External dependencies as separate layer/border
- Clear hierarchy showing module relationships
- Data flow indicators between components
- Legend explaining connection types

**Style Guidelines:**
- Corporate presentation quality
- Technical documentation aesthetic
- High contrast for readability
- Professional spacing and alignment
- Modern flat design with subtle shadows
""".strip()
        
        return ImagePrompt(
            prompt_id=f"architecture_{model.metadata.epmo_name.lower().replace(' ', '_')}",
            title=f"{model.metadata.epmo_name} Architecture",
            prompt_text=prompt_text,
            style_guidance="Professional technical architecture diagram, corporate presentation style, modern and clean",
            aspect_ratio="16:9",
            complexity_level="medium",
            color_palette=["#3B82F6", "#10B981", "#F59E0B", "#6B7280", "#FFFFFF"],
            narrative_description=f"Comprehensive architecture overview of the {model.metadata.epmo_name} system showing component relationships and data flow patterns"
        )
    
    def _generate_dependency_visualization_prompt(
        self,
        model: EPMDocumentationModel
    ) -> Optional[ImagePrompt]:
        """Generate dependency network visualization prompt."""
        
        dep_count = len(model.dependencies)
        circular_deps = model.architecture.circular_dependencies if model.architecture else 0
        
        prompt_text = f"""
Create a network-style dependency visualization for '{model.metadata.epmo_name}' module relationships.

**Dependency Analysis:**
- {dep_count} total module dependencies
- {"⚠️ Circular dependencies detected" if circular_deps > 0 else "✅ Clean dependency structure"}
- Import relationships and module interconnections
- Dependency strength and relationship types

**Visual Design:**
- Network graph layout with nodes and edges
- Nodes represent modules (sized by complexity/importance)
- Edges represent dependencies (thickness = strength)
- Color coding for different relationship types:
  - Blue: Direct imports
  - Green: Inheritance relationships  
  - Orange: External dependencies
  - Red: Circular dependencies (if any)

**Layout Requirements:**
- 1:1 square format for balanced network view
- Central hub layout with core modules in center
- Peripheral modules around edges
- Clear directional indicators on edges
- Legend explaining node sizes and edge types

**Technical Style:**
- Network visualization aesthetic
- Clean modern design
- High contrast colors
- Professional technical documentation style
""".strip()
        
        return ImagePrompt(
            prompt_id=f"dependencies_{model.metadata.epmo_name.lower().replace(' ', '_')}",
            title=f"{model.metadata.epmo_name} Dependencies",
            prompt_text=prompt_text,
            style_guidance="Network graph visualization, technical and informative, clear relationship indicators",
            aspect_ratio="1:1",
            complexity_level="high",
            color_palette=["#6B46C1", "#3B82F6", "#10B981", "#F59E0B", "#EF4444"],
            narrative_description=f"Network visualization showing how modules in {model.metadata.epmo_name} interconnect and depend on each other"
        )
    
    def _generate_health_dashboard_prompt(
        self,
        model: EPMDocumentationModel
    ) -> Optional[ImagePrompt]:
        """Generate health dashboard visualization prompt."""
        
        if not model.health:
            return None
        
        health = model.health
        
        prompt_text = f"""
Create a software quality dashboard for '{model.metadata.epmo_name}' health metrics.

**Health Metrics:**
- Overall Score: {health.overall_score:.1f}/100
- Status: {health.health_status.title()}
- Issues Found: {health.issues_found}
- Auto-fixable: {health.auto_fixable_issues}
- Priority Issues: {health.priority_issues}

**Dashboard Elements:**
- Circular progress indicator for overall score
- Color-coded status (green=good, yellow=fair, red=poor)
- Issue breakdown with icons and counts
- Trend indicators and improvement suggestions
- Quality badges for different dimensions

**Visual Design:**
- Modern dashboard UI style
- 16:9 landscape layout
- Card-based information layout
- Clean typography and iconography
- Professional color scheme matching health status
- Data visualization elements (charts, gauges, progress bars)

**Content Organization:**
- Header with overall score and status
- Main metrics in prominent cards
- Issue breakdown in secondary section
- Recommendations or next steps area
- Clean spacing and visual hierarchy
""".strip()
        
        status_colors = {
            'excellent': ["#10B981", "#065F46"],
            'good': ["#3B82F6", "#1E40AF"], 
            'fair': ["#F59E0B", "#D97706"],
            'poor': ["#EF4444", "#DC2626"]
        }
        
        colors = status_colors.get(health.health_status, ["#6B7280", "#374151"])
        
        return ImagePrompt(
            prompt_id=f"health_{model.metadata.epmo_name.lower().replace(' ', '_')}",
            title=f"{model.metadata.epmo_name} Health Dashboard",
            prompt_text=prompt_text,
            style_guidance="Modern dashboard UI, professional metrics visualization, clean and informative",
            aspect_ratio="16:9",
            complexity_level="medium",
            color_palette=colors + ["#FFFFFF", "#F9FAFB", "#374151"],
            narrative_description=f"Health and quality dashboard showing metrics and status for {model.metadata.epmo_name}"
        )
    
    def _generate_component_overview_prompt(
        self,
        model: EPMDocumentationModel,
        modules_data: List[Dict[str, Any]]
    ) -> Optional[ImagePrompt]:
        """Generate component overview visualization prompt."""
        
        total_classes = sum(len(f.classes) for f in model.files)
        total_functions = sum(len(f.functions) for f in model.files)
        
        prompt_text = f"""
Create a component overview diagram for '{model.metadata.epmo_name}' showing module composition.

**Component Structure:**
- {len(model.files)} modules/files
- {total_classes} classes total
- {total_functions} functions total
- Object-oriented architecture with clear interfaces

**Visual Layout:**
- Grid or hierarchical layout of components
- Each component shown as rounded rectangle card
- Size indicates relative complexity/importance
- Color coding by component type or responsibility
- Connection lines showing key relationships

**Component Cards Content:**
- Module name as header
- Class count and function count
- Complexity indicator (visual meter)
- Key responsibilities or interfaces
- Import/export indicators

**Design Style:**
- Modern component diagram style
- 9:16 portrait orientation for detailed view
- Clean card-based layout
- Professional technical aesthetic
- Consistent spacing and alignment
- Readable typography at all levels

**Color Scheme:**
- Primary components: Deep blue
- Utility components: Teal green
- Interface components: Orange
- Support components: Gray
- High complexity: Red accents
""".strip()
        
        return ImagePrompt(
            prompt_id=f"components_{model.metadata.epmo_name.lower().replace(' ', '_')}",
            title=f"{model.metadata.epmo_name} Components",
            prompt_text=prompt_text,
            style_guidance="Component diagram, technical documentation style, clean and organized",
            aspect_ratio="9:16",
            complexity_level="medium",
            color_palette=["#1E40AF", "#0891B2", "#EA580C", "#6B7280", "#DC2626"],
            narrative_description=f"Detailed component breakdown showing the structure and organization of {model.metadata.epmo_name}"
        )
    
    def _convert_epm_results_to_image_prompts(
        self,
        epm_results: Dict[str, Any]
    ) -> List[ImagePrompt]:
        """Convert EPM image generator results to ImagePrompt objects."""
        image_prompts = []
        
        try:
            results = epm_results.get('results', {})
            prompts_dir = Path(epm_results.get('prompts_dir', ''))
            
            for diagram_key, diagram_info in results.items():
                if isinstance(diagram_info, dict) and 'file_path' in diagram_info:
                    prompt_file = Path(diagram_info['file_path'])
                    if prompt_file.exists():
                        # Read the prompt content
                        prompt_content = prompt_file.read_text(encoding='utf-8')
                        
                        # Extract title from content or use diagram key
                        title = diagram_info.get('title', diagram_key.replace('_', ' ').title())
                        
                        image_prompt = ImagePrompt(
                            prompt_id=diagram_key,
                            title=title,
                            prompt_text=prompt_content,
                            style_guidance="Professional technical diagram generated by CORTEX EPM",
                            aspect_ratio=diagram_info.get('aspect_ratio', '16:9'),
                            complexity_level="medium",
                            color_palette=["#6B46C1", "#3B82F6", "#10B981", "#F59E0B"],
                            narrative_description=f"EPM-generated visualization: {title}",
                            prompt_file_path=str(prompt_file)
                        )
                        image_prompts.append(image_prompt)
                        
        except Exception as e:
            logger.warning(f"Error converting EPM results: {e}")
        
        return image_prompts
    
    def save_image_prompts(
        self,
        image_prompts: List[ImagePrompt],
        output_dir: Optional[Path] = None
    ) -> Dict[str, str]:
        """
        Save image prompts to files for AI generation.
        
        Args:
            image_prompts: List of image prompts to save
            output_dir: Output directory (defaults to self.output_dir/prompts)
            
        Returns:
            Dictionary mapping prompt IDs to file paths
        """
        if not output_dir:
            output_dir = self.output_dir / 'prompts'
        
        output_dir.mkdir(parents=True, exist_ok=True)
        saved_files = {}
        
        for prompt in image_prompts:
            # Create filename
            filename = f"{prompt.prompt_id}.md"
            file_path = output_dir / filename
            
            # Create prompt file content
            content = f"""# {prompt.title}

**Prompt ID:** {prompt.prompt_id}  
**Aspect Ratio:** {prompt.aspect_ratio}  
**Complexity:** {prompt.complexity_level}  

## AI Generation Prompt

{prompt.prompt_text}

## Style Guidance

{prompt.style_guidance}

## Color Palette

{', '.join(prompt.color_palette)}

## Description

{prompt.narrative_description}

---

*Generated by CORTEX EPM Image Prompt Integration Bridge*  
*Part of Feature 4 Phase 4.2 Multi-Modal Documentation System*
"""
            
            # Write to file
            file_path.write_text(content, encoding='utf-8')
            saved_files[prompt.prompt_id] = str(file_path)
            
            # Update prompt object with file path
            prompt.prompt_file_path = str(file_path)
        
        logger.info(f"Saved {len(saved_files)} image prompt files to {output_dir}")
        return saved_files


def integrate_image_prompts_with_epmo(
    model: EPMDocumentationModel,
    output_dir: Optional[Path] = None
) -> Tuple[List[ImagePrompt], Dict[str, str]]:
    """
    Complete integration function to generate and save image prompts for an EPMO.
    
    Args:
        model: Complete EPM documentation model
        output_dir: Output directory for prompt files
        
    Returns:
        Tuple of (generated image prompts, saved file paths)
    """
    bridge = ImagePromptIntegrationBridge(output_dir)
    
    # Generate image prompts
    image_prompts = bridge.generate_epmo_image_prompts(model)
    
    # Save prompts to files
    saved_files = bridge.save_image_prompts(image_prompts)
    
    return image_prompts, saved_files