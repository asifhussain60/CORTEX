/**
 * Architecture Tab Component
 * 
 * Renders architecture view with 3D Three.js visualization and D3.js dependency graph.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Render architecture tab
 * @param {Object} data - Dashboard data containing architecture information
 */
export function renderArchitecture(data) {
    const container = document.getElementById('architecture-container');
    if (!container) {
        console.error('Architecture container not found');
        return;
    }
    
    const architecture = data.architecture || {};
    const summary = architecture.summary || {};
    const tiers = architecture.tiers || [];
    const components = architecture.components || [];
    
    // Build HTML
    container.innerHTML = `
        <div class="view-header">
            <h2>🏗️ Architecture Overview</h2>
            <div class="header-actions">
                <button class="btn-secondary" onclick="toggle3DView()">Toggle 3D/2D</button>
            </div>
        </div>

        <!-- Architecture Summary -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.5rem; padding: 1.5rem;">
                <div style="text-align: center;">
                    <h3 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Architecture Style</h3>
                    <p style="font-size: 1.5rem; font-weight: 600; color: var(--accent-primary);">
                        ${architecture.style || 'Unknown'}
                    </p>
                </div>
                <div style="text-align: center;">
                    <h3 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Components</h3>
                    <p style="font-size: 1.5rem; font-weight: 600;">
                        ${summary.total_components || 0}
                    </p>
                </div>
                <div style="text-align: center;">
                    <h3 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Total Files</h3>
                    <p style="font-size: 1.5rem; font-weight: 600;">
                        ${summary.total_files || 0}
                    </p>
                </div>
                <div style="text-align: center;">
                    <h3 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Lines of Code</h3>
                    <p style="font-size: 1.5rem; font-weight: 600;">
                        ${(summary.total_loc || 0).toLocaleString()}
                    </p>
                </div>
                <div style="text-align: center;">
                    <h3 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Architecture Score</h3>
                    <p style="font-size: 1.5rem; font-weight: 600; color: ${getScoreColor(summary.architecture_score)};">
                        ${summary.architecture_score || 0}/100
                    </p>
                </div>
            </div>
        </div>

        <!-- 3D Architecture Visualization -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h3 style="margin-bottom: 1rem;">3D Tier Architecture</h3>
            <div id="architecture-3d-container" style="width: 100%; height: 500px; background: rgba(0, 0, 0, 0.2); border-radius: 8px;"></div>
            <div style="text-align: center; margin-top: 1rem;">
                <button class="btn-secondary" onclick="resetCamera()">Reset View</button>
                <button class="btn-secondary" onclick="autoRotate()">Auto Rotate</button>
            </div>
        </div>

        <!-- Tier Breakdown -->
        <div style="margin-bottom: 2rem;">
            <h3 style="margin-bottom: 1.5rem;">📊 Tier Breakdown</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
                ${tiers.map(tier => renderTierCard(tier)).join('')}
            </div>
        </div>

        <!-- Component Dependency Graph -->
        <div class="glass-card">
            <h3 style="margin-bottom: 1rem;">🔗 Component Dependencies</h3>
            <div id="component-graph" style="width: 100%; height: 600px;"></div>
            <div style="display: flex; gap: 1.5rem; justify-content: center; margin-top: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 16px; height: 16px; background: #ec4899; border-radius: 50%;"></div>
                    <span style="font-size: 0.875rem;">Presentation</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 16px; height: 16px; background: #3b82f6; border-radius: 50%;"></div>
                    <span style="font-size: 0.875rem;">Application</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 16px; height: 16px; background: #10b981; border-radius: 50%;"></div>
                    <span style="font-size: 0.875rem;">Domain</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 16px; height: 16px; background: #f59e0b; border-radius: 50%;"></div>
                    <span style="font-size: 0.875rem;">Infrastructure</span>
                </div>
            </div>
        </div>
    `;
    
    // Initialize visualizations after DOM is updated
    setTimeout(() => {
        init3DArchitecture(tiers);
        initComponentGraph(components);
    }, 100);
}

/**
 * Render tier card
 * @param {Object} tier - Tier object
 * @returns {string} HTML string
 */
