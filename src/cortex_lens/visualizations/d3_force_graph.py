"""
CORTEX Lens v3.0 - D3.js Force Graph Visualization Template

Replaces Mermaid.js dependency graph with interactive D3.js force-directed graph.

Features:
- Force-directed layout with collision detection
- Node dragging and pinning
- Zoom and pan interactions
- Node filtering by type
- Hover tooltips with details
- Link strength visualization
- Export to PNG

Usage:
    from cortex_lens.visualizations.d3_force_graph import D3ForceGraph
    
    graph = D3ForceGraph(nodes, links)
    html = graph.render()
"""

from typing import List, Dict, Any
import json


class D3ForceGraph:
    """D3.js force-directed graph visualization."""
    
    def __init__(self, nodes: List[Dict[str, Any]], links: List[Dict[str, Any]]):
        """
        Initialize force graph.
        
        Args:
            nodes: List of node dicts with {id, label, type, group}
            links: List of link dicts with {source, target, value}
        """
        self.nodes = nodes
        self.links = links
    
    def render(self, container_id: str = 'force-graph', width: int = 1200, height: int = 800) -> str:
        """
        Render D3 force graph HTML.
        
        Args:
            container_id: HTML container ID
            width: Canvas width
            height: Canvas height
            
        Returns:
            HTML string with embedded D3.js visualization
        """
        nodes_json = json.dumps(self.nodes)
        links_json = json.dumps(self.links)
        
        html = f'''
<div id="{container_id}" class="d3-force-graph-container"></div>

<style>
.d3-force-graph-container {{
    width: 100%;
    height: {height}px;
    background: var(--color-bg-secondary);
    border-radius: var(--radius-lg);
    position: relative;
    overflow: hidden;
}}

.d3-force-graph-container svg {{
    display: block;
    width: 100%;
    height: 100%;
}}

.node {{
    cursor: pointer;
    transition: all 0.2s ease;
}}

.node:hover {{
    filter: brightness(1.3);
}}

.node circle {{
    stroke: var(--color-text-primary);
    stroke-width: 2px;
}}

.link {{
    stroke: var(--color-text-tertiary);
    stroke-opacity: 0.6;
    stroke-width: 1.5px;
}}

.link.dependency {{
    stroke: var(--color-primary);
}}

.link.import {{
    stroke: var(--color-accent);
}}

.node-label {{
    font-size: var(--font-size-sm);
    font-family: var(--font-family-base);
    fill: var(--color-text-primary);
    pointer-events: none;
    text-anchor: middle;
    dominant-baseline: central;
}}

.graph-tooltip {{
    position: absolute;
    background: var(--glass-bg-heavy);
    backdrop-filter: var(--blur-medium);
    border: 1px solid var(--glass-border-medium);
    border-radius: var(--radius-md);
    padding: var(--spacing-3);
    font-size: var(--font-size-sm);
    color: var(--color-text-primary);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s ease;
    z-index: 1000;
    max-width: 300px;
}}

.graph-tooltip.visible {{
    opacity: 1;
}}

.graph-controls {{
    position: absolute;
    top: var(--spacing-4);
    right: var(--spacing-4);
    display: flex;
    gap: var(--spacing-2);
}}

.graph-control-btn {{
    background: var(--glass-bg-medium);
    backdrop-filter: var(--blur-light);
    border: 1px solid var(--glass-border-light);
    border-radius: var(--radius-sm);
    padding: var(--spacing-2) var(--spacing-3);
    color: var(--color-text-primary);
    font-size: var(--font-size-sm);
    cursor: pointer;
    transition: var(--transition-all);
}}

.graph-control-btn:hover {{
    background: var(--glass-bg-heavy);
    border-color: var(--color-primary);
}}

.graph-legend {{
    position: absolute;
    bottom: var(--spacing-4);
    left: var(--spacing-4);
    background: var(--glass-bg-medium);
    backdrop-filter: var(--blur-light);
    border: 1px solid var(--glass-border-light);
    border-radius: var(--radius-md);
    padding: var(--spacing-3);
}}

.legend-item {{
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    margin-bottom: var(--spacing-2);
    font-size: var(--font-size-sm);
}}

.legend-item:last-child {{
    margin-bottom: 0;
}}

.legend-color {{
    width: 16px;
    height: 16px;
    border-radius: 50%;
}}
</style>

<script>
(function() {{
    'use strict';
    
    // Data
    const nodes = {nodes_json};
    const links = {links_json};
    
    // Configuration
    const width = {width};
    const height = {height};
    
    // Colors by node type
    const colorScale = {{
        'module': '#3b82f6',      // Primary
        'class': '#8b5cf6',       // Secondary
        'function': '#10b981',    // Accent
        'file': '#f59e0b',        // Warning
        'package': '#ec4899',     // Pink
        'default': '#6b7280'      // Gray
    }};
    
    // Create SVG
    const container = d3.select('#{container_id}');
    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Create tooltip
    const tooltip = container.append('div')
        .attr('class', 'graph-tooltip');
    
    // Create zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {{
            g.attr('transform', event.transform);
        }});
    
    svg.call(zoom);
    
    // Create main group
    const g = svg.append('g');
    
    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links)
            .id(d => d.id)
            .distance(100)
            .strength(0.5))
        .force('charge', d3.forceManyBody()
            .strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide()
            .radius(30));
    
    // Create links
    const link = g.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('class', d => `link ${{d.type || 'dependency'}}`)
        .attr('stroke-width', d => Math.sqrt(d.value || 1));
    
    // Create nodes
    const node = g.append('g')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .attr('class', 'node')
        .call(drag(simulation));
    
    // Add circles to nodes
    node.append('circle')
        .attr('r', d => d.size || 10)
        .attr('fill', d => colorScale[d.type] || colorScale.default);
    
    // Add labels to nodes
    node.append('text')
        .attr('class', 'node-label')
        .attr('dy', 25)
        .text(d => d.label || d.id);
    
    // Node hover effects
    node.on('mouseover', function(event, d) {{
        d3.select(this).select('circle')
            .transition()
            .duration(200)
            .attr('r', (d.size || 10) * 1.3);
        
        // Show tooltip
        tooltip
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px')
            .html(`
                <strong>${{d.label || d.id}}</strong><br/>
                Type: ${{d.type || 'unknown'}}<br/>
                Group: ${{d.group || 'none'}}<br/>
                Connections: ${{links.filter(l => l.source.id === d.id || l.target.id === d.id).length}}
            `)
            .classed('visible', true);
    }})
    .on('mouseout', function(event, d) {{
        d3.select(this).select('circle')
            .transition()
            .duration(200)
            .attr('r', d.size || 10);
        
        tooltip.classed('visible', false);
    }})
    .on('click', function(event, d) {{
        console.log('Node clicked:', d);
        // Emit custom event
        document.dispatchEvent(new CustomEvent('cortex:node-click', {{
            detail: {{ node: d }}
        }}));
    }});
    
    // Update positions on simulation tick
    simulation.on('tick', () => {{
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
    }});
    
    // Drag behavior
    function drag(simulation) {{
        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}
        
        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}
        
        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}
        
        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }}
    
    // Controls
    const controls = container.append('div')
        .attr('class', 'graph-controls');
    
    controls.append('button')
        .attr('class', 'graph-control-btn')
        .text('Reset Zoom')
        .on('click', () => {{
            svg.transition()
                .duration(750)
                .call(zoom.transform, d3.zoomIdentity);
        }});
    
    controls.append('button')
        .attr('class', 'graph-control-btn')
        .text('Restart Layout')
        .on('click', () => {{
            simulation.alpha(1).restart();
        }});
    
    // Legend
    const legend = container.append('div')
        .attr('class', 'graph-legend');
    
    Object.entries(colorScale).forEach(([type, color]) => {{
        if (type !== 'default') {{
            const item = legend.append('div')
                .attr('class', 'legend-item');
            
            item.append('div')
                .attr('class', 'legend-color')
                .style('background-color', color);
            
            item.append('span')
                .text(type.charAt(0).toUpperCase() + type.slice(1));
        }}
    }});
    
    // Expose API
    window.D3ForceGraph = {{
        simulation,
        svg,
        nodes,
        links,
        resetZoom: () => {{
            svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
        }},
        restartSimulation: () => {{
            simulation.alpha(1).restart();
        }},
        filterNodesByType: (type) => {{
            node.style('opacity', d => d.type === type || type === 'all' ? 1 : 0.2);
            link.style('opacity', d => {{
                return d.source.type === type || d.target.type === type || type === 'all' ? 0.6 : 0.1;
            }});
        }}
    }};
}})();
</script>
'''
        return html
    
    @staticmethod
    def sample_data():
        """Generate sample data for testing."""
        nodes = [
            {"id": "cortex", "label": "CORTEX", "type": "module", "size": 15},
            {"id": "tier0", "label": "Tier 0", "type": "module", "size": 12},
            {"id": "tier1", "label": "Tier 1", "type": "module", "size": 12},
            {"id": "tier2", "label": "Tier 2", "type": "module", "size": 12},
            {"id": "brain", "label": "Brain Protector", "type": "class", "size": 10},
            {"id": "orchestrator", "label": "Orchestrator", "type": "class", "size": 10},
            {"id": "agent", "label": "Agent", "type": "class", "size": 10},
            {"id": "utils", "label": "Utils", "type": "package", "size": 8},
        ]
        
        links = [
            {"source": "cortex", "target": "tier0", "value": 2, "type": "dependency"},
            {"source": "cortex", "target": "tier1", "value": 2, "type": "dependency"},
            {"source": "cortex", "target": "tier2", "value": 2, "type": "dependency"},
            {"source": "tier0", "target": "brain", "value": 1, "type": "import"},
            {"source": "tier1", "target": "orchestrator", "value": 1, "type": "import"},
            {"source": "tier2", "target": "agent", "value": 1, "type": "import"},
            {"source": "brain", "target": "utils", "value": 1, "type": "dependency"},
            {"source": "orchestrator", "target": "utils", "value": 1, "type": "dependency"},
        ]
        
        return nodes, links


if __name__ == '__main__':
    # Test rendering
    nodes, links = D3ForceGraph.sample_data()
    graph = D3ForceGraph(nodes, links)
    html = graph.render()
    
    print("D3 Force Graph HTML generated successfully")
    print(f"HTML length: {len(html)} characters")
