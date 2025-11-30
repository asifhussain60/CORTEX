#!/usr/bin/env python3
"""
Visual Asset Generator

Generates visual documentation assets including Mermaid diagrams and
AI image prompts to support comprehensive feature documentation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
import logging

# Import implementation data structures
from .implementation_discovery_engine import ImplementationData, CodeElement, APIEndpoint

logger = logging.getLogger(__name__)

@dataclass
class MermaidDiagram:
    """Represents a Mermaid diagram"""
    diagram_type: str  # 'class', 'sequence', 'flowchart', 'architecture'
    title: str
    content: str  # Mermaid syntax
    description: str
    suggested_filename: str

@dataclass
class ImagePrompt:
    """Represents an AI image generation prompt"""
    prompt_type: str  # 'architecture', 'workflow', 'ui_mockup', 'concept'
    title: str
    prompt_text: str
    style_specifications: str
    suggested_filename: str
    priority: str  # 'high', 'medium', 'low'

@dataclass
class VisualAssets:
    """Complete collection of visual assets for a feature"""
    feature_name: str
    generation_timestamp: datetime
    
    # Diagrams
    mermaid_diagrams: List[MermaidDiagram] = field(default_factory=list)
    
    # AI Image prompts
    image_prompts: List[ImagePrompt] = field(default_factory=list)
    
    # File references
    diagram_files_created: List[str] = field(default_factory=list)
    image_prompt_files_created: List[str] = field(default_factory=list)
    
    # Metrics
    diagrams_generated: int = 0
    prompts_generated: int = 0


class MermaidDiagramGenerator:
    """Generates Mermaid diagrams from implementation data"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def generate_class_diagrams(self, classes: List[CodeElement]) -> List[MermaidDiagram]:
        """Generate class diagrams for new classes"""
        diagrams = []
        
        if not classes:
            return diagrams
            
        # Group classes by module/package
        modules = {}
        for cls in classes:
            module_path = str(Path(cls.file_path).parent)
            if module_path not in modules:
                modules[module_path] = []
            modules[module_path].append(cls)
            
        # Create diagram for each module
        for module_path, module_classes in modules.items():
            diagram = self._create_class_diagram(module_path, module_classes)
            diagrams.append(diagram)
            
        return diagrams
    
    def _create_class_diagram(self, module_path: str, classes: List[CodeElement]) -> MermaidDiagram:
        """Create a class diagram for classes in a module"""
        module_name = Path(module_path).name or "root"
        
        # Start mermaid class diagram
        mermaid_content = "classDiagram\n"
        
        for cls in classes:
            # Add class definition
            mermaid_content += f"    class {cls.name} {{\n"
            
            # Add methods (simplified - would need method parsing)
            if cls.element_type == 'class':
                mermaid_content += f"        +__init__()\n"
                # Add placeholder methods
                mermaid_content += f"        +method1()\n"
                mermaid_content += f"        +method2()\n"
                
            mermaid_content += "    }\n\n"
            
        # Add relationships (simplified)
        if len(classes) > 1:
            for i, cls in enumerate(classes[:-1]):
                next_cls = classes[i + 1]
                mermaid_content += f"    {cls.name} --> {next_cls.name}\n"
                
        diagram = MermaidDiagram(
            diagram_type="class",
            title=f"Class Diagram: {module_name}",
            content=mermaid_content,
            description=f"Class diagram showing relationships in {module_name} module",
            suggested_filename=f"class-diagram-{module_name.lower().replace('_', '-')}.md"
        )
        
        return diagram
    
    def generate_api_sequence_diagrams(self, endpoints: List[APIEndpoint]) -> List[MermaidDiagram]:
        """Generate sequence diagrams for API flows"""
        diagrams = []
        
        # Group endpoints by logical flows
        flows = self._group_endpoints_by_flow(endpoints)
        
        for flow_name, flow_endpoints in flows.items():
            diagram = self._create_sequence_diagram(flow_name, flow_endpoints)
            diagrams.append(diagram)
            
        return diagrams
    
    def _group_endpoints_by_flow(self, endpoints: List[APIEndpoint]) -> Dict[str, List[APIEndpoint]]:
        """Group endpoints into logical flows"""
        flows = {}
        
        for endpoint in endpoints:
            # Extract flow name from path (first path segment)
            path_parts = endpoint.path.strip('/').split('/')
            flow_name = path_parts[0] if path_parts else 'general'
            
            if flow_name not in flows:
                flows[flow_name] = []
            flows[flow_name].append(endpoint)
            
        return flows
    
    def _create_sequence_diagram(self, flow_name: str, endpoints: List[APIEndpoint]) -> MermaidDiagram:
        """Create a sequence diagram for an API flow"""
        mermaid_content = "sequenceDiagram\n"
        mermaid_content += "    participant Client\n"
        mermaid_content += "    participant API\n"
        mermaid_content += "    participant Service\n"
        mermaid_content += "    participant Database\n\n"
        
        for i, endpoint in enumerate(endpoints, 1):
            # Client to API
            mermaid_content += f"    Client->>+API: {endpoint.method} {endpoint.path}\n"
            
            # API to Service
            service_name = self._infer_service_name(endpoint)
            mermaid_content += f"    API->>+Service: {endpoint.handler_function}()\n"
            
            # Service to Database (for data operations)
            if endpoint.method in ['GET', 'POST', 'PUT', 'DELETE']:
                operation = self._infer_db_operation(endpoint.method)
                mermaid_content += f"    Service->>+Database: {operation}\n"
                mermaid_content += f"    Database-->>-Service: result\n"
                
            # Service back to API
            mermaid_content += f"    Service-->>-API: response\n"
            
            # API back to Client
            mermaid_content += f"    API-->>-Client: HTTP Response\n\n"
            
        diagram = MermaidDiagram(
            diagram_type="sequence",
            title=f"API Flow: {flow_name}",
            content=mermaid_content,
            description=f"Sequence diagram showing {flow_name} API flow",
            suggested_filename=f"sequence-{flow_name.lower().replace('_', '-')}.md"
        )
        
        return diagram
    
    def _infer_service_name(self, endpoint: APIEndpoint) -> str:
        """Infer service name from endpoint"""
        path_parts = endpoint.path.strip('/').split('/')
        if path_parts:
            return f"{path_parts[0].title()}Service"
        return "Service"
    
    def _infer_db_operation(self, method: str) -> str:
        """Infer database operation from HTTP method"""
        operations = {
            'GET': 'SELECT',
            'POST': 'INSERT',
            'PUT': 'UPDATE',
            'DELETE': 'DELETE'
        }
        return operations.get(method, 'OPERATION')
    
    def generate_architecture_diagrams(self, implementation_data: ImplementationData) -> List[MermaidDiagram]:
        """Generate high-level architecture diagrams"""
        diagrams = []
        
        # Create component architecture diagram
        if implementation_data.new_classes or implementation_data.new_endpoints:
            diagram = self._create_architecture_diagram(implementation_data)
            diagrams.append(diagram)
            
        return diagrams
    
    def _create_architecture_diagram(self, implementation_data: ImplementationData) -> MermaidDiagram:
        """Create high-level architecture diagram"""
        mermaid_content = "graph TD\n"
        
        # Add client layer
        mermaid_content += "    Client[Client Application]\n"
        
        # Add API layer if endpoints exist
        if implementation_data.new_endpoints:
            mermaid_content += "    API[API Layer]\n"
            mermaid_content += "    Client --> API\n"
            
            # Group endpoints by service
            services = set()
            for endpoint in implementation_data.new_endpoints:
                service = self._infer_service_name(endpoint)
                services.add(service)
                
            # Add service layer
            for service in services:
                service_id = service.replace(' ', '')
                mermaid_content += f"    {service_id}[{service}]\n"
                mermaid_content += f"    API --> {service_id}\n"
                
        # Add data layer if classes exist
        if implementation_data.new_classes:
            mermaid_content += "    Data[Data Layer]\n"
            
            for cls in implementation_data.new_classes:
                class_id = cls.name.replace(' ', '')
                mermaid_content += f"    {class_id}[{cls.name}]\n"
                mermaid_content += f"    Data --> {class_id}\n"
                
        # Add database
        mermaid_content += "    DB[(Database)]\n"
        mermaid_content += "    Data --> DB\n"
        
        diagram = MermaidDiagram(
            diagram_type="architecture",
            title=f"Architecture: {implementation_data.feature_name}",
            content=mermaid_content,
            description=f"High-level architecture diagram for {implementation_data.feature_name} feature",
            suggested_filename=f"architecture-{implementation_data.feature_name.lower().replace(' ', '-')}.md"
        )
        
        return diagram