function renderTierCard(tier) {
    return `
        <div class="glass-card">
            <h4 style="margin-bottom: 1rem; color: var(--accent-primary);">
                ${(tier.name || '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </h4>
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">Files:</span>
                    <span style="font-weight: 600;">${tier.file_count || 0}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">LOC:</span>
                    <span style="font-weight: 600;">${(tier.loc || 0).toLocaleString()}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--text-secondary);">Path:</span>
                    <span style="font-size: 0.75rem; color: var(--text-secondary);">${tier.path || 'N/A'}</span>
                </div>
            </div>
            ${tier.directories && tier.directories.length > 0 ? `
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--glass-border);">
                    <strong style="font-size: 0.875rem;">Directories:</strong>
                    <ul style="margin-top: 0.5rem; padding-left: 1.5rem; font-size: 0.875rem; color: var(--text-secondary);">
                        ${tier.directories.slice(0, 5).map(dir => `<li>${dir}</li>`).join('')}
                        ${tier.directories.length > 5 ? `<li style="color: var(--accent-primary);">+${tier.directories.length - 5} more...</li>` : ''}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Get color based on score
 * @param {number} score - Architecture score (0-100)
 * @returns {string} Color value
 */
function getScoreColor(score) {
    if (score >= 80) return 'var(--success)';
    if (score >= 60) return 'var(--warning)';
    return 'var(--danger)';
}

/**
 * Initialize 3D architecture visualization with Three.js
 * @param {Array} tiers - Tier data
 */
function init3DArchitecture(tiers) {
    // Check if Three.js is available
    if (typeof THREE === 'undefined') {
        console.warn('Three.js not loaded, skipping 3D visualization');
        return;
    }
    
    const container = document.getElementById('architecture-3d-container');
    if (!container) return;
    
    // Clear any existing content
    container.innerHTML = '';
    
    const width = container.clientWidth;
    const height = 500;
    
    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e27);
    
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 15;
    camera.position.y = 5;
    
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 10);
    scene.add(directionalLight);
    
    // Create tier boxes
    const tierColors = [0x00d4ff, 0x7b61ff, 0x00ff88, 0xffa500];
    tiers.forEach((tier, index) => {
        const geometry = new THREE.BoxGeometry(6, 2, 4);
        const material = new THREE.MeshPhongMaterial({ 
            color: tierColors[index % tierColors.length],
            transparent: true,
            opacity: 0.8
        });
        const cube = new THREE.Mesh(geometry, material);
        cube.position.y = index * 3 - (tiers.length * 1.5);
        scene.add(cube);
    });
    
    // Animation loop
    let isRotating = true;
    function animate() {
        requestAnimationFrame(animate);
        if (isRotating) {
            scene.rotation.y += 0.005;
        }
        renderer.render(scene, camera);
    }
    animate();
    
    // Store controls globally for button handlers
    window.resetCamera = function() {
        camera.position.set(0, 5, 15);
        camera.lookAt(0, 0, 0);
        scene.rotation.y = 0;
    };
    
    window.autoRotate = function() {
        isRotating = !isRotating;
    };
}

/**
 * Initialize component dependency graph with D3.js
 * @param {Array} components - Component data
 */
function initComponentGraph(components) {
    // Check if D3 is available
    if (typeof d3 === 'undefined') {
        console.warn('D3.js not loaded, skipping dependency graph');
        return;
    }
    
    const container = document.getElementById('component-graph');
    if (!container) return;
    
    // Clear any existing content
    d3.select('#component-graph').selectAll('*').remove();
    
    const nodes = components.map(c => ({
        id: c.name,
        tier: c.tier,
        loc: c.loc || 100
    }));

    const links = [];
    components.forEach(comp => {
        if (comp.dependencies) {
            comp.dependencies.forEach(dep => {
                const target = nodes.find(n => n.id === dep);
                if (target) {
                    links.push({ source: comp.name, target: dep });
                }
            });
        }
    });

    const width = container.clientWidth;
    const height = 600;

    const colorMap = {
        'presentation': '#ec4899',
        'application': '#3b82f6',
        'domain': '#10b981',
        'infrastructure': '#f59e0b',
        'api': '#8b5cf6',
        'other': '#6b7280'
    };

    const svg = d3.select('#component-graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .enter()
        .append('line')
        .attr('stroke', '#475569')
        .attr('stroke-width', 2)
        .attr('opacity', 0.6);

    const node = svg.append('g')
        .selectAll('circle')
        .data(nodes)
        .enter()
        .append('circle')
        .attr('r', d => Math.sqrt(d.loc) / 5 + 10)
        .attr('fill', d => colorMap[d.tier] || colorMap.other)
        .style('cursor', 'pointer')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    const label = svg.append('g')
        .selectAll('text')
        .data(nodes)
        .enter()
        .append('text')
        .text(d => d.id)
        .attr('font-size', '12px')
        .attr('fill', '#e2e8f0')
        .attr('text-anchor', 'middle')
        .attr('dy', '.35em');

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

/**
 * Toggle 3D view (placeholder)
 */
window.toggle3DView = function() {
    console.log('Toggle 3D/2D view');
    alert('3D/2D toggle functionality coming soon!');
};
