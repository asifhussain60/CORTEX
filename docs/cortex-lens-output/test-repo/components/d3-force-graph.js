/**
 * D3.js Force-Directed Graph Component
 * 
 * Interactive network visualization for:
 * - Module dependencies
 * - API endpoint relationships
 * - Component architecture
 */

class D3ForceGraph {
    constructor(containerId, graphData) {
        this.container = document.getElementById(containerId);
        this.data = graphData;
        this.width = 800;
        this.height = 600;
        this.svg = null;
        this.simulation = null;

        if (this.container) {
            this.init();
        }
    }

    init() {
        // Clear container
        this.container.innerHTML = '';

        // Create SVG
        this.svg = d3.select(`#${this.container.id}`)
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('viewBox', [0, 0, this.width, this.height]);

        // Create force simulation
        this.simulation = d3.forceSimulation(this.data.nodes)
            .force('link', d3.forceLink(this.data.links)
                .id(d => d.id)
                .distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(40));

        this.render();
    }

    render() {
        // Create links
        const link = this.svg.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(this.data.links)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => Math.sqrt(d.value || 1));

        // Create nodes
        const node = this.svg.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(this.data.nodes)
            .enter()
            .append('g')
            .attr('class', 'node')
            .call(this.drag(this.simulation));

        // Add circles to nodes
        node.append('circle')
            .attr('r', d => d.size || 20)
            .attr('fill', d => this.getNodeColor(d.type))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);

        // Add labels to nodes
        node.append('text')
            .attr('dx', 0)
            .attr('dy', 30)
            .attr('text-anchor', 'middle')
            .attr('fill', '#fff')
            .attr('font-size', '12px')
            .text(d => d.label);

        // Add tooltips
        node.append('title')
            .text(d => `${d.label}\nType: ${d.type}\nConnections: ${d.connections || 0}`);

        // Update positions on tick
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });

        // Add zoom behavior
        this.svg.call(d3.zoom()
            .extent([[0, 0], [this.width, this.height]])
            .scaleExtent([0.5, 4])
            .on('zoom', (event) => {
                this.svg.selectAll('g').attr('transform', event.transform);
            }));
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
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }

    getNodeColor(type) {
        const colors = {
            'module': '#6366f1',
            'component': '#8b5cf6',
            'service': '#a855f7',
            'controller': '#c084fc',
            'utility': '#d8b4fe',
            'default': '#9ca3af'
        };
        return colors[type] || colors['default'];
    }

    update(newData) {
        this.data = newData;
        this.init();
    }
}

// Export
window.D3ForceGraph = D3ForceGraph;
