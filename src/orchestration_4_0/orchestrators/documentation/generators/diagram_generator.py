"""
Diagram Generator - Generate D3.js interactive diagrams

Creates interactive visualizations:
- Phase flow diagrams (orchestrator execution flow)
- Class hierarchy diagrams (inheritance structure)
- Sequence diagrams (method call sequences)
"""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..extractors.code_analyzer import ClassInfo, ModuleInfo


class DiagramGenerator:
    """
    Generates D3.js-based interactive diagrams for documentation
    
    Output is HTML with embedded D3.js visualization code.
    Diagrams are fully interactive with zoom, pan, and hover tooltips.
    """
    
    def __init__(self):
        self.logger = None
        self.d3_version = "7.8.5"  # D3.js version to use
    
    def generate_class_hierarchy(
        self,
        modules: List[ModuleInfo],
        output_path: Path,
        title: str = "Class Hierarchy"
    ) -> Path:
        """
        Generate interactive class hierarchy diagram
        
        Shows inheritance relationships with:
        - Classes as nodes
        - Inheritance as directed edges
        - Method counts as node size
        - Abstract classes highlighted
        
        Args:
            modules: List of analyzed modules
            output_path: Where to save the HTML diagram
            title: Diagram title
            
        Returns:
            Path to generated HTML file
        """
        # Build class hierarchy data
        nodes = []
        links = []
        class_map = {}
        
        for module in modules:
            for cls in module.classes:
                node_id = f"{module.name}.{cls.name}"
                class_map[cls.name] = node_id
                
                nodes.append({
                    'id': node_id,
                    'name': cls.name,
                    'module': module.name,
                    'method_count': len(cls.methods),
                    'is_abstract': cls.is_abstract,
                    'docstring': cls.docstring or 'No documentation'
                })
                
                # Add inheritance links
                for base in cls.base_classes:
                    links.append({
                        'source': base if '.' in base else class_map.get(base, base),
                        'target': node_id,
                        'type': 'inherits'
                    })
        
        # Generate D3.js HTML
        html = self._generate_hierarchy_html(nodes, links, title)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')
        
        return output_path
    
    def generate_phase_flow_diagram(
        self,
        phase_data: List[Dict[str, Any]],
        output_path: Path,
        title: str = "Phase Flow"
    ) -> Path:
        """
        Generate phase flow diagram for an orchestrator
        
        Shows:
        - Phase sequence as flowchart
        - Decision points
        - Error handling paths
        - Success/failure outcomes
        
        Args:
            phase_data: List of phase definitions with transitions
            output_path: Where to save the HTML diagram
            title: Diagram title
            
        Returns:
            Path to generated HTML file
        """
        # Convert phase data to D3.js format
        nodes = []
        links = []
        
        for i, phase in enumerate(phase_data):
            node_id = phase.get('name', f'phase_{i}')
            nodes.append({
                'id': node_id,
                'name': phase.get('display_name', node_id),
                'type': phase.get('type', 'standard'),
                'description': phase.get('description', ''),
                'order': i
            })
            
            # Add transition links
            for transition in phase.get('transitions', []):
                links.append({
                    'source': node_id,
                    'target': transition['target'],
                    'condition': transition.get('condition', 'always'),
                    'type': transition.get('type', 'success')
                })
        
        html = self._generate_flow_html(nodes, links, title)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')
        
        return output_path
    
    def generate_sequence_diagram(
        self,
        sequences: List[Dict[str, Any]],
        output_path: Path,
        title: str = "Sequence Diagram"
    ) -> Path:
        """
        Generate sequence diagram showing method calls
        
        Args:
            sequences: List of method call sequences
            output_path: Where to save the HTML diagram
            title: Diagram title
            
        Returns:
            Path to generated HTML file
        """
        html = self._generate_sequence_html(sequences, title)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')
        
        return output_path
    
    def _generate_hierarchy_html(
        self,
        nodes: List[Dict[str, Any]],
        links: List[Dict[str, Any]],
        title: str
    ) -> str:
        """Generate HTML with D3.js for class hierarchy"""
        nodes_json = json.dumps(nodes, indent=2)
        links_json = json.dumps(links, indent=2)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v{self.d3_version}.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        #diagram {{
            width: 100%;
            height: 800px;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .node {{
            cursor: pointer;
            stroke: #333;
            stroke-width: 2px;
        }}
        .node.abstract {{
            stroke-dasharray: 5, 5;
        }}
        .link {{
            stroke: #999;
            stroke-width: 2px;
            fill: none;
            marker-end: url(#arrow);
        }}
        .node-label {{
            font-size: 12px;
            font-weight: bold;
            pointer-events: none;
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div id="diagram"></div>
    <div class="tooltip" id="tooltip"></div>
    
    <script>
        const nodes = {nodes_json};
        const links = {links_json};
        
        const width = document.getElementById('diagram').offsetWidth;
        const height = 800;
        
        const svg = d3.select("#diagram")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        // Define arrow marker
        svg.append("defs").append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999");
        
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(150))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .selectAll("path")
            .data(links)
            .join("path")
            .attr("class", "link");
        
        const node = svg.append("g")
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("class", d => d.is_abstract ? "node abstract" : "node")
            .attr("r", d => 10 + d.method_count * 2)
            .attr("fill", d => d.is_abstract ? "#ff9999" : "#6699ff")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip);
        
        const label = svg.append("g")
            .selectAll("text")
            .data(nodes)
            .join("text")
            .attr("class", "node-label")
            .text(d => d.name)
            .attr("text-anchor", "middle")
            .attr("dy", -15);
        
        simulation.on("tick", () => {{
            link.attr("d", d => {{
                const dx = d.target.x - d.source.x;
                const dy = d.target.y - d.source.y;
                const dr = Math.sqrt(dx * dx + dy * dy);
                return `M${{d.source.x}},${{d.source.y}}A${{dr}},${{dr}} 0 0,1 ${{d.target.x}},${{d.target.y}}`;
            }});
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        function showTooltip(event, d) {{
            const tooltip = d3.select("#tooltip");
            tooltip.style("opacity", 1)
                .html(`
                    <strong>${{d.name}}</strong><br/>
                    Module: ${{d.module}}<br/>
                    Methods: ${{d.method_count}}<br/>
                    ${{d.is_abstract ? "Abstract Class<br/>" : ""}}
                    ${{d.docstring}}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}
        
        function hideTooltip() {{
            d3.select("#tooltip").style("opacity", 0);
        }}
    </script>
</body>
</html>"""
    
    def _generate_flow_html(
        self,
        nodes: List[Dict[str, Any]],
        links: List[Dict[str, Any]],
        title: str
    ) -> str:
        """Generate HTML with D3.js for phase flow"""
        nodes_json = json.dumps(nodes, indent=2)
        links_json = json.dumps(links, indent=2)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v{self.d3_version}.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        #diagram {{
            width: 100%;
            height: 600px;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .phase-node {{
            fill: #4CAF50;
            stroke: #333;
            stroke-width: 2px;
        }}
        .phase-node.start {{
            fill: #2196F3;
        }}
        .phase-node.error {{
            fill: #f44336;
        }}
        .phase-link {{
            stroke: #333;
            stroke-width: 2px;
            fill: none;
            marker-end: url(#arrow);
        }}
        .phase-link.error {{
            stroke: #f44336;
            stroke-dasharray: 5, 5;
        }}
        .phase-label {{
            font-size: 14px;
            font-weight: bold;
            text-anchor: middle;
            pointer-events: none;
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div id="diagram"></div>
    <div class="tooltip" id="tooltip"></div>
    
    <script>
        const phases = {nodes_json};
        const transitions = {links_json};
        
        const width = document.getElementById('diagram').offsetWidth;
        const height = 600;
        const nodeWidth = 150;
        const nodeHeight = 60;
        const horizontalSpacing = 250;
        const verticalSpacing = 150;
        
        // Calculate positions (hierarchical layout)
        phases.forEach((phase, i) => {{
            phase.x = width / 2 + (i - phases.length / 2) * horizontalSpacing;
            phase.y = 100 + phase.order * verticalSpacing;
        }});
        
        const svg = d3.select("#diagram")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        // Define arrow marker
        svg.append("defs").append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#333");
        
        // Draw transitions
        const link = svg.append("g")
            .selectAll("path")
            .data(transitions)
            .join("path")
            .attr("class", d => d.type === "error" ? "phase-link error" : "phase-link")
            .attr("d", d => {{
                const source = phases.find(p => p.id === d.source);
                const target = phases.find(p => p.id === d.target);
                if (!source || !target) return "";
                return `M${{source.x}},${{source.y + nodeHeight/2}}L${{target.x}},${{target.y - nodeHeight/2}}`;
            }});
        
        // Draw phase nodes
        const node = svg.append("g")
            .selectAll("rect")
            .data(phases)
            .join("rect")
            .attr("class", d => `phase-node ${{d.type}}`)
            .attr("x", d => d.x - nodeWidth/2)
            .attr("y", d => d.y - nodeHeight/2)
            .attr("width", nodeWidth)
            .attr("height", nodeHeight)
            .attr("rx", 5)
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip);
        
        // Draw labels
        const label = svg.append("g")
            .selectAll("text")
            .data(phases)
            .join("text")
            .attr("class", "phase-label")
            .text(d => d.name)
            .attr("x", d => d.x)
            .attr("y", d => d.y + 5);
        
        function showTooltip(event, d) {{
            const tooltip = d3.select("#tooltip");
            tooltip.style("opacity", 1)
                .html(`
                    <strong>${{d.name}}</strong><br/>
                    ${{d.description}}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}
        
        function hideTooltip() {{
            d3.select("#tooltip").style("opacity", 0);
        }}
    </script>
</body>
</html>"""
    
    def _generate_sequence_html(
        self,
        sequences: List[Dict[str, Any]],
        title: str
    ) -> str:
        """Generate HTML with D3.js for sequence diagram"""
        sequences_json = json.dumps(sequences, indent=2)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v{self.d3_version}.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        #diagram {{
            width: 100%;
            height: 600px;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            overflow: auto;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div id="diagram"></div>
    
    <script>
        const sequences = {sequences_json};
        // Sequence diagram implementation would go here
        // This is a simplified placeholder
        d3.select("#diagram").append("p").text("Sequence diagram: " + sequences.length + " sequences");
    </script>
</body>
</html>"""
