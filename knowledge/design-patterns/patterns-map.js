/**
 * CORTEX Design Patterns - Interactive D3.js Map
 * Force-directed graph visualization of pattern relationships
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

class PatternMap {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.tooltip = document.querySelector('.viz-tooltip');
        this.width = this.container.clientWidth;
        this.height = 500;
        this.currentView = 'categories';
        
        this.colors = {
            creational: '#10b981',
            structural: '#3b82f6',
            behavioral: '#8b5cf6',
            enterprise: '#f59e0b'
        };
        
        this.categoryLabels = {
            creational: 'Creational',
            structural: 'Structural',
            behavioral: 'Behavioral',
            enterprise: 'Enterprise'
        };
        
        this.init();
    }
    
    init() {
        // Clear existing content
        this.container.innerHTML = '';
        
        // Create SVG
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('width', '100%')
            .attr('height', this.height)
            .attr('viewBox', `0 0 ${this.width} ${this.height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.3, 3])
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });
        
        this.svg.call(zoom);
        
        // Create main group for transformations
        this.g = this.svg.append('g');
        
        // Add defs for gradients and markers
        this.createDefs();
        
        // Initial render
        this.renderCategoriesView();
        
        // Handle resize
        window.addEventListener('resize', () => this.handleResize());
    }
    
    createDefs() {
        const defs = this.svg.append('defs');
        
        // Create gradients for each category
        Object.entries(this.colors).forEach(([key, color]) => {
            const gradient = defs.append('radialGradient')
                .attr('id', `gradient-${key}`)
                .attr('cx', '30%')
                .attr('cy', '30%');
            
            gradient.append('stop')
                .attr('offset', '0%')
                .attr('stop-color', d3.color(color).brighter(0.5));
            
            gradient.append('stop')
                .attr('offset', '100%')
                .attr('stop-color', color);
        });
        
        // Arrow marker for relationships
        defs.append('marker')
            .attr('id', 'arrow')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#666');
    }
    
    handleResize() {
        this.width = this.container.clientWidth;
        this.svg.attr('viewBox', `0 0 ${this.width} ${this.height}`);
    }
    
    renderCategoriesView() {
        this.currentView = 'categories';
        this.g.selectAll('*').remove();
        
        const categories = [
            { id: 'creational', label: 'Creational', count: 5, icon: '➕' },
            { id: 'structural', label: 'Structural', count: 7, icon: '🔗' },
            { id: 'behavioral', label: 'Behavioral', count: 11, icon: '↔️' },
            { id: 'enterprise', label: 'Enterprise', count: 2, icon: '🏢' }
        ];
        
        const spacing = this.width / (categories.length + 1);
        const yPos = this.height / 2;
        
        categories.forEach((cat, i) => {
            const xPos = spacing * (i + 1);
            const group = this.g.append('g')
                .attr('class', 'category-node')
                .attr('transform', `translate(${xPos}, ${yPos})`)
                .style('cursor', 'pointer')
                .on('click', () => this.expandCategory(cat.id))
                .on('mouseover', (event) => this.showTooltip(event, `${cat.label} Patterns (${cat.count})\nClick to expand`))
                .on('mouseout', () => this.hideTooltip());
            
            // Outer glow
            group.append('circle')
                .attr('r', 55)
                .attr('fill', 'none')
                .attr('stroke', this.colors[cat.id])
                .attr('stroke-width', 2)
                .attr('opacity', 0.3)
                .attr('class', 'pulse-ring');
            
            // Main circle
            group.append('circle')
                .attr('r', 45)
                .attr('fill', `url(#gradient-${cat.id})`)
                .attr('stroke', this.colors[cat.id])
                .attr('stroke-width', 2);
            
            // Count badge
            group.append('circle')
                .attr('cx', 30)
                .attr('cy', -30)
                .attr('r', 15)
                .attr('fill', '#1a1f3a')
                .attr('stroke', this.colors[cat.id])
                .attr('stroke-width', 2);
            
            group.append('text')
                .attr('x', 30)
                .attr('y', -25)
                .attr('text-anchor', 'middle')
                .attr('fill', 'white')
                .attr('font-size', '12px')
                .attr('font-weight', 'bold')
                .text(cat.count);
            
            // Label
            group.append('text')
                .attr('y', 70)
                .attr('text-anchor', 'middle')
                .attr('fill', 'white')
                .attr('font-size', '14px')
                .attr('font-weight', '500')
                .text(cat.label);
        });
        
        // Add CSS animation for pulse
        if (!document.getElementById('pulse-animation')) {
            const style = document.createElement('style');
            style.id = 'pulse-animation';
            style.textContent = `
                @keyframes pulse {
                    0%, 100% { opacity: 0.3; transform: scale(1); }
                    50% { opacity: 0.6; transform: scale(1.1); }
                }
                .pulse-ring { animation: pulse 2s ease-in-out infinite; }
            `;
            document.head.appendChild(style);
        }
    }
    
    expandCategory(categoryId) {
        this.currentView = 'expanded';
        this.g.selectAll('*').remove();
        
        const patterns = Object.entries(PATTERNS_DATA)
            .filter(([_, p]) => p.type === categoryId)
            .map(([id, p]) => ({ id, ...p }));
        
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        
        // Draw center category node
        const centerGroup = this.g.append('g')
            .attr('transform', `translate(${centerX}, ${centerY})`);
        
        centerGroup.append('circle')
            .attr('r', 50)
            .attr('fill', `url(#gradient-${categoryId})`)
            .attr('stroke', this.colors[categoryId])
            .attr('stroke-width', 3);
        
        centerGroup.append('text')
            .attr('y', 5)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .attr('font-size', '14px')
            .attr('font-weight', 'bold')
            .text(this.categoryLabels[categoryId]);
        
        // Draw pattern nodes around center
        const radius = Math.min(this.width, this.height) * 0.35;
        const angleStep = (2 * Math.PI) / patterns.length;
        
        patterns.forEach((pattern, i) => {
            const angle = angleStep * i - Math.PI / 2;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            
            // Draw connection line
            this.g.append('line')
                .attr('x1', centerX)
                .attr('y1', centerY)
                .attr('x2', x)
                .attr('y2', y)
                .attr('stroke', this.colors[categoryId])
                .attr('stroke-width', 1)
                .attr('opacity', 0.3);
            
            // Draw pattern node
            const group = this.g.append('g')
                .attr('transform', `translate(${x}, ${y})`)
                .style('cursor', 'pointer')
                .on('click', () => this.showPatternDetail(pattern.id))
                .on('mouseover', (event) => this.showTooltip(event, `${pattern.name}\n${pattern.intent.substring(0, 60)}...`))
                .on('mouseout', () => this.hideTooltip());
            
            group.append('circle')
                .attr('r', 30)
                .attr('fill', '#1a1f3a')
                .attr('stroke', this.colors[categoryId])
                .attr('stroke-width', 2);
            
            // Pattern name (wrapped if needed)
            const words = pattern.name.split(' ');
            if (words.length > 1) {
                group.append('text')
                    .attr('y', -5)
                    .attr('text-anchor', 'middle')
                    .attr('fill', 'white')
                    .attr('font-size', '10px')
                    .text(words[0]);
                group.append('text')
                    .attr('y', 8)
                    .attr('text-anchor', 'middle')
                    .attr('fill', 'white')
                    .attr('font-size', '10px')
                    .text(words.slice(1).join(' '));
            } else {
                group.append('text')
                    .attr('y', 4)
                    .attr('text-anchor', 'middle')
                    .attr('fill', 'white')
                    .attr('font-size', '10px')
                    .text(pattern.name);
            }
        });
        
        // Add back button
        const backBtn = this.g.append('g')
            .attr('transform', `translate(60, 40)`)
            .style('cursor', 'pointer')
            .on('click', () => this.renderCategoriesView());
        
        backBtn.append('rect')
            .attr('x', -40)
            .attr('y', -15)
            .attr('width', 80)
            .attr('height', 30)
            .attr('rx', 5)
            .attr('fill', '#1a1f3a')
            .attr('stroke', '#666')
            .attr('stroke-width', 1);
        
        backBtn.append('text')
            .attr('text-anchor', 'middle')
            .attr('y', 5)
            .attr('fill', '#a0a6c0')
            .attr('font-size', '12px')
            .text('← Back');
    }
    
    renderFullMap() {
        this.currentView = 'full';
        this.g.selectAll('*').remove();
        
        // Build nodes and links
        const nodes = [];
        const links = [];
        
        // Add category nodes
        const categories = ['creational', 'structural', 'behavioral', 'enterprise'];
        categories.forEach(cat => {
            nodes.push({
                id: cat,
                name: this.categoryLabels[cat],
                type: 'category',
                category: cat,
                r: 35
            });
        });
        
        // Add pattern nodes
        Object.entries(PATTERNS_DATA).forEach(([id, pattern]) => {
            nodes.push({
                id,
                name: pattern.name,
                type: 'pattern',
                category: pattern.type,
                r: 20
            });
            
            // Link to category
            links.push({
                source: pattern.type,
                target: id,
                type: 'category'
            });
            
            // Add relationship links
            if (pattern.relatedPatterns) {
                pattern.relatedPatterns.forEach(related => {
                    const relatedId = related.toLowerCase().replace(/ /g, '-');
                    if (PATTERNS_DATA[relatedId]) {
                        links.push({
                            source: id,
                            target: relatedId,
                            type: 'related'
                        });
                    }
                });
            }
        });
        
        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(d => d.type === 'category' ? 120 : 80))
            .force('charge', d3.forceManyBody().strength(-200))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(d => d.r + 10));
        
        // Draw links
        const link = this.g.append('g')
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('stroke', d => d.type === 'category' ? '#444' : '#333')
            .attr('stroke-width', d => d.type === 'category' ? 2 : 1)
            .attr('stroke-dasharray', d => d.type === 'related' ? '3,3' : 'none')
            .attr('opacity', 0.5);
        
        // Draw nodes
        const node = this.g.append('g')
            .selectAll('g')
            .data(nodes)
            .join('g')
            .style('cursor', 'pointer')
            .call(d3.drag()
                .on('start', (event, d) => {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                })
                .on('drag', (event, d) => {
                    d.fx = event.x;
                    d.fy = event.y;
                })
                .on('end', (event, d) => {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }));
        
        node.append('circle')
            .attr('r', d => d.r)
            .attr('fill', d => d.type === 'category' ? `url(#gradient-${d.category})` : '#1a1f3a')
            .attr('stroke', d => this.colors[d.category])
            .attr('stroke-width', d => d.type === 'category' ? 3 : 2);
        
        node.append('text')
            .attr('y', d => d.type === 'category' ? 4 : 3)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .attr('font-size', d => d.type === 'category' ? '11px' : '8px')
            .attr('font-weight', d => d.type === 'category' ? 'bold' : 'normal')
            .text(d => d.type === 'category' ? d.name : d.name.substring(0, 10));
        
        node.on('click', (event, d) => {
            if (d.type === 'pattern') {
                this.showPatternDetail(d.id);
            } else {
                this.expandCategory(d.id);
            }
        })
        .on('mouseover', (event, d) => {
            if (d.type === 'pattern') {
                const pattern = PATTERNS_DATA[d.id];
                this.showTooltip(event, `${pattern.name}\n${pattern.intent.substring(0, 80)}...`);
            }
        })
        .on('mouseout', () => this.hideTooltip());
        
        // Update positions on tick
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node.attr('transform', d => `translate(${d.x}, ${d.y})`);
        });
    }
    
    renderRelationshipsView() {
        this.currentView = 'relationships';
        this.g.selectAll('*').remove();
        
        // Build relationship-focused graph
        const nodes = [];
        const links = [];
        const addedNodes = new Set();
        
        Object.entries(PATTERNS_DATA).forEach(([id, pattern]) => {
            if (!addedNodes.has(id)) {
                nodes.push({
                    id,
                    name: pattern.name,
                    category: pattern.type,
                    r: 25
                });
                addedNodes.add(id);
            }
            
            if (pattern.relatedPatterns) {
                pattern.relatedPatterns.forEach(related => {
                    const relatedId = related.toLowerCase().replace(/ /g, '-');
                    if (PATTERNS_DATA[relatedId] && !links.some(l => 
                        (l.source === id && l.target === relatedId) ||
                        (l.source === relatedId && l.target === id)
                    )) {
                        links.push({
                            source: id,
                            target: relatedId
                        });
                    }
                });
            }
        });
        
        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(35));
        
        // Draw links
        const link = this.g.append('g')
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('stroke', '#666')
            .attr('stroke-width', 1.5)
            .attr('opacity', 0.6);
        
        // Draw nodes
        const node = this.g.append('g')
            .selectAll('g')
            .data(nodes)
            .join('g')
            .style('cursor', 'pointer')
            .call(d3.drag()
                .on('start', (event, d) => {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                })
                .on('drag', (event, d) => {
                    d.fx = event.x;
                    d.fy = event.y;
                })
                .on('end', (event, d) => {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }));
        
        node.append('circle')
            .attr('r', d => d.r)
            .attr('fill', '#1a1f3a')
            .attr('stroke', d => this.colors[d.category])
            .attr('stroke-width', 2);
        
        node.append('text')
            .attr('y', 4)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .attr('font-size', '9px')
            .text(d => d.name.length > 12 ? d.name.substring(0, 10) + '...' : d.name);
        
        node.on('click', (event, d) => this.showPatternDetail(d.id))
            .on('mouseover', (event, d) => {
                const pattern = PATTERNS_DATA[d.id];
                const relCount = pattern.relatedPatterns?.length || 0;
                this.showTooltip(event, `${pattern.name}\nRelated to ${relCount} patterns`);
            })
            .on('mouseout', () => this.hideTooltip());
        
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node.attr('transform', d => `translate(${d.x}, ${d.y})`);
        });
    }
    
    showPatternDetail(patternId) {
        // Dispatch custom event for the main app to handle
        window.dispatchEvent(new CustomEvent('showPatternDetail', { detail: patternId }));
    }
    
    showTooltip(event, text) {
        this.tooltip.innerHTML = text.replace(/\n/g, '<br>');
        this.tooltip.style.opacity = '1';
        this.tooltip.style.left = (event.pageX + 15) + 'px';
        this.tooltip.style.top = (event.pageY - 10) + 'px';
    }
    
    hideTooltip() {
        this.tooltip.style.opacity = '0';
    }
    
    setView(view) {
        switch (view) {
            case 'categories':
                this.renderCategoriesView();
                break;
            case 'full':
                this.renderFullMap();
                break;
            case 'relationships':
                this.renderRelationshipsView();
                break;
        }
    }
    
    reset() {
        this.renderCategoriesView();
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PatternMap;
}
