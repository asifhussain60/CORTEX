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
import { renderOnboarding } from './components/onboarding-tab.js';
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
 * Transform backend recommendations structure to UI-expected format
 * Backend: {recommendations: {category: [rec, ...]}, summary: {...}}
 * UI: {recommendations: [], top_recommendations: [], counts: {}}
 */
function transformRecommendationsData(rawData) {
    console.log('[TRANSFORM] Raw recommendations data:', rawData);
    
    if (!rawData || !rawData.recommendations) {
        console.warn('[TRANSFORM] No recommendations data to transform');
        return { recommendations: [], top_recommendations: [], counts: {} };
    }

    // Calculate ROI score from impact and effort
    const calculateROI = (impact, effort) => {
        const impactScore = { high: 3, medium: 2, low: 1 }[impact?.toLowerCase()] || 1;
        const effortScore = { low: 3, medium: 2, high: 1 }[effort?.toLowerCase()] || 1;
        return impactScore * effortScore; // Higher is better (high impact + low effort = 9)
    };

    // Generate title from description
    const generateTitle = (description) => {
        if (!description) return 'Recommendation';
        const cleaned = description.replace(/^(Consider|Add|Remove|Update|Fix|Improve)\s+/i, '');
        return cleaned.length > 60 ? cleaned.substring(0, 57) + '...' : cleaned;
    };

    // Flatten nested categories into single array
    const flatRecommendations = [];
    for (const [category, recs] of Object.entries(rawData.recommendations)) {
        if (Array.isArray(recs)) {
            recs.forEach(rec => {
                flatRecommendations.push({
                    ...rec,
                    title: generateTitle(rec.description),
                    roi_score: calculateROI(rec.impact, rec.effort),
                    category: rec.category || category // Ensure category is set
                });
            });
        }
    }

    // Sort by ROI score (highest first)
    flatRecommendations.sort((a, b) => b.roi_score - a.roi_score);

    // Extract top recommendations
    const topRecommendations = flatRecommendations.slice(0, 10);

    // Build counts from summary
    const counts = {
        total: rawData.summary?.total_recommendations || flatRecommendations.length,
        by_priority: rawData.summary?.by_priority || {},
        by_category: rawData.summary?.by_category || {}
    };

    console.log('[TRANSFORM] Transformed to:', {
        count: flatRecommendations.length,
        topCount: topRecommendations.length,
        counts
    });

    return {
        recommendations: flatRecommendations,
        top_recommendations: topRecommendations,
        counts: counts
    };
}

/**
 * Initialize the dashboard application
 */
