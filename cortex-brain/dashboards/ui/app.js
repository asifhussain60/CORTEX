/**
 * Dashboard Application Main Controller
 * 
 * Handles routing, state management, and component coordination.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { loadDashboardData, clearCache, exportToJson, exportToCsv, enrichDashboardData } from './data-loader.js';
import { initializeAdaptiveVisibility } from './adaptive-visibility.js';
import { renderArchitecturePanels } from './components/architecture-panels.js';
import { renderOverview } from './components/overview-tab.js';
import { renderExecutiveSummary } from './components/executive-summary-tab.js';
import { renderTechStack } from './components/tech-stack-tab.js';
import { renderSecurity } from './components/security-tab.js';
import { renderArchitecture } from './components/architecture-tab.js';
import { renderCodeOrganization } from './components/code-org-tab.js';
import { renderVendors } from './components/vendors-tab.js';
import { initKeyboardNavigation } from './keyboard-navigation.js';
import { 
    initPerformanceMonitoring, 
    lazyRenderTab, 
    optimizeResizeHandler, 
    logPerformanceReport,
    clearRenderCache,
    forceRerender
} from './performance-utils.js';
import { showLoading, hideLoading, showErrorToast, showSuccessToast } from './shared-utils.js';
import { generateFullReport } from './export-utils.js';

// Application state
const appState = {
    currentSource: 'mock',
    currentTab: 'overview',
    data: null,
    loading: false,
    error: null
};

/**
 * Initialize the dashboard application
 */
async function initializeApp() {
    console.log('Initializing dashboard application...');
    
    try {
        // Initialize performance monitoring
        initPerformanceMonitoring();
        
        // Initialize keyboard navigation
        initKeyboardNavigation();
        
        // Parse URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const source = urlParams.get('source') || 'mock';
        const tab = urlParams.get('tab') || 'overview';
        
        // Update state
        appState.currentSource = source;
        appState.currentTab = tab;
        
        // Set up event listeners
        setupEventListeners();
        
        // Show loading overlay
        showLoading('Loading dashboard data...');
        
        // Load initial data
        await loadData(source);
        
        // Render initial tab
        await renderCurrentTab();
        
        // Hide loading overlay and show dashboard
        hideLoading();
        showDashboard();
        
        // Log performance metrics after initialization
        setTimeout(() => {
            logPerformanceReport();
        }, 1000);
        
        console.log('Dashboard initialized successfully');
        
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        showError('Failed to load dashboard', error.message);
        hideLoading();
    }
}

/**
 * Set up global event listeners
 */
function setupEventListeners() {
    // Tab change event
    window.addEventListener('tabChanged', async (event) => {
        appState.currentTab = event.detail.tab;
        await renderCurrentTab();
    });
    
    // Source change event
    window.addEventListener('sourceChanged', async (event) => {
        showLoading('Loading data...');
        appState.currentSource = event.detail.source;
        clearRenderCache(); // Force re-render all tabs with new data
        await loadData(event.detail.source);
        await renderCurrentTab();
        hideLoading();
    });
    
    // Refresh data event
    window.addEventListener('refreshData', async () => {
        showLoading('Refreshing data...');
        clearCache();
        clearRenderCache();
        await loadData(appState.currentSource);
        forceRerender(appState.currentTab); // Force re-render current tab
        await renderCurrentTab();
        hideLoading();
        showSuccessToast('Data refreshed successfully');
    });
    
    // Export data event
    window.addEventListener('exportData', () => {
        if (appState.data) {
            const filename = `dashboard-${appState.currentSource}-${Date.now()}.json`;
            exportToJson(appState.data, filename);
        }
    });
    
    // Generate report event
    window.addEventListener('generateReport', () => {
        if (appState.data) {
            generateFullReport(appState.data, appState.currentSource);
        }
    });
    
    // Handle browser back/forward
    window.addEventListener('popstate', () => {
        const urlParams = new URLSearchParams(window.location.search);
        const source = urlParams.get('source') || 'mock';
        const tab = urlParams.get('tab') || 'overview';
        
        if (source !== appState.currentSource) {
            document.getElementById('sourceSelect').value = source;
            appState.currentSource = source;
            loadData(source).then(() => renderCurrentTab());
        }
        
        if (tab !== appState.currentTab) {
            // Trigger tab switch through global function
            switchTab(tab);
        }
    });
}

