/**
 * Architecture Tab Component
 * 
 * Renders architecture view with 3D Three.js visualization and D3.js dependency graph.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showPanelSpinner } from '../shared-utils.js';

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
    
    // Show loading spinner
    showPanelSpinner(container, 'Loading architecture visualization...');
    
    // Render after brief delay to show spinner
    setTimeout(() => {
        const architecture = data.architecture || {};
        const summary = architecture.summary || {};
        const tiers = architecture.tiers || [];
        const components = architecture.components || [];
        const appType = architecture.application_type || {};
        const style = architecture.style || {};
        const endpoints = architecture.endpoints || [];
        const deployment = architecture.deployment || {};
        const metrics = architecture.metrics || {};
        
        // Build HTML
        container.innerHTML = `
        <div class="view-header">
            <h2>🏗️ Architecture Overview</h2>
        </div>

        <!-- Application Type & Style -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; padding: 1.5rem;">
                <div>
                    <h3 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Application Type</h3>
                    <p style="font-size: 1.25rem; font-weight: 600; color: var(--accent-primary); margin-bottom: 0.5rem;">
                        ${appType.type || 'Unknown'}
                    </p>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">
                        Confidence: <span style="color: ${appType.confidence >= 70 ? '#10b981' : '#f59e0b'}; font-weight: 600;">${appType.confidence || 0}%</span>
                    </div>
                    ${appType.evidence && appType.evidence.length > 0 ? `
                        <ul style="margin-top: 0.75rem; font-size: 0.75rem; color: var(--text-secondary); padding-left: 1.25rem;">
                            ${appType.evidence.slice(0, 3).map(ev => `<li>${ev}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
                <div>
                    <h3 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Architecture Style</h3>
                    <p style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">
                        ${style.name || 'Unknown'}
                    </p>
                    <p style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
                        ${style.description || ''}
                    </p>
                    ${style.characteristics && style.characteristics.length > 0 ? `
                        <ul style="font-size: 0.75rem; color: var(--text-secondary); padding-left: 1.25rem;">
                            ${style.characteristics.slice(0, 3).map(ch => `<li>${ch}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
                <div>
                    <h3 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Deployment</h3>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="font-size: 0.75rem; color: var(--text-secondary);">Hosting:</span>
                        <span style="font-size: 0.875rem; font-weight: 600; display: block;">${deployment.hosting || 'Unknown'}</span>
                    </div>
                    <div>
                        <span style="font-size: 0.75rem; color: var(--text-secondary);">Platform:</span>
                        <span style="font-size: 0.875rem; font-weight: 600; display: block;">${deployment.platform || 'Unknown'}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Metrics Dashboard -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h3 style="margin-bottom: 1rem;">📊 Architecture Metrics</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
                <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.02); border-radius: 8px;">
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Overall Score</div>
                    <div style="font-size: 2rem; font-weight: 600; color: ${getScoreColor(metrics.overall_score || 0)};">
                        ${metrics.overall_score || 0}
                    </div>
                </div>
                <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.02); border-radius: 8px;">
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Layer Separation</div>
                    <div style="font-size: 2rem; font-weight: 600; color: ${getScoreColor(metrics.layer_separation || 0)};">
                        ${metrics.layer_separation || 0}
                    </div>
                </div>
                <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.02); border-radius: 8px;">
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Modularity</div>
                    <div style="font-size: 2rem; font-weight: 600; color: ${getScoreColor(metrics.modularity || 0)};">
                        ${metrics.modularity || 0}
                    </div>
                </div>
                <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.02); border-radius: 8px;">
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">API Design</div>
                    <div style="font-size: 2rem; font-weight: 600; color: ${getScoreColor(metrics.api_design || 0)};">
                        ${metrics.api_design || 0}
                    </div>
                </div>
                <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.02); border-radius: 8px;">
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Tier Balance</div>
                    <div style="font-size: 2rem; font-weight: 600; color: ${getScoreColor(metrics.tier_balance || 0)};">
                        ${metrics.tier_balance || 0}
                    </div>
                </div>
            </div>
        </div>

        <!-- API Endpoints -->
        ${endpoints.length > 0 ? `
            <div class="glass-card" style="margin-bottom: 2rem;">
                <h3 style="margin-bottom: 1rem;">🔌 API Endpoints (${endpoints.length})</h3>
                <div style="max-height: 400px; overflow-y: auto;">
                    ${endpoints.map(ep => renderEndpointCard(ep)).join('')}
                </div>
            </div>
        ` : ''}

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
    }, 250);
}

/**
 * Render tier card
 * @param {Object} tier - Tier object
 * @returns {string} HTML string
 */
