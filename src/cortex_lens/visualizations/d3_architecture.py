"""
CORTEX Lens v3.0 - D3.js Architecture Diagram Visualization

Interactive architecture diagram showing CORTEX component relationships.

Features:
- Hierarchical tree layout
- Collapsible nodes
- Module grouping
- Dependency visualization
- Zoom and pan
- Export capabilities

Usage:
    from cortex_lens.visualizations.d3_architecture import D3Architecture
    
    arch = D3Architecture(architecture_data)
    html = arch.render()
"""

from typing import Dict, Any, List
import json


class D3Architecture:
    """D3.js architecture diagram visualization."""
    
    def __init__(self, architecture: Dict[str, Any]):
        """
        Initialize architecture diagram.
        
        Args:
            architecture: Nested dict representing architecture hierarchy
        """
        self.architecture = architecture
    
    def render(self, container_id: str = 'architecture-diagram', width: int = 1400, height: int = 900) -> str:
        """
        Render D3 architecture diagram HTML.
        
        Args:
            container_id: HTML container ID
            width: Canvas width
            height: Canvas height
            
        Returns:
            HTML string with embedded D3.js visualization
        """
        arch_json = json.dumps(self.architecture)
        
        html = f'''
<div id="{container_id}" class="d3-architecture-container"></div>

<style>
.d3-architecture-container {{
    width: 100%;
    height: {height}px;
    background: var(--color-bg-secondary);
    border-radius: var(--radius-lg);
    position: relative;
    overflow: hidden;
}}

.d3-architecture-container svg {{
    display: block;
    width: 100%;
    height: 100%;
}}

.arch-node {{
    cursor: pointer;
}}

.arch-node rect {{
    fill: var(--glass-bg-medium);
    stroke: var(--color-primary);
    stroke-width: 2px;
    rx: var(--radius-md);
}}

.arch-node.collapsed rect {{
    fill: var(--glass-bg-light);
}}

.arch-node:hover rect {{
    fill: var(--glass-bg-heavy);
    stroke: var(--color-primary-light);
}}

.arch-node text {{
    font-size: var(--font-size-base);
    font-family: var(--font-family-base);
    fill: var(--color-text-primary);
    pointer-events: none;
}}

.arch-node .node-label {{
    font-weight: var(--font-weight-semibold);
}}

.arch-node .node-type {{
    font-size: var(--font-size-sm);
    fill: var(--color-text-secondary);
}}

.arch-link {{
    fill: none;
    stroke: var(--color-text-tertiary);
    stroke-opacity: 0.4;
    stroke-width: 2px;
}}

.arch-link.dependency {{
    stroke: var(--color-accent);
    stroke-dasharray: 5,5;
}}

.arch-badge {{
    font-size: var(--font-size-xs);
    fill: var(--color-text-tertiary);
}}

.arch-controls {{
    position: absolute;
    top: var(--spacing-4);
    right: var(--spacing-4);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2);
}}

.arch-control-btn {{
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

.arch-control-btn:hover {{
    background: var(--glass-bg-heavy);
    border-color: var(--color-primary);
}}

.arch-info-panel {{
    position: absolute;
    bottom: var(--spacing-4);
    left: var(--spacing-4);
    right: var(--spacing-4);
    background: var(--glass-bg-medium);
    backdrop-filter: var(--blur-medium);
    border: 1px solid var(--glass-border-medium);
    border-radius: var(--radius-md);
    padding: var(--spacing-4);
    max-height: 150px;
    overflow-y: auto;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}}

.arch-info-panel.visible {{
    opacity: 1;
    pointer-events: auto;
}}

.arch-info-title {{
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
    margin-bottom: var(--spacing-2);
}}

.arch-info-details {{
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    line-height: 1.6;
}}
</style>

<script>
(function() {{
    'use strict';
    
    // Data
    const data = {arch_json};
    
    // Configuration
    const width = {width};
    const height = {height};
    const nodeWidth = 180;
    const nodeHeight = 60;
    const verticalSpacing = 120;
    const horizontalSpacing = 200;
    
    // Create SVG
    const container = d3.select('#{container_id}');
    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Create zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 3])
        .on('zoom', (event) => {{
            g.attr('transform', event.transform);
        }});
    
    svg.call(zoom);
    
    // Create main group
    const g = svg.append('g');
    
    // Create tree layout
    const treeLayout = d3.tree()
        .nodeSize([nodeWidth + horizontalSpacing, nodeHeight + verticalSpacing]);
    
    // Create hierarchy
    const root = d3.hierarchy(data);
    
    // Apply layout
    treeLayout(root);
    
    // Create links
    const link = g.selectAll('.arch-link')
        .data(root.links())
        .join('path')
        .attr('class', d => `arch-link ${{d.target.data.linkType || 'hierarchy'}}`)
        .attr('d', d3.linkVertical()
            .x(d => d.x)
            .y(d => d.y));
    
    // Create nodes
    const node = g.selectAll('.arch-node')
        .data(root.descendants())
        .join('g')
        .attr('class', d => `arch-node ${{d.children ? '' : 'leaf'}}`)
        .attr('transform', d => `translate(${{d.x}},${{d.y}})`);
    
    // Add rectangles to nodes
    node.append('rect')
        .attr('x', -nodeWidth / 2)
        .attr('y', -nodeHeight / 2)
        .attr('width', nodeWidth)
        .attr('height', nodeHeight);
    
    // Add labels to nodes
    node.append('text')
        .attr('class', 'node-label')
        .attr('dy', -5)
        .attr('text-anchor', 'middle')
        .text(d => d.data.name);
    
    // Add type badges
    node.append('text')
        .attr('class', 'node-type')
        .attr('dy', 15)
        .attr('text-anchor', 'middle')
        .text(d => d.data.type || '');
    
    // Add child count badges
    node.filter(d => d.children)
        .append('text')
        .attr('class', 'arch-badge')
        .attr('x', nodeWidth / 2 - 5)
        .attr('y', nodeHeight / 2 - 5)
        .attr('text-anchor', 'end')
        .text(d => `${{d.children.length}} children`);
    
    // Info panel
    const infoPanel = container.append('div')
        .attr('class', 'arch-info-panel');
    
    // Node interactions
    node.on('click', function(event, d) {{
        event.stopPropagation();
        
        // Toggle collapse
        if (d.children) {{
            d._children = d.children;
            d.children = null;
            d3.select(this).classed('collapsed', true);
        }} else if (d._children) {{
            d.children = d._children;
            d._children = null;
            d3.select(this).classed('collapsed', false);
        }}
        
        // Update layout
        update(d);
        
        // Show info
        showInfo(d.data);
    }});
    
    node.on('mouseover', function(event, d) {{
        d3.select(this).select('rect')
            .transition()
            .duration(200)
            .attr('width', nodeWidth * 1.1)
            .attr('height', nodeHeight * 1.1)
            .attr('x', -nodeWidth * 1.1 / 2)
            .attr('y', -nodeHeight * 1.1 / 2);
    }});
    
    node.on('mouseout', function(event, d) {{
        d3.select(this).select('rect')
            .transition()
            .duration(200)
            .attr('width', nodeWidth)
            .attr('height', nodeHeight)
            .attr('x', -nodeWidth / 2)
            .attr('y', -nodeHeight / 2);
    }});
    
    // Update function for dynamic layout changes
    function update(source) {{
        const duration = 750;
        
        // Recompute layout
        treeLayout(root);
        
        // Update links
        const links = root.links();
        
        const linkUpdate = g.selectAll('.arch-link')
            .data(links, d => d.target.data.name);
        
        linkUpdate.exit()
            .transition()
            .duration(duration)
            .style('opacity', 0)
            .remove();
        
        linkUpdate.enter()
            .append('path')
            .attr('class', d => `arch-link ${{d.target.data.linkType || 'hierarchy'}}`)
            .style('opacity', 0)
            .merge(linkUpdate)
            .transition()
            .duration(duration)
            .style('opacity', 1)
            .attr('d', d3.linkVertical()
                .x(d => d.x)
                .y(d => d.y));
        
        // Update nodes
        const nodes = root.descendants();
        
        const nodeUpdate = g.selectAll('.arch-node')
            .data(nodes, d => d.data.name);
        
        nodeUpdate.exit()
            .transition()
            .duration(duration)
            .style('opacity', 0)
            .remove();
        
        const nodeEnter = nodeUpdate.enter()
            .append('g')
            .attr('class', d => `arch-node ${{d.children ? '' : 'leaf'}}`)
            .attr('transform', d => `translate(${{source.x}},${{source.y}})`)
            .style('opacity', 0);
        
        nodeEnter.append('rect')
            .attr('x', -nodeWidth / 2)
            .attr('y', -nodeHeight / 2)
            .attr('width', nodeWidth)
            .attr('height', nodeHeight);
        
        nodeEnter.append('text')
            .attr('class', 'node-label')
            .attr('dy', -5)
            .attr('text-anchor', 'middle')
            .text(d => d.data.name);
        
        nodeEnter.append('text')
            .attr('class', 'node-type')
            .attr('dy', 15)
            .attr('text-anchor', 'middle')
            .text(d => d.data.type || '');
        
        nodeEnter.merge(nodeUpdate)
            .transition()
            .duration(duration)
            .attr('transform', d => `translate(${{d.x}},${{d.y}})`)
            .style('opacity', 1);
    }}
    
    // Show info panel
    function showInfo(nodeData) {{
        const title = nodeData.name;
        const details = `
            <strong>Type:</strong> ${{nodeData.type || 'Unknown'}}<br/>
            <strong>Description:</strong> ${{nodeData.description || 'No description'}}<br/>
            <strong>Files:</strong> ${{nodeData.fileCount || 0}}<br/>
            <strong>LOC:</strong> ${{nodeData.loc || 0}}
        `;
        
        infoPanel.html(`
            <div class="arch-info-title">${{title}}</div>
            <div class="arch-info-details">${{details}}</div>
        `).classed('visible', true);
        
        setTimeout(() => {{
            infoPanel.classed('visible', false);
        }}, 5000);
    }}
    
    // Controls
    const controls = container.append('div')
        .attr('class', 'arch-controls');
    
    controls.append('button')
        .attr('class', 'arch-control-btn')
        .text('Reset Zoom')
        .on('click', () => {{
            svg.transition()
                .duration(750)
                .call(zoom.transform, d3.zoomIdentity.translate(width / 2, 100).scale(0.8));
        }});
    
    controls.append('button')
        .attr('class', 'arch-control-btn')
        .text('Expand All')
        .on('click', () => {{
            root.descendants().forEach(d => {{
                if (d._children) {{
                    d.children = d._children;
                    d._children = null;
                }}
            }});
            update(root);
        }});
    
    controls.append('button')
        .attr('class', 'arch-control-btn')
        .text('Collapse All')
        .on('click', () => {{
            root.descendants().forEach(d => {{
                if (d.children && d.depth > 0) {{
                    d._children = d.children;
                    d.children = null;
                }}
            }});
            update(root);
        }});
    
    // Initial zoom
    svg.call(zoom.transform, d3.zoomIdentity.translate(width / 2, 100).scale(0.8));
    
    // Expose API
    window.D3Architecture = {{
        root,
        svg,
        update,
        resetZoom: () => {{
            svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity.translate(width / 2, 100).scale(0.8));
        }},
        expandAll: () => {{
            root.descendants().forEach(d => {{
                if (d._children) {{
                    d.children = d._children;
                    d._children = null;
                }}
            }});
            update(root);
        }},
        collapseAll: () => {{
            root.descendants().forEach(d => {{
                if (d.children && d.depth > 0) {{
                    d._children = d.children;
                    d.children = null;
                }}
            }});
            update(root);
        }}
    }};
}})();
</script>
'''
        return html
    
    @staticmethod
    def sample_data():
        """Generate sample CORTEX architecture data."""
        return {
            "name": "CORTEX",
            "type": "System",
            "description": "AI Assistant with long-term memory",
            "fileCount": 150,
            "loc": 15000,
            "children": [
                {
                    "name": "cortex-brain",
                    "type": "Module",
                    "description": "4-tier memory system",
                    "fileCount": 50,
                    "loc": 5000,
                    "children": [
                        {"name": "tier0", "type": "Package", "description": "Governance", "fileCount": 10, "loc": 1000},
                        {"name": "tier1", "type": "Package", "description": "Working memory", "fileCount": 15, "loc": 1500},
                        {"name": "tier2", "type": "Package", "description": "Knowledge graph", "fileCount": 15, "loc": 1500},
                        {"name": "tier3", "type": "Package", "description": "Dev context", "fileCount": 10, "loc": 1000}
                    ]
                },
                {
                    "name": "src",
                    "type": "Module",
                    "description": "Core implementation",
                    "fileCount": 60,
                    "loc": 6000,
                    "children": [
                        {"name": "cortex_agents", "type": "Package", "description": "2 agents", "fileCount": 10, "loc": 1200},
                        {"name": "orchestrators", "type": "Package", "description": "8 workflows", "fileCount": 20, "loc": 2500},
                        {"name": "operations", "type": "Package", "description": "Core operations", "fileCount": 15, "loc": 1500},
                        {"name": "cortex_lens", "type": "Package", "description": "Visualization dashboard", "fileCount": 15, "loc": 800}
                    ]
                },
                {
                    "name": "tests",
                    "type": "Module",
                    "description": "Test suite",
                    "fileCount": 40,
                    "loc": 4000,
                    "children": [
                        {"name": "unit", "type": "Package", "description": "Unit tests", "fileCount": 20, "loc": 2000},
                        {"name": "integration", "type": "Package", "description": "Integration tests", "fileCount": 15, "loc": 1500},
                        {"name": "e2e", "type": "Package", "description": "End-to-end tests", "fileCount": 5, "loc": 500}
                    ]
                }
            ]
        }


if __name__ == '__main__':
    # Test rendering
    arch = D3Architecture(D3Architecture.sample_data())
    html = arch.render()
    
    print("D3 Architecture Diagram HTML generated successfully")
    print(f"HTML length: {len(html)} characters")
