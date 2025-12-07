/**
 * Progressive Loading Manager
 * 
 * Handles skeleton loaders, progressive data loading, and smooth transitions
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

export class ProgressiveLoadingManager {
    constructor() {
        this.loadingStates = new Map();
        this.skeletonTemplates = this.initSkeletonTemplates();
    }

    /**
     * Initialize skeleton templates for different components
     */
    initSkeletonTemplates() {
        return {
            healthScore: `
                <div class="skeleton-health-score"></div>
                <div class="loading-message">
                    Calculating holistic health score...
                    <div class="loading-submessage">Analyzing across all dimensions</div>
                </div>
            `,
            
            metricCards: `
                <div class="skeleton-metrics-grid">
                    ${Array(4).fill('<div class="skeleton-metric-card"><div class="skeleton-metric-card-title"></div><div class="skeleton-metric-card-value"></div></div>').join('')}
                </div>
            `,
            
            chart: `
                <div class="skeleton-chart"></div>
                <div class="loading-message">Loading visualization...</div>
            `,
            
            table: (rows = 5) => `
                <div class="skeleton-table">
                    ${Array(rows).fill(`
                        <div class="skeleton-table-row">
                            <div class="skeleton-table-cell"></div>
                            <div class="skeleton-table-cell"></div>
                            <div class="skeleton-table-cell"></div>
                        </div>
                    `).join('')}
                </div>
            `,
            
            techStack: `
                <div class="skeleton-tech-stack">
                    ${Array(8).fill('<div class="skeleton-tech-item"></div>').join('')}
                </div>
                <div class="loading-message">Analyzing technology stack...</div>
            `,
            
            security: `
                <div class="skeleton-security-grid">
                    ${Array(4).fill('<div class="skeleton-vulnerability-card"></div>').join('')}
                </div>
                <div class="loading-message">Scanning security vulnerabilities...</div>
            `,
            
            architecture: `
                <div class="skeleton-architecture">
                    <div class="skeleton-architecture-diagram"></div>
                </div>
                <div class="loading-message">Detecting architecture patterns...</div>
            `,
            
            codeOrganization: `
                <div class="loading-container">
                    <div class="skeleton-chart"></div>
                    <div class="skeleton-metrics-grid">
                        ${Array(3).fill('<div class="skeleton-metric-card"><div class="skeleton-metric-card-title"></div><div class="skeleton-metric-card-value"></div></div>').join('')}
                    </div>
                </div>
                <div class="loading-message">Analyzing code organization...</div>
            `,
            
            executiveSummary: `
                <div class="skeleton-executive-summary">
                    <div class="skeleton-health-score"></div>
                    <div class="skeleton-text skeleton-text-long"></div>
                    <div class="skeleton-text skeleton-text-medium"></div>
                    <div class="skeleton-text skeleton-text-short"></div>
                    <div class="skeleton-metrics-grid" style="margin-top: 30px;">
                        ${Array(6).fill('<div class="skeleton-metric-card"><div class="skeleton-metric-card-title"></div><div class="skeleton-metric-card-value"></div></div>').join('')}
                    </div>
                </div>
            `
        };
    }

    /**
     * Show skeleton loader for a component
     * @param {string} containerId - Container element ID
     * @param {string} type - Skeleton type (healthScore, metricCards, etc.)
     * @param {Object} options - Additional options
     */
    showSkeleton(containerId, type, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`Container ${containerId} not found`);
            return;
        }

        // Get skeleton template
        const template = typeof this.skeletonTemplates[type] === 'function' 
            ? this.skeletonTemplates[type](options.rows)
            : this.skeletonTemplates[type];

        if (!template) {
            console.warn(`Unknown skeleton type: ${type}`);
            return;
        }

        // Show skeleton
        container.innerHTML = `<div class="loading-overlay">${template}</div>`;
        this.loadingStates.set(containerId, { type, startTime: Date.now() });
    }

    /**
     * Hide skeleton and show content with smooth transition
     * @param {string} containerId - Container element ID
     * @param {string} contentHtml - Content to display
     * @param {number} minDisplayTime - Minimum skeleton display time (ms)
     */
    async hideSkeleton(containerId, contentHtml, minDisplayTime = 300) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const loadingState = this.loadingStates.get(containerId);
        if (!loadingState) {
            // No skeleton was shown, just set content
            container.innerHTML = contentHtml;
            return;
        }

        // Calculate elapsed time
        const elapsed = Date.now() - loadingState.startTime;
        const remainingTime = Math.max(0, minDisplayTime - elapsed);

        // Wait for minimum display time
        if (remainingTime > 0) {
            await new Promise(resolve => setTimeout(resolve, remainingTime));
        }

        // Fade out skeleton
        const overlay = container.querySelector('.loading-overlay');
        if (overlay) {
            overlay.style.transition = 'opacity 0.3s ease-out';
            overlay.style.opacity = '0';
            
            await new Promise(resolve => setTimeout(resolve, 300));
        }

        // Set content and fade in
        container.innerHTML = contentHtml;
        container.classList.add('content-loaded');

        // Cleanup
        this.loadingStates.delete(containerId);
    }

    /**
     * Show progress bar with percentage
     * @param {string} containerId - Container element ID
     * @param {number} progress - Progress percentage (0-100)
     * @param {string} message - Loading message
     */
    showProgress(containerId, progress, message = 'Loading...') {
        const container = document.getElementById(containerId);
        if (!container) return;

        let progressBar = container.querySelector('.skeleton-progress');
        if (!progressBar) {
            container.innerHTML = `
                <div class="loading-overlay">
                    <div class="skeleton-progress">
                        <div class="skeleton-progress-bar" style="width: 0%"></div>
                    </div>
                    <div class="loading-message">
                        ${message}
                        <div class="loading-submessage">
                            <span class="progress-percentage">0%</span> complete
                        </div>
                    </div>
                </div>
            `;
            progressBar = container.querySelector('.skeleton-progress-bar');
        }

        // Update progress
        const bar = container.querySelector('.skeleton-progress-bar');
        const percentage = container.querySelector('.progress-percentage');
        
        if (bar) bar.style.width = `${progress}%`;
        if (percentage) percentage.textContent = `${Math.round(progress)}%`;
    }

    /**
     * Load tab with skeleton and progressive data loading
     * @param {string} tabName - Tab name
     * @param {Function} dataLoader - Async function that loads data
     * @param {Function} renderer - Function that renders data
     */
    async loadTabWithSkeleton(tabName, dataLoader, renderer) {
        const containerId = `${tabName}-content`;
        const skeletonType = this.getSkeletonTypeForTab(tabName);

        // Show skeleton
        this.showSkeleton(containerId, skeletonType);

        try {
            // Load data
            const data = await dataLoader();

            // Render content
            const contentHtml = renderer(data);

            // Hide skeleton and show content
            await this.hideSkeleton(containerId, contentHtml);

            return { success: true, data };
        } catch (error) {
            console.error(`Error loading ${tabName}:`, error);
            
            // Show error state
            const errorHtml = `
                <div class="error-state">
                    <div class="error-icon">⚠️</div>
                    <div class="error-message">Failed to load ${tabName}</div>
                    <div class="error-details">${error.message}</div>
                    <button onclick="window.retryLoad('${tabName}')" class="retry-button">
                        Retry
                    </button>
                </div>
            `;
            
            await this.hideSkeleton(containerId, errorHtml, 0);
            
            return { success: false, error };
        }
    }

    /**
     * Get appropriate skeleton type for tab
     * @param {string} tabName - Tab name
     * @returns {string} - Skeleton type
     */
    getSkeletonTypeForTab(tabName) {
        const skeletonMap = {
            'executive': 'executiveSummary',
            'overview': 'executiveSummary',
            'tech-stack': 'techStack',
            'security': 'security',
            'architecture': 'architecture',
            'code-organization': 'codeOrganization',
            'code-org': 'codeOrganization',
            'dependencies': 'table',
            'team': 'metricCards',
            'engineering': 'metricCards'
        };

        return skeletonMap[tabName] || 'metricCards';
    }

    /**
     * Preload data in background and cache
     * @param {string} source - Data source
     * @param {Array<string>} tabs - Tabs to preload
     */
    async preloadData(source, tabs = []) {
        // This would connect to data-loader.js
        console.log(`Preloading data for ${source}: ${tabs.join(', ')}`);
        
        // Implementation would trigger background data loading
        // and cache results for instant display when tab is clicked
    }

    /**
     * Show loading state for expensive calculations
     * @param {string} containerId - Container ID
     * @param {string} calculationType - Type of calculation
     * @returns {Function} - Completion callback
     */
    startCalculation(containerId, calculationType) {
        const container = document.getElementById(containerId);
        if (!container) return () => {};

        const messages = {
            'holistic_score': 'Calculating holistic health score...',
            'security_scan': 'Running security vulnerability scan...',
            'tech_debt': 'Analyzing technical debt...',
            'architecture': 'Detecting architecture patterns...',
            'dependencies': 'Analyzing dependencies...'
        };

        const message = messages[calculationType] || 'Processing...';
        
        this.showSkeleton(containerId, 'healthScore');
        const startTime = Date.now();

        // Return completion callback
        return (result) => {
            const duration = Date.now() - startTime;
            console.log(`${calculationType} completed in ${duration}ms`);
            
            // Ensure minimum display time for UX
            const minTime = 500;
            const remainingTime = Math.max(0, minTime - duration);
            
            setTimeout(() => {
                this.hideSkeleton(containerId, result);
            }, remainingTime);
        };
    }
}

// Export singleton instance
export const progressiveLoader = new ProgressiveLoadingManager();

// Global retry function
window.retryLoad = function(tabName) {
    const event = new CustomEvent('retryTabLoad', { detail: { tab: tabName } });
    window.dispatchEvent(event);
};
