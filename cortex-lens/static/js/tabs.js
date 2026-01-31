/**
 * CORTEX LENS Dashboard - Tab Management
 * Simple vanilla JS tab switching (no framework dependencies)
 */

(function() {
    'use strict';

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeTabs();
        loadDashboardData();
        updateGeneratedDate();
    });

    /**
     * Initialize tab switching functionality
     */
    function initializeTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabPanels = document.querySelectorAll('.tab-panel');

        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab');
                
                // Remove active class from all buttons and panels
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabPanels.forEach(panel => panel.classList.remove('active'));
                
                // Add active class to clicked button and corresponding panel
                this.classList.add('active');
                const targetPanel = document.getElementById(`${tabName}-tab`);
                if (targetPanel) {
                    targetPanel.classList.add('active');
                    
                    // Load visualization for this tab (if not already loaded)
                    loadTabVisualization(tabName);
                }
            });
        });
    }

    /**
     * Load dashboard data from JSON files
     */
    function loadDashboardData() {
        // Load overview data first (Tab 1)
        fetch('data/cortex/overview.json')
            .then(response => response.json())
            .then(data => {
                renderOverview(data);
            })
            .catch(error => {
                console.error('Error loading overview data:', error);
                document.getElementById('overview-content').innerHTML = 
                    '<p class="error">No dashboard data found. Run: <code>cortex lens generate</code></p>';
            });
    }

    /**
     * Load visualization for specific tab
     */
    function loadTabVisualization(tabName) {
        const vizContainer = document.getElementById(`${tabName}-viz`);
        if (!vizContainer) return;
        
        // Check if already loaded (has SVG child)
        if (vizContainer.querySelector('svg')) {
            return; // Already loaded
        }

        // Load data and render visualization
        fetch(`data/cortex/${tabName}.json`)
            .then(response => response.json())
            .then(data => {
                // Call appropriate D3.js rendering function
                switch(tabName) {
                    case 'dependencies':
                        window.renderImportGraph(data, vizContainer);
                        break;
                    case 'orchestrators':
                        window.renderOrchestratorGraph(data, vizContainer);
                        break;
                    case 'timeline':
                        window.renderTimeline(data, vizContainer);
                        break;
                    case 'impact':
                        window.renderHeatmap(data, vizContainer);
                        break;
                    case 'brain':
                        window.renderBrainArchitecture(data, vizContainer);
                        break;
                }
            })
            .catch(error => {
                console.error(`Error loading ${tabName} data:`, error);
                vizContainer.innerHTML = `<p class="error">Failed to load ${tabName} data</p>`;
            });
    }

    /**
     * Render overview content (Tab 1)
     */
    function renderOverview(data) {
        const container = document.getElementById('overview-content');
        if (!container) return;

        const html = `
            <div class="overview-section">
                <h3>What is this?</h3>
                <p class="description">${data.description || 'No description available.'}</p>
            </div>

            <div class="overview-section">
                <h3>Key Capabilities</h3>
                <ul class="capabilities-list">
                    ${(data.capabilities || []).map(cap => `<li>${cap}</li>`).join('')}
                </ul>
            </div>

            <div class="overview-section">
                <h3>Technology Stack</h3>
                <div class="tech-tags">
                    ${(data.tech_stack || []).map(tech => `<span class="tech-tag">${tech}</span>`).join('')}
                </div>
            </div>

            <div class="overview-section">
                <h3>Architecture Pattern</h3>
                <p>${data.architecture_pattern || 'N/A'}</p>
            </div>

            <div class="overview-stats">
                <div class="stat-card">
                    <div class="stat-value">${data.file_stats?.files || '0'}</div>
                    <div class="stat-label">Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${formatNumber(data.file_stats?.lines_of_code) || '0'}</div>
                    <div class="stat-label">Lines of Code</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${data.file_stats?.test_coverage || 'N/A'}</div>
                    <div class="stat-label">Test Coverage</div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    /**
     * Update generated date in footer
     */
    function updateGeneratedDate() {
        const dateElement = document.getElementById('generated-date');
        if (dateElement) {
            dateElement.textContent = new Date().toLocaleString();
        }
    }

    /**
     * Format large numbers with commas
     */
    function formatNumber(num) {
        if (!num) return '0';
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

})();
