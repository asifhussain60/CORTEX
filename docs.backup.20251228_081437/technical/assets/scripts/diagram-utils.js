/**
 * CORTEX Technical Documentation - D3.js Diagram Utilities
 * Version: 1.0.0
 * Author: Asif Hussain
 * Copyright: © 2025 Asif Hussain. All rights reserved.
 */

class DiagramUtils {
    constructor() {
        this.defaultColors = {
            primary: '#7C3AED',
            secondary: '#2563EB',
            accent: '#10B981',
            warning: '#F59E0B',
            error: '#EF4444',
            info: '#06B6D4'
        };
    }

    /**
     * Create force-directed graph
     */
    createForceGraph(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 600;

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        // Create force simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(50));

        // Add zoom behavior
        const g = svg.append('g');
        this.addZoom(svg, g);

        // Draw links
        const link = g.append('g')
            .selectAll('line')
            .data(data.links)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke-width', d => Math.sqrt(d.value || 1));

        // Draw nodes
        const node = g.append('g')
            .selectAll('g')
            .data(data.nodes)
            .enter()
            .append('g')
            .attr('class', d => `node node-${d.type || 'default'}`)
            .call(this.createDragBehavior(simulation));

        node.append('circle')
            .attr('r', d => d.size || 20);

        node.append('text')
            .text(d => d.label)
            .attr('text-anchor', 'middle')
            .attr('dy', 35);

        // Add tooltip
        const tooltip = this.createTooltip(container);
        this.addTooltipBehavior(node, tooltip);

        // Update positions on tick
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node.attr('transform', d => `translate(${d.x},${d.y})`);
        });

        return { svg, simulation, link, node };
    }

    /**
     * Create hierarchical tree
     */
    createTree(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 600;
        const orientation = options.orientation || 'vertical'; // 'vertical' or 'horizontal'

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g')
            .attr('transform', `translate(${width / 2},${50})`);

        this.addZoom(svg, g);

        // Create tree layout
        const treeLayout = d3.tree()
            .size(orientation === 'vertical' ? [width - 100, height - 100] : [height - 100, width - 100]);

        const root = d3.hierarchy(data);
        treeLayout(root);

        // Draw links
        const link = g.selectAll('.link')
            .data(root.links())
            .enter()
            .append('path')
            .attr('class', 'link')
            .attr('d', orientation === 'vertical' ? 
                d3.linkVertical()
                    .x(d => d.x)
                    .y(d => d.y) :
                d3.linkHorizontal()
                    .x(d => d.y)
                    .y(d => d.x)
            );

        // Draw nodes
        const node = g.selectAll('.node')
            .data(root.descendants())
            .enter()
            .append('g')
            .attr('class', 'node')
            .attr('transform', d => orientation === 'vertical' ? 
                `translate(${d.x},${d.y})` : 
                `translate(${d.y},${d.x})`
            );

        node.append('circle')
            .attr('r', 10);

        node.append('text')
            .text(d => d.data.name)
            .attr('dy', orientation === 'vertical' ? 20 : 5)
            .attr('dx', orientation === 'vertical' ? 0 : 15)
            .attr('text-anchor', orientation === 'vertical' ? 'middle' : 'start');

        return { svg, root, link, node };
    }

    /**
     * Create sequence diagram
     */
    createSequenceDiagram(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 600;
        const actorWidth = 120;
        const actorHeight = 40;
        const messageSpacing = 60;

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g')
            .attr('transform', 'translate(50, 50)');

        // Calculate actor positions
        const actorSpacing = (width - 100) / data.actors.length;
        const actors = data.actors.map((actor, i) => ({
            ...actor,
            x: actorSpacing * (i + 0.5),
            y: 0
        }));

        // Draw actors
        const actorGroups = g.selectAll('.actor')
            .data(actors)
            .enter()
            .append('g')
            .attr('class', 'actor')
            .attr('transform', d => `translate(${d.x},${d.y})`);

        actorGroups.append('rect')
            .attr('class', 'actor-box')
            .attr('x', -actorWidth / 2)
            .attr('y', 0)
            .attr('width', actorWidth)
            .attr('height', actorHeight);

        actorGroups.append('text')
            .attr('class', 'actor-label')
            .text(d => d.name)
            .attr('text-anchor', 'middle')
            .attr('y', actorHeight / 2 + 5);

        // Draw lifelines
        actorGroups.append('line')
            .attr('class', 'lifeline')
            .attr('x1', 0)
            .attr('y1', actorHeight)
            .attr('x2', 0)
            .attr('y2', height - 100);

        // Draw messages
        data.messages.forEach((message, i) => {
            const fromActor = actors.find(a => a.id === message.from);
            const toActor = actors.find(a => a.id === message.to);
            const y = actorHeight + messageSpacing * (i + 1);

            // Message arrow
            g.append('line')
                .attr('class', 'message-line')
                .attr('x1', fromActor.x)
                .attr('y1', y)
                .attr('x2', toActor.x)
                .attr('y2', y)
                .attr('marker-end', 'url(#arrow)');

            // Message label
            g.append('text')
                .attr('class', 'message-label')
                .text(message.label)
                .attr('x', (fromActor.x + toActor.x) / 2)
                .attr('y', y - 5)
                .attr('text-anchor', 'middle');
        });

        // Define arrow marker
        svg.append('defs').append('marker')
            .attr('id', 'arrow')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 8)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('class', 'arrow');

        return { svg, actors };
    }

    /**
     * Create flowchart
     */
    createFlowchart(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 600;

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g');
        this.addZoom(svg, g);

        // Layout nodes
        const nodeSpacing = 120;
        const levelHeight = 100;
        
        data.nodes.forEach((node, i) => {
            node.x = node.x || width / 2;
            node.y = node.y || levelHeight * (node.level || i);
        });

        // Draw connectors
        const links = g.selectAll('.connector')
            .data(data.links)
            .enter()
            .append('path')
            .attr('class', 'connector-line')
            .attr('d', d => {
                const source = data.nodes.find(n => n.id === d.source);
                const target = data.nodes.find(n => n.id === d.target);
                return `M${source.x},${source.y + 40} L${target.x},${target.y - 40}`;
            });

        // Draw nodes
        const nodes = g.selectAll('.flowchart-node')
            .data(data.nodes)
            .enter()
            .append('g')
            .attr('class', d => `node ${d.type}-node`)
            .attr('transform', d => `translate(${d.x},${d.y})`);

        // Different shapes for different node types
        nodes.each(function(d) {
            const node = d3.select(this);
            
            if (d.type === 'process') {
                node.append('rect')
                    .attr('x', -60)
                    .attr('y', -30)
                    .attr('width', 120)
                    .attr('height', 60);
            } else if (d.type === 'decision') {
                node.append('polygon')
                    .attr('points', '0,-40 80,0 0,40 -80,0');
            } else if (d.type === 'start' || d.type === 'end') {
                node.append('ellipse')
                    .attr('rx', 70)
                    .attr('ry', 35);
            }

            node.append('text')
                .text(d.label)
                .attr('text-anchor', 'middle')
                .attr('dy', 5);
        });

        return { svg, nodes, links };
    }

    /**
     * Add zoom and pan behavior
     */
    addZoom(svg, g) {
        const zoom = d3.zoom()
            .scaleExtent([0.5, 5])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });

        svg.call(zoom);

        return zoom;
    }

    /**
     * Create drag behavior for nodes
     */
    createDragBehavior(simulation) {
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }

    /**
     * Create tooltip
     */
    createTooltip(container) {
        return container.append('div')
            .attr('class', 'diagram-tooltip');
    }

    /**
     * Add tooltip behavior to nodes
     */
    addTooltipBehavior(nodes, tooltip) {
        nodes.on('mouseenter', function(event, d) {
            tooltip.html(`
                <div class="tooltip-title">${d.label || d.name}</div>
                <div class="tooltip-content">${d.description || 'No description'}</div>
                ${d.metadata ? `<div class="tooltip-meta">${d.metadata}</div>` : ''}
            `)
            .style('left', `${event.pageX + 10}px`)
            .style('top', `${event.pageY + 10}px`)
            .classed('show', true);
        })
        .on('mouseleave', function() {
            tooltip.classed('show', false);
        });
    }

    /**
     * Add zoom controls
     */
    addZoomControls(container, zoom, svg) {
        const controls = container.append('div')
            .attr('class', 'zoom-controls');

        controls.append('button')
            .attr('class', 'zoom-btn')
            .html('<i class="fas fa-plus"></i>')
            .on('click', () => {
                svg.transition().call(zoom.scaleBy, 1.3);
            });

        controls.append('button')
            .attr('class', 'zoom-btn')
            .html('<i class="fas fa-minus"></i>')
            .on('click', () => {
                svg.transition().call(zoom.scaleBy, 0.7);
            });

        controls.append('button')
            .attr('class', 'zoom-btn')
            .html('<i class="fas fa-compress"></i>')
            .on('click', () => {
                svg.transition().call(zoom.transform, d3.zoomIdentity);
            });

        return controls;
    }

    /**
     * Create Sankey diagram for migration flow visualization
     */
    createSankeyDiagram(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 600;

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g');
        this.addZoom(svg, g);

        // Create Sankey generator
        const sankey = d3.sankey()
            .nodeWidth(15)
            .nodePadding(10)
            .extent([[1, 1], [width - 1, height - 5]]);

        const {nodes, links} = sankey(data);

        // Add links with gradient
        const link = g.append('g')
            .selectAll('.link')
            .data(links)
            .enter().append('path')
            .attr('class', 'link')
            .attr('d', d3.sankeyLinkHorizontal())
            .attr('stroke-width', d => Math.max(1, d.width))
            .attr('fill', 'none')
            .attr('stroke', d => d.risk ? this.getRiskColor(d.risk) : this.defaultColors.primary)
            .attr('opacity', 0.5);

        // Add hover tooltips
        link.append('title')
            .text(d => `${d.source.name} → ${d.target.name}\n${d.value} LOC\nRisk: ${d.risk || 'LOW'}`);

        // Add nodes
        const node = g.append('g')
            .selectAll('.node')
            .data(nodes)
            .enter().append('g')
            .attr('class', 'node');

        node.append('rect')
            .attr('x', d => d.x0)
            .attr('y', d => d.y0)
            .attr('height', d => d.y1 - d.y0)
            .attr('width', d => d.x1 - d.x0)
            .attr('fill', this.defaultColors.primary)
            .attr('opacity', 0.8);

        node.append('text')
            .attr('x', d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
            .attr('y', d => (d.y1 + d.y0) / 2)
            .attr('dy', '0.35em')
            .attr('text-anchor', d => d.x0 < width / 2 ? 'start' : 'end')
            .text(d => d.name);

        return svg;
    }

    /**
     * Create DI Container network graph
     */
    createDIContainerGraph(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 600;

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g');
        this.addZoom(svg, g);

        // Create force simulation with clustering
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(150))
            .force('charge', d3.forceManyBody().strength(-500))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(60));

        // Draw links with arrow markers
        const defs = svg.append('defs');
        defs.append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '-0 -5 10 10')
            .attr('refX', 25)
            .attr('refY', 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .append('svg:path')
            .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
            .attr('fill', this.defaultColors.secondary);

        const link = g.append('g')
            .selectAll('line')
            .data(data.links)
            .enter().append('line')
            .attr('class', d => d.circular ? 'link circular' : 'link')
            .attr('stroke', d => d.circular ? this.defaultColors.error : this.defaultColors.secondary)
            .attr('stroke-width', 2)
            .attr('marker-end', 'url(#arrowhead)');

        // Draw nodes
        const node = g.append('g')
            .selectAll('g')
            .data(data.nodes)
            .enter().append('g')
            .attr('class', 'node')
            .call(this.createDragBehavior(simulation));

        node.append('circle')
            .attr('r', d => d.type === 'container' ? 30 : 20)
            .attr('fill', d => d.type === 'container' ? this.defaultColors.primary : this.defaultColors.accent);

        node.append('text')
            .attr('dy', 4)
            .attr('text-anchor', 'middle')
            .text(d => d.name);

        // Simulation tick
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node.attr('transform', d => `translate(${d.x},${d.y})`);
        });

        return svg;
    }

    /**
     * Create swimlane timeline diagram
     */
    createSwimlaneDiagram(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 600;
        const laneHeight = height / data.lanes.length;

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g');
        
        // Time scale
        const timeScale = d3.scaleLinear()
            .domain([0, d3.max(data.operations, d => d.endTime)])
            .range([100, width - 50]);

        // Draw lanes
        data.lanes.forEach((lane, i) => {
            g.append('rect')
                .attr('x', 0)
                .attr('y', i * laneHeight)
                .attr('width', width)
                .attr('height', laneHeight)
                .attr('fill', i % 2 === 0 ? '#f8f9fa' : '#ffffff')
                .attr('stroke', '#dee2e6');

            g.append('text')
                .attr('x', 10)
                .attr('y', i * laneHeight + laneHeight / 2)
                .attr('dy', '0.35em')
                .text(lane)
                .style('font-weight', 'bold');
        });

        // Draw operations
        data.operations.forEach(op => {
            const laneIndex = data.lanes.indexOf(op.lane);
            const y = laneIndex * laneHeight + laneHeight * 0.2;
            const barHeight = laneHeight * 0.6;

            const opGroup = g.append('g')
                .attr('class', 'operation');

            opGroup.append('rect')
                .attr('x', timeScale(op.startTime))
                .attr('y', y)
                .attr('width', timeScale(op.endTime) - timeScale(op.startTime))
                .attr('height', barHeight)
                .attr('fill', this.defaultColors.primary)
                .attr('opacity', 0.7)
                .attr('rx', 5);

            opGroup.append('text')
                .attr('x', (timeScale(op.startTime) + timeScale(op.endTime)) / 2)
                .attr('y', y + barHeight / 2)
                .attr('dy', '0.35em')
                .attr('text-anchor', 'middle')
                .attr('fill', 'white')
                .text(op.name);
        });

        // Time axis
        const axis = d3.axisTop(timeScale);
        g.append('g')
            .attr('transform', `translate(0, 0)`)
            .call(axis);

        return svg;
    }

    /**
     * Create finite state machine diagram
     */
    createStateMachine(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 600;

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g');
        this.addZoom(svg, g);

        // Layout states in a grid
        const cols = Math.ceil(Math.sqrt(data.states.length));
        const cellWidth = width / cols;
        const cellHeight = height / Math.ceil(data.states.length / cols);

        data.states.forEach((state, i) => {
            state.x = (i % cols) * cellWidth + cellWidth / 2;
            state.y = Math.floor(i / cols) * cellHeight + cellHeight / 2;
        });

        // Draw transitions
        const defs = svg.append('defs');
        defs.append('marker')
            .attr('id', 'fsm-arrow')
            .attr('viewBox', '-0 -5 10 10')
            .attr('refX', 35)
            .attr('refY', 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .append('svg:path')
            .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
            .attr('fill', this.defaultColors.secondary);

        g.selectAll('.transition')
            .data(data.transitions)
            .enter().append('path')
            .attr('class', 'transition')
            .attr('d', d => {
                const source = data.states.find(s => s.id === d.from);
                const target = data.states.find(s => s.id === d.to);
                return this.createCurvedPath(source, target);
            })
            .attr('fill', 'none')
            .attr('stroke', this.defaultColors.secondary)
            .attr('stroke-width', 2)
            .attr('marker-end', 'url(#fsm-arrow)');

        // Draw states
        const stateNodes = g.selectAll('.state')
            .data(data.states)
            .enter().append('g')
            .attr('class', 'state')
            .attr('transform', d => `translate(${d.x},${d.y})`);

        stateNodes.append('circle')
            .attr('r', 30)
            .attr('fill', d => {
                if (d.type === 'initial') return this.defaultColors.accent;
                if (d.type === 'final') return this.defaultColors.error;
                return this.defaultColors.primary;
            })
            .attr('opacity', 0.8);

        stateNodes.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.35em')
            .attr('fill', 'white')
            .text(d => d.name);

        return svg;
    }

    /**
     * Create decision tree diagram
     */
    createDecisionTree(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 600;

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g')
            .attr('transform', `translate(50,50)`);

        this.addZoom(svg, g);

        // Create tree layout
        const treeLayout = d3.tree().size([width - 100, height - 100]);
        const root = d3.hierarchy(data);
        const treeData = treeLayout(root);

        // Draw links
        g.selectAll('.link')
            .data(treeData.links())
            .enter().append('path')
            .attr('class', 'link')
            .attr('d', d3.linkVertical()
                .x(d => d.x)
                .y(d => d.y))
            .attr('fill', 'none')
            .attr('stroke', this.defaultColors.secondary)
            .attr('stroke-width', 2);

        // Draw nodes
        const node = g.selectAll('.node')
            .data(treeData.descendants())
            .enter().append('g')
            .attr('class', d => d.children ? 'node decision' : 'node leaf')
            .attr('transform', d => `translate(${d.x},${d.y})`);

        node.append('circle')
            .attr('r', d => d.children ? 8 : 6)
            .attr('fill', d => d.children ? this.defaultColors.primary : this.defaultColors.accent);

        node.append('text')
            .attr('dy', -15)
            .attr('text-anchor', 'middle')
            .text(d => d.data.name)
            .style('font-size', '12px');

        // Add condition labels on edges
        g.selectAll('.edge-label')
            .data(treeData.links())
            .enter().append('text')
            .attr('class', 'edge-label')
            .attr('x', d => (d.source.x + d.target.x) / 2)
            .attr('y', d => (d.source.y + d.target.y) / 2)
            .attr('text-anchor', 'middle')
            .text(d => d.target.data.condition || '')
            .style('font-size', '10px')
            .style('fill', this.defaultColors.info);

        return svg;
    }

    /**
     * Create treemap for coverage heatmap
     */
    createTreemap(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 600;

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        const root = d3.hierarchy(data)
            .sum(d => d.loc)
            .sort((a, b) => b.value - a.value);

        d3.treemap()
            .size([width, height])
            .padding(2)
            (root);

        // Color scale for coverage
        const colorScale = d3.scaleLinear()
            .domain([0, 50, 100])
            .range([this.defaultColors.error, this.defaultColors.warning, this.defaultColors.accent]);

        const cell = svg.selectAll('g')
            .data(root.leaves())
            .enter().append('g')
            .attr('transform', d => `translate(${d.x0},${d.y0})`);

        cell.append('rect')
            .attr('width', d => d.x1 - d.x0)
            .attr('height', d => d.y1 - d.y0)
            .attr('fill', d => colorScale(d.data.coverage))
            .attr('stroke', 'white')
            .attr('stroke-width', 2);

        cell.append('text')
            .attr('x', 5)
            .attr('y', 20)
            .text(d => d.data.name)
            .style('font-size', '11px')
            .style('fill', 'white');

        cell.append('text')
            .attr('x', 5)
            .attr('y', 35)
            .text(d => `${d.data.coverage}% coverage`)
            .style('font-size', '9px')
            .style('fill', 'white');

        // Tooltip
        cell.append('title')
            .text(d => `${d.data.name}\n${d.data.loc} LOC\n${d.data.coverage}% coverage`);

        return svg;
    }

    /**
     * Create animated flow diagram
     */
    createAnimatedFlow(container, data, options = {}) {
        const width = options.width || container.node().clientWidth;
        const height = options.height || 400;

        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height);

        const stageWidth = width / data.stages.length;
        const stageY = height / 2;

        // Draw stages
        data.stages.forEach((stage, i) => {
            const x = i * stageWidth + stageWidth / 2;

            svg.append('rect')
                .attr('x', x - 60)
                .attr('y', stageY - 40)
                .attr('width', 120)
                .attr('height', 80)
                .attr('fill', this.defaultColors.primary)
                .attr('opacity', 0.2)
                .attr('rx', 10);

            svg.append('text')
                .attr('x', x)
                .attr('y', stageY)
                .attr('text-anchor', 'middle')
                .text(stage.name)
                .style('font-weight', 'bold');

            svg.append('text')
                .attr('x', x)
                .attr('y', stageY + 20)
                .attr('text-anchor', 'middle')
                .text(`${stage.duration}ms`)
                .style('font-size', '11px')
                .style('fill', this.defaultColors.info);

            // Draw connections
            if (i < data.stages.length - 1) {
                svg.append('line')
                    .attr('x1', x + 60)
                    .attr('y1', stageY)
                    .attr('x2', x + stageWidth - 60)
                    .attr('y2', stageY)
                    .attr('stroke', this.defaultColors.secondary)
                    .attr('stroke-width', 2);
            }
        });

        // Animate particles
        this.animateFlowParticles(svg, data.stages, stageWidth, stageY);

        return svg;
    }

    /**
     * Animate particles along flow
     */
    animateFlowParticles(svg, stages, stageWidth, stageY) {
        const duration = stages.reduce((sum, s) => sum + s.duration, 0);
        
        function animate() {
            const particle = svg.append('circle')
                .attr('r', 5)
                .attr('fill', '#10B981')
                .attr('cx', stageWidth / 2)
                .attr('cy', stageY);

            let delay = 0;
            stages.forEach((stage, i) => {
                const x = i * stageWidth + stageWidth / 2;
                particle.transition()
                    .delay(delay)
                    .duration(stage.duration)
                    .attr('cx', x + (i < stages.length - 1 ? stageWidth : 0));
                delay += stage.duration;
            });

            particle.transition()
                .delay(duration)
                .remove();
        }

        // Start animation loop
        setInterval(animate, 2000);
        animate();
    }

    /**
     * Helper: Create curved path between two points
     */
    createCurvedPath(source, target) {
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dr = Math.sqrt(dx * dx + dy * dy);
        return `M${source.x},${source.y}A${dr},${dr} 0 0,1 ${target.x},${target.y}`;
    }

    /**
     * Helper: Get risk color
     */
    getRiskColor(risk) {
        const colors = {
            'LOW': this.defaultColors.accent,
            'MEDIUM': this.defaultColors.warning,
            'HIGH': this.defaultColors.error
        };
        return colors[risk] || this.defaultColors.info;
    }

    /**
     * Export diagram as PNG
     */
    exportToPNG(svg, filename = 'diagram.png') {
        const svgData = new XMLSerializer().serializeToString(svg.node());
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();

        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
            const pngFile = canvas.toDataURL('image/png');
            
            const downloadLink = document.createElement('a');
            downloadLink.download = filename;
            downloadLink.href = pngFile;
            downloadLink.click();
        };

        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    }

    /**
     * Export diagram as SVG
     */
    exportToSVG(svg, filename = 'diagram.svg') {
        const svgData = new XMLSerializer().serializeToString(svg.node());
        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
        const svgUrl = URL.createObjectURL(svgBlob);
        
        const downloadLink = document.createElement('a');
        downloadLink.href = svgUrl;
        downloadLink.download = filename;
        downloadLink.click();
    }
}

// Export for use in other scripts
window.DiagramUtils = DiagramUtils;