class ImagePromptGenerator:
    """Generates AI image prompts for visual documentation"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def generate_architecture_prompts(self, implementation_data: ImplementationData) -> List[ImagePrompt]:
        """Generate architecture visualization prompts"""
        prompts = []
        
        # System architecture prompt
        arch_prompt = self._create_architecture_prompt(implementation_data)
        prompts.append(arch_prompt)
        
        # Data flow prompt
        if implementation_data.new_endpoints:
            flow_prompt = self._create_data_flow_prompt(implementation_data)
            prompts.append(flow_prompt)
            
        return prompts
    
    def _create_architecture_prompt(self, implementation_data: ImplementationData) -> ImagePrompt:
        """Create system architecture visualization prompt"""
        components = []
        
        if implementation_data.new_endpoints:
            components.append("RESTful API endpoints")
        if implementation_data.new_classes:
            components.append("service classes")
        if implementation_data.new_tests:
            components.append("test coverage")
            
        prompt_text = f"""
Create a clean, professional system architecture diagram for a {implementation_data.feature_name} feature.

Components to include:
{', '.join(components)}

Show the following layers:
1. Client/Frontend layer at the top
2. API/Controller layer in the middle  
3. Service/Business logic layer
4. Data/Persistence layer at the bottom

Use modern software architecture visualization style with:
- Clean geometric shapes (rectangles, circles)
- Professional color scheme (blues, grays, whites)
- Clear directional arrows showing data flow
- Minimal text labels
- Isometric or flat design aesthetic

