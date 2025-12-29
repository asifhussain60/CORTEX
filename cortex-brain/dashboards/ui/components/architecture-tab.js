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
import { BaseTabComponent } from '../core/BaseTabComponent.js';

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
        // Handle both nested (data.architecture) and direct structure
        const architecture = data.architecture || data;
        const summary = architecture.summary || {};
        const tiers = architecture.tiers || [];
        const components = architecture.components || [];
        const appType = architecture.application_type || {};
        const style = architecture.style || {};
        const endpoints = architecture.endpoints || [];
        const deployment = architecture.deployment || {};
        const metrics = architecture.metrics || {};
        
        // Determine if full-stack (has multiple layers/tiers)
        const isFullStack = tiers.length >= 3 || (appType.type && appType.type.toLowerCase().includes('full'));
        
        // Build HTML
        container.innerHTML = `
        <!-- Application Overview - Compact Header -->
        <div style="
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 1rem; 
            margin-bottom: 1.5rem;
        ">
            <div class="glass-card" style="padding: 1.25rem; text-align: center;">
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    Application Type
                </div>
                <div style="font-size: 1.75rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 0.25rem;">
                    ${appType.type || 'Unknown'}
                </div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">
                    ${appType.confidence || 0}% confidence
                </div>
            </div>
            <div class="glass-card" style="padding: 1.25rem; text-align: center;">
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    Architecture Style
                </div>
                <div style="font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">
                    ${style.name || 'Unknown'}
                </div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">
                    ${style.description || 'Pattern-based design'}
                </div>
            </div>
            <div class="glass-card" style="padding: 1.25rem; text-align: center;">
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    Deployment
                </div>
                <div style="font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">
                    ${deployment.platform || 'Unknown'}
                </div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">
                    ${deployment.hosting || 'Standard hosting'}
                </div>
            </div>
        </div>

        <!-- Architecture Quality Metrics -->
        <div class="glass-card" style="margin-bottom: 1.5rem; padding: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700;">📊 Quality Metrics</h3>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">
                    Hover for details
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem;">
                ${renderArchitectureMetricCard('Overall', metrics.overall_score || 0, metrics.overall_explanation || 'Weighted average of all architecture quality metrics.')}
                ${renderArchitectureMetricCard('Separation', metrics.layer_separation || 0, metrics.layer_separation_explanation || 'Measures how well tiers are separated with clear boundaries.')}
                ${renderArchitectureMetricCard('Modularity', metrics.modularity || 0, metrics.modularity_explanation || 'Evaluates component independence and reusability.')}
                ${renderArchitectureMetricCard('API Design', metrics.api_design || 0, metrics.api_design_explanation || 'Assesses endpoint consistency and RESTful principles.')}
                ${renderArchitectureMetricCard('Balance', metrics.tier_balance || 0, metrics.tier_balance_explanation || 'Checks if code is evenly distributed across tiers.')}
            </div>
        </div>

        ${isFullStack ? `
        <!-- 3D Visualization & Component Graph - Side by Side -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
            <!-- 3D Tier Visualization -->
            <div class="glass-card" style="padding: 1.25rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <h3 style="margin: 0; font-size: 1rem; font-weight: 700;">🎯 3D Tier Architecture</h3>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn-secondary" onclick="resetCamera()" style="padding: 0.375rem 0.75rem; font-size: 0.75rem;">🔄</button>
                        <button class="btn-secondary" onclick="autoRotate()" style="padding: 0.375rem 0.75rem; font-size: 0.75rem;">🔁</button>
                    </div>
                </div>
                <div id="architecture-3d-container" style="width: 100%; height: 350px; background: rgba(0, 0, 0, 0.2); border-radius: 6px; position: relative;">
                    <div id="tier-labels-overlay" style="
                        position: absolute;
                        left: 12px;
                        top: 50%;
                        transform: translateY(-50%);
                        pointer-events: none;
                        z-index: 10;
                    "></div>
                </div>
                <div style="font-size: 0.7rem; color: var(--text-secondary); text-align: center; margin-top: 0.5rem;">
                    Drag to rotate • Scroll to zoom
                </div>
            </div>

            <!-- Component Dependencies -->
            <div class="glass-card" style="padding: 1.25rem;">
                <h3 style="margin: 0 0 0.75rem 0; font-size: 1rem; font-weight: 700;">🔗 Component Dependencies</h3>
                <div id="component-graph" style="width: 100%; height: 350px; border-radius: 6px; background: rgba(0, 0, 0, 0.1);"></div>
                <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 0.5rem; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 0.375rem;">
                        <div style="width: 10px; height: 10px; background: #ec4899; border-radius: 50%;"></div>
                        <span style="font-size: 0.7rem;">Presentation</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.375rem;">
                        <div style="width: 10px; height: 10px; background: #3b82f6; border-radius: 50%;"></div>
                        <span style="font-size: 0.7rem;">Application</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.375rem;">
                        <div style="width: 10px; height: 10px; background: #10b981; border-radius: 50%;"></div>
                        <span style="font-size: 0.7rem;">Domain</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.375rem;">
                        <div style="width: 10px; height: 10px; background: #f59e0b; border-radius: 50%;"></div>
                        <span style="font-size: 0.7rem;">Infrastructure</span>
                    </div>
                </div>
            </div>
        </div>
        ` : ''}

        <!-- Tier Breakdown & API Endpoints - Combined -->
        <div style="display: grid; grid-template-columns: ${endpoints.length > 0 ? '2fr 1fr' : '1fr'}; gap: 1.5rem;">
            <!-- Tier Breakdown -->
            <div>
                <h3 style="margin: 0 0 1rem 0; font-size: 1.25rem; font-weight: 700;">📊 Tier Breakdown</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
                    ${tiers.map(tier => renderTierCard(tier)).join('')}
                </div>
            </div>

            ${endpoints.length > 0 ? `
            <!-- API Endpoints -->
            <div class="glass-card" style="padding: 1.25rem;">
                <h3 style="margin: 0 0 0.75rem 0; font-size: 1rem; font-weight: 700;">🔌 API Endpoints</h3>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
                    ${endpoints.length} total endpoints
                </div>
                <div style="max-height: 400px; overflow-y: auto; padding-right: 0.5rem;">
                    ${endpoints.map(ep => renderEndpointCard(ep)).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;
        
        // Initialize visualizations after DOM is updated (only for full-stack apps)
        if (isFullStack) {
            setTimeout(() => {
                init3DArchitecture(tiers);
                initComponentGraph(components);
            }, 100);
        }
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
        <div class="glass-card" style="
            padding: 1rem; 
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        " 
        onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.3)'" 
        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                <h4 style="margin: 0; color: var(--accent-primary); font-size: 1rem; font-weight: 700;">
                    ${tier.name || 'Unknown'}
                </h4>
                <div style="
                    background: var(--accent-primary)20;
                    color: var(--accent-primary);
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.7rem;
                    font-weight: 600;
                ">${tier.file_count || 0} files</div>
            </div>
            <div style="font-size: 1.5rem; font-weight: 800; font-family: 'SF Mono', monospace; margin-bottom: 0.75rem;">
                ${(tier.loc || 0).toLocaleString()} <span style="font-size: 0.75rem; font-weight: 500; color: var(--text-secondary);">LOC</span>
            </div>
            ${tier.technologies && tier.technologies.length > 0 ? `
                <div style="display: flex; flex-wrap: wrap; gap: 0.375rem; margin-bottom: 0.75rem;">
                    ${tier.technologies.slice(0, 4).map(tech => `
                        <span style="
                            background: rgba(0, 212, 255, 0.1);
                            color: var(--accent-primary);
                            padding: 0.25rem 0.5rem;
                            border-radius: 10px;
                            font-size: 0.7rem;
                            font-weight: 500;
                        ">${tech}</span>
                    `).join('')}
                    ${tier.technologies.length > 4 ? `<span style="font-size: 0.7rem; color: var(--text-secondary);">+${tier.technologies.length - 4}</span>` : ''}
                </div>
            ` : ''}
            ${tier.key_files && tier.key_files.length > 0 ? `
                <div style="padding-top: 0.75rem; border-top: 1px solid var(--glass-border);">
                    <div style="font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 0.375rem;">Key Files:</div>
                    <ul style="margin: 0; padding-left: 1rem; font-size: 0.7rem; color: var(--text-secondary); line-height: 1.4;">
                        ${tier.key_files.slice(0, 3).map(file => `<li style="margin: 0.125rem 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${file}</li>`).join('')}
                        ${tier.key_files.length > 3 ? `<li style="color: var(--accent-primary); margin: 0.125rem 0;">+${tier.key_files.length - 3} more...</li>` : ''}
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
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            background: rgba(255, 255, 255, 0.02);
            border-left: 2px solid ${color};
            border-radius: 4px;
            transition: all 0.2s;
        " onmouseover="this.style.background='rgba(255, 255, 255, 0.05)'; this.style.transform='translateX(2px)'" onmouseout="this.style.background='rgba(255, 255, 255, 0.02)'; this.style.transform='translateX(0)'">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.375rem;">
                <div style="flex: 1; min-width: 0;">
                    <div style="font-weight: 600; color: var(--text-primary); font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        ${endpoint.method || endpoint.service || 'Unknown'}
                    </div>
                </div>
                <span style="
                    background: ${color}25;
                    color: ${color};
                    padding: 0.125rem 0.5rem;
                    border-radius: 10px;
                    font-size: 0.65rem;
                    font-weight: 600;
                    white-space: nowrap;
                    margin-left: 0.5rem;
                ">${endpoint.type}</span>
            </div>
            <div style="font-size: 0.7rem; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                📁 ${endpoint.file}
            </div>
            ${endpoint.http_method ? `
                <div style="font-size: 0.65rem; color: var(--accent-primary); margin-top: 0.25rem; font-weight: 600;">
                    ${endpoint.http_method}
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Render architecture metric card with hover tooltip
 * @param {string} label - Metric label
 * @param {number} score - Metric score (0-100)
 * @param {string} explanation - Detailed explanation
 * @returns {string} HTML string
 */
function renderArchitectureMetricCard(label, score, explanation) {
    const color = getScoreColor(score);
    const statusEmoji = score >= 80 ? '🟢' : score >= 60 ? '🟡' : '🔴';
    
    return `
        <div class="metric-card" style="
            position: relative;
            text-align: center;
            padding: 0.875rem;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 6px;
            cursor: help;
            transition: all 0.2s ease;
            border: 1px solid transparent;
        " 
        onmouseover="showMetricTooltip(event, '${label.replace(/'/g, "\\'")}', ${score}, '${explanation.replace(/'/g, "\\'")}', this)"
        onmouseout="hideMetricTooltip(this)">
            <div style="display: flex; align-items: center; justify-content: center; gap: 0.375rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1rem;">${statusEmoji}</span>
                <div style="font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.03em;">
                    ${label}
                </div>
            </div>
            <div style="font-size: 2.5rem; font-weight: 800; color: ${color}; font-family: 'SF Mono', monospace; line-height: 1; margin-bottom: 0.5rem;">
                ${score}
            </div>
            <div style="
                height: 3px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
                overflow: hidden;
            ">
                <div style="
                    height: 100%;
                    width: ${score}%;
                    background: ${color};
                    transition: width 0.5s ease;
                    box-shadow: 0 0 8px ${color}50;
                "></div>
            </div>
        </div>
    `;
}

/**
 * Show metric tooltip on hover
 */
window.showMetricTooltip = function(event, label, score, explanation, element) {
    // Enhanced hover effect
    element.style.background = 'rgba(255, 255, 255, 0.08)';
    element.style.transform = 'translateY(-4px)';
    element.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.3)';
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.id = 'metric-tooltip';
    tooltip.style.cssText = `
        position: fixed;
        background: linear-gradient(135deg, rgba(26, 31, 58, 0.98) 0%, rgba(10, 14, 39, 0.98) 100%);
        color: var(--text-primary);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
        z-index: 10000;
        max-width: 350px;
        border: 1px solid ${getScoreColor(score)}44;
        backdrop-filter: blur(10px);
        pointer-events: none;
        animation: tooltipFadeIn 0.2s ease-out;
    `;
    
    const statusEmoji = score >= 80 ? '🟢' : score >= 60 ? '🟡' : '🔴';
    const statusText = score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : 'Needs Work';
    
    tooltip.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; padding-bottom: 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="font-size: 2rem;">${statusEmoji}</div>
            <div style="flex: 1;">
                <div style="font-weight: 600; font-size: 1rem; color: var(--accent-primary);">${label}</div>
                <div style="font-size: 0.875rem; color: ${getScoreColor(score)}; font-weight: 600;">
                    ${score}/100 - ${statusText}
                </div>
            </div>
        </div>
        <div style="font-size: 0.875rem; line-height: 1.6; color: var(--text-secondary);">
            ${explanation}
        </div>
        ${score < 80 ? `
            <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.75rem; color: #fbbf24;">
                💡 <strong>Tip:</strong> ${score < 60 ? 'Consider significant refactoring to improve this metric.' : 'Minor adjustments can improve this score.'}
            </div>
        ` : ''}
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip near cursor
    const x = event.clientX + 15;
    const y = event.clientY + 15;
    
    // Ensure tooltip stays on screen
    const rect = tooltip.getBoundingClientRect();
    tooltip.style.left = (x + rect.width > window.innerWidth ? window.innerWidth - rect.width - 10 : x) + 'px';
    tooltip.style.top = (y + rect.height > window.innerHeight ? window.innerHeight - rect.height - 10 : y) + 'px';
};

/**
 * Hide metric tooltip
 */
window.hideMetricTooltip = function(element) {
    element.style.background = 'rgba(255, 255, 255, 0.02)';
    element.style.transform = 'translateY(0)';
    element.style.boxShadow = 'none';
    
    const tooltip = document.getElementById('metric-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
};

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
    const height = 350; // Reduced from 500
    
    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e27);
    
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 12; // Closer zoom
    camera.position.y = 4;
    
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 10);
    scene.add(directionalLight);
    
    // Create tier boxes with labels
    const tierColors = [0x00d4ff, 0x7b61ff, 0x00ff88, 0xffa500];
    const tierMeshes = [];
    
    tiers.forEach((tier, index) => {
        const geometry = new THREE.BoxGeometry(5, 1.5, 3.5); // Slightly smaller
        const material = new THREE.MeshPhongMaterial({ 
            color: tierColors[index % tierColors.length],
            transparent: true,
            opacity: 0.85,
            emissive: tierColors[index % tierColors.length],
            emissiveIntensity: 0.25
        });
        const cube = new THREE.Mesh(geometry, material);
        cube.position.y = index * 2.5 - (tiers.length * 1.25); // Tighter spacing
        cube.userData = {
            name: tier.name,
            files: tier.file_count || 0,
            loc: tier.loc || 0
        };
        scene.add(cube);
        tierMeshes.push(cube);
        
        // Add edge lines for better definition
        const edges = new THREE.EdgesGeometry(geometry);
        const lineMaterial = new THREE.LineBasicMaterial({ 
            color: 0xffffff, 
            transparent: true, 
            opacity: 0.6 
        });
        const wireframe = new THREE.LineSegments(edges, lineMaterial);
        wireframe.position.copy(cube.position);
        scene.add(wireframe);
    });
    
    // Create HTML labels overlay
    const labelsContainer = document.getElementById('tier-labels-overlay');
    if (labelsContainer && tiers.length > 0) {
        labelsContainer.innerHTML = tiers.map((tier, index) => {
            const topPosition = 50 - ((index - (tiers.length - 1) / 2) * 22); // Adjusted spacing
            return `
                <div style="
                    margin-bottom: 0.75rem;
                    position: absolute;
                    top: ${topPosition}%;
                    transform: translateY(-50%);
                    background: rgba(10, 14, 39, 0.92);
                    padding: 0.5rem 0.75rem;
                    border-radius: 6px;
                    border-left: 2px solid ${getColorHex(tierColors[index % tierColors.length])};
                    backdrop-filter: blur(10px);
                    min-width: 140px;
                ">
                    <div style="font-weight: 700; font-size: 0.8rem; color: ${getColorHex(tierColors[index % tierColors.length])}; margin-bottom: 0.125rem;">
                        ${tier.name}
                    </div>
                    <div style="font-size: 0.65rem; color: var(--text-secondary);">
                        ${tier.file_count || 0} files • ${(tier.loc || 0).toLocaleString()} LOC
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // Mouse controls
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    
    renderer.domElement.addEventListener('mousedown', (e) => {
        isDragging = true;
        isRotating = false; // Stop auto-rotation when user interacts
    });
    
    renderer.domElement.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const deltaX = e.clientX - previousMousePosition.x;
            const deltaY = e.clientY - previousMousePosition.y;
            
            scene.rotation.y += deltaX * 0.01;
            scene.rotation.x += deltaY * 0.01;
        }
        
        previousMousePosition = {
            x: e.clientX,
            y: e.clientY
        };
    });
    
    renderer.domElement.addEventListener('mouseup', () => {
        isDragging = false;
    });
    
    // Zoom with mouse wheel
    renderer.domElement.addEventListener('wheel', (e) => {
        e.preventDefault();
        camera.position.z += e.deltaY * 0.01;
        camera.position.z = Math.max(5, Math.min(25, camera.position.z)); // Clamp zoom
    });
    
    // Animation loop
    let isRotating = false; // Start with rotation off
    function animate() {
        requestAnimationFrame(animate);
        if (isRotating && !isDragging) {
            scene.rotation.y += 0.005;
        }
        renderer.render(scene, camera);
    }
    animate();
    
    // Store controls globally for button handlers
    window.resetCamera = function() {
        camera.position.set(0, 4, 12);
        camera.lookAt(0, 0, 0);
        scene.rotation.set(0, 0, 0);
        isRotating = false;
    };
    
    window.autoRotate = function() {
        isRotating = !isRotating;
    };
}