function renderTierCard(tier) {
    const locPercentage = tier.loc_percentage || 0;
    return `
        <div class="glass-card" style="transition: transform 0.2s; position: relative;" onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">
            <h4 style="margin-bottom: 0.75rem; color: var(--accent-primary); font-size: 1.1rem;">
                ${tier.name || 'Unknown Tier'}
            </h4>
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary); font-size: 0.875rem;">Files:</span>
                    <span style="font-weight: 600;">${tier.file_count || 0}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary); font-size: 0.875rem;">LOC:</span>
                    <span style="font-weight: 600;">${(tier.loc || 0).toLocaleString()}</span>
                </div>
            </div>
            ${tier.technologies && tier.technologies.length > 0 ? `
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Technologies:</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${tier.technologies.map(tech => `
                            <span style="
                                background: rgba(0, 212, 255, 0.1);
                                color: var(--accent-primary);
                                padding: 0.25rem 0.75rem;
                                border-radius: 12px;
                                font-size: 0.75rem;
                                font-weight: 500;
                            ">${tech}</span>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            ${tier.key_files && tier.key_files.length > 0 ? `
                <div style="padding-top: 1rem; border-top: 1px solid var(--glass-border);">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Key Files:</div>
                    <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.75rem; color: var(--text-secondary);">
                        ${tier.key_files.slice(0, 5).map(file => `<li style="margin: 0.25rem 0;">${file}</li>`).join('')}
                        ${tier.key_files.length > 5 ? `<li style="color: var(--accent-primary); margin: 0.25rem 0;">+${tier.key_files.length - 5} more...</li>` : ''}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Render endpoint card
 * @param {Object} endpoint - Endpoint object
 * @returns {string} HTML string
 */
function renderEndpointCard(endpoint) {
    const typeColors = {
        "ASMX Web Service": "#ec4899",
        "WCF Service": "#8b5cf6",
        "REST API": "#10b981"
    };
    const color = typeColors[endpoint.type] || "#6b7280";
    
    return `
        <div style="
            padding: 1rem;
            margin-bottom: 0.75rem;
            background: rgba(255, 255, 255, 0.02);
            border-left: 3px solid ${color};
            border-radius: 6px;
            transition: transform 0.2s, background 0.2s;
        " onmouseover="this.style.background='rgba(255, 255, 255, 0.04)'; this.style.transform='translateX(4px)'" onmouseout="this.style.background='rgba(255, 255, 255, 0.02)'; this.style.transform='translateX(0)'">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem;">
                        ${endpoint.method || endpoint.service || 'Unknown'}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">
                        📁 ${endpoint.file}
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="
                        background: ${color}22;
                        color: ${color};
                        padding: 0.25rem 0.75rem;
                        border-radius: 12px;
                        font-size: 0.75rem;
                        font-weight: 600;
                        display: inline-block;
                        margin-bottom: 0.25rem;
                    ">${endpoint.type}</span>
                    ${endpoint.http_method ? `
                        <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                            ${endpoint.http_method}
                        </div>
                    ` : ''}
                </div>
            </div>
            ${endpoint.protocol ? `
                <div style="font-size: 0.75rem; color: var(--text-secondary);">
                    Protocol: <span style="color: var(--accent-primary);">${endpoint.protocol}</span>
                    ${endpoint.url ? ` | URL: <code style="background: rgba(0,0,0,0.3); padding: 0.125rem 0.5rem; border-radius: 4px;">${endpoint.url}</code>` : ''}
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
