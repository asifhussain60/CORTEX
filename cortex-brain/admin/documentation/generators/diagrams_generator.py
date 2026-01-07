"""
Diagrams Generator

Generates Mermaid diagrams, system architecture diagrams, and visual documentation.
Supports image generation prompts for AI art tools (Gemini, DALL-E, etc.).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from .base_generator import (
    BaseDocumentationGenerator,
    GenerationConfig,
    GenerationResult,
    GeneratorType
)


logger = logging.getLogger(__name__)


class DiagramsGenerator(BaseDocumentationGenerator):
    """
    Generates diagrams for CORTEX documentation.
    
    Supported diagram types:
    - Mermaid diagrams (architecture, flow, sequence)
    - Image generation prompts (for Gemini, DALL-E)
    - System architecture diagrams
    - Component relationship diagrams
    """
    
    def __init__(self, config: GenerationConfig, workspace_root: Optional[Path] = None):
        """Initialize diagrams generator"""
        super().__init__(config, workspace_root)
        
        # Load diagram definitions
        self.diagram_config = self.load_config_file("diagram-definitions.yaml")
        self.master_diagram_list = self.load_config_file("master-diagram-list.yaml")
    
    def get_component_name(self) -> str:
        """Component name for logging"""
        return "Diagram Documentation"
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data needed for diagram generation.
        
        Returns:
            Dictionary with diagram specifications, templates, existing diagrams
        """
        data = {
            "diagram_config": self.diagram_config or {},
            "master_diagram_list": self.master_diagram_list or {},
            "workspace_root": str(self.workspace_root),
            "output_path": str(self.output_path)
        }
        
        # Collect existing diagrams
        docs_path = self.workspace_root / "docs"
        if docs_path.exists():
            existing_diagrams = list(docs_path.rglob("*.mmd"))
            existing_diagrams.extend(docs_path.rglob("diagram-*.md"))
            data["existing_diagrams"] = [str(p) for p in existing_diagrams]
        
        return data
    
    def generate(self) -> GenerationResult:
        """
        Generate all configured diagrams.
        
        Returns:
            GenerationResult with files generated
        """
        logger.info("Generating diagrams...")
        
        # Generate Mermaid diagrams
        self._generate_mermaid_diagrams()
        
        # Generate image generation prompts (if profile includes them)
        if self.config.profile.value in ["comprehensive", "custom"]:
            self._generate_image_prompts()
        
        # Generate diagram index
        self._generate_diagram_index()
        
        return self._create_success_result(metadata={
            "diagrams_generated": len(self.files_generated),
            "mermaid_count": len([f for f in self.files_generated if f.suffix == ".mmd"]),
            "prompt_count": len([f for f in self.files_generated if "prompt" in f.stem])
        })
    
    def _generate_mermaid_diagrams(self):
        """Generate Mermaid diagram files"""
        if not self.master_diagram_list:
            self.record_warning("No master diagram list found, skipping Mermaid generation")
            return
        
        diagrams = self.master_diagram_list.get("diagrams", [])
        
        for diagram_spec in diagrams:
            try:
                diagram_id = diagram_spec.get("id")
                diagram_name = diagram_spec.get("name")
                diagram_type = diagram_spec.get("type", "flowchart")
                
                if not diagram_id:
                    self.record_warning(f"Diagram missing ID, skipping: {diagram_spec}")
                    continue
                
                # Generate diagram content based on type
                content = self._generate_diagram_content(diagram_spec)
                
                # Write diagram file
                diagram_file = self.output_path / "diagrams" / f"{diagram_id}.mmd"
                diagram_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(diagram_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.record_file_generated(diagram_file)
                
            except Exception as e:
                self.record_error(f"Failed to generate diagram {diagram_spec}: {e}")
    
    def _generate_diagram_content(self, diagram_spec: Dict[str, Any]) -> str:
        """
        Generate Mermaid diagram content based on specification.
        
        Args:
            diagram_spec: Diagram specification from config
        
        Returns:
            Mermaid diagram content
        """
        diagram_type = diagram_spec.get("type", "flowchart")
        diagram_name = diagram_spec.get("name", "Diagram")
        
        # Start with title
        content = f"---\ntitle: {diagram_name}\n---\n\n"
        
        if diagram_type == "flowchart":
            content += "flowchart TD\n"
            content += "    Start([Start]) --> Process[Process]\n"
            content += "    Process --> Decision{Decision?}\n"
            content += "    Decision -->|Yes| Success([Success])\n"
            content += "    Decision -->|No| Error([Error])\n"
        
        elif diagram_type == "sequence":
            content += "sequenceDiagram\n"
            content += "    participant User\n"
            content += "    participant System\n"
            content += "    User->>System: Request\n"
            content += "    System-->>User: Response\n"
        
        elif diagram_type == "class":
            content += "classDiagram\n"
            content += "    class Entity {\n"
            content += "        +String id\n"
            content += "        +String name\n"
            content += "        +method()\n"
            content += "    }\n"
        
        else:
            # Generic flowchart
            content += "flowchart LR\n"
            content += "    A[Start] --> B[Process]\n"
            content += "    B --> C[End]\n"
        
        return content
    
    def _generate_image_prompts(self):
        """Generate image generation prompts for AI art tools"""
        if not self.diagram_config:
            self.record_warning("No diagram config found, skipping image prompts")
            return
        
        visual_assets = self.diagram_config.get("visual_assets", {})
        image_prompts_config = visual_assets.get("image_prompts", {})
        
        if not image_prompts_config.get("enabled", False):
            logger.info("Image prompts disabled in config, skipping")
            return
        
        diagrams = image_prompts_config.get("diagrams", [])
        
        for diagram in diagrams:
            try:
                diagram_id = diagram.get("id")
                diagram_name = diagram.get("name")
                aspect_ratio = diagram.get("aspect_ratio", "16:9")
                size = diagram.get("size", "1920x1080")
                
                # Generate prompt content
                prompt_content = self._generate_prompt_content(diagram_name, aspect_ratio, size)
                
                # Write prompt file
                prompt_file = self.output_path / "diagrams" / "prompts" / f"{diagram_id}-prompt.md"
                prompt_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(prompt_content)
                
                self.record_file_generated(prompt_file)
                
            except Exception as e:
                self.record_error(f"Failed to generate image prompt {diagram}: {e}")
    
    def _generate_prompt_content(self, diagram_name: str, aspect_ratio: str, size: str) -> str:
        """Generate image generation prompt content"""
        return f"""# {diagram_name} - Image Generation Prompt

**Aspect Ratio:** {aspect_ratio}
**Size:** {size}

## Prompt for Gemini/DALL-E

Generate a professional technical diagram for "{diagram_name}".

Style: Modern, clean, professional technical documentation
Color scheme: Blue/purple gradient with white accents
Layout: {aspect_ratio} aspect ratio

Include:
- Clear component labels
- Connection lines showing relationships
- Legend if needed
- Professional styling

---

*Generated by CORTEX Documentation System*
"""
    
    def _generate_diagram_index(self):
        """Generate index of all diagrams"""
        index_content = "# CORTEX Diagrams Index\n\n"
        index_content += "## Generated Diagrams\n\n"
        
        for diagram_file in sorted(self.files_generated):
            if diagram_file.suffix == ".mmd":
                rel_path = diagram_file.relative_to(self.output_path)
                diagram_name = diagram_file.stem.replace("-", " ").title()
                index_content += f"- [{diagram_name}]({rel_path})\n"
        
        index_file = self.output_path / "diagrams" / "INDEX.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        self.record_file_generated(index_file)
    
    def validate(self) -> bool:
        """
        Validate generated diagrams.
        
        Returns:
            True if validation passes
        """
        if not self.files_generated:
            self.record_error("No diagrams were generated")
            return False
        
        # Validate Mermaid syntax (basic check)
        for diagram_file in self.files_generated:
            if diagram_file.suffix == ".mmd":
                try:
                    with open(diagram_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Basic validation: should have diagram type keyword
                    if not any(kw in content for kw in ["flowchart", "sequenceDiagram", "classDiagram", "graph"]):
                        self.record_warning(f"Diagram may be invalid: {diagram_file.name}")
                
                except Exception as e:
                    self.record_error(f"Failed to validate {diagram_file}: {e}")
                    return False
        
        return True
