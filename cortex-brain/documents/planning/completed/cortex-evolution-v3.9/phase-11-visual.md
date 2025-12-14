# Phase 11: Visual Intelligence

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ⏳ Pending  
**Phase ID:** 11  
**Estimated Time:** 2 hours (120 minutes)  
**Actual Start:** -  
**Actual End:** -  
**Actual Work Time:** -  
**Dependencies:** Phase 08 (AST Engine Wrapper) ⏳, Phase 09 (Enhanced Analyzers) ⏳  
**Blocks:** None (standalone feature)

---

## 🎯 Phase Objective

Develop visual intelligence capabilities for automatic generation of dependency graphs, architecture diagrams, and progress visualizations using AST insights and orchestration metrics.

**Success Criteria:**
- ✅ Dependency graph generation (Mermaid/DOT formats)
- ✅ Architecture diagram automation
- ✅ Progress visualization for multi-phase operations
- ✅ Integration with AST Engine for structural insights
- ✅ Export formats: Markdown, SVG, PNG
- ✅ 100% test coverage with passing tests

---

## 🏗️ Implementation Plan

### Task 1: Dependency Graph Generator (1 hour)

**Create `src/operations/modules/visualization/dependency_graph_generator.py`:**

```python
"""
Dependency Graph Generator - Visualize module dependencies.

Generates dependency graphs in Mermaid and DOT formats using
AST analysis of import relationships.
"""

from pathlib import Path
from typing import Dict, Any, List, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DependencyNode:
    """Node in dependency graph."""
    name: str
    type: str  # "module", "class", "function"
    file_path: str
    dependencies: List[str]

class DependencyGraphGenerator:
    """Generate visual dependency graphs."""
    
    def __init__(self, ast_engine):
        self.ast_engine = ast_engine
        
    def generate_module_graph(
        self,
        target_path: Path = None,
        format: str = "mermaid"
    ) -> str:
        """
        Generate module-level dependency graph.
        
        Args:
            target_path: Specific directory or None for full project
            format: Output format ("mermaid", "dot", "json")
            
        Returns:
            Graph representation in specified format
        """
        logger.info(f"Generating module dependency graph (format: {format})")
        
        # Get architecture data from AST engine
        arch = self.ast_engine.analyze_architecture()
        module_graph = arch['module_graph']
        
        if format == "mermaid":
            return self._generate_mermaid_graph(module_graph)
        elif format == "dot":
            return self._generate_dot_graph(module_graph)
        elif format == "json":
            return self._generate_json_graph(module_graph)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _generate_mermaid_graph(self, module_graph: List[Dict]) -> str:
        """Generate Mermaid graph syntax."""
        lines = ["graph TD"]
        
        # Add nodes and edges
        edges_added = set()
        for edge in module_graph:
            from_module = edge['from'].replace('/', '_').replace('.', '_')
            to_module = edge['to'].replace('/', '_').replace('.', '_')
            
            edge_key = f"{from_module}-->{to_module}"
            if edge_key not in edges_added:
                lines.append(f"    {from_module}[{edge['from']}] --> {to_module}[{edge['to']}]")
                edges_added.add(edge_key)
                
        # Add styling for different module types
        lines.extend([
            "",
            "    classDef orchestrator fill:#e1f5ff,stroke:#01579b",
            "    classDef analyzer fill:#f3e5f5,stroke:#4a148c",
            "    classDef utility fill:#fff9c4,stroke:#f57f17"
        ])
        
        return "\n".join(lines)
        
    def _generate_dot_graph(self, module_graph: List[Dict]) -> str:
        """Generate Graphviz DOT format."""
        lines = ["digraph Dependencies {"]
        lines.append("    rankdir=LR;")
        lines.append("    node [shape=box];")
        
        for edge in module_graph:
            from_module = edge['from']
            to_module = edge['to']
            lines.append(f'    "{from_module}" -> "{to_module}";')
            
        lines.append("}")
        return "\n".join(lines)
        
    def detect_circular_dependencies(self) -> str:
        """
        Generate visualization highlighting circular dependencies.
        
        Returns:
            Mermaid graph with circular deps highlighted in red
        """
        arch = self.ast_engine.analyze_architecture()
        circular_deps = arch.get('circular_dependencies', [])
        
        lines = ["graph TD"]
        
        for cycle in circular_deps:
            # Highlight circular paths in red
            for i in range(len(cycle)):
                from_node = cycle[i].replace('/', '_').replace('.', '_')
                to_node = cycle[(i + 1) % len(cycle)].replace('/', '_').replace('.', '_')
                lines.append(
                    f"    {from_node}[{cycle[i]}] -->|CIRCULAR| {to_node}[{cycle[(i + 1) % len(cycle)]}]"
                )
                
        lines.append("    linkStyle default stroke:red,stroke-width:2px")
        
        return "\n".join(lines)
```

### Task 2: Architecture Diagram Generator (45 min)

**Create `src/operations/modules/visualization/architecture_diagram_generator.py`:**

