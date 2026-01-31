/**
 * CORTEX LENS Dashboard - D3.js Visualization Wrappers
 * Renders data visualizations using D3.js v7
 */

(function() {
    'use strict';

    /**
     * Show loading spinner in container
     */
    function showLoading(container, message = 'Loading visualization...') {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; color: #b8c5d6;">
                <div style="width: 50px; height: 50px; border: 4px solid rgba(0, 212, 255, 0.2); border-top-color: #00d4ff; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <p style="margin-top: 1rem; font-size: 0.9rem;">${message}</p>
            </div>
            <style>
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            </style>
        `;
    }

    /**
     * Render import dependency graph (Tab 2)
     */
    window.renderImportGraph = function(data, container) {
        // Show loading
        showLoading(container, 'Building import graph...');
        
        // Use setTimeout to allow loading spinner to render
        setTimeout(() => {
            _renderImportGraphInternal(data, container);
        }, 10);
    };
    
    function _renderImportGraphInternal(data, container) {
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
        showLoading(container, 'Building orchestrator network...');
        setTimeout(() => {
            _renderOrchestratorGraphInternal(data, container);
        }, 10);
    };
    
    function _renderOrchestratorGraphInternal(data, container) {
        // Clear container
        container.innerHTML = '';

        if (!data || !data.nodes) {
            container.innerHTML = '<p class="error">Invalid orchestrator data</p>';
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

        // Category colors
        const categoryColors = {
            'core': '#00d4ff',
            'domain': '#7b2cbf',
            'support': '#06ffa5'
        };

        // Create force simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(80))
            .force('charge', d3.forceManyBody().strength(-400))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collide', d3.forceCollide(30));

        // Draw links
        const link = svg.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(data.links)
            .join('line')
            .attr('stroke', '#475569')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', 2)
            .attr('marker-end', 'url(#arrowhead)');

        // Add arrowhead marker
        svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '-0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 8)
            .attr('markerHeight', 8)
            .attr('xoverflow', 'visible')
            .append('svg:path')
            .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
            .attr('fill', '#475569')
            .style('stroke', 'none');

        // Draw nodes
        const node = svg.append('g')
            .attr('class', 'nodes')
            .selectAll('circle')
            .data(data.nodes)
            .join('circle')
            .attr('r', 12)
            .attr('fill', d => categoryColors[d.category] || '#64748b')
            .attr('stroke', '#1e293b')
            .attr('stroke-width', 2)
            .call(drag(simulation));

        // Add labels
        const label = svg.append('g')
            .attr('class', 'labels')
            .selectAll('text')
            .data(data.nodes)
            .join('text')
            .text(d => d.id)
            .attr('font-size', 10)
            .attr('fill', '#cbd5e1')
            .attr('text-anchor', 'middle')
            .attr('dy', 25)
            .style('pointer-events', 'none');

        // Add tooltips
        node.append('title')
            .text(d => `${d.id}\nCategory: ${d.category}\nCapabilities: ${d.capabilities.length}\nTier: ${d.tier}`);

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

        // Add stats
        const stats = container.appendChild(document.createElement('div'));
        stats.style.cssText = 'position: absolute; top: 10px; left: 10px; background: rgba(15, 23, 42, 0.8); padding: 8px 12px; border-radius: 4px; font-size: 12px; color: #cbd5e1;';
        stats.innerHTML = `
            <div><span style="color: #00d4ff">●</span> Core: ${data.stats.core}</div>
            <div><span style="color: #7b2cbf">●</span> Domain: ${data.stats.domain}</div>
            <div><span style="color: #06ffa5">●</span> Support: ${data.stats.support}</div>
        `;

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
     * Render git timeline (Tab 4)
     */
    window.renderTimeline = function(data, container) {
        showLoading(container, 'Analyzing git timeline...');
        setTimeout(() => {
            _renderTimelineInternal(data, container);
        }, 10);
    };
    
    function _renderTimelineInternal(data, container) {
        // Clear container
        container.innerHTML = '';

        if (!data || !data.commits || data.commits.length === 0) {
            container.innerHTML = '<p class="info">No git history available (may need .git directory)</p>';
            return;
        }

        const width = container.clientWidth || 800;
        const height = 400;

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

        // Parse dates
        const commits = data.commits.map(c => ({
            ...c,
            date: new Date(c.date)
        }));

        // Create scales
        const xScale = d3.scaleTime()
            .domain(d3.extent(commits, d => d.date))
            .range([60, width - 40]);

        const yScale = d3.scaleLinear()
            .domain([0, d3.max(commits, d => d.files_changed) || 10])
            .range([height - 40, 40]);

        // Draw axes
        svg.append('g')
            .attr('transform', `translate(0, ${height - 40})`)
            .call(d3.axisBottom(xScale).ticks(6))
            .attr('color', '#cbd5e1');

        svg.append('g')
            .attr('transform', 'translate(60, 0)')
            .call(d3.axisLeft(yScale).ticks(5))
            .attr('color', '#cbd5e1');

        // Draw circles for commits
        svg.append('g')
            .selectAll('circle')
            .data(commits)
            .join('circle')
            .attr('cx', d => xScale(d.date))
            .attr('cy', d => yScale(d.files_changed))
            .attr('r', 4)
            .attr('fill', '#00d4ff')
            .attr('opacity', 0.7)
            .append('title')
            .text(d => `${d.date.toLocaleDateString()}\n${d.author}\n${d.message}`);

        // Stats
        const stats = container.appendChild(document.createElement('div'));
        stats.style.cssText = 'position: absolute; top: 10px; left: 10px; background: rgba(15, 23, 42, 0.8); padding: 8px 12px; border-radius: 4px; font-size: 12px; color: #cbd5e1;';
        stats.innerHTML = `Commits: ${data.total_commits} | Authors: ${data.authors.length}`;
    };

    /**
     * Render impact heatmap (Tab 5)
     */
    window.renderHeatmap = function(data, container) {
        showLoading(container, 'Calculating impact analysis...');
        setTimeout(() => {
            _renderHeatmapInternal(data, container);
        }, 10);
    };
    
    function _renderHeatmapInternal(data, container) {
        // Clear container
        container.innerHTML = '';

        if (!data || !data.hotspots || data.hotspots.length === 0) {
            container.innerHTML = '<p class="info">No impact hotspots found (analyzing recent commits...)</p>';
            return;
        }

        // Create simple bar chart of hotspots
        const width = container.clientWidth || 800;
        const height = 400;

        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', [0, 0, width, height]);

        svg.append('rect')
            .attr('width', width)
            .attr('height', height)
            .attr('fill', '#0f172a');

        const margin = {top: 40, right: 40, bottom: 120, left: 60};
        const chartWidth = width - margin.left - margin.right;
        const chartHeight = height - margin.top - margin.bottom;

        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        const xScale = d3.scaleBand()
            .domain(data.hotspots.map((d, i) => i))
            .range([0, chartWidth])
            .padding(0.1);

        const yScale = d3.scaleLinear()
            .domain([0, d3.max(data.hotspots, d => d.changes) || 10])
            .range([chartHeight, 0]);

        // Draw bars
        g.selectAll('rect')
            .data(data.hotspots)
            .join('rect')
            .attr('x', (d, i) => xScale(i))
            .attr('y', d => yScale(d.changes))
            .attr('width', xScale.bandwidth())
            .attr('height', d => chartHeight - yScale(d.changes))
            .attr('fill', '#ff6b9d')
            .append('title')
            .text(d => `${d.file}\nChanges: ${d.changes}`);

        // Axes
        g.append('g')
            .attr('transform', `translate(0, ${chartHeight})`)
            .call(d3.axisBottom(xScale).tickFormat(i => data.hotspots[i].file.split('/').pop()))
            .attr('color', '#cbd5e1')
            .selectAll('text')
            .attr('transform', 'rotate(-45)')
            .style('text-anchor', 'end');

        g.append('g')
            .call(d3.axisLeft(yScale))
            .attr('color', '#cbd5e1');

        // Stats
        const stats = container.appendChild(document.createElement('div'));
        stats.style.cssText = 'position: absolute; top: 10px; left: 10px; background: rgba(15, 23, 42, 0.8); padding: 8px 12px; border-radius: 4px; font-size: 12px; color: #cbd5e1;';
        stats.innerHTML = `Impact Score: ${data.impact_score.toFixed(2)} | Hotspots: ${data.hotspots.length}`;
    };

    /**
     * Render brain architecture (Tab 6)
     */
    window.renderBrainArchitecture = function(data, container) {
        showLoading(container, 'Rendering brain architecture...');
        setTimeout(() => {
            _renderBrainArchitectureInternal(data, container);
        }, 10);
    };
    
    function _renderBrainArchitectureInternal(data, container) {
        // Clear container
        container.innerHTML = '';

        if (!data || !data.tiers) {
            container.innerHTML = '<p class="error">Invalid brain data</p>';
            return;
        }

        const width = container.clientWidth || 800;
        const height = 500;

        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', [0, 0, width, height]);

        svg.append('rect')
            .attr('width', width)
            .attr('height', height)
            .attr('fill', '#0f172a');

        // 4-Tier architecture visualization
        const tierHeight = height / data.tiers.length;
        const tierColors = ['#00d4ff', '#7b2cbf', '#06ffa5', '#ffb627'];

        data.tiers.forEach((tier, i) => {
            const y = i * tierHeight;

            // Draw tier rectangle
            svg.append('rect')
                .attr('x', 50)
                .attr('y', y + 20)
                .attr('width', width - 100)
                .attr('height', tierHeight - 40)
                .attr('fill', 'none')
                .attr('stroke', tierColors[i])
                .attr('stroke-width', 2)
                .attr('rx', 8);

            // Tier label
            svg.append('text')
                .attr('x', width / 2)
                .attr('y', y + tierHeight / 2 - 10)
                .attr('text-anchor', 'middle')
                .attr('font-size', 18)
                .attr('font-weight', 'bold')
                .attr('fill', tierColors[i])
                .text(tier.name);

            // Tier description
            svg.append('text')
                .attr('x', width / 2)
                .attr('y', y + tierHeight / 2 + 15)
                .attr('text-anchor', 'middle')
                .attr('font-size', 14)
                .attr('fill', '#cbd5e1')
                .text(tier.description);

            // Rules count
            if (tier.rules) {
                svg.append('text')
                    .attr('x', width / 2)
                    .attr('y', y + tierHeight / 2 + 35)
                    .attr('text-anchor', 'middle')
                    .attr('font-size', 12)
                    .attr('fill', '#6b7a90')
                    .text(`${tier.rules} rules`);
            }
        });

        // Title
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .attr('font-size', 16)
            .attr('font-weight', 'bold')
            .attr('fill', '#cbd5e1')
            .text('4-Tier Brain Architecture');
    };

})();
