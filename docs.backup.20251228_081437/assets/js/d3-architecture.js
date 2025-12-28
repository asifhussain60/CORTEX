/**
 * D3.js 4-Tier Architecture Visualization
 * Renders interactive vertical stack diagram with tier details
 */

function renderTierVisualization() {
    const container = document.getElementById('tier-visualization');
    const width = container.clientWidth;
    const height = 600;
    
    // Clear existing content
    container.innerHTML = '';
    
    // Create SVG
    const svg = d3.select('#tier-visualization')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Define tier data with real metrics from narratives
    const tiers = [
        {
            id: 'tier0',
            name: 'Tier 0: Governance',
            color: '#ffc107',
            description: '22 immutable SKULL rules',
            metrics: ['22 Rules', '100% Enforcement', '<10ms Access'],
            y: 50,
            height: 100
        },
        {
            id: 'tier1',
            name: 'Tier 1: Working Memory',
            color: '#00d4ff',
            description: '70 conversations in FIFO queue',
            metrics: ['70 Conversations', '<100ms Query', 'FIFO Mechanism'],
            y: 180,
            height: 100
        },
        {
            id: 'tier2',
            name: 'Tier 2: Knowledge Graph',
            color: '#7b61ff',
            description: 'Long-term pattern learning',
            metrics: ['8,429 Nodes', '24,817 Connections', 'Hebbian Learning'],
            y: 310,
            height: 100
        },
        {
            id: 'tier3',
            name: 'Tier 3: Development Context',
            color: '#2196f3',
            description: 'Real-time project tracking',
            metrics: ['Git Activity', 'Code Metrics', 'Hotspot Detection'],
            y: 440,
            height: 100
        }
    ];
    
    // Create tier groups
    const tierGroups = svg.selectAll('.tier-group')
        .data(tiers)
        .enter()
        .append('g')
        .attr('class', 'tier-group')
        .attr('transform', (d, i) => `translate(50, ${d.y})`)
        .style('cursor', 'pointer')
        .on('click', function(event, d) {
            showTierDetails(d);
        })
        .on('mouseenter', function(event, d) {
            d3.select(this).select('rect')
                .transition()
                .duration(200)
                .attr('filter', 'url(#glow)');
        })
        .on('mouseleave', function(event, d) {
            d3.select(this).select('rect')
                .transition()
                .duration(200)
                .attr('filter', 'none');
        });
    
    // Define glow filter
    const defs = svg.append('defs');
    const filter = defs.append('filter')
        .attr('id', 'glow');
    
    filter.append('feGaussianBlur')
        .attr('stdDeviation', '5')
        .attr('result', 'coloredBlur');
    
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');
    
    // Draw tier rectangles with glassmorphism
    tierGroups.append('rect')
        .attr('width', width - 100)
        .attr('height', d => d.height)
        .attr('rx', 12)
        .attr('fill', d => d.color)
        .attr('fill-opacity', 0.15)
        .attr('stroke', d => d.color)
        .attr('stroke-width', 2);
    
    // Add tier names
    tierGroups.append('text')
        .attr('x', 20)
        .attr('y', 35)
        .attr('fill', d => d.color)
        .style('font-size', '1.25rem')
        .style('font-weight', '700')
        .text(d => d.name);
    
    // Add tier descriptions
    tierGroups.append('text')
        .attr('x', 20)
        .attr('y', 60)
        .attr('fill', '#9ca3af')
        .style('font-size', '0.875rem')
        .text(d => d.description);
    
    // Add metrics badges
    tierGroups.each(function(d, i) {
        const group = d3.select(this);
        d.metrics.forEach((metric, index) => {
            const badge = group.append('g')
                .attr('transform', `translate(${20 + index * 180}, 75)`);
            
            badge.append('rect')
                .attr('width', 160)
                .attr('height', 25)
                .attr('rx', 6)
                .attr('fill', d.color)
                .attr('fill-opacity', 0.2)
                .attr('stroke', d.color)
                .attr('stroke-width', 1);
            
            badge.append('text')
                .attr('x', 80)
                .attr('y', 17)
                .attr('text-anchor', 'middle')
                .attr('fill', d.color)
                .style('font-size', '0.75rem')
                .style('font-weight', '600')
                .text(metric);
        });
    });
    
    // Draw data flow arrows
    for (let i = 0; i < tiers.length - 1; i++) {
        const startY = tiers[i].y + tiers[i].height;
        const endY = tiers[i + 1].y;
        const midX = width / 2;
        
        // Downward arrow (commands)
        svg.append('line')
            .attr('x1', midX - 30)
            .attr('y1', startY)
            .attr('x2', midX - 30)
            .attr('y2', endY - 10)
            .attr('stroke', '#00d4ff')
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', '5,5')
            .attr('opacity', 0.6);
        
        svg.append('polygon')
            .attr('points', `${midX - 30},${endY - 10} ${midX - 35},${endY - 20} ${midX - 25},${endY - 20}`)
            .attr('fill', '#00d4ff')
            .attr('opacity', 0.6);
        
        // Upward arrow (feedback)
        svg.append('line')
            .attr('x1', midX + 30)
            .attr('y1', endY)
            .attr('x2', midX + 30)
            .attr('y2', startY + 10)
            .attr('stroke', '#7b61ff')
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', '5,5')
            .attr('opacity', 0.6);
        
        svg.append('polygon')
            .attr('points', `${midX + 30},${startY + 10} ${midX + 25},${startY + 20} ${midX + 35},${startY + 20}`)
            .attr('fill', '#7b61ff')
            .attr('opacity', 0.6);
    }
    
    // Add legend
    const legend = svg.append('g')
        .attr('transform', `translate(${width - 250}, 20)`);
    
    legend.append('text')
        .attr('x', 0)
        .attr('y', 0)
        .attr('fill', '#9ca3af')
        .style('font-size', '0.875rem')
        .style('font-weight', '600')
        .text('Data Flow:');
    
    legend.append('line')
        .attr('x1', 0)
        .attr('y1', 20)
        .attr('x2', 40)
        .attr('y2', 20)
        .attr('stroke', '#00d4ff')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5');
    
    legend.append('text')
        .attr('x', 50)
        .attr('y', 24)
        .attr('fill', '#9ca3af')
        .style('font-size', '0.75rem')
        .text('Commands ⬇️');
    
    legend.append('line')
        .attr('x1', 0)
        .attr('y1', 45)
        .attr('x2', 40)
        .attr('y2', 45)
        .attr('stroke', '#7b61ff')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5');
    
    legend.append('text')
        .attr('x', 50)
        .attr('y', 49)
        .attr('fill', '#9ca3af')
        .style('font-size', '0.75rem')
        .text('Feedback ⬆️');
}

function showTierDetails(tier) {
    const detailPages = {
        'tier0': '../governance/skull-rulebook.html',
        'tier1': 'four-tier-brain.html#tier1',
        'tier2': 'four-tier-brain.html#tier2',
        'tier3': 'four-tier-brain.html#tier3'
    };
    
    if (detailPages[tier.id]) {
        window.location.href = detailPages[tier.id];
    }
}

// Responsive resize
window.addEventListener('resize', () => {
    if (document.getElementById('tier-visualization')) {
        renderTierVisualization();
    }
});
