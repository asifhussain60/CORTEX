/**
 * Migration Roadmap Tab Component
 * 
 * Wrapper for migration-roadmap-generator.js to integrate with main dashboard.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showPanelSpinner } from '../shared-utils.js';

/**
 * Render migration roadmap tab
 * @param {Object} data - Dashboard data containing tech stack information
 */
export function renderMigrationRoadmap(data) {
    const container = document.getElementById('migration-roadmap-container');
    if (!container) {
        console.error('Migration roadmap container not found');
        return;
    }
    
    // Show loading spinner
    showPanelSpinner(container, 'Loading migration roadmap...');
    
    // Render after brief delay to show spinner
    setTimeout(() => {
        try {
            // Create container structure for roadmap generator
            container.innerHTML = `
                <div class="view-header">
                    <h2>🗺️ Migration Roadmap</h2>
                    <div class="header-actions">
                        <button class="btn-secondary" onclick="exportRoadmapMarkdown()">Export Markdown</button>
                        <button class="btn-secondary" onclick="exportRoadmapJSON()">Export JSON</button>
                    </div>
                </div>
                
                <div class="glass-card" style="margin-bottom: 2rem;">
                    <h3 style="margin-bottom: 1rem;">📋 Migration Planning</h3>
                    <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1rem;">
                        This roadmap prioritizes technology migrations based on risk scores, complexity, and EOL status. 
                        Technologies are organized into 4 phases with estimated timelines and dependencies.
                    </p>
                </div>
                
                <!-- Risk Threshold Control -->
                <div class="glass-card" style="margin-bottom: 2rem;">
                    <label for="risk-threshold">
                        <strong>Risk Threshold:</strong> Only show migrations with priority score ≥
                    </label>
                    <input type="range" id="risk-threshold" min="0" max="100" value="50" 
                           style="width: 200px; margin: 0 1rem;" 
                           oninput="updateRoadmapThreshold(this.value)">
                    <span id="threshold-value">50</span>
                </div>
                
                <!-- Roadmap Container -->
                <div id="roadmap-generator-container"></div>
            `;
            
            // Initialize the roadmap generator if it exists
            if (typeof window.initializeMigrationRoadmap === 'function') {
                // Convert dashboard data to tech-stack format expected by generator
                const techStackData = convertDashboardDataToTechStack(data);
                window.initializeMigrationRoadmap(techStackData);
            } else {
                console.error('Migration roadmap generator not loaded');
                container.innerHTML += '<p style="color: var(--danger); padding: 2rem;">Migration roadmap generator not available. Please ensure migration-roadmap-generator.js is loaded.</p>';
            }
        } catch (error) {
            console.error('Error rendering migration roadmap:', error);
            container.innerHTML = `<p style="color: var(--danger); padding: 2rem;">Error loading migration roadmap: ${error.message}</p>`;
        }
    }, 100);
}

/**
 * Convert dashboard data format to tech-stack format
 * @param {Object} data - Dashboard data
 * @returns {Object} Tech stack data format
 */
function convertDashboardDataToTechStack(data) {
    // If data already has solutions array, use it
    if (data.solutions && Array.isArray(data.solutions)) {
        return data;
    }
    
    // Otherwise try to convert from dashboard format
    const solutions = [];
    
    // Extract from tech stack if available
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
 * Export roadmap as Markdown
 */
window.exportRoadmapMarkdown = function() {
    console.log('Exporting roadmap as Markdown...');
    // This function should be implemented by migration-roadmap-generator.js
    if (typeof window.exportRoadmap === 'function') {
        window.exportRoadmap('markdown');
    }
};

/**
 * Export roadmap as JSON
 */
window.exportRoadmapJSON = function() {
    console.log('Exporting roadmap as JSON...');
    if (typeof window.exportRoadmap === 'function') {
        window.exportRoadmap('json');
    }
};

/**
 * Update roadmap with new threshold
 */
window.updateRoadmapThreshold = function(threshold) {
    document.getElementById('threshold-value').textContent = threshold;
    if (typeof window.filterRoadmapByThreshold === 'function') {
        window.filterRoadmapByThreshold(parseInt(threshold));
    }
};
