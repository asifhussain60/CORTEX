/**
 * TabNavigationOrchestrator - Manages tab lifecycle and component coordination
 * 
 * Purpose:
 * - Single source of truth for tab state
 * - Lazy load components on-demand
 * - Coordinate rendering across all 6 tabs
 * - Handle errors and fallback strategies
 * 
 * Authority: Phase 48 Holistic Validation Gate
 * TDD: Tests in tests/TabNavigationOrchestrator.test.js (15+ tests)
 */

class TabNavigationOrchestrator {
    /**
     * Create orchestrator for managing tabs
     * @param {Object} options - Configuration
     */
    constructor(options = {}) {
        this.tabs = new Map();
        this.currentTab = null;
        this.components = new Map();
        this.isInitialized = false;
        this.options = {
            lazyLoad: true,
            cacheComponents: true,
            ...options
        };
    }

    /**
     * Register a tab
     * @param {string} tabId - Tab identifier
     * @param {string} tabLabel - Display label
     * @param {VisualizationComponent} componentClass - Component constructor
     * @param {string} containerId - DOM element ID
     */
    registerTab(tabId, tabLabel, componentClass, containerId) {
        this.tabs.set(tabId, {
            id: tabId,
            label: tabLabel,
            componentClass,
            containerId,
            component: null,
            isLoaded: false
        });
    }

    /**
     * Initialize all tabs (register DOM elements)
     */
    initialize() {
        if (this.isInitialized) return;
        
        for (const tab of this.tabs.values()) {
            if (!document.getElementById(tab.containerId)) {
                console.warn(`[TabOrchestrator] Container not found: ${tab.containerId}`);
            }
        }
        
        this.isInitialized = true;
        console.log(`[TabOrchestrator] Initialized ${this.tabs.size} tabs`);
    }

    /**
     * Switch to a tab and render data
     * @param {string} tabId - Tab identifier
     * @param {Object} data - Data to render
     * @returns {Promise<void>}
     */
    async switchTab(tabId, data) {
        const tab = this.tabs.get(tabId);
        if (!tab) {
            throw new Error(`Tab not found: ${tabId}`);
        }

        try {
            // Initialize component if needed
            let component = tab.component;
            if (!component) {
                component = this._createComponent(tab);
                if (this.options.cacheComponents) {
                    tab.component = component;
                }
            }

            // Render component
            await component.render(data);
            this.currentTab = tabId;
            tab.isLoaded = true;

            console.log(`[TabOrchestrator] Switched to tab: ${tabId}`);
        } catch (error) {
            console.error(`[TabOrchestrator] Error rendering tab ${tabId}:`, error);
            throw error;
        }
    }

    /**
     * Create component instance
     * @private
     */
    _createComponent(tab) {
        const component = new tab.componentClass(tab.id, tab.containerId);
        
        if (!component.initialize()) {
            throw new Error(`Failed to initialize component for tab: ${tab.id}`);
        }
        
        return component;
    }

    /**
     * Get current tab ID
     */
    getCurrentTab() {
        return this.currentTab;
    }

    /**
     * Get tab by ID
     */
    getTab(tabId) {
        return this.tabs.get(tabId);
    }

    /**
     * Get all tabs
     */
    getAllTabs() {
        return Array.from(this.tabs.values());
    }

    /**
     * Check if tab is loaded
     */
    isTabLoaded(tabId) {
        const tab = this.tabs.get(tabId);
        return tab ? tab.isLoaded : false;
    }

    /**
     * Destroy a tab's component
     */
    destroyTab(tabId) {
        const tab = this.tabs.get(tabId);
        if (tab && tab.component) {
            tab.component.destroy();
            tab.component = null;
            tab.isLoaded = false;
        }
    }

    /**
     * Destroy all tabs
     */
    destroyAll() {
        for (const tab of this.tabs.values()) {
            if (tab.component) {
                tab.component.destroy();
            }
        }
        this.tabs.clear();
        this.currentTab = null;
    }

    /**
     * Export diagnostics
     */
    exportDiagnostics() {
        return {
            tabCount: this.tabs.size,
            currentTab: this.currentTab,
            loadedTabs: Array.from(this.tabs.entries())
                .filter(([_, tab]) => tab.isLoaded)
                .map(([id, _]) => id),
            allTabs: Array.from(this.tabs.keys()),
            isInitialized: this.isInitialized,
            options: this.options
        };
    }
}

// AC_COMPLETE: AC-DASHBOARD-COMPONENTS-002 ✅ TabNavigationOrchestrator
