/**
 * Framework Health Heatmap Tab Component
 * 
 * Wrapper for framework-health-heatmap.js to integrate with main dashboard.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showPanelSpinner } from '../shared-utils.js';

/**
 * Render framework health heatmap tab
 * @param {Object} data - Dashboard data containing tech stack information
 */
export function renderFrameworkHealth(data) {
    const container = document.getElementById('framework-health-container');
    if (!container) {
        console.error('Framework health container not found');
        return;
    }
    
    // Show loading spinner
    showPanelSpinner(container, 'Loading framework health heatmap...');
    
    // Render after brief delay to show spinner
    setTimeout(() => {
        try {
            // Create container structure for heatmap
            container.innerHTML = `
                <div class="view-header">
                    <h2>🏥 Framework Health Heatmap</h2>
                    <div class="header-actions">
                        <button class="btn-secondary" onclick="exportHeatmapData()">Export Data</button>
                        <button class="btn-secondary" onclick="downloadHeatmapImage()">Download Image</button>
                    </div>
                </div>
                
                <div class="glass-card" style="margin-bottom: 2rem;">
                    <h3 style="margin-bottom: 1rem;">📊 Health Score Formula</h3>
                    <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1rem;">
                        Health Score = (Version Currency × 25%) + (CVE Score × 30%) + (EOL Status × 25%) + (Community Activity × 20%)
                    </p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                        <div style="text-align: center;">
                            <div style="width: 40px; height: 40px; background: #27AE60; border-radius: 8px; margin: 0 auto 0.5rem;"></div>
                            <strong>70-100</strong><br>
                            <span style="color: var(--text-secondary);">Healthy</span>
                        </div>
                        <div style="text-align: center;">
                            <div style="width: 40px; height: 40px; background: #F39C12; border-radius: 8px; margin: 0 auto 0.5rem;"></div>
                            <strong>50-69</strong><br>
                            <span style="color: var(--text-secondary);">Warning</span>
                        </div>
                        <div style="text-align: center;">
                            <div style="width: 40px; height: 40px; background: #E67E22; border-radius: 8px; margin: 0 auto 0.5rem;"></div>
                            <strong>30-49</strong><br>
                            <span style="color: var(--text-secondary);">Attention</span>
                        </div>
                        <div style="text-align: center;">
                            <div style="width: 40px; height: 40px; background: #E74C3C; border-radius: 8px; margin: 0 auto 0.5rem;"></div>
                            <strong>0-29</strong><br>
                            <span style="color: var(--text-secondary);">Critical</span>
                        </div>
                    </div>
                </div>
                
                <!-- Filter Controls -->
                <div class="glass-card" style="margin-bottom: 2rem;">
                    <div style="display: flex; gap: 2rem; align-items: center; flex-wrap: wrap;">
                        <div>
                            <label for="health-category-filter"><strong>Category:</strong></label>
                            <select id="health-category-filter" onchange="filterHeatmapByCategory(this.value)" 
                                    style="margin-left: 0.5rem; padding: 0.5rem; background: var(--glass-bg); color: var(--text-primary); border: 1px solid var(--glass-border); border-radius: 4px;">
                                <option value="all">All Categories</option>
                                <option value="frontend">Frontend</option>
                                <option value="backend">Backend</option>
                                <option value="database">Database</option>
                                <option value="devops">DevOps</option>
                            </select>
                        </div>
                        <div>
                            <label>
                                <input type="checkbox" id="show-critical-only" onchange="toggleCriticalOnly(this.checked)">
                                <span style="margin-left: 0.5rem;">Show Critical Only (&lt; 50)</span>
                            </label>
                        </div>
                    </div>
                </div>
                
                <!-- Heatmap Container -->
                <div id="health-heatmap-container"></div>
            `;
            
            // Initialize the heatmap if it exists
            if (typeof window.initializeFrameworkHealthHeatmap === 'function') {
                const techStackData = convertDashboardDataToTechStack(data);
                window.initializeFrameworkHealthHeatmap(techStackData);
            } else {
                console.error('Framework health heatmap not loaded');
                container.innerHTML += '<p style="color: var(--danger); padding: 2rem;">Framework health heatmap not available. Please ensure framework-health-heatmap.js is loaded.</p>';
            }
        } catch (error) {
            console.error('Error rendering framework health:', error);
            container.innerHTML = `<p style="color: var(--danger); padding: 2rem;">Error loading framework health: ${error.message}</p>`;
        }
    }, 100);
}

/**
 * Convert dashboard data format to tech-stack format
 * @param {Object} data - Dashboard data
 * @returns {Object} Tech stack data format
 */
function convertDashboardDataToTechStack(data) {
    if (data.solutions && Array.isArray(data.solutions)) {
        return data;
    }
    
    const solutions = [];
    
    if (data.techStack && data.techStack.categories) {
        Object.entries(data.techStack.categories).forEach(([category, items]) => {
            if (Array.isArray(items)) {
                items.forEach(item => {
                    solutions.push({
                        name: item.name || item.technology,
                        category: category,
                        version: item.currentVersion || item.version,
                        latest: item.latestVersion || item.targetVersion,
                        packages: item.packages || []
                    });
                });
            }
        });
    }
    
    return { solutions };
}

/**
 * Export heatmap data
 */
window.exportHeatmapData = function() {
    console.log('Exporting heatmap data...');
    if (typeof window.exportHeatmap === 'function') {
        window.exportHeatmap('json');
    }
};

/**
 * Download heatmap as image
 */
window.downloadHeatmapImage = function() {
    console.log('Downloading heatmap image...');
    if (typeof window.exportHeatmap === 'function') {
        window.exportHeatmap('png');
    }
};

/**
 * Filter heatmap by category
 */
window.filterHeatmapByCategory = function(category) {
    console.log('Filtering by category:', category);
    if (typeof window.filterHeatmap === 'function') {
        window.filterHeatmap({ category });
    }
};

/**
 * Toggle critical-only view
 */
window.toggleCriticalOnly = function(showCriticalOnly) {
    console.log('Show critical only:', showCriticalOnly);
    if (typeof window.filterHeatmap === 'function') {
        window.filterHeatmap({ showCriticalOnly });
    }
};