Style: Technical diagram, corporate presentation quality, white background
"""
        
        return ImagePrompt(
            prompt_type="architecture",
            title=f"System Architecture: {implementation_data.feature_name}",
            prompt_text=prompt_text.strip(),
            style_specifications="Professional technical diagram, isometric view, blue/gray color scheme",
            suggested_filename=f"architecture-{implementation_data.feature_name.lower().replace(' ', '-')}.png",
            priority="high"
        )
    
    def _create_data_flow_prompt(self, implementation_data: ImplementationData) -> ImagePrompt:
        """Create data flow visualization prompt"""
        endpoints = implementation_data.new_endpoints
        
        flow_description = []
        for endpoint in endpoints[:3]:  # Limit to first 3 for clarity
            flow_description.append(f"{endpoint.method} {endpoint.path}")
            
        prompt_text = f"""
Create a data flow diagram showing how information moves through the {implementation_data.feature_name} system.

Key flows to visualize:
{chr(10).join(f'- {desc}' for desc in flow_description)}

Show:
1. User/client request entry point
2. Request processing flow
3. Data transformation steps
4. Database interactions
5. Response flow back to user

Visual style:
- Flowchart with rounded rectangles for processes
- Arrows indicating data direction
- Different colors for different data types
- Clean, minimal design
- Professional presentation quality

Style: Flowchart diagram, modern flat design, teal/blue color palette, white background
"""
        
        return ImagePrompt(
            prompt_type="workflow", 
            title=f"Data Flow: {implementation_data.feature_name}",
            prompt_text=prompt_text.strip(),
            style_specifications="Flowchart style, modern flat design, teal/blue palette",
            suggested_filename=f"dataflow-{implementation_data.feature_name.lower().replace(' ', '-')}.png",
            priority="medium"
        )
    
    def generate_ui_prompts(self, implementation_data: ImplementationData) -> List[ImagePrompt]:
        """Generate UI mockup prompts for user-facing features"""
        prompts = []
        
        # Only generate UI prompts for features that likely have UI components
        ui_indicators = ['dashboard', 'login', 'form', 'panel', 'page', 'view', 'interface']
        
        feature_name_lower = implementation_data.feature_name.lower()
        has_ui_component = any(indicator in feature_name_lower for indicator in ui_indicators)
        
        if has_ui_component:
            ui_prompt = self._create_ui_mockup_prompt(implementation_data)
            prompts.append(ui_prompt)
            
        return prompts
    
    def _create_ui_mockup_prompt(self, implementation_data: ImplementationData) -> ImagePrompt:
        """Create UI mockup prompt"""
        prompt_text = f"""
