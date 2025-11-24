"""
Multi-Modal Diagram Generator for CORTEX EPM Documentation

Generates both Mermaid diagrams and AI image prompts from architecture data.
Integrates with the existing ImagePromptGenerator to create comprehensive
visual documentation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - Part of CORTEX 3.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .models import (
    MermaidDiagram, ImagePrompt, MultiModalDiagram, DiagramType,
    EPMDocumentationModel, FileAnalysis, DependencyRelation,
    ArchitectureMetrics, ClassModel, CodeElement
)

logger = logging.getLogger(__name__)


@dataclass
class DiagramConfig:
    """Configuration for diagram generation."""
    max_nodes: int = 50
    max_edges: int = 100
    include_private: bool = False
    color_by_complexity: bool = True
    group_by_module: bool = True
    show_external_deps: bool = True


class MermaidDiagramGenerator:
    """
    Generate Mermaid diagrams from EPM analysis data.
    
    Supports multiple diagram types:
    - Class diagrams
    - Dependency graphs
    - Architecture diagrams
    - Flow charts
    """
    
    def __init__(self, config: DiagramConfig = None):
        """Initialize Mermaid generator."""
        self.config = config or DiagramConfig()
        
    def generate_class_diagram(
        self, 
        files: List[FileAnalysis], 
        title: str = "Class Diagram"
    ) -> MermaidDiagram:
        """Generate class diagram showing class relationships."""
        
        mermaid_lines = ["classDiagram"]
        
        # Add classes
        all_classes = []
        for file_analysis in files:
            for class_model in file_analysis.classes:
                if not self.config.include_private and class_model.visibility == 'private':
                    continue
                all_classes.append((file_analysis.module_name, class_model))
        
        # Limit diagram size
        if len(all_classes) > self.config.max_nodes:
            all_classes = all_classes[:self.config.max_nodes]
            logger.warning(f"Limited class diagram to {self.config.max_nodes} classes")
        
        # Define classes
        for module_name, class_model in all_classes:
            class_name = f"{module_name}_{class_model.name}" if self.config.group_by_module else class_model.name
            
            # Class definition
            mermaid_lines.append(f"    class {class_name} {{")
            
            # Add methods (limit to public methods)
            public_methods = [m for m in class_model.methods if m.visibility == 'public'][:5]
            for method in public_methods:
                method_line = f"        +{method.name}({', '.join(method.parameters[:2])})"
                if method.return_type:
                    method_line += f" : {method.return_type}"
                mermaid_lines.append(method_line)
            
            if len(class_model.methods) > 5:
                mermaid_lines.append("        +...")
            
            mermaid_lines.append("    }")
            
            # Inheritance relationships
            for base_class in class_model.base_classes:
                base_name = base_class.split('.')[-1]  # Get simple name
                mermaid_lines.append(f"    {base_name} <|-- {class_name}")
        
        mermaid_syntax = "\n".join(mermaid_lines)
        
        return MermaidDiagram(
            diagram_type=DiagramType.CLASS,
            title=title,
            mermaid_syntax=mermaid_syntax,
            description="Class relationships and inheritance hierarchy"
        )
    
    def generate_dependency_diagram(
        self,
        dependencies: List[DependencyRelation],
        architecture: ArchitectureMetrics,
        title: str = "Dependency Graph"
    ) -> MermaidDiagram:
        """Generate dependency diagram showing module relationships."""
        
        mermaid_lines = ["graph TD"]
        
        # Collect all modules
        modules = set()
        for dep in dependencies:
            modules.add(dep.source_module)
            modules.add(dep.target_module)
        
        # Add external dependencies
        if self.config.show_external_deps and architecture.external_dependencies:
            for ext_dep in architecture.external_dependencies[:10]:  # Limit external deps
                modules.add(ext_dep)
        
        # Limit diagram size
        if len(dependencies) > self.config.max_edges:
            dependencies = sorted(dependencies, key=lambda d: d.strength, reverse=True)[:self.config.max_edges]
            logger.warning(f"Limited dependency diagram to {self.config.max_edges} relationships")
        
        # Define nodes with styling
        for module in modules:
            module_id = module.replace('.', '_').replace('-', '_')
            
            # Style based on type
            if module in architecture.external_dependencies:
                mermaid_lines.append(f"    {module_id}[{module}]")
                mermaid_lines.append(f"    class {module_id} external")
            elif module in getattr(architecture, 'hotspot_modules', []):
                mermaid_lines.append(f"    {module_id}[{module}]")
                mermaid_lines.append(f"    class {module_id} hotspot")
            else:
                mermaid_lines.append(f"    {module_id}[{module}]")
        
        # Add relationships
        for dep in dependencies:
            source_id = dep.source_module.replace('.', '_').replace('-', '_')
            target_id = dep.target_module.replace('.', '_').replace('-', '_')
            
            # Choose arrow style based on relationship type
            if dep.relationship_type == 'imports':
                arrow = "-->"
            elif dep.relationship_type == 'extends':
                arrow = "-..->"
            else:
                arrow = "-->"
            
            # Add strength indicator
            strength_label = f"|{dep.strength:.1f}|" if dep.strength < 1.0 else ""
            
            mermaid_lines.append(f"    {source_id} {arrow}{strength_label} {target_id}")
        
        # Add styling classes
        mermaid_lines.extend([
            "    classDef external fill:#e1f5fe",
            "    classDef hotspot fill:#fff3e0"
        ])
        
        mermaid_syntax = "\n".join(mermaid_lines)
        
        return MermaidDiagram(
            diagram_type=DiagramType.DEPENDENCY,
            title=title,
            mermaid_syntax=mermaid_syntax,
            description="Module dependencies and relationships"
        )
    
    def generate_architecture_diagram(
        self,
        model: EPMDocumentationModel,
        title: str = "Architecture Overview"
    ) -> MermaidDiagram:
        """Generate high-level architecture diagram."""
        
        mermaid_lines = ["graph TB"]
        
        if not model.files:
            return MermaidDiagram(
                diagram_type=DiagramType.ARCHITECTURE,
                title=title,
                mermaid_syntax="graph TB\n    Empty[No components found]",
                description="No architecture components to display"
            )
        
        # Group files by directory
        file_groups = {}
        for file_analysis in model.files:
            parts = Path(file_analysis.relative_path).parts
            if len(parts) > 1:
                group = parts[0]
            else:
                group = "root"
            
            if group not in file_groups:
                file_groups[group] = []
            file_groups[group].append(file_analysis)
        
        # Create subgraphs for each group
        for group_name, files in file_groups.items():
            group_id = group_name.replace('.', '_').replace('-', '_')
            mermaid_lines.append(f"    subgraph {group_id}[{group_name}]")
            
            for file_analysis in files:
                file_id = file_analysis.module_name.replace('.', '_').replace('-', '_')
                
                # Node styling based on complexity
                if file_analysis.complexity_score > 20:
                    node_style = f"{file_id}[{file_analysis.module_name}<br/>High Complexity]"
                    mermaid_lines.append(f"        {node_style}")
                    mermaid_lines.append(f"        class {file_id} complex")
                else:
                    mermaid_lines.append(f"        {file_id}[{file_analysis.module_name}]")
            
            mermaid_lines.append("    end")
        
        # Add key relationships between groups
        processed_deps = set()
        for dep in model.dependencies[:20]:  # Limit to avoid clutter
            source_parts = dep.source_module.split('.')
            target_parts = dep.target_module.split('.')
            
            if len(source_parts) > 0 and len(target_parts) > 0:
                source_group = source_parts[0]
                target_group = target_parts[0]
                
                if source_group != target_group:
                    dep_key = (source_group, target_group)
                    if dep_key not in processed_deps:
                        source_id = source_group.replace('.', '_').replace('-', '_')
                        target_id = target_group.replace('.', '_').replace('-', '_')
                        mermaid_lines.append(f"    {source_id} --> {target_id}")
                        processed_deps.add(dep_key)
        
        # Add styling
        mermaid_lines.extend([
            "    classDef complex fill:#ffebee,stroke:#c62828",
            "    classDef default fill:#f3e5f5,stroke:#7b1fa2"
        ])
        
        mermaid_syntax = "\n".join(mermaid_lines)
        
        return MermaidDiagram(
            diagram_type=DiagramType.ARCHITECTURE,
            title=title,
            mermaid_syntax=mermaid_syntax,
            description="High-level architecture and component relationships"
        )


class MultiModalDiagramGenerator:
    """
    Generate comprehensive diagrams with both Mermaid and AI image prompts.
    
    Combines technical precision of Mermaid with professional presentation
    of AI-generated images.
    """
    
    def __init__(self, config: DiagramConfig = None):
        """Initialize multi-modal generator."""
        self.config = config or DiagramConfig()
        self.mermaid_generator = MermaidDiagramGenerator(config)
        
    def generate_architecture_multimodal(
        self,
        model: EPMDocumentationModel
    ) -> MultiModalDiagram:
        """Generate multi-modal architecture diagram."""
        
        # Generate Mermaid diagram
        mermaid_diagram = self.mermaid_generator.generate_architecture_diagram(
            model, "Architecture Overview"
        )
        
        # Generate corresponding AI image prompt
        image_prompt = self._create_architecture_image_prompt(model)
        
        return MultiModalDiagram(
            diagram_id="architecture_overview",
            title="EPMO Architecture Overview",
            diagram_type=DiagramType.ARCHITECTURE,
            mermaid_diagram=mermaid_diagram,
            image_prompt=image_prompt,
            description="Complete architectural view with technical details and professional presentation",
            use_case="architecture",
            priority=1
        )
    
    def generate_dependency_multimodal(
        self,
        model: EPMDocumentationModel
    ) -> MultiModalDiagram:
        """Generate multi-modal dependency diagram."""
        
        # Generate Mermaid diagram
        mermaid_diagram = self.mermaid_generator.generate_dependency_diagram(
            model.dependencies, 
            model.architecture,
            "Dependency Graph"
        )
        
        # Generate corresponding AI image prompt
        image_prompt = self._create_dependency_image_prompt(model)
        
        return MultiModalDiagram(
            diagram_id="dependency_graph",
            title="EPMO Dependency Analysis",
            diagram_type=DiagramType.DEPENDENCY,
            mermaid_diagram=mermaid_diagram,
            image_prompt=image_prompt,
            description="Module dependencies with technical graph and visual representation",
            use_case="architecture",
            priority=2
        )
    
    def generate_class_multimodal(
        self,
        model: EPMDocumentationModel
    ) -> MultiModalDiagram:
        """Generate multi-modal class diagram."""
        
        # Generate Mermaid diagram
        mermaid_diagram = self.mermaid_generator.generate_class_diagram(
            model.files, "Class Relationships"
        )
        
        # Generate corresponding AI image prompt
        image_prompt = self._create_class_image_prompt(model)
        
        return MultiModalDiagram(
            diagram_id="class_relationships",
            title="EPMO Class Structure",
            diagram_type=DiagramType.CLASS,
            mermaid_diagram=mermaid_diagram,
            image_prompt=image_prompt,
            description="Object-oriented design with UML and professional visualization",
            use_case="class",
            priority=3
        )
    
    def _create_architecture_image_prompt(self, model: EPMDocumentationModel) -> ImagePrompt:
        """Create AI image prompt for architecture diagram."""
        
        # Analyze model for prompt content
        total_components = len(model.files)
        external_deps = len(model.architecture.external_dependencies) if model.architecture else 0
        
        prompt_text = f"""
