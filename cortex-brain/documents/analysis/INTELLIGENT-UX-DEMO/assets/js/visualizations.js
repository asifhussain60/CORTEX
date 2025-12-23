/**
 * CORTEX UX Enhancement Dashboard - Visualizations
 * D3.js visualization implementations for all 6 tabs
 */

// Global data store
let dashboardData = null;

/**
 * Load analysis data from JSON file
 */
async function loadAnalysisData() {
    try {
        console.log('🔍 Loading analysis data from analysis-data.json...');
        
        // Fetch real data from analysis-data.json
        const response = await fetch('analysis-data.json');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        dashboardData = await response.json();
        console.log('✅ Analysis data loaded successfully:', dashboardData.metadata.projectName);
        
        // Validate data structure
        if (!dashboardData.metadata || !dashboardData.scores || !dashboardData.architecture) {
            throw new Error('Invalid data structure in analysis-data.json');
        }
        
        // Initialize all visualizations with real data
        initializeExecutiveSummary();
        initializeArchitectureTab();
        initializeQualityTab();
        initializeRoadmapTab();
        initializeJourneyTab();
        initializeSecurityTab();
        
        // Show discovery panel if there are recommendations
        if (dashboardData.discoveries && dashboardData.discoveries.length > 0) {
            setTimeout(() => showDiscoveryPanel(), 2000);
        }
        
        console.log('🎨 All visualizations initialized with real data');
        
    } catch (error) {
        handleDataLoadFailure(error);
    }
}

/**
 * Handle data loading failure
 * REAL DATA ONLY - No mock data fallback
 */
