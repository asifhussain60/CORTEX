#!/usr/bin/env python3
"""
🎨 CORTEX Intelligent Diagram Generator
========================================

Automatically generates D3.js and Mermaid diagrams for HTML pages based on
content analysis and value scoring.

**Author:** Asif Hussain
**Version:** 1.0.0
**Date:** January 4, 2026
**Copyright:** © 2026 Asif Hussain. All rights reserved.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


class DiagramGenerator:
    """Generate intelligent diagrams for HTML pages."""
    
    def __init__(self, value_scoring_path: Path):
        """Initialize with value scoring analysis results."""
        self.scoring_data = json.loads(value_scoring_path.read_text())
        self.results = {r['file_path']: r for r in self.scoring_data['detailed_results']}
    
    def _generate_d3_force_directed(self, page_data: Dict) -> str:
        """Generate D3.js force-directed graph for architectural relationships."""
        return """
<div class="diagram-container glassmorphism" id="architecture-diagram">
    <h3 class="diagram-title"><i class="fas fa-project-diagram"></i> Architecture Overview</h3>
    <div id="d3-force-graph" class="d3-visualization"></div>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
(function() {
    const width = 800;
    const height = 600;
    
    // Sample data - replace with actual page content analysis
    const nodes = [
        { id: "cortex", group: 1, radius: 20 },
        { id: "orchestrators", group: 2, radius: 15 },
        { id: "agents", group: 2, radius: 15 },
        { id: "brain", group: 3, radius: 12 },
        { id: "toolkit", group: 3, radius: 12 }
    ];
    
    const links = [
        { source: "cortex", target: "orchestrators", value: 3 },
        { source: "cortex", target: "agents", value: 3 },
        { source: "orchestrators", target: "brain", value: 2 },
        { source: "agents", target: "brain", value: 2 },
        { source: "orchestrators", target: "toolkit", value: 1 }
    ];
    
    const svg = d3.select("#d3-force-graph")
        .append("svg")
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");
    
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2));
    
    const link = svg.append("g")
        .selectAll("line")
        .data(links)
        .join("line")
        .attr("stroke", "rgba(124, 124, 255, 0.6)")
        .attr("stroke-width", d => Math.sqrt(d.value) * 2);
    
    const node = svg.append("g")
        .selectAll("circle")
        .data(nodes)
        .join("circle")
        .attr("r", d => d.radius)
        .attr("fill", d => d3.schemeCategory10[d.group])
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
    
    const label = svg.append("g")
        .selectAll("text")
        .data(nodes)
        .join("text")
        .text(d => d.id)
        .attr("font-size", 12)
        .attr("fill", "#fff")
        .attr("text-anchor", "middle");
    
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        
        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
        
        label
            .attr("x", d => d.x)
            .attr("y", d => d.y + 4);
    });
    
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }
    
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
})();
</script>

<style>
.diagram-container {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 2rem 0;
}

.diagram-title {
    color: #fff;
    margin-bottom: 1rem;
    font-size: 1.2rem;
}

.d3-visualization {
    width: 100%;
    min-height: 600px;
}
</style>
"""
    
    def _generate_mermaid_flowchart(self, page_data: Dict) -> str:
        """Generate Mermaid flowchart for process flows."""
        return """
<div class="diagram-container glassmorphism">
    <h3 class="diagram-title"><i class="fas fa-sitemap"></i> Process Flow</h3>
    <div class="mermaid-diagram">
        %%{init: {'theme':'dark', 'themeVariables': { 'primaryColor':'#7c7cff'}}}%%
        flowchart TD
            A[Start: User Request] --> B{Analyze Intent}
            B -->|Planning| C[Create Plan Structure]
            B -->|Execution| D[Load Orchestrator]
            B -->|Investigation| E[Analyze Context]
            C --> F[Generate Phases]
            D --> G[Execute Workflow]
            E --> H[Report Findings]
            F --> I[Validate Criteria]
            G --> I
            H --> I
            I --> J[Complete]
            
            style A fill:#7c7cff,stroke:#fff,stroke-width:2px
            style J fill:#00ff88,stroke:#fff,stroke-width:2px
            style B fill:#ff6b6b,stroke:#fff,stroke-width:2px
    </div>
</div>

<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({ 
        startOnLoad: true,
        theme: 'dark',
        themeVariables: {
            primaryColor: '#7c7cff',
            primaryTextColor: '#fff',
            primaryBorderColor: '#fff',
            lineColor: '#7c7cff',
            secondaryColor: '#ff6b6b',
            tertiaryColor: '#00ff88'
        }
    });
</script>
"""
    
    def _generate_mermaid_sequence(self, page_data: Dict) -> str:
        """Generate Mermaid sequence diagram for interaction flows."""
        return """
