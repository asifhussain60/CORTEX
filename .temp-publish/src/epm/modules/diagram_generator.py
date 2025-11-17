"""
CORTEX EPM - Diagram Generator Module
Generates Mermaid diagrams from code structure and configuration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, List
import yaml
import logging

logger = logging.getLogger(__name__)


class DiagramGenerator:
    """Generates Mermaid diagrams from CORTEX architecture and code"""
    
    def __init__(self, root_path: Path, dry_run: bool = False):
        self.root_path = root_path
        self.brain_path = root_path / "cortex-brain"
        self.src_path = root_path / "src"
        self.output_path = root_path / "docs"  # Base docs path, diagrams will add images/diagrams
        self.dry_run = dry_run
    
    def generate_all_diagrams(self, definitions_file: Path) -> Dict:
        """
        Generate all diagrams defined in diagram-definitions.yaml
        
        Returns:
            Dictionary with generation statistics
        """
        diagrams_generated = []
        
        # Load diagram definitions
        with open(definitions_file, 'r') as f:
            definitions = yaml.safe_load(f)
        
        for diagram_def in definitions.get('diagrams', []):
            diagram_type = diagram_def['type']
            output_file = self.output_path / diagram_def['output_path']
            
            if diagram_type == 'tier_architecture':
                content = self._generate_tier_architecture()
            elif diagram_type == 'agent_system':
                content = self._generate_agent_system()
            elif diagram_type == 'pipeline_flow':
                content = self._generate_pipeline_flow(diagram_def)
            elif diagram_type == 'module_structure':
                content = self._generate_module_structure(diagram_def)
            elif diagram_type == 'data_flow':
                content = self._generate_data_flow(diagram_def)
            else:
                logger.warning(f"Unknown diagram type: {diagram_type}")
                continue
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would generate: {output_file}")
            else:
                # Write diagram file
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w') as f:
                    f.write(content)
                logger.info(f"✓ Generated: {output_file}")
            
            diagrams_generated.append(str(output_file))
        
        return {
            "diagrams_generated": len(diagrams_generated),
            "files": diagrams_generated
        }
    
    def _generate_tier_architecture(self) -> str:
        """Generate 4-tier architecture diagram"""
        # TODO: Read from cortex-brain/capabilities.yaml or module-definitions.yaml
        # to get actual tier structure
        
        return """```mermaid
graph TB
    subgraph Tier0["Tier 0: Instinct"]
        T0_Rules[Governance Rules]
        T0_Protection[Brain Protection]
    end
    
    subgraph Tier1["Tier 1: Working Memory"]
        T1_Conv[Conversations]
        T1_Context[Context Tracking]
        T1_FIFO[FIFO Queue]
    end
    
    subgraph Tier2["Tier 2: Knowledge Graph"]
        T2_Patterns[Pattern Learning]
        T2_Relations[File Relationships]
        T2_Workflows[Workflow Templates]
    end
    
    subgraph Tier3["Tier 3: Context Intelligence"]
        T3_Git[Git Analysis]
        T3_Metrics[Code Metrics]
        T3_Health[Health Tracking]
    end
    
    Tier0 --> Tier1
    Tier1 --> Tier2
    Tier2 --> Tier3
```"""
    
    def _generate_agent_system(self) -> str:
        """Generate agent coordination diagram"""
        # TODO: Read from cortex-brain/module-definitions.yaml
        # to get actual agent structure
        
        return """```mermaid
graph LR
    subgraph RightBrain["Right Brain - Strategic"]
        IR[Intent Router]
        WP[Work Planner]
        SA[Screenshot Analyzer]
        CG[Change Governor]
        BP[Brain Protector]
    end
    
    subgraph Coordination["Corpus Callosum"]
        Queue[Message Queue]
    end
    
    subgraph LeftBrain["Left Brain - Tactical"]
        CE[Code Executor]
        TG[Test Generator]
        EC[Error Corrector]
        HV[Health Validator]
        CH[Commit Handler]
    end
    
    IR --> Queue
    WP --> Queue
    Queue --> CE
    Queue --> TG
```"""
    
    def _generate_pipeline_flow(self, definition: Dict) -> str:
        """Generate pipeline flow diagram"""
        pipeline_name = definition.get('name', 'Pipeline')
        stages = definition.get('stages', [])
        
        # Build mermaid diagram
        lines = ["```mermaid", "graph LR"]
        
        for i, stage in enumerate(stages):
            stage_id = f"S{i+1}"
            stage_name = stage.replace('_', ' ').title()
            lines.append(f"    {stage_id}[{stage_name}]")
            
            if i > 0:
                prev_id = f"S{i}"
                lines.append(f"    {prev_id} --> {stage_id}")
        
        lines.append("```")
        return '\n'.join(lines)
    
    def _generate_module_structure(self, definition: Dict) -> str:
        """Generate module structure diagram"""
        # TODO: Scan src/ directory to discover actual module structure
        # For now, return placeholder
        
        return """```mermaid
graph TB
    subgraph EPM["Entry Point Module"]
        Main[Main Orchestrator]
    end
    
    subgraph Modules["Generation Modules"]
        Valid[Validation Engine]
        Clean[Cleanup Manager]
        Diagram[Diagram Generator]
        Page[Page Generator]
        XRef[Cross-Reference Builder]
    end
    
    Main --> Valid
    Main --> Clean
    Main --> Diagram
    Main --> Page
    Main --> XRef
```"""
    
    def _generate_data_flow(self, definition: Dict) -> str:
        """Generate data flow diagram"""
        source = definition.get('source', 'Source')
        target = definition.get('target', 'Target')
        
        return f"""```mermaid
graph LR
    Source[{source}]
    Processing[Processing]
    Target[{target}]
    
    Source --> Processing
    Processing --> Target
```"""
