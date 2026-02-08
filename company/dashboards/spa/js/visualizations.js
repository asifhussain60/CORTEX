/**
 * CORTEX Dashboard D3.js Visualizations
 * Rich interactive diagrams for repository code visualization
 * 
 * Version: 2.0.0
 * Dependencies: D3.js v7
 * Last Updated: 2026-02-08
 */

// ============================================================================
// COLOR PALETTES
// ============================================================================

const COLORS = {
    primary: '#00d4ff',
    secondary: '#7b61ff',
    tertiary: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    text: {
        primary: '#ffffff',
        secondary: '#a0a6c0',
        muted: '#6b7280'
    },
    languages: {
        JavaScript: '#f7df1e',
        TypeScript: '#3178c6',
        Python: '#3572A5',
        'C#': '#178600',
        HTML: '#e34c26',
        CSS: '#563d7c',
        SQL: '#e38c00',
        PHP: '#777BB4',
        Config: '#6b7280'
    },
    categories: {
        core: '#7b61ff',
        domain: '#00d4ff',
        support: '#10b981',
        dev: '#f59e0b'
    }
};

// ============================================================================
// LANGUAGE DISTRIBUTION SUNBURST
// ============================================================================

/**
 * Create an interactive sunburst chart for language distribution
 * @param {string} containerId - DOM element ID
 * @param {Object} languages - Language data { name: lines }
 */
function createLanguageSunburst(containerId, languages) {
    const container = document.getElementById(containerId);
    if (!container || !languages) return;
    
    container.innerHTML = '';
    
    const width = container.clientWidth || 400;
    const height = 400;
    const radius = Math.min(width, height) / 2;
    
    // Transform data for hierarchy
    const data = {
        name: 'Languages',
        children: Object.entries(languages).map(([name, value]) => ({
            name,
            value,
            color: COLORS.languages[name] || COLORS.categories.support
        }))
    };
    
    // Sort by value descending
    data.children.sort((a, b) => b.value - a.value);
    
    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');
    
    const g = svg.append('g')
        .attr('transform', `translate(${width / 2}, ${height / 2})`);
    
    // Create partition layout
    const partition = d3.partition()
        .size([2 * Math.PI, radius]);
    
    const root = d3.hierarchy(data)
        .sum(d => d.value)
        .sort((a, b) => b.value - a.value);
    
    partition(root);
    
    // Arc generator
    const arc = d3.arc()
        .startAngle(d => d.x0)
        .endAngle(d => d.x1)
        .innerRadius(d => d.y0 * 0.6)
        .outerRadius(d => d.y1 - 2)
        .padAngle(0.02)
        .padRadius(radius / 2);
    
    // Tooltip
    const tooltip = d3.select('body').append('div')
        .attr('class', 'viz-tooltip')
        .style('position', 'absolute')
        .style('visibility', 'hidden')
        .style('background', 'rgba(26, 31, 58, 0.95)')
        .style('border', '1px solid rgba(0, 212, 255, 0.3)')
        .style('border-radius', '8px')
        .style('padding', '12px 16px')
        .style('color', '#fff')
        .style('font-size', '14px')
        .style('z-index', '10000')
        .style('pointer-events', 'none')
        .style('backdrop-filter', 'blur(10px)');
    
    // Draw arcs
    const path = g.selectAll('path')
        .data(root.descendants().filter(d => d.depth))
        .join('path')
        .attr('fill', d => d.data.color || COLORS.primary)
        .attr('d', arc)
        .style('cursor', 'pointer')
        .style('transition', 'all 0.3s ease')
        .on('mouseover', function(event, d) {
            d3.select(this)
                .style('filter', 'brightness(1.3)')
                .style('transform', 'scale(1.02)');
            
            const total = root.value;
            const percentage = ((d.value / total) * 100).toFixed(1);
            
            tooltip
                .style('visibility', 'visible')
                .html(`
                    <div style="font-weight: 600; color: ${d.data.color}; margin-bottom: 4px;">
                        ${d.data.name}
                    </div>
                    <div style="color: #a0a6c0;">
                        ${d.value.toLocaleString()} lines (${percentage}%)
                    </div>
                `);
        })
        .on('mousemove', function(event) {
            tooltip
                .style('top', (event.pageY - 10) + 'px')
                .style('left', (event.pageX + 10) + 'px');
        })
        .on('mouseout', function() {
            d3.select(this)
                .style('filter', 'brightness(1)')
                .style('transform', 'scale(1)');
            tooltip.style('visibility', 'hidden');
        });
    
    // Center text
    g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '-0.5em')
        .style('fill', COLORS.text.primary)
        .style('font-size', '24px')
        .style('font-weight', '700')
        .text(root.value.toLocaleString());
    
    g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '1.2em')
        .style('fill', COLORS.text.secondary)
        .style('font-size', '12px')
        .style('text-transform', 'uppercase')
        .style('letter-spacing', '0.1em')
        .text('Total Lines');
}

