// ============================================================================
// CORTEX Registry Explorer — D3.js Graph Renderer
// Interactive force-directed graph for cross-registry dependency DAG
// ============================================================================

const GraphRenderer = {
    /** @type {object|null} Current D3 simulation */
    _simulation: null,

    /**
     * Render the dependency graph into a container element.
     * @param {HTMLElement} container - DOM element to render into
     * @param {Object} graph - { nodes: [...], edges: [...] } from registry.json
     * @param {Object} [options] - Rendering options
     */
    render(container, graph, options = {}) {
        const { nodes = [], edges = [] } = graph;
        if (nodes.length === 0) {
            container.innerHTML = '<div class="empty-graph"><p>📊 No graph data available</p></div>';
            return;
        }

        const width = options.width || container.clientWidth || 800;
        const height = options.height || container.clientHeight || 600;

        // Clear previous
        container.innerHTML = '';

        // Type → color map
        const typeColors = {
            'governance-rule': '#ef4444',
            'workflow-template': '#3b82f6',
            'pattern': '#8b5cf6',
            'plan': '#10b981',
            'config': '#f59e0b',
            'knowledge': '#06b6d4',
            'response-template': '#ec4899',
            'generic': '#6b7280',
        };

        // Build SVG
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', width);
        svg.setAttribute('height', height);
        svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        svg.classList.add('graph-svg');
        container.appendChild(svg);

        // Filter controls
        const filterBar = document.createElement('div');
        filterBar.className = 'graph-filters';
        const types = [...new Set(nodes.map(n => n.type))].sort();
        types.forEach(t => {
            const btn = document.createElement('button');
            btn.className = 'filter-btn active';
            btn.dataset.type = t;
            btn.style.borderColor = typeColors[t] || '#6b7280';
            btn.textContent = `${t} (${nodes.filter(n => n.type === t).length})`;
            btn.onclick = () => this._toggleFilter(btn, svg, t);
            filterBar.appendChild(btn);
        });
        container.insertBefore(filterBar, svg);

        // Render nodes as circles + labels
        const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        nodeGroup.classList.add('nodes');

        // Render edges as lines
        const edgeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        edgeGroup.classList.add('edges');

        // Position nodes in a simple circular layout (no D3 dependency required)
        const cx = width / 2;
        const cy = height / 2;
        const radius = Math.min(width, height) * 0.35;
        const nodePositions = {};

        nodes.forEach((node, i) => {
            const angle = (2 * Math.PI * i) / nodes.length;
            const x = cx + radius * Math.cos(angle);
            const y = cy + radius * Math.sin(angle);
            nodePositions[node.id] = { x, y };

            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', x);
            circle.setAttribute('cy', y);
            circle.setAttribute('r', 6);
            circle.setAttribute('fill', typeColors[node.type] || '#6b7280');
            circle.setAttribute('data-type', node.type);
            circle.setAttribute('data-id', node.id);
            circle.classList.add('graph-node');

            const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
            title.textContent = `${node.id}\n${node.title || ''}\n${node.type}`;
            circle.appendChild(title);

            nodeGroup.appendChild(circle);
        });

        edges.forEach(edge => {
            const src = nodePositions[edge.source];
            const tgt = nodePositions[edge.target];
            if (!src || !tgt) return;

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', src.x);
            line.setAttribute('y1', src.y);
            line.setAttribute('x2', tgt.x);
            line.setAttribute('y2', tgt.y);
            line.setAttribute('stroke', 'rgba(255,255,255,0.15)');
            line.setAttribute('stroke-width', 1);
            line.classList.add('graph-edge');
            edgeGroup.appendChild(line);
        });

        svg.appendChild(edgeGroup);
        svg.appendChild(nodeGroup);

        // Stats bar
        const statsBar = document.createElement('div');
        statsBar.className = 'graph-stats';
        statsBar.innerHTML = `<span>📊 ${nodes.length} nodes · ${edges.length} edges · ${types.length} types</span>`;
        container.appendChild(statsBar);
    },

    _toggleFilter(btn, svg, type) {
        btn.classList.toggle('active');
        const show = btn.classList.contains('active');
        svg.querySelectorAll(`[data-type="${type}"]`).forEach(el => {
            el.style.display = show ? '' : 'none';
        });
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = GraphRenderer;
}