function handleDataLoadFailure(error) {
    console.error('❌ CRITICAL: Failed to load analysis-data.json', error);
    
    // Display user-friendly error message
    const errorHTML = `
        <div class="flex items-center justify-center h-screen">
            <div class="text-center p-8 max-w-2xl">
                <div class="text-6xl mb-4">⚠️</div>
                <h1 class="text-3xl font-bold mb-4 text-red-600">Data Load Failed</h1>
                <p class="text-lg mb-6 text-gray-700">
                    Unable to load <code>analysis-data.json</code>. 
                    The dashboard requires real analysis data to function.
                </p>
                <div class="bg-gray-100 p-4 rounded-lg text-left">
                    <p class="font-semibold mb-2">Troubleshooting:</p>
                    <ul class="list-disc list-inside space-y-1 text-sm">
                        <li>Ensure <code>analysis-data.json</code> exists in the same directory</li>
                        <li>Run on a web server (not <code>file://</code> protocol)</li>
                        <li>Check browser console for CORS errors</li>
                        <li>Verify JSON file is valid (not corrupted)</li>
                    </ul>
                </div>
                <div class="mt-6">
                    <button onclick="location.reload()" 
                            class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-6 rounded">
                        Retry
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.innerHTML = errorHTML;
}

/**
 * Tab 1: Executive Summary
 */
function initializeExecutiveSummary() {
    console.log('Initializing Executive Summary...');
    if (!dashboardData) {
        console.error('No dashboardData available');
        return;
    }
    
    const { scores, summary } = dashboardData;
    console.log('Scores:', scores);
    console.log('Summary:', summary);
    
    // Update score cards
    D3Utils.updateScore('overall-score', scores.overall);
    D3Utils.updateScore('quality-score', scores.quality);
    D3Utils.updateScore('performance-score', scores.performance);
    D3Utils.updateScore('security-score', scores.security);
    
    // Animate progress bars
    D3Utils.animateProgressBar('overall-progress', scores.overall);
    D3Utils.animateProgressBar('quality-progress', scores.quality);
    D3Utils.animateProgressBar('performance-progress', scores.performance);
    D3Utils.animateProgressBar('security-progress', scores.security);
    
    // Update summary text
    document.getElementById('summary-text').innerHTML = `<p>${summary.text}</p>`;
    
    // Update quick wins
    const quickWinsList = document.getElementById('quick-wins-list');
    quickWinsList.innerHTML = summary.quickWins
        .map(win => `<li class="flex items-start space-x-2">
            <span class="text-green-500 mt-1">✓</span>
            <span>${win}</span>
        </li>`)
        .join('');
    
    // Update critical issues
    const criticalIssuesList = document.getElementById('critical-issues-list');
    criticalIssuesList.innerHTML = summary.criticalIssues
        .map(issue => `<li class="flex items-start space-x-2">
            <span class="text-red-500 mt-1">⚠</span>
            <span>${issue}</span>
        </li>`)
        .join('');
}

/**
 * Tab 2: Architecture
 */
function initializeArchitectureTab() {
    if (!dashboardData) return;
    
    const { components, relationships, issues } = dashboardData.architecture;
    
    // Create force-directed graph
    const graphData = {
        nodes: components.map(c => ({ ...c })),
        links: relationships.map(r => ({ ...r }))
    };
    
    D3Utils.createForceGraph('architecture-graph', graphData, {
        dimensions: { height: 600 }
    });
    
    // Populate component list
    const componentList = document.getElementById('component-list');
    componentList.innerHTML = components
        .map(comp => `
            <div class="mb-3 p-3 border border-gray-200 dark:border-gray-700 rounded">
                <div class="flex items-center space-x-2">
                    <div class="w-4 h-4 rounded" style="background-color: ${comp.color}"></div>
                    <strong>${comp.name}</strong>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">${comp.description}</p>
            </div>
        `)
        .join('');
    
    // Populate architectural issues
    const issuesList = document.getElementById('architecture-issues');
    issuesList.innerHTML = issues
        .map(issue => `
            <div class="mb-3 p-3 border-l-4 ${issue.severity === 'high' ? 'border-red-500' : 'border-yellow-500'} bg-gray-50 dark:bg-gray-800 rounded">
                <div class="font-semibold">${issue.type}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">${issue.file}</div>
                ${issue.complexity ? `<div class="text-sm mt-1">Complexity: ${issue.complexity}</div>` : ''}
            </div>
        `)
        .join('');
}

/**
 * Tab 3: Quality
 */
function initializeQualityTab() {
    if (!dashboardData) return;
    
    const { codeSmells, complexity, maintainability } = dashboardData.quality;
    
    // Code smells heatmap
    const heatmapData = codeSmells.map(smell => ({
        x: smell.file,
        y: smell.type,
        value: smell.count
    }));
    
    D3Utils.createHeatmap('quality-heatmap', heatmapData, {
        dimensions: { height: 400 }
    });
    
    // Complexity treemap
    createComplexityTreemap(complexity);
    
    // Maintainability bar chart
    createMaintainabilityChart(maintainability);
}

function createComplexityTreemap(data) {
    const { svg, width, height } = D3Utils.createSVG('complexity-treemap', { 
        dimensions: { height: 400, margin: { top: 10, right: 10, bottom: 10, left: 10 } }
    });
    
    const root = d3.hierarchy({ children: data })
        .sum(d => d.complexity)
        .sort((a, b) => b.value - a.value);
    
    d3.treemap()
        .size([width, height])
        .padding(2)(root);
    
    const tooltip = D3Utils.createTooltip();
    
    const cell = svg.selectAll('g')
        .data(root.leaves())
        .enter()
        .append('g')
        .attr('transform', d => `translate(${d.x0},${d.y0})`);
    
    cell.append('rect')
        .attr('width', d => d.x1 - d.x0)
        .attr('height', d => d.y1 - d.y0)
        .attr('fill', d => D3Utils.getScoreColor(100 - d.data.complexity * 2))
        .attr('opacity', 0.8)
        .on('mouseover', (event, d) => {
            D3Utils.showTooltip(tooltip, 
                `<strong>${d.data.name}</strong><br>Complexity: ${d.data.complexity}<br>Lines: ${d.data.lines}`,
                event
            );
        })
        .on('mouseout', () => D3Utils.hideTooltip(tooltip));
    
    cell.append('text')
        .attr('x', 4)
        .attr('y', 16)
        .style('font-size', '11px')
        .style('fill', 'white')
        .text(d => D3Utils.truncateText(d.data.name, d.x1 - d.x0 - 8));
}

function createMaintainabilityChart(data) {
    const { svg, width, height } = D3Utils.createSVG('maintainability-chart', {
        dimensions: { height: 400 }
    });
    
    const xScale = d3.scaleBand()
        .domain(data.map(d => d.metric))
        .range([0, width])
        .padding(0.3);
    
    const yScale = d3.scaleLinear()
        .domain([0, 100])
        .range([height, 0]);
    
    const tooltip = D3Utils.createTooltip();
    
    // Target lines
    svg.selectAll('.target-line')
        .data(data)
        .enter()
        .append('line')
        .attr('x1', d => xScale(d.metric))
        .attr('x2', d => xScale(d.metric) + xScale.bandwidth())
        .attr('y1', d => yScale(d.target))
        .attr('y2', d => yScale(d.target))
        .attr('stroke', '#94a3b8')
        .attr('stroke-dasharray', '4,4')
        .attr('stroke-width', 2);
    
    // Bars
    svg.selectAll('.bar')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.metric))
        .attr('y', height)
        .attr('width', xScale.bandwidth())
        .attr('height', 0)
        .attr('fill', d => D3Utils.getScoreColor(d.value))
        .on('mouseover', (event, d) => {
            D3Utils.showTooltip(tooltip, 
                `<strong>${d.metric}</strong><br>Current: ${d.value}%<br>Target: ${d.target}%`,
                event
            );
        })
        .on('mouseout', () => D3Utils.hideTooltip(tooltip))
        .transition()
        .duration(1000)
        .attr('y', d => yScale(d.value))
        .attr('height', d => height - yScale(d.value));
    
    // Axes
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale))
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end')
        .style('fill', 'var(--text-primary)');
    
    svg.append('g')
        .call(d3.axisLeft(yScale))
        .style('color', 'var(--text-primary)');
}

/**
 * Tab 4: Roadmap
 */
function initializeRoadmapTab() {
    if (!dashboardData) return;
    
    const { tasks, dependencies } = dashboardData.roadmap;
    
    // Gantt chart
    createGanttChart(tasks);
    
    // Priority matrix
    createPriorityMatrix(tasks);
    
    // Dependency graph
    createDependencyGraph(tasks, dependencies);
}

function createGanttChart(tasks) {
    const { svg, width, height } = D3Utils.createSVG('roadmap-gantt', {
        dimensions: { height: 500, margin: { top: 20, right: 20, bottom: 40, left: 150 } }
    });
    
    const xScale = d3.scaleLinear()
        .domain([0, d3.max(tasks, d => d.start + d.duration)])
        .range([0, width]);
    
    const yScale = d3.scaleBand()
        .domain(tasks.map(d => d.name))
        .range([0, height])
        .padding(0.2);
    
    const colorMap = {
        critical: '#ef4444',
        high: '#f59e0b',
        medium: '#3b82f6',
        low: '#6b7280'
    };
    
    const tooltip = D3Utils.createTooltip();
    
    // Bars
    svg.selectAll('.task')
        .data(tasks)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.start))
        .attr('y', d => yScale(d.name))
        .attr('width', d => xScale(d.duration))
        .attr('height', yScale.bandwidth())
        .attr('fill', d => colorMap[d.priority])
        .attr('rx', 4)
        .on('mouseover', (event, d) => {
            D3Utils.showTooltip(tooltip,
                `<strong>${d.name}</strong><br>Duration: ${d.duration} days<br>Priority: ${d.priority}`,
                event
            );
        })
        .on('mouseout', () => D3Utils.hideTooltip(tooltip));
    
    // Axes
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale).ticks(10))
        .style('color', 'var(--text-primary)');
    
    svg.append('g')
        .call(d3.axisLeft(yScale))
        .style('color', 'var(--text-primary)');
    
    // Add legend
    D3Utils.createLegend(svg, [
        { label: 'Critical', color: colorMap.critical },
        { label: 'High', color: colorMap.high },
        { label: 'Medium', color: colorMap.medium },
        { label: 'Low', color: colorMap.low }
    ], { x: width - 80, y: 0 });
}

function createPriorityMatrix(tasks) {
    const { svg, width, height } = D3Utils.createSVG('priority-matrix', {
        dimensions: { height: 400 }
    });
    
    const xScale = d3.scaleLinear()
        .domain([0, 10])
        .range([0, width]);
    
    const yScale = d3.scaleLinear()
        .domain([0, 10])
        .range([height, 0]);
    
    const tooltip = D3Utils.createTooltip();
    
    // Quadrant backgrounds
    const quadrants = [
        { x: 0, y: 0, width: width/2, height: height/2, label: 'Quick Wins', color: '#10b981' },
        { x: width/2, y: 0, width: width/2, height: height/2, label: 'Major Projects', color: '#3b82f6' },
        { x: 0, y: height/2, width: width/2, height: height/2, label: 'Fill Ins', color: '#6b7280' },
        { x: width/2, y: height/2, width: width/2, height: height/2, label: 'Thankless Tasks', color: '#ef4444' }
    ];
    
    svg.selectAll('.quadrant')
        .data(quadrants)
        .enter()
        .append('rect')
        .attr('x', d => d.x)
        .attr('y', d => d.y)
        .attr('width', d => d.width)
        .attr('height', d => d.height)
        .attr('fill', d => d.color)
        .attr('opacity', 0.1);
    
    // Plot tasks
    svg.selectAll('.task-point')
        .data(tasks)
        .enter()
        .append('circle')
        .attr('cx', d => xScale(d.effort))
        .attr('cy', d => yScale(d.impact))
        .attr('r', 8)
        .attr('fill', '#3b82f6')
        .attr('opacity', 0.7)
        .on('mouseover', (event, d) => {
            D3Utils.showTooltip(tooltip,
                `<strong>${d.name}</strong><br>Impact: ${d.impact}/10<br>Effort: ${d.effort}/10`,
                event
            );
        })
        .on('mouseout', () => D3Utils.hideTooltip(tooltip));
    
    // Axes
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale))
        .style('color', 'var(--text-primary)')
        .append('text')
        .attr('x', width / 2)
        .attr('y', 35)
        .attr('fill', 'var(--text-primary)')
        .text('Effort →');
    
    svg.append('g')
        .call(d3.axisLeft(yScale))
        .style('color', 'var(--text-primary)')
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -height / 2)
        .attr('y', -45)
        .attr('fill', 'var(--text-primary)')
        .text('← Impact');
}

function createDependencyGraph(tasks, dependencies) {
    const { svg, width, height } = D3Utils.createSVG('dependency-graph', {
        dimensions: { height: 400 }
    });
    
    const nodes = tasks.map(t => ({ id: t.id, name: t.name }));
    const links = dependencies.map(d => ({ source: d.source, target: d.target }));
    
    D3Utils.createForceGraph('dependency-graph', { nodes, links }, {
        dimensions: { height: 400 }
    });
}

/**
 * Tab 5: Journey (Performance)
 */
function initializeJourneyTab() {
    if (!dashboardData) return;
    
    const { bottlenecks, dataFlow } = dashboardData.performance;
    
    // Flamegraph
    createFlamegraph(bottlenecks);
    
    // Sankey diagram
    createSankeyDiagram(dataFlow);
    
    // Optimization timeline
    createOptimizationTimeline();
}

function createFlamegraph(data) {
    const { svg, width, height } = D3Utils.createSVG('performance-flamegraph', {
        dimensions: { height: 500 }
    });
    
    const xScale = d3.scaleBand()
        .domain(data.map(d => d.function))
        .range([0, width])
        .padding(0.1);
    
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.time)])
        .range([height, 0]);
    
    const colorScale = d3.scaleSequential()
        .domain([0, d3.max(data, d => d.time)])
        .interpolator(d3.interpolateRdYlGn);
    
    const tooltip = D3Utils.createTooltip();
    
    svg.selectAll('.flame')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.function))
        .attr('y', height)
        .attr('width', xScale.bandwidth())
        .attr('height', 0)
        .attr('fill', d => colorScale(d3.max(data, d => d.time) - d.time))
        .on('mouseover', (event, d) => {
            D3Utils.showTooltip(tooltip,
                `<strong>${d.function}</strong><br>Time: ${d.time}ms<br>Calls: ${d.calls.toLocaleString()}`,
                event
            );
        })
        .on('mouseout', () => D3Utils.hideTooltip(tooltip))
        .transition()
        .duration(1000)
        .attr('y', d => yScale(d.time))
        .attr('height', d => height - yScale(d.time));
    
    // Axes
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale))
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end')
        .style('fill', 'var(--text-primary)');
    
    svg.append('g')
        .call(d3.axisLeft(yScale))
        .style('color', 'var(--text-primary)');
}

function createSankeyDiagram(data) {
    const { svg, width, height } = D3Utils.createSVG('dataflow-sankey', {
        dimensions: { height: 400 }
    });
    
    const nodes = [...new Set(data.flatMap(d => [d.source, d.target]))].map(name => ({ name }));
    const links = data.map(d => ({
        source: nodes.findIndex(n => n.name === d.source),
        target: nodes.findIndex(n => n.name === d.target),
        value: d.value
    }));
    
    const sankey = d3.sankey()
        .nodeWidth(15)
        .nodePadding(10)
        .extent([[1, 1], [width - 1, height - 6]]);
    
    const { nodes: sankeyNodes, links: sankeyLinks } = sankey({
        nodes: nodes.map(d => Object.assign({}, d)),
        links: links.map(d => Object.assign({}, d))
    });
    
    const tooltip = D3Utils.createTooltip();
    
    // Links
    svg.append('g')
        .selectAll('path')
        .data(sankeyLinks)
        .enter()
        .append('path')
        .attr('d', d3.sankeyLinkHorizontal())
        .attr('stroke-width', d => Math.max(1, d.width))
        .style('fill', 'none')
        .style('stroke', '#3b82f6')
        .style('opacity', 0.5);
    
    // Nodes
    svg.append('g')
        .selectAll('rect')
        .data(sankeyNodes)
        .enter()
        .append('rect')
        .attr('x', d => d.x0)
        .attr('y', d => d.y0)
        .attr('height', d => d.y1 - d.y0)
        .attr('width', d => d.x1 - d.x0)
        .style('fill', '#3b82f6')
        .on('mouseover', (event, d) => {
            D3Utils.showTooltip(tooltip, `<strong>${d.name}</strong>`, event);
        })
        .on('mouseout', () => D3Utils.hideTooltip(tooltip));
    
    // Labels
    svg.append('g')
        .selectAll('text')
        .data(sankeyNodes)
        .enter()
        .append('text')
        .attr('x', d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
        .attr('y', d => (d.y1 + d.y0) / 2)
        .attr('dy', '0.35em')
        .attr('text-anchor', d => d.x0 < width / 2 ? 'start' : 'end')
        .text(d => d.name)
        .style('font-size', '12px')
        .style('fill', 'var(--text-primary)');
}

function createOptimizationTimeline() {
    const container = document.getElementById('optimization-timeline');
    container.innerHTML = `
        <div class="space-y-4">
            <div class="flex items-start">
                <div class="w-24 text-sm text-gray-500 dark:text-gray-400">Week 1-2</div>
                <div class="flex-1 border-l-2 border-blue-500 pl-4 pb-4">
                    <div class="font-semibold">Quick Performance Wins</div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">Database query optimization, caching strategies</div>
                </div>
            </div>
            <div class="flex items-start">
                <div class="w-24 text-sm text-gray-500 dark:text-gray-400">Week 3-4</div>
                <div class="flex-1 border-l-2 border-green-500 pl-4 pb-4">
                    <div class="font-semibold">Algorithm Improvements</div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">Optimize data processing algorithms</div>
                </div>
            </div>
            <div class="flex items-start">
                <div class="w-24 text-sm text-gray-500 dark:text-gray-400">Week 5-6</div>
                <div class="flex-1 border-l-2 border-purple-500 pl-4">
                    <div class="font-semibold">Architecture Refactoring</div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">Implement async processing, load balancing</div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Tab 6: Security
 */
function initializeSecurityTab() {
    if (!dashboardData) return;
    
    const { vulnerabilities, owasp, riskScore } = dashboardData.security;
    
    // Update vulnerability counts
    document.getElementById('critical-vulns').textContent = vulnerabilities.critical;
    document.getElementById('high-vulns').textContent = vulnerabilities.high;
    document.getElementById('medium-vulns').textContent = vulnerabilities.medium;
    
    // Severity chart
    createSeverityChart(vulnerabilities);
    
    // OWASP radar chart
    createOwaspRadar(owasp);
    
    // Risk gauge
    createRiskGauge(riskScore);
}

function createSeverityChart(data) {
    const { svg, width, height } = D3Utils.createSVG('security-severity-chart', {
        dimensions: { height: 400 }
    });
    
    const severities = Object.keys(data);
    const counts = Object.values(data);
    
    const xScale = d3.scaleBand()
        .domain(severities)
        .range([0, width])
        .padding(0.3);
    
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(counts)])
        .range([height, 0]);
    
    const colorMap = {
        critical: '#ef4444',
        high: '#f59e0b',
        medium: '#fbbf24',
        low: '#3b82f6'
    };
    
    svg.selectAll('.bar')
        .data(severities)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d))
        .attr('y', height)
        .attr('width', xScale.bandwidth())
        .attr('height', 0)
        .attr('fill', d => colorMap[d])
        .transition()
        .duration(1000)
        .attr('y', d => yScale(data[d]))
        .attr('height', d => height - yScale(data[d]));
    
    // Value labels
    svg.selectAll('.label')
        .data(severities)
        .enter()
        .append('text')
        .attr('x', d => xScale(d) + xScale.bandwidth() / 2)
        .attr('y', d => yScale(data[d]) - 5)
        .attr('text-anchor', 'middle')
        .style('fill', 'var(--text-primary)')
        .text(d => data[d]);
    
    // Axes
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale))
        .style('color', 'var(--text-primary)');
    
    svg.append('g')
        .call(d3.axisLeft(yScale))
        .style('color', 'var(--text-primary)');
}