/**
 * Load dashboard data from specified source
 * @param {string} source - Data source to load from
 */
async function loadData(source) {
    console.log(`Loading data from source: ${source}`);
    showLoading();
    clearError();
    
    try {
        appState.loading = true;
        appState.data = await loadDashboardData(source);
        
        // Enrich data with architecture detection
        appState.data = enrichDashboardData(appState.data);
        
        appState.error = null;
        appState.loading = false;
        
        // Store data globally for component access (e.g., vulnerability details)
        window.currentDashboardData = appState.data;
        
        // Initialize adaptive visibility based on detected architecture
        initializeAdaptiveVisibility(appState.data);
        
        // Render architecture panels if architecture tab is visible
        if (appState.data.architecture) {
            renderArchitecturePanels(appState.data.architecture);
        }
        
        console.log('Data loaded successfully:', appState.data);
        
    } catch (error) {
        console.error('Failed to load data:', error);
        appState.error = error.message;
        appState.loading = false;
        showError('Failed to load data', error.message);
        throw error;
    } finally {
        hideLoading();
    }
}

/**
 * Render the current active tab (with lazy loading)
 */
async function renderCurrentTab() {
    if (!appState.data) {
        console.warn('No data available to render');
        return;
    }
    
    console.log(`Rendering tab: ${appState.currentTab}`);
    
    try {
        // Use lazy rendering to only render active tab
        switch (appState.currentTab) {
            case 'overview':
                await lazyRenderTab('overview', () => renderOverview(appState.data), appState.data);
                break;
            case 'executive':
                await lazyRenderTab('executive', () => renderExecutiveSummary(appState.data), appState.data);
                break;
            case 'tech-stack':
                await lazyRenderTab('tech-stack', () => renderTechStack(appState.data), appState.data);
                break;
            case 'security':
                await lazyRenderTab('security', () => renderSecurity(appState.data), appState.data);
                break;
            case 'architecture':
                await lazyRenderTab('architecture', () => renderArchitecture(appState.data), appState.data);
                break;
            case 'code-org':
                await lazyRenderTab('code-org', () => renderCodeOrganization(appState.data), appState.data);
                break;
            case 'vendors':
                await lazyRenderTab('vendors', () => renderVendors(appState.data), appState.data);
                break;
            default:
                console.warn(`Unknown tab: ${appState.currentTab}`);
        }
    } catch (error) {
        console.error(`Error rendering tab ${appState.currentTab}:`, error);
        showError(`Failed to render ${appState.currentTab}`, error.message);
    }
}

/**
 * Show dashboard container
 */
function showDashboard() {
    const container = document.getElementById('dashboardContainer');
    if (container) {
        container.style.display = 'flex';
    }
}

/**
 * Generate PDF report of dashboard data
 */
function generatePdfReport() {
    console.log('Generating PDF report...');
    
    // For now, just show a message
    // Full PDF generation would require a library like jsPDF
    alert('PDF report generation will be available in the next update.\nFor now, you can export to JSON using the Export button.');
}

/**
 * Show error message
 * @param {string} title - Error title
 * @param {string} message - Error message
 */
function showError(title, message) {
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.innerHTML = `
            <div class="error-message">
                <h3>❌ ${title}</h3>
                <p>${message}</p>
                <button class="btn" onclick="location.reload()">Reload Page</button>
            </div>
        `;
    }
}

/**
 * Clear error message
 */
function clearError() {
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.innerHTML = '';
    }
}

/**
 * Get current application state
 * @returns {Object} - Current state
 */
export function getAppState() {
    return { ...appState };
}

/**
 * Update application state
 * @param {Object} updates - State updates
 */
export function updateAppState(updates) {
    Object.assign(appState, updates);
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Add optimized resize handler
window.addEventListener('resize', optimizeResizeHandler(async () => {
    console.log('Window resized, re-rendering visualizations...');
    forceRerender(appState.currentTab);
    await renderCurrentTab();
}, 300));

// Export for debugging
window.appState = appState;
window.loadData = loadData;
window.logPerformanceReport = logPerformanceReport;