// ============================================================================
// DEPENDENCY FORCE GRAPH
// ============================================================================

/**
 * Create an interactive force-directed dependency graph
 * @param {string} containerId - DOM element ID
 * @param {Array} packages - Package data array
 */
function createDependencyGraph(containerId, packages) {
    const container = document.getElementById(containerId);
    if (!container || !packages || packages.length === 0) return;
    
    container.innerHTML = '';
    
    const width = container.clientWidth || 800;
    const height = 500;
    
    // Take top 50 packages for visualization
    const topPackages = packages.slice(0, 50);
    
    // Create nodes and links
    const nodes = topPackages.map((pkg, i) => ({
        id: pkg.name,
        version: pkg.version,
        isDirect: pkg.is_direct,
        group: pkg.is_direct ? 'direct' : 'transitive',
        radius: pkg.is_direct ? 12 : 6
    }));
    
    // Create some interconnections based on common prefixes
    const links = [];
    const prefixGroups = {};
    
    nodes.forEach(node => {
        const prefix = node.id.split('/')[0].split('-')[0];
        if (!prefixGroups[prefix]) prefixGroups[prefix] = [];
        prefixGroups[prefix].push(node.id);
    });
    
    Object.values(prefixGroups).forEach(group => {
        if (group.length > 1) {
            for (let i = 1; i < Math.min(group.length, 4); i++) {
                links.push({
                    source: group[0],
                    target: group[i],
                    value: 1
                });
            }
        }
    });
    
    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');
    
    // Gradient definitions
    const defs = svg.append('defs');
    
    const gradient = defs.append('radialGradient')
        .attr('id', 'nodeGlow');
    gradient.append('stop').attr('offset', '0%').attr('stop-color', COLORS.primary).attr('stop-opacity', 0.8);
    gradient.append('stop').attr('offset', '100%').attr('stop-color', COLORS.primary).attr('stop-opacity', 0);
    
    // Simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(80))
        .force('charge', d3.forceManyBody().strength(-100))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => d.radius + 10));
    
    // Links
    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', 'rgba(0, 212, 255, 0.2)')
        .attr('stroke-width', 1);
    
    // Tooltip
    const tooltip = d3.select('body').append('div')
        .attr('class', 'viz-tooltip-dep')
        .style('position', 'absolute')
        .style('visibility', 'hidden')
        .style('background', 'rgba(26, 31, 58, 0.95)')
        .style('border', '1px solid rgba(0, 212, 255, 0.3)')
        .style('border-radius', '8px')
        .style('padding', '12px 16px')
        .style('color', '#fff')
        .style('font-size', '13px')
        .style('z-index', '10000')
        .style('pointer-events', 'none')
        .style('backdrop-filter', 'blur(10px)');
    
    // Nodes
    const node = svg.append('g')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .style('cursor', 'pointer')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Node circles
    node.append('circle')
        .attr('r', d => d.radius)
        .attr('fill', d => d.isDirect ? COLORS.primary : COLORS.secondary)
        .attr('stroke', d => d.isDirect ? COLORS.primary : 'transparent')
        .attr('stroke-width', 2)
        .attr('opacity', d => d.isDirect ? 1 : 0.6)
        .on('mouseover', function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', d.radius * 1.5)
                .attr('filter', 'drop-shadow(0 0 10px rgba(0, 212, 255, 0.5))');
            
            tooltip
                .style('visibility', 'visible')
                .html(`
                    <div style="font-weight: 600; color: ${d.isDirect ? COLORS.primary : COLORS.secondary}; margin-bottom: 4px;">
                        ${d.id}
                    </div>
                    <div style="color: #a0a6c0; font-family: monospace;">
                        v${d.version || 'unknown'}
                    </div>
                    <div style="margin-top: 4px; font-size: 11px; color: #6b7280;">
                        ${d.isDirect ? '📦 Direct Dependency' : '🔗 Transitive'}
                    </div>
                `);
        })
        .on('mousemove', function(event) {
            tooltip
                .style('top', (event.pageY - 10) + 'px')
                .style('left', (event.pageX + 10) + 'px');
        })
        .on('mouseout', function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', d.radius)
                .attr('filter', 'none');
            tooltip.style('visibility', 'hidden');
        });
    
    // Simulation tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node.attr('transform', d => {
            d.x = Math.max(20, Math.min(width - 20, d.x));
            d.y = Math.max(20, Math.min(height - 20, d.y));
            return `translate(${d.x}, ${d.y})`;
        });
    });
    
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
}