function createOwaspRadar(data) {
    const { svg, width, height } = D3Utils.createSVG('owasp-chart', {
        dimensions: { height: 400 }
    });
    
    const radius = Math.min(width, height) / 2 - 40;
    const angleSlice = (Math.PI * 2) / data.length;
    
    const rScale = d3.scaleLinear()
        .domain([0, 100])
        .range([0, radius]);
    
    const g = svg.append('g')
        .attr('transform', `translate(${width/2},${height/2})`);
    
    // Draw circular grid
    const levels = 5;
    for (let i = 1; i <= levels; i++) {
        g.append('circle')
            .attr('r', radius * i / levels)
            .style('fill', 'none')
            .style('stroke', 'var(--border-color)')
            .style('stroke-width', 1);
    }
    
    // Draw axes
    data.forEach((d, i) => {
        const angle = angleSlice * i - Math.PI / 2;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        
        g.append('line')
            .attr('x1', 0)
            .attr('y1', 0)
            .attr('x2', x)
            .attr('y2', y)
            .style('stroke', 'var(--border-color)')
            .style('stroke-width', 1);
        
        // Labels
        const labelX = Math.cos(angle) * (radius + 20);
        const labelY = Math.sin(angle) * (radius + 20);
        
        g.append('text')
            .attr('x', labelX)
            .attr('y', labelY)
            .attr('text-anchor', labelX > 0 ? 'start' : 'end')
            .style('font-size', '10px')
            .style('fill', 'var(--text-primary)')
            .text(d.category.split(' - ')[0]);
    });
    
    // Draw data area
    const lineGenerator = d3.lineRadial()
        .angle((d, i) => angleSlice * i)
        .radius(d => rScale(d.score))
        .curve(d3.curveLinearClosed);
    
    g.append('path')
        .datum(data)
        .attr('d', lineGenerator)
        .style('fill', '#3b82f6')
        .style('fill-opacity', 0.3)
        .style('stroke', '#3b82f6')
        .style('stroke-width', 2);
    
    // Draw data points
    g.selectAll('.point')
        .data(data)
        .enter()
        .append('circle')
        .attr('cx', (d, i) => Math.cos(angleSlice * i - Math.PI / 2) * rScale(d.score))
        .attr('cy', (d, i) => Math.sin(angleSlice * i - Math.PI / 2) * rScale(d.score))
        .attr('r', 4)
        .style('fill', '#3b82f6');
}

