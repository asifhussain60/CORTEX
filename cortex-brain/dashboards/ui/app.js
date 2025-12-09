/**
 * Dashboard Application Main Controller
 * 
 * Handles routing, state management, and component coordination.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { loadDashboardData, loadAdditionalData, clearCache, exportToJson, exportToCsv, enrichDashboardData } from './data-loader.js';
import { initializeAdaptiveVisibility } from './adaptive-visibility.js';
// REMOVED: Frontend/Backend/Database panels now consolidated in architecture-tab.js
// import { renderArchitecturePanels } from './components/architecture-panels.js';
import { renderExecutiveSummary } from './components/executive-tab.js';
import { renderOverview } from './components/overview-tab-v3.js'; // UPDATED: Use new v3 component
import { renderTechStack } from './components/tech-stack-tab.js';
import { renderSecurity } from './components/security-tab.js';
import { renderArchitecture } from './components/architecture-tab.js';
import { renderCodeOrganization } from './components/code-org-tab.js';
import { renderVendors } from './components/vendors-tab.js';
import { renderUseCases } from './components/use-cases-tab.js';
import { renderRecommendations } from './components/recommendations-tab.js';
import EngineeringOnboardingTab from './components/engineering-onboarding-tab.js';
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
import { progressiveLoader } from './progressive-loader.js';

// Application state
const appState = {
    currentSource: 'mock',
    currentTab: 'executive',
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
        const tab = urlParams.get('tab') || 'executive';
        
        // Update state
        appState.currentSource = source;
        appState.currentTab = tab;
        
        // Set up event listeners
        setupEventListeners();
        
        // Set up tab navigation (MUST be after DOM ready)
        setupTabNavigation();
        
        // Update source selector with discovered repositories
        await updateSourceSelector();
        
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
 * Global function to switch tabs (called from inline onclick and event listeners)
 * Shows loading indicator, renders content, and updates UI
 * @param {string} tabName - Name of the tab to switch to
 */
