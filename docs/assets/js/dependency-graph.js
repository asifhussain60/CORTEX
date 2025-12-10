/**
 * CORTEX Dependency Graph Visualization
 * Force-directed graph showing feature dependencies and strategic relationships
 * Uses D3.js v7 force simulation
 */

class DependencyGraphVisualization {
    constructor() {
        this.data = null;
        this.svg = null;
        this.simulation = null;
        this.g = null;
        this.links = null;
        this.nodes = null;
        this.width = 0;
        this.height = 0;
        this.transform = d3.zoomIdentity;
        this.isFrozen = false;
        this.selectedNode = null;
        this.highlightedPath = new Set();
        
        // Color schemes
        this.nodeColors = {
            strategic_goal: '#667eea',
            milestone: '#f093fb',
            dependency: '#43e97b'
        };
        
        this.statusColors = {
            'in-progress': '#feca57',
            'planned': '#667eea',
            'future': '#a8b2d1',
            'external': '#43e97b'
        };
        
        this.linkColors = {
            depends_on: '#667eea',
            delivers_in: '#f093fb'
        };
    }
    
    async init() {
        console.log('Initializing Dependency Graph Visualization...');
        
        // Setup SVG
        this.setupSVG();
        
        // Setup controls
        this.setupControls();
        
        // Load data
        await this.loadData();
        
        // Render graph
        this.renderGraph();
        
        // Render statistics
        this.renderStatistics();
        
        console.log('Dependency Graph initialized successfully');
    }
    
    setupSVG() {
        const container = document.querySelector('.graph-wrapper');
        this.width = container.clientWidth;
        this.height = 800;
        
        this.svg = d3.select('#dependencyGraph')
            .attr('width', this.width)
            .attr('height', this.height);
        
        // Add arrow markers for links
        const defs = this.svg.append('defs');
        
        defs.append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '-0 -5 10 10')
            .attr('refX', 25)
            .attr('refY', 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 8)
            .attr('markerHeight', 8)
            .append('path')
            .attr('d', 'M 0,-5 L 10,0 L 0,5')
            .attr('fill', '#667eea')
            .attr('opacity', 0.6);
        