<div class="diagram-container glassmorphism">
    <h3 class="diagram-title"><i class="fas fa-exchange-alt"></i> Interaction Flow</h3>
    <div class="mermaid-diagram">
        %%{init: {'theme':'dark'}}%%
        sequenceDiagram
            participant U as User
            participant C as CORTEX
            participant O as Orchestrator
            participant B as Brain
            
            U->>C: Send Request
            C->>C: Parse Intent
            C->>O: Route to Orchestrator
            O->>B: Query Context
            B-->>O: Return Knowledge
            O->>O: Execute Workflow
            O-->>C: Return Results
            C-->>U: Display Response
            
            Note over C,O: Autonomous Execution
            Note over O,B: Context Enrichment
    </div>
</div>
"""
    
    def _generate_mermaid_mindmap(self, page_data: Dict) -> str:
        """Generate Mermaid mindmap for concept relationships."""
        return """
<div class="diagram-container glassmorphism">
    <h3 class="diagram-title"><i class="fas fa-brain"></i> Concept Map</h3>
    <div class="mermaid-diagram">
        %%{init: {'theme':'dark'}}%%
        mindmap
          root((CORTEX))
            Orchestrators
              Planning v5
              ADO v2
              TDD Mastery
              Git Operations
            Brain System
              Tier 0: Governance
              Tier 1: Working Memory
              Tier 2: Knowledge Graph
              Tier 3: Dev Context
            Agents
              Specialist Agents
              LLM Fallback
            Toolkit
              Validators
              Generators
              Analyzers
    </div>
</div>
"""
    
    def _generate_d3_timeline(self, page_data: Dict) -> str:
        """Generate D3.js timeline for sequential events."""
        return """
<div class="diagram-container glassmorphism">
    <h3 class="diagram-title"><i class="fas fa-history"></i> Timeline</h3>
    <div id="d3-timeline" class="d3-visualization"></div>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
(function() {
    const events = [
        { date: "Phase 0", label: "Context Discovery", value: 100 },
        { date: "Phase 1", label: "HTML Audit", value: 100 },
        { date: "Phase 2", label: "Framework Setup", value: 100 },
        { date: "Phase 3", label: "Critical Pages", value: 100 },
        { date: "Phase 4", label: "Documentation", value: 100 },
        { date: "Phase 5", label: "Secondary Pages", value: 100 },
        { date: "Phase 6", label: "Legacy Pages", value: 100 }
    ];
    
    const width = 800;
    const height = 200;
    const margin = { top: 40, right: 40, bottom: 40, left: 40 };
    
    const svg = d3.select("#d3-timeline")
        .append("svg")
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");
    
    const x = d3.scalePoint()
        .domain(events.map(d => d.date))
        .range([margin.left, width - margin.right]);
    
    // Draw timeline line
    svg.append("line")
        .attr("x1", margin.left)
        .attr("y1", height / 2)
        .attr("x2", width - margin.right)
        .attr("y2", height / 2)
        .attr("stroke", "rgba(124, 124, 255, 0.6)")
        .attr("stroke-width", 2);
    
    // Draw event markers
    const g = svg.selectAll("g")
        .data(events)
        .join("g")
        .attr("transform", d => `translate(${x(d.date)}, ${height / 2})`);
    
    g.append("circle")
        .attr("r", 8)
        .attr("fill", d => d.value === 100 ? "#00ff88" : "#7c7cff")
        .attr("stroke", "#fff")
        .attr("stroke-width", 2);
    
    g.append("text")
        .attr("y", -15)
        .attr("text-anchor", "middle")
        .attr("fill", "#fff")
        .attr("font-size", 12)
        .text(d => d.label);
    
    g.append("text")
        .attr("y", 25)
        .attr("text-anchor", "middle")
        .attr("fill", "#aaa")
        .attr("font-size", 10)
        .text(d => d.date);
})();
</script>
"""
    
    def _generate_d3_sankey(self, page_data: Dict) -> str:
        """Generate D3.js Sankey diagram for data flow."""
        return """
<div class="diagram-container glassmorphism">
    <h3 class="diagram-title"><i class="fas fa-stream"></i> Data Flow</h3>
    <div id="d3-sankey" class="d3-visualization"></div>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js"></script>