async function switchTab(tabName) {
    if (!appState.data && tabName !== 'executive') {
        console.warn('No data available to render tab:', tabName);
        return;
    }
    
    try {
        // Show loading indicator
        showLoading(`Loading ${tabName}...`);
        
        // Update app state
        appState.currentTab = tabName;
        
        // Update UI - nav tabs
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        const activeTab = document.querySelector(`[data-tab="${tabName}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        // Update UI - content visibility
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        const targetContent = document.getElementById(`tab-${tabName}`);
        if (targetContent) {
            targetContent.classList.add('active');
        }
        
        // Update title
        const titles = {
            'executive': 'Executive Summary',
            'overview': 'System Overview',
            'tech-stack': 'Tech Stack',
            'security': 'Security',
            'use-cases': 'Use Cases',
            'recommendations': 'Recommendations',
            'architecture': 'Architecture',
            'code-org': 'Code Organization',
            'vendors': 'Dependencies',
            'engineering': 'Engineering Onboarding'
        };
        const titleElement = document.getElementById('contentTitle');
        if (titleElement && titles[tabName]) {
            titleElement.textContent = titles[tabName];
        }
        
        // Render tab content automatically
        await renderCurrentTab();
        
        // Hide loading indicator
        hideLoading();
        
    } catch (error) {
        console.error(`Failed to switch to tab ${tabName}:`, error);
        hideLoading();
        showErrorToast(`Failed to load ${tabName} tab`);
    }
}

/**
 * Set up tab navigation event listeners
 */
function setupTabNavigation() {
    // Add click listeners to all nav tabs
    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = tab.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

/**
 * Render engineering tab (special case with async data loading)
 */
async function renderEngineeringTab() {
    try {
        const onboardingData = await loadAdditionalData('mock', 'engineering-onboarding.json');
        const tab = new EngineeringOnboardingTab();
        await tab.init(onboardingData);
    } catch (e) {
        console.error('Failed to load onboarding data:', e);
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
    
    // Repository monitoring events
    window.addEventListener('repository-added', (event) => {
        console.log('Repository added:', event.detail);
        updateSourceSelector();
    });
    
    window.addEventListener('repository-removed', (event) => {
        console.log('Repository removed:', event.detail);
        updateSourceSelector();
        
        // If currently viewing removed repository, switch to mock
        if (appState.currentSource === event.detail.name) {
            handleSourceChange('mock');
        }
    });
    
    window.addEventListener('repository-updated', (event) => {
        console.log('Repository updated:', event.detail);
        
        // Refresh data if currently viewing updated repository
        if (appState.currentSource === event.detail.name) {
            window.dispatchEvent(new CustomEvent('refreshData'));
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
        // REMOVED: Frontend/Backend/Database panels now consolidated in architecture-tab.js
        // if (appState.data.architecture) {
        //     renderArchitecturePanels(appState.data.architecture);
        // }
        
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
 * Render the current active tab
 */
async function renderCurrentTab() {
    if (!appState.data) {
        console.warn('No data available to render');
        return;
    }
    
    try {
        const tabId = getTabContainerId(appState.currentTab);
        const tabElement = document.getElementById(tabId);
        
        if (!tabElement) {
            console.error(`Tab element not found: ${tabId}`);
            return;
        }
        
        // Render content - tab visibility already managed by setupTabNavigation()
        switch (appState.currentTab) {
            case 'executive':
                renderExecutiveSummary(appState.data);
                break;
            case 'overview':
                renderOverview(appState.data.overview || appState.data);
                break;
            case 'tech-stack':
                renderTechStack(appState.data);
                break;
            case 'security':
                renderSecurity(appState.data);
                break;
            case 'architecture':
                renderArchitecture(appState.data);
                break;
            case 'code-org':
                renderCodeOrganization(appState.data);
                break;
            case 'vendors':
                renderVendors(appState.data);
                break;
            case 'use-cases': {
                // Load use cases data separately
                try {
                    const useCasesData = await loadAdditionalData(appState.currentSource, 'use-cases.json');
                    renderUseCases(useCasesData);
                } catch (e) {
                    console.error('Failed to load use cases data:', e);
                    renderUseCases({ use_cases: [], roles: [], domains: [], counts: {} });
                }
                break;
            }
            case 'recommendations': {
                // Load recommendations data separately
                try {
                    const recommendationsData = await loadAdditionalData(appState.currentSource, 'recommendations.json');
                    renderRecommendations(recommendationsData);
                } catch (e) {
                    console.error('Failed to load recommendations data:', e);
                    renderRecommendations({ recommendations: [], top_recommendations: [], counts: {} });
                }
                break;
            }
            case 'engineering':
                // Content loaded by click handler in setupTabNavigation()
                break;
            default:
                console.warn(`Unknown tab: ${appState.currentTab}`);
                return;
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
 * Helper: Map tab key to container id used by progressive loader
 */
function getTabContainerId(tabKey) {
    switch (tabKey) {
        case 'executive': return 'tab-executive';
        case 'overview': return 'tab-overview';
        case 'use-cases': return 'tab-use-cases';
        case 'tech-stack': return 'tab-tech-stack';
        case 'security': return 'tab-security';
        case 'architecture': return 'tab-architecture';
        case 'code-org': return 'tab-code-org';
        case 'vendors': return 'tab-vendors';
        case 'engineering': return 'tab-engineering';
        case 'recommendations': return 'tab-recommendations';
        default: return 'tab-overview';
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
 * Update source selector dropdown with current repositories
 */
async function updateSourceSelector() {
    try {
        const response = await fetch('../data/registry.json');
        const registry = await response.json();
        
        const select = document.getElementById('sourceSelect');
        if (!select) return;
        
        // Store current selection
        const currentValue = select.value;
        
        // Clear existing options except mock
        select.innerHTML = '<option value="mock">Mock Data (Demo)</option>';
        
        // Add repositories from registry
        if (registry.repositories && Array.isArray(registry.repositories)) {
            registry.repositories.forEach(repo => {
                const option = document.createElement('option');
                option.value = repo.name;
                option.textContent = repo.display_name || repo.name;
                select.appendChild(option);
            });
        }
        
        // Restore selection if still available
        if (currentValue && [...select.options].some(opt => opt.value === currentValue)) {
            select.value = currentValue;
        }
        
    } catch (error) {
        console.error('Failed to update source selector:', error);
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

// Note: Single getTabContainerId defined above; removed duplicate mapping to avoid confusion.

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

// Export for debugging and global access
window.appState = appState;
window.loadData = loadData;
window.logPerformanceReport = logPerformanceReport;
window.switchTab = switchTab;

// Export for module usage
export { switchTab };