/**
 * Convert THREE.js hex color to CSS hex string
 * @param {number} color - THREE.js color (e.g., 0x00d4ff)
 * @returns {string} CSS hex color (e.g., "#00d4ff")
 */
function getColorHex(color) {
    return '#' + color.toString(16).padStart(6, '0');
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
    const height = 350; // Reduced from 600

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
        .force('link', d3.forceLink(links).id(d => d.id).distance(80)) // Tighter
        .force('charge', d3.forceManyBody().strength(-250)) // Less repulsion
        .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .enter()
        .append('line')
        .attr('stroke', '#475569')
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.5);

    // Create node groups for better interaction
    const nodeGroup = svg.append('g')
        .selectAll('g')
        .data(nodes)
        .enter()
        .append('g')
        .style('cursor', 'pointer')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Add circles with glow effect
    nodeGroup.append('circle')
        .attr('r', d => Math.sqrt(d.loc) / 6 + 8) // Smaller nodes
        .attr('fill', d => colorMap[d.tier] || colorMap.other)
        .attr('stroke', d => colorMap[d.tier] || colorMap.other)
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.9)
        .on('mouseover', function(event, d) {
            d3.select(this)
                .transition()
                .duration(150)
                .attr('r', Math.sqrt(d.loc) / 6 + 12)
                .attr('stroke-width', 2.5);
            
            // Show info tooltip
            showNodeInfo(event, d);
        })
        .on('mouseout', function(event, d) {
            d3.select(this)
                .transition()
                .duration(150)
                .attr('r', Math.sqrt(d.loc) / 6 + 8)
                .attr('stroke-width', 1.5);
            
            hideNodeInfo();
        });
    
    // Add labels with background for readability
    const labelGroup = nodeGroup.append('g');
    
    // Background rect for text
    labelGroup.append('rect')
        .attr('fill', 'rgba(10, 14, 39, 0.92)')
        .attr('rx', 3)
        .attr('ry', 3)
        .attr('x', d => -d.id.length * 3)
        .attr('y', -18)
        .attr('width', d => d.id.length * 6)
        .attr('height', 14);
    
    // Text label
    labelGroup.append('text')
        .text(d => d.id)
        .attr('font-size', '10px')
        .attr('font-weight', '600')
        .attr('fill', '#e2e8f0')
        .attr('text-anchor', 'middle')
        .attr('dy', -9);
    
    // LOC indicator
    labelGroup.append('text')
        .text(d => `${d.loc} LOC`)
        .attr('font-size', '8px')
        .attr('fill', '#94a3b8')
        .attr('text-anchor', 'middle')
        .attr('dy', 20);

    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        nodeGroup
            .attr('transform', d => `translate(${d.x},${d.y})`);
    });
    
    // Node info tooltip functions
    function showNodeInfo(event, d) {
        const tooltip = document.createElement('div');
        tooltip.id = 'node-info-tooltip';
        tooltip.style.cssText = `
            position: fixed;
            background: linear-gradient(135deg, rgba(26, 31, 58, 0.98) 0%, rgba(10, 14, 39, 0.98) 100%);
            color: var(--text-primary);
            padding: 0.625rem 0.875rem;
            border-radius: 6px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
            z-index: 10000;
            border: 1px solid ${colorMap[d.tier] || colorMap.other}44;
            backdrop-filter: blur(10px);
            pointer-events: none;
            font-size: 0.8rem;
        `;
        
        tooltip.innerHTML = `
            <div style="font-weight: 700; margin-bottom: 0.375rem; color: ${colorMap[d.tier] || colorMap.other}; font-size: 0.85rem;">
                ${d.id}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.75rem;">
                <div>📊 LOC: <strong style="color: var(--text-primary);">${d.loc.toLocaleString()}</strong></div>
                <div>🏷️ Tier: <strong style="color: ${colorMap[d.tier] || colorMap.other};">${d.tier}</strong></div>
            </div>
        `;
        
        document.body.appendChild(tooltip);
        
        const x = event.pageX + 12;
        const y = event.pageY + 12;
        const rect = tooltip.getBoundingClientRect();
        
        tooltip.style.left = (x + rect.width > window.innerWidth ? window.innerWidth - rect.width - 10 : x) + 'px';
        tooltip.style.top = (y + rect.height > window.innerHeight ? window.innerHeight - rect.height - 10 : y) + 'px';
    }
    
    function hideNodeInfo() {
        const tooltip = document.getElementById('node-info-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

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

// BaseTabComponent wrapper
class ArchitectureTab extends BaseTabComponent {
    constructor() {
        super('architecture-container');
    }
    
    render() {
        renderArchitecture(this.data);
    }
}

export { ArchitectureTab };