async function initializeApp() {
    console.log('[INIT] 🚀 Starting dashboard initialization...');
    
    try {
        // Initialize performance monitoring
        console.log('[INIT] Initializing performance monitoring...');
        initPerformanceMonitoring();
        
        // Initialize keyboard navigation
        console.log('[INIT] Initializing keyboard navigation...');
        initKeyboardNavigation();
        
        // Parse URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const source = urlParams.get('source') || 'mock';
        const tab = urlParams.get('tab') || 'executive';
        console.log(`[INIT] URL params - source: ${source}, tab: ${tab}`);
        
        // Update state
        appState.currentSource = source;
        appState.currentTab = tab;
        console.log('[INIT] App state:', JSON.stringify(appState, null, 2));
        
        // Set up event listeners
        console.log('[INIT] Setting up event listeners...');
        setupEventListeners();
        
        // Set up tab navigation (MUST be after DOM ready)
        console.log('[INIT] Setting up tab navigation...');
        setupTabNavigation();
        console.log('[INIT] Tab navigation setup complete');
        
        // Update source selector with discovered repositories
        console.log('[INIT] Updating source selector...');
        await updateSourceSelector();
        
        // Show loading overlay
        showLoading('Loading dashboard data...');
        
        // Load initial data
        console.log(`[INIT] Loading data from source: ${source}...`);
        await loadData(source);
        console.log('[INIT] ✓ Data loaded successfully');
        
        // Render initial tab using switchTab to properly manage visibility
        console.log(`[INIT] Rendering initial tab: ${tab}...`);
        await switchTab(tab);
        console.log('[INIT] ✓ Initial tab rendered');
        
        // Hide loading overlay and show dashboard
        hideLoading();
        showDashboard();
        
        // Log performance metrics after initialization
        setTimeout(() => {
            logPerformanceReport();
        }, 1000);
        
        console.log('[INIT] ✅ Dashboard initialized successfully');
        
    } catch (error) {
        console.error('[INIT] ❌ Failed to initialize dashboard:', error);
        console.error('[INIT] Error stack:', error.stack);
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
    console.log(`[SWITCH] Tab switch requested: ${tabName}`);
    
    if (!appState.data && tabName !== 'executive') {
        console.warn('[SWITCH] No data available to render tab:', tabName);
        return;
    }
    
    try {
        // Show loading indicator
        showLoading(`Loading ${tabName}...`);
        
        // Update app state
        console.log(`[SWITCH] Updating app state to: ${tabName}`);
        appState.currentTab = tabName;
        
        // Update UI - nav tabs
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        const activeTab = document.querySelector(`[data-tab="${tabName}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
            console.log(`[VISIBILITY] Nav tab activated: ${tabName}`);
        } else {
            console.warn(`[VISIBILITY] Nav tab not found: ${tabName}`);
        }
        
        // Update UI - content visibility
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        const targetContent = document.getElementById(`tab-${tabName}`);
        if (targetContent) {
            targetContent.classList.add('active');
            console.log(`[VISIBILITY] Content container activated: tab-${tabName}`);
        } else {
            console.error(`[VISIBILITY] Content container not found: tab-${tabName}`);
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
            'onboarding': 'Onboarding'
        };
        const titleElement = document.getElementById('contentTitle');
        if (titleElement && titles[tabName]) {
            titleElement.textContent = titles[tabName];
        }
        
        // Render tab content automatically
        console.log(`[SWITCH] Calling renderCurrentTab for: ${tabName}`);
        await renderCurrentTab();
        console.log(`[SWITCH] Completed rendering: ${tabName}`);
        
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
            console.log(`[NAV] Tab clicked: ${tabName}`);
            switchTab(tabName);
        });
    });
}

/**
 * Set up global event listeners
 */
function setupEventListeners() {
    // Tab change event
    window.addEventListener('tabChanged', async (event) => {
        await switchTab(event.detail.tab);
    });
    
    // Source change event
    window.addEventListener('sourceChanged', async (event) => {
        showLoading('Loading data...');
        appState.currentSource = event.detail.source;
        clearRenderCache(); // Force re-render all tabs with new data
        await loadData(event.detail.source);
        await switchTab(appState.currentTab);
        hideLoading();
    });
    
    // Refresh data event
    window.addEventListener('refreshData', async () => {
        showLoading('Refreshing data...');
        clearCache();
        clearRenderCache();
        await loadData(appState.currentSource);
        forceRerender(appState.currentTab); // Force re-render current tab
        await switchTab(appState.currentTab);
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
    console.log(`[RENDER] renderCurrentTab called for: ${appState.currentTab}`);
    
    if (!appState.data) {
        console.warn('[RENDER] No data available to render');
        return;
    }
    
    try {
        const tabId = getTabContainerId(appState.currentTab);
        console.log(`[RENDER] Resolved tab container ID: ${tabId}`);
        const tabElement = document.getElementById(tabId);
        
        if (!tabElement) {
            console.error(`[RENDER] Tab element not found: ${tabId}`);
            return;
        }
        
        // Render content - tab visibility already managed by switchTab()
        console.log(`[RENDER] Entering switch statement for: ${appState.currentTab}`);
        switch (appState.currentTab) {
            case 'executive':
                console.log('[RENDER] Rendering executive tab');
                renderExecutiveSummary(appState.data);
                break;
            case 'overview':
                console.log('[RENDER] Rendering overview tab');
                renderOverview(appState.data.overview || appState.data);
                break;
            case 'tech-stack':
                console.log('[RENDER] Rendering tech-stack tab');
                renderTechStack(appState.data);
                break;
            case 'security':
                console.log('[RENDER] Rendering security tab');
                renderSecurity(appState.data);
                break;
            case 'architecture':
                console.log('[RENDER] Rendering architecture tab');
                renderArchitecture(appState.data);
                break;
            case 'code-org':
                console.log('[RENDER] Rendering code-org tab');
                renderCodeOrganization(appState.data);
                break;
            case 'vendors':
                console.log('[RENDER] Rendering vendors tab');
                renderVendors(appState.data);
                break;
            case 'use-cases': {
                // Load use cases data separately
                console.log('[DATA] Loading use-cases.json');
                try {
                    const useCasesData = await loadAdditionalData(appState.currentSource, 'use-cases.json');
                    console.log('[DATA] Use cases data loaded, rendering...');
                    renderUseCases(useCasesData);
                } catch (e) {
                    console.error('[DATA] Failed to load use cases data:', e);
                    renderUseCases({ use_cases: [], roles: [], domains: [], counts: {} });
                }
                break;
            }
            case 'recommendations': {
                // Load recommendations data separately
                console.log('[DATA] Loading recommendations.json');
                try {
                    const rawData = await loadAdditionalData(appState.currentSource, 'recommendations.json');
                    console.log('[DATA] Transforming recommendations data...');
                    const transformedData = transformRecommendationsData(rawData);
                    console.log('[DATA] Recommendations data transformed, rendering...');
                    renderRecommendations(transformedData);
                } catch (e) {
                    console.error('[DATA] Failed to load recommendations data:', e);
                    renderRecommendations({ recommendations: [], top_recommendations: [], counts: {} });
                }
                break;
            }
            case 'onboarding': {
                // Load onboarding data separately
                console.log('[DATA] Loading onboarding.json');
                try {
                    const onboardingData = await loadAdditionalData('mock', 'onboarding.json');
                    console.log('[DATA] Onboarding data loaded:', onboardingData);
                    console.log('[RENDER] Calling renderOnboarding function...');
                    await renderOnboarding(onboardingData);
                    console.log('[RENDER] Onboarding tab rendered successfully');
                } catch (e) {
                    console.error('[DATA] Failed to load onboarding data:', e);
                    // Render with empty data on error
                    await renderOnboarding({ stages: [], team: [], resources: [] });
                }
                break;
            }
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
        case 'onboarding': return 'tab-onboarding';
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