Design a clean, modern user interface mockup for the {implementation_data.feature_name} feature.

Requirements:
- Modern web application interface
- Clean, minimal design aesthetic
- Professional color scheme (whites, grays, accent blues)
- Responsive layout design
- Clear navigation elements
- Proper visual hierarchy

Include typical elements:
- Header/navigation bar
- Main content area
- Forms or data display as appropriate
- Buttons and interactive elements
- Footer

Style: Modern web UI mockup, flat design, professional corporate aesthetic, high-fidelity wireframe
"""
        
        return ImagePrompt(
            prompt_type="ui_mockup",
            title=f"UI Mockup: {implementation_data.feature_name}",
            prompt_text=prompt_text.strip(),
            style_specifications="Modern web UI, flat design, corporate aesthetic",
            suggested_filename=f"ui-mockup-{implementation_data.feature_name.lower().replace(' ', '-')}.png",
            priority="low"
        )
    
    def generate_concept_prompts(self, implementation_data: ImplementationData) -> List[ImagePrompt]:
        """Generate conceptual/metaphorical prompts for abstract features"""
        prompts = []
        
        # Generate concept visualization for complex features
        if implementation_data.complexity_score > 20 or len(implementation_data.new_classes) > 3:
            concept_prompt = self._create_concept_prompt(implementation_data)
            prompts.append(concept_prompt)
            
        return prompts
    
    def _create_concept_prompt(self, implementation_data: ImplementationData) -> ImagePrompt:
        """Create conceptual visualization prompt"""
        prompt_text = f"""
Create a conceptual illustration representing the {implementation_data.feature_name} feature.

The image should convey the core concept of this feature through:
- Abstract geometric shapes and forms
- Visual metaphors for software concepts
- Clean, modern illustration style
- Subtle gradients and professional colors
- Minimalist approach

Think of this as a hero image for technical documentation - it should be:
- Professional and sophisticated
- Visually appealing but not overly complex
- Suitable for technical documentation
- Conveying innovation and reliability

Style: Modern abstract illustration, technical aesthetic, gradient backgrounds, vector-style graphics
"""
        
        return ImagePrompt(
            prompt_type="concept",
            title=f"Concept Art: {implementation_data.feature_name}",
            prompt_text=prompt_text.strip(),
            style_specifications="Abstract technical illustration, modern vector style, gradient backgrounds",
            suggested_filename=f"concept-{implementation_data.feature_name.lower().replace(' ', '-')}.png",
            priority="low"
        )


class VisualAssetGenerator:
    """
    Main generator that coordinates Mermaid diagram generation and
    AI image prompt creation to create comprehensive visual documentation.
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.diagram_generator = MermaidDiagramGenerator(workspace_path)
        self.prompt_generator = ImagePromptGenerator(workspace_path)
        
    async def generate_visual_assets(self, implementation_data: ImplementationData) -> VisualAssets:
        """
        Main orchestration method that generates complete visual assets
        for an implemented feature.
        """
        logger.info(f"Starting visual asset generation for feature: {implementation_data.feature_name}")
        
        # Generate Mermaid diagrams
        diagrams = []
        diagrams.extend(self.diagram_generator.generate_class_diagrams(implementation_data.new_classes))
        diagrams.extend(self.diagram_generator.generate_api_sequence_diagrams(implementation_data.new_endpoints))
        diagrams.extend(self.diagram_generator.generate_architecture_diagrams(implementation_data))
        
        # Generate AI image prompts
        prompts = []
        prompts.extend(self.prompt_generator.generate_architecture_prompts(implementation_data))
        prompts.extend(self.prompt_generator.generate_ui_prompts(implementation_data))
        prompts.extend(self.prompt_generator.generate_concept_prompts(implementation_data))
        
        # Create output files
        diagram_files = await self._save_diagrams(diagrams, implementation_data.feature_name)
        prompt_files = await self._save_prompts(prompts, implementation_data.feature_name)
        
        assets = VisualAssets(
            feature_name=implementation_data.feature_name,
            generation_timestamp=datetime.now(),
            mermaid_diagrams=diagrams,
            image_prompts=prompts,
            diagram_files_created=diagram_files,
            image_prompt_files_created=prompt_files,
            diagrams_generated=len(diagrams),
            prompts_generated=len(prompts)
        )
        
        logger.info(f"Visual asset generation complete for {implementation_data.feature_name}: "
                   f"{len(diagrams)} diagrams, {len(prompts)} image prompts")
        
        return assets
    
    async def _save_diagrams(self, diagrams: List[MermaidDiagram], feature_name: str) -> List[str]:
        """Save Mermaid diagrams to files"""
        saved_files = []
        
        # Create diagrams directory
        diagrams_dir = Path(self.workspace_path) / "docs" / "diagrams" 
        diagrams_dir.mkdir(parents=True, exist_ok=True)
        
        for diagram in diagrams:
            filename = diagram.suggested_filename
            file_path = diagrams_dir / filename
            
            # Create markdown file with Mermaid diagram
            content = f"""# {diagram.title}

{diagram.description}

```mermaid
{diagram.content}
```

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} for feature: {feature_name}*
"""
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                saved_files.append(str(file_path))
                logger.info(f"Saved diagram: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to save diagram {filename}: {e}")
                
        return saved_files
    
    async def _save_prompts(self, prompts: List[ImagePrompt], feature_name: str) -> List[str]:
        """Save image prompts to files"""
        saved_files = []
        
        # Create prompts directory
        prompts_dir = Path(self.workspace_path) / "docs" / "image-prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        
        for prompt in prompts:
            filename = prompt.suggested_filename.replace('.png', '.md')
            file_path = prompts_dir / filename
            
            # Create markdown file with prompt
            content = f"""# {prompt.title}

**Type:** {prompt.prompt_type}  
**Priority:** {prompt.priority}  
**Style:** {prompt.style_specifications}  

## AI Image Generation Prompt

{prompt.prompt_text}

## Suggested Usage

This prompt can be used with AI image generation tools like:
- DALL-E 3
- Midjourney  
- Stable Diffusion
- Adobe Firefly

## Output Specifications

- **Format:** PNG or SVG
- **Resolution:** 1920x1080 (landscape) or 1080x1920 (portrait)
- **Style:** {prompt.style_specifications}
- **Filename:** `{prompt.suggested_filename}`

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} for feature: {feature_name}*
"""
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                saved_files.append(str(file_path))
                logger.info(f"Saved image prompt: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to save image prompt {filename}: {e}")
                
        return saved_files