// ============================================================================
// HEALTH SCORE GAUGE
// ============================================================================

/**
 * Create an animated health score gauge
 * @param {string} containerId - DOM element ID
 * @param {number} score - Health score 0-100
 */
function createHealthGauge(containerId, score) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    const width = container.clientWidth || 250;
    const height = 200;
    const radius = Math.min(width, height * 2) / 2 - 20;
    
    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');
    
    const g = svg.append('g')
        .attr('transform', `translate(${width / 2}, ${height - 20})`);
    
    // Background arc
    const backgroundArc = d3.arc()
        .innerRadius(radius - 20)
        .outerRadius(radius)
        .startAngle(-Math.PI / 2)
        .endAngle(Math.PI / 2)
        .cornerRadius(10);
    
    g.append('path')
        .attr('d', backgroundArc)
        .attr('fill', 'rgba(255, 255, 255, 0.1)');
    
    // Score color
    const getScoreColor = (s) => {
        if (s >= 80) return COLORS.tertiary;
        if (s >= 60) return COLORS.warning;
        if (s >= 40) return '#f97316';
        return COLORS.danger;
    };
    
    // Gradient
    const gradientId = `gauge-gradient-${containerId}`;
    const defs = svg.append('defs');
    const gradient = defs.append('linearGradient')
        .attr('id', gradientId)
        .attr('x1', '0%').attr('y1', '0%')
        .attr('x2', '100%').attr('y2', '0%');
    
    gradient.append('stop').attr('offset', '0%').attr('stop-color', COLORS.danger);
    gradient.append('stop').attr('offset', '50%').attr('stop-color', COLORS.warning);
    gradient.append('stop').attr('offset', '100%').attr('stop-color', COLORS.tertiary);
    
    // Score arc
    const scoreArc = d3.arc()
        .innerRadius(radius - 20)
        .outerRadius(radius)
        .startAngle(-Math.PI / 2)
        .cornerRadius(10);
    
    const scorePath = g.append('path')
        .attr('fill', `url(#${gradientId})`)
        .attr('filter', 'drop-shadow(0 0 10px rgba(0, 212, 255, 0.3))');
    
    // Animate
    scorePath.transition()
        .duration(1500)
        .ease(d3.easeElasticOut)
        .attrTween('d', function() {
            const interpolate = d3.interpolate(-Math.PI / 2, -Math.PI / 2 + (Math.PI * score / 100));
            return function(t) {
                return scoreArc.endAngle(interpolate(t))();
            };
        });
    
    // Score text
    const scoreText = g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '-30px')
        .style('fill', getScoreColor(score))
        .style('font-size', '48px')
        .style('font-weight', '800')
        .text('0');
    
    scoreText.transition()
        .duration(1500)
        .tween('text', function() {
            const i = d3.interpolateNumber(0, score);
            return function(t) {
                this.textContent = Math.round(i(t));
            };
        });
    
    // Label
    g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '5px')
        .style('fill', COLORS.text.secondary)
        .style('font-size', '14px')
        .style('text-transform', 'uppercase')
        .style('letter-spacing', '0.1em')
        .text('Health Score');
}

// ============================================================================
// SECURITY FINDINGS DONUT
// ============================================================================

/**
 * Create a security findings donut chart
 * @param {string} containerId - DOM element ID
 * @param {Object} security - Security data
 */