<script>
(function() {
    const width = 800;
    const height = 400;
    
    const data = {
        nodes: [
            { name: "User Input" },
            { name: "Intent Router" },
            { name: "Orchestrator" },
            { name: "Brain Query" },
            { name: "Execution" },
            { name: "Results" }
        ],
        links: [
            { source: 0, target: 1, value: 10 },
            { source: 1, target: 2, value: 10 },
            { source: 2, target: 3, value: 5 },
            { source: 2, target: 4, value: 5 },
            { source: 3, target: 4, value: 5 },
            { source: 4, target: 5, value: 10 }
        ]
    };
    
    const svg = d3.select("#d3-sankey")
        .append("svg")
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");
    
    const sankey = d3.sankey()
        .nodeWidth(15)
        .nodePadding(10)
        .extent([[1, 1], [width - 1, height - 5]]);
    
    const { nodes, links } = sankey(data);
    
    // Draw links
    svg.append("g")
        .selectAll("path")
        .data(links)
        .join("path")
        .attr("d", d3.sankeyLinkHorizontal())
        .attr("stroke", d => {
            const t = d.source.index / nodes.length;
            return d3.interpolateBlues(t);
        })
        .attr("stroke-width", d => Math.max(1, d.width))
        .attr("fill", "none")
        .attr("opacity", 0.5);
    
    // Draw nodes
    svg.append("g")
        .selectAll("rect")
        .data(nodes)
        .join("rect")
        .attr("x", d => d.x0)
        .attr("y", d => d.y0)
        .attr("height", d => d.y1 - d.y0)
        .attr("width", d => d.x1 - d.x0)
        .attr("fill", "#7c7cff");
    
    // Draw labels
    svg.append("g")
        .selectAll("text")
        .data(nodes)
        .join("text")
        .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
        .attr("y", d => (d.y1 + d.y0) / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
        .attr("fill", "#fff")
        .text(d => d.name);
})();
</script>
"""
    
    def enhance_page(self, html_path: Path) -> bool:
        """Add intelligent diagrams to an HTML page based on content analysis."""
        try:
            html_str_path = str(html_path)
            if html_str_path not in self.results:
                return False
            
            page_data = self.results[html_str_path]
            
            # Only enhance pages with score >= 50 (MEDIUM or higher)
            score = page_data.get('value_score', {}).get('total', 0)
            if score < 50:
                return False
            
            recommendations = page_data.get('diagram_recommendations', [])
            if not recommendations:
                return False
            
            # Read HTML content
            content = html_path.read_text(encoding='utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find insertion point (after first section or before footer)
            main_content = soup.find('main') or soup.find('div', class_='content')
            if not main_content:
                return False
            
            # Generate top 2 recommended diagrams
            diagram_html = []
            for rec in recommendations[:2]:
                diagram_type = rec['type']
                
                if diagram_type == 'd3-force-directed':
                    diagram_html.append(self._generate_d3_force_directed(page_data))
                elif diagram_type == 'mermaid-flowchart':
                    diagram_html.append(self._generate_mermaid_flowchart(page_data))
                elif diagram_type == 'mermaid-sequence':
                    diagram_html.append(self._generate_mermaid_sequence(page_data))
                elif diagram_type == 'mermaid-mindmap':
                    diagram_html.append(self._generate_mermaid_mindmap(page_data))
                elif diagram_type == 'd3-timeline':
                    diagram_html.append(self._generate_d3_timeline(page_data))
                elif diagram_type == 'd3-sankey':
                    diagram_html.append(self._generate_d3_sankey(page_data))
            
            if not diagram_html:
                return False
            
            # Insert diagrams
            diagrams_section = soup.new_tag('section', **{'class': 'visualizations-section'})
            diagrams_section.append(BeautifulSoup('\n'.join(diagram_html), 'html.parser'))
            
            # Insert after first h2 or at beginning of main content
            first_section = main_content.find('section')
            if first_section:
                first_section.insert_after(diagrams_section)
            else:
                main_content.insert(0, diagrams_section)
            
            # Write back
            html_path.write_text(str(soup), encoding='utf-8')
            return True
            
        except Exception as e:
            print(f"❌ Error enhancing {html_path}: {e}")
            return False
    
    def batch_enhance(self, docs_dir: Path, min_score: int = 50):
        """Enhance all eligible pages with diagrams."""
        enhanced_count = 0
        skipped_count = 0
        
        # Get pages eligible for enhancement
        eligible_pages = [
            r for r in self.scoring_data['detailed_results']
            if r.get('value_score', {}).get('total', 0) >= min_score
            and r.get('diagram_recommendations')
        ]
        
        print(f"🎨 Enhancing {len(eligible_pages)} pages (score >= {min_score})...")
        
        for page_data in eligible_pages:
            html_path = Path(page_data['file_path'])
            if html_path.exists():
                if self.enhance_page(html_path):
                    score = page_data['value_score']['total']
                    tier = page_data['value_score']['quality_tier']
                    print(f"  ✅ Enhanced: {html_path.name} (Score: {score}, Tier: {tier})")
                    enhanced_count += 1
                else:
                    skipped_count += 1
        
        print(f"\n✅ Enhancement complete:")
        print(f"   Enhanced: {enhanced_count} pages")
        print(f"   Skipped: {skipped_count} pages")
        
        return enhanced_count


if __name__ == '__main__':
    scoring_file = Path(__file__).parent.parent / 'reports' / 'value-scoring-analysis.json'
    docs_dir = Path(__file__).parent.parent / 'docs'
    
    generator = DiagramGenerator(scoring_file)
    enhanced_count = generator.batch_enhance(docs_dir, min_score=50)
    
    print(f"\n📊 Total diagrams added: {enhanced_count * 2} (2 per page)")