Create a professional software architecture diagram showing a Python Entry Point Module (EPMO) system.

**System Overview:**
- {total_components} main components/modules
- {external_deps} external dependencies
- Modern microservices-style architecture

**Visual Requirements:**
- Clean, modern technical diagram style
- 16:9 landscape orientation
- Component boxes with rounded corners
- Directional arrows showing data flow
- Color-coded components (blue for core, green for utilities, orange for external)
- Professional typography and spacing

**Components to Show:**
- Core modules as main building blocks
- Data flow arrows between components
- External dependencies as separate layer
- Clear hierarchy and relationships
""".strip()
        
        return ImagePrompt(
            prompt_id=f"architecture_{model.metadata.epmo_name.lower()}",
            title=f"{model.metadata.epmo_name} Architecture",
            prompt_text=prompt_text,
            style_guidance="Professional technical diagram, clean modern design, corporate presentation style",
            aspect_ratio="16:9",
            complexity_level="medium",
            color_palette=["#3B82F6", "#10B981", "#F59E0B", "#6B7280"],
            narrative_description=f"Professional architecture diagram for the {model.metadata.epmo_name} system showing component relationships and data flow"
        )
    
    def _create_dependency_image_prompt(self, model: EPMDocumentationModel) -> ImagePrompt:
        """Create AI image prompt for dependency diagram."""
        
        dep_count = len(model.dependencies)
        circular_deps = model.architecture.circular_dependencies if model.architecture else 0
        
        prompt_text = f"""