function createSecurityDonut(containerId, security) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    const width = container.clientWidth || 300;
    const height = 300;
    const radius = Math.min(width, height) / 2 - 20;
    
    const data = [
        { label: 'Critical', value: security.critical_count || 0, color: '#ef4444' },
        { label: 'High', value: security.high_count || 0, color: '#f97316' },
        { label: 'Medium', value: security.medium_count || 0, color: '#f59e0b' },
        { label: 'Low', value: security.low_count || 0, color: '#10b981' }
    ].filter(d => d.value > 0);
    
    // If no vulnerabilities, show success state
    if (data.length === 0) {
        const svg = d3.select(`#${containerId}`)
            .append('svg')
            .attr('viewBox', `0 0 ${width} ${height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
        
        const g = svg.append('g')
            .attr('transform', `translate(${width / 2}, ${height / 2})`);
        
        g.append('circle')
            .attr('r', radius)
            .attr('fill', 'rgba(16, 185, 129, 0.1)')
            .attr('stroke', COLORS.tertiary)
            .attr('stroke-width', 3);
        
        g.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '-10px')
            .style('fill', COLORS.tertiary)
            .style('font-size', '48px')
            .text('✓');
        
        g.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '30px')
            .style('fill', COLORS.text.secondary)
            .style('font-size', '14px')
            .text('No Vulnerabilities');
        
        return;
    }
    
    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');
    
    const g = svg.append('g')
        .attr('transform', `translate(${width / 2}, ${height / 2})`);
    
    const pie = d3.pie()
        .value(d => d.value)
        .sort(null)
        .padAngle(0.03);
    
    const arc = d3.arc()
        .innerRadius(radius * 0.6)
        .outerRadius(radius)
        .cornerRadius(4);
    
    const hoverArc = d3.arc()
        .innerRadius(radius * 0.6)
        .outerRadius(radius + 10)
        .cornerRadius(4);
    
    // Tooltip
    const tooltip = d3.select('body').append('div')
        .attr('class', 'viz-tooltip-sec')
        .style('position', 'absolute')
        .style('visibility', 'hidden')
        .style('background', 'rgba(26, 31, 58, 0.95)')
        .style('border', '1px solid rgba(255, 255, 255, 0.1)')
        .style('border-radius', '8px')
        .style('padding', '12px 16px')
        .style('color', '#fff')
        .style('font-size', '13px')
        .style('z-index', '10000')
        .style('backdrop-filter', 'blur(10px)');
    
    // Arcs
    const arcs = g.selectAll('.arc')
        .data(pie(data))
        .join('g')
        .attr('class', 'arc');
    
    arcs.append('path')
        .attr('d', arc)
        .attr('fill', d => d.data.color)
        .style('cursor', 'pointer')
        .style('transition', 'all 0.3s ease')
        .on('mouseover', function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('d', hoverArc)
                .attr('filter', `drop-shadow(0 0 10px ${d.data.color})`);
            
            tooltip
                .style('visibility', 'visible')
                .html(`
                    <div style="font-weight: 600; color: ${d.data.color};">
                        ${d.data.label}
                    </div>
                    <div style="font-size: 24px; font-weight: 700; margin: 4px 0;">
                        ${d.data.value}
                    </div>
                    <div style="color: #6b7280; font-size: 11px;">
                        vulnerabilities
                    </div>
                `);
        })
        .on('mousemove', function(event) {
            tooltip
                .style('top', (event.pageY - 10) + 'px')
                .style('left', (event.pageX + 10) + 'px');
        })
        .on('mouseout', function() {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('d', arc)
                .attr('filter', 'none');
            tooltip.style('visibility', 'hidden');
        });
    
    // Center text
    const total = d3.sum(data, d => d.value);
    g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '-5px')
        .style('fill', COLORS.text.primary)
        .style('font-size', '36px')
        .style('font-weight', '800')
        .text(total);
    
    g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '20px')
        .style('fill', COLORS.text.secondary)
        .style('font-size', '12px')
        .text('Total Issues');
}

// ============================================================================
// FILE TREE VISUALIZATION
// ============================================================================

/**
 * Create an interactive file tree visualization
 * @param {string} containerId - DOM element ID  
 * @param {Object} metrics - Repository metrics with languages
 */
function createFileTree(containerId, metrics) {
    const container = document.getElementById(containerId);
    if (!container || !metrics?.languages) return;
    
    container.innerHTML = '';
    
    const width = container.clientWidth || 600;
    const height = 400;
    
    // Build tree structure from languages
    const data = {
        name: 'Repository',
        children: Object.entries(metrics.languages).map(([lang, lines]) => ({
            name: lang,
            value: lines,
            children: generateFakeFiles(lang, lines)
        }))
    };
    
    function generateFakeFiles(lang, totalLines) {
        const extensions = {
            JavaScript: '.js',
            TypeScript: '.ts',
            Python: '.py',
            'C#': '.cs',
            HTML: '.html',
            CSS: '.css',
            SQL: '.sql',
            Config: '.json'
        };
        
        const ext = extensions[lang] || '.txt';
        const numFiles = Math.min(Math.ceil(totalLines / 100), 8);
        const files = [];
        let remaining = totalLines;
        
        for (let i = 0; i < numFiles; i++) {
            const value = i === numFiles - 1 ? remaining : Math.floor(remaining / (numFiles - i) * Math.random() * 1.5);
            remaining -= value;
            files.push({
                name: `${lang.toLowerCase()}-${i + 1}${ext}`,
                value: Math.max(value, 10)
            });
        }
        
        return files;
    }
    
    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');
    
    const treemap = d3.treemap()
        .size([width, height])
        .paddingTop(20)
        .paddingRight(4)
        .paddingInner(2)
        .round(true);
    
    const root = d3.hierarchy(data)
        .sum(d => d.value)
        .sort((a, b) => b.value - a.value);
    
    treemap(root);
    
    // Tooltip
    const tooltip = d3.select('body').append('div')
        .attr('class', 'viz-tooltip-tree')
        .style('position', 'absolute')
        .style('visibility', 'hidden')
        .style('background', 'rgba(26, 31, 58, 0.95)')
        .style('border', '1px solid rgba(0, 212, 255, 0.3)')
        .style('border-radius', '8px')
        .style('padding', '12px 16px')
        .style('color', '#fff')
        .style('font-size', '13px')
        .style('z-index', '10000')
        .style('backdrop-filter', 'blur(10px)');
    
    // Cells
    const cell = svg.selectAll('g')
        .data(root.leaves())
        .join('g')
        .attr('transform', d => `translate(${d.x0}, ${d.y0})`);
    
    cell.append('rect')
        .attr('width', d => d.x1 - d.x0)
        .attr('height', d => d.y1 - d.y0)
        .attr('fill', d => COLORS.languages[d.parent.data.name] || COLORS.secondary)
        .attr('opacity', 0.7)
        .attr('rx', 4)
        .style('cursor', 'pointer')
        .style('transition', 'all 0.2s ease')
        .on('mouseover', function(event, d) {
            d3.select(this)
                .attr('opacity', 1)
                .attr('stroke', '#fff')
                .attr('stroke-width', 2);
            
            tooltip
                .style('visibility', 'visible')
                .html(`
                    <div style="font-weight: 600; color: ${COLORS.languages[d.parent.data.name] || COLORS.primary};">
                        ${d.data.name}
                    </div>
                    <div style="color: #a0a6c0; margin-top: 4px;">
                        ${d.data.value.toLocaleString()} lines
                    </div>
                    <div style="color: #6b7280; font-size: 11px; margin-top: 2px;">
                        ${d.parent.data.name}
                    </div>
                `);
        })
        .on('mousemove', function(event) {
            tooltip
                .style('top', (event.pageY - 10) + 'px')
                .style('left', (event.pageX + 10) + 'px');
        })
        .on('mouseout', function() {
            d3.select(this)
                .attr('opacity', 0.7)
                .attr('stroke', 'none');
            tooltip.style('visibility', 'hidden');
        });
    
    // Labels for larger cells
    cell.filter(d => (d.x1 - d.x0) > 50 && (d.y1 - d.y0) > 25)
        .append('text')
        .attr('x', 6)
        .attr('y', 16)
        .style('fill', '#fff')
        .style('font-size', '11px')
        .style('font-weight', '500')
        .style('pointer-events', 'none')
        .text(d => d.data.name.length > 12 ? d.data.name.slice(0, 10) + '...' : d.data.name);
    
    // Category headers
    const categories = svg.selectAll('.category-label')
        .data(root.children)
        .join('text')
        .attr('class', 'category-label')
        .attr('x', d => d.x0 + 6)
        .attr('y', d => d.y0 + 14)
        .style('fill', COLORS.text.primary)
        .style('font-size', '12px')
        .style('font-weight', '700')
        .style('pointer-events', 'none')
        .text(d => d.data.name);
}

// ============================================================================
// EXPORT FUNCTIONS
// ============================================================================

window.CortexViz = {
    createLanguageSunburst,
    createDependencyGraph,
    createHealthGauge,
    createSecurityDonut,
    createFileTree,
    COLORS
};
