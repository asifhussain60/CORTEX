/**
 * CORTEX Architecture Graph Visualization
 * D3.js Force-Directed Graph with Health Score Coloring
 * 
 * Features:
 * - Force simulation (forceLink, forceManyBody, forceCollide)
 * - Zoom 0.5x-3x with controls
 * - Pan with mouse drag
 * - Node coloring by health score (green/yellow/red)
 * - Tooltips with <100ms latency
 * - Details panel on click
 * - Performance optimized for 500+ nodes
 * 
 * @version 1.0.0
 * @author Asif Hussain
 */

class ArchitectureGraph {
    constructor(svgId, data) {
        this.svgId = svgId;
        this.data = data;
        this.nodes = data.nodes || [];
        this.edges = data.edges || [];
        this.metadata = data.metadata || {};
        
        // Graph dimensions
        this.width = window.innerWidth - 40;
        this.height = window.innerHeight - 200;
        
        // Zoom state
        this.zoomLevel = 1.0;
        this.minZoom = 0.5;
        this.maxZoom = 3.0;
        
        // Filter state
        this.currentLanguageFilter = 'all';
        
        // D3 selections
        this.svg = null;
        this.g = null;
        this.simulation = null;
        this.link = null;
        this.node = null;
        this.tooltip = null;
        this.detailsPanel = null;
        
        // Performance tracking
        this.renderStartTime = null;
        this.frameCount = 0;
        this.lastFrameTime = performance.now();
    }

    /**
     * Initialize the graph visualization
     */
    initialize() {
        this.renderStartTime = performance.now();
        
        // Setup SVG
        this.setupSVG();
        
        // Setup controls
        this.setupControls();
        
        // Setup tooltip
        this.setupTooltip();
        
        // Setup details panel
        this.setupDetailsPanel();
        
        // Build graph
        this.buildGraph();
        
        // Update stats
        this.updateStats();
        
        // Hide loading overlay
        document.getElementById('loading-overlay').style.display = 'none';
        
        // Performance logging
        const renderTime = performance.now() - this.renderStartTime;
        console.log(`Graph rendered in ${renderTime.toFixed(2)}ms`);
        console.log(`Total nodes: ${this.nodes.length}, Total edges: ${this.edges.length}`);
    }

    /**
     * Setup SVG container with zoom/pan
     */
    setupSVG() {
        this.svg = d3.select(`#${this.svgId}`)
            .attr('width', this.width)
            .attr('height', this.height);

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([this.minZoom, this.maxZoom])
            .on('zoom', (event) => this.handleZoom(event));

        this.svg.call(zoom);

        // Create container group for graph elements
        this.g = this.svg.append('g')
            .attr('class', 'graph-group');

        // Add arrow markers for directed edges
        this.svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#999');
    }

    /**
     * Setup control buttons
     */
    setupControls() {
        // Zoom controls
        document.getElementById('zoom-in').addEventListener('click', () => this.zoomIn());
        document.getElementById('zoom-out').addEventListener('click', () => this.zoomOut());
        document.getElementById('zoom-reset').addEventListener('click', () => this.zoomReset());

        // Layout controls
        document.getElementById('layout-force').addEventListener('click', () => this.applyForceLayout());
        document.getElementById('layout-circular').addEventListener('click', () => this.applyCircularLayout());
        document.getElementById('layout-hierarchical').addEventListener('click', () => this.applyHierarchicalLayout());

        // Filter controls
        document.getElementById('filter-language').addEventListener('change', (e) => this.filterByLanguage(e.target.value));

        // Export controls
        document.getElementById('export-svg').addEventListener('click', () => this.exportSVG());
        document.getElementById('export-png').addEventListener('click', () => this.exportPNG());

        // Window resize
        window.addEventListener('resize', () => this.handleResize());
    }

    /**
     * Setup tooltip
     */
    setupTooltip() {
        this.tooltip = d3.select('#node-tooltip');
    }

