/**
 * Dependency Bloat Analyzer Tab Component
 * 
 * Wrapper for dependency-bloat-analyzer.js to integrate with main dashboard.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showPanelSpinner } from '../shared-utils.js';

/**
 * Render dependency bloat analyzer tab
 * @param {Object} data - Dashboard data containing tech stack information
 */
export function renderDependencyBloat(data) {
    const container = document.getElementById('dependency-bloat-container');
    if (!container) {
        console.error('Dependency bloat container not found');
        return;
    }
    
    // Show loading spinner
    showPanelSpinner(container, 'Loading dependency bloat analysis...');
    
    // Render after brief delay to show spinner
    setTimeout(() => {
        try {
            // Create container structure for bloat analyzer
            container.innerHTML = `
                <div class="view-header">
                    <h2>📦 Dependency Bloat Analyzer</h2>
                    <div class="header-actions">
                        <button class="btn-secondary" onclick="exportBloatAnalysis()">Export Analysis</button>
                        <button class="btn-secondary" onclick="downloadBloatReport()">Download Report</button>
                    </div>
                </div>
                
                <div class="glass-card" style="margin-bottom: 2rem;">
                    <h3 style="margin-bottom: 1rem;">📊 Bloat Score Formula (Z-Score)</h3>
                    <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1rem;">
                        Bloat Score = (Package Count - Mean) / Standard Deviation
                    </p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                        <div style="text-align: center;">
                            <div style="width: 40px; height: 40px; background: #E74C3C; border-radius: 8px; margin: 0 auto 0.5rem;"></div>
                            <strong>≥ 2.0</strong><br>
                            <span style="color: var(--text-secondary);">Critical</span>
                        </div>
                        <div style="text-align: center;">
                            <div style="width: 40px; height: 40px; background: #F39C12; border-radius: 8px; margin: 0 auto 0.5rem;"></div>
                            <strong>1.0 - 1.99</strong><br>
                            <span style="color: var(--text-secondary);">Warning</span>
                        </div>
                        <div style="text-align: center;">
                            <div style="width: 40px; height: 40px; background: #27AE60; border-radius: 8px; margin: 0 auto 0.5rem;"></div>
                            <strong>&lt; 1.0</strong><br>
                            <span style="color: var(--text-secondary);">Normal</span>
                        </div>
                    </div>
                </div>
                
                <!-- Statistics Summary -->
                <div id="bloat-stats-summary" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
                    <!-- Will be populated by analyzer -->
                </div>
                
                <!-- Filter Controls -->
                <div class="glass-card" style="margin-bottom: 2rem;">
                    <div style="display: flex; gap: 2rem; align-items: center; flex-wrap: wrap;">
                        <div>
                            <label for="bloat-category-filter"><strong>Category:</strong></label>
                            <select id="bloat-category-filter" onchange="filterBloatByCategory(this.value)" 
                                    style="margin-left: 0.5rem; padding: 0.5rem; background: var(--glass-bg); color: var(--text-primary); border: 1px solid var(--glass-border); border-radius: 4px;">
                                <option value="all">All Categories</option>
                                <option value="critical">Critical Only</option>
                                <option value="warning">Warning Only</option>
                                <option value="normal">Normal Only</option>
                            </select>
                        </div>
                        <div>
                            <label>
                                <input type="checkbox" id="show-outliers-only" onchange="toggleOutliersOnly(this.checked)">
                                <span style="margin-left: 0.5rem;">Show Outliers Only</span>
                            </label>
                        </div>
                    </div>
                </div>
                
                <!-- Histogram Container -->
                <div class="glass-card" style="margin-bottom: 2rem;">
                    <h3 style="margin-bottom: 1rem;">📊 Package Distribution Histogram</h3>
                    <div id="bloat-histogram-container"></div>
                </div>
                
                <!-- Box Plot Container -->
                <div class="glass-card" style="margin-bottom: 2rem;">
                    <h3 style="margin-bottom: 1rem;">📈 Box Plot Analysis</h3>
                    <div id="bloat-boxplot-container"></div>
                </div>
                
                <!-- Solutions Table -->
                <div class="glass-card">
                    <h3 style="margin-bottom: 1rem;">📋 Top Solutions by Bloat Score</h3>
                    <div id="bloat-solutions-table"></div>
                </div>
                
                <!-- Recommendations -->
                <div class="glass-card" style="margin-top: 2rem;">
                    <h3 style="margin-bottom: 1rem;">💡 Recommendations</h3>
                    <div id="bloat-recommendations"></div>
                </div>
            `;
            
            // Initialize the bloat analyzer if it exists
            if (typeof window.initializeDependencyBloatAnalyzer === 'function') {
                const techStackData = convertDashboardDataToTechStack(data);
                window.initializeDependencyBloatAnalyzer(techStackData);
            } else {
                console.error('Dependency bloat analyzer not loaded');
                container.innerHTML += '<p style="color: var(--danger); padding: 2rem;">Dependency bloat analyzer not available. Please ensure dependency-bloat-analyzer.js is loaded.</p>';
            }
        } catch (error) {
            console.error('Error rendering dependency bloat:', error);
            container.innerHTML = `<p style="color: var(--danger); padding: 2rem;">Error loading dependency bloat analyzer: ${error.message}</p>`;
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
 * Export bloat analysis
 */
window.exportBloatAnalysis = function() {
    console.log('Exporting bloat analysis...');
    if (typeof window.exportBloatData === 'function') {
        window.exportBloatData('json');
    }
};

/**
 * Download bloat report
 */
window.downloadBloatReport = function() {
    console.log('Downloading bloat report...');
    if (typeof window.exportBloatData === 'function') {
        window.exportBloatData('pdf');
    }
};

/**
 * Filter by bloat category
 */
window.filterBloatByCategory = function(category) {
    console.log('Filtering by category:', category);
    if (typeof window.filterBloatAnalysis === 'function') {
        window.filterBloatAnalysis({ category });
    }
};

/**
 * Toggle outliers-only view
 */
window.toggleOutliersOnly = function(showOutliersOnly) {
    console.log('Show outliers only:', showOutliersOnly);
    if (typeof window.filterBloatAnalysis === 'function') {
        window.filterBloatAnalysis({ showOutliersOnly });
    }
};