Create a network-style dependency visualization showing module relationships in a Python system.

**Dependency Analysis:**
- {dep_count} total dependencies
- {"Circular dependencies detected" if circular_deps > 0 else "Clean dependency structure"}
- Module interconnections and data flow

**Visual Style:**
- Network graph with nodes and connecting lines
- Nodes sized by importance/complexity
- Edge thickness represents dependency strength
- Color coding for different relationship types
- 1:1 square format for balanced composition

**Elements:**
- Central core modules as larger nodes
- Peripheral modules as smaller nodes
- Clear directional flow indicators
- Legend explaining relationship types
""".strip()
        
        return ImagePrompt(
            prompt_id=f"dependencies_{model.metadata.epmo_name.lower()}",
            title=f"{model.metadata.epmo_name} Dependencies",
            prompt_text=prompt_text,
            style_guidance="Network visualization, technical graph style, clear and informative",
            aspect_ratio="1:1",
            complexity_level="high",
            color_palette=["#6B46C1", "#3B82F6", "#10B981", "#F59E0B"],
            narrative_description=f"Dependency network visualization showing how modules in {model.metadata.epmo_name} interconnect"
        )
    
    def _create_class_image_prompt(self, model: EPMDocumentationModel) -> ImagePrompt:
        """Create AI image prompt for class diagram."""
        
        total_classes = sum(len(f.classes) for f in model.files)
        
        prompt_text = f"""
