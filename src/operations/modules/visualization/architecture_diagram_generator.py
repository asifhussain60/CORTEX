"""
Architecture Diagram Generator - Visualize system architecture.

Generates architecture diagrams showing layers, components, and
their relationships.
"""

from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ArchitectureDiagramGenerator:
    """Generate architecture diagrams."""
    
    def __init__(self, ast_engine):
        """
        Initialize architecture diagram generator.
        
        Args:
            ast_engine: AST engine for architecture insights
        """
        self.ast_engine = ast_engine
        
        # Define architecture layers
        self.layers = {
            'presentation': ['cli', 'api', 'ui'],
            'orchestration': ['orchestrators', 'orchestration'],
            'intelligence': ['routing', 'analysis', 'learning', 'intelligence'],
            'infrastructure': ['tier0', 'tier1', 'tier2', 'tier3']
        }
        
    def generate_layer_diagram(self) -> str:
        """
        Generate layered architecture diagram.
        
        Returns:
            Mermaid diagram showing architectural layers
        """
        logger.info("Generating layered architecture diagram")
        
        lines = ["graph TB"]
        lines.append("    subgraph Presentation")
        lines.append("        CLI[CLI Interface]")
        lines.append("        API[REST API]")
        lines.append("    end")
        lines.append("")
        lines.append("    subgraph Orchestration")
        lines.append("        PLAN[Planning Orchestrator]")
        lines.append("        ADO[ADO Orchestrator]")
        lines.append("        TDD[TDD Orchestrator]")
        lines.append("        MAINT[Maintenance Orchestrator]")
        lines.append("    end")
        lines.append("")
        lines.append("    subgraph Intelligence")
        lines.append("        ROUTE[Tiered Router]")
        lines.append("        ANALYZE[Complexity Analyzer]")
        lines.append("        LEARN[Learning Subsystem]")
        lines.append("    end")
        lines.append("")
        lines.append("    subgraph Infrastructure")
        lines.append("        TIER0[Tier 0: Governance]")
        lines.append("        TIER1[Tier 1: Memory]")
        lines.append("        TIER2[Tier 2: Knowledge]")
        lines.append("    end")
        lines.append("")
        lines.append("    CLI --> ROUTE")
        lines.append("    ROUTE --> PLAN")
        lines.append("    ROUTE --> ADO")
        lines.append("    ROUTE --> TDD")
        lines.append("    PLAN --> TIER1")
        lines.append("    ANALYZE --> LEARN")
        lines.append("    MAINT --> TIER0")
        
        return "\n".join(lines)
        
    def generate_component_diagram(self, component: str) -> str:
        """
        Generate detailed component diagram.
        
        Args:
            component: Component name (e.g., "planning_orchestrator")
            
        Returns:
            Mermaid diagram showing component internals
        """
        logger.info(f"Generating component diagram for {component}")
        
        # Example for Planning Orchestrator
        if component == "planning_orchestrator":
            return """graph TD
    INPUT[User Request] --> CLASSIFY[Classify Tier]
    CLASSIFY --> ROUTE[Route to Execution Path]
    ROUTE --> TIER1[Tier 1: Instant]
    ROUTE --> TIER2[Tier 2: Lightweight]
    ROUTE --> TIER3[Tier 3: Documented]
    ROUTE --> TIER4[Tier 4: Complex]
    
    TIER3 --> REFACTOR[Refactor Cycle]
    TIER4 --> REFACTOR
    REFACTOR --> VACUUM[Vacuum Cycle]
    VACUUM --> DOC[Generate Documentation]
    DOC --> OUTPUT[Return Results]
    
    classDef instant fill:#c8e6c9
    classDef lightweight fill:#fff9c4
    classDef documented fill:#ffccbc
    classDef complex fill:#f8bbd0
    
    class TIER1 instant
    class TIER2 lightweight
    class TIER3 documented
    class TIER4 complex
"""
        
        # Generic fallback
        return f"""graph TD
    {component.upper()}["{component}"]
    INPUT[Input] --> {component.upper()}
    {component.upper()} --> OUTPUT[Output]
"""
