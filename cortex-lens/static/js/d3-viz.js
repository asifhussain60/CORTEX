/**
 * CORTEX LENS Dashboard - D3.js Visualization Wrappers
 * Renders data visualizations using D3.js v7
 */

(function() {
    'use strict';

    /**
     * Render import dependency graph (Tab 2)
     */
    window.renderImportGraph = function(data, container) {
        // Clear container
        container.innerHTML = '';

        if (!data || !data.nodes || !data.links) {
            container.innerHTML = '<p class="error">Invalid graph data</p>';
            return;
        }

        // Check if D3 is loaded
        if (typeof d3 === 'undefined') {
            container.innerHTML = '<p class="error">D3.js not loaded. Using CDN fallback...</p>';
            // Try loading from CDN
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/d3@7';
            script.onload = () => window.renderImportGraph(data, container);
            document.head.appendChild(script);
            return;
        }

        const width = container.clientWidth || 800;
        const height = 600;

        // Create SVG
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', [0, 0, width, height]);

        // Add background
        svg.append('rect')
            .attr('width', width)
            .attr('height', height)
            .attr('fill', '#0f172a');

        // Create force simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(50))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collide', d3.forceCollide(10));

        // Draw links
        const link = svg.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(data.links)
            .join('line')
            .attr('stroke', '#475569')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', 1);

        // Draw nodes
        const node = svg.append('g')
            .attr('class', 'nodes')
            .selectAll('circle')
            .data(data.nodes)
            .join('circle')
            .attr('r', d => d.size || 5)
            .attr('fill', d => d.color || '#64748b')
            .attr('stroke', '#1e293b')
            .attr('stroke-width', 1.5)
            .call(drag(simulation));

        // Add tooltips
        node.append('title')
            .text(d => `${d.id}\n${d.group}`);

        // Add labels for larger nodes
        const label = svg.append('g')
            .attr('class', 'labels')
            .selectAll('text')
            .data(data.nodes.filter(d => (d.size || 5) > 7))
            .join('text')
            .text(d => d.label || d.id.split('.').pop())
            .attr('font-size', 10)
            .attr('fill', '#cbd5e1')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.3em')
            .style('pointer-events', 'none');

        // Update positions on simulation tick
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);

            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });

        // Add circular dependency warning if any
        if (data.circular_dependencies && data.circular_dependencies.length > 0) {
            const warning = container.insertBefore(
                document.createElement('div'),
                container.firstChild
            );
            warning.className = 'circular-warning';
            warning.style.cssText = 'background: #7c2d12; color: #fecaca; padding: 8px 12px; margin-bottom: 8px; border-radius: 4px; font-size: 12px;';
            warning.innerHTML = `⚠️ ${data.circular_dependencies.length} circular dependencies detected`;
        }

        // Add stats
        const stats = container.appendChild(document.createElement('div'));
        stats.style.cssText = 'position: absolute; top: 10px; left: 10px; background: rgba(15, 23, 42, 0.8); padding: 8px 12px; border-radius: 4px; font-size: 12px; color: #cbd5e1;';
        stats.innerHTML = `Nodes: ${data.nodes.length} | Links: ${data.links.length}`;

        // Drag functionality
        function drag(simulation) {
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
    };

    /**
     * Render orchestrator constellation (Tab 3)
     */
    window.renderOrchestratorGraph = function(data, container) {
        // Clear container
        container.innerHTML = '';

        // Implementation coming in Sprint 4
        container.innerHTML = '<p class="info">Orchestrator graph - Coming in Sprint 4</p>';
    };

    /**
     * Render git timeline (Tab 4)
     */
    window.renderTimeline = function(data, container) {
        // Clear container
        container.innerHTML = '';

        // Implementation coming in Sprint 4
        container.innerHTML = '<p class="info">Timeline visualization - Coming in Sprint 4</p>';
    };

    /**
     * Render impact heatmap (Tab 5)
     */
    window.renderHeatmap = function(data, container) {
        // Clear container
        container.innerHTML = '';

        // Implementation coming in Sprint 4
        container.innerHTML = '<p class="info">Impact heatmap - Coming in Sprint 4</p>';
    };

    /**
     * Render brain architecture (Tab 6)
     */
    window.renderBrainArchitecture = function(data, container) {
        // Clear container
        container.innerHTML = '';

        // Implementation coming in Sprint 4
        container.innerHTML = '<p class="info">Brain architecture - Coming in Sprint 4</p>';
    };

})();