    /**
     * Setup details panel
     */
    setupDetailsPanel() {
        this.detailsPanel = document.getElementById('details-panel');
        document.getElementById('details-close').addEventListener('click', () => {
            this.detailsPanel.classList.remove('open');
        });
    }

    /**
     * Build D3 force-directed graph
     */
    buildGraph() {
        // Create simulation
        this.simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.edges)
                .id(d => d.id)
                .distance(100)
                .strength(0.3))
            .force('charge', d3.forceManyBody()
                .strength(-300))
            .force('collision', d3.forceCollide()
                .radius(30))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2));

        // Create links
        this.link = this.g.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(this.edges)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => Math.sqrt(d.weight || 1))
            .attr('marker-end', 'url(#arrowhead)');

        // Create nodes
        this.node = this.g.append('g')
            .attr('class', 'nodes')
            .selectAll('circle')
            .data(this.nodes)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('r', d => this.getNodeRadius(d))
            .attr('fill', d => this.getNodeColor(d))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mouseout', () => this.hideTooltip())
            .on('click', (event, d) => this.showDetails(d))
            .call(d3.drag()
                .on('start', (event, d) => this.dragStarted(event, d))
                .on('drag', (event, d) => this.dragged(event, d))
                .on('end', (event, d) => this.dragEnded(event, d)));

        // Create node labels
        this.g.append('g')
            .attr('class', 'labels')
            .selectAll('text')
            .data(this.nodes)
            .enter().append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', -15)
            .text(d => d.label)
            .style('font-size', '10px')
            .style('fill', '#333')
            .style('pointer-events', 'none');

        // Update positions on tick
        this.simulation.on('tick', () => this.tick());

        // FPS monitoring
        this.simulation.on('tick', () => this.monitorFPS());
    }

    /**
     * Update positions on simulation tick
     */
    tick() {
        this.link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        this.node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        this.g.selectAll('.node-label')
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    }

    /**
     * Monitor FPS performance
     */
    monitorFPS() {
        this.frameCount++;
        const now = performance.now();
        const elapsed = now - this.lastFrameTime;
        
        if (elapsed >= 1000) {
            const fps = Math.round(this.frameCount / (elapsed / 1000));
            console.log(`FPS: ${fps}`);
            this.frameCount = 0;
            this.lastFrameTime = now;
        }
    }

    /**
     * Get node radius based on LOC
     */
    getNodeRadius(node) {
        const loc = node.loc || 0;
        const minRadius = 5;
        const maxRadius = 20;
        const scale = d3.scaleLog()
            .domain([1, Math.max(...this.nodes.map(n => n.loc || 1))])
            .range([minRadius, maxRadius]);
        return scale(Math.max(loc, 1));
    }

    /**
     * Get node color based on health score
     */
    getNodeColor(node) {
        const health = node.health_score || 0;
        
        if (health >= 90) {
            return '#28a745'; // Green - Healthy
        } else if (health >= 70) {
            return '#ffc107'; // Yellow - Warning
        } else if (health > 0) {
            return '#dc3545'; // Red - Critical
        } else {
            return '#6c757d'; // Gray - Unknown
        }
    }

    /**
     * Show tooltip on node hover
     */
    showTooltip(event, node) {
        const tooltipStartTime = performance.now();
        
        this.tooltip
            .style('opacity', 1)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px');

        document.getElementById('tooltip-name').textContent = node.label;
        document.getElementById('tooltip-language').textContent = node.language || 'Unknown';
        document.getElementById('tooltip-loc').textContent = node.loc || 'N/A';
        
        const deps = this.edges.filter(e => e.source.id === node.id).length;
        document.getElementById('tooltip-deps').textContent = deps;
        
        const health = node.health_score || 0;
        document.getElementById('tooltip-health').textContent = health > 0 ? `${health}/100` : 'Unknown';
        document.getElementById('tooltip-path').textContent = node.file_path || node.id;

        const tooltipTime = performance.now() - tooltipStartTime;
        if (tooltipTime > 100) {
            console.warn(`Tooltip render time: ${tooltipTime.toFixed(2)}ms (exceeds 100ms target)`);
        }
    }

    /**
     * Hide tooltip
     */
    hideTooltip() {
        this.tooltip.style('opacity', 0);
    }

    /**
     * Show details panel on node click
     */
    showDetails(node) {
        // Populate details
        document.getElementById('details-name').textContent = node.label;
        document.getElementById('details-type').textContent = node.type || 'Unknown';
        document.getElementById('details-language').textContent = node.language || 'Unknown';
        document.getElementById('details-loc').textContent = node.loc || 'N/A';

        // Dependencies
        const dependencies = this.edges.filter(e => e.source.id === node.id);
        const depsList = document.getElementById('details-dependencies');
        depsList.innerHTML = '';
        dependencies.forEach(dep => {
            const li = document.createElement('li');
            li.textContent = dep.target.label || dep.target.id;
            depsList.appendChild(li);
        });

        // Dependents
        const dependents = this.edges.filter(e => e.target.id === node.id);
        const depList = document.getElementById('details-dependents');
        depList.innerHTML = '';
        dependents.forEach(dep => {
            const li = document.createElement('li');
            li.textContent = dep.source.label || dep.source.id;
            depList.appendChild(li);
        });

        // Health score
        const health = node.health_score || 0;
        document.getElementById('details-health-score').textContent = health > 0 ? `${health}/100` : 'Unknown';
        const healthFill = document.getElementById('details-health-fill');
        healthFill.style.width = `${health}%`;
        healthFill.style.backgroundColor = this.getNodeColor(node);

        // File path
        document.getElementById('details-filepath').textContent = node.file_path || node.id;

        // Show panel
        this.detailsPanel.classList.add('open');
    }

    /**
     * Handle zoom event
     */
    handleZoom(event) {
        this.zoomLevel = event.transform.k;
        this.g.attr('transform', event.transform);
        this.updateZoomLabel();
    }

    /**
     * Zoom in
     */
    zoomIn() {
        const newZoom = Math.min(this.zoomLevel + 0.2, this.maxZoom);
        this.svg.transition().duration(300).call(
            d3.zoom().scaleTo,
            newZoom
        );
    }

    /**
     * Zoom out
     */
    zoomOut() {
        const newZoom = Math.max(this.zoomLevel - 0.2, this.minZoom);
        this.svg.transition().duration(300).call(
            d3.zoom().scaleTo,
            newZoom
        );
    }

    /**
     * Reset zoom
     */
    zoomReset() {
        this.svg.transition().duration(300).call(
            d3.zoom().transform,
            d3.zoomIdentity
        );
    }

    /**
     * Update zoom label
     */
    updateZoomLabel() {
        document.getElementById('zoom-level').textContent = `${Math.round(this.zoomLevel * 100)}%`;
    }

    /**
     * Apply force layout (default)
     */
    applyForceLayout() {
        this.simulation.alpha(1).restart();
        this.setActiveLayout('layout-force');
    }

    /**
     * Apply circular layout
     */
    applyCircularLayout() {
        const radius = Math.min(this.width, this.height) / 2 - 50;
        const angleStep = (2 * Math.PI) / this.nodes.length;

        this.nodes.forEach((node, i) => {
            node.fx = this.width / 2 + radius * Math.cos(i * angleStep);
            node.fy = this.height / 2 + radius * Math.sin(i * angleStep);
        });

        this.simulation.alpha(1).restart();
        this.setActiveLayout('layout-circular');
    }

    /**
     * Apply hierarchical layout
     */
    applyHierarchicalLayout() {
        // Simple hierarchical layout (top-down by dependency depth)
        const levels = new Map();
        const visited = new Set();

        const assignLevel = (nodeId, level) => {
            if (visited.has(nodeId)) return;
            visited.add(nodeId);
            levels.set(nodeId, level);

            const outgoing = this.edges.filter(e => e.source.id === nodeId);
            outgoing.forEach(edge => assignLevel(edge.target.id, level + 1));
        };

        // Start from nodes with no incoming edges
        const rootNodes = this.nodes.filter(node => 
            !this.edges.some(e => e.target.id === node.id)
        );

        rootNodes.forEach(node => assignLevel(node.id, 0));

        // Assign remaining nodes
        this.nodes.forEach(node => {
            if (!levels.has(node.id)) {
                assignLevel(node.id, 0);
            }
        });

        // Position nodes
        const maxLevel = Math.max(...levels.values());
        const levelHeight = this.height / (maxLevel + 1);

        this.nodes.forEach(node => {
            const level = levels.get(node.id) || 0;
            const nodesAtLevel = this.nodes.filter(n => levels.get(n.id) === level);
            const indexAtLevel = nodesAtLevel.indexOf(node);
            const levelWidth = this.width / (nodesAtLevel.length + 1);

            node.fx = (indexAtLevel + 1) * levelWidth;
            node.fy = (level + 1) * levelHeight;
        });

        this.simulation.alpha(1).restart();
        this.setActiveLayout('layout-hierarchical');
    }

    /**
     * Set active layout button
     */
    setActiveLayout(buttonId) {
        document.querySelectorAll('.control-btn').forEach(btn => {
            if (btn.id.startsWith('layout-')) {
                btn.classList.remove('active');
            }
        });
        document.getElementById(buttonId).classList.add('active');
    }

    /**
     * Filter by language
     */
    filterByLanguage(language) {
        this.currentLanguageFilter = language;

        this.node.style('opacity', d => {
            if (language === 'all') return 1;
            return d.language === language ? 1 : 0.2;
        });

        this.link.style('opacity', d => {
            if (language === 'all') return 0.6;
            return (d.source.language === language || d.target.language === language) ? 0.6 : 0.1;
        });
    }

    /**
     * Drag handlers
     */
    dragStarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    dragEnded(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    /**
     * Update statistics
     */
    updateStats() {
        document.getElementById('stat-nodes').textContent = this.nodes.length;
        document.getElementById('stat-edges').textContent = this.edges.length;

        const depCounts = this.nodes.map(n => 
            this.edges.filter(e => e.source.id === n.id).length
        );
        const avgDeps = depCounts.length > 0 
            ? (depCounts.reduce((a, b) => a + b, 0) / depCounts.length).toFixed(1)
            : 0;
        const maxDeps = depCounts.length > 0 ? Math.max(...depCounts) : 0;

        document.getElementById('stat-avg-deps').textContent = avgDeps;
        document.getElementById('stat-max-deps').textContent = maxDeps;
    }

    /**
     * Handle window resize
     */
    handleResize() {
        this.width = window.innerWidth - 40;
        this.height = window.innerHeight - 200;

        this.svg
            .attr('width', this.width)
            .attr('height', this.height);

        this.simulation.force('center', d3.forceCenter(this.width / 2, this.height / 2));
        this.simulation.alpha(0.3).restart();
    }

    /**
     * Export SVG
     */
    exportSVG() {
        const svgData = document.getElementById(this.svgId).outerHTML;
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'cortex-architecture.svg';
        link.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Export PNG
     */
    exportPNG() {
        const svgElement = document.getElementById(this.svgId);
        const svgData = new XMLSerializer().serializeToString(svgElement);
        const canvas = document.createElement('canvas');
        canvas.width = this.width;
        canvas.height = this.height;
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
            ctx.drawImage(img, 0, 0);
            canvas.toBlob(blob => {
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'cortex-architecture.png';
                link.click();
                URL.revokeObjectURL(url);
            });
        };

        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(svgBlob);
        img.src = url;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ArchitectureGraph;
}