        // Create main group for zoom/pan
        this.g = this.svg.append('g')
            .attr('class', 'graph-main');
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                this.transform = event.transform;
                this.g.attr('transform', event.transform);
            });
        
        this.svg.call(zoom);
        
        // Handle window resize
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }
    
    setupControls() {
        // Filter by type
        document.getElementById('filterType').addEventListener('change', (e) => {
            this.filterByType(e.target.value);
        });
        
        // Filter by status
        document.getElementById('filterStatus').addEventListener('change', (e) => {
            this.filterByStatus(e.target.value);
        });
        
        // Search nodes
        document.getElementById('searchNode').addEventListener('input', (e) => {
            this.searchNodes(e.target.value);
        });
        
        // Reset graph
        document.getElementById('resetGraph').addEventListener('click', () => {
            this.resetGraph();
        });
        
        // Center graph
        document.getElementById('centerGraph').addEventListener('click', () => {
            this.centerGraph();
        });
        
        // Freeze/unfreeze
        document.getElementById('freezeGraph').addEventListener('click', () => {
            this.toggleFreeze();
        });
        
        // Close detail panel
        document.getElementById('closeDetail').addEventListener('click', () => {
            this.closeDetailPanel();
        });
    }
    
    async loadData() {
        try {
            const response = await fetch('../assets/data/dependency-graph.json');
            this.data = await response.json();
            console.log('Loaded dependency data:', this.data);
        } catch (error) {
            console.error('Error loading dependency data:', error);
            this.data = this.getMockData();
        }
    }
    
    getMockData() {
        return {
            nodes: [
                { id: 'goal-0', name: 'Multi-Agent Orchestration', type: 'strategic_goal', status: 'in-progress', priority: 'HIGH', category: 'architecture' },
                { id: 'goal-1', name: 'Universal Context Protocol', type: 'strategic_goal', status: 'planned', priority: 'HIGH', category: 'integration' },
                { id: 'goal-2', name: 'Semantic Code Understanding', type: 'strategic_goal', status: 'planned', priority: 'MEDIUM', category: 'intelligence' },
                { id: 'milestone-0', name: 'CORTEX 3.1', type: 'milestone', status: 'planned', priority: 'HIGH', category: 'timeline' }
            ],
            links: [
                { source: 'goal-0', target: 'milestone-0', type: 'delivers_in', strength: 'strong' },
                { source: 'goal-1', target: 'goal-0', type: 'depends_on', strength: 'medium' }
            ],
            statistics: {
                total_nodes: 4,
                total_links: 2,
                most_connected: []
            }
        };
    }
    
    renderGraph() {
        if (!this.data) return;
        
        // Create force simulation
        this.simulation = d3.forceSimulation(this.data.nodes)
            .force('link', d3.forceLink(this.data.links)
                .id(d => d.id)
                .distance(150))
            .force('charge', d3.forceManyBody()
                .strength(-500))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(40));
        
        // Draw links
        this.links = this.g.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(this.data.links)
            .join('line')
            .attr('class', 'link')
            .attr('stroke', d => this.linkColors[d.type] || '#667eea')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => d.strength === 'strong' ? 3 : 2)
            .attr('stroke-dasharray', d => d.type === 'delivers_in' ? '5,5' : '0')
            .attr('marker-end', 'url(#arrowhead)');
        
        // Draw nodes
        const nodeGroup = this.g.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(this.data.nodes)
            .join('g')
            .attr('class', 'node')
            .call(this.drag(this.simulation));
        
        // Add node shapes based on type
        nodeGroup.each((d, i, nodes) => {
            const node = d3.select(nodes[i]);
            const color = this.nodeColors[d.type] || '#667eea';
            const strokeColor = this.statusColors[d.status] || '#667eea';
            
            if (d.type === 'strategic_goal') {
                node.append('circle')
                    .attr('r', 20)
                    .attr('fill', color)
                    .attr('stroke', strokeColor)
                    .attr('stroke-width', 3);
            } else if (d.type === 'milestone') {
                node.append('rect')
                    .attr('x', -18)
                    .attr('y', -18)
                    .attr('width', 36)
                    .attr('height', 36)
                    .attr('fill', color)
                    .attr('stroke', strokeColor)
                    .attr('stroke-width', 3)
                    .attr('rx', 4);
            } else {
                node.append('polygon')
                    .attr('points', '0,-20 20,15 -20,15')
                    .attr('fill', color)
                    .attr('stroke', strokeColor)
                    .attr('stroke-width', 3);
            }
        });
        
        // Add node labels
        nodeGroup.append('text')
            .attr('class', 'node-label')
            .attr('dy', 35)
            .attr('text-anchor', 'middle')
            .style('font-size', '12px')
            .style('fill', '#fff')
            .style('pointer-events', 'none')
            .text(d => this.truncateText(d.name, 20));
        
        // Add node interactions
        nodeGroup
            .on('mouseover', (event, d) => this.showNodeTooltip(event, d))
            .on('mouseout', () => this.hideTooltip())
            .on('click', (event, d) => this.handleNodeClick(event, d));
        
        this.nodes = nodeGroup;
        
        // Update positions on simulation tick
        this.simulation.on('tick', () => {
            this.links
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            this.nodes
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });
    }
    
    drag(simulation) {
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
            if (!this.isFrozen) {
                event.subject.fx = null;
                event.subject.fy = null;
            }
        }
        
        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended.bind(this));
    }
    
    handleNodeClick(event, d) {
        // Highlight dependency path
        this.highlightPath(d);
        
        // Show detail panel
        this.showDetailPanel(d);
    }
    
    highlightPath(node) {
        this.highlightedPath.clear();
        
        // Find all connected nodes
        const connected = new Set();
        this.data.links.forEach(link => {
            if (link.source.id === node.id) {
                connected.add(link.target.id);
                this.highlightedPath.add(`${link.source.id}-${link.target.id}`);
            }
            if (link.target.id === node.id) {
                connected.add(link.source.id);
                this.highlightedPath.add(`${link.source.id}-${link.target.id}`);
            }
        });
        
        connected.add(node.id);
        
        // Update node opacity
        this.nodes
            .style('opacity', d => connected.has(d.id) ? 1 : 0.2);
        
        // Update link opacity
        this.links
            .style('opacity', d => {
                const linkId = `${d.source.id}-${d.target.id}`;
                return this.highlightedPath.has(linkId) ? 1 : 0.1;
            })
            .attr('stroke-width', d => {
                const linkId = `${d.source.id}-${d.target.id}`;
                return this.highlightedPath.has(linkId) ? 4 : 2;
            });
    }
    
    showDetailPanel(node) {
        document.getElementById('nodeDetailName').textContent = node.name;
        document.getElementById('nodeDetailType').textContent = node.type.replace('_', ' ');
        document.getElementById('nodeDetailCategory').textContent = node.category || '-';
        document.getElementById('nodeDetailStatus').textContent = node.status;
        document.getElementById('nodeDetailPriority').textContent = node.priority || '-';
        document.getElementById('nodeDetailDescription').textContent = node.description || 'No description available';
        
        // Show connections
        const connectionsDiv = document.getElementById('nodeDetailConnections');
        const incoming = this.data.links.filter(l => l.target.id === node.id);
        const outgoing = this.data.links.filter(l => l.source.id === node.id);
        
        connectionsDiv.innerHTML = `
            <div><strong>Incoming:</strong> ${incoming.length}</div>
            <div><strong>Outgoing:</strong> ${outgoing.length}</div>
            <div><strong>Total:</strong> ${incoming.length + outgoing.length}</div>
        `;
        
        document.getElementById('nodeDetail').style.display = 'block';
    }
    
    closeDetailPanel() {
        document.getElementById('nodeDetail').style.display = 'none';
        
        // Reset highlighting
        this.nodes.style('opacity', 1);
        this.links.style('opacity', 0.6).attr('stroke-width', d => d.strength === 'strong' ? 3 : 2);
        this.highlightedPath.clear();
    }
    
    filterByType(type) {
        if (type === 'all') {
            this.nodes.style('display', 'block');
        } else {
            this.nodes.style('display', d => d.type === type ? 'block' : 'none');
        }
        this.simulation.alpha(0.3).restart();
    }
    
    filterByStatus(status) {
        if (status === 'all') {
            this.nodes.style('display', 'block');
        } else {
            this.nodes.style('display', d => d.status === status ? 'block' : 'none');
        }
        this.simulation.alpha(0.3).restart();
    }
    
    searchNodes(query) {
        if (!query) {
            this.nodes.style('opacity', 1);
            return;
        }
        
        const lowerQuery = query.toLowerCase();
        this.nodes.style('opacity', d => {
            return d.name.toLowerCase().includes(lowerQuery) ? 1 : 0.2;
        });
    }
    
    resetGraph() {
        // Reset filters
        document.getElementById('filterType').value = 'all';
        document.getElementById('filterStatus').value = 'all';
        document.getElementById('searchNode').value = '';
        
        // Reset display
        this.nodes.style('display', 'block').style('opacity', 1);
        this.links.style('opacity', 0.6).attr('stroke-width', d => d.strength === 'strong' ? 3 : 2);
        
        // Reset zoom
        this.svg.transition().duration(750).call(
            d3.zoom().transform,
            d3.zoomIdentity
        );
        
        // Restart simulation
        this.simulation.alpha(1).restart();
    }
    
    centerGraph() {
        const bounds = this.g.node().getBBox();
        const fullWidth = this.width;
        const fullHeight = this.height;
        const width = bounds.width;
        const height = bounds.height;
        const midX = bounds.x + width / 2;
        const midY = bounds.y + height / 2;
        
        const scale = 0.8 / Math.max(width / fullWidth, height / fullHeight);
        const translate = [fullWidth / 2 - scale * midX, fullHeight / 2 - scale * midY];
        
        this.svg.transition().duration(750).call(
            d3.zoom().transform,
            d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
        );
    }
    
    toggleFreeze() {
        this.isFrozen = !this.isFrozen;
        
        if (this.isFrozen) {
            this.simulation.stop();
            this.data.nodes.forEach(node => {
                node.fx = node.x;
                node.fy = node.y;
            });
            document.getElementById('freezeGraph').textContent = 'Unfreeze';
        } else {
            this.data.nodes.forEach(node => {
                node.fx = null;
                node.fy = null;
            });
            this.simulation.alpha(0.3).restart();
            document.getElementById('freezeGraph').textContent = 'Freeze';
        }
    }
    
    renderStatistics() {
        if (!this.data || !this.data.statistics) return;
        
        const stats = this.data.statistics;
        
        document.getElementById('totalNodes').textContent = stats.total_nodes || 0;
        document.getElementById('totalLinks').textContent = stats.total_links || 0;
        
        // Critical nodes (most connected)
        const criticalCount = stats.most_connected?.length || 0;
        document.getElementById('criticalNodes').textContent = criticalCount;
        
        // Graph density
        const n = stats.total_nodes || 0;
        const density = n > 1 ? ((stats.total_links / (n * (n - 1))) * 100).toFixed(1) : 0;
        document.getElementById('graphDensity').textContent = `${density}%`;
    }
    
    showNodeTooltip(event, node) {
        const tooltip = document.getElementById('graphTooltip');
        tooltip.innerHTML = `
            <strong>${node.name}</strong><br>
            Type: ${node.type.replace('_', ' ')}<br>
            Status: ${node.status}<br>
            Priority: ${node.priority || 'N/A'}
        `;
        tooltip.style.display = 'block';
        tooltip.style.left = (event.pageX + 10) + 'px';
        tooltip.style.top = (event.pageY - 10) + 'px';
    }
    
    hideTooltip() {
        document.getElementById('graphTooltip').style.display = 'none';
    }
    
    handleResize() {
        const container = document.querySelector('.graph-wrapper');
        this.width = container.clientWidth;
        
        this.svg
            .attr('width', this.width)
            .attr('height', this.height);
        
        this.simulation
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .alpha(0.3)
            .restart();
    }
    
    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}