Create a UML-style class diagram showing object-oriented design relationships.

**Class Structure:**
- {total_classes} main classes
- Inheritance hierarchies
- Method and property relationships
- Clean object-oriented design patterns

**Visual Design:**
- Traditional UML class box format
- Three-section boxes (name, attributes, methods)
- Inheritance arrows and association lines
- Professional technical documentation style
- 9:16 portrait orientation for detailed view

**Layout:**
- Hierarchical arrangement with base classes at top
- Clear separation between class groups
- Readable typography for method signatures
- Color coding for public/private members
""".strip()
        
        return ImagePrompt(
            prompt_id=f"classes_{model.metadata.epmo_name.lower()}",
            title=f"{model.metadata.epmo_name} Class Design",
            prompt_text=prompt_text,
            style_guidance="UML diagram style, technical documentation, clean and professional",
            aspect_ratio="9:16",
            complexity_level="high",
            color_palette=["#E3F2FD", "#BBDEFB", "#90CAF9", "#64B5F6"],
            narrative_description=f"UML class diagram showing the object-oriented design of {model.metadata.epmo_name}"
        )
    
    def generate_all_diagrams(self, model: EPMDocumentationModel) -> List[MultiModalDiagram]:
        """Generate all standard diagrams for an EPMO."""
        diagrams = []
        
        try:
            # Architecture diagram
            arch_diagram = self.generate_architecture_multimodal(model)
            diagrams.append(arch_diagram)
            
            # Dependency diagram (only if dependencies exist)
            if model.dependencies:
                dep_diagram = self.generate_dependency_multimodal(model)
                diagrams.append(dep_diagram)
            
            # Class diagram (only if classes exist)
            total_classes = sum(len(f.classes) for f in model.files)
            if total_classes > 0:
                class_diagram = self.generate_class_multimodal(model)
                diagrams.append(class_diagram)
                
        except Exception as e:
            logger.error(f"Error generating diagrams: {e}")
        
        logger.info(f"Generated {len(diagrams)} multi-modal diagrams")
        return diagrams


def create_diagrams_for_model(
    model: EPMDocumentationModel,
    config: Optional[DiagramConfig] = None
) -> List[MultiModalDiagram]:
    """
    Create all appropriate diagrams for an EPM model.
    
    Args:
        model: Complete EPM documentation model
        config: Optional diagram generation configuration
        
    Returns:
        List of generated multi-modal diagrams
    """
    generator = MultiModalDiagramGenerator(config)
    return generator.generate_all_diagrams(model)