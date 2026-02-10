/**
 * CORTEX LENS Dashboard Application
 * 
 * Handles data loading and D3.js visualizations
 * 
 * Author: Asif Hussain
 * Version: 1.0.0
 */

// ============================================================================
// DATA LOADER
// ============================================================================

const DataLoader = {
    cache: {},
    
    async load(dataPath) {
        if (this.cache[dataPath]) {
            return this.cache[dataPath];
        }
        
        try {
            const response = await fetch(dataPath);
            if (!response.ok) {
                console.warn(`Could not load ${dataPath}`);
                return null;
            }
            const data = await response.json();
            this.cache[dataPath] = data;
            return data;
        } catch (error) {
            console.warn(`Error loading ${dataPath}:`, error.message);
            return null;
        }
    },
    
    clearCache() {
        this.cache = {};
    }
};

// ============================================================================
// D3.JS VISUALIZATIONS
// ============================================================================

const Visualizations = {
    
    // Force-directed dependency graph
    renderDependencyGraph(containerId, data) {
        if (!data || !data.nodes || !data.links) {
            console.log('No dependency data available');
            return;
        }
        
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Clear existing content
        container.innerHTML = '';
        
        const width = container.clientWidth || 800;
        const height = 500;
        
        // Color scale for groups
        const color = d3.scaleOrdinal()
            .domain(['core', 'domain', 'support', 'brain', 'lens', 'wiring', 'infra'])
            .range(['#00d4ff', '#06ffa5', '#ffb627', '#7b2cbf', '#ff6b9d', '#667eea', '#6b7a90']);
        
        // Create SVG
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', [0, 0, width, height])
            .style('background', '#1a1f3a')
            .style('border-radius', '12px');
        
        // Create force simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => d.size + 5));
        
        // Draw links
        const link = svg.append('g')
            .attr('stroke', '#4a5568')
            .attr('stroke-opacity', 0.6)
            .selectAll('line')
            .data(data.links)
            .join('line')
            .attr('stroke-width', d => Math.sqrt(d.value));
        
        // Draw nodes
        const node = svg.append('g')
            .selectAll('circle')
            .data(data.nodes)
            .join('circle')
            .attr('r', d => d.size / 3)
            .attr('fill', d => color(d.group))
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)
            .call(drag(simulation));
        
        // Add labels
        const labels = svg.append('g')
            .selectAll('text')
            .data(data.nodes)
            .join('text')
            .text(d => d.id.split('.').pop())
            .attr('font-size', '10px')
            .attr('fill', '#b8c5d6')
            .attr('text-anchor', 'middle')
            .attr('dy', d => d.size / 3 + 15);
        
        // Add title on hover
        node.append('title')
            .text(d => d.id);
        
        // Update positions on tick
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            
            labels
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });
        
        // Drag behavior
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
        
        // Add legend
        const legend = svg.append('g')
            .attr('transform', `translate(20, 20)`);
        
        const groups = ['core', 'domain', 'support', 'brain', 'lens'];
        groups.forEach((group, i) => {
            legend.append('circle')
                .attr('cx', 0)
                .attr('cy', i * 20)
                .attr('r', 6)
                .attr('fill', color(group));
            
            legend.append('text')
                .attr('x', 15)
                .attr('y', i * 20 + 4)
                .attr('fill', '#b8c5d6')
                .attr('font-size', '11px')
                .text(group);
        });
    },
    
    // Timeline chart
    renderTimeline(containerId, data) {
        if (!data || !data.commit_frequency) {
            console.log('No timeline data available');
            return;
        }
        
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Clear existing content
        container.innerHTML = '';
        
        const margin = {top: 20, right: 30, bottom: 40, left: 50};
        const width = (container.clientWidth || 800) - margin.left - margin.right;
        const height = 400 - margin.top - margin.bottom;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .style('background', '#1a1f3a')
            .style('border-radius', '12px')
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        // Parse dates
        const parseDate = d3.timeParse('%Y-%m-%d');
        const commits = data.commit_frequency.map(d => ({
            date: parseDate(d.date),
            commits: d.commits,
            additions: d.additions,
            deletions: d.deletions
        }));
        
        // Scales
        const x = d3.scaleTime()
            .domain(d3.extent(commits, d => d.date))
            .range([0, width]);
        
        const y = d3.scaleLinear()
            .domain([0, d3.max(commits, d => d.commits)])
            .nice()
            .range([height, 0]);
        
        // Axes
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x).ticks(6))
            .attr('color', '#6b7a90');
        
        svg.append('g')
            .call(d3.axisLeft(y).ticks(5))
            .attr('color', '#6b7a90');
        
        // Line
        const line = d3.line()
            .x(d => x(d.date))
            .y(d => y(d.commits))
            .curve(d3.curveMonotoneX);
        
        svg.append('path')
            .datum(commits)
            .attr('fill', 'none')
            .attr('stroke', '#00d4ff')
            .attr('stroke-width', 2)
            .attr('d', line);
        
        // Area
        const area = d3.area()
            .x(d => x(d.date))
            .y0(height)
            .y1(d => y(d.commits))
            .curve(d3.curveMonotoneX);
        
        svg.append('path')
            .datum(commits)
            .attr('fill', 'rgba(0, 212, 255, 0.2)')
            .attr('d', area);
        
        // Points
        svg.selectAll('circle')
            .data(commits)
            .join('circle')
            .attr('cx', d => x(d.date))
            .attr('cy', d => y(d.commits))
            .attr('r', 4)
            .attr('fill', '#00d4ff');
        
        // Y-axis label
        svg.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('y', -40)
            .attr('x', -height / 2)
            .attr('fill', '#b8c5d6')
            .attr('font-size', '12px')
            .attr('text-anchor', 'middle')
            .text('Commits per Week');
    }
};

// ============================================================================
// MERMAID RENDERER
// ============================================================================

const MermaidRenderer = {
    async render(containerId, mermaidCode) {
        const container = document.getElementById(containerId);
        if (!container || !mermaidCode) return;
        
        try {
            const { svg } = await mermaid.render('mermaid-' + Date.now(), mermaidCode);
            container.innerHTML = svg;
        } catch (error) {
            console.warn('Mermaid render error:', error);
            container.innerHTML = `<pre style="color: #ff6b9d;">${error.message}</pre>`;
        }
    }
};

// ============================================================================
// EXPORTS
// ============================================================================

window.CortexLens = {
    DataLoader,
    Visualizations,
    MermaidRenderer
};

console.log('🧠 CORTEX LENS Dashboard JS loaded');