function createRiskGauge(score) {
    const { svg, width, height } = D3Utils.createSVG('risk-gauge', {
        dimensions: { height: 400, margin: { top: 20, right: 20, bottom: 20, left: 20 } }
    });
    
    const radius = Math.min(width, height) / 2;
    const arcGenerator = d3.arc()
        .innerRadius(radius * 0.65)
        .outerRadius(radius)
        .startAngle(-Math.PI / 2)
        .cornerRadius(10);
    
    const g = svg.append('g')
        .attr('transform', `translate(${width/2},${height/2})`);
    
    // Background arc
    g.append('path')
        .datum({ endAngle: Math.PI / 2 })
        .attr('d', arcGenerator)
        .style('fill', 'var(--border-color)');
    
    // Score arc
    const scoreAngle = -Math.PI / 2 + (Math.PI * score / 100);
    g.append('path')
        .datum({ endAngle: scoreAngle })
        .attr('d', arcGenerator)
        .style('fill', D3Utils.getScoreColor(100 - score))
        .transition()
        .duration(1500)
        .attrTween('d', function(d) {
            const interpolate = d3.interpolate(-Math.PI / 2, d.endAngle);
            return function(t) {
                d.endAngle = interpolate(t);
                return arcGenerator(d);
            };
        });
    
    // Score text
    g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.3em')
        .style('font-size', '48px')
        .style('font-weight', 'bold')
        .style('fill', D3Utils.getScoreColor(100 - score))
        .text(score);
    
    g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '2.5em')
        .style('font-size', '16px')
        .style('fill', 'var(--text-secondary)')
        .text('Risk Score');
}

/**
 * Show discovery panel with smart suggestions
 */
function showDiscoveryPanel() {
    const panel = document.getElementById('discovery-panel');
    const content = document.getElementById('discovery-content');
    
    if (!dashboardData.discoveries || dashboardData.discoveries.length === 0) return;
    
    content.innerHTML = dashboardData.discoveries
        .slice(0, 3)
        .map(discovery => `
            <div class="mb-4 p-3 border-l-4 ${discovery.type === 'critical' ? 'border-red-500' : 'border-green-500'} bg-gray-50 dark:bg-gray-700 rounded">
                <div class="font-semibold">${discovery.title}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">${discovery.description}</div>
                <div class="flex space-x-2 mt-2">
                    <span class="badge badge-${discovery.impact}">${discovery.impact} impact</span>
                    <span class="badge badge-${discovery.effort}">${discovery.effort} effort</span>
                </div>
            </div>
        `)
        .join('');
    
    panel.style.display = 'block';
}

// Close discovery panel
document.getElementById('close-discovery')?.addEventListener('click', () => {
    document.getElementById('discovery-panel').style.display = 'none';
});