```python
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
        self.ast_engine = ast_engine
        
        # Define architecture layers
        self.layers = {
            'presentation': ['cli', 'api', 'ui'],
            'orchestration': ['orchestrators', 'orchestration'],
            'intelligence': ['routing', 'analysis', 'learning'],
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
        
        return f"graph TD\n    {component}[Component: {component}]"
```

### Task 3: Progress Visualization (15 min)

**Create `src/operations/modules/visualization/progress_visualizer.py`:**

```python
"""
Progress Visualizer - Visual representations of operation progress.

Generates progress bars, phase timelines, and completion charts
for multi-phase operations.
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ProgressVisualizer:
    """Generate progress visualizations."""
    
    def generate_progress_bar(
        self,
        current: int,
        total: int,
        width: int = 50
    ) -> str:
        """
        Generate ASCII progress bar.
        
        Args:
            current: Current progress value
            total: Total progress value
            width: Bar width in characters
            
        Returns:
            ASCII progress bar string
        """
        percent = (current / total) * 100 if total > 0 else 0
        filled = int((current / total) * width) if total > 0 else 0
        bar = "█" * filled + "░" * (width - filled)
        
        return f"[{bar}] {percent:.0f}% ({current}/{total})"
        
    def generate_phase_timeline(
        self,
        phases: List[Dict[str, Any]]
    ) -> str:
        """
        Generate Gantt-style phase timeline.
        
        Args:
            phases: List of phase dicts with start, end, duration
            
        Returns:
            Mermaid Gantt chart
        """
        lines = ["gantt"]
        lines.append("    title CORTEX Evolution v3.9 - Phase Timeline")
        lines.append("    dateFormat YYYY-MM-DD HH:mm")
        lines.append("    section Foundation")
        
        for phase in phases:
            if phase.get('status') == 'complete':
                status = ":done"
            elif phase.get('status') == 'in_progress':
                status = ":active"
            else:
                status = ""
                
            start = phase.get('start', 'N/A')
            end = phase.get('end', 'N/A')
            
            if start != 'N/A' and end != 'N/A':
                lines.append(
                    f"    {phase['name']}{status} :{phase['id']}, {start}, {end}"
                )
                
        return "\n".join(lines)
        
    def generate_metrics_chart(
        self,
        metrics: Dict[str, Any]
    ) -> str:
        """
        Generate metrics visualization.
        
        Args:
            metrics: Dict of metric names to values
            
        Returns:
            ASCII bar chart
        """
        lines = ["Metrics Summary:"]
        lines.append("=" * 50)
        
        max_value = max(metrics.values()) if metrics else 1
        
        for name, value in metrics.items():
            bar_length = int((value / max_value) * 30)
            bar = "█" * bar_length
            lines.append(f"{name:.<30} {bar} {value}")
            
        return "\n".join(lines)
```

---

## 📦 Expected Deliverables

### Code Deliverables
- ✅ `src/operations/modules/visualization/dependency_graph_generator.py`
- ✅ `src/operations/modules/visualization/architecture_diagram_generator.py`
- ✅ `src/operations/modules/visualization/progress_visualizer.py`
- ✅ `src/operations/modules/visualization/__init__.py`

### Test Deliverables
- ✅ `tests/test_dependency_graph_generator.py`
- ✅ `tests/test_architecture_diagram_generator.py`
- ✅ `tests/test_progress_visualizer.py`
- ✅ Integration tests with real CORTEX data

### Documentation Deliverables
- ✅ Visualization usage guide
- ✅ Mermaid syntax reference
- ✅ Export format documentation
- ✅ Example visualizations gallery

---

## 🔄 Next Steps

1. **Phase 08-09 Completion:** AST Engine and analyzers must be operational
2. **Format Testing:** Validate Mermaid/DOT output renders correctly
3. **Integration:** Add visualization to orchestrator outputs
4. **Export Utilities:** Implement PNG/SVG export (optional enhancement)

---

## 🔗 Integration Points

### Upstream Dependencies
- **AST Engine (Phase 08):** Architecture and dependency data
- **Enhanced Analyzers (Phase 09):** Structural insights

### Downstream Consumers
- **Planning Orchestrator (Phase 03):** Progress visualization
- **Documentation (Phase 18):** Automatic diagram generation
- **System Maintenance (Phase 06):** Healthcheck visualizations

---

## 🚨 Risk Mitigation

### Risk 1: Mermaid Rendering Compatibility
**Mitigation:**
- Test with GitHub Markdown, VS Code extensions
- Provide fallback to DOT format
- Include syntax validation

### Risk 2: Large Graph Complexity
**Mitigation:**
- Implement graph simplification (hide low-level details)
- Support filtering by module/layer
- Paginated output for large graphs

---

## 📊 Success Metrics

- ✅ Dependency graphs render correctly in GitHub Markdown
- ✅ Architecture diagrams accurately represent CORTEX structure
- ✅ Progress visualization updates in <50ms
- ✅ Support for 3 output formats (Mermaid, DOT, JSON)
- ✅ User satisfaction ≥4.0/5.0 for visual clarity

---

**Phase Owner:** Asif Hussain  
**Phase Status:** ⏳ Awaiting Phase 08-09 completion  
**Last Updated:** 2024-12-14