if __name__ == "__main__":
    # Test visual asset generation
    import asyncio
    from .implementation_discovery_engine import ImplementationData, CodeElement, APIEndpoint
    
    async def test_visual_generation():
        # Create test implementation data
        test_data = ImplementationData(
            feature_name="User Authentication",
            discovery_timestamp=datetime.now(),
            new_classes=[
                CodeElement(
                    name="AuthService",
                    element_type="class",
                    file_path="src/auth/auth_service.py",
                    line_number=10,
                    docstring="Service for handling authentication"
                ),
                CodeElement(
                    name="UserModel",
                    element_type="class", 
                    file_path="src/auth/models.py",
                    line_number=5
                )
            ],
            new_endpoints=[
                APIEndpoint(
                    path="/auth/login",
                    method="POST",
                    handler_function="login",
                    file_path="src/auth/routes.py",
                    line_number=25
                ),
                APIEndpoint(
                    path="/auth/logout",
                    method="POST",
                    handler_function="logout", 
                    file_path="src/auth/routes.py",
                    line_number=45
                )
            ],
            complexity_score=25
        )
        
        generator = VisualAssetGenerator("/Users/asifhussain/PROJECTS/CORTEX")
        assets = await generator.generate_visual_assets(test_data)
        
        print(f"Visual Asset Generation Results for {assets.feature_name}:")
        print(f"- Diagrams generated: {assets.diagrams_generated}")
        print(f"- Image prompts generated: {assets.prompts_generated}")
        print(f"- Diagram files created: {len(assets.diagram_files_created)}")
        print(f"- Prompt files created: {len(assets.image_prompt_files_created)}")
        
        print("\nDiagrams:")
        for diagram in assets.mermaid_diagrams:
            print(f"  - {diagram.title} ({diagram.diagram_type})")
            
        print("\nImage Prompts:")
        for prompt in assets.image_prompts:
            print(f"  - {prompt.title} ({prompt.prompt_type}, {prompt.priority} priority)")
    
    asyncio.run(test_visual_generation())