// ============================================================================
// CORTEX Registry Explorer - D3 Diagram Generators
// Force-directed graphs and workflow visualizations
// ============================================================================

/**
 * D3 Diagram Manager
 * Handles relationship graphs and workflow diagrams
 */
class DiagramGenerator {
    /**
     * Render relationship graph (force-directed)
     */
    static renderRelationshipGraph(graph, containerId) {
        console.log('renderRelationshipGraph called:', { graph, containerId, nodes: graph?.nodes?.length, links: graph?.links?.length });
        
        if (!graph || graph.nodes.length === 0) {
            console.log('No graph data, rendering empty state');
            return this.renderEmptyGraph(containerId);
        }

        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Container not found:', containerId);
            return;
        }

        // Clear existing
        container.innerHTML = '';

        // Create a proper container with fixed height for the graph
        const graphWrapper = document.createElement('div');
        graphWrapper.className = 'graph-container';
        graphWrapper.style.cssText = 'width: 100%; height: 600px; position: relative;';
        container.appendChild(graphWrapper);

        // Dimensions
        const width = graphWrapper.clientWidth || 800;
        const height = 600;

        // Create SVG in the wrapper
        const svg = d3.select(graphWrapper)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('class', 'graph-svg');

        // Add zoom behavior
        const g = svg.append('g');
        
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });
        
        svg.call(zoom);

        // Create arrow markers
        svg.append('defs').selectAll('marker')
            .data(['depends-on', 'transition', 'sequence'])
            .enter().append('marker')
            .attr('id', d => `arrow-${d}`)
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', d => this.getLinkColor(d));

        // Create force simulation
        const simulation = d3.forceSimulation(graph.nodes)
            .force('link', d3.forceLink(graph.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(50));

        // Create links
        const link = g.append('g')
            .selectAll('line')
            .data(graph.links)
            .enter().append('line')
            .attr('class', 'graph-link')
            .attr('stroke', d => this.getLinkColor(d.type))
            .attr('stroke-width', 2)
            .attr('marker-end', d => `url(#arrow-${d.type})`);

        // Create nodes
        const node = g.append('g')
            .selectAll('g')
            .data(graph.nodes)
            .enter().append('g')
            .attr('class', 'graph-node')
            .call(d3.drag()
                .on('start', (event, d) => this.dragstarted(event, d, simulation))
                .on('drag', (event, d) => this.dragged(event, d))
                .on('end', (event, d) => this.dragended(event, d, simulation)));

        // Add circles
        node.append('circle')
            .attr('r', d => this.getNodeRadius(d))
            .attr('fill', d => this.getNodeColor(d))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);

        // Add labels
        node.append('text')
            .text(d => d.label || d.id)
            .attr('x', 0)
            .attr('y', -20)
            .attr('text-anchor', 'middle')
            .attr('class', 'graph-label')
            .style('font-size', '11px')
            .style('fill', '#fff')
            .style('pointer-events', 'none');

        // Add tooltips
        node.append('title')
            .text(d => `${d.label || d.id}\nType: ${d.type}\nStatus: ${d.status || 'unknown'}`);

        // Update positions on tick
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node.attr('transform', d => `translate(${d.x},${d.y})`);
        });

        // Add legend
        this.addLegend(svg, width, graph);

        // Add controls
        this.addGraphControls(containerId, svg, simulation);
    }

    /**
     * Render workflow diagram (sequential flow)
     */
    static renderWorkflowDiagram(graph, containerId) {
        if (!graph || graph.nodes.length === 0) {
            return this.renderEmptyGraph(containerId);
        }

        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';

        const width = container.clientWidth || 800;
        const height = 400;

        const svg = d3.select(`#${containerId}`)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('class', 'workflow-svg');

        const g = svg.append('g');

        // Zoom
        const zoom = d3.zoom()
            .scaleExtent([0.5, 2])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });
        
        svg.call(zoom);

        // Calculate positions (left to right layout)
        const nodes = [...graph.nodes].sort((a, b) => (a.order || 0) - (b.order || 0));
        const stepWidth = Math.min(150, (width - 100) / nodes.length);
        const startX = 50;
        const y = height / 2;

        nodes.forEach((node, i) => {
            node.x = startX + i * stepWidth + stepWidth / 2;
            node.y = y;
        });

        // Create links
        const link = g.append('g')
            .selectAll('path')
            .data(graph.links)
            .enter().append('path')
            .attr('class', 'workflow-link')
            .attr('d', d => {
                const source = nodes.find(n => n.id === d.source || n.id === d.source.id);
                const target = nodes.find(n => n.id === d.target || n.id === d.target.id);
                if (!source || !target) return '';
                
                return `M ${source.x} ${source.y} L ${target.x} ${target.y}`;
            })
            .attr('stroke', d => d.type === 'transition' ? '#f59e0b' : '#00d4ff')
            .attr('stroke-width', 2)
            .attr('fill', 'none')
            .attr('marker-end', 'url(#workflow-arrow)');

        // Arrow marker
        svg.append('defs').append('marker')
            .attr('id', 'workflow-arrow')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 25)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#00d4ff');

        // Create nodes
        const node = g.append('g')
            .selectAll('g')
            .data(nodes)
            .enter().append('g')
            .attr('class', 'workflow-node')
            .attr('transform', d => `translate(${d.x},${d.y})`);

        // Add rectangles
        node.append('rect')
            .attr('width', stepWidth - 20)
            .attr('height', 60)
            .attr('x', -(stepWidth - 20) / 2)
            .attr('y', -30)
            .attr('rx', 8)
            .attr('fill', 'rgba(0, 212, 255, 0.2)')
            .attr('stroke', '#00d4ff')
            .attr('stroke-width', 2);

        // Add step numbers
        node.append('circle')
            .attr('r', 12)
            .attr('cy', -45)
            .attr('fill', '#7b61ff')
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);

        node.append('text')
            .text((d, i) => i + 1)
            .attr('y', -40)
            .attr('text-anchor', 'middle')
            .attr('class', 'workflow-number')
            .style('font-size', '10px')
            .style('font-weight', 'bold')
            .style('fill', '#fff');

        // Add labels
        node.append('text')
            .text(d => d.label || d.id)
            .attr('y', 5)
            .attr('text-anchor', 'middle')
            .attr('class', 'workflow-label')
            .style('font-size', '12px')
            .style('fill', '#fff')
            .each(function(d) {
                // Wrap text if too long
                const text = d3.select(this);
                const words = (d.label || d.id).split(/\s+/);
                if (words.length > 2) {
                    text.text('');
                    text.append('tspan')
                        .text(words.slice(0, 2).join(' '))
                        .attr('x', 0)
                        .attr('dy', 0);
                    text.append('tspan')
                        .text(words.slice(2).join(' '))
                        .attr('x', 0)
                        .attr('dy', '1.1em');
                }
            });

        // Add tooltips
        node.append('title')
            .text(d => `Step ${(d.order || 0) + 1}: ${d.label || d.id}`);
    }

    /**
     * Drag handlers
     */
    static dragstarted(event, d, simulation) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    static dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    static dragended(event, d, simulation) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    /**
     * Get node radius based on connections
     */
    static getNodeRadius(node) {
        return 15;
    }

    /**
     * Get node color based on type/status
     */
    static getNodeColor(node) {
        const statusColors = {
            'completed': '#10b981',
            'active': '#00d4ff',
            'planned': '#7b61ff',
            'deferred': '#6b7280',
            'unknown': '#374151'
        };

        return statusColors[node.status] || statusColors['unknown'];
    }

    /**
     * Get link color based on type
     */
    static getLinkColor(type) {
        const colors = {
            'depends-on': '#00d4ff',
            'transition': '#f59e0b',
            'sequence': '#10b981',
            'uses': '#7b61ff'
        };
        return colors[type] || '#6b7280';
    }

    /**
     * Add legend to graph
     */
    static addLegend(svg, width, graph) {
        const legend = svg.append('g')
            .attr('class', 'graph-legend')
            .attr('transform', `translate(${width - 150}, 20)`);

        // Get unique statuses
        const statuses = [...new Set(graph.nodes.map(n => n.status))];

        legend.append('rect')
            .attr('width', 140)
            .attr('height', 20 + statuses.length * 25)
            .attr('fill', 'rgba(0, 0, 0, 0.7)')
            .attr('rx', 4);

        legend.append('text')
            .text('Legend')
            .attr('x', 10)
            .attr('y', 15)
            .style('font-size', '12px')
            .style('font-weight', 'bold')
            .style('fill', '#fff');

        statuses.forEach((status, i) => {
            const item = legend.append('g')
                .attr('transform', `translate(10, ${30 + i * 25})`);

            item.append('circle')
                .attr('r', 6)
                .attr('fill', this.getNodeColor({ status }));

            item.append('text')
                .text(status)
                .attr('x', 15)
                .attr('y', 5)
                .style('font-size', '11px')
                .style('fill', '#fff');
        });
    }

    /**
     * Add graph controls
     */
    static addGraphControls(containerId, svg, simulation) {
        const controls = document.createElement('div');
        controls.className = 'graph-controls';
        controls.innerHTML = `
            <button class="graph-control-btn" onclick="resetZoom('${containerId}')" title="Reset Zoom">
                <span>🔍</span>
            </button>
            <button class="graph-control-btn" onclick="pauseSimulation('${containerId}')" title="Pause/Resume">
                <span id="pause-icon-${containerId}">⏸️</span>
            </button>
        `;
        
        document.getElementById(containerId).appendChild(controls);
    }

    /**
     * Render empty graph state
     */
    static renderEmptyGraph(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🕸️</div>
                <div class="empty-message">No relationships detected</div>
                <div class="empty-hint">Add dependency fields to entities to see connections</div>
            </div>
        `;
    }
}

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DiagramGenerator };
}
