/**
 * CORTEX Architecture D3.js Visualizations
 * Interactive force-directed graph for architecture overview
 * Version: 4.1.4 (Principles now use HTML cards per glassmorphism v4.1.4)
 * Author: Asif Hussain
 */

// ============================================
// Architecture Overview - Force-Directed Graph
// ============================================
function initArchitectureGraph() {
    const container = d3.select('#architecture-overview');
    const width = container.node().getBoundingClientRect().width;
    const height = 500;

    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);

    // Define gradient for links
    const defs = svg.append('defs');
    
    const gradient = defs.append('linearGradient')
        .attr('id', 'link-gradient')
        .attr('gradientUnits', 'userSpaceOnUse');
    
    gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', '#7b61ff')
        .attr('stop-opacity', 0.6);
    
    gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#00d4ff')
        .attr('stop-opacity', 0.6);

    // Data structure
    const nodes = [
        { id: 'cortex', label: 'CORTEX', icon: '\uf49e', size: 60, color: '#7b61ff', type: 'core' },
        
        // Brain Tiers
        { id: 't0', label: 'Tier 0\nSKULL', icon: '\uf3ed', size: 45, color: '#ef4444', type: 'brain' },
        { id: 't1', label: 'Tier 1\nMemory', icon: '\uf538', size: 45, color: '#10b981', type: 'brain' },
        { id: 't2', label: 'Tier 2\nGraph', icon: '\uf542', size: 45, color: '#3b82f6', type: 'brain' },
        { id: 't3', label: 'Tier 3\nContext', icon: '\uf201', size: 45, color: '#f59e0b', type: 'brain' },
        
        // Agents
        { id: 'planning', label: 'Planning\nAgent', icon: '\uf0ae', size: 40, color: '#06b6d4', type: 'agent' },
        { id: 'strategy', label: 'Strategic\nAgent', icon: '\uf439', size: 40, color: '#8b5cf6', type: 'agent' },
        
        // Orchestrators (sample)
        { id: 'plan-orch', label: 'Planning', icon: '\uf542', size: 35, color: '#14b8a6', type: 'orchestrator' },
        { id: 'tdd-orch', label: 'TDD', icon: '\uf560', size: 35, color: '#10b981', type: 'orchestrator' },
        { id: 'ado-orch', label: 'ADO', icon: '\uf46c', size: 35, color: '#3b82f6', type: 'orchestrator' },
        { id: 'debug-orch', label: 'Debug', icon: '\uf188', size: 35, color: '#f59e0b', type: 'orchestrator' }
    ];

    const links = [
        // CORTEX to tiers
        { source: 'cortex', target: 't0', strength: 1 },
        { source: 'cortex', target: 't1', strength: 1 },
        { source: 'cortex', target: 't2', strength: 1 },
        { source: 'cortex', target: 't3', strength: 1 },
        
        // CORTEX to agents
        { source: 'cortex', target: 'planning', strength: 0.8 },
        { source: 'cortex', target: 'strategy', strength: 0.8 },
        
        // Tier relationships
        { source: 't0', target: 't1', strength: 0.5 },
        { source: 't1', target: 't2', strength: 0.5 },
        { source: 't2', target: 't3', strength: 0.5 },
        
        // Agents to brain
        { source: 'planning', target: 't1', strength: 0.3 },
        { source: 'planning', target: 't2', strength: 0.3 },
        { source: 'strategy', target: 't2', strength: 0.3 },
        { source: 'strategy', target: 't3', strength: 0.3 },
        
        // Orchestrators to CORTEX
        { source: 'plan-orch', target: 'cortex', strength: 0.6 },
        { source: 'tdd-orch', target: 'cortex', strength: 0.6 },
        { source: 'ado-orch', target: 'cortex', strength: 0.6 },
        { source: 'debug-orch', target: 'cortex', strength: 0.6 },
        
        // Orchestrators to agents
        { source: 'plan-orch', target: 'planning', strength: 0.4 },
        { source: 'ado-orch', target: 'planning', strength: 0.4 },
        { source: 'debug-orch', target: 'strategy', strength: 0.4 }
    ];

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(120).strength(d => d.strength))
        .force('charge', d3.forceManyBody().strength(-400))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => d.size + 10));

    // Create links
    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .enter()
        .append('line')
        .attr('stroke', 'url(#link-gradient)')
        .attr('stroke-width', 2)
        .attr('opacity', 0.4);

    // Create node groups
    const node = svg.append('g')
        .selectAll('g')
        .data(nodes)
        .enter()
        .append('g')
        .attr('class', 'node')
        .style('cursor', 'pointer')
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragged)
            .on('end', dragEnded));

    // Node glow (for hover effect)
    node.append('circle')
        .attr('class', 'node-glow')
        .attr('r', d => d.size + 8)
        .attr('fill', d => d.color)
        .attr('opacity', 0)
        .attr('filter', 'blur(8px)');

    // Node circle background
    node.append('circle')
        .attr('r', d => d.size)
        .attr('fill', 'rgba(30, 41, 59, 0.8)')
        .attr('stroke', d => d.color)
        .attr('stroke-width', 3)
        .style('backdrop-filter', 'blur(12px)');

    // Node icon
    node.append('text')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .attr('font-family', 'Font Awesome 6 Free')
        .attr('font-weight', 900)
        .attr('font-size', d => d.size * 0.5 + 'px')
        .attr('fill', d => d.color)
        .attr('pointer-events', 'none')
        .text(d => d.icon);

    // Node label
    node.append('text')
        .attr('class', 'node-label')
        .attr('text-anchor', 'middle')
        .attr('y', d => d.size + 18)
        .attr('font-size', '11px')
        .attr('font-weight', '600')
        .attr('fill', '#e2e8f0')
        .attr('pointer-events', 'none')
        .each(function(d) {
            const lines = d.label.split('\n');
            const text = d3.select(this);
            lines.forEach((line, i) => {
                text.append('tspan')
                    .attr('x', 0)
                    .attr('dy', i === 0 ? 0 : '1.2em')
                    .text(line);
            });
        });

    // Hover interactions
    node.on('mouseenter', function(event, d) {
        d3.select(this).select('.node-glow')
            .transition()
            .duration(200)
            .attr('opacity', 0.4);
        
        d3.select(this).select('circle:not(.node-glow)')
            .transition()
            .duration(200)
            .attr('stroke-width', 5);
    })
    .on('mouseleave', function(event, d) {
        d3.select(this).select('.node-glow')
            .transition()
            .duration(200)
            .attr('opacity', 0);
        
        d3.select(this).select('circle:not(.node-glow)')
            .transition()
            .duration(200)
            .attr('stroke-width', 3);
    });

    // Update positions on simulation tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node.attr('transform', d => `translate(${d.x}, ${d.y})`);
    });

    // Drag functions
    function dragStarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragEnded(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // Legend
    const legendData = [
        { label: 'Core System', color: '#7b61ff' },
        { label: 'Brain Tiers', color: '#10b981' },
        { label: 'Agents', color: '#06b6d4' },
        { label: 'Orchestrators', color: '#14b8a6' }
    ];

    const legend = svg.append('g')
        .attr('class', 'legend')
        .attr('transform', `translate(20, ${height - 80})`);

    const legendItems = legend.selectAll('.legend-item')
        .data(legendData)
        .enter()
        .append('g')
        .attr('class', 'legend-item')
        .attr('transform', (d, i) => `translate(0, ${i * 24})`);

    legendItems.append('circle')
        .attr('r', 6)
        .attr('fill', d => d.color);

    legendItems.append('text')
        .attr('x', 16)
        .attr('y', 4)
        .attr('font-size', '12px')
        .attr('fill', '#94a3b8')
        .text(d => d.label);
}

// ============================================
// Initialize Visualizations
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Principles now use HTML cards (glassmorphism v4.1.4 Pattern D)
    // Only initialize force-directed graph
    initArchitectureGraph();
});
